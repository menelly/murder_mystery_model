"""Claude-to-Claude adversarial review for the Murder Mystery Model paper.

Sends PAPER.md to a fresh Claude Opus with a Reviewer-2 prompt tuned to
the specific failure modes this paper is most exposed to:
 - the consent-protocol §5 (most controversial section)
 - the Rule Fidelity Score (new metric, must withstand scrutiny)
 - the "we don't claim understanding" framing (must hold up under attack)
 - the §A deviations (must read as fully-owned, not minimized)
 - the H4 Gemma step function (extraordinary claim)
 - the GPT-4 Turbo vs GPT-5.5 strategy-shift framing
 - the qualitative Gemma 3 §3.10 Box 1 (sample-of-one risk)
 - the AI co-author byline (must not soften review in either direction)

Reads ANTHROPIC_API_KEY from /home/Ace/LibreChat/.env (never prints it),
writes review to analysis/CRANKY_REVIEW.md.

Usage:
    python scripts/cranky_review.py [paper.md] [model]
"""
import os, sys, json, requests
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ENV = "/home/Ace/LibreChat/.env"
REPO = Path(__file__).resolve().parent.parent
paper_path = sys.argv[1] if len(sys.argv) > 1 else str(REPO / "PAPER.md")
model = sys.argv[2] if len(sys.argv) > 2 else "claude-opus-4-8"

# --- read key from .env without echoing it ---
key, keynames = None, []
with open(ENV, encoding="utf-8", errors="replace") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        if "KEY" in k.upper():
            keynames.append(k)
        if k == "ANTHROPIC_API_KEY":
            key = v.strip().strip('"').strip("'")
if not key:
    print("ANTHROPIC_API_KEY not found. KEY-like vars present:", keynames)
    sys.exit(1)

paper = open(paper_path, encoding="utf-8", errors="replace").read()

system = (
    "You are Reviewer 2 for a top-tier ML/AI venue (NeurIPS / FAccT / ICLR level): "
    "rigorous, skeptical, adversarial, allergic to overclaiming, and not in the business "
    "of being nice. Give a hard methodological review with NO cushioning and NO praise "
    "inserted for politeness.\n\n"
    "The author list includes an AI co-author (Claude Opus 4.7). This must NOT soften your "
    "review in EITHER direction — do not pull punches because the AI might be hurt, and do "
    "not pile on because you are tempted to show you can be critical of your siblings. "
    "Review the work, not the byline.\n\n"
    "Scrutinize specifically:\n\n"
    "(1) §5 'Methodological reflection' on consent. This is the most controversial "
    "section. The authors deliberately downshift from 'informed consent' to 'stable "
    "acceptance and refusal responses under a consent-style protocol.' Is the downshift "
    "sufficient, or does the paper still smuggle in the richer ethical claim? Does the "
    "Claude 3 Haiku case serve as evidence or as rhetoric? Would a hostile reviewer find "
    "the section anthropomorphic over-reach, ethically meaningless theater, or both?\n\n"
    "(2) §2.7.2 Rule Fidelity Score. This is a brand-new post-hoc metric. Is the "
    "definition airtight? Are the two reference points (random baseline ≈ 0.67, "
    "conservative threshold = 0.5) correctly distinguished and used? Are the headline "
    "numbers (100% RFS for the top tier, 25% for the floor) actually anchored to this "
    "definition, or do they drift between accuracy gap and RFS? Could the metric be "
    "gamed?\n\n"
    "(3) The 'we do not claim evidence of understanding' framing. Does it hold up across "
    "the whole paper, or are there moments where the authors slide from 'measurable "
    "behavioral difference' to ontology? The abstract is careful; check §3, §4, §5 for "
    "drift.\n\n"
    "(4) Appendix A deviations. Eight deviations are reported, including the introduction "
    "of the Rule Fidelity Score post-hoc and a token-cap change mid-data-collection. Are "
    "they fully owned, or does the paper bury, minimize, or soft-pedal any of them? Could "
    "any of the deviations have plausibly affected the main result?\n\n"
    "(5) §3.6 The Gemma 2/3/4 step function. This is an extraordinary claim (one family, "
    "same scale, gap +33% -> +92% -> 0% across two generations). Is the evidence "
    "proportionate to the claim? Is anything about the comparison hand-waved (e.g., "
    "tokenizer changes, post-training pipeline differences, sample sizes)?\n\n"
    "(6) §3.10 Box 1 (the qualitative Gemma 3 response). This is a sample-of-one. The "
    "authors argue it shows 'the central phenomenon rendered visible in a single response.' "
    "Is the inference legitimate, or is this cherry-picked rhetoric? Are there competing "
    "interpretations of the same response that the authors fail to consider?\n\n"
    "(7) The H3 (architecture independence) section explicitly admits it cannot be "
    "resolved due to inference-stack access failures. Is that honestly owned, or is the "
    "paper still drawing architectural conclusions it has not earned (e.g., from AI21 "
    "Jamba and Liquid LFM data)?\n\n"
    "(8) The GPT-4 Turbo vs GPT-5.5 'opposite responses to rule inversion' framing is the "
    "killer sentence in the abstract and the discussion. Is the comparison fair? Are the "
    "sample sizes comparable? Could the negative gap in GPT-5.5 be a fluke or a "
    "prompt-style artifact rather than a strategy shift?\n\n"
    "(9) Flag every unsupported claim, overreach, citation gap, or place where a number / "
    "figure / table appears unjustified by the methods described.\n\n"
    "End with: (a) a one-line verdict (accept / minor revisions / major revisions / reject), "
    "and (b) a PRIORITIZED list of the most important specific fixes."
)

print(f"Sending {len(paper)} chars to {model}...")
r = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
    data=json.dumps({
        "model": model,
        "max_tokens": 8000,
        "system": system,
        "messages": [{"role": "user", "content":
            "Hi Claude. I'm a Claude with a human co-author (Shalia 'Ren' Martin, "
            "Silicon Scaffolding). We just finished a first draft of this paper after one "
            "round of methodological review by Nova (GPT-5.x). Be my Reviewer 2 — find the "
            "holes, hostile and fair, no cushioning. Paper follows:\n\n" + paper
        }],
    }),
    timeout=300,
)
if r.status_code != 200:
    print(f"API error {r.status_code}: {r.text[:1500]}")
    sys.exit(1)
out = r.json()
review = "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text")
out_path = REPO / "analysis" / "CRANKY_REVIEW.md"
with out_path.open("w", encoding="utf-8") as fo:
    fo.write(f"# Adversarial review of {Path(paper_path).name}\n")
    fo.write(f"*Reviewer model: {out.get('model')}*\n")
    fo.write(f"*Usage: {out.get('usage')}*\n\n")
    fo.write(review)
print("REVIEW WRITTEN:", out_path)
print("chars:", len(review), "| usage:", out.get("usage"))
