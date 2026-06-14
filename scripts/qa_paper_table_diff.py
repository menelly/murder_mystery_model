# -*- coding: utf-8 -*-
"""Final gate: flag any % in PAPER.md plain tables that doesn't match the model's
true stats from scores.jsonl. Skips Table 1 (CI brackets -> already verified)."""
import json, re, collections

ROWS = [json.loads(l) for l in open("/home/Ace/murder_mystery_model/results/scores.jsonl", encoding="utf-8")]
by = collections.defaultdict(lambda: collections.defaultdict(list))
names = {}
for r in ROWS:
    m = r.get("model_slug")
    if not m: continue
    names[m] = r.get("model_name", m)
    by[m][r.get("variant")].append(r)

def acc(rows):
    p = [x for x in rows if x.get("score") in (0,1)]
    c = [x for x in p if x.get("correct")]
    return round(100*len(c)/len(p)) if p else None

def rfs(m):
    o = {(x["puzzle_id"],x["seed"]):x for x in by[m].get("original",[]) if x.get("score") in (0,1)}
    i = {(x["puzzle_id"],x["seed"]):x for x in by[m].get("inverted",[]) if x.get("score") in (0,1)}
    k = set(o)&set(i)
    if not k: return None
    same = sum(1 for q in k if o[q].get("extracted_answer")==i[q].get("extracted_answer"))
    return round(100*(1-same/len(k)),1)

def norm(s):
    return re.sub(r"[^a-z0-9]","", s.lower())

stats = {}
for m in by:
    o,i,d = acc(by[m].get("original",[])), acc(by[m].get("inverted",[])), acc(by[m].get("distractor",[]))
    rf = rfs(m)
    if None in (o,i,d): continue
    allowed = {o,i,d,abs(o-i),round(rf) if rf is not None else -999}
    if rf is not None: allowed.add(rf)
    stats[m] = {"name":names[m],"allowed":allowed,"o":o,"i":i,"d":d,"gap":o-i,"rfs":rf}

# strip parenthetical + year for matching
def clean_label(cell):
    cell = re.sub(r"\(.*?\)","",cell)
    cell = re.sub(r"\b20\d\d(-\d\d)?\b","",cell)
    return norm(cell)

flags = 0
for ln, line in enumerate(open("/home/Ace/murder_mystery_model/PAPER.md", encoding="utf-8"), 1):
    if not line.startswith("|") or "%" not in line or "[" in line:  # skip CI tables + non-rows
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if not cells: continue
    label = clean_label(cells[0])
    if not label or label in ("model","generation"): continue
    # best model match: longest recompute-norm that is substring of label
    best, blen = None, 0
    for m,s in stats.items():
        nm = norm(re.sub(r"\b20\d\d(-\d\d)?\b","",s["name"]))
        if nm and nm in label and len(nm) > blen:
            best, blen = m, len(nm)
    if not best: continue
    s = stats[best]
    pcts = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)%", line)]
    for v in pcts:
        if not any(abs(v-a) <= 1.0 for a in s["allowed"]):
            print(f"L{ln} [{s['name']}] FOREIGN value {v}%  (true: orig{s['o']} inv{s['i']} dist{s['d']} gap{s['gap']} rfs{s['rfs']})")
            print(f"     row: {line.strip()[:120]}")
            flags += 1

print("="*60)
print("CLEAN -- no foreign values in plain tables." if flags==0 else f"{flags} FOREIGN value(s) flagged above.")
