"""Measure this model's actual chars/token on the real filler, and prefill vs generation.

The 5.95 chars/token constant was an estimate. Sizing prompt-side fill on a wrong constant
either undershoots the cell target or overflows num_ctx and gets silently truncated, so it
is measured against the model that will be used.

Reports prompt_eval_count/duration and eval_count/duration from /api/generate, which is the
only place the prefill/generation split is exposed.
"""
import json, sys, time, urllib.request
sys.path.insert(0, r"D:\local-llm-bench\ollama-bench")
import pibench

MODEL = sys.argv[1]
TARGET = int(sys.argv[2])
INSTRUCTION = open(sys.argv[3], encoding="utf-8").read() if len(sys.argv) > 3 else "Summarise the material below in one sentence.\n"
CPT = float(sys.argv[4]) if len(sys.argv) > 4 else pibench.PAD_CHARS_PER_TOKEN

prompt, info = pibench.build_filled_prompt(INSTRUCTION, TARGET, chars_per_token=CPT)
req = {"model": MODEL, "prompt": prompt, "stream": False, "options": {"num_predict": 24}}
body = json.dumps(req).encode()
t0 = time.time()
with urllib.request.urlopen(urllib.request.Request(
        "http://127.0.0.1:11434/api/generate", data=body,
        headers={"Content-Type": "application/json"}), timeout=1800) as r:
    d = json.loads(r.read().decode())
wall = time.time() - t0
pe, ec = d.get("prompt_eval_count", 0), d.get("eval_count", 0)
ped, ed = d.get("prompt_eval_duration", 0) / 1e9, d.get("eval_duration", 0) / 1e9
print(json.dumps({
    "model": MODEL, "target_tokens": TARGET, "assumed_chars_per_token": CPT,
    "prompt_chars": len(prompt), "prompt_eval_count": pe,
    "measured_chars_per_token": round(len(prompt) / pe, 3) if pe else None,
    "pct_of_target": round(100 * pe / TARGET, 1) if TARGET else None,
    "prefill_s": round(ped, 2), "prefill_tps": round(pe / ped, 1) if ped else None,
    "gen_tokens": ec, "gen_s": round(ed, 2), "gen_tps": round(ec / ed, 1) if ed else None,
    "wall_s": round(wall, 2),
}, indent=1))
