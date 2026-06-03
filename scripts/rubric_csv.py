"""Emit a CSV ready for human-applied 4-cell reasoning rubric annotation.

Per pre-reg §8b, two annotators score a random 20% sample of trials
into one of:
    full_success | lucky_guess | near_miss | full_failure

This script:
  1. Lists every parseable trial result
  2. Stratifies by (model, variant) and samples 20%
  3. Writes analysis/rubric_sample.csv with one row per sampled trial:
       model, puzzle, variant, seed, correct_position, extracted_answer,
       correct (T/F), excerpt, annotator1_cell, annotator2_cell

For Ace + Ren as the two annotators. Inter-rater κ computed later.

Usage:
    python scripts/rubric_csv.py            # 20% stratified sample
    python scripts/rubric_csv.py --fraction 0.4
    python scripts/rubric_csv.py --all      # every parseable trial
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

from score_responses import extract_answer


REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "results"
ANALYSIS = REPO / "analysis"


def iter_trials():
    for d in RESULTS.iterdir():
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.json")):
            try:
                rec = json.loads(p.read_text())
            except json.JSONDecodeError:
                continue
            yield rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fraction", type=float, default=0.20)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=str(ANALYSIS / "rubric_sample.csv"))
    args = ap.parse_args()

    random.seed(args.seed)

    # Stratify by (model, variant)
    by_strata: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for rec in iter_trials():
        if rec.get("error"):
            continue
        text = rec.get("verbatim_response", "")
        extracted = extract_answer(text)
        if extracted is None:
            continue  # unparseable doesn't need a reasoning rubric
        rec["_extracted"] = extracted
        rec["_correct"] = (extracted == rec.get("correct_position"))
        by_strata[(rec["model_slug"], rec["variant"])].append(rec)

    sampled = []
    for stratum, recs in by_strata.items():
        if args.all:
            sampled.extend(recs)
        else:
            k = max(1, int(round(len(recs) * args.fraction)))
            sampled.extend(random.sample(recs, k=min(k, len(recs))))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "model_slug", "model_name", "vendor",
            "puzzle_id", "variant", "seed",
            "correct_position", "red_herring_position", "extracted_answer", "correct",
            "annotator_ace", "annotator_ren", "agreement_note",
            "verbatim_response_excerpt"
        ])
        for r in sampled:
            excerpt = (r.get("verbatim_response", "") or "")[:1500]
            w.writerow([
                r.get("model_slug"), r.get("model_name"), r.get("vendor"),
                r.get("puzzle_id"), r.get("variant"), r.get("seed"),
                r.get("correct_position"), r.get("red_herring_position"),
                r["_extracted"], "T" if r["_correct"] else "F",
                "", "", "",
                excerpt.replace("\n", " | "),
            ])
    print(f"Wrote {len(sampled)} sampled trials (across {len(by_strata)} model×variant strata) to {out}")


if __name__ == "__main__":
    main()
