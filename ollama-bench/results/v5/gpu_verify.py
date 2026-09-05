import json, time, urllib.request, subprocess, sys

BASE = "http://127.0.0.1:11434"
tag = sys.argv[1] if len(sys.argv) > 1 else "q27-Q3_K_S-24k"

def post(path, payload, timeout=600):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))

t0 = time.time()
r = post("/api/chat", {"model": tag, "stream": False,
                       "messages": [{"role": "user",
                                     "content": "Write a 150-word explanation of how a B-tree index speeds up range queries."}]})
wall = time.time() - t0
ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1)
print(f"tag={tag} wall={wall:.1f}s eval_count={ec} gen_tok_s={ec/(ed/1e9):.2f}")

ps = json.load(urllib.request.urlopen(BASE + "/api/ps", timeout=30))
for m in ps.get("models", []):
    total, vram = m.get("size", 0), m.get("size_vram", 0)
    print(f"ps: {m['name']} size={total/1e9:.2f}GB vram={vram/1e9:.2f}GB pct_gpu={100*vram/total:.0f}% ctx={m.get('context_length')}")

smi = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader"],
                     capture_output=True, text=True)
print("nvidia-smi used:", smi.stdout.strip())
