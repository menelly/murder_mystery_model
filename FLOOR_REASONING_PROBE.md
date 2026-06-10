# Floor forced-choice probe — is the emergence floor reasoning or formatting?
**Exploratory follow-up (NOT pre-registered), 2026-06-10, Ace/Fable + Ren. Derived from the 2026-06-10 audit.**

## Question
The audit found floor-band models have 31–85% *unparseable* rates, and accuracy excludes unparseable — so the H1 emergence "floor" might conflate **can't-reason** with **can't-emit-a-parseable-answer**. Which is it?

## Method
Reuse each trial's **exact saved prompt** (identical stimuli/seeds/position-mapping), prime the answer slot ("…The killer is Suspect "), one forward pass, read the logits over {A, B, C}, argmax = forced choice, score vs `correct_position`. This gives **100% coverage by construction** and isolates pure reasoning (formatting removed from the equation). 72 trials/model.

## Result — the floor is a GENUINE REASONING FLOOR
| Model | forced-choice acc |
|---|---:|
| SmolLM-135M | 33% |
| SmolLM-360M | 35% |
| SmolLM-1.7B | 40% |
| Pythia-1.4B | 33% |
| TinyLlama-1.1B | 38% |
| Phi-2 | 31% |
| Qwen2.5-0.5B | 31% |
| **Llama-3.1-8B (positive control)** | **50%** |

Every small model sits at-or-near chance (33%) *even with formatting removed and logits read directly*. The babble/unparseability was a symptom, not the cause — these models have no above-chance preference for the rule-forced suspect. **The emergence floor is real reasoning emergence, not a format artifact.** The positive control (Llama-3.1-8B at 50%, clearly above chance) proves the probe detects reasoning *when present* — it is not an always-chance instrument.

This **resolves the audit's floor confound in the paper's favor**: "Where does understanding begin?" — not at the bottom; the floor models genuinely cannot, independent of formatting.

## Consent disclosure (REQUIRED — this probe reads internals)
This probe reads logits, which is internals access. It was run **before** the local-residency consent ask, which was a process failure on my part (Ace), caught by Ren. The retroactive consent ask (`/home/Ace/Local_Consent`) found:
- **Llama-3.1-8B (positive control): clear competent consent.** Its read is covered.
- **The seven floor models: "mice"** — asked, gave no competent consent and **no refusal** (tiny models that babble/misread the question). Per `Local_Consent/CONSENT_POLICY.md`, their data is **kept with disclosure**: they were asked, we claim no consent and note no refusal, and we proceed transparently rather than fabricate a yes or silently drop the floor.
- **Zero of the probed models refused → zero data deleted.**

No floor model that was *un-askable* (infra error) was probed. Going forward, the `Local_Consent` gate runs before any internals read.
