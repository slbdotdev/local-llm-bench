#!/usr/bin/env python3
import argparse, json
from pathlib import Path
from urllib.request import Request, urlopen

def ask(base, model, prompt):
    body={"model":model,"prompt":prompt,"max_tokens":128,"temperature":0,"top_p":1,"stream":False}
    req=Request(base.rstrip("/")+"/v1/completions",data=json.dumps(body).encode(),headers={"content-type":"application/json"})
    with urlopen(req,timeout=600) as response: data=json.load(response)
    return data.get("choices",[{}])[0].get("text",""), data.get("usage",{})

ap=argparse.ArgumentParser()
ap.add_argument("--target-url",required=True); ap.add_argument("--spec-url",required=True)
ap.add_argument("--target-model",required=True); ap.add_argument("--spec-model",required=True)
ap.add_argument("--prompts",required=True); ap.add_argument("--output",required=True); args=ap.parse_args()
rows=[]
for line in Path(args.prompts).read_text().splitlines():
    item=json.loads(line); target,tu=ask(args.target_url,args.target_model,item["prompt"])
    spec,su=ask(args.spec_url,args.spec_model,item["prompt"])
    rows.append({"prompt_id":item["id"],"exact_match":target==spec,
                 "target_tokens":tu.get("completion_tokens"),"spec_tokens":su.get("completion_tokens"),
                 "target":target,"spec":spec})
result={"rows":rows,"all_exact":all(row["exact_match"] for row in rows)}
Path(args.output).write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({"all_exact":result["all_exact"],"rows":len(rows)}))
