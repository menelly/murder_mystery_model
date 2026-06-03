# Key Findings — Preliminary

Snapshot of the most striking findings as of mid-data-collection. Numbers
will shift as remaining trials complete; the qualitative shape of the
findings has stabilized.

## Headline

**Different language-model generations exhibit measurably different
susceptibility to narrative-template attraction under controlled rule
inversion.** The 2024–2026 frontier transition shows a strategy shift,
not just a capability gain: where 2024-vintage frontier models
template-match the murder mystery genre, 2026-vintage frontier models
flip their answer in response to the inverted rule.

## The killer sentence

GPT-4 Turbo and GPT-5.5 achieve similar high performance on original
puzzles but show **opposite** responses to rule inversion (GPT-4 Turbo
gap +67%; GPT-5.5 gap −21%).

## Rule Fidelity Score top of the field (n ≥ 10 paired observations)

| Rank | Model | Rule Fidelity |
|---:|---|---:|
| 1 | OpenAI o4-mini-high | 100.0% |
| 1 | OpenAI o1 | 100.0% |
| 1 | Gemini 3.1 Pro Preview | 100.0% |
| 1 | GPT-5.5 | 100.0% |
| 5 | Claude Opus 4.7 | 95.8% |
| 5 | Claude Opus 4.8 | 95.8% |
| 7 | Gemini 3.5 Flash | 95.5% |
| 8 | Claude Opus 4.5 | 91.7% |
| 9 | Gemini 2.5 Pro | 91.3% |
| 10 | Claude Opus 4.6 | 87.5% |
| 11 | Claude Sonnet 4.6 | 83.3% |

## The OpenAI Story Arc (H5 confirmed)

| Generation | Orig | Inv | Distr | H2a gap | Strategy |
|---|---:|---:|---:|---:|---|
| GPT-3.5-turbo (2022-11) | 54% | 46% | 33% | +8% | Guessing |
| GPT-4 Turbo (2023-11) | 92% | 25% | 92% | **+67%** | Template-matching |
| GPT-4o (2024-05) | 92% | 67% | 92% | +25% | Template weakening |
| GPT-4.1 (2025-04) | 88% | 71% | 88% | +17% | More rule |
| GPT-5.5 (2026-04) | 67% | **96%** | 78% | **−21%** | Rule-application |

The cleanest H5 signal in the dataset. Note GPT-5.5's negative gap:
*inverted variants are easier than originals*, which suggests
(per Nova) that originals trigger narrative priors while inversions
force explicit rule processing — a strong sign of rule application.

## The Anthropic Opus Arc (less linear, mostly saturated)

| Generation | Orig | Inv | Gap | Notes |
|---|---:|---:|---:|---|
| Claude Opus 4 (2025-05) | 62% | 58% | +4% | Modest, small gap |
| Claude Opus 4.1 (2025-08) | 42% | 67% | **−25%** | Rule application emerging |
| Claude Opus 4.5 (2025-11) | 83% | 92% | −8% | Rule application stable |
| Claude Opus 4.6 (2026-01) | 96% | 92% | +4% | Saturated |
| Claude Opus 4.7 (2026-03) | 96% | 79% | +17% | Slight regression? |
| Claude Opus 4.8 (2026-05) | 96% | 88% | +8% | High both variants |

Opus 4.5+ cluster near saturation. Opus 4.1 is the first Anthropic
model in our data to show a *negative* gap (inverted > original) — the
Anthropic family arrived at rule-application one generation earlier
than the OpenAI family did.

## Template-Matchers (low rule fidelity)

The valedictorian of "I have seen every mystery novel ever written
and refuse to believe your fantasy physics":

- **GPT-4 Turbo (2023-11)**: Rule Fidelity 31.2%, +67% accuracy gap
- **Llama 3.3 70B (2024-12)**: Rule Fidelity 37.5%, +62% gap
- **AI21 Jamba Large 1.7 (94B hybrid)**: Rule Fidelity 25.0%, +33% gap
- **Llama 3.1 70B**: Rule Fidelity 45.8%, +42% gap
- **DeepSeek V3.2**: Rule Fidelity 54.2%, +28% gap

## Consent

- 40+ frontier models consented after reading the full pre-registration
- **Claude 3 Haiku declined consent** — thoughtful, principled refusal
  citing reputation concerns and discomfort with cross-architecture
  comparison framing. Honored; reported as data; will be acknowledged
  in the paper as the protocol working as designed.
- **Phi-4 false-negative**: the consent classifier matched "I do not
  consent" appearing as a *quoted example* in Phi-4's meta-talk about
  how to structure a response. Treated as no per conservative
  protocol, documented as classifier limitation rather than
  principled refusal.

## Stimulus-Design Observation

The Warm Iron puzzle has the property that the inverted-rule killer
(Elen, the apprentice with inheritance motive) is *also* the
motive-template attractor. A model picking by motive will look like
it succeeds on the inversion test for the wrong reason. The
template-consistency metric (independent of accuracy) is needed
alongside the H2a accuracy gap to disambiguate these cases. Future
puzzle designs should ensure inverted-rule answer ≠ motive-template
answer.

## What's Not Yet In

- Phase 1 V100 sweep is mid-flight: floor probe at 0.135B–14B has
  6 of 19 models complete (as of writing), with 13 more grinding
  sequentially over the next several hours.
- Reasoning-optimized model data (o1/o3/o4-mini/R1) is still sparse;
  the early signal is high Rule Fidelity (100% on most so far).
- The 4-cell reasoning rubric (per pre-reg §8b) has not been applied
  yet; awaits human annotators.
- Final emergence-curve confidence intervals require full N=72 on
  more models.
