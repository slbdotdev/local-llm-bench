#!/usr/bin/env python3
import argparse, json, statistics, time
from pathlib import Path
from urllib.request import Request, urlopen

def call(url, model, prompt, max_tokens):
    body={"model":model,"prompt":prompt,"max_tokens":max_tokens,"temperature":0,"top_p":1,"stream":False}
    req=Request(url.rstrip("/")+"/v1/completions",data=json.dumps(body).encode(),headers={"content-type":"application/json"})
    started=time.perf_counter()
    with urlopen(req,timeout=600) as response: data=json.load(response)
    elapsed=time.perf_counter()-started
    usage=data.get("usage",{})
    text=data.get("choices",[{}])[0].get("text","")
    tokens=int(usage.get("completion_tokens") or len(text.split()))
    return {"elapsed_s":elapsed,"output_tokens":tokens,"tokens_per_s":tokens/elapsed if elapsed else 0,"usage":usage}

ap=argparse.ArgumentParser()
ap.add_argument("--base-url",default="http://127.0.0.1:8000"); ap.add_argument("--model",required=True)
ap.add_argument("--prompts",required=True); ap.add_argument("--context",type=int,required=True)
ap.add_argument("--max-tokens",type=int,default=256); ap.add_argument("--repeats",type=int,default=3)
ap.add_argument("--output",required=True); args=ap.parse_args()
rows=[]
for line in Path(args.prompts).read_text().splitlines():
    item=json.loads(line)
    padding=(" Context padding: audit review code tool diff."*max(0,args.context//8)) if args.context>8192 else ""
    for trial in range(args.repeats):
        rows.append({"prompt_id":item["id"],"context_target":args.context,"trial":trial,
                     **call(args.base_url,args.model,item["prompt"]+padding,args.max_tokens)})
Path(args.output).parent.mkdir(parents=True,exist_ok=True)
Path(args.output).write_text("\n".join(json.dumps(row) for row in rows)+"\n")
values=[row["tokens_per_s"] for row in rows if row["output_tokens"]]
print(json.dumps({"context":args.context,"rows":len(rows),"median_tps":statistics.median(values) if values else 0,
                  "dispersion":statistics.pstdev(values) if len(values)>1 else 0}))
