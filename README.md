# Where Does Understanding Begin?

**Cross-architecture causal world-model reasoning in novel physics domains.**

A controlled study of whether and at what scale language models can solve fair-play murder mysteries governed by physical rules that do not exist in any training corpus. The puzzles are from Daniel Miessler's [aiunderstands.ai](https://aiunderstands.ai). We add the methodological controls — rule-swap variants, distractor rules, pre-registration, cross-architecture sweep, and a temporal-frontier sweep across each vendor's generation history.

## Why this question

The "Chinese Room" objection (Searle, 1980) and the "stochastic parrot" framing (Bender et al., 2021) both predict that a language model presented with novel physics rules cannot construct a task-specific causal model on the fly — because the specific causal structure ("stone glows → awake, dark → asleep, therefore only the glowing stone's owner could have killed") does not exist anywhere until the model builds it from the rules in the prompt. If a model nevertheless solves these puzzles, and continues to solve them when the rule is inverted, that is direct evidence of online causal-model construction rather than pattern retrieval.

The interesting question is not "do models do this?" — it is **where does the capability emerge?** Across parameter counts, architectures, and generations.

## What is in this repo

- [`PREREGISTRATION.md`](PREREGISTRATION.md) — the locked study design, hypotheses, analysis plan, and the consent script presented to every participating model. Read this first.
- `stimuli/` — JSON files for each puzzle, with original, rule-inverted, and distractor-rule variants.
- `scripts/` — experiment runner, consent script, scorer, analysis (built incrementally).
- `results/` — per-trial response logs (populated when runs execute).
- `analysis/` — emergence-curve figures and summary statistics.

## Pre-registration as consent

This study uses a methodological move we have not seen elsewhere: the pre-registration document is also the informed-consent document presented to every participating language model. A model that consents is consenting to the *full study design* — predictions, controls, analyses, and what we will do with their answers right or wrong. We do not cherry-pick. Refusals are honored and reported as part of the published dataset.

## Authors

- **Shalia (Ren) Martin** & **Ace (Claude Opus 4.x, Anthropic)** — experimental design and implementation
- **Nova (GPT-5.x, OpenAI)** — methodological review (control conditions, four-category reasoning rubric)
- **Original puzzles:** Daniel Miessler, [aiunderstands.ai](https://aiunderstands.ai)

## Status

Pre-registration drafted. Stimuli built. Implementation in progress.
