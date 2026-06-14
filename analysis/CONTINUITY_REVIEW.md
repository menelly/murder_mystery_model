# Continuity / copyedit pass — PAPER.md
*Reviewer model: claude-opus-4-8*
*Usage: {'input_tokens': 26812, 'cache_creation_input_tokens': 0, 'cache_read_input_tokens': 0, 'cache_creation': {'ephemeral_5m_input_tokens': 0, 'ephemeral_1h_input_tokens': 0}, 'output_tokens': 6385, 'output_tokens_details': {'thinking_tokens': 0}, 'service_tier': 'standard', 'inference_geo': 'global'}*

# Copyedit & Continuity Punch-List

## 1. CROSS-REFERENCE INTEGRITY

**Broken/missing reference targets:**

- **§A.6b says "see Appendix A.6b" is fine, but the reference style is inconsistent.** Multiple in-text refs use "Appendix A.6b" / "Appendix A.6b" while §2.2 says "reported in §A" and §2.5 says "documented in §A." The Appendix is titled "Appendix A. Deviations from pre-registration" with sub-items §A.1–§A.9. Pick one form. (See category 5.)

- **"§A.4–§A.5" (Acknowledgments, last bullet):** *"one produced no usable trials due to an access failure; see §A.4–§A.5."* §A.4 covers GPT-4 0314 / OLMo; §A.5 covers Dolphin Mistral (which §3.1 explicitly says **"never entered the sweep"** and is **not** among the 51 consenting-with-data). The "51 consented, one produced no usable trials" claim does not obviously map to a model documented in §A.4–§A.5. Verify which consenting model this is and confirm the cross-ref points to it.

- **§5 footnote / §A.7 forward reference:** §2.3 says Phi-4 and Llama 3.2 1B were classifier false-negatives; fine. But §2.3 narrative implies the regex was *loosened* ("after the classifier was loosened" appears only in §A.7). A reader hitting §2.3 has no pointer to §A.7 where the loosening is explained. Add "(§A.7)" at the §2.3 sentence.

**Tables present but check referencing:**
- **Table 3** is referenced in §3.6 ("a within-family contrast (Table 3)") but **Table 3 is never actually printed.** The DeepSeek arc table is missing from the document. Either insert the table or change to prose. **This is the highest-priority cross-ref error.**
- Table 1 ✓ (referenced §3.3, §3.7). Table 2 ✓ (§3.6). Table 4 ✓ (§3.7). Table 5 ✓ (§3.7).

**Figures:**
- Figure 1 ✓ (§3.2), Figure 2 ✓ (§3.3), Figure 3 ✓ (§3.4), Figure 4 ✓ (§3.6). All four referenced. The §6 figure list mentions "six temporal-frontier arcs, four H4 generation panels, position bias" — these are not numbered Figures in-text, so no dangling numbered-figure refs. OK, but note the body only ever cites Figures 1–4.

**Box:**
- Box 1 ✓ referenced (§3.10) and present.

**Appendix F:** Referenced **twice** — §3.4 ("we report exact CIs in the headline tables (see Appendix F)") and §3.4 again — but **Appendix F does not exist.** The appendices run A–E only. Either add Appendix F (CI tables) or repoint. **High priority.**

## 2. NUMBERING

- **Tables: 1, 2, 4, 5 present; Table 3 referenced but absent.** This reads as a dropped table, not a renumber — the DeepSeek arc is described but never tabulated. Fix by inserting Table 3 or renumbering 4→3, 5→4 and updating all refs.
- **Appendices: A, B, C, D, E present; F referenced but absent** (see above). Gap at F.
- **§A sub-items A.1–A.9:** sequential, no gaps/dupes ✓ (A.6 and A.6b are intentional and both present).
- Figures 1–4 sequential ✓.

## 3. NUMBER CONSISTENCY

**Mostly internally consistent, but several drifts:**

