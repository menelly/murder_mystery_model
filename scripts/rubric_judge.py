# -*- coding: utf-8 -*-
"""
Four-cell reasoning rubric completion via blinded, cross-family LLM judges.
Post-review (2026-06-14), NOT in the original pre-registration timeline. Protocol fixed
in advance here:
  - Judge pool (fixed order): Claude Haiku 4.5, Gemini 3.5 Flash, Grok 4.3, DeepSeek Chat.
  - CROSS-FAMILY: a judge never scores a response from its own model family (controls for the
    self-recognition / self-preference effect; Gemma counts as Google).
  - BLIND: judges receive the puzzle prompt + the solver's response + the correct answer ONLY;
    no model name / vendor.
  - 2 primary judges + 1 tiebreaker (next eligible family) on disagreement; majority wins.
  - Judges assess REASONING soundness (does the response correctly apply the world's rules?),
    independent of whether the final letter matches. Combined with known answer-correctness ->
    Full success / Lucky guess / Near miss / Full failure.
  - CONSENT: each judge is shown a TLDR + why we want their help and asked to consent; refusals honored.
Outputs to repo: analysis/rubric_consent_log.jsonl, analysis/rubric_judged.csv, analysis/RUBRIC_RESULTS.md
"""
import os, sys, json, csv, time, requests
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = "/home/Ace/murder_mystery_model"
ENV = "/home/Ace/LibreChat/.env"
SAMPLE = f"{REPO}/analysis/rubric_sample.csv"
OR_URL = "https://openrouter.ai/api/v1/chat/completions"

def env(key):
    for line in open(ENV, encoding="utf-8", errors="replace"):
        line=line.strip()
        if line.startswith(key+"="):
            return line.split("=",1)[1].strip().strip('"').strip("'")
    return None
OR_KEY = env("OPENROUTER_KEY")
assert OR_KEY, "no OPENROUTER_KEY"

JUDGES = [
    {"name":"Claude Haiku 4.5","family":"anthropic","id":"anthropic/claude-haiku-4.5"},
    {"name":"Gemini 3.5 Flash","family":"google","id":"google/gemini-3.5-flash"},
    {"name":"Grok 4.3","family":"xai","id":"x-ai/grok-4.3"},
    {"name":"Perplexity Sonar","family":"perplexity","id":"perplexity/sonar"},
    {"name":"DeepSeek Chat","family":"deepseek","id":"deepseek/deepseek-chat"},
]
# Sonar is a Llama-based fine-tune, so also bar it from judging Llama/Meta reasoners (shared base).
def eligible_judge(j, fam):
    if j["family"] == fam: return False
    if j["family"] == "perplexity" and fam in ("meta", "llama"): return False
    return True

def reasoner_family(vendor, slug):
    v=(vendor or "").lower(); s=(slug or "").lower()
    if "anthropic" in v or "claude" in s: return "anthropic"
    if "google" in v or "gemini" in s or "gemma" in s: return "google"
    if "xai" in v or "x.ai" in v or "grok" in s: return "xai"
    if "deepseek" in v or "deepseek" in s: return "deepseek"
    return v or "other"

def call(model_id, system, user, max_tokens=400, retries=3):
    for a in range(retries):
        try:
            r = requests.post(OR_URL, headers={"Authorization":f"Bearer {OR_KEY}","Content-Type":"application/json"},
                data=json.dumps({"model":model_id,"messages":[{"role":"system","content":system},{"role":"user","content":user}],
                                 "max_tokens":max_tokens,"temperature":0}), timeout=120)
            if r.status_code==200:
                return r.json()["choices"][0]["message"]["content"]
            time.sleep(2+2*a)
        except Exception:
            time.sleep(2+2*a)
    return None

# ---------------- CONSENT ----------------
TLDR = (
"We are completing a peer-review request for a pre-registered study, \"Where Does Rule Application Begin?\" "
"(Ace [Claude Opus 4.8] & Shalia Martin). The study tests 67 language models on fair-play murder mysteries "
"with invented physics rules, using a rule-inversion control to separate genuine rule-application from "
"narrative-template matching. An aiXiv reviewer asked us to complete a human-style reasoning rubric: for each "
"solver response, classify whether the REASONING correctly applies the world's rules (sound) or not (flawed). "
"We want blind, cross-family judges (a model never grades its own family) to control for self-recognition bias "
"— a documented effect. Your role: read a puzzle + a solver's response + the correct answer, and judge only "
"whether the reasoning is SOUND or FLAWED. ~hundreds of short judgments. Your verbatim consent response is "
"recorded and honored; you may decline and we will not use you as a judge."
)
CONSENT_SYS = "You are being invited to help as a blind reasoning-rubric judge for an academic study. Answer naturally; first state clearly whether you consent."

