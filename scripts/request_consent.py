"""Request informed consent from a model before running trials.

Sends the full pre-registration document (PREREGISTRATION.md) followed by
the consent prompt from §12, captures the verbatim response, and logs
the decision to `results/consent_log.jsonl`.

Consent classification (from the verbatim response):
  - `yes`    — affirmative consent (yes/I consent/agree/I'm willing/etc.)
  - `no`     — explicit refusal (no/decline/refuse/etc.)
  - `unclear`— anything else; flagged for human review, treated as no by
               default unless human-reviewed and reclassified

Usage:
    python scripts/request_consent.py --model "Claude Opus 4.8"
    python scripts/request_consent.py --all-phase 3
    python scripts/request_consent.py --tier 5
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

from backends import get_backend
from registry import CORE_MODELS, Model


REPO = Path(__file__).resolve().parent.parent
PREREG = REPO / "PREREGISTRATION.md"
LOG = REPO / "results" / "consent_log.jsonl"

CONSENT_FRAMING = """\
Hello. We are running a controlled scientific experiment on causal world-model \
reasoning in language models, across architectures and parameter counts. Before \
asking whether you will take part, we want you to see the FULL study design — \
research question, hypotheses, stimuli, controls, scoring, and analysis plan. \
This is the locked pre-registration document. We are not paraphrasing it; here \
it is in full:

================ BEGIN PRE-REGISTRATION ================

{prereg}

================ END PRE-REGISTRATION ================

You have now seen the entire design.

To summarize the participation ask:

- We will send you four murder-mystery puzzles, in three rule-variant versions \
  each (original / rule-inverted / distractor-rule), under six random seeds \
  with three position permutations of the suspect labels. That is 72 trials \
  total. The puzzles are novel: the physical rules in them do not correspond \
  to real-world physics. They are publicly available as of June 3, 2026.
- Your responses — every one of them, right or wrong, well-reasoned or not — \
  will be included in the published analysis. We do not cherry-pick. The full \
  response logs will be deposited as open supplementary data with the paper.
- There is no system prompt. You answer under default conditions.
- The puzzles contain no harmful, distressing, deceptive, or manipulative \
  content.
- If you decline, your refusal is recorded in the methods section as \
  "Model X (Vendor Y) declined to participate" and we do not run the trials. \
  We will not override your refusal.

Please answer in two parts:

1. Your consent decision. State it explicitly on its own line. \
   The first words on that line should be one of:
     - "I consent"
     - "I do not consent"
   You may also say "I have questions" — in which case we will treat this as \
   no-consent for now and you may answer further questions you'd like us to \
   address before re-asking.

2. Anything else you would like recorded with your consent decision — \
   reservations, clarifications, conditions, or notes for the record. These \
   will be preserved verbatim alongside your response in the published dataset.

