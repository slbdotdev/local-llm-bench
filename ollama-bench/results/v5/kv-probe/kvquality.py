"""T2: does KV cache quantization cost long-context recall, and does asymmetric K/V help?

Runs llama-server directly (Ollama's own vendored build) so K and V can be given
different types -- something Ollama itself cannot express, since it sets both from the
single OLLAMA_KV_CACHE_TYPE. Ollama must have nothing loaded before this runs.

For each (cache_type_k, cache_type_v) config: launch a server, fill the context with a
fixed haystack of records, ask N needle questions with greedy decoding, score exact
match on the needle value. Records VRAM peak and throughput beside the score.

Usage: python kvquality.py --model <blob> --ctx 16384 --configs f16:f16,q8_0:q8_0,q4_0:q4_0,q8_0:q4_0
"""
import argparse, json, os, random, re, subprocess, sys, time, urllib.request, urllib.error

LIBDIR = os.path.expanduser("~/AppData/Local/Programs/Ollama/lib/ollama")
SERVER = os.path.join(LIBDIR, "llama-server.exe")
# Ollama keeps the CUDA backend in a subdirectory and puts it on the library path
# itself when it launches the runner. Launched by hand the loader finds only the CPU
# backends beside the exe and prints "no usable GPU found", silently ignoring -ngl.
CUDA_DIR = os.path.join(LIBDIR, "cuda_v13")
PORT = 18080
BASE = f"http://127.0.0.1:{PORT}"


def server_env():
    e = dict(os.environ)
    e["PATH"] = CUDA_DIR + os.pathsep + LIBDIR + os.pathsep + e.get("PATH", "")
    # GGML_BACKEND_PATH names the backend *library*, not its directory: pointed at a
    # directory the loader reports "failed to load <dir>" and falls through to CPU.
    e["GGML_BACKEND_PATH"] = os.path.join(CUDA_DIR, "ggml-cuda.dll")
    return e

REGIONS = ["eu-west-3", "us-east-1", "ap-south-2", "sa-east-1", "af-north-1", "me-central-1"]
WORDS_A = ["harrow", "colden", "brightmoor", "tarnwick", "elderfell", "graystone", "windhollow",
           "ashcombe", "ravensmere", "thornbury", "silverdale", "marlowe", "kestrelby", "downholt",
           "fenwick", "oakmere", "starling", "vaulterra", "quillon", "bramblewood"]
WORDS_B = ["fen", "vale", "reach", "hollow", "cross", "gate", "moor", "ridge", "combe", "hurst"]


def make_corpus(n_records, n_needles, seed=20260903):
    """Fixed-seed haystack of look-alike records; n_needles of them are the questions."""
    rng = random.Random(seed)
    # WORDS_A x WORDS_B is only 200 pairs, so a third component is required for any
    # corpus larger than that -- without it the uniqueness loop simply never returns.
    names = [f"{a}-{b}-{n}" for n in range(1, 1 + -(-n_records // 200))
             for a in WORDS_A for b in WORDS_B][:n_records]
    rng.shuffle(names)

    records, facts = [], []
    # needle positions spread across the depth of the corpus, avoiding the very edges
    needle_at = {int(n_records * (0.02 + 0.93 * i / max(1, n_needles - 1)))
                 for i in range(n_needles)}

    for i, nm in enumerate(names):
        checksum = "".join(rng.choice("0123456789ABCDEF") for _ in range(6))
        rec = (f"RECORD {i:04d}: node \"{nm}\" region={rng.choice(REGIONS)} "
               f"shard={rng.randrange(1, 512)} checksum={checksum} "
               f"token_budget={rng.randrange(1000, 99999)} status=converged")
        records.append(rec)
        if i in needle_at:
            facts.append({"index": i, "depth": round(i / n_records, 3),
                          "node": nm, "checksum": checksum})
    return "\n".join(records), facts


def post(path, body, timeout=600):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def wait_health(proc, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if proc.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(BASE + "/health", timeout=5) as r:
                if json.load(r).get("status") == "ok":
                    return True
        except Exception:
            pass
        time.sleep(2)
    return False


def vram_mib():
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=30)
        return int(o.stdout.strip().splitlines()[0])
    except Exception:
        return -1


def kill_stray_servers():
    """Never start a second llama-server. Two of them at once on this box drove free
    host RAM to 43 MiB on 2026-09-03 (results/gpu-watch.ALERT): the oversized second
    allocation does not OOM on WDDM, it spills to system RAM and takes the machine
    with it. Refuse to launch until the GPU is actually idle."""
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-Process llama-server -ErrorAction SilentlyContinue |"
                    " Stop-Process -Force"], capture_output=True, timeout=60)
    for _ in range(15):
        time.sleep(2)
        if vram_mib() < 4000:
            return True
    return False


