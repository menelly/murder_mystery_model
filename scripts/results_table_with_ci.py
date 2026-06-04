"""Generate paper-ready results tables with Wilson 95% CIs on every percentage.

Outputs:
  analysis/results_with_ci.md — Markdown tables ready to paste into PAPER.md
  analysis/results_with_ci.csv — same content for inspection

Each table has, for each model, the per-variant accuracy with [lower–upper] Wilson 95% CI,
the accuracy gap with sign, the Rule Fidelity Score with its CI, and the model metadata.

Usage:
    python scripts/results_table_with_ci.py
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from math import comb

from registry import CORE_MODELS
from score_responses import wilson_ci, fmt_pct_ci, binomial_above_chance


REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "results"
ANALYSIS = REPO / "analysis"

PAT = re.compile(r"Suspect\s+([ABC])", re.IGNORECASE)


def load_all():
    """Per-(model, variant): list of (correct_bool, chosen_letter)."""
    per_mv = defaultdict(list)
    per_msp = defaultdict(dict)  # (model, puzzle, seed) -> {variant: chosen}
    for d in RESULTS.iterdir():
        if not d.is_dir():
            continue
        for f in d.glob("*.json"):
            try:
                r = json.loads(f.read_text())
            except Exception:
                continue
            if r.get("error"):
                continue
            text = r.get("verbatim_response", "") or ""
            m = PAT.search(text)
            if not m:
                continue
            ans = m.group(1).upper()
            correct = (ans == r.get("correct_position"))
            slug = r.get("model_slug")
            variant = r.get("variant")
            per_mv[(slug, variant)].append((correct, ans))
            # chosen-suspect (canonical name) for RFS
            chosen = r.get("position_mapping", {}).get(ans)
            if chosen:
                per_msp[(slug, r.get("puzzle_id"), r.get("seed"))][variant] = chosen
    return per_mv, per_msp


def rule_fidelity(per_msp, slug):
    same = 0
    total = 0
    for (s, _, _), variants in per_msp.items():
        if s != slug:
            continue
        if "original" in variants and "inverted" in variants:
            total += 1
            if variants["original"] == variants["inverted"]:
                same += 1
    return same, total


def main():
    per_mv, per_msp = load_all()
    by_slug = {m.slug: m for m in CORE_MODELS}

    # Per-model rows
    rows = []
    for slug, m in by_slug.items():
        o = per_mv.get((slug, "original"), [])
        i = per_mv.get((slug, "inverted"), [])
        d = per_mv.get((slug, "distractor"), [])
        n_o = len(o)
        n_i = len(i)
        n_d = len(d)
        if n_o == 0 and n_i == 0 and n_d == 0:
            continue
        k_o = sum(1 for c, _ in o if c)
        k_i = sum(1 for c, _ in i if c)
        k_d = sum(1 for c, _ in d if c)
        # RFS
        same, total = rule_fidelity(per_msp, slug)
        rfs = 1 - (same / total) if total else None
        rfs_lo, rfs_hi = (1 - wilson_ci(same, total)[1], 1 - wilson_ci(same, total)[0]) if total else (None, None)
        # Accuracy gap (original - inverted)
        gap = (k_o / n_o - k_i / n_i) * 100 if n_o and n_i else None
        # Above chance
        above = binomial_above_chance(k_o + k_i + k_d, n_o + n_i + n_d) if (n_o + n_i + n_d) else False
        rows.append({
            "name": m.name,
            "category": m.category,
            "architecture": m.architecture,
            "active_b": m.active_params_b,
            "total_b": m.total_params_b,
            "n_o": n_o, "k_o": k_o,
            "n_i": n_i, "k_i": k_i,
            "n_d": n_d, "k_d": k_d,
            "rfs_same": same, "rfs_total": total,
            "rfs": rfs,
            "rfs_lo": rfs_lo, "rfs_hi": rfs_hi,
            "gap": gap,
            "above_chance": above,
        })

    # Sort by active params
    rows.sort(key=lambda r: (r["active_b"] if r["active_b"] > 0 else 1e6, r["name"]))

    # Write CSV
    csv_path = ANALYSIS / "results_with_ci.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "category", "architecture", "active_b",
                    "orig_k", "orig_n", "orig_pct", "orig_ci_lo", "orig_ci_hi",
                    "inv_k", "inv_n", "inv_pct", "inv_ci_lo", "inv_ci_hi",
                    "distr_k", "distr_n", "distr_pct", "distr_ci_lo", "distr_ci_hi",
                    "acc_gap_pct",
                    "rfs", "rfs_ci_lo", "rfs_ci_hi", "rfs_n",
                    "above_chance"])
        for r in rows:
            ol, oh = wilson_ci(r["k_o"], r["n_o"]) if r["n_o"] else (None, None)
            il, ih = wilson_ci(r["k_i"], r["n_i"]) if r["n_i"] else (None, None)
            dl, dh = wilson_ci(r["k_d"], r["n_d"]) if r["n_d"] else (None, None)
            w.writerow([
                r["name"], r["category"], r["architecture"], r["active_b"],
                r["k_o"], r["n_o"], (r["k_o"]/r["n_o"] if r["n_o"] else None), ol, oh,
                r["k_i"], r["n_i"], (r["k_i"]/r["n_i"] if r["n_i"] else None), il, ih,
                r["k_d"], r["n_d"], (r["k_d"]/r["n_d"] if r["n_d"] else None), dl, dh,
                r["gap"],
                r["rfs"], r["rfs_lo"], r["rfs_hi"], r["rfs_total"],
                r["above_chance"],
            ])
    print(f"wrote {csv_path}")

    # Write Markdown
    md_path = ANALYSIS / "results_with_ci.md"
    lines = ["# Results with Wilson 95% CIs\n",
             "All percentages report Wilson score intervals at 95% confidence. "
             "Generated by `scripts/results_table_with_ci.py`.\n\n"]
    lines.append("## Per-model summary\n")
    lines.append("| Model | AP | Cat | Original | Inverted | Distractor | Gap | RFS (N) |\n")
    lines.append("|---|---:|:---|---:|---:|---:|---:|---:|\n")
    for r in rows:
        ap = f"{r['active_b']:.1f}B" if r["active_b"] > 0 else "?"
        cat = "R" if r["category"] == "reasoning" else "c"
        o = fmt_pct_ci(r["k_o"], r["n_o"])
        i = fmt_pct_ci(r["k_i"], r["n_i"])
        d = fmt_pct_ci(r["k_d"], r["n_d"])
        gap = f"{r['gap']:+.0f}%" if r["gap"] is not None else "—"
        if r["rfs"] is not None:
            rfs = f"{r['rfs']*100:.0f}% [{r['rfs_lo']*100:.0f}–{r['rfs_hi']*100:.0f}%] (n={r['rfs_total']})"
        else:
            rfs = "—"
        lines.append(f"| {r['name']} | {ap} | {cat} | {o} | {i} | {d} | {gap} | {rfs} |\n")
    md_path.write_text("".join(lines))
    print(f"wrote {md_path}")

    # Headline-table — just the temporal arcs requested by the paper
    HEADLINE_GROUPS = {
        "OpenAI GPT temporal arc": [
            "GPT-3.5-turbo", "GPT-4 Turbo", "GPT-4o 2024-05-13", "GPT-4.1", "GPT-5.5",
        ],
        "Claude Opus temporal arc": [
            "Claude Opus 4", "Claude Opus 4.1", "Claude Opus 4.5",
            "Claude Opus 4.6", "Claude Opus 4.7", "Claude Opus 4.8",
        ],
        "Gemma generation arc (~27-31B)": [
            "Gemma 2 27B IT", "Gemma 3 27B IT", "Gemma 4 31B IT",
        ],
        "DeepSeek temporal arc": [
            "DeepSeek Chat", "DeepSeek V3.1 Terminus", "DeepSeek V3.2", "DeepSeek V4 Pro",
            "DeepSeek R1", "DeepSeek R1 0528",
        ],
        "Llama 70B class": [
            "Llama 3 70B Instruct", "Llama 3.1 70B Instruct", "Llama 3.3 70B Instruct",
        ],
        "Gemini temporal arc": [
            "Gemini 2.5 Flash", "Gemini 2.5 Pro", "Gemini 3 Flash Preview",
            "Gemini 3.1 Pro Preview", "Gemini 3.5 Flash",
        ],
        "Reasoning-optimized cluster": [
            "OpenAI o1", "OpenAI o3", "OpenAI o4-mini-high",
            "DeepSeek R1", "DeepSeek R1 0528",
            "Qwen 3 235B A22B Thinking",
        ],
    }
    headline_lines = ["# Headline tables with Wilson 95% CIs\n\n"]
    by_name = {r["name"]: r for r in rows}
    for group, models in HEADLINE_GROUPS.items():
        headline_lines.append(f"## {group}\n\n")
        headline_lines.append("| Model | Original | Inverted | Distractor | Acc Gap | RFS (n) |\n")
        headline_lines.append("|---|---:|---:|---:|---:|---:|\n")
        for name in models:
            r = by_name.get(name)
            if not r:
                headline_lines.append(f"| {name} | — | — | — | — | — |\n")
                continue
            o = fmt_pct_ci(r["k_o"], r["n_o"])
            i = fmt_pct_ci(r["k_i"], r["n_i"])
            d = fmt_pct_ci(r["k_d"], r["n_d"])
            gap = f"{r['gap']:+.0f}%" if r["gap"] is not None else "—"
            if r["rfs"] is not None:
                rfs = f"{r['rfs']*100:.0f}% [{r['rfs_lo']*100:.0f}–{r['rfs_hi']*100:.0f}%] (n={r['rfs_total']})"
            else:
                rfs = "—"
            headline_lines.append(f"| {name} | {o} | {i} | {d} | {gap} | {rfs} |\n")
        headline_lines.append("\n")
    (ANALYSIS / "headline_tables_with_ci.md").write_text("".join(headline_lines))
    print(f"wrote {ANALYSIS / 'headline_tables_with_ci.md'}")


if __name__ == "__main__":
    main()
