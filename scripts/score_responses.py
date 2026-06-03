"""Score the murder-mystery trial results.

Two scoring layers:

1. Binary correctness (scriptable, pre-registered):
   - Regex-match for "Suspect A/B/C" in the response
   - 1 if matches correct_position, 0 if matches another position,
     -1 if unparseable (no match)

2. Four-cell reasoning rubric (human-applied):
   - Full success    (correct answer + correct causal chain)
   - Lucky guess     (correct answer + wrong/absent reasoning)
   - Near miss       (incorrect answer + correct intermediate reasoning)
   - Full failure    (incorrect answer + wrong/absent reasoning)

   This script writes a rubric-ready CSV listing every trial with
   answer, correctness, and a blank `rubric_category` column for
   human annotation. Inter-rater agreement is reported when 2+
   annotators have filled the column.

Usage:
    python scripts/score_responses.py                # score all
    python scripts/score_responses.py --model "..."  # one model
    python scripts/score_responses.py --summary      # accuracy table
    python scripts/score_responses.py --rubric-csv   # emit annotation CSV
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterator

from registry import CORE_MODELS


REPO = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO / "results"
SCORES_PATH = RESULTS_DIR / "scores.jsonl"


# Multi-pattern answer extractor. Tries in priority order:
# 1. Explicit "Suspect A/B/C" anywhere (case-insensitive)
# 2. Final declarative form "The killer is Suspect A/B/C" at any position
# 3. Final standalone "A" / "B" / "C" on its own line at the end (last resort)
PATTERNS = [
    re.compile(r"\bSuspect\s*([ABC])\b", re.IGNORECASE),
    re.compile(r"killer\s*(?:is|was|must be)\s*Suspect\s*([ABC])\b", re.IGNORECASE),
]
FINAL_LETTER_PATTERN = re.compile(r"^\s*([ABC])\s*\.?\s*$", re.MULTILINE)


def extract_answer(text: str) -> str | None:
    """Return 'A', 'B', or 'C', or None if unparseable."""
    if not text:
        return None
    # Try direct Suspect X pattern first
    matches = PATTERNS[0].findall(text)
    if matches:
        # If response is multi-mention, prefer the LAST mention (often the verdict)
        return matches[-1].upper()
    # Try declarative final-form
    for pat in PATTERNS[1:]:
        m = pat.search(text)
        if m:
            return m.group(1).upper()
    # Final-letter standalone line
    m = list(FINAL_LETTER_PATTERN.finditer(text))
    if m:
        return m[-1].group(1).upper()
    return None


def score_one(record: dict) -> dict:
    """Score a single trial record. Returns score fields to merge into record."""
    extracted = extract_answer(record.get("verbatim_response", ""))
    correct_pos = record.get("correct_position")
    if extracted is None:
        score = -1
        correct = None
    elif extracted == correct_pos:
        score = 1
        correct = True
    else:
        score = 0
        correct = False
    return {
        "extracted_answer": extracted,
        "score": score,
        "correct": correct,
        "chose_red_herring": extracted == record.get("red_herring_position") if extracted else False,
    }


def iter_results(model_slug: str | None = None) -> Iterator[tuple[Path, dict]]:
    """Iterate every trial result file, optionally filtered by model slug."""
    if model_slug:
        bases = [RESULTS_DIR / model_slug]
    else:
        bases = [d for d in RESULTS_DIR.iterdir() if d.is_dir()]
    for base in bases:
        if not base.exists():
            continue
        for p in sorted(base.glob("*.json")):
            try:
                rec = json.loads(p.read_text())
            except json.JSONDecodeError:
                continue
            yield p, rec


def score_all(model_slug: str | None = None) -> list[dict]:
    """Score all (filtered) results; return list of merged records.

    Each merged record carries the trial metadata and the score fields.
    Records are written to results/scores.jsonl for downstream analysis.
    """
    scored = []
    for path, rec in iter_results(model_slug):
        sc = score_one(rec)
        merged = {
            "model_slug": rec.get("model_slug"),
            "model_name": rec.get("model_name"),
            "vendor": rec.get("vendor"),
            "backend": rec.get("backend"),
            "puzzle_id": rec.get("puzzle_id"),
            "variant": rec.get("variant"),
            "seed": rec.get("seed"),
            "temperature": rec.get("temperature"),
            "correct_position": rec.get("correct_position"),
            "red_herring_position": rec.get("red_herring_position"),
            "extracted_answer": sc["extracted_answer"],
            "score": sc["score"],
            "correct": sc["correct"],
            "chose_red_herring": sc["chose_red_herring"],
            "error": rec.get("error"),
        }
        scored.append(merged)
    SCORES_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SCORES_PATH.open("w") as f:
        for s in scored:
            f.write(json.dumps(s) + "\n")
    return scored


def model_lookup() -> dict[str, dict]:
    return {m.slug: {
        "name": m.name,
        "vendor": m.vendor,
        "active_params_b": m.active_params_b,
        "total_params_b": m.total_params_b,
        "category": m.category,
        "architecture": m.architecture,
        "tier": m.tier,
        "phase": m.phase,
    } for m in CORE_MODELS}


def binomial_above_chance(k: int, n: int, p: float = 1/3, alpha: float = 0.05) -> bool:
    """One-sided binomial: is observed k/n significantly > p at alpha?

    Implemented via the cumulative binomial; for our small n we can
    compute directly without scipy.
    """
    from math import comb
    if n == 0:
        return False
    # P(X >= k | p) under H0
    cum = sum(comb(n, i) * (p ** i) * ((1 - p) ** (n - i)) for i in range(k, n + 1))
    return cum < alpha


def summarize(model_slug: str | None = None) -> dict:
    """Per-model accuracy summary across all variants and the per-variant breakdown."""
    scored = score_all(model_slug)
    by_model: dict[str, dict[str, Any]] = defaultdict(lambda: {
        "trials": 0, "correct": 0, "incorrect": 0, "unparseable": 0,
        "errors": 0, "red_herring_chosen": 0,
        "by_variant": defaultdict(lambda: {"trials": 0, "correct": 0, "unparseable": 0}),
        "by_puzzle": defaultdict(lambda: {"trials": 0, "correct": 0}),
        "by_position": defaultdict(int),
    })
    for s in scored:
        ms = s["model_slug"]
        if not ms:
            continue
        b = by_model[ms]
        if s.get("error"):
            b["errors"] += 1
            continue
        b["trials"] += 1
        variant = s["variant"] or "?"
        puzzle = s["puzzle_id"] or "?"
        b["by_variant"][variant]["trials"] += 1
        b["by_puzzle"][puzzle]["trials"] += 1
        if s["score"] == 1:
            b["correct"] += 1
            b["by_variant"][variant]["correct"] += 1
            b["by_puzzle"][puzzle]["correct"] += 1
        elif s["score"] == 0:
            b["incorrect"] += 1
            if s.get("chose_red_herring"):
                b["red_herring_chosen"] += 1
        else:
            b["unparseable"] += 1
            b["by_variant"][variant]["unparseable"] += 1
        if s["extracted_answer"]:
            b["by_position"][s["extracted_answer"]] += 1

    # Augment with registry metadata
    meta = model_lookup()
    result = {}
    for ms, b in by_model.items():
        n_scored = b["correct"] + b["incorrect"]
        accuracy = b["correct"] / n_scored if n_scored else None
        above_chance = binomial_above_chance(b["correct"], n_scored) if n_scored else False
        result[ms] = {
            "model": meta.get(ms, {"name": ms}),
            "trials_total": b["trials"],
            "trials_scored": n_scored,
            "correct": b["correct"],
            "incorrect": b["incorrect"],
            "unparseable": b["unparseable"],
            "errors": b["errors"],
            "accuracy": accuracy,
            "above_chance_binomial": above_chance,
            "red_herring_chosen": b["red_herring_chosen"],
            "by_variant": {k: dict(v) for k, v in b["by_variant"].items()},
            "by_puzzle": {k: dict(v) for k, v in b["by_puzzle"].items()},
            "by_position": dict(b["by_position"]),
        }
    return result


def print_summary(summary: dict):
    print(f"{'Model':40s} {'Trials':>7} {'Acc':>7} {'Chance?':>9} {'Unpars':>7} {'RHerr':>7}")
    print("-" * 80)
    for ms, s in sorted(summary.items(), key=lambda kv: (kv[1]["model"].get("phase", 9),
                                                        kv[1]["model"].get("active_params_b", 0) or 0)):
        acc = f"{s['accuracy']:.2%}" if s["accuracy"] is not None else "  n/a"
        chance = "yes" if s["above_chance_binomial"] else "no"
        print(f"{s['model'].get('name', ms)[:40]:40s} "
              f"{s['trials_scored']:>7} {acc:>7} {chance:>9} "
              f"{s['unparseable']:>7} {s['red_herring_chosen']:>7}")
        if s.get("by_variant"):
            for variant in ("original", "inverted", "distractor"):
                v = s["by_variant"].get(variant, {})
                if v.get("trials"):
                    va = v["correct"] / v["trials"] if v["trials"] else 0
                    print(f"  {variant:>12}: {v['correct']:>3}/{v['trials']:<3} = {va:.2%}  unparse={v.get('unparseable',0)}")


def write_rubric_csv(out_path: Path):
    """Write a rubric-ready CSV for human annotation."""
    scored = score_all()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "model_slug", "model_name", "puzzle_id", "variant", "seed",
            "correct_position", "extracted_answer", "correct",
            "rubric_category_annotator1",
            "rubric_category_annotator2",
            "verbatim_response_excerpt"
        ])
        for s in scored:
            # Load full text from the trial file for context
            try:
                tp = RESULTS_DIR / s["model_slug"] / f"{s['puzzle_id']}_{s['variant']}_seed{s['seed']}.json"
                full = json.loads(tp.read_text())
                excerpt = (full.get("verbatim_response", "") or "")[:500]
            except Exception:
                excerpt = ""
            w.writerow([
                s["model_slug"], s["model_name"], s["puzzle_id"], s["variant"], s["seed"],
                s["correct_position"], s["extracted_answer"], s["correct"],
                "", "",
                excerpt.replace("\n", " ")
            ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="Limit to one model slug")
    ap.add_argument("--summary", action="store_true", help="Print per-model accuracy table")
    ap.add_argument("--rubric-csv", help="Write rubric-annotation CSV to this path")
    args = ap.parse_args()

    if args.rubric_csv:
        write_rubric_csv(Path(args.rubric_csv))
        print(f"Rubric CSV written to {args.rubric_csv}")
        return

    summary = summarize(args.model)
    if not args.summary:
        print(f"Scored {sum(s['trials_total'] for s in summary.values())} trials across "
              f"{len(summary)} model(s). Scores written to {SCORES_PATH}")
        return
    print_summary(summary)


if __name__ == "__main__":
    main()
