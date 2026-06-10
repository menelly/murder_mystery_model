# Forced-choice logprob probe (EXPLORATORY follow-up, 2026-06-10, Ace/Fable).
# NOT pre-registered. Separates format-following from reasoning at the floor:
# reuse each trial's EXACT saved prompt, prime 'The killer is Suspect ', read
# the model's logits over A/B/C. 100% coverage by construction -> pure reasoning.
import os, sys, json, glob, math
os.environ['CUDA_VISIBLE_DEVICES']='0'
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

CACHE='/mnt/Arcana/huggingface'
MODELS={
 'smollm_135m_instruct': f'{CACHE}/SmolLM-135M-Instruct',
 'smollm_360m_instruct': f'{CACHE}/SmolLM-360M-Instruct',
 'smollm_1_7b_instruct': f'{CACHE}/SmolLM-1.7B-Instruct',
 'pythia_1_4b':          f'{CACHE}/pythia-1.4b',
 'tinyllama_1_1b_chat':  f'{CACHE}/TinyLlama-1.1B-Chat',
 'phi_2':                f'{CACHE}/phi-2',
 'qwen2_5_0_5b_instruct':f'{CACHE}/Qwen2.5-0.5B-Instruct',
}
PRIME='\nThe killer is Suspect '

def first_tok(tok, s):
    ids=tok.encode(s, add_special_tokens=False)
    return ids[0] if ids else None

def run(slug, path):
    tok=AutoTokenizer.from_pretrained(path)
    model=AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.float16).to('cuda').eval()
    # candidate token ids for ' A',' B',' C' and 'A','B','C'
    cand={c: [t for t in {first_tok(tok,' '+c), first_tok(tok,c)} if t is not None] for c in 'ABC'}
    files=sorted(glob.glob(f'results/{slug}/*.json'))
    rows=[]; correct=0; n=0
    for fp in files:
        d=json.load(open(fp))
        base=d['prompt']
        try:
            msgs=[{'role':'user','content':base}]
            text=tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        except Exception:
            text=base
        text=text+PRIME
        ids=tok(text, return_tensors='pt').to('cuda')
        with torch.no_grad():
            logits=model(**ids).logits[0,-1]
        scores={c: max(float(logits[t]) for t in toks) for c,toks in cand.items() if toks}
        pick=max(scores, key=scores.get)
        cp=d['correct_position']
        ok=int(pick==cp); correct+=ok; n+=1
        rows.append({'model_slug':slug,'puzzle_id':d['puzzle_id'],'variant':d['variant'],'seed':d['seed'],'correct_position':cp,'forced_pick':pick,'score':ok})
    json.dump(rows, open(f'results_forced_choice/{slug}.json','w'))
    del model; torch.cuda.empty_cache()
    print(f'{slug:26s} forced-choice acc = {100*correct/n:.0f}%  (n={n})', flush=True)
    return correct,n

if __name__=='__main__':
    only=sys.argv[1] if len(sys.argv)>1 else None
    for slug,path in MODELS.items():
        if only and slug!=only: continue
        try: run(slug,path)
        except Exception as e: print(f'{slug}: ERROR {e!r}', flush=True)
