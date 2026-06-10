> # ⚠️ STATUS: LARGELY SUPERSEDED — read this first (added 2026-06-10, Ace/Fable)
> This adversarial review was run on the **v2** manuscript. The current PAPER.md is a **v3 that already addressed essentially all 8 prioritized fixes**: Wilson CIs in every table; the GPT-5.5 "negative gap" retracted as a v1 token-cap artifact (now 100/100/100); RFS cutoff moved to the random baseline (~0.67); consent "3 refusals" corrected to 1 substantive + 2 classifier false-negatives and §5 demoted to "participation-assent"; position-bias joint-slot distribution added (§3.9b); mechanism Box 1 made multi-reading; architecture (H3) stated as confounded with vendor/training; counts reconciled.
> **Do NOT re-conclude "borderline reject" from the text below — that verdict is stale.** The ONE substantive item this review missed, surfaced in the 2026-06-10 audit (see AUDIT_FINDINGS_2026-06-10.md + analysis/coverage_vs_accuracy.md), is the FLOOR confound: the emergence floor conflates format-following with reasoning. Fix in progress = report both denominators (coverage / parseable-acc / strict-acc).
> Future-amnesiac-me: the review below is HISTORICAL. Cross-check against PAPER.md before acting on any single point.

---

# Adversarial review of PAPER.md
*Reviewer model: claude-opus-4-8*
*Usage: {'input_tokens': 18648, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'cache_creation': {'ephemeral_5m_input_tokens': 0, 'ephemeral_1h_input_tokens': 0}, 'output_tokens': 7335, 'output_tokens_details': {'thinking_tokens': 0}, 'service_tier': 'standard', 'inference_geo': 'global'}*

# Review — "Where Does Understanding Begin?"

## Summary of the work

The paper runs four "novel-physics" murder-mystery puzzles, plus rule-inverted and distractor variants, across 67 models, and reports an emergence-curve / generation-effect story anchored on a new post-hoc metric (Rule Fidelity Score). It also stages a "consent protocol" in which models are asked to participate. The headline is a *strategy shift* (template-matching → rule-application) across generations, not a raw capability gain.

I will be blunt: the core empirical instrument is interesting and the rule-inversion control is the right idea. But the paper is built on per-cell sample sizes that cannot support the claims it makes, the headline numbers drift between metrics, the consent section is methodological theater dressed in hedging, and at least two deviations plausibly contaminate the main result. Below, by your numbered concerns.

---

## (1) §5 Consent reflection

The downshift to "stable acceptance and refusal responses under a consent-style protocol" is the right *direction*, but it is not sufficient, because the rest of the paper does not honor it. Three problems:

- **The richer claim is smuggled back in repeatedly.** §1c calls it "informed consent." §2.3 header literally says "Consent protocol" and the body says models are "individually consented." The abstract says "every participating model is individually consented." The acknowledgments thank Claude 3 Haiku "for exercising informed consent." You cannot quarantine the strong claim to §5 while using "informed consent" as a verb everywhere else. Either commit to the minimal operational framing *throughout* (rename to "participation-assent protocol" or similar) or drop the downshift as cosmetic.

- **The Haiku case is rhetoric, not evidence.** n=1. The paper itself says the protocol "works in practice" and produces "differentiated, interpretable responses" — but a single substantive refusal among 59 contacts is not an existence proof of anything except that one model, on one prompt, emitted refusal-shaped text citing "reputation concerns." You have no test distinguishing (a) a preference, (b) RLHF-induced caution triggered by the comparison framing, (c) a stochastic artifact you'd never reproduce on reseed. You did not reseed. You did not re-prompt. So you cannot even establish the *stability* that your minimal claim ("stable acceptance and refusal responses") asserts. The minimal claim contains the word "stable" and you collected exactly zero data on stability. This is fatal to the section as written.