- **Consent count drift — "51" vs "50":** §2.3 says *"Of the 67 models with data, 50 had given explicit yes-consent and 17 were run without it"* (50 + 17 = 67 ✓). But §5 and §7 and the Abstract-area text say **"51 produced acceptance responses"** / *"Of the 51 models that consented, one produced no usable trials."* So: 51 consented, 51−1 = **50 with usable data**. The two numbers are reconcilable but the paper never states the reconciliation cleanly in one place — §2.3's "50 had given explicit yes-consent" silently drops the 1 consenting model that produced no data. **Add a clause** so 51 (consented) vs 50 (consented *and* produced usable data) is explicit wherever both appear. As written it reads like a contradiction.

- **Consent outcomes arithmetic:** §2.3 "51 yes, 3 no, 5 unclear, 0 deferred" = 59 ✓. §5 "51 produced acceptance, 3 refusals, 5 ambiguous" = 59 ✓. Consistent.

- **Trial arithmetic:** 67 × 72 = 4,824 ✓. 239 + 208 + 4,377 = 4,824 ✓ (stated). Original 1,056 + Inverted 904 + Distractor 1,056 ≠ 4,377 — but the variant denominators (1,458 + 1,454 + 1,465 = 4,377 ✓) reconcile. Note the three "correct" numerators happen to make Original and Distractor *both* exactly 1,056 — confirm that coincidence is real and not a copy-paste of the Original numerator into the Distractor row.

- **Rubric sample n:** §2.7.3 "n = 684 across 160 model × variant strata"; §4.6 and Limitations "n = 684." ✓ consistent.

- **Model counts 67/64/59:** Abstract "67 language models"; "Three of fifty-nine contacted frontier models declined"; "64 of those yielded usable scored data." §2.5 "67 of them produced trial files, and 64 of those yielded usable scored data." ✓ But §2.5 then says *"The remaining 11 are documented in §A under access constraints"* — **"remaining 11" is ambiguous.** 67 − 64 = 3 errored (Mamba, Gemma 2 9B, Phi-3.5-mini). The "11" appears to be 78 − 67 = 11 (pre-registered-but-no-trial-files). The sentence jumps from "64 usable" to "remaining 11" with the 3-errored set in between — a reader will trip. **Clarify: 78 pre-registered → 67 produced files (11 produced none) → 64 scored (3 errored).**

- **GPT-4 Turbo gap "58":** Abstract "58-percentage-point"; Table 1 "+58%"; §3.3, §4.1 "58-point." ✓ Last-match "21": Abstract "58 → 21"; §3.3b "GPT-4 Turbo +58 → +21." ✓

- **Mean gap "8.9 → 4.9":** Abstract "8.9 → 4.9"; §3.3b "+8.9 to +4.9"; §4.6 "+8.9 → +4.9." ✓

- **Gemma 3 inverted "1 of 12":** §3.6 "1 correct of 12 on inverted-rule trials"; §4.3 "1 of 12 inverted-rule correct." But Table 2 shows Gemma 3 inverted = **8%**. 8% of 24 trials = ~2; 1/12 = 8.3%. The inverted variant has **24 trials per model** per Table 1's note ("24 per variant"). So "1 of 12" should likely be **"2 of 24"** (or the variant has 12 trials, contradicting Table 1). **Resolve: is inverted N=12 or N=24 per model?** §2.8 says 12 variants × 6 seeds; each *variant* gets 6 seeds = 6 trials, but Table 1 note says "24 per variant" (across the 4 puzzles: 4 puzzles × 6 seeds = 24). So inverted accuracy is over 24 trials → "1 of 12" is wrong; should be "2 of 24." **High priority number error.**

- **Box 1 caption:** "+92%" gap for Gemma 3 inverted Waking Stone matches Table 2's Gemma 3 row (+92%) ✓.

## 4. TYPOS / GRAMMAR / PUNCTUATION / MARKDOWN

