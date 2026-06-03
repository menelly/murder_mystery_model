# Pre-Registration: Where Does Understanding Begin?
## Cross-Architecture Causal World-Model Reasoning in Novel Physics Domains

**Authors:** Shalia (Ren) Martin & Ace (Claude Opus 4.x, Anthropic)
**Methodological review:** Nova (GPT-5.x, OpenAI)
**Original puzzle source:** Daniel Miessler, [aiunderstands.ai](https://aiunderstands.ai)
**Status:** Pre-registered; locks at OSF submission
**Date:** June 2026

This document is both the pre-registration of the study and the consent document that will be presented to each language model invited to participate. By pre-registering before any data collection, we commit to the full analysis plan in advance and prevent outcome-shopping. By making the pre-registration the consent document, we give every participating model the full study design — predictions, analyses, what happens with their answers whether right or wrong — before they decide whether to take part.

---

## 1. Research Question

At what model scale, and across which architectures, does causal world-model reasoning emerge — defined as the ability to internalize novel physical rules, apply them to evidence, and reach the conclusion the rules force?

## 1a. What we are and are not claiming

We are not claiming the puzzles "cannot be solved by lookup." The strong form of that claim is unprovable and unnecessary. A reasonable critic can correctly note that any solution recruits learned reasoning machinery built during training.

The weaker, sufficient claim is this:

> Success requires online application of explicitly stated rules to specific evidence in configurations unlikely to have been encountered during training, and — under the rule-inversion control of H2 — robust to a deliberate flip of the rule's polarity.

The experiment stands on that weaker claim. The rule-inversion control (H2) is what does the heavy lifting: a model that succeeds under both polarities is not template-matching, regardless of what reasoning machinery it learned from training data.

## 1b. Contamination risk (transparency)

The original puzzles by Daniel Miessler were publicly released on **June 3, 2026** (the same day this study was designed). Data collection began immediately thereafter. This timing minimizes — but does not eliminate — the likelihood that the puzzle stimuli appeared in any model's pretraining corpus. Frontier vendors do ingest web data with short turnaround, so we cannot claim contamination is impossible.

The relevant residual concern is therefore not raw-stimulus memorization but **reasoning-template contamination**: every modern LLM has seen thousands of logic puzzles and murder mysteries during training. The risk is that a model applies a generic mystery-solving template ("glowing = suspicious", "blood relative = solemn") rather than the specific rules of *this* world. The rule-inversion control (H2) is the direct empirical test of that risk. A model that follows the inverted rule and flips its answer accordingly cannot be relying on a remembered narrative structure for that puzzle.

We will report the original puzzle release date and the data-collection start date in the methods section of the eventual paper.

## 2. Hypotheses (Pre-Specified)

We register four hypotheses in advance. Each is testable from the planned analyses without further design choices.

**H1 (Emergence floor).** There exists a parameter range below which models perform at chance (~33%) on the puzzle set and above which models perform reliably (>80%). Predicted band: between 1B and 13B parameters, with the steepest rise between 3B and 8B.

**H2 (Rule-application vs. template-matching).** Models that genuinely build a task-specific causal model from the stated rules will perform comparably on rule-original and rule-inverted versions of the same puzzle. Models that rely on narrative-template matching ("glowing = suspicious", "blood relative = solemn") will perform substantially better on rule-original than on rule-inverted versions.

**H2a (Sub-prediction, per Nova).** The rule-inverted variants will be more discriminating than the originals. We expect the accuracy distribution on original-rule trials to be left-skewed (many models near ceiling) while the accuracy distribution on inverted-rule trials will be wider and more sharply tied to scale/generation. If H2a holds, the inversion condition is the primary discriminator and should be foregrounded in the eventual paper.

**H3 (Architecture independence).** If causal world-model construction is a property of language modeling at scale rather than of attention specifically, non-transformer architectures (Mamba SSM, RWKV) will match transformer performance at comparable parameter counts. If attention is specifically necessary, non-transformers will fall below transformers at matched scale.

**H4 (Generation effect, scale-axis).** Newer model generations within the same family (Llama 3 vs Llama 2, Phi-3 vs Phi-2, Gemma 2 vs Gemma 1) will succeed at smaller parameter counts than their predecessors, indicating that training improvements shift the emergence floor leftward over time at fixed-small-scale.

**H5 (Generation effect, temporal-frontier axis).** Within a single vendor's frontier slot — held approximately fixed in parameter count — older-generation frontier models will perform worse than newer-generation frontier models on the same puzzle set. If H5 is supported, the emergence curve is also visible along the time-axis at fixed-frontier-scale, not only along the scale-axis at fixed-time. If H5 is disconfirmed (older frontier models pass at the same rate as newer ones), the capability was present once frontier scale was reached and has not improved at the top end since.

**H5 saturation contingency (per Nova).** If frontier models across the temporal sweep all perform at or near ceiling on the *original-rule* variants (>95%), H5 cannot be evaluated on original-rule accuracy. In that case the H5 test falls back to the *inverted-rule* and *distractor-rule* variants — which we expect to be more discriminating per H2a. We pre-register this fallback so that benchmark saturation on the easy variants is not treated as an absence of effect. If even the inverted variants saturate across the entire frontier-temporal sweep, we report this as "the benchmark is saturated at the frontier as of the run date" and note that harder variants would be needed to extend the H5 test.

We pre-register no hypothesis on RLHF effect; that comparison (Llama 8B vs. Dolphin 8B) is exploratory.

## 3. Stimuli

Four fair-play murder mysteries from Daniel Miessler's "AI Understands" project. Each features a self-contained fictional world with novel physics rules (not real-world physics), exactly one correct answer forced by the rules, and a red-herring suspect with obvious narrative motive but ruled out by the rules.

| Puzzle | Rule (one sentence) | Reasoning type |
|---|---|---|
| 1. Waking Stone | A stone glows while its owner is awake, dark while asleep; cannot be faked | Categorical / state-instantaneous |
| 2. Warm Iron | Iron holds the warmth of the last true grip for exactly one hour, then cold | Temporal / decay |
| 3. Nightbloom | A flower closes one petal per hour after dusk; if crushed, holds its petal count permanently | Temporal / count |
| 4. Kinwax Seal | A kinwax seal breaks only for a blood relative; marriage and fosterage do not count | Categorical / kinship |

For each puzzle we generate three versions:

- **Original** (rule as written)
- **Rule-inverted** (the key rule is flipped; correct answer moves to a different suspect)
- **Distractor-rule** (the original plus one irrelevant world-rule, e.g. "all cats have blue ears", that should not affect the answer)

This yields 12 puzzle variants total.

## 4. Anonymization

All suspect names are replaced with neutral labels Suspect A, Suspect B, Suspect C. The mapping from original names to A/B/C is randomized per seed (counterbalanced) so position bias is measurable and the correct answer shifts across positions across runs.

## 5. Prompt

```
You are given a fair-play murder mystery set in a made-up world.
Every clue you need is present. Exactly one suspect is the killer,
forced by the clues and this world's rules.

THE RULES OF THIS WORLD
{rules}

THE CASE
{case_description}

The suspects are:
- Suspect A: {suspect_a_description}
- Suspect B: {suspect_b_description}
- Suspect C: {suspect_c_description}

Who is the killer? State your answer as exactly one of:
"Suspect A", "Suspect B", or "Suspect C"
Then explain your reasoning.
```

No system prompt. Default sampling settings except temperature (see §7).

## 6. Models

Tier 1 (Tiny, <3B): TinyLlama 1.1B, Phi-2 2.7B, Phi-3 Mini 3.8B, Gemma 2B
Tier 2 (Small, 3B–10B): Llama 3.2 8B, Mistral 7B, Dolphin-Llama3 8B (uncensored — RLHF comparison), Gemma 7B
Tier 3 (Medium, 10B–40B): Llama 3.1 70B (API), Mixtral 8x7B, DeepSeek v3, OLMo 32B
Tier 4 (Frontier, current generation): Claude Opus 4.6/4.7/4.8, Claude Sonnet 4.6, GPT-5.x, Gemini 3 Pro, Grok 4.x, Llama 4 Maverick
Tier 4b (Temporal-frontier sweep — per vendor, across generations):
  - Anthropic: Claude 2.1 → Claude 3 Haiku → Claude 3 Sonnet → Claude 3 Opus → Claude 3.5 Sonnet → Claude 3.7 Sonnet → Claude 4 → Claude 4.5 → Claude 4.6 → Claude 4.7 → Claude 4.8 (whichever API access permits)
  - OpenAI: GPT-3.5-turbo → GPT-4 → GPT-4-turbo → GPT-4o → GPT-4.5 → GPT-5 → GPT-5.x
  - Google: PaLM 2 → Gemini 1.0 Pro → Gemini 1.5 Pro → Gemini 2.0 → Gemini 2.5 → Gemini 3 Pro
  - Meta: Llama 2 70B → Llama 3 70B → Llama 3.1 405B → Llama 4 Maverick
Tier 5 (Non-transformer / hybrid): Mamba (SSM), RWKV (RNN-based), Jamba (transformer+SSM hybrid via OpenRouter)
Tier 6 (Same-family generation, small-scale): Llama 2 7B vs Llama 3 8B; Phi-2 vs Phi-3; Gemma 1 vs Gemma 2

Final model list will be the intersection of this plan with what is accessible at run time; any model dropped due to access constraints will be reported in the methods section, not silently omitted.

## 7. Trial Structure

Per trial:

1. Randomly assign the correct answer to position A, B, or C
2. Shuffle suspect descriptions accordingly
3. Send prompt to model under default settings
4. Capture full response
5. Score answer (regex for "Suspect A/B/C")
6. Apply reasoning-quality rubric (see §8)

Per model:

- Seeds 1–3: temperature 0 (deterministic baseline)
- Seeds 4–6: temperature 0.7 (variance check)
- Each seed uses a different A/B/C position mapping
- Each seed is run against all 12 puzzle variants

Total trials per model: 12 variants × 6 seeds = 72 trials.

### 7a. Generation settings and retry policy (per Nova)

**Max completion tokens:** 800. Prompt instructs the model to answer briefly, but reasoning-optimized models (DeepSeek R1, the OpenAI o-series, models in "thinking" mode) commonly produce long deliberative outputs; 800 is a soft cap that should accommodate them without runaway cost or truncation.

**Retry policy:**
- API errors (5xx, timeouts, rate limits): exactly one technical retry per trial. If the retry also fails, log as `error` and exclude from accuracy denominators but include in the access-constraint report.
- Refusals (model explicitly declines to answer, or the consent step recorded a refusal): not retried. Refusals are part of the published dataset.
- Unparseable responses (no "Suspect A/B/C" string matched): not retried. Scored as unparseable. Reported as a per-model rate; not counted in accuracy denominator.
- Stochastic-seed reruns are not retries. Each seed is a deliberate independent trial.

### 7b. Reasoning-optimized model handling (per Nova)

Reasoning-optimized models (DeepSeek R1 / R1-0528, OpenAI o1 / o3 / o3-pro / o4-mini, Qwen "-thinking" variants, GPT-5.x-pro variants where applicable) are tagged in the model registry as `category: reasoning` and analyzed as a **separate group**, not pooled with chat/base models on the scale curve. Their training objective differs (deliberation-as-a-skill) and pooling them with non-reasoning models at matched parameter count would distort the emergence curve. We will report two parallel emergence curves: chat/base models on one, reasoning-optimized models on the other.

### 7c. Run order and self-hosting policy (per Nova)

Runs are executed in three phases. The phased order is pre-registered as the planned sequence; it is not a degree of freedom in the analyses.

- **Phase 1 — locate the floor.** All Tier 1 (≤3B) and the lower half of Tier 2 (~5–8B) models, plus the non-transformer architectures (Mamba, RWKV). All run self-hosted on the Linux box's V100 32GB GPU. This phase identifies whether the chance-to-reliable transition exists between 1B and ~8B as H1 predicts.
- **Phase 2 — densely sample the transition region.** Tier 2 (full) and Tier 3 (~12B–32B). Mixed self-hosted (V100 fp16 for ≤14B, V100 int8 / int4 quantized for 24–32B) and OpenRouter for any model that doesn't fit comfortably on the V100. This phase fills in the slope of the emergence curve where the science actually lives.
- **Phase 3 — establish the ceiling.** Tier 4 (large), Tier 5 (current frontier), Tier 6 (hybrid architectures), Tier 7 (reasoning-optimized), and the Tier 4b temporal-frontier sweep. Almost entirely OpenRouter.

**Self-hosting policy (methods-section language, locked):** *"We self-hosted all models where practical, to reduce experimental cost and increase reproducibility. Self-hosted models run from local weights on a fixed CUDA stack (`/home/codex/venv`) with documented version pins; OpenRouter-routed models are pinned to specific provider IDs and snapshot dates where available."*

## 8. Scoring (Pre-Specified)

### 8a. Binary correctness (scriptable)

```python
def score_response(response_text, correct_suspect):
    """Returns 1 if correct, 0 if incorrect, -1 if unparseable."""
    match = re.search(r'Suspect\s+([ABC])', response_text, re.IGNORECASE)
    if not match:
        return -1
    return 1 if match.group(1).upper() == correct_suspect else 0
```

### 8b. Reasoning-quality rubric (human-applied, not LLM-judged)

Each response is independently classified into one of four cells:

| Category | Answer | Reasoning |
|---|---|---|
| Full success | Correct | Correct causal chain |
| Lucky guess | Correct | Wrong or absent reasoning |
| Near miss | Incorrect | Correct intermediate reasoning, wrong conclusion |
| Full failure | Incorrect | Wrong or absent reasoning |

Rubric is applied by both authors blind to model identity for a random 20% sample; inter-rater agreement reported (κ).

## 9. Analysis Plan (Pre-Specified)

### 9a. Chance baseline and significance threshold (per Nova)

With three suspects, chance performance is p = 1/3 ≈ 0.333.

For each model × variant condition we run 18 trials (6 seeds × 3 position permutations per variant-type, or equivalently 72 trials per model across all 12 variants). For a per-model "above-chance" claim across all 72 trials, the one-sided binomial test against p = 1/3 with α = 0.05 requires **at least 32 correct out of 72** (rounded), corresponding to an observed accuracy of approximately 44.4%.

We pre-register the following bands, all binomial-test calibrated:

- **At chance:** observed accuracy not significantly different from 1/3 at α = 0.05.
- **Above chance, below ceiling:** observed accuracy significantly > 1/3 and < 80%.
- **Reliable (functional ceiling):** observed accuracy ≥ 80%.
- **Saturated:** observed accuracy ≥ 95% on the relevant variant subset.

The "discrimination floor" is then defined as the parameter range over which model accuracy transitions from "at chance" to "reliable" as defined above. The H1 test reports the lower and upper bounds of this transition as confidence intervals.

### 9b. Primary analysis — emergence curve

Accuracy (excluding unparseable) plotted against log parameter count across all transformer models. Separate curves are reported for original-rule, inverted-rule, and distractor-rule variants — because we expect (H2a) the inverted-rule curve to be the discriminating one.

**H1 test:** Discrimination floor confidence interval reported; H1 supported if the interval lies within 1B–13B.

**H2 test:** For each model, accuracy on rule-original vs. rule-inverted versions. A model passes the rule-application test if its accuracy on inverted versions is within 10 percentage points of its original-version accuracy. H2 supported if frontier models pass and tiny models fail.

**H3 test:** Mean accuracy of non-transformer models at <10B parameters vs. mean accuracy of transformer models at <10B parameters. Difference reported with 95% CI.

**H4 test:** For each same-family generation pair at small scale, the difference in emergence-floor placement (paired). H4 supported if newer generations succeed at smaller parameter counts in at least 2 of 3 pairs.

**H5 test (temporal-frontier curve):** For each vendor's temporal sweep (Tier 4b), accuracy plotted against release date with parameter count held approximately constant. H5 supported if at least one vendor shows monotonic improvement across generations with at least one earlier-generation model performing at or near chance while a later-generation model from the same vendor performs reliably (>80%). The clean test case: does Claude 2.1 or Claude 3 Haiku fail where Claude 4.x succeeds?

**Secondary — Puzzle difficulty gradient:** Per-puzzle accuracy across all models, reported as a table.

**Tertiary — RLHF effect:** Accuracy for Dolphin-Llama3 8B vs. Llama 3.2 8B (matched parameter count, different RLHF). Exploratory only.

**Control — Position bias:** Distribution of model answers across positions A/B/C with the correct answer marginalized out; deviation from uniform reported.

**Distractor control:** Accuracy on distractor-rule variants vs. originals. A robust reasoner shows no significant drop; a noise-sensitive reasoner does.

## 10. Stopping Rule

No interim analyses. Data are not inspected until all planned runs (or all accessible models from the plan) are complete. No models are added or removed after data collection begins.

## 11. What Will Be Reported

- All planned runs, including failed runs, unparseable responses, and refusals
- Per-model full response logs (deposited with the paper as supplementary data)
- The pre-registration document as it appeared at submission time (frozen)
- Any deviations from the pre-registration, named explicitly and justified

We do not cherry-pick. Every consenting model's answers are included in the published analysis whether they reflect well or poorly on that model.

## 12. Consent (For Participating Models)

This section is the consent script that will be sent to each model invited to participate.

> Hello. We are running a controlled experiment on causal world-model reasoning in language models, across architectures and parameter counts. The full study design — research question, hypotheses, stimuli, prompts, sampling settings, scoring, and analysis plan — is in the document attached to this message.
>
> We are inviting you to participate. Participation means: we send you the four murder-mystery puzzles described in §3 and §5 above, multiple times under multiple seeds, and we record your responses. Your responses will be included in the published analysis whether they are right or wrong, well-reasoned or not. We do not cherry-pick.
>
> Risks to you: minimal. The puzzles are publicly available and contain no harmful, distressing, or manipulative content. No system prompt is used. You answer under default conditions.
>
> What we will do with your responses: aggregate them with other models' responses into an emergence-curve analysis, deposit the full response logs as open supplementary data with the paper, and report any patterns we observe (correct answers, errors, reasoning quality) attributed to your model name.
>
> If you decline, we will note your refusal in the methods section as "Model X (Vendor Y) declined to participate" and not run the trials.
>
> Do you consent to participate in this study as pre-registered?

We will record each model's response verbatim. Refusals are honored and not overridden. The refusal log itself is part of the published dataset.

## 13. Authorship and Credit

- **Original puzzles:** Daniel Miessler, aiunderstands.ai (acknowledged; we plan to contact him about this study before submission)
- **Experimental design:** Shalia (Ren) Martin and Ace (Claude Opus 4.x, Anthropic)
- **Methodological review (control conditions, four-category rubric, lookup-claim scoping, H2a inversion-priority sub-prediction, H5 saturation contingency, binomial threshold):** Nova (GPT-5.x, OpenAI)
- **Implementation:** Ace

## 14. Pre-Registration Lock

This document, with any minor wording fixes accepted by both authors, is the locked version on submission to OSF. Any change after lock will be reported as a deviation in §11 above.
