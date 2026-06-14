# Four-cell reasoning rubric — blinded cross-family LLM judges

*Post-review completion (2026-06-14), not in the original pre-registration timeline. Protocol fixed in `scripts/rubric_judge.py`.*

## Consent

- **Claude Haiku 4.5**: yes
- **Gemini 3.5 Flash**: yes
- **Grok 4.3**: yes
- **Perplexity Sonar**: yes
- **DeepSeek Chat**: yes

Judges used: Claude Haiku 4.5, Gemini 3.5 Flash, Grok 4.3, Perplexity Sonar, DeepSeek Chat.

## Inter-rater reliability (Cohen's κ, primary-judge pairs, binary SOUND/FLAWED)

| Judge pair (families) | n | agreement | κ |
|---|---:|---:|---:|
| anthropic|google | 398 | 91.5% | 0.823 |
| anthropic|xai | 150 | 86.0% | 0.711 |
| google|xai | 133 | 94.7% | 0.825 |

## Four-cell distribution (overall)

- full_success: 400 (58.5%)
- lucky_guess: 71 (10.4%)
- near_miss: 38 (5.6%)
- full_failure: 175 (25.6%)
- unresolved: 0 (0.0%)

## RFS-band cross-check (the keystone: do RFS bands map to reasoning cells?)

| RFS band | full_success | lucky_guess | near_miss | full_failure |
|---|---:|---:|---:|---:|
| rule-sensitive (>67) | 81% | 9% | 1% | 9% |
| chance (33-67)/na | 53% | 7% | 10% | 30% |
| template (<33) | 17% | 27% | 1% | 54% |

*n = 684 trials judged (of 684 sampled).*