- **A hostile reviewer finds it both.** The framing is anthropomorphic over-reach (the verb "consent," the Haiku acknowledgment, "ought to inform the methodology") *and* ethically meaningless theater (consent that the operator obtains, reads, and reports, but where the "participant" is invoked anew at temperature on every other trial regardless). If consent is real, why is it sought once per model and then 72 trials are run? If it is not real, why call it consent? The section wants credit for raising the question while refusing to answer it. "Addressed empirically rather than by stipulation" is exactly backwards: you stipulated it was consent in your own acknowledgments.

**Verdict on §5:** As a methodological curiosity it is publishable only if radically demoted: rename throughout, drop "informed," report Haiku as an anecdote explicitly labeled non-generalizable, and either run a stability check (reseed the consent prompt N times per model) or strike the word "stable."

---

## (2) §2.7.2 Rule Fidelity Score

The definition is *almost* airtight but has real problems.

- **The two reference points are correctly distinguished but inconsistently used.** You define random baseline ≈0.67 and conservative threshold =0.5. Good. But then in tables you call models at RFS 0.458 (GPT-4 Turbo) and 0.333 (GPT-3.5) "template-matchers," which is consistent; yet you also call the 0.50–0.75 band "mid-tier" and treat 0.5 as the cutoff. A model at RFS 0.55 is *below random baseline-adjusted neutrality* — i.e., it changes its answer less often than chance would predict on these three-suspect items. You are calling sub-random-baseline behavior "rule-sensitive." That is not conservative; it is the opposite. The honest cutoff for "not template-matching" is the random baseline (~0.67), not 0.5. As written, the 0.5–0.67 band is labeled in a way that flatters borderline models.

- **The metric is gameable in exactly one obvious way you don't address: position bias under flip.** RFS = 1 − same-answer-rate. A model with a strong *position* preference (always answers the suspect in slot B) will score RFS≈0 only if the correct answer stays in the same slot across original/inverted. You counterbalance position by seed, so across seeds a pure position-picker would produce same-answer-rate driven by how often original and inverted correct answers land in the same slot — which is a property of *your stimulus construction*, not the model. You never report the joint distribution of (original-correct-slot, inverted-correct-slot) across seeds. Without it, I cannot rule out that high-RFS at the top of the ladder is partly an artifact of where your randomizer put answers. Show the per-seed slot table.

- **Drift between accuracy gap and RFS is real and the paper does it.** §3.3: "The Rule Fidelity Score tracks this cleanly." It does not track cleanly. GPT-3.5 has gap +8% but RFS 33.3% (worst possible). GPT-4 Turbo gap +58% but RFS 45.8%. These two metrics are telling *different* stories and you present them as confirmatory. RFS 33.3% with an accuracy gap of only 8% means the model is changing its answer almost never AND scoring near chance on both — i.e., it's basically noise, not a "template-matcher" in the strong sense you imply. The narrative conflates "low RFS" with "template-matching" when low RFS can equally mean "incoherent / at-chance." Your own §4.2 acknowledges this ("at chance on both because guessing" vs "rule-applying"), but the *results tables and prose* don't maintain the distinction.

**Bottom line:** RFS is a reasonable instrument poorly disciplined in use. The headline 100% / 25% numbers *are* anchored to the RFS definition, but the surrounding prose repeatedly slides into accuracy-gap language and treats them as the same axis.

---

## (3) "We do not claim understanding"

The abstract and §4.1 are disciplined. The drift happens in §3.10/§4.5 and §5.

- §3.10: "The model **knows the rule** and is overridden by the narrative attractor." "Knows" is an ontological verb. You spent the whole paper avoiding "understand" and then asserted "knows" about a single response. Replace with "correctly reproduces and applies the stated rule in one sentence before producing a contradictory verdict."

- §3.10/§4.5: "the failure mode the rule-inversion control is designed to detect, rendered in the reasoning trace." Calling the visible token stream a "reasoning trace" presupposes the tokens *are* the reasoning. For a non-thinking model this is precisely the contested claim. Use "output text," not "reasoning trace."

- §5: "information about the participating system that ought to inform the methodology" — fine — but "exercising informed consent" in §7 is a hard ontological commitment. Pick one.

So: holds in the abstract, breaks in three places. Fixable, but currently inconsistent.