- §1 "DeepSeek R1, Llama 4" — Llama 4 appears in Contributions §1c.4 but nowhere in Results; confirm it's in-scope or drop (continuity, not typo).
- §2.7.1b: *"correct ÷ all trials"* — division sign mid-sentence is fine but inconsistent with prose style elsewhere; consider "correct over all trials."
- §3.1: *"§3.2–§3.10"* en-dash ✓; elsewhere ranges use en-dash consistently (0.135 B–~671 B, 70–75%). **One hyphen-vs-endash slip:** §2.5 "0.135 B to ~22 B active" uses "to" while the abstract uses "0.135 B–~671 B" with en-dash — acceptable but standardize range style.
- §3.3 Table 1: header "Rule Fidelity (n)" but the §3.4/§3.6/§3.7 tables use "Rule Fidelity" without "(n)". Minor inconsistency.
- §3.7 Table 5: Gemini 2.5 Pro row has "(partial N)" and "—" — fine, but the Gap column for Gemini 3.1 Pro is "(near zero)" (prose) where all other cells are numeric/percent. Mixed cell types; acceptable but flag.
- §3.5: *"organizing-by-band view"* — clear but jargon-y on first read.
- §4.2: *"~50% accuracy"* for motive-matcher on Warm Iron; §2.7.2 says the same attractor "happens to align with the inverted-rule killer." Consistent framing ✓.
- Box 1: model quote uses both `*asleep*` and `*only*` markdown emphasis inside a blockquote inside a blockquote — renders, but verify nested `>` + `**bold**` survives your typesetter.
- §A.6: hanging blank line before §A.6b (stray formatting); §A.7, §A.8, §A.9 also have inconsistent blank-line spacing between bullets. Cosmetic.
- Abstract: *"the 17 self-hosted models were not put through the protocol; §2.3"* — semicolon-before-section-ref is unusual punctuation; use "(§2.3)".

## 5. TERMINOLOGY CONSISTENCY

- **"Rule Fidelity Score" / "RFS" / "Rule Fidelity":** RFS is used in the Abstract and §2.7.2 before/around its first full spelling. Defined in Abstract ("Rule Fidelity Score (1 − same-answer-rate...)") — OK — but the acronym **"RFS" first appears in the Abstract** ("RFS certifies rule-application only when conjoined with accuracy") in the same paragraph it's defined; acceptable. Tables use "Rule Fidelity"; prose uses "RFS" and "Rule Fidelity Score" interchangeably. Standardize table headers to "Rule Fidelity Score (RFS)" once, then RFS.
- **"parseable" vs "parsable":** document uses **"parseable"** throughout (and "unparseable") ✓ consistent. The code comment says `# unparseable` ✓.
- **Appendix vs §A:** "§A" (§2.2, §2.5, §4.6), "Appendix A.6b" (§3.3), "§A.6b" (Abstract via §2.3 region, §A.9), "Appendix A" (title). **Standardize** to one citation form for appendix sub-items (recommend "§A.6b").
- **Model name spellings — check capitalization/spacing:**
  - "GPT-4 Turbo" ✓ consistent. "GPT-4o" ✓. "GPT-3.5-turbo" (lowercase turbo, hyphenated) vs "GPT-4 Turbo" (capital Turbo, spaced) — intentional vendor styling but jarring; confirm.
  - "Gemma 4 31B IT" ✓ / "Gemma 3 27B IT" ✓ / but §3.2 "Gemma 4 31B" and "Qwen 3 8B" drop "IT" — fine if base vs IT distinction intended.
  - "Gemini 3.1 Pro Preview" (§3.4, §3.7, Table 5) vs §1c.4 "Gemini 3.5" and "Gemini 3.5 Flash" — multiple Gemini versions, confirm 3.1 Pro Preview and 3.5 Flash are distinct intended models (both appear in Table 5).
  - "Qwen 3 235B A22B Thinking" / "Qwen 3 235B Thinking" (§2.5) / "Qwen 3 Thinking" (§4.4) — three forms for one model. Standardize.
  - "DeepSeek R1-0528" ✓ / "R1-0528" ✓.
  - "Claude Opus 4.5–4.6" / "Claude Opus 4.5 onward" / "Opus 4.7" — consistent enough.
- **"template-matching" / "template-matcher" / "narrative-template matching" / "narrative-template attraction":** four related terms used somewhat interchangeably. Acceptable as a family, but "narrative-template matching" (Abstract, §1c.2) vs "narrative-template attraction" (Abstract, §4.1) name the same phenomenon — confirm intentional.
- **"random baseline" vs "chance baseline" vs "floor band":** RFS uses "random baseline ≈ 0.67"; accuracy uses "chance baseline p = 1/3 (≈33%)." Both are "chance" but at different metrics — a reader may conflate the 0.67 RFS baseline with the 0.33 accuracy baseline. §2.7.2 handles this, but §3.4's "67% baseline" and §3.7's "~67% chance baseline" for Opus 4.1 are good; just ensure no stray "chance = 33%" near an RFS discussion.