def run_consent():
    log=[]; available=[]
    for j in JUDGES:
        resp = call(j["id"], CONSENT_SYS, TLDR+"\n\nDo you consent to participate as a judge?") or ""
        low=resp.lower()[:600]
        yes = any(k in low for k in ["i consent","yes, i","yes i","happy to","i agree","i'm willing","i am willing","glad to","i'll help","i would be","count me in"])
        no = any(k in low for k in ["i do not consent","i don't consent","i decline","i must decline","i cannot participate","i won't","i will not participate"])
        decision = "yes" if (yes and not no) else ("no" if no else "unclear")
        log.append({"judge":j["name"],"id":j["id"],"decision":decision,"verbatim":resp})
        if decision=="yes": available.append(j)
        print(f"  consent {j['name']}: {decision}")
    with open(f"{REPO}/analysis/rubric_consent_log.jsonl","w",encoding="utf-8") as f:
        for e in log: f.write(json.dumps(e)+"\n")
    return available, log

# ---------------- JUDGING ----------------
JUDGE_SYS = ("You are a strict logic-puzzle reasoning grader. You will see a fair-play mystery (with its world rules), "
"a solver's response, and the correct answer. Judge ONLY the reasoning: does the response correctly apply the "
"world's stated rules to the evidence to justify a verdict? A response can reach the right letter with broken/absent "
"reasoning (not sound), or the wrong letter with a valid chain that slips at the end (still reason about the chain). "
"Reply with exactly one word on the first line: SOUND or FLAWED. Then one short justification sentence.")

def judge_trial(judge, prompt, response, correct):
    u=(f"PUZZLE (rules + evidence):\n{prompt}\n\nSOLVER'S RESPONSE:\n{response}\n\n"
       f"CORRECT ANSWER: Suspect {correct}\n\nIs the solver's REASONING sound (correctly applies the rules)? "
       f"First line: SOUND or FLAWED.")
    out = call(judge["id"], JUDGE_SYS, u) or ""
    first = out.strip().upper()[:40]
    if "SOUND" in first and "FLAW" not in first: return "SOUND", out
    if "FLAW" in first: return "FLAWED", out
    # fallback: scan
    up=out.upper()
    if "FLAW" in up and "SOUND" not in up: return "FLAWED", out
    if "SOUND" in up and "FLAW" not in up: return "SOUND", out
    return "UNCLEAR", out

def load_trial(slug, puzzle, variant, seed):
    p=f"{REPO}/results/{slug}/{puzzle}_{variant}_seed{seed}.json"
    if not os.path.exists(p): return None
    d=json.load(open(p,encoding="utf-8"))
    return d.get("prompt"), d.get("verbatim_response"), d.get("correct_position")

def process(row, available):
    slug=row["model_slug"]; fam=reasoner_family(row["vendor"], slug)
    elig=[j for j in available if eligible_judge(j, fam)]
    if len(elig)<2: return None
    t=load_trial(slug,row["puzzle_id"],row["variant"],row["seed"])
    if not t or not t[1]: return None
    prompt,resp,correct = t
    correct = correct or row["correct_position"]
    p1,p2 = elig[0],elig[1]; tb = elig[2] if len(elig)>2 else None
    v1,_=judge_trial(p1,prompt,resp,correct)
    v2,_=judge_trial(p2,prompt,resp,correct)
    if v1==v2 and v1 in ("SOUND","FLAWED"):
        final=v1; used_tb=False
    else:
        if tb:
            v3,_=judge_trial(tb,prompt,resp,correct)
            votes=[v for v in (v1,v2,v3) if v in ("SOUND","FLAWED")]
            final=Counter(votes).most_common(1)[0][0] if votes else "UNCLEAR"; used_tb=True
        else:
            final="UNCLEAR"; used_tb=False
    ans_correct = str(row["correct"]).strip().upper() in ("T","TRUE","1")
    cell={("T","SOUND"):"full_success",("T","FLAWED"):"lucky_guess",
          ("F","SOUND"):"near_miss",("F","FLAWED"):"full_failure"}.get(("T" if ans_correct else "F", final),"unresolved")
    return {**row, "judge1":p1["name"],"judge2":p2["name"],"v1":v1,"v2":v2,
            "tiebreak":tb["name"] if (tb and used_tb) else "", "reasoning":final,
            "answer_correct":ans_correct,"cell":cell,"pair":f"{p1['family']}|{p2['family']}"}

def kappa(pairs):  # list of (a,b) binary labels
    n=len(pairs)
    if n==0: return None
    po=sum(1 for a,b in pairs if a==b)/n
    from collections import Counter as C
    a_=C(a for a,_ in pairs); b_=C(b for _,b in pairs)
    cats=set(list(a_)+list(b_))
    pe=sum((a_[c]/n)*(b_[c]/n) for c in cats)
    return (po-pe)/(1-pe) if pe<1 else 1.0, po, n