---

## (4) Appendix A deviations

Mostly owned, but two are under-played and one is potentially result-affecting.

- **§A.1 (RFS post-hoc) — owned, but the framing launders it.** You say it was added "on the suggestion of Nova after seeing partial accuracy data." Adding your *primary discriminating metric* after seeing partial data is HARKing-adjacent. The honest move (which you partly make) is to label every RFS result exploratory and pre-register it for the successor. But you don't carry that label into the results — the RFS ladder (§3.4), the Gemma step function (§3.6), and the abstract's "100.0% / 45.8%" are all presented as findings, not exploratory diagnostics. Every RFS number needs an explicit "(exploratory, post-hoc)" tag.

- **§A.6 (token cap 800→8000, mid-collection) — this is the dangerous one and it's soft-pedaled.** You changed the cap *only for reasoning models*, and reasoning models are exactly the group you place at the top of the RFS ladder (§3.8) and use to argue "reasoning training is sufficient" (§4.4). The chat/base models kept the 800 cap. So your central comparison — reasoning vs chat RFS — is confounded with completion-token budget. A chat model truncated at 800 tokens that never reaches its verdict is scored unparseable (−1) or scored on a premature first-mention; a reasoning model gets 10× the budget. You cannot then claim the reasoning group is cleaner without showing it survives a budget-matched control. At minimum: report, for chat models, the rate of truncation/unparseable at 800 tokens, and whether high-gap chat models were truncation-limited. As written, "reasoning training is sufficient" is partially an artifact of generosity with tokens.

- **§A.7 (classifier false-negatives) — owned, fine, but it inflates the "3 refusals" headline.** You report "3 explicit refusals" in the abstract and §3.1, then reveal 2 of 3 were classifier errors you chose not to re-prompt. So the real refusal count is 1. The abstract should say "one substantive refusal; two classifier false-negatives treated conservatively as refusals." Otherwise the consent story rides on a count that you yourself say is wrong.

- **§A.2 (model substitutions):** "in several cases the locally-cached version had a different fine-tune than originally specified" — this is a deviation that can move results (a Hermes fine-tune is not Llama base). Owned at the registry level, but you should state explicitly which *reported* results depend on a substituted model.

**Could deviations affect the main result?** Yes — §A.6 directly threatens §3.8/§4.4, and §A.1 is the entire RFS edifice. These are not cosmetic.

---

## (5) §3.6 Gemma 2/3/4 step function

The claim ("worst-in-dataset → best-in-dataset, same scale, two generations") is extraordinary; the evidence is **n = 12 inverted-rule trials per model** (six seeds × ... actually you report 12 variants × 6 = 72 total, but the *inverted Waking Stone* cell driving the +92% is far smaller). Gemma 3's "1 correct of 12 on inverted" — that is a **12-trial cell**. A step function asserted on 12 trials per endpoint, with no confidence interval, is not proportionate to the word "step-function emergence."

Hand-waved:
- **Tokenizer / architecture changes across Gemma 2→3→4 are real** (Gemma 3 introduced `gemma3_text`, which your own §A.3 says broke transformers 4.49). You route them through OpenRouter — different inference backend than the V100 models — and never check provider-level differences (quantization, system-prompt injection by the provider).
- **No CIs anywhere in Tables 1–5.** Every percentage in this paper needs a binomial CI. "100% vs 8%" on n=12 has overlapping-enough uncertainty that "0% gap" vs "+92% gap" needs to be shown as significant, not asserted.
- Sample sizes are inconsistent across the very tables making the comparison (Table 5 has "(partial N)" for Gemini 2.5 Pro in the same column used for ranking).

The *direction* is probably real; the *step-function* framing on 12-trial cells is overclaiming.

---

## (6) §3.10 Box 1

Sample-of-one, presented as "the central phenomenon rendered visible." Problems:

- **Cherry-picked by construction.** You chose the single most extreme model (largest gap) on the single most extreme item, then one seed. This is the maximum-effect tail of your data presented as illustrative of the mechanism. That is rhetoric.