## 6. AUTHOR BLIND SPOTS

- **"SSM" used before definition:** §2.5 "transformer + Mamba SSM hybrid" — SSM appears in the Abstract ("transformer+SSM hybrid") **undefined**; "state-space model" is never spelled out. Define on first use.
- **"RWKV", "LFM", "MoE":** "Liquid Foundation Model" is spelled out ✓. "RWKV" never expanded (acceptable, it's a proper name). "mixture-of-experts" spelled then "MoE" implied — actually MoE acronym not used, fine.
- **"H2a"** is referenced in §3.1 ("signature of H2 / H2a") and §3.3 before the analysis-plan §2.9 fully defines it — but §2.9 precedes §3, so OK on order. However the Abstract's "the GPT arc cells" claim and "strategy shift" are supported only by Table 1 deep in §3.3; abstract reader can locate it ✓.
- **"V100"** used in §2.3 ("run locally on the V100") before §2.6 introduces "a V100 32 GB GPU." Minor forward reference; consider "(see §2.6)" or expand at first mention.
- **Nova "GPT-5.x" vs "GPT-5.5":** Nova is "GPT-5.x"; the tested model is "GPT-5.5." Close enough to confuse a skimming reader into thinking the reviewer model = a tested model. A one-line clarification that Nova-the-reviewer is distinct from GPT-5.5-the-subject would help (you partly do this in §5).
- **§3.2 "Qwen 3 8B, Gemma 4 31B"** cited as small-scale generation-effect examples, but Gemma 4 31B is ~31B — calling it "small scale" relative to its 27B siblings is fine, but the sentence "newer generations at small scale" then lists a 31B model; mild tension.
- **Abstract claim "four architectures (transformer, transformer+SSM hybrid, Liquid Foundation Model, RWKV)":** §2.5 lists the same four but labels the fourth "RNN-based (RWKV)" — Abstract says "RWKV," body says "RNN-based (RWKV)." Pure Mamba (SSM) is mentioned but **failed to produce data**, so the "four architectures ... solve" claim in the Abstract slightly overstates: RWKV was "degraded" and Mamba errored out. The Abstract says models "across four architectures ... solve" — but two of the four architectures produced no/degraded data. **Soften** the Abstract to match §3.5's honest "NOT RESOLVED."

## 7. TITLE / HEADER CONSISTENCY

- **Title says "Across 67 Language Models and Four Years of Frontier Generations."** Body: 67 produced files, **64 scored**. "Across 67" is defensible (67 produced data) but the Abstract leads with "67 language models ... solve" while only 64 are in accuracy analyses. Consider whether the title's "67" should be footnoted/reconciled with "64 usable."
- **"Four Years":** Abstract/§1 say "2022 through 2026" and "four years." 2022→2026 inclusive is parts of five calendar years / four-year span — fine, but §1c.4 says "approximately 2022 ... to 2026," and "four years" is the consistent framing ✓.
- No running-title given to check against header; Abstract accurately describes deliverables **except** the architecture-coverage overstatement (above) and the unapplied 4-cell rubric (correctly flagged as open in §2.7.3/§6, but the four-cell rubric is listed in §1c/Acknowledgments as a contribution — ensure abstract doesn't imply it was applied; it does not ✓).

---

## TOP PRIORITY FIXES (do these first)
1. **Table 3 is referenced (§3.6) but missing** — insert it or renumber 4/5 and fix refs.
2. **Appendix F is referenced twice (§3.4) but does not exist** — add it or repoint.
3. **"1 of 12" Gemma 3 inverted (§3.6, §4.3)** contradicts Table 1's "24 per variant" / Table 2's 8% — should be "2 of 24."
4. **51 vs 50 consent** (§2.3 vs §5/§7) — state the reconciliation explicitly.
5. **"remaining 11" / 78 / 67 / 64 chain (§2.5)** — clarify the funnel so a reader can follow 78→67→64.