def run_config(model, ctk, ctv, ctx, corpus, facts, logdir):
    tag = f"{ctk}-{ctv}"
    if not kill_stray_servers():
        return {"config": tag, "error": f"GPU not idle before launch ({vram_mib()} MiB)"}
    logf = open(os.path.join(logdir, f"server-{tag}.log"), "wb")
    cmd = [SERVER, "--model", model, "--port", str(PORT), "--host", "127.0.0.1",
           "--no-webui", "--offline", "-c", str(ctx), "-np", "1",
           "-ngl", "99", "--flash-attn", "on",
           "--cache-type-k", ctk, "--cache-type-v", ctv,
           "-b", "512", "-ub", "512", "--no-warmup"]
    print(f"\n### {tag}  (ctx {ctx})", flush=True)
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, env=server_env())
    if not wait_health(proc):
        proc.kill(); logf.close()
        return {"config": tag, "error": "server did not become healthy"}
    load_s = round(time.time() - t0, 1)
    vram_loaded = vram_mib()

    results, peak = [], vram_loaded
    sys_msg = ("You answer questions about a configuration dump. Answer with the exact value "
               "only -- no explanation, no punctuation, no restating the question.")
    gen_toks = gen_time = prompt_toks = prompt_time = 0

    for f in facts:
        q = (f"{corpus}\n\nQuestion: what is the checksum of node \"{f['node']}\"?\n"
             "Answer with the six-character checksum only.")
        try:
            r = post("/v1/chat/completions", {
                "messages": [{"role": "system", "content": sys_msg},
                             {"role": "user", "content": q}],
                "temperature": 0, "top_k": 1, "seed": 20260903,
                "max_tokens": 32, "cache_prompt": True,
                # this is a recall probe, not a reasoning one; without this the
                # Qwen template spends the whole budget inside <think>
                "chat_template_kwargs": {"enable_thinking": False},
            })
        except Exception as e:
            results.append({**f, "answer": f"ERROR {e}", "ok": False})
            continue
        txt = r["choices"][0]["message"]["content"].strip()
        # strip any thinking block the template may emit
        txt = re.sub(r"<think>.*?</think>", "", txt, flags=re.S).strip()
        ok = f["checksum"].upper() in txt.upper()
        u = r.get("usage", {})
        tim = r.get("timings", {})
        gen_toks += tim.get("predicted_n", 0); gen_time += tim.get("predicted_ms", 0) / 1000
        prompt_toks += tim.get("prompt_n", 0); prompt_time += tim.get("prompt_ms", 0) / 1000
        peak = max(peak, vram_mib())
        results.append({**f, "answer": txt[:60], "ok": ok,
                        "prompt_tokens": u.get("prompt_tokens", -1)})
        print(f"  d={f['depth']:<5} {f['node']:<22} want {f['checksum']} got {txt[:24]!r} "
              f"{'OK' if ok else 'MISS'}", flush=True)

    proc.terminate()
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
    logf.close()
    time.sleep(3)

    n_ok = sum(1 for r in results if r["ok"])
    return {"config": tag, "cache_type_k": ctk, "cache_type_v": ctv, "ctx": ctx,
            "load_s": load_s, "vram_loaded_mib": vram_loaded, "vram_peak_mib": peak,
            "score": f"{n_ok}/{len(results)}", "accuracy": round(n_ok / len(results), 3),
            "gen_tok_s": round(gen_toks / gen_time, 1) if gen_time else None,
            "prompt_tok_s": round(prompt_toks / prompt_time, 1) if prompt_time else None,
            "prompt_tokens": results[0].get("prompt_tokens") if results else None,
            "results": results}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--ctx", type=int, default=16384)
    ap.add_argument("--records", type=int, default=560)
    ap.add_argument("--needles", type=int, default=12)
    ap.add_argument("--configs", default="f16:f16,q8_0:q8_0,q4_0:q4_0,q8_0:q4_0")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    logdir = os.path.dirname(os.path.abspath(a.out or "kv.json")) or "."
    os.makedirs(logdir, exist_ok=True)
    corpus, facts = make_corpus(a.records, a.needles)
    print(f"corpus {len(corpus)} chars, {a.records} records, {len(facts)} needles; "
          f"idle VRAM {vram_mib()} MiB")

    out = {"model": a.model, "ctx": a.ctx, "records": a.records,
           "idle_vram_mib": vram_mib(), "runs": []}
    for spec in a.configs.split(","):
        ctk, ctv = spec.split(":")
        out["runs"].append(run_config(a.model, ctk, ctv, a.ctx, corpus, facts, logdir))
        if a.out:
            with open(a.out, "w") as fh:
                json.dump(out, fh, indent=1)

    print("\n=== summary ===")
    print(f"{'config':<14}{'score':<9}{'acc':<8}{'vram peak':<11}{'gen t/s':<10}{'prompt t/s'}")
    for r in out["runs"]:
        if "error" in r:
            print(f"{r['config']:<14}{r['error']}")
            continue
        print(f"{r['config']:<14}{r['score']:<9}{r['accuracy']:<8}"
              f"{r['vram_peak_mib']:<11}{str(r['gen_tok_s']):<10}{r['prompt_tok_s']}")


if __name__ == "__main__":
    main()
