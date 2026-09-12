"""Verify the GPU by a REAL LOAD on a given tag, against an explicit base URL.

results/v5/gpu_verify.py hardcodes http://127.0.0.1:11434, which the Windows interpreter cannot
reach: Ollama binds to the Tailscale address only (org/local-ollama-route-2026-09-11.md). This
takes the base URL as an argument so the endpoint is never assumed.

  python gpu_verify8.py <base_url> <tag>

Prints the generation rate and the resident size, then unloads. A version string is not a
verification (org/ollama-cuda-repair-2026-09-04.md).
"""
import json, sys, time, urllib.request

def post(base, path, payload, timeout=600):
    req = urllib.request.Request(base + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))

def main():
    if len(sys.argv) < 3:
        print("usage: gpu_verify8.py <base_url> <tag>"); return 2
    base, tag = sys.argv[1].rstrip("/"), sys.argv[2]
    print(f"base={base} tag={tag}")

    t0 = time.time()
    r = post(base, "/api/chat", {"model": tag, "stream": False, "options": {"num_ctx": 4096},
                                 "messages": [{"role": "user", "content":
                                 "Write a 150-word explanation of how a B-tree index speeds up range queries."}]})
    wall = time.time() - t0
    ec, ed = r.get("eval_count", 0), r.get("eval_duration", 1)
    pc, pd = r.get("prompt_eval_count", 0), r.get("prompt_eval_duration", 1)
    gen = ec / (ed / 1e9) if ed else 0.0
    pre = pc / (pd / 1e9) if pd else 0.0
    print(f"wall={wall:.1f}s eval_count={ec} gen_tok_s={gen:.2f} prompt_eval_count={pc} prefill_tok_s={pre:.1f}")

    ps = json.load(urllib.request.urlopen(base + "/api/ps", timeout=30))
    ok_resident = False
    for m in ps.get("models", []):
        size, vram = m.get("size", 0), m.get("size_vram", 0)
        pct = (100.0 * vram / size) if size else 0.0
        print(f"resident={size/2**30:.2f}GiB vram={vram/2**30:.2f}GiB gpu_pct={pct:.1f} name={m.get('name')}")
        if pct >= 99.0:
            ok_resident = True
        else:
            print("  WARNING: not fully on the GPU — a broken upgrade serves every model on the CPU silently")

    post(base, "/api/generate", {"model": tag, "keep_alive": 0}, timeout=60)
    ps2 = json.load(urllib.request.urlopen(base + "/api/ps", timeout=30))
    print("unloaded; /api/ps models:", len(ps2.get("models", [])))

    if not ok_resident:
        print("VERIFY FAILED: no fully-resident model observed"); return 1
    if gen < 20:
        print(f"VERIFY FAILED: {gen:.1f} tok/s is below the spill threshold"); return 1
    print("VERIFY OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
