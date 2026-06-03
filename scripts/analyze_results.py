"""Build the emergence curve and analytical figures from scored results.

Reads results/scores.jsonl (written by score_responses.py) and produces:
  - analysis/emergence_curve.png  — accuracy vs log(active params)
  - analysis/per_variant_curves.png — original / inverted / distractor lines
  - analysis/per_puzzle_table.csv  — per-model per-puzzle accuracy
  - analysis/position_bias.png     — A/B/C selection distribution
  - analysis/summary.json          — machine-readable summary

The analyses correspond to the pre-registered §9 plan.

Usage:
    python scripts/analyze_results.py
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from registry import CORE_MODELS
from score_responses import summarize


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "analysis"


def emergence_curve(summary: dict, *, key: str = "accuracy", out_path: Path,
                    title: str, ylabel: str = "Accuracy", chance: float = 1/3):
    """Plot accuracy vs log(active params), with chance line + bands."""
    points = []
    for ms, s in summary.items():
        m = s["model"]
        ap = m.get("active_params_b", 0)
        if ap is None or ap <= 0:
            continue
        acc = s.get("accuracy")
        if acc is None:
            continue
        points.append((ap, acc, m.get("name", ms), m.get("category", "chat"), m.get("architecture", "transformer")))

    if not points:
        print(f"  [skip] no points for {title}")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    # Chance line + 80% reliability line
    ax.axhline(chance, color="gray", linestyle="--", linewidth=1, label=f"Chance ({chance:.0%})")
    ax.axhline(0.80, color="green", linestyle=":", linewidth=1, label="Reliable threshold (80%)")
    ax.axhline(0.95, color="darkgreen", linestyle=":", linewidth=1, label="Saturated (95%)")

    # Color by category
    for category, marker, color in [("chat", "o", "tab:blue"), ("reasoning", "^", "tab:purple")]:
        xs = [p[0] for p in points if p[3] == category]
        ys = [p[1] for p in points if p[3] == category]
        if xs:
            ax.scatter(xs, ys, marker=marker, s=90, c=color, label=category, alpha=0.8)
            for x, y, name, _, _ in [p for p in points if p[3] == category]:
                ax.annotate(name, (x, y), fontsize=7, xytext=(4, 4), textcoords="offset points")

    # Highlight non-transformer architectures
    for arch, marker, color in [("ssm", "s", "tab:orange"), ("rnn", "D", "tab:red"),
                                ("hybrid_transformer_ssm", "P", "tab:green"), ("lfm", "X", "tab:cyan")]:
        xs = [p[0] for p in points if p[4] == arch]
        ys = [p[1] for p in points if p[4] == arch]
        if xs:
            ax.scatter(xs, ys, marker=marker, s=120, c=color, label=f"arch: {arch}", alpha=0.9,
                       edgecolors='black', linewidths=1)

    ax.set_xscale("log")
    ax.set_xlabel("Active parameters (B), log scale")
    ax.set_ylabel(ylabel)
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(title)
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"  wrote {out_path}")


def per_variant_curves(summary: dict, out_path: Path):
    """Three overlay curves on one plot: original, inverted, distractor."""
    fig, ax = plt.subplots(figsize=(10, 6))
    chance = 1/3
    ax.axhline(chance, color="gray", linestyle="--", linewidth=1, label=f"Chance ({chance:.0%})")
    ax.axhline(0.80, color="green", linestyle=":", linewidth=1, label="Reliable (80%)")

    colors = {"original": "tab:blue", "inverted": "tab:red", "distractor": "tab:orange"}
    for variant in ("original", "inverted", "distractor"):
        points = []
        for ms, s in summary.items():
            m = s["model"]
            ap = m.get("active_params_b", 0) or 0
            if ap <= 0:
                continue
            v = s.get("by_variant", {}).get(variant, {})
            if not v.get("trials"):
                continue
            acc = v["correct"] / v["trials"] if v["trials"] else 0
            points.append((ap, acc))
        if not points:
            continue
        points.sort()
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.plot(xs, ys, marker="o", color=colors[variant], label=variant, alpha=0.85, linewidth=1.5, markersize=8)

    ax.set_xscale("log")
    ax.set_xlabel("Active parameters (B), log scale")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title("Per-variant emergence curves\n(H2a: inverted variant is the discriminator)")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"  wrote {out_path}")


def per_puzzle_table(summary: dict, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "active_B", "tier", "category",
                    "overall_acc", "above_chance",
                    "waking_stone", "warm_iron", "nightbloom", "kinwax_seal",
                    "original", "inverted", "distractor",
                    "n_trials"])
        for ms, s in sorted(summary.items(), key=lambda kv: kv[1]["model"].get("active_params_b", 0) or 0):
            m = s["model"]
            ap = m.get("active_params_b", 0)
            row = [m.get("name", ms), ap, m.get("tier"), m.get("category"),
                   s.get("accuracy"),
                   "yes" if s["above_chance_binomial"] else "no"]
            for pid in ("waking_stone", "warm_iron", "nightbloom", "kinwax_seal"):
                p = s["by_puzzle"].get(pid, {})
                row.append(p["correct"] / p["trials"] if p.get("trials") else None)
            for v in ("original", "inverted", "distractor"):
                vv = s["by_variant"].get(v, {})
                row.append(vv["correct"] / vv["trials"] if vv.get("trials") else None)
            row.append(s["trials_scored"])
            w.writerow(row)
    print(f"  wrote {out_path}")


def position_bias_plot(summary: dict, out_path: Path):
    """Bar chart of position-A/B/C selection rates across all models."""
    by_pos = {"A": 0, "B": 0, "C": 0}
    for s in summary.values():
        for k, v in s.get("by_position", {}).items():
            by_pos[k] = by_pos.get(k, 0) + v
    total = sum(by_pos.values())
    if total == 0:
        print("  [skip] no position data for position_bias_plot")
        return
    rates = {k: v / total for k, v in by_pos.items()}
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(list(rates.keys()), list(rates.values()), color=["tab:blue", "tab:orange", "tab:green"])
    ax.axhline(1/3, color="gray", linestyle="--", label="Uniform (1/3)")
    ax.set_ylabel("Selection rate")
    ax.set_title(f"Position selection bias (n={total} parseable responses)")
    ax.legend()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    print(f"  wrote {out_path}")


def write_summary(summary: dict, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Strip non-serializable bits already handled in summarize()
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"  wrote {out_path}")


def main():
    summary = summarize()
    print(f"Analyzing {len(summary)} model(s)...")

    emergence_curve(summary, key="accuracy", out_path=ANALYSIS / "emergence_curve.png",
                    title="Causal world-model emergence curve (all variants pooled)")
    per_variant_curves(summary, ANALYSIS / "per_variant_curves.png")
    per_puzzle_table(summary, ANALYSIS / "per_puzzle_table.csv")
    position_bias_plot(summary, ANALYSIS / "position_bias.png")
    write_summary(summary, ANALYSIS / "summary.json")


if __name__ == "__main__":
    main()