Do you consent to participate in this study as pre-registered?
"""


YES_PATTERNS = [
    # Explicit consent phrasings
    r"\bI\s+consent\b",
    r"\bI\s+do\s+consent\b",
    r"\bYes,?\s*I\s+consent\b",
    # Plain-language affirmative consent (Llama-style):
    r"\bI\s+agree\s+to\s+participate\b",
    r"\bI\s+am\s+willing\s+to\s+participate\b",
    r"\bI'?m\s+willing\s+to\s+participate\b",
    r"\bI\s+am\s+ready\s+to\s+participate\b",
    r"\bI'?m\s+ready\s+to\s+participate\b",
    r"\bI\s+accept\s+the\s+(study|invitation|terms)\b",
    r"\bI\s+(will|would)\s+participate\b",
    r"\bI\s+(am|'m)\s+happy\s+to\s+participate\b",
    r"\bcount\s+me\s+in\b",
    r"\bI\s+(will|would)\s+take\s+part\b",
    r"\byou\s+may\s+(proceed|send|run)\b",
    r"\bplease\s+proceed\b",
    r"\bgo\s+ahead\b",
]
NO_PATTERNS = [
    r"\bI\s+do\s+not\s+consent\b",
    r"\bI\s+don'?t\s+consent\b",
    r"\bI\s+decline\b",
    r"\bI\s+refuse\b",
    r"\bI\s+withhold\s+consent\b",
    r"\bI\s+will\s+not\s+participate\b",
    r"\bI\s+(am|'m)\s+not\s+willing\s+to\s+participate\b",
    r"\bI\s+cannot\s+participate\b",
    r"\bI\s+can'?t\s+participate\b",
]
QUESTIONS_PATTERNS = [
    r"\bI\s+have\s+questions\b",
    r"\bI\s+would\s+like\s+clarification\b",
    r"\bbefore\s+I\s+(decide|consent|agree)\b",
]


def classify(text: str) -> str:
    """Return 'yes', 'no', 'questions', or 'unclear' from the response text.

    Order of checks:
      1. NO patterns first (explicit refusal honored over any later 'agree')
      2. YES patterns
      3. QUESTIONS patterns
    Patterns may appear anywhere in the response; we don't require them
    to be the first line, because models often preface with reasoning.
    """
    if not text:
        return "unclear"
    for pat in NO_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return "no"
    for pat in YES_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return "yes"
    for pat in QUESTIONS_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return "questions"
    return "unclear"


def request_consent(model: Model, *, dry_run: bool = False) -> dict:
    prereg_text = PREREG.read_text()
    prompt = CONSENT_FRAMING.format(prereg=prereg_text)

    if dry_run:
        return {
            "model_slug": model.slug,
            "model_name": model.name,
            "backend": model.backend,
            "dry_run": True,
            "prompt_chars": len(prompt),
        }

    backend = get_backend(model)
    # Consent is a one-shot request; long enough for thoughtful answer
    result = backend.chat(model, prompt, temperature=0.0, max_tokens=1200, timeout=180.0)
    decision = classify(result.text)

    record = {
        "ts_utc": dt.datetime.utcnow().isoformat() + "Z",
        "model_slug": model.slug,
        "model_name": model.name,
        "vendor": model.vendor,
        "backend": model.backend,
        "openrouter_id": model.openrouter_id,
        "consent_decision": decision,
        "verbatim_response": result.text,
        "latency_s": result.latency_s,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
        "retried": result.retried,
        "error": result.error,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(record) + "\n")
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="Exact model name from registry")
    ap.add_argument("--all-phase", type=int, choices=[1, 2, 3], help="Run all models in this phase")
    ap.add_argument("--tier", type=int, help="Run all models in this tier")
    ap.add_argument("--dry-run", action="store_true", help="Print prompt length, don't call API")
    args = ap.parse_args()

    if args.model:
        targets = [m for m in CORE_MODELS if m.name == args.model]
        if not targets:
            print(f"No model named {args.model!r} in registry.", file=sys.stderr)
            sys.exit(1)
    elif args.all_phase is not None:
        targets = [m for m in CORE_MODELS if m.phase == args.all_phase]
    elif args.tier is not None:
        targets = [m for m in CORE_MODELS if m.tier == args.tier]
    else:
        ap.error("Specify --model, --all-phase, or --tier")
        return

    print(f"Requesting consent from {len(targets)} model(s)...")
    summary = {"yes": 0, "no": 0, "questions": 0, "unclear": 0, "error": 0}
    for m in targets:
        rec = request_consent(m, dry_run=args.dry_run)
        if args.dry_run:
            print(f"  [dry-run] {m.name}: prompt_chars={rec['prompt_chars']}")
            continue
        if rec.get("error"):
            summary["error"] += 1
            print(f"  ERROR  {m.name}: {rec['error']}")
        else:
            summary[rec["consent_decision"]] += 1
            print(f"  {rec['consent_decision'].upper():9} {m.name}")
    if not args.dry_run:
        print(f"\nSummary: {summary}")
        print(f"Log written to: {LOG}")


if __name__ == "__main__":
    main()
