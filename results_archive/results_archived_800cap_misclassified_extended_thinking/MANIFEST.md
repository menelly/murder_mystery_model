# Archive: 800-token-cap trials for models with extended-thinking behavior

**Created:** 2026-06-04
**Reason:** rerun because missingness was non-random and caused by an implementation constraint, not because scores were low.

## What happened

Four models were initially classified as `category: chat` in the model registry:

- GPT-5.5
- Qwen 3 14B
- Qwen 3 32B
- DeepSeek V4 Pro

In our run, all four behaved like reasoning-optimized / extended-thinking models: they consumed substantial completion tokens on internal deliberation before producing a visible answer. Under the chat-category 800-token cap, this caused a subset of their visible responses to be empty or truncated below the point at which they produced their `Suspect [ABC]` verdict.

The breakdown of trials where `completion_tokens >= 795` AND no parseable `Suspect [ABC]` was emitted:

| Model | Truncated-unparseable v1 trials |
|---|---:|
| GPT-5.5 | 12 / 72 |
| Qwen 3 14B | 53 / 72 |
| Qwen 3 32B | 34 / 72 |
| DeepSeek V4 Pro | 36 / 72 |
| **Total** | **135** |

## What we did

1. Identified the 135 trials matching the truncated-unparseable criterion.
2. **Archived (moved, not deleted) those files here**, preserving them unchanged for audit. v1 numbers remain reproducible from these files.
3. Reclassified the four models in `scripts/registry.py` as `category: reasoning` based on their observed inference behavior (this is empirical reclassification, not a retroactive promotion: the models were not chosen for reclassification because their scores were low; they were chosen because their visible-answer outputs were non-random-missing under the chat cap).
4. Re-ran only those 135 trials under the 8000-token cap that reasoning-category models already used. The repo's idempotent file-skip logic ensured all other trial files were left untouched.
5. Regenerated all analysis figures and tables from the corrected visible-answer dataset.

## Reporting

The deviations log (PAPER.md Appendix A.6 / A.8) reports this correction in full. The paper's reasoning-category emergence curve and §4.4 conclusion are now budget-matched. Per pre-registration §11, we treat this as a named deviation rather than a silent re-run.

## File index

(see directory contents — 135 archived JSON files plus this manifest)
