import json, collections

ROWS = [json.loads(l) for l in open("/home/Ace/murder_mystery_model/results/scores.jsonl", encoding="utf-8")]
by = collections.defaultdict(lambda: collections.defaultdict(list))
names = {}
for r in ROWS:
    m = r.get("model_slug")
    if not m:
        continue
    names[m] = r.get("model_name", m)
    by[m][r.get("variant")].append(r)

def acc(rows):
    parse = [x for x in rows if x.get("score") in (0, 1)]
    cor = [x for x in parse if x.get("correct")]
    pct = round(100*len(cor)/len(parse)) if parse else None
    return pct, len(parse), len(rows)

def rfs(model):
    o = {(x["puzzle_id"], x["seed"]): x for x in by[model].get("original", []) if x.get("score") in (0,1)}
    i = {(x["puzzle_id"], x["seed"]): x for x in by[model].get("inverted", []) if x.get("score") in (0,1)}
    keys = set(o) & set(i)
    if not keys:
        return None, 0
    same = sum(1 for k in keys if o[k].get("extracted_answer") == i[k].get("extracted_answer"))
    return round(100*(1-same/len(keys)), 1), len(keys)

rowsout = []
for m in by:
    o,_,_ = acc(by[m].get("original", []))
    i,_,_ = acc(by[m].get("inverted", []))
    d,_,_ = acc(by[m].get("distractor", []))
    rf, npair = rfs(m)
    gap = (o-i) if (o is not None and i is not None) else None
    rowsout.append((names[m], o, i, d, gap, rf, npair))

print(f"{'MODEL':<32}{'orig':>6}{'inv':>6}{'dist':>6}{'gap':>6}{'RFS':>8}{'npair':>7}")
print("-"*73)
for name,o,i,d,gap,rf,npair in sorted(rowsout, key=lambda x: (-(x[5] if x[5] is not None else -1))):
    print(f"{name:<32}{str(o):>6}{str(i):>6}{str(d):>6}{str(gap):>6}{str(rf):>8}{npair:>7}")
