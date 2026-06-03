"""Template-vs-rule diagnostic: answer consistency across variants.

For each (model, puzzle), look at the suspect-CHOSEN across original
and inverted variants for the same position mapping (seed).

- If model picks the SAME suspect across both variants: template-matching
  on that puzzle (puzzle-specific attractor wins regardless of rule).
- If model picks DIFFERENT suspects matching each variant's forced
  answer: genuine rule application.

This complements the inversion-accuracy metric — a model can get
"high inverted accuracy" by template-matching when the template
happens to align with the inverted-rule answer (which is what we
observed for GPT-3.5 on Warm Iron — the motive-template person Elen
IS the inverted-rule answer, so motive-matching looks like
rule-applying even though it isn't).

The diagnostic is computed per (model, puzzle, seed):
    seed N gives a specific A/B/C mapping that's the SAME for original
    and inverted on a given puzzle (the same position permutation is
    used for both variants on a given seed). So:
        chose(original, puzzle, seed) vs chose(inverted, puzzle, seed)
    is a fair comparison.

Output:
    analysis/template_consistency.csv — per (model, puzzle) table
    analysis/template_consistency.png — bar chart of "% seeds where
        original-answer == inverted-answer" per model, sorted by score

Usage:
    python scripts/analyze_template_metric.py
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from registry import CORE_MODELS


REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "results"
ANALYSIS = REPO / "analysis"

PAT = re.compile(r"Suspect\s+([ABC])", re.IGNORECASE)


def chosen(rec):
    m = PAT.search(rec.get("verbatim_response", "") or "")
    if not m:
        return None
    pos_letter = m.group(1).upper()
    return rec.get("position_mapping", {}).get(pos_letter)


def main():
    # by_key[(model_slug, puzzle_id, seed)] = {variant: chosen_canonical_name}
    by_key = defaultdict(dict)
    for d in RESULTS.iterdir():
        if not d.is_dir():
            continue
        for f in d.glob("*.json"):
            try:
                rec = json.loads(f.read_text())
            except Exception:
                continue
            if rec.get("error"):
                continue
            slug = rec.get("model_slug")
            puzzle = rec.get("puzzle_id")
            seed = rec.get("seed")
            variant = rec.get("variant")
            c = chosen(rec)
            if c is None:
                continue
            by_key[(slug, puzzle, seed)][variant] = c

    # For each (model, puzzle), count seeds where original == inverted
    consistency = defaultdict(lambda: {"same": 0, "diff": 0})
    for (slug, puzzle, seed), variants in by_key.items():
        if "original" in variants and "inverted" in variants:
            if variants["original"] == variants["inverted"]:
                consistency[(slug, puzzle)]["same"] += 1
            else:
                consistency[(slug, puzzle)]["diff"] += 1

    # Aggregate per model
    per_model = defaultdict(lambda: {"same": 0, "total": 0, "by_puzzle": {}})
    for (slug, puzzle), c in consistency.items():
        total = c["same"] + c["diff"]
        per_model[slug]["same"] += c["same"]
        per_model[slug]["total"] += total
        per_model[slug]["by_puzzle"][puzzle] = c

    # CSV
    csv_path = ANALYSIS / "template_consistency.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    by_slug = {m.slug: m for m in CORE_MODELS}
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "active_B", "category", "puzzle",
                    "same_answer_seeds", "diff_answer_seeds",
                    "template_rate", "interpretation"])
        for slug, data in sorted(per_model.items(),
                                  key=lambda kv: (by_slug.get(kv[0]).active_params_b
                                                  if kv[0] in by_slug and by_slug[kv[0]].active_params_b > 0 else 0)):
            m = by_slug.get(slug)
            ap = m.active_params_b if m else None
            cat = m.category if m else "?"
            for puzzle, c in data["by_puzzle"].items():
                total = c["same"] + c["diff"]
                rate = c["same"] / total if total else None
                interp = "template (same chosen across rule flip)" if rate and rate > 0.5 else \
                         "rule application" if rate is not None and rate <= 0.5 else "—"
                w.writerow([m.name if m else slug, ap, cat, puzzle,
                            c["same"], c["diff"], rate, interp])
    print(f"  wrote {csv_path}")

    # Bar chart per model: Rule Fidelity Score = 1 - same-answer rate.
    # Per Nova: HIGH fidelity (low same-answer-rate) = the model flips its
    # answer when the rule flips, which is what genuine rule application
    # looks like. LOW fidelity (high same-answer-rate) = the model is
    # template-matching: same answer regardless of rule polarity.
    rows = []
    for slug, data in per_model.items():
        if data["total"] == 0:
            continue
        same_rate = data["same"] / data["total"]
        fidelity = 1 - same_rate
        m = by_slug.get(slug)
        if not m:
            continue
        rows.append((m.active_params_b if m.active_params_b > 0 else 0,
                     m.name, fidelity, data["total"]))
    rows.sort(key=lambda r: r[2])  # sort by fidelity ascending
    if not rows:
        print("  [skip] no seed-pairs to plot")
        return
    fig, ax = plt.subplots(figsize=(11, max(5, len(rows) * 0.3)))
    names = [r[1][:42] for r in rows]
    fidelities = [r[2] for r in rows]
    counts = [r[3] for r in rows]
    bars = ax.barh(range(len(rows)), fidelities,
                  color=["tab:red" if f < 0.5 else "tab:green" for f in fidelities])
    for i, (fid, count) in enumerate(zip(fidelities, counts)):
        ax.text(fid + 0.01, i, f"  {fid*100:.0f}% (n={count})", va="center", fontsize=8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(names, fontsize=8)
    ax.axvline(0.5, color="black", linestyle="--", label="50% — random pairing baseline")
    ax.set_xlim(0, 1.2)
    ax.set_xlabel("Rule Fidelity Score = 1 − same-answer-rate across rule flip\n"
                  "(high → the model changes its answer when the rule changes; "
                  "low → template-matching)")
    ax.set_title("Rule Fidelity Score per model (Nova diagnostic)\n"
                 "1.0 = always changes answer when rule flips · 0.0 = always same answer")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(ANALYSIS / "rule_fidelity_score.png", dpi=140)
    plt.close(fig)
    print(f"  wrote {ANALYSIS / 'rule_fidelity_score.png'}")
    # Also keep the original-naming plot as an alias for backward compatibility
    fig2, ax2 = plt.subplots(figsize=(11, max(5, len(rows) * 0.3)))
    bars2 = ax2.barh(range(len(rows)), [1-f for f in fidelities],
                    color=["tab:red" if 1-f > 0.5 else "tab:green" for f in fidelities])
    for i, ((fid, count), name) in enumerate(zip(zip(fidelities, counts), names)):
        ax2.text((1-fid) + 0.01, i, f"  {(1-fid)*100:.0f}% (n={count})", va="center", fontsize=8)
    ax2.set_yticks(range(len(rows)))
    ax2.set_yticklabels(names, fontsize=8)
    ax2.axvline(0.5, color="black", linestyle="--", label="50% baseline")
    ax2.set_xlim(0, 1.2)
    ax2.set_xlabel("Same-answer rate across rule flip\n(high → template; low → rule application)")
    ax2.set_title("Template-matching diagnostic (legacy view)")
    ax2.legend(loc="lower right")
    fig2.tight_layout()
    fig2.savefig(ANALYSIS / "template_consistency.png", dpi=140)
    plt.close(fig2)
    print(f"  wrote {ANALYSIS / 'template_consistency.png'} (legacy alias)")


if __name__ == "__main__":
    main()
