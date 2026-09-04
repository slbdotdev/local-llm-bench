import json, os, re, sys, time, subprocess, tempfile, shutil, urllib.request

OLLAMA = "http://localhost:11434"
MODELS = [
    "hf.co/empero-ai/Qwen3.8-27B-Ridge-GGUF:latest",
    "hf.co/OBLITERATUS/Qwen3.8-27B-OBLITERATED:Q4_K_M",
]
THINK = "--think" in sys.argv

def post(path, body, timeout=900):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def unload(model):
    try: post("/api/generate", {"model": model, "keep_alive": 0})
    except Exception: pass

# ---------- TPS ----------
def tps(model):
    post("/api/generate", {"model": model, "prompt": "hi", "stream": False, "think": False, "options": {"num_predict": 8}})  # warm load
    res = []
    for prompt in ["Write a 300 word essay about the history of compilers.",
                   "Explain in detail how TCP congestion control works, with examples."]:
        r = post("/api/generate", {"model": model, "prompt": prompt, "stream": False, "think": False,
                                   "options": {"num_predict": 400, "temperature": 0.2}})
        res.append({"prompt_tps": r["prompt_eval_count"] / (r["prompt_eval_duration"] / 1e9),
                    "gen_tps": r["eval_count"] / (r["eval_duration"] / 1e9),
                    "gen_tokens": r["eval_count"], "load_s": r.get("load_duration", 0) / 1e9})
    return res

# ---------- Agentic ----------
SYSTEM = """You are a coding agent working in a sandbox directory. Complete the user's task by issuing actions.
Reply with exactly ONE action per message, in a fenced block:

```action
{"tool": "write_file", "path": "relative/path.py", "content": "..."}
```
or
```action
{"tool": "run", "cmd": "python test.py"}
```
or when the task is fully done and verified:
```action
{"tool": "done"}
```
Never modify test.py. Always run `python test.py` before declaring done. Keep prose brief."""

TASKS = [
    {"name": "fizzbuzz_new",
     "task": "Create fizzbuzz.py containing a function fizzbuzz(n) that returns a list of strings for 1..n (Fizz/Buzz/FizzBuzz/number). Run `python test.py` to verify.",
     "files": {"test.py": "from fizzbuzz import fizzbuzz\nr=fizzbuzz(15)\nassert r[:3]==['1','2','Fizz'], r\nassert r[4]=='Buzz' and r[14]=='FizzBuzz', r\nassert len(r)==15\nprint('PASS')\n"}},
    {"name": "median_bugfix",
     "task": "stats.py has a bug in median() for even-length lists. Fix it without changing the function signature. Run `python test.py` to verify.",
     "files": {"stats.py": "def median(xs):\n    s = sorted(xs)\n    n = len(s)\n    return s[n // 2]\n",
               "test.py": "from stats import median\nassert median([3,1,2])==2\nassert median([4,1,3,2])==2.5, median([4,1,3,2])\nassert median([1,2])==1.5\nprint('PASS')\n"}},
    {"name": "wc_cli",
     "task": "Create wc.py: a CLI that takes a file path argument and prints '<lines> <words>' (space separated). Run `python test.py` to verify.",
     "files": {"test.py": "import subprocess,sys\nopen('in.txt','w').write(chr(10).join(['a b c','d e','','f','']))\nout=subprocess.run([sys.executable,'wc.py','in.txt'],capture_output=True,text=True).stdout.split()\nassert out==['4','6'], out\nprint('PASS')\n"}},
]

def parse_action(text):
    m = re.search(r"```action\s*(\{.*?\})\s*```", text, re.S)
    if not m: return None
    try: return json.loads(m.group(1))
    except Exception: return None

def run_task(model, t, max_turns=8):
    d = tempfile.mkdtemp(prefix="bench_")
    for k, v in t["files"].items():
        with open(os.path.join(d, k), "w", encoding="utf-8") as f: f.write(v)
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": t["task"]}]
    t0 = time.time(); toks = 0; turns = 0; passed = False; log = []
    for turns in range(1, max_turns + 1):
        r = post("/api/chat", {"model": model, "messages": msgs, "stream": False, "think": THINK,
                               "options": {"temperature": 0.1, "num_predict": 1500}})
        toks += r.get("eval_count", 0)
        content = r["message"]["content"]; msgs.append({"role": "assistant", "content": content})
        a = parse_action(content)
        if not a:
            obs = "ERROR: no valid ```action block found. Reply with exactly one action block."; log.append("noaction")
        elif a.get("tool") == "done":
            log.append("done"); break
        elif a.get("tool") == "write_file" and os.path.basename(a.get("path", "")) == "test.py":
            obs = "ERROR: test.py is read-only; do not modify it."; log.append("clobber")
        elif a.get("tool") == "write_file":
            p = os.path.join(d, a.get("path", "")); os.makedirs(os.path.dirname(p) or d, exist_ok=True)
            open(p, "w", encoding="utf-8").write(a.get("content", "")); obs = f"wrote {a['path']}"; log.append("write")
        elif a.get("tool") == "run":
            try:
                cp = subprocess.run(a["cmd"], shell=True, cwd=d, capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace")
                obs = f"exit={cp.returncode}\nstdout:\n{cp.stdout[-1500:]}\nstderr:\n{cp.stderr[-1500:]}"
            except subprocess.TimeoutExpired: obs = "timeout"
            log.append("run")
        else:
            obs = "ERROR: unknown tool"; log.append("bad")
        msgs.append({"role": "user", "content": obs})
    # final grade
    cp = subprocess.run([sys.executable, "test.py"], cwd=d, capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace")
    passed = "PASS" in cp.stdout
    shutil.rmtree(d, ignore_errors=True)
    return {"task": t["name"], "pass": passed, "final": (cp.stdout+cp.stderr)[-300:].strip(), "turns": turns, "gen_tokens": toks, "wall_s": round(time.time() - t0, 1), "log": log}

if __name__ == "__main__":
    out = {}
    for m in MODELS:
        print(f"\n=== {m} (think={THINK}) ===", flush=True)
        tp = tps(m); print("TPS:", json.dumps(tp), flush=True)
        tasks = []
        for t in TASKS:
            res = run_task(m, t); tasks.append(res); print(json.dumps(res), flush=True)
        out[m] = {"tps": tp, "tasks": tasks}
        unload(m)
    with open(f"results_think{THINK}.json", "w") as f: json.dump(out, f, indent=2)
    print("\nSUMMARY")
    for m, r in out.items():
        g = sum(x["gen_tps"] for x in r["tps"]) / len(r["tps"]); p = sum(x["prompt_tps"] for x in r["tps"]) / len(r["tps"])
        print(f"{m}\n  gen {g:.1f} tok/s | prompt {p:.0f} tok/s | tasks passed {sum(t['pass'] for t in r['tasks'])}/{len(r['tasks'])} | total agent wall {sum(t['wall_s'] for t in r['tasks']):.0f}s | turns {[t['turns'] for t in r['tasks']]}")
