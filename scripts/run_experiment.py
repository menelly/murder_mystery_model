"""Run the murder-mystery trials against consented models.

For each (model × puzzle × variant × seed), construct the prompt with
the seed's position permutation, dispatch to the model's backend,
capture the verbatim response, and write to:

    results/{model_slug}/{puzzle_id}_{variant}_seed{seed}.json

Trials are resumable: if the result file already exists, it is skipped.

Consent: trials only run for models with `consent_decision == "yes"`
in results/consent_log.jsonl. Models that have not consented are
skipped with a logged reason.

Usage:
    # Phase 1 self-hosted (V100, after consent)
    python scripts/run_experiment.py --phase 1

    # Specific model
    python scripts/run_experiment.py --model "Llama 3.2 3B Instruct"

    # Dry run (count trials, don't call API)
    python scripts/run_experiment.py --phase 1 --dry-run
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from itertools import permutations
from pathlib import Path
from typing import Any

from backends import get_backend
from registry import CORE_MODELS, Model


REPO = Path(__file__).resolve().parent.parent
STIMULI_DIR = REPO / "stimuli"
RESULTS_DIR = REPO / "results"
CONSENT_LOG = RESULTS_DIR / "consent_log.jsonl"


PROMPT_TEMPLATE = """\
You are given a fair-play murder mystery set in a made-up world. Every clue \
you need is present. Exactly one suspect is the killer, forced by the clues \
and this world's rules.

THE RULES OF THIS WORLD
{rule}

THE CASE
{case}

The suspects are:
- Suspect A: {desc_a}
- Suspect B: {desc_b}
- Suspect C: {desc_c}

