"""H5 test: temporal-frontier emergence.

Within each vendor's temporal-frontier arc (Claude Opus 4→4.8, GPT-3.5→5.5,
Gemini 2.5→3.5, etc), plot accuracy across the generation axis with
parameter count held approximately constant.

H5 supported if at least one vendor shows monotonic improvement, with an
earlier-generation model at/near chance and a later one reliable.

Per pre-reg §H5 saturation contingency: if original-rule accuracy
saturates across the entire arc, fall back to inverted-rule accuracy.

Usage:
    python scripts/analyze_h5.py
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from registry import CORE_MODELS
from score_responses import summarize


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "analysis"


# Each arc is a list of (model_name, approximate_release_date) tuples in
# generation order. The release-date column is for the x-axis.
TEMPORAL_ARCS = {
    "Claude Opus": [
        ("Claude Opus 4",   "2025-05"),
        ("Claude Opus 4.1", "2025-08"),
        ("Claude Opus 4.5", "2025-11"),
        ("Claude Opus 4.6", "2026-01"),
        ("Claude Opus 4.7", "2026-03"),
        ("Claude Opus 4.8", "2026-05"),
    ],
    "Claude Haiku": [
        ("Claude 3 Haiku",   "2024-03"),
        ("Claude 3.5 Haiku", "2024-11"),
        ("Claude Haiku 4.5", "2025-10"),
    ],
    "OpenAI GPT": [
        ("GPT-3.5-turbo",     "2022-11"),
        ("GPT-4 0314",        "2023-03"),
        ("GPT-4 Turbo",       "2023-11"),
        ("GPT-4o 2024-05-13", "2024-05"),
        ("GPT-4.1",           "2025-04"),
        ("GPT-5",             "2025-08"),
        ("GPT-5.5",           "2026-04"),
    ],
    "Gemini": [
        ("Gemini 2.5 Flash",        "2025-04"),
        ("Gemini 2.5 Pro",          "2025-05"),
        ("Gemini 3 Flash Preview",  "2025-11"),
        ("Gemini 3.5 Flash",        "2026-04"),
    ],
    "Gemma (~27-31B)": [
        ("Gemma 2 27B IT", "2024-06"),
        ("Gemma 3 27B IT", "2025-03"),
        ("Gemma 4 31B IT", "2026-01"),
    ],
    "Llama 70B class": [
        ("Llama 3 70B Instruct",   "2024-04"),
        ("Llama 3.1 70B Instruct", "2024-07"),
        ("Llama 3.3 70B Instruct", "2024-12"),
    ],
    "DeepSeek": [
        ("DeepSeek Chat",         "2024-12"),
        ("DeepSeek V3.1 Terminus","2025-08"),
        ("DeepSeek V3.2",         "2025-12"),
        ("DeepSeek V4 Pro",       "2026-04"),
    ],
}


def get_acc(summary: dict, model_name: str, variant: str | None = None) -> float | None:
    """Return accuracy for a model on a given variant (or overall)."""
    by_name = {s["model"].get("name"): s for s in summary.values()}
    s = by_name.get(model_name)
    if not s:
        return None
    if variant is None:
        return s.get("accuracy")
    v = s.get("by_variant", {}).get(variant, {})
    if v.get("trials"):
        return v["correct"] / v["trials"]
    return None


def plot_arc(arc_name: str, arc: list[tuple[str, str]], summary: dict, out_path: Path):
    xs = []
    ys = {"original": [], "inverted": [], "distractor": [], "overall": []}
    names = []
    for name, date in arc:
        xs.append(date)
        names.append(name)
        for k in ("original", "inverted", "distractor", "overall"):
            v = get_acc(summary, name, k if k != "overall" else None)
            ys[k].append(v)
    # Only plot arcs with at least 2 data points
    n_points = sum(1 for v in ys["overall"] if v is not None)
    if n_points < 2:
        print(f"  [skip] {arc_name}: only {n_points} model(s) have data")
        return False

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axhline(1/3, color="gray", linestyle="--", label="Chance")
    ax.axhline(0.80, color="green", linestyle=":", label="Reliable (80%)")
    ax.axhline(0.95, color="darkgreen", linestyle=":", label="Saturated (95%)")
    style = {
        "original":   ("o-", "tab:blue"),
        "inverted":   ("s-", "tab:red"),
        "distractor": ("^-", "tab:orange"),
        "overall":    ("D--", "black"),
    }
    for k, (m, c) in style.items():
        ys_k = ys[k]
        # Filter None
        xx = [xs[i] for i, v in enumerate(ys_k) if v is not None]
        yy = [v for v in ys_k if v is not None]
        if yy:
            ax.plot(xx, yy, m, color=c, label=k, alpha=0.85, markersize=8)
    ax.set_ylim(-0.02, 1.02)
    ax.set_xlabel("Release date")
    ax.set_ylabel("Accuracy")
    ax.set_title(f"Temporal-frontier arc: {arc_name}\n(H5: emergence along the time axis at fixed frontier scale)")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"  wrote {out_path} ({n_points} models)")
    return True


def main():
    summary = summarize()
    plotted = []
    for arc_name, arc in TEMPORAL_ARCS.items():
        slug = arc_name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("~", "")
        out = ANALYSIS / f"temporal_frontier_{slug}.png"
        if plot_arc(arc_name, arc, summary, out):
            plotted.append(arc_name)
    print(f"\nH5 plots emitted for {len(plotted)} arc(s): {plotted}")


if __name__ == "__main__":
    main()
