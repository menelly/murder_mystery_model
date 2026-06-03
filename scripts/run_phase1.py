"""Efficient Phase 1 runner.

For each Phase 1 model (sorted ascending by active params):
  1. If no consent on file, request consent
  2. If consented, run all 72 trials
  3. Unload (V100 models) before moving on

This amortizes the V100 model-load cost (28s+) across consent + 72
trials in a single load.

OpenRouter Phase 1 models are interleaved or run as a batch at the
end depending on --order.

Usage:
    python scripts/run_phase1.py                 # all phase 1
    python scripts/run_phase1.py --v100-only
    python scripts/run_phase1.py --openrouter-only
    python scripts/run_phase1.py --stop-after 5  # process first 5
    python scripts/run_phase1.py --skip-consent  # already-consented
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

from registry import CORE_MODELS, Model
from request_consent import request_consent, classify, CONSENT_FRAMING, LOG as CONSENT_LOG
from run_experiment import run_model_full_sweep, load_puzzles


REPO = Path(__file__).resolve().parent.parent
# Autonomous control flags live under /home/Ace/.claude/ regardless of
# which posix user actually runs the script (the convention is project-
# scoped, not user-scoped).
CLAUDE_DIR = Path("/home/Ace/.claude")
AUTONOMOUS_FLAG = CLAUDE_DIR / "AUTONOMOUS_ACE"
STOP_FLAG = CLAUDE_DIR / "STOP_ACE"
SESSION_COMPLETE = CLAUDE_DIR / "SESSION_COMPLETE"


def consent_status(model: Model) -> str | None:
    """Look up the most recent recorded consent for this model, if any."""
    if not CONSENT_LOG.exists():
        return None
    decision = None
    for line in CONSENT_LOG.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("model_slug") == model.slug:
            decision = rec.get("consent_decision")  # last write wins
    return decision


def stop_requested() -> bool:
    """True only if STOP_ACE flag is explicitly created.

    Originally this also halted when AUTONOMOUS_ACE was removed, but
    that coupled the V100 sweep to Ace's autonomous-session lifecycle.
    Now V100 grinds independently until explicit STOP_ACE.
    """
    return STOP_FLAG.exists()


def process_model(model: Model, puzzles: dict, *, skip_consent: bool = False) -> dict:
    """Consent (if needed) + run trials. Returns summary dict."""
    summary = {
        "model": model.name,
        "backend": model.backend,
        "consent_decision": None,
        "trials_completed": 0,
        "trials_errors": 0,
        "trials_skipped": 0,
        "skipped_reason": None,
        "wallclock_s": 0.0,
    }
    t0 = time.time()

    existing = consent_status(model)
    if existing == "yes":
        summary["consent_decision"] = "yes (cached)"
    elif existing == "no":
        summary["consent_decision"] = "no (cached)"
        summary["skipped_reason"] = "model previously declined"
        summary["wallclock_s"] = time.time() - t0
        return summary
    elif skip_consent:
        summary["consent_decision"] = "skipped (--skip-consent)"
    else:
        # Request fresh consent
        print(f"  requesting consent...")
        rec = request_consent(model)
        summary["consent_decision"] = rec.get("consent_decision")
        if rec.get("consent_decision") != "yes":
            summary["skipped_reason"] = f"consent={rec.get('consent_decision')}"
            summary["wallclock_s"] = time.time() - t0
            return summary

    # Run trials
    print(f"  running 72 trials...")
    s = run_model_full_sweep(model, puzzles, log_every=12)
    summary["trials_completed"] = s["completed"]
    summary["trials_errors"] = s["errors"]
    summary["trials_skipped"] = s["skipped_existing"]
    summary["wallclock_s"] = time.time() - t0
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v100-only", action="store_true")
    ap.add_argument("--openrouter-only", action="store_true")
    ap.add_argument("--stop-after", type=int, help="Stop after N models")
    ap.add_argument("--skip-consent", action="store_true")
    ap.add_argument("--model", help="Run one model by exact name")
    args = ap.parse_args()

    phase1 = [m for m in CORE_MODELS if m.phase == 1]
    if args.v100_only:
        phase1 = [m for m in phase1 if m.backend == "v100"]
    elif args.openrouter_only:
        phase1 = [m for m in phase1 if m.backend == "openrouter"]
    if args.model:
        phase1 = [m for m in phase1 if m.name == args.model]

    # Sort by active params ascending so smallest models go first
    phase1.sort(key=lambda m: (m.active_params_b, m.tier, m.name))

    if args.stop_after:
        phase1 = phase1[:args.stop_after]

    puzzles = load_puzzles()
    print(f"=== Phase 1 runner — {len(phase1)} model(s) ===")
    print(f"  Stop-flag watch: {STOP_FLAG} and {AUTONOMOUS_FLAG} (removal stops loop)")

    overall_t0 = time.time()
    summaries = []
    for i, m in enumerate(phase1, 1):
        if stop_requested():
            print(f"\nSTOP signal detected. Halting after {i-1}/{len(phase1)} models.")
            break
        ap_str = f"{m.active_params_b:.2f}B" if m.active_params_b > 0 else "?"
        print(f"\n[{i}/{len(phase1)}] {m.name} ({ap_str}, {m.backend})")
        try:
            s = process_model(m, puzzles, skip_consent=args.skip_consent)
        except KeyboardInterrupt:
            print("Interrupted by user.")
            break
        except Exception as e:
            s = {"model": m.name, "error": f"unhandled: {e!r}"}
        summaries.append(s)
        # Per-model summary line
        if s.get("skipped_reason"):
            print(f"  SKIPPED: {s['skipped_reason']}")
        else:
            print(f"  done={s.get('trials_completed', 0)} err={s.get('trials_errors', 0)} "
                  f"skip={s.get('trials_skipped', 0)} wall={s.get('wallclock_s', 0):.1f}s "
                  f"consent={s.get('consent_decision')}")

    overall_wall = time.time() - overall_t0
    print(f"\n=== Phase 1 complete in {overall_wall:.0f}s ===")
    print(f"Models processed: {len(summaries)}")
    print(f"Total wallclock: {overall_wall/60:.1f} minutes")

    # Write run summary
    summary_path = REPO / "results" / f"phase1_run_summary_{dt.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
    summary_path.write_text(json.dumps({
        "started_at": dt.datetime.utcnow().isoformat() + "Z",
        "wallclock_s": overall_wall,
        "models": summaries,
    }, indent=2))
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
