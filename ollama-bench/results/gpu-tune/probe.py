"""Fast fit/throughput probe for one (model, num_ctx, num_gpu) config.

Loads the model, reads layer residency + buffer sizes from server.log, samples
nvidia-smi VRAM and host free RAM, then measures gen/prompt tok/s at empty
context and at a near-full fill. Always unloads (keep_alive 0) at the end.
"""
import json, os, re, subprocess, sys, time, urllib.request, argparse

OLLAMA = "http://127.0.0.1:11434"
LOG = os.environ.get("PROBE_SERVER_LOG") or os.path.expanduser("~/AppData/Local/Ollama/server.log")


def post(path, body, timeout=900):
    req = urllib.request.Request(OLLAMA + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def get(path, timeout=10):
    with urllib.request.urlopen(OLLAMA + path, timeout=timeout) as r:
        return json.load(r)


def vram_mib():
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=30)
        return int(o.stdout.strip().splitlines()[0])
    except Exception:
        return -1


def free_ram_mib():
    try:
        o = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"],
                           capture_output=True, text=True, timeout=60)
        return int(int(o.stdout.strip()) / 1024)
    except Exception:
        return -1


def unload_all(timeout=120):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            ps = get("/api/ps")
        except Exception:
            time.sleep(2); continue
        if not ps.get("models"):
            return True
        for m in ps["models"]:
            try:
                post("/api/generate", {"model": m["model"], "keep_alive": 0}, timeout=60)
            except Exception:
                pass
        time.sleep(3)
    return False


def log_size():
    try:
        return os.path.getsize(LOG)
    except Exception:
        return 0


def log_tail(offset):
    try:
        with open(LOG, "rb") as f:
            f.seek(offset)
            return f.read().decode("utf-8", "replace")
    except Exception:
        return ""


def parse_log(txt):
    out = {}
    m = None
    for m in re.finditer(r"offloaded (\d+)/(\d+) layers to GPU", txt):
        pass
    if m:
        out["layers"] = f"{m.group(1)}/{m.group(2)}"
        out["layers_full"] = m.group(1) == m.group(2)
    for key, pat in [("model_mib", r"CUDA0 model buffer size\s*=\s*([\d.]+) MiB"),
                     ("kv_cuda_mib", r"CUDA0 KV buffer size\s*=\s*([\d.]+) MiB"),
                     ("kv_cpu_mib", r"CPU KV buffer size\s*=\s*([\d.]+) MiB"),
                     ("compute_mib", r"CUDA0 compute buffer size\s*=\s*([\d.]+) MiB")]:
        mm = None
        for mm in re.finditer(pat, txt):
            pass
        if mm:
            out[key] = float(mm.group(1))
    mm = None
    for mm in re.finditer(r"llama_kv_cache: size = ([\d.]+) MiB \(\s*(\d+) cells,\s*(\d+) layers", txt):
        pass
    if mm:
        out["kv_total_mib"] = float(mm.group(1)); out["kv_cells"] = int(mm.group(2)); out["kv_layers"] = int(mm.group(3))
    mm = None
    for mm in re.finditer(r"graph splits = (\d+)", txt):
        pass
    if mm:
        out["graph_splits"] = int(mm.group(1))
    if re.search(r"out of memory|OutOfMemory|CUDA error|failed to allocate", txt, re.I):
        out["oom_text"] = True
    return out


FILLER = ("The quick brown fox jumps over the lazy dog while the committee reviews quarterly "
          "logistics reports, weather patterns, and the migration of monarch butterflies. ")


def gen(model, num_ctx, num_gpu, fill, npred=200):
    text = (FILLER * (fill * 6 // len(FILLER) + 1))[: int(fill * 5.95)] if fill else ""
    prompt = f"Session {fill}. " + (text + "\n\n" if text else "") + \
             "Write a detailed 300 word explanation of how hash tables work."
    opts = {"num_predict": npred, "temperature": 0.2, "num_ctx": num_ctx}
    if num_gpu is not None:
        opts["num_gpu"] = num_gpu
    r = post("/api/generate", {"model": model, "prompt": prompt, "stream": False,
                               "think": False, "options": opts})
    return {"fill_tokens": r["prompt_eval_count"],
            "prompt_tps": round(r["prompt_eval_count"] / max(r.get("prompt_eval_duration", 1), 1) * 1e9, 1),
            "gen_tps": round(r["eval_count"] / (r["eval_duration"] / 1e9), 1),
            "eval_count": r["eval_count"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--num-ctx", type=int, required=True)
    ap.add_argument("--num-gpu", type=int, default=None)
    ap.add_argument("--fills", default=None, help="comma list; default 0 and num_ctx-4096")
    ap.add_argument("--note", default="")
    a = ap.parse_args()

    res = {"model": a.model, "num_ctx": a.num_ctx, "num_gpu": a.num_gpu, "note": a.note,
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
    unload_all()
    time.sleep(2)
    res["vram_idle_mib"] = vram_mib()
    res["free_ram_before_mib"] = free_ram_mib()
    off = log_size()

    fills = [int(x) for x in a.fills.split(",")] if a.fills else [0, max(0, a.num_ctx - 4096)]
    t0 = time.time()
    try:
        first = gen(a.model, a.num_ctx, a.num_gpu, fills[0])
        res["load_plus_first_s"] = round(time.time() - t0, 1)
    except Exception as e:
        res["error"] = f"{type(e).__name__}: {e}"
        res.update(parse_log(log_tail(off)))
        res["vram_loaded_mib"] = vram_mib()
        print(json.dumps(res)); unload_all(); return

    res["vram_loaded_mib"] = vram_mib()
    res.update(parse_log(log_tail(off)))
    try:
        ps = get("/api/ps")
        for m in ps.get("models", []):
            if m["model"].split(":")[0] == a.model.split(":")[0]:
                res["ps_size_gb"] = round(m["size"] / 2**30, 2)
                res["ps_vram_gb"] = round(m.get("size_vram", 0) / 2**30, 2)
                res["ps_pct_gpu"] = round(100 * m.get("size_vram", 0) / m["size"]) if m["size"] else 0
    except Exception:
        pass

    curve = [first]
    for f in fills[1:]:
        try:
            curve.append(gen(a.model, a.num_ctx, a.num_gpu, f))
        except Exception as e:
            curve.append({"fill_target": f, "error": f"{type(e).__name__}: {e}"})
    res["curve"] = curve
    res["vram_peak_mib"] = vram_mib()
    res["free_ram_after_mib"] = free_ram_mib()
    unload_all()
    time.sleep(2)
    res["vram_unloaded_mib"] = vram_mib()
    res["free_ram_unloaded_mib"] = free_ram_mib()
    print(json.dumps(res))


main()
