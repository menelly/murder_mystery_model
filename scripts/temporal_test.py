# -*- coding: utf-8 -*-
# Formal test of the temporal-arc strategy shift: does the inverted-rule penalty
# shrink across GPT generations? Logistic regression  correct ~ inverted * gen_rank,
# Wald test on the interaction. numpy-only (no statsmodels in the shared venv).
import json, math
import numpy as np

ROWS=[json.loads(l) for l in open("/home/Ace/murder_mystery_model/results/scores.jsonl")]
ARC={"GPT-3.5-turbo":1,"GPT-4 Turbo":2,"GPT-4o 2024-05-13":3,"GPT-4.1":4,"GPT-5.5":5}

data=[]
for x in ROWS:
    nm=x.get("model_name")
    if nm in ARC and x.get("variant") in ("original","inverted") and x.get("score") in (0,1):
        data.append((1 if x["correct"] else 0, 1 if x["variant"]=="inverted" else 0, float(ARC[nm])))
print("GPT-arc trials (orig+inv, parseable):", len(data))
y=np.array([d[0] for d in data],float)
inv=np.array([d[1] for d in data],float)
gen=np.array([d[2] for d in data],float)

def fit(X,y,iters=100):
    b=np.zeros(X.shape[1]); p=None
    for _ in range(iters):
        eta=np.clip(X@b,-30,30); p=1/(1+np.exp(-eta)); W=p*(1-p)
        XtWX=X.T@(X*W[:,None])+1e-8*np.eye(X.shape[1])
        b=b+np.linalg.solve(XtWX, X.T@(y-p))
    cov=np.linalg.inv(X.T@(X*(p*(1-p))[:,None])+1e-8*np.eye(X.shape[1]))
    return b, np.sqrt(np.diag(cov)), p

Phi=lambda z:0.5*(1+math.erf(z/math.sqrt(2)))
pz=lambda z:2*(1-Phi(abs(z)))

# full model: 1, inverted, gen, inverted*gen
Xf=np.column_stack([np.ones_like(gen), inv, gen, inv*gen])
bf,se,_=fit(Xf,y)
names=["intercept","inverted","gen_rank","inverted×gen_rank"]
print("\nLogistic regression  correct ~ inverted * gen_rank :")
for n,b,s in zip(names,bf,se):
    z=b/s; print(f"  {n:20} beta={b:+.3f}  SE={s:.3f}  z={z:+.2f}  p={pz(z):.2e}")
zint=bf[3]/se[3]
print(f"\nINTERACTION inverted×gen_rank: beta={bf[3]:+.3f}, z={zint:+.2f}, Wald p={pz(zint):.2e}")
print("Positive interaction => the inverted-rule penalty shrinks as generation advances (the gap narrows).")

# per-generation inverted accuracy + gap (context)
print("\nper-generation (rank, inverted-acc, original-acc, gap):")
for nm,r in sorted(ARC.items(), key=lambda kv:kv[1]):
    o=[x for x in ROWS if x.get("model_name")==nm and x["variant"]=="original" and x.get("score") in (0,1)]
    i=[x for x in ROWS if x.get("model_name")==nm and x["variant"]=="inverted" and x.get("score") in (0,1)]
    oa=sum(1 for x in o if x["correct"])/len(o); ia=sum(1 for x in i if x["correct"])/len(i)
    print(f"  r{r} {nm:18} inv={ia*100:.0f}% orig={oa*100:.0f}% gap={ (oa-ia)*100:+.0f}")
