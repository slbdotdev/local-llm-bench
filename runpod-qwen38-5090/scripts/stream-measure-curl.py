#!/usr/bin/env python3
import argparse,json,statistics,subprocess,time,uuid
from pathlib import Path

def call(base,model,prompt,max_tokens):
    body=json.dumps({'model':model,'prompt':prompt,'max_tokens':max_tokens,'temperature':0,'top_p':1,'stream':True,'stream_options':{'include_usage':True}}).encode()
    cmd=['curl','--http2','--no-buffer','--silent','--show-error','--fail-with-body','-H','content-type: application/json','-H','Expect:','--data-binary','@-',base.rstrip('/')+'/v1/completions']
    t0=time.perf_counter(); ttft=None; toks=None; chunks=0; text=''
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.stdin.write(body); p.stdin.close()
    for line in p.stdout:
        if not line.startswith(b'data:'): continue
        raw=line[5:].strip()
        if raw==b'[DONE]': break
        d=json.loads(raw); ch=(d.get('choices') or [{}])[0]; piece=ch.get('text','')
        if ch.get('text') is not None: chunks+=1
        if piece and ttft is None: ttft=time.perf_counter()-t0
        text+=piece
        if d.get('usage') and 'completion_tokens' in d['usage']: toks=d['usage']['completion_tokens']
    err=p.stderr.read(); p.wait(timeout=600)
    if p.returncode: raise RuntimeError(f'curl exit {p.returncode}: {err.decode(errors="replace")[:500]}')
    elapsed=time.perf_counter()-t0
    ttft=ttft or elapsed
    return {'elapsed_s':elapsed,'ttft_s':ttft,'chunks':chunks,'completion_tokens':toks,'decode_tps':(toks-1)/(elapsed-ttft) if toks is not None and elapsed>ttft and toks>1 else 0,'text':text}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--base-url',required=True); ap.add_argument('--model',default='qwen38'); ap.add_argument('--prompts',required=True); ap.add_argument('--context',type=int,default=8192); ap.add_argument('--output',required=True); ap.add_argument('--repeats',type=int,default=3); ap.add_argument('--max-tokens',type=int,default=256); a=ap.parse_args(); rows=[]
    for line in Path(a.prompts).read_text().splitlines():
        x=json.loads(line); pad=(' Context padding: audit review code tool diff.'*max(0,a.context//8)) if a.context>=8192 else ''
        for trial in range(a.repeats):
            salt=uuid.uuid4().hex; submitted=f'Trial salt: {salt}\n'+pad+x['prompt']
            rows.append({'prompt_id':x['id'],'trial':trial,'salt':salt,'submitted_prompt':submitted,**call(a.base_url,a.model,submitted,a.max_tokens)})
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text('\n'.join(json.dumps(x) for x in rows)+'\n'); print(json.dumps({'median_decode_tps':statistics.median([x['decode_tps'] for x in rows]),'rows':len(rows)}))

if __name__ == '__main__': main()