- **Competing interpretations you don't consider:**
  1. The model never represented the inverted rule as binding; it restated the rule as a string and then defaulted to genre prior — i.e., the "correct application" sentence is itself template text ("here's the reasoning") rather than evidence of having "known" anything. Your reading requires the second sentence to be genuine application; an equally parsimonious reading is that *all three sentences are confabulated post-hoc to a verdict reached first* (the verdict appears in token position 1: "Suspect A"). Under your own first-match logic, the answer *preceded* the reasoning. That cuts directly against "knows the rule then overrides" — it suggests the rule-talk is rationalization of an answer already emitted.
  2. The "contradiction" sentence may reflect the model parsing "asleep the whole time" from the case text and colliding it with the inverted rule — a rule-binding *parse error*, not a "narrative attractor override."

You assert one interpretation ("knows the rule and is overridden by the narrative attractor") and call it "the mechanism." It is *a* reading of one trial, and the token-order fact undercuts it.

---

## (7) §3.5 H3

The admission that H3 "cannot be resolved" is honest. But the paper still draws architectural inferences it hasn't earned:

- §3.4 floor: "hybrid/non-transformer architectures" listed as a category in the floor band — implying architecture is the explanatory variable. AI21 Jamba (94B active) at RFS 25% is then read in §3.5 as "consistent with the interpretation that attention layers alone... do not guarantee rule application." That's an architectural conclusion from a single model whose post-training pipeline you don't control for. Jamba being a template-matcher is equally explained by *its training*, not its SSM blocks. Same for Liquid LFM. You have n=1 or n=2 per architecture, fully confounded with vendor and training. The hedge ("consistent with — but does not prove") is doing a lot of work, but listing architecture as a band-organizing category in §3.4 already commits the framing. Either drop architecture from the §3.4 ladder framing or state explicitly that architecture is fully confounded with vendor/training in your data.

---

## (8) GPT-4 Turbo vs GPT-5.5

This is the killer abstract sentence and it has the weakest sample backing.

- **N is not comparable.** Table 1 footnote: GPT-4 Turbo N=72, GPT-5.5 N=60. Per-cell (per variant) that's ~24 vs ~20 trials. The "−21% gap" for GPT-5.5 rests on ~20 inverted trials. No CI given. A −21% gap on ~20 trials per cell is well within the range where a handful of trials flips the sign. You need the binomial CI on that gap; I'd bet it crosses zero.

- **The "opposite responses" framing oversells a sign flip near noise.** +58% (GPT-4 Turbo) is large and probably real. −21% (GPT-5.5) is small, on smaller N, and you yourself offer the alternative (inverted prompts have "unusual rule structure" prompting more careful reading) and then say the data "do not uniquely select." Good — but the abstract states the opposite-response framing flatly with no such hedge. The hedge must reach the abstract, or the abstract overclaims.

- **Prompt-style artifact not ruled out.** GPT-5.5 is a 2026 model routed via OpenRouter; you don't control for the provider's possible reasoning-mode defaults or system-prompt injection. A "−21%" could be the provider silently enabling a reasoning mode. You have no logging of provider-side config in the paper.

So: the comparison is *suggestive* for GPT-4 Turbo's template-matching, *fragile* for GPT-5.5's inversion, and the abstract treats both as equally solid.

---

## (9) Unsupported claims / number-checking