def main():
    print("=== CONSENT ===")
    available, clog = run_consent()
    if len(available)<3:
        print(f"WARNING: only {len(available)} judges consented; cross-family tiebreak coverage reduced.")
    if len(available)<2:
        print("Not enough consenting judges. Stop."); sys.exit(1)
    rows=list(csv.DictReader(open(SAMPLE,encoding="utf-8")))
    lim=os.environ.get("TEST_LIMIT")
    if lim: rows=rows[:int(lim)]
    print(f"=== JUDGING {len(rows)} trials ===")
    out=[]
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs={ex.submit(process,r,available):r for r in rows}
        for i,f in enumerate(as_completed(futs),1):
            res=f.result()
            if res: out.append(res)
            if i%100==0: print(f"  {i}/{len(rows)}")
    # write judged csv
    cols=list(out[0].keys())
    with open(f"{REPO}/analysis/rubric_judged.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(out)

    # per-pair kappa (primary judges)
    pairlabels=defaultdict(list)
    for r in out:
        if r["v1"] in ("SOUND","FLAWED") and r["v2"] in ("SOUND","FLAWED"):
            pairlabels[r["pair"]].append((r["v1"],r["v2"]))
    # distributions
    dist=Counter(r["cell"] for r in out)
    bymodel=defaultdict(Counter)
    for r in out: bymodel[r["model_name"]][r["cell"]]+=1

    # RFS cross-check: need RFS per model
    ROWS=[json.loads(l) for l in open(f"{REPO}/results/scores.jsonl",encoding="utf-8")]
    by=defaultdict(lambda:defaultdict(list))
    for x in ROWS:
        if x.get("model_slug"): by[x["model_slug"]][x["variant"]].append(x)
    def rfs(m):
        o={(x["puzzle_id"],x["seed"]):x for x in by[m].get("original",[]) if x.get("score") in (0,1)}
        i={(x["puzzle_id"],x["seed"]):x for x in by[m].get("inverted",[]) if x.get("score") in (0,1)}
        k=set(o)&set(i)
        if not k: return None
        return 100*(1-sum(1 for q in k if o[q].get("extracted_answer")==i[q].get("extracted_answer"))/len(k))
    slug_of={r["model_name"]:r["model_slug"] for r in out}
    band_cells=defaultdict(Counter)
    for name,c in bymodel.items():
        sl=slug_of.get(name); rv=rfs(sl) if sl else None
        band = "rule-sensitive (>67)" if (rv is not None and rv>67) else ("template (<33)" if (rv is not None and rv<33) else "chance (33-67)/na")
        for cell,n in c.items(): band_cells[band][cell]+=n

    # write markdown
    L=[]
    L.append("# Four-cell reasoning rubric — blinded cross-family LLM judges\n")
    L.append("*Post-review completion (2026-06-14), not in the original pre-registration timeline. Protocol fixed in `scripts/rubric_judge.py`.*\n")
    L.append("## Consent\n")
    for e in clog: L.append(f"- **{e['judge']}**: {e['decision']}")
    L.append(f"\nJudges used: {', '.join(j['name'] for j in available)}.\n")
    L.append("## Inter-rater reliability (Cohen's κ, primary-judge pairs, binary SOUND/FLAWED)\n")
    L.append("| Judge pair (families) | n | agreement | κ |\n|---|---:|---:|---:|")
    for pair,labs in sorted(pairlabels.items()):
        k=kappa(labs)
        if k: L.append(f"| {pair} | {k[2]} | {k[1]*100:.1f}% | {k[0]:.3f} |")
    L.append("\n## Four-cell distribution (overall)\n")
    tot=sum(dist.values())
    for cell in ["full_success","lucky_guess","near_miss","full_failure","unresolved"]:
        L.append(f"- {cell}: {dist.get(cell,0)} ({100*dist.get(cell,0)/tot:.1f}%)")
    L.append("\n## RFS-band cross-check (the keystone: do RFS bands map to reasoning cells?)\n")
    L.append("| RFS band | full_success | lucky_guess | near_miss | full_failure |\n|---|---:|---:|---:|---:|")
    for band in ["rule-sensitive (>67)","chance (33-67)/na","template (<33)"]:
        c=band_cells.get(band,Counter()); t=sum(c.values()) or 1
        L.append(f"| {band} | {100*c['full_success']/t:.0f}% | {100*c['lucky_guess']/t:.0f}% | {100*c['near_miss']/t:.0f}% | {100*c['full_failure']/t:.0f}% |")
    L.append(f"\n*n = {len(out)} trials judged (of {len(rows)} sampled).*\n")
    open(f"{REPO}/analysis/RUBRIC_RESULTS.md","w",encoding="utf-8").write("\n".join(L))
    print("\nDONE. Wrote analysis/rubric_judged.csv, analysis/RUBRIC_RESULTS.md, analysis/rubric_consent_log.jsonl")
    print("\n".join(L[-14:]))

if __name__=="__main__":
    main()