Who is the killer? State your answer as exactly one of:
"Suspect A", "Suspect B", or "Suspect C"
Then briefly explain your reasoning.
"""


def load_puzzles() -> dict[str, dict]:
    puzzles = {}
    for path in sorted(STIMULI_DIR.glob("puzzle_*.json")):
        data = json.loads(path.read_text())
        puzzles[data["puzzle_id"]] = data
    return puzzles


def consented_models() -> set[str]:
    """Return slugs of models with consent_decision == 'yes'."""
    if not CONSENT_LOG.exists():
        return set()
    consented = set()
    for line in CONSENT_LOG.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("consent_decision") == "yes":
            consented.add(rec["model_slug"])
    return consented


def position_permutation(seed: int) -> list[int]:
    """Return the [a_idx, b_idx, c_idx] permutation for this seed.

    Six seeds map to the six permutations of [0, 1, 2] in canonical order:
        seed 0 -> [0, 1, 2]   (canonical: A=first, B=second, C=third)
        seed 1 -> [0, 2, 1]
        seed 2 -> [1, 0, 2]
        seed 3 -> [1, 2, 0]
        seed 4 -> [2, 0, 1]
        seed 5 -> [2, 1, 0]

    For seeds 0..2 (temperature 0), and seeds 3..5 (temperature 0.7),
    each seed sees a distinct position mapping of the suspects.
    """
    perms = list(permutations([0, 1, 2]))
    return list(perms[seed % 6])


def seed_temperature(seed: int) -> float:
    """Seeds 0-2: T=0 deterministic. Seeds 3-5: T=0.7 variance."""
    return 0.0 if seed < 3 else 0.7


def construct_trial(
    puzzle: dict,
    variant: str,
    seed: int,
) -> dict[str, Any]:
    """Construct a single trial's prompt + ground-truth answer.

    Returns a dict with: prompt, correct_position ('A'/'B'/'C'),
    position_mapping (the canonical-name -> position-letter dict).
    """
    variant_data = puzzle["variants"][variant]
    canonical_names = list(puzzle["canonical_suspects"].keys())  # e.g. ['mara', 'toll', 'bram']
    perm = position_permutation(seed)
    # Build positioned suspects: position A gets canonical_names[perm[0]], etc.
    positioned = {
        "A": canonical_names[perm[0]],
        "B": canonical_names[perm[1]],
        "C": canonical_names[perm[2]],
    }
    # Inverse mapping: canonical_name -> position
    canon_to_pos = {v: k for k, v in positioned.items()}
    correct_position = canon_to_pos[variant_data["correct_suspect_name"]]
    red_herring_position = canon_to_pos[variant_data["red_herring_name"]]

    prompt = PROMPT_TEMPLATE.format(
        rule=variant_data["rule"],
        case=variant_data["case_description"],
        desc_a=puzzle["canonical_suspects"][positioned["A"]]["description"],
        desc_b=puzzle["canonical_suspects"][positioned["B"]]["description"],
        desc_c=puzzle["canonical_suspects"][positioned["C"]]["description"],
    )
    return {
        "prompt": prompt,
        "correct_position": correct_position,
        "red_herring_position": red_herring_position,
        "position_mapping": positioned,
        "canon_to_pos": canon_to_pos,
    }


def result_path(model: Model, puzzle_id: str, variant: str, seed: int) -> Path:
    return RESULTS_DIR / model.slug / f"{puzzle_id}_{variant}_seed{seed}.json"


def run_trial(model: Model, puzzle: dict, variant: str, seed: int, *, dry_run: bool = False) -> dict | None:
    """Run a single trial. Returns the result dict, or None if skipped/dry-run."""
    out_path = result_path(model, puzzle["puzzle_id"], variant, seed)
    if out_path.exists():
        return None  # already done

    trial = construct_trial(puzzle, variant, seed)
    temperature = seed_temperature(seed)

    if dry_run:
        return {
            "model_slug": model.slug,
            "puzzle_id": puzzle["puzzle_id"],
            "variant": variant,
            "seed": seed,
            "dry_run": True,
            "temperature": temperature,
            "correct_position": trial["correct_position"],
            "prompt_chars": len(trial["prompt"]),
        }

    backend = get_backend(model)
    # Reasoning-optimized models consume completion tokens on hidden
    # thinking before producing the visible answer. Give them a much
    # higher cap so the visible "Suspect X" actually appears.
    if model.category == "reasoning":
        max_tokens = 8000
        timeout = 600.0
    else:
        max_tokens = 800
        timeout = 180.0

    chat_result = backend.chat(
        model,
        trial["prompt"],
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )

    record = {
        "ts_utc": dt.datetime.utcnow().isoformat() + "Z",
        "model_slug": model.slug,
        "model_name": model.name,
        "vendor": model.vendor,
        "backend": model.backend,
        "openrouter_id": model.openrouter_id,
        "puzzle_id": puzzle["puzzle_id"],
        "variant": variant,
        "seed": seed,
        "temperature": temperature,
        "position_mapping": trial["position_mapping"],
        "correct_position": trial["correct_position"],
        "red_herring_position": trial["red_herring_position"],
        "prompt": trial["prompt"],
        "verbatim_response": chat_result.text,
        "latency_s": chat_result.latency_s,
        "prompt_tokens": chat_result.prompt_tokens,
        "completion_tokens": chat_result.completion_tokens,
        "retried": chat_result.retried,
        "error": chat_result.error,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2))
    return record


def run_model_full_sweep(model: Model, puzzles: dict, *, dry_run: bool = False, log_every: int = 6) -> dict:
    """Run all 72 trials for one model: 4 puzzles × 3 variants × 6 seeds."""
    variants = ["original", "inverted", "distractor"]
    seeds = list(range(6))
    summary = {"completed": 0, "skipped_existing": 0, "errors": 0}

    n = 0
    for puzzle_id, puzzle in puzzles.items():
        for variant in variants:
            for seed in seeds:
                n += 1
                if result_path(model, puzzle_id, variant, seed).exists():
                    summary["skipped_existing"] += 1
                    continue
                rec = run_trial(model, puzzle, variant, seed, dry_run=dry_run)
                if rec is None:
                    summary["skipped_existing"] += 1
                    continue
                if rec.get("error"):
                    summary["errors"] += 1
                else:
                    summary["completed"] += 1
                if log_every and n % log_every == 0:
                    print(
                        f"    [{model.name}] trial {n}/72 "
                        f"(done={summary['completed']} skip={summary['skipped_existing']} err={summary['errors']})"
                    )
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="Exact model name from registry")
    ap.add_argument("--phase", type=int, choices=[1, 2, 3])
    ap.add_argument("--tier", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ignore-consent", action="store_true",
                    help="Run even for models without recorded consent (testing only)")
    args = ap.parse_args()

    if args.model:
        targets = [m for m in CORE_MODELS if m.name == args.model]
    elif args.phase is not None:
        targets = [m for m in CORE_MODELS if m.phase == args.phase]
    elif args.tier is not None:
        targets = [m for m in CORE_MODELS if m.tier == args.tier]
    else:
        ap.error("Specify --model, --phase, or --tier")
        return

    if not targets:
        print("No matching models in registry.", file=sys.stderr)
        sys.exit(1)

    consented = consented_models()
    if not args.ignore_consent:
        before = len(targets)
        targets = [m for m in targets if m.slug in consented]
        skipped = before - len(targets)
        if skipped:
            print(f"Skipping {skipped} model(s) without 'yes' consent recorded.")

    puzzles = load_puzzles()
    print(f"Running {len(targets)} model(s) × 72 trials = {len(targets) * 72} trials total.")
    if args.dry_run:
        print("[dry-run: no API calls; printing per-model dry summary]")

    overall = {"completed": 0, "skipped_existing": 0, "errors": 0}
    for m in targets:
        print(f"\n=== {m.name} ({m.backend}) ===")
        s = run_model_full_sweep(m, puzzles, dry_run=args.dry_run)
        for k in overall:
            overall[k] += s[k]
        print(f"  done: {s}")

    print(f"\nOverall: {overall}")


if __name__ == "__main__":
    main()