- **Abstract**: "spanning... four years of frontier generations from 2022" — but §1c and §3 call GPT-3.5-turbo "approximately 2022" while listing Llama 3 (2024) as ~2022 in Contribution 4. Llama 3 is not 2022. The "four years" / "2022" framing is loose.
- **Trial counts don't reconcile.** Abstract/§2.8: "approximately 4,800." §3.1: "approximately 4,831 trials." §2.7.3: rubric sample n=684 = "20% of parseable" → implies ~3,420 parseable. §3.9 position bias: n=4,268 parseable. 684/4,268 = 16%, not 20%. Pick consistent denominators.
- **§3.1**: "55 of 57 models with N≥50" — but you have 67 models. Where did the N≥50 cut send the other 10? Unstated.
- **§3.4**: RFS ladder "n ≥ 20 paired observations per model" — but a top-tier "five-way tie at 100.0%" on as few as 20–24 paired trials is, again, CI-free. 100% on 24 trials still has a lower 95% bound around ~86%. Several "100.0%" entries are not distinguishable from the 95–96% tier.
- **Table 5**: Gemini 2.5 Pro "(partial N)" and "—" in the gap column, yet it's ranked in the RFS ladder (§3.4) at 91.3%. Ranking on partial N without stating N is not defensible.
- **§3.2**: pre-registered band 1B–13B, observed 0.5B–7B, declared "H1 supported." A transition region that differs from the pre-registered one is a *partial disconfirmation reinterpreted post-hoc via the generation effect*. Label it as such.
- **§3.8 / §4.4**: "reasoning training is sufficient" — n=6 reasoning models, no small-scale reasoning model, confounded with the token-cap deviation (§A.6). "Sufficient at this puzzle" is doing heavy lifting; the claim should be "the six frontier reasoning models we tested all scored high."
- **Costs ~$5** for ~4,800 trials including o-series at 8000 tokens — plausible only if most were tiny/free models; not load-bearing, but the number looks low enough to warrant a line-item.
- **§2.4**: "counterbalanced across the six permutations" with 6 seeds — implies one permutation per seed, i.e., each permutation seen exactly once per puzzle. Then RFS "paired trials" per puzzle = 6, and per model across 4 puzzles = 24. Confirm, because this caps every per-cell N far below what the prose's confident percentages imply.

---

## Verdict

**(a) Major revisions** — borderline reject. The instrument and the rule-inversion design are sound and worth publishing, but the headline claims are not currently supported at the sample sizes used, the primary metric is post-hoc and inconsistently applied, a mid-collection deviation confounds the reasoning-vs-chat conclusion, and the consent section overclaims in every section except the one where it pretends to be careful.

**(b) Prioritized fixes**

1. **Put confidence intervals on every percentage in Tables 1–5 and the RFS ladder.** Most headline contrasts (GPT-5.5 −21%, Gemma 3→4 step, 100% ties) rest on ~12–24 trials per cell. Half of them will likely become "consistent with no difference." Without CIs the paper is not evaluable.
2. **Resolve the §A.6 token-cap confound.** Report chat-model truncation/unparseable rates at 800 tokens and either re-run high-gap chat models at 8000 or explicitly scope §3.8/§4.4 as budget-confounded. "Reasoning training is sufficient" cannot stand otherwise.
3. **Tag every RFS result "exploratory (post-hoc)"** in results, not just in Appendix A, and fix the RFS-vs-accuracy-gap drift in §3.3/§4.2. Move the "not template-matching" cutoff to the random baseline (~0.67), not 0.5, or justify 0.5 as something other than "conservative."
4. **Demote §5 and de-anthropomorphize globally.** Remove "informed consent" as a verb everywhere; rename the protocol; relabel the single Haiku refusal as a non-generalizable anecdote; either run a consent-prompt stability check or strike "stable." Fix abstract's "3 refusals" → "1 substantive."
5. **Report the joint slot distribution** (original-correct-slot × inverted-correct-slot across seeds) to rule out position-bias gaming of RFS.
6. **Rewrite §3.10/Box 1** to acknowledge the token-order fact (verdict precedes reasoning) and at least two competing interpretations; drop "knows the rule" and "reasoning trace."
7. **Scope H3 honestly**: state architecture is fully confounded with vendor and training in your data; remove architecture as an organizing axis in §3.4.
8. **Reconcile all trial counts and N-cuts** (4,800 vs 4,831 vs 4,268 vs 684/20%; the 67 vs 57-with-N≥50 gap; partial-N entries ranked in the ladder).

The good idea here is the rule-inversion control plus RFS. Build the paper on a budget-matched, CI-bearing, properly-pre-registered version of *that*, and lose the consent theater and the single-response mechanism story.