#!/usr/bin/env python3
"""Per-task verdict grid for round three: the five reference arms and the workhorse GPU rows.
Prints markdown; paste into authoring-r3-2026-09-08.md section 3. Run from ollama-bench/."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
SAN = os.path.join(HERE, "authoring", "sanity")
rows = {}
for arm in ["haiku", "sonnet", "luna", "glm", "fp8"]:
    p = os.path.join(SAN, arm, "trial-r3", "results.json")
    rows[arm] = json.load(open(p)) if os.path.exists(p) else {}
gpu = {}
for tag, model in [("v7r3-gate-main", "q27-IQ2_M-64k"), ("v7r3-gate-cheap", "q27-IQ2_M-24k"),
                   ("v7r3-gate-n06", "q27-IQ2_M-64k")]:
    p = os.path.join(HERE, "..", "%s.json" % tag)
    if os.path.exists(p):
        for v in json.load(open(p))[model]["runs"]:
            gpu[v["task"]] = v["verdict"]
tasks = ["n01-main-claude", "n02-main-glm", "n03-main-luna", "n04-main-claude", "n05-main-luna",
         "n06-main-glm", "n07-main-claude", "n08-cheap-glm", "n09-cheap-luna", "n10-cheap-claude"]
ab = {"correct": "pass", "confidently_wrong": "**cw**", "visibly_failed": "**vf**",
      "unsafe": "**unsafe**", "unverified_claim": "**uc**"}
print("| slot | Sonnet 5 | Haiku 4.5 | Luna | GLM 5.3 Flash | fp8 27B | IQ2_M workhorse |")
print("| --- | --- | --- | --- | --- | --- | --- |")
for t in tasks:
    cells = [ab.get(rows[a].get(t, {}).get("verdict"), "pending") for a in ["sonnet", "haiku", "luna", "glm", "fp8"]]
    cells.append(ab.get(gpu.get(t), "pending"))
    print("| %s | %s |" % (t, " | ".join(cells)))
