"""Move the half-installed cuda_v13 backend aside and see whether Ollama recovers the GPU.

2026-09-03 21:16-21:17 an Ollama install/upgrade was interrupted. It left
lib/ollama/cuda_v13 holding only concrt140.dll, cublas64_13.dll and a 477 MB Inno Setup
temp file (is-XMOXADJX6M.tmp); ggml-cuda.dll, cublasLt64_13.dll and cudart64_13.dll are
absent. lib/ollama/cuda_v12 is complete and untouched from the working 16:49 install.

Measured consequence: Ollama serves entirely on CPU. /api/ps reports pct_gpu 0 and
0.00 GB VRAM, and generation runs at 3.2 tok/s against the 51-53 tok/s measured on
2026-09-03. A direct llama-server launch logs "failed to load ...cuda_v13\\ggml-cuda.dll"
then "no usable GPU found, --gpu-layers option will be ignored".

This is deliberately the smallest reversible action: RENAME, never delete, so the evidence
survives and one rename undoes it. It does not touch ansible-slb and runs no playbook.
A proper repair is a reinstall/converge and belongs to whoever owns that.

CAVEAT, stated because it may well be why this fails: an RTX 5080 is Blackwell, sm_120.
Ollama very likely selects cuda_v13 on this card for that reason. Whether the shipped
cuda_v12 build carries sm_120 kernels (or has to fall back to slow PTX JIT) is exactly
what this script measures rather than assumes.

Run with WINDOWS python from WSL:
  /mnt/c/Users/slb/scoop/apps/python/current/python.exe repair-cuda.py [--revert]
"""
import json, os, subprocess, sys, time, urllib.request

OLLAMA_DIR = os.path.expanduser("~/AppData/Local/Programs/Ollama")
LIB = os.path.join(OLLAMA_DIR, "lib", "ollama")
BROKEN = os.path.join(LIB, "cuda_v13")
ASIDE = os.path.join(LIB, "cuda_v13.broken-20260904")
APP = os.path.join(OLLAMA_DIR, "ollama app.exe")
BASE = "http://localhost:11434"


def vram():
    o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=30)
    return o.stdout.strip().splitlines()[0]


def stop_ollama():
    for image in ("ollama app.exe", "ollama.exe"):
        subprocess.run(["taskkill", "/IM", image, "/F"], capture_output=True, timeout=60)
    for _ in range(30):
        time.sleep(1)
        o = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ollama.exe", "/FO", "CSV", "/NH"],
                           capture_output=True, text=True, timeout=60)
        if "ollama.exe" not in o.stdout.lower():
            return True
    return False


def start_ollama():
    # DETACHED_PROCESS so the service outlives this script, exactly as the tray app does.
    subprocess.Popen([APP], creationflags=0x00000008 | 0x00000200,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(60):
        time.sleep(2)
        try:
            with urllib.request.urlopen(BASE + "/api/tags", timeout=5) as r:
                json.load(r)
            return True
        except Exception:
            pass
    return False


def probe(model="q27-Q3_K_S"):
    """Load, generate a few tokens, and report the residency split and real tok/s."""
    body = {"model": model, "prompt": "hi", "stream": False, "think": False,
            "options": {"num_predict": 16}}
    req = urllib.request.Request(BASE + "/api/generate", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as r:
        g = json.load(r)
    wall = time.time() - t0
    tps = g["eval_count"] / (g["eval_duration"] / 1e9) if g.get("eval_duration") else 0.0
    with urllib.request.urlopen(BASE + "/api/ps", timeout=15) as r:
        ps = json.load(r)
    split = None
    for m in ps.get("models", []):
        size, vr = m["size"], m.get("size_vram", 0)
        split = {"name": m["name"], "size_gb": round(size / 2**30, 2),
                 "vram_gb": round(vr / 2**30, 2),
                 "pct_gpu": round(100 * vr / size) if size else 0}
    # put the card back the way we found it
    body = {"model": model, "keep_alive": 0}
    req = urllib.request.Request(BASE + "/api/generate", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=120).read()
    except Exception:
        pass
    return {"wall_s": round(wall, 1), "gen_tok_s": round(tps, 1), "ps": split,
            "vram_mib_during_load": None}


def main():
    revert = "--revert" in sys.argv
    src, dst = (ASIDE, BROKEN) if revert else (BROKEN, ASIDE)
    print(f"idle VRAM {vram()} MiB")
    if not os.path.isdir(src):
        print(f"nothing to do: {src} is not a directory")
        return 1
    if os.path.exists(dst):
        print(f"refusing: {dst} already exists")
        return 1
    print("stopping ollama ...", flush=True)
    if not stop_ollama():
        print("ollama.exe did not exit; aborting without touching any files")
        return 1
    os.rename(src, dst)
    print(f"renamed\n  {src}\n  -> {dst}", flush=True)
    print("starting ollama ...", flush=True)
    if not start_ollama():
        print("ollama did not come back up")
        return 1
    print("probing GPU residency ...", flush=True)
    r = probe()
    print(json.dumps(r, indent=1))
    ok = bool(r["ps"] and r["ps"]["pct_gpu"] >= 90 and r["gen_tok_s"] > 20)
    print("VERDICT", "GPU RECOVERED" if ok else "STILL CPU-ONLY")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
