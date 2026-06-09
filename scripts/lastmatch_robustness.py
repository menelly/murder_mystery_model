#!/usr/bin/env python3
"""Robustness check for the murder-mystery paper (Fable-Ace review #5):
re-score every trial with LAST-match instead of the pre-registered FIRST-match,
and compare per-variant accuracy + the original-inverted gap + RFS. If the
headline (large template gaps in older models, narrowing across generations)
survives last-match, the first-match scoring artifact is not driving it.
 — Ace, 2026-06-09
"""
import json, re
from pathlib import Path
from collections import defaultdict

RESULTS = Path("/home/Ace/murder_mystery_model/results")
PAT = re.compile(r"Suspect\s+([ABC])", re.IGNORECASE)

def first_ans(t):
    m = PAT.search(t or "")
    return m.group(1).upper() if m else None
def last_ans(t):
    ms = PAT.findall(t or "")
    return ms[-1].upper() if ms else None

# agg[(slug,name)][variant][method] = [correct, scored]
agg = defaultdict(lambda: defaultdict(lambda: {"first":[0,0], "last":[0,0]}))
# pairs[(slug,name)][(puzzle,seed)][variant] = {"first":a,"last":a}
pairs = defaultdict(lambda: defaultdict(dict))

for d in sorted(RESULTS.iterdir()):
    if not d.is_dir(): continue
    for p in d.glob("*.json"):
        try: rec = json.loads(p.read_text())
        except Exception: continue
        if rec.get("error"): continue
        variant = rec.get("variant"); cp = rec.get("correct_position")
        txt = rec.get("verbatim_response","")
        key = (rec.get("model_slug"), rec.get("model_name"))
        fa, la = first_ans(txt), last_ans(txt)
        for method, a in (("first",fa),("last",la)):
            if a is None: continue
            agg[key][variant][method][1]+=1
            if a==cp: agg[key][variant][method][0]+=1
        pairs[key][(rec.get("puzzle_id"), rec.get("seed"))][variant] = {"first":fa,"last":la}

def acc(cell):
    c,n = cell
    return (100.0*c/n) if n else None

def rfs(model_key, method):
    same=tot=0
    for k,v in pairs[model_key].items():
        if "original" in v and "inverted" in v:
            o=v["original"][method]; i=v["inverted"][method]
            if o is None or i is None: continue
            tot+=1
            if o==i: same+=1
    return (100.0*(1-same/tot)) if tot else None, tot

rows=[]
for key in agg:
    slug,name=key
    of=acc(agg[key]["original"]["first"]); ol=acc(agg[key]["original"]["last"])
    inf=acc(agg[key]["inverted"]["first"]); il=acc(agg[key]["inverted"]["last"])
    gap_f = (of-inf) if (of is not None and inf is not None) else None
    gap_l = (ol-il) if (ol is not None and il is not None) else None
    dgap = (gap_l-gap_f) if (gap_f is not None and gap_l is not None) else None
    rf,_=rfs(key,"first"); rl,_=rfs(key,"last")
    rows.append((name, of,ol,inf,il,gap_f,gap_l,dgap,rf,rl))

def s(x,suf=""):
    return f"{x:5.0f}{suf}" if x is not None else "   - "

rows.sort(key=lambda r: (r[5] if r[5] is not None else -999), reverse=True)
print(f"{'Model':28s} {'oF':>5}{'oL':>5} {'iF':>5}{'iL':>5} {'gapF':>6}{'gapL':>6}{'Δgap':>6} {'rfsF':>6}{'rfsL':>6}")
print("-"*92)
for r in rows:
    name=r[0][:28]
    print(f"{name:28s} {s(r[1])}{s(r[2])} {s(r[3])}{s(r[4])} {s(r[5])}{s(r[6])}{s(r[7])} {s(r[8])}{s(r[9])}")

# ---- summary ----
gaps=[(r[0],r[5],r[6],r[7]) for r in rows if r[5] is not None and r[6] is not None]
import statistics as st
mean_f=st.mean(g[1] for g in gaps); mean_l=st.mean(g[2] for g in gaps)
shrink=[g for g in gaps if g[3] is not None and g[3] < -5]   # gap shrank >5pp under last-match
grow=[g for g in gaps if g[3] is not None and g[3] > 5]
print("\n==== SUMMARY ====")
print(f"models compared: {len(gaps)}")
print(f"mean original-inverted gap:  first-match {mean_f:+.1f}pp   last-match {mean_l:+.1f}pp   (Δ {mean_l-mean_f:+.1f}pp)")
print(f"gap SHRANK >5pp under last-match: {len(shrink)} models")
print(f"gap GREW   >5pp under last-match: {len(grow)} models")
print("\nHeadline 'template-gap' models — do the big gaps survive last-match?")
for tag in ["GPT-4 Turbo","Llama 3.3 70B","Gemma 3 27B","Qwen 2.5 72B","Llama 3.1 70B","GPT-5.5","Gemma 4 31B"]:
    for r in rows:
        if r[0].startswith(tag):
            print(f"  {r[0]:26s} gap {s(r[5]).strip():>5} -> {s(r[6]).strip():>5}  (orig {s(r[1]).strip()}->{s(r[2]).strip()}, inv {s(r[3]).strip()}->{s(r[4]).strip()})")
            break
print("\nLargest gap-shrinks (where first-match most over-stated the gap):")
for g in sorted([g for g in gaps if g[3] is not None], key=lambda x:x[3])[:8]:
    print(f"  {g[0]:26s} Δgap {g[3]:+.0f}pp  ({g[1]:+.0f} -> {g[2]:+.0f})")
