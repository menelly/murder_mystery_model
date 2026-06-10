# Coverage vs accuracy: disentangle format-following from reasoning.
# coverage = parseable/total ; parseable_acc = correct/parseable ; strict_acc = correct/total
# (Ace, 2026-06-10 audit — report BOTH denominators per Ren.)
import json, collections
from pathlib import Path
rows=[json.loads(l) for l in open('results/scores.jsonl')]
DEAD={'Mamba 2.8B','Gemma 2 9B IT','Phi-3.5-mini Instruct','Gemma 2 9B Instruct'}
agg=collections.defaultdict(lambda:[0,0,0])
for r in rows:
    nm=r['model_name']
    if nm in DEAD: continue
    agg[nm][0]+=1
    if str(r['score'])!='-1': agg[nm][1]+=1
    if str(r['score'])=='1': agg[nm][2]+=1
lines=['# Coverage vs Accuracy — disentangling format-following from reasoning',
'','Three numbers per model, all reported (Ren, 2026-06-10): **coverage** = parseable/total (did it emit a usable answer at all — instruction-following + truncation); **parseable accuracy** = correct/parseable (reasoning, given a parseable answer); **strict accuracy** = correct/total (unparseable counted as failure — the conjunction).','',
'| Model | N | coverage | parseable acc | strict acc |','|---|---:|---:|---:|---:|']
for nm,(t,p,c) in sorted(agg.items(), key=lambda x:(x[1][1]/x[1][0] if x[1][0] else 0)):
    cov=100*p/t if t else 0; pa=100*c/p if p else 0; sa=100*c/t if t else 0
    lines.append(f'| {nm} | {t} | {cov:.0f}% | {pa:.0f}% | {sa:.0f}% |')
lines+=['','## How to read it','- **Floor models** (RWKV, SmolLM-135M/360M, Pythia, Liquid LFM 2.5): low coverage AND ~chance parseable accuracy = both a format-following floor and a reasoning floor.','- **SmolLM-1.7B / Phi-2**: high coverage (~92%) but ~30% parseable accuracy = a clean reasoning floor with format-following intact (the cleanest evidence the floor is partly genuine reasoning failure).','- **Frontier reasoners** (Qwen-3-14B, o4-mini, DeepSeek R1): coverage 82-96% but parseable accuracy 97-100% = their lower coverage is extended-thinking truncation, not error; strict accuracy understates them.','','So "Where does understanding begin?" has two emergence curves, not one: a format/instruction-following curve and a reasoning curve. Reporting both denominators separates them instead of conflating them in a single accuracy number.']
Path('analysis/coverage_vs_accuracy.md').write_text(chr(10).join(lines))
print('wrote analysis/coverage_vs_accuracy.md (', len(agg), 'models )')
