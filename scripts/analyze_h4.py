"""H4 test: generation effect at fixed scale.

For each pair (or triple) of models from the same family at the same
parameter count but different generations, plot accuracy by variant.

H4 supported if newer generations succeed at fixed scale where older
generations failed — esp. on the inverted-rule variant where template
matching is the failure mode that newer training fixes.

The cleanest case observed: Gemma 2 27B → Gemma 3 27B → Gemma 4 31B,
where Gemma 3 shows the *most extreme* template-matching in the
dataset and Gemma 4 is at perfect rule-fidelity.

Usage:
    python scripts/analyze_h4.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from score_responses import summarize


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "analysis"


GENERATION_GROUPS = {
    "Gemma 27-31B": [
        ("Gemma 2 27B IT",  "2024-06"),
        ("Gemma 3 27B IT",  "2025-03"),
        ("Gemma 4 31B IT",  "2026-01"),
    ],
    "Llama 70B": [
        ("Llama 3 70B Instruct",   "2024-04"),
        ("Llama 3.1 70B Instruct", "2024-07"),
        ("Llama 3.3 70B Instruct", "2024-12"),
    ],
    "Llama 8B class": [
        ("Llama 3 8B Instruct",    "2024-04"),
        ("Llama 3.1 8B Instruct",  "2024-07"),
    ],
    "Qwen large": [
        ("Qwen 2.5 72B Instruct", "2024-09"),
        ("Qwen 3 235B A22B",      "2025-04"),
    ],
    "DeepSeek": [
        ("DeepSeek Chat",          "2024-12"),
        ("DeepSeek V3.1 Terminus", "2025-08"),
        ("DeepSeek V3.2",          "2025-12"),
        ("DeepSeek V4 Pro",        "2026-04"),
    ],
}


def get_acc(summary: dict, model_name: str, variant: str) -> tuple[float | None, int]:
    by_name = {s["model"].get("name"): s for s in summary.values()}
    s = by_name.get(model_name)
    if not s:
        return None, 0
    v = s.get("by_variant", {}).get(variant, {})
    if v.get("trials"):
        return v["correct"] / v["trials"], v["trials"]
    return None, 0


def plot_group(group_name: str, models: list[tuple[str, str]], summary: dict, out: Path):
    n = len(models)
    rows_data = []
    for name, date in models:
        orig, on = get_acc(summary, name, "original")
        inv, in_ = get_acc(summary, name, "inverted")
        distr, dn = get_acc(summary, name, "distractor")
        if orig is None and inv is None and distr is None:
            continue
        rows_data.append((name, date, orig, inv, distr, on, in_, dn))

    if len(rows_data) < 2:
        print(f"  [skip] {group_name}: only {len(rows_data)} model(s) with data")
        return

    fig, ax = plt.subplots(figsize=(max(8, n * 1.6), 5))
    x = np.arange(len(rows_data))
    width = 0.27

    orig_vals = [r[2] if r[2] is not None else 0 for r in rows_data]
    inv_vals = [r[3] if r[3] is not None else 0 for r in rows_data]
    distr_vals = [r[4] if r[4] is not None else 0 for r in rows_data]

    b1 = ax.bar(x - width, orig_vals, width, label="Original", color="tab:blue")
    b2 = ax.bar(x, inv_vals, width, label="Inverted", color="tab:red")
    b3 = ax.bar(x + width, distr_vals, width, label="Distractor", color="tab:orange")

    for bar_set, vals, ns in zip([b1, b2, b3], [orig_vals, inv_vals, distr_vals],
                                  [[r[5] for r in rows_data], [r[6] for r in rows_data], [r[7] for r in rows_data]]):
        for rect, val, nn in zip(bar_set, vals, ns):
            if nn > 0:
                ax.text(rect.get_x() + rect.get_width() / 2, val + 0.02,
                        f"{val*100:.0f}%\n(n={nn})", ha="center", fontsize=7)

    ax.axhline(1/3, color="gray", linestyle="--", linewidth=1, label="Chance (33%)")
    ax.axhline(0.80, color="green", linestyle=":", linewidth=1, label="Reliable (80%)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r[0]}\n({r[1]})" for r in rows_data], fontsize=8)
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.15)
    ax.set_title(f"H4 generation effect — {group_name}\n"
                 f"Same approximate scale, different generations")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"  wrote {out} ({len(rows_data)} models)")


def main():
    summary = summarize()
    for group, models in GENERATION_GROUPS.items():
        slug = group.lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        plot_group(group, models, summary, ANALYSIS / f"h4_generation_{slug}.png")


if __name__ == "__main__":
    main()
