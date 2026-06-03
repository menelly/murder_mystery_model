"""Quick status dashboard for the running sweeps."""
from __future__ import annotations

import json
from pathlib import Path

from registry import CORE_MODELS
from score_responses import summarize, binomial_above_chance


REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "results"
CONSENT_LOG = RESULTS / "consent_log.jsonl"


def consent_table():
    if not CONSENT_LOG.exists():
        return {}
    out = {}
    for line in CONSENT_LOG.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["model_slug"]] = r.get("consent_decision")  # last write wins
    return out


def trial_counts():
    out = {}
    for d in RESULTS.iterdir():
        if d.is_dir():
            count = len(list(d.glob("*.json")))
            if count > 0:
                out[d.name] = count
    return out


def main():
    consents = consent_table()
    counts = trial_counts()
    summary = summarize()
    by_slug = {m.slug: m for m in CORE_MODELS}

    print("="*88)
    print("  MURDER MYSTERY MODEL — STATUS DASHBOARD")
    print("="*88)
    print()

    # Consent summary
    yes_n = sum(1 for v in consents.values() if v == "yes")
    no_n = sum(1 for v in consents.values() if v == "no")
    other_n = len(consents) - yes_n - no_n
    print(f"CONSENT: {yes_n} yes, {no_n} no, {other_n} unclear/questions  "
          f"({len(consents)} models contacted / {len(CORE_MODELS)} in registry)")
    print()

    # Per-phase progress
    for phase in (1, 2, 3):
        models = [m for m in CORE_MODELS if m.phase == phase]
        completed_72 = sum(1 for m in models if counts.get(m.slug, 0) >= 72)
        in_progress = sum(1 for m in models if 0 < counts.get(m.slug, 0) < 72)
        not_started = sum(1 for m in models if counts.get(m.slug, 0) == 0)
        consented = sum(1 for m in models if consents.get(m.slug) == "yes")
        declined = sum(1 for m in models if consents.get(m.slug) == "no")
        print(f"PHASE {phase}: {len(models)} models | "
              f"consent: {consented}y/{declined}n | "
              f"trials: {completed_72} done, {in_progress} in-progress, {not_started} not-started")

    print()

    # Per-model rolling accuracy (sorted by active params)
    print(f"{'MODEL':40s} {'Acc':>7} {'Chance':>7} {'Trials':>7} {'Orig':>7} {'Inv':>7} {'Distr':>7}")
    print("-"*88)
    sortable = []
    for ms, s in summary.items():
        m = by_slug.get(ms)
        if not m:
            continue
        sortable.append((m.active_params_b, m.phase, m.tier, ms, s))
    for ap, phase, tier, ms, s in sorted(sortable):
        if not s.get("by_variant"):
            continue
        acc = f"{s['accuracy']*100:.1f}%" if s.get("accuracy") is not None else "  n/a"
        ch = "yes" if s["above_chance_binomial"] else "no"
        oriv = s["by_variant"].get("original", {})
        invv = s["by_variant"].get("inverted", {})
        disv = s["by_variant"].get("distractor", {})
        def fmt(v):
            if v.get("trials"):
                return f"{v['correct']/v['trials']*100:.0f}%({v['trials']})"
            return "—"
        print(f"  [P{phase}T{tier}] {by_slug[ms].name[:32]:32s} "
              f"{acc:>7} {ch:>7} {s['trials_scored']:>7} "
              f"{fmt(oriv):>7} {fmt(invv):>7} {fmt(disv):>7}")

    print()

    # Models above chance and showing the H2a pattern (orig > inverted by 15%+)
    h2a_signature = []
    for ms, s in summary.items():
        oriv = s["by_variant"].get("original", {})
        invv = s["by_variant"].get("inverted", {})
        if oriv.get("trials", 0) >= 6 and invv.get("trials", 0) >= 6:
            orig_acc = oriv["correct"] / oriv["trials"]
            inv_acc = invv["correct"] / invv["trials"]
            diff = orig_acc - inv_acc
            if diff > 0.15:
                m = by_slug.get(ms)
                if m:
                    h2a_signature.append((m.active_params_b, m.name, orig_acc, inv_acc, diff))
    if h2a_signature:
        print("H2a SIGNATURE (orig > inverted by 15%+, template-matching candidates):")
        for ap, name, orig, inv, diff in sorted(h2a_signature):
            print(f"  {name:40s} {ap:.2f}B  orig={orig*100:.0f}% inv={inv*100:.0f}% diff={diff*100:+.0f}%")


if __name__ == "__main__":
    main()
