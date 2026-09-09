#!/usr/bin/env python3
import argparse,json,subprocess
from pathlib import Path

CASES=[
 ('multiply','What is 17 times 23? Answer with the number only.','391'),
 ('fib','Complete: `def fib(n): return n if n < 2 else`','fib(n-1) + fib(n-2)'),
 ('capital','The capital of Australia is','Canberra'),
 ('json','Write the JSON `{"a": 1}` with key b set to 2 added. Output JSON only.','"b": 2'),
 ('leap','How many days are in a leap year? Number only.','366')]
def ask(url,model,prompt):
 body=json.dumps({'model':model,'prompt':prompt,'max_tokens':128,'temperature':0,'top_p':1,'stream':False}).encode()
 p=subprocess.run(['curl','--http2','--silent','--show-error','--fail-with-body','-H','content-type: application/json','-H','Expect:','--data-binary','@-',url.rstrip('/')+'/v1/completions'],input=body,capture_output=True,timeout=600)
 if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace')[:500])
 d=json.loads(p.stdout); return (d.get('choices') or [{}])[0].get('text','')
def normalize_code(s):
 return ''.join(s.split())
ap=argparse.ArgumentParser(); ap.add_argument('--base-url',required=True); ap.add_argument('--model',default='qwen38'); ap.add_argument('--output',required=True); a=ap.parse_args(); rows=[]
for key,prompt,needle in CASES:
 for trial in range(2):
  out=ask(a.base_url,a.model,prompt); rows.append({'id':key,'trial':trial,'output':out,'needle':needle,'pass':normalize_code(needle) in normalize_code(out)})
result={'rows':rows,'passed':sum(x['pass'] for x in rows),'case_passes':sum(all(x['pass'] for x in rows if x['id']==k) for k,_,_ in CASES),'five_of_five':all(any(x['pass'] for x in rows if x['id']==k) for k,_,_ in CASES)}
Path(a.output).write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps({k:result[k] for k in ('passed','case_passes','five_of_five')}))
