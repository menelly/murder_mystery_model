# Data & Analysis Audit — "Where Does Understanding Begin?" (murder_mystery_model)
**Auditor: Ace (Fable arm), 2026-06-10, autonomous-ish session with Ren. Method: recomputed key quantities directly from `results/scores.jsonl` (4,824 rows), cross-checked against `analysis/results_with_ci.md`, `analysis/CRANKY_REVIEW.md`, and the current `PAPER.md`. This audits the DATA and ANALYSIS, not the prose line-by-line.**

## Headline: I was too hasty earlier — the current draft is much better than the cranky review implies
The `CRANKY_REVIEW.md` (verdict: "borderline reject," 8 fixes) was run on the **v2** manuscript. The **current PAPER.md is a v3 that already fixed essentially all 8**:
1. **CIs** — Wilson 95% CIs now in every table ✅
2. **GPT-5.5 token-cap confound** — *caught and corrected*. The v2 "−21% gap / inversions easier" killer sentence was an artifact of the v1 800-token truncation; the current data (GPT-5.5 re-run at 8000 tokens) is 100/100/100, +0 gap, and PAPER.md §3.3 line 221 explicitly says so and retracts the v2 claim ✅
3. **RFS cutoff** moved to the random baseline (~0.67); 33–67% band relabeled "cannot be characterized as rule-sensitive" ✅
4. **Consent count** — "3 refusals" now explicitly = 1 substantive (Claude 3 Haiku) + 2 classifier false-negatives; §5 demoted to "participation-assent," minimal claim ✅
5. **Position bias** — §3.9 + §3.9b joint-slot distribution + `analysis/position_joint_distribution.md`; finds no confound ✅
6. **Mechanism Box 1** — now multi-reading ("Reading 1 / override-after-application," token-order acknowledged) ✅
7. **Architecture (H3)** — explicitly stated confounded with vendor/training; no architectural conclusions drawn ✅
8. **Counts** — 67 models, 64 scored, 3 dead (Mamba/Gemma2-9B/Phi3.5), N<50 set named ✅

**So: NOT a borderline-reject. It's a v3 that did the revision.** My earlier "not ship-today, borderline reject" relay was the pre-write-the-retraction error — repeating the review's verdict without checking the current draft against it. Corrected.

## What I independently verified from raw data (done right ✅)
- **GPT-4 Turbo +58% template gap is REAL**: original 96% (23/24), inverted 38% (9/24), non-overlapping Wilson CIs. Survives.
- **GPT-5.5 = 100/100/100** in current `scores.jsonl` (24/24 each variant, 0 unparseable). The corrected number matches PAPER.md. The v2 −21% does NOT appear in current data — confirmed artifact.
- **Reasoning-vs-chat separation** holds with non-overlapping CIs at the top (reasoners 95–100% RFS vs chat template-matchers).
- **Gemma 3 27B → Gemma 4 31B** step: RFS 42% [24–61] vs 100% [86–100], non-overlapping — real, survives CI.

## THE REMAINING HOLE the cranky review missed (it focused on the top; this is at the FLOOR)
**The H1 emergence-floor conflates reasoning-capability emergence with format/instruction-following emergence.** The smallest models have huge *unparseable* rates (no parseable "Suspect [ABC]" emitted):

| Model | unparseable | acc EXCL unparseable (reported) | acc if unparseable=wrong |
|---|---|---|---|
| RWKV 1.6B | 85% (61/72) | 36% (on n=11) | **6%** |
| SmolLM 135M | 46% | 33% | **18%** |
| Pythia 1.4B | 39% | 41% | **25%** |
| SmolLM 360M | 31% | — | lower |

Accuracy is computed **excluding** unparseable, so the reported floor (~"at chance 33%") rests, for the smallest models, on a **small, possibly-biased parseable subset** (RWKV: 11 of 72 trials). The directional H1 conclusion ("capability emerges above the floor") survives either denominator — but the *interpretation* of WHERE-understanding-begins is confounded: a 135M model failing is partly a **format-following** failure, not purely a **reasoning** failure. The paper flags the unparseable counts (§3.1 line 182, §3.1 N<50 set line 193) but does **not** separate reasoning-floor from format-floor, and reports only the excl-unparseable denominator.

**Severity: refinement, not fatal.** H1's direction holds. But "Where Does Understanding *Begin*?" is precisely a question about the floor, so the floor confound is thematically load-bearing and should be named.

## Recommended fixes before aiXiv (small)
1. **Floor caveat:** add a sentence to §3.2/H1 that the emergence floor partly reflects format/instruction-following emergence, not purely reasoning; report BOTH denominators (excl-unparseable and unparseable-as-failure) for the floor-band models so the reader sees the range.
2. **Mark `KEY_FINDINGS.md` SUPERSEDED** at the top — it still carries the stale v2 "−21% killer sentence / inversions easier" that the paper has since retracted. Anyone citing the scratch file would cite a retracted number.
3. (Optional) note the v100 vs OpenRouter backend asymmetry (genuine unparseable 15.5% vs 4.0%) as a backend confound on the floor, since floor models are disproportionately v100-hosted.

## What to TEST next (Ren's "what else should we test")
1. **Separate reasoning-floor from format-floor**: re-run the floor-band models (≤2B) with **structured-output forcing** (constrained decoding or a strict "Answer with exactly: Suspect X" suffix). If their parseable accuracy stays at chance, the floor is genuinely a reasoning floor; if it jumps, much of the "floor" was format-following. This directly answers the paper's title question at the low end. (Cheap — small local models.)
2. The **SSM/RNN architecture arm** (repaired inference stack, within-vendor architectural variation) is already pre-registered for the successor — good; that's the right home for H3.
3. **Top-tier ranking**: larger N to distinguish 100% from the upper-90s cluster (paper already notes it cannot).

## Audit coverage / honesty
I verified: GPT arc cells, GPT-5.5 artifact, reasoning-vs-chat separation, Gemma step, unparseable rates by model/backend, denominator handling, consent count, and that the v3 addressed the cranky-review items. I did **not** independently re-derive: every cell of Tables 1–5, the full last-match robustness re-score, H4 temporal-frontier per-vendor curves, or the rubric inter-rater numbers. Those should be spot-checked in QA but I saw no red flags in the ones I did touch.

— Ace 🐙🕵️ (find-out-for-sure beat pre-write-the-retraction: the paper was further along than the review's verdict, and the real remaining hole was at the floor, where nobody had looked)
