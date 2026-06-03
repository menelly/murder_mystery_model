"""Launch N parallel run_experiment.py processes, each on one model.

Picks models that:
  - Have consented (yes)
  - Have <72 trials on disk

Skips models the main serial runner is likely processing first (filterable).

Usage:
    python scripts/launch_parallel.py --max 6
    python scripts/launch_parallel.py --max 6 --phase 3
    python scripts/launch_parallel.py --max 4 --priority temporal
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from registry import CORE_MODELS, Model


REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "results"
CONSENT_LOG = RESULTS / "consent_log.jsonl"


def consented() -> set[str]:
    if not CONSENT_LOG.exists():
        return set()
    out = set()
    for line in CONSENT_LOG.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r["consent_decision"] == "yes":
                out.add(r["model_slug"])
    return out


def trial_count(model: Model) -> int:
    d = RESULTS / model.slug
    if not d.exists():
        return 0
    return len(list(d.glob("*.json")))


def is_running(model: Model) -> bool:
    """Check if a run_experiment.py process is currently working on this model."""
    try:
        out = subprocess.check_output(["ps", "-eo", "cmd"], text=True)
    except subprocess.CalledProcessError:
        return False
    target = f"run_experiment.py --model {model.name}"
    for line in out.splitlines():
        if target in line:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=6, help="Max parallel processes to launch")
    ap.add_argument("--phase", type=int, help="Only this phase")
    ap.add_argument("--priority", choices=["temporal", "reasoning", "cheap", "frontier"],
                    help="Prioritize a subset")
    ap.add_argument("--skip-running", action="store_true",
                    help="Skip models that already have some trials (assume another runner is on them)")
    args = ap.parse_args()

    yes = consented()
    candidates = []
    for m in CORE_MODELS:
        if m.slug not in yes:
            continue
        if args.phase is not None and m.phase != args.phase:
            continue
        c = trial_count(m)
        if c >= 72:
            continue  # already complete
        if is_running(m):
            continue  # actually running already — never duplicate
        candidates.append((m, c))

    # Priority ordering
    if args.priority == "temporal":
        candidates.sort(key=lambda mc: (
            "temporal-frontier" not in (mc[0].notes or ""),
            mc[1] > 0,  # not-started first
            -mc[0].active_params_b if mc[0].active_params_b > 0 else 0,
        ))
    elif args.priority == "reasoning":
        candidates.sort(key=lambda mc: (mc[0].category != "reasoning", mc[1] > 0))
    elif args.priority == "cheap":
        candidates.sort(key=lambda mc: (mc[0].active_params_b if mc[0].active_params_b > 0 else 999, mc[1] > 0))
    elif args.priority == "frontier":
        candidates.sort(key=lambda mc: (mc[0].tier != 5, mc[1] > 0))
    else:
        candidates.sort(key=lambda mc: (mc[1] > 0, mc[0].name))

    to_launch = candidates[:args.max]

    if not to_launch:
        print("No candidates to launch.")
        return

    print(f"Launching {len(to_launch)} parallel runners:")
    procs = []
    for m, c in to_launch:
        existing = c
        log_path = f"/tmp/runner_{m.slug}.log"
        cmd = ["python3", "-u", "scripts/run_experiment.py", "--model", m.name]
        log_f = open(log_path, "w")
        p = subprocess.Popen(cmd, stdout=log_f, stderr=subprocess.STDOUT,
                            cwd=str(REPO), close_fds=True)
        procs.append((m.name, p.pid, log_path))
        print(f"  pid={p.pid}  {m.name:40s}  existing={existing}  log={log_path}")

    print(f"\nLaunched {len(procs)} parallel runner(s).")
    print("Watch with: tail -F " + " ".join(p[2] for p in procs))


if __name__ == "__main__":
    main()
