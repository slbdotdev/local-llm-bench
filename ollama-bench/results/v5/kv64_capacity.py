"""Capacity test for the 64k KV question: does q8_0 fit at 64k, or does it spill?

Ollama allocates the whole num_ctx KV cache at load, so a one-token generate is enough
to settle fit. Records the /api/ps split and the nvidia-smi peak per model.
"""
import json, subprocess, sys, time, urllib.request

MODELS = ["q27-Q3_K_S-64k", "q27-IQ3_M-64k"]


def smi():
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=15)
    return int(r.stdout.strip().splitlines()[0])


def post(path, payload, timeout=1800):
    body = json.dumps(payload).encode()
    with urllib.request.urlopen(urllib.request.Request(
            "http://127.0.0.1:11434" + path, data=body,
            headers={"Content-Type": "application/json"}), timeout=timeout) as r:
        return json.loads(r.read().decode())


out = {"idle_mib": smi(), "cells": []}
for m in MODELS:
    post("/api/generate", {"model": m, "prompt": "hi", "stream": False,
                           "options": {"num_predict": 1}})
    peak = smi()
    ps = post("/api/ps", {}) if False else json.loads(
        urllib.request.urlopen("http://127.0.0.1:11434/api/ps", timeout=30).read().decode())
    row = {"model": m, "nvidia_smi_mib": peak, "resident": None}
    for e in ps.get("models", []):
        if e.get("name", "").startswith(m):
            tot, vram = e.get("size", 0), e.get("size_vram", 0)
            row["size_gb"] = round(tot / 2**30, 2)
            row["vram_gb"] = round(vram / 2**30, 2)
            row["pct_gpu"] = round(100 * vram / tot) if tot else None
            row["resident"] = row["pct_gpu"] == 100
            row["context_length"] = e.get("context_length")
    out["cells"].append(row)
    post("/api/generate", {"model": m, "keep_alive": 0, "prompt": "", "stream": False})
    time.sleep(5)
print(json.dumps(out, indent=1))
