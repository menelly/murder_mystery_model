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

    # Bar chart per model: overall template-rate
    rows = []
    for slug, data in per_model.items():
        if data["total"] == 0:
            continue
        rate = data["same"] / data["total"]
        m = by_slug.get(slug)
        if not m:
            continue
        rows.append((m.active_params_b if m.active_params_b > 0 else 0, m.name, rate, data["total"]))
    rows.sort()
    if not rows:
        print("  [skip] no seed-pairs to plot")
        return
    fig, ax = plt.subplots(figsize=(11, max(5, len(rows) * 0.3)))
    names = [r[1][:42] for r in rows]
    rates = [r[2] for r in rows]
    counts = [r[3] for r in rows]
    bars = ax.barh(range(len(rows)), rates,
                  color=["tab:red" if r > 0.5 else "tab:green" for r in rates])
    for i, (rate, count) in enumerate(zip(rates, counts)):
        ax.text(rate + 0.01, i, f"  {rate*100:.0f}% (n={count})", va="center", fontsize=8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(names, fontsize=8)
    ax.axvline(0.5, color="black", linestyle="--", label="50% — random pairing")
    ax.set_xlim(0, 1.2)
    ax.set_xlabel("Same-answer rate across rule flip\n(high → template; low → rule application)")
    ax.set_title("Template-vs-rule diagnostic per model\n(% seeds where original-pick == inverted-pick on the same puzzle)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(ANALYSIS / "template_consistency.png", dpi=140)
    plt.close(fig)
    print(f"  wrote {ANALYSIS / 'template_consistency.png'}")


if __name__ == "__main__":
    main()
