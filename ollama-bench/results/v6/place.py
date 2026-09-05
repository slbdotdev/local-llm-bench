"""v6 phase 0 placement: measure one quant at one context rung.

Run with the WINDOWS interpreter from WSL, never ssh:
  PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe
  "$PY" results/v6/place.py q27-IQ2_M-64k 65536

Records, per plan section 5: quant, num_ctx, resident GB (/api/ps size/2**30), pct_gpu,
nvidia-smi peak MiB, load time, gen tok/s at empty context, gen tok/s at ~90% fill,
prompt tok/s at that fill, TTFT at that fill, and the pass/marginal/spill verdict.

Appends one object to results/v6/placement.json. Never rewrites a record.
"""
import json, os, subprocess, sys, threading, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE = "http://localhost:11434"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "placement.json")
CHARS_PER_TOKEN = 4.664          # measured, v5 authoring/bands-2026-09-05.json
LINE_GB = 14.2                   # fair-weather resident line
PASS_TPS = 35.0
SPILL_TPS = 20.0


def post(path, body, timeout=900):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def get(path, timeout=30):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return json.load(r)


def unload_all():
    try:
        for m in get("/api/ps").get("models", []):
            try:
                post("/api/generate", {"model": m["name"], "keep_alive": 0}, timeout=120)
            except Exception:
                pass
    except Exception:
        pass
    time.sleep(3)


class Smi(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.peak = 0
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set():
            try:
                o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used",
                                    "--format=csv,noheader,nounits"],
                                   capture_output=True, text=True, timeout=20)
                v = int(o.stdout.strip().splitlines()[0])
                self.peak = max(self.peak, v)
            except Exception:
                pass
            self._stop.wait(2.0)

    def stop(self):
        self._stop.set()


FILLER = (
    "The migration log records every change applied to the ledger service between the "
    "March release and the June freeze, together with the operator who applied it, the "
    "rollback token, and the observed effect on p99 latency. Entries are ordered by "
    "commit time, not by deploy time, and the two diverge whenever a change was staged "
    "behind a feature flag. Reconciliation of the two orderings is left to the reader.\n"
)


def make_fill(target_tokens):
    target_chars = int(target_tokens * CHARS_PER_TOKEN)
    parts, n = [], 0
    i = 0
    while n < target_chars:
        parts.append("## Section %d\n" % i)
        parts.append(FILLER)
        n += len(parts[-1]) + len(parts[-2])
        i += 1
    return "".join(parts)


def manifest_facts(tag):
    """Read the tag's own manifest: model-layer size and whether a vision projector rides
    along. The projector is 0.86 GiB of VRAM this text-only suite never uses, and only some
    of the roster's tags carry one, so every record says which build it measured (D6-9)."""
    base = tag.split(":")[0]
    path = os.path.join(os.path.expanduser("~"), ".ollama", "models", "manifests",
                        "registry.ollama.ai", "library", base, "latest")
    path = path.replace("/", os.sep)
    try:
        with open(path, encoding="utf-8") as f:
            m = json.load(f)
        model = proj = 0
        for l in m.get("layers", []):
            if l["mediaType"].endswith(".model"):
                model = l["size"]
            elif l["mediaType"].endswith(".projector"):
                proj = l["size"]
        return round(model / 2 ** 30, 2), round(proj / 2 ** 30, 2), proj > 0
    except Exception:
        return None, None, None


def ps_for(tag):
    try:
        for m in get("/api/ps").get("models", []):
            if m["name"].split(":")[0] == tag or m.get("model", "").split(":")[0] == tag:
                size, vram = m.get("size", 0), m.get("size_vram", 0)
                return (round(size / 2 ** 30, 2), round(vram / 2 ** 30, 2),
                        round(100 * vram / size) if size else None,
                        m.get("context_length"))
    except Exception:
        pass
    return None, None, None, None


def main():
    tag = sys.argv[1]
    num_ctx = int(sys.argv[2])
    fill_timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 1200
    quant = tag.replace("q27-", "").rsplit("-", 1)[0]

    mg, pg, has_proj = manifest_facts(tag)
    rec = {"quant": quant, "tag": tag, "num_ctx": num_ctx,
           "manifest_model_gib": mg, "manifest_projector_gib": pg,
           "has_projector": has_proj,
           "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    unload_all()
    smi = Smi()
    smi.start()
    try:
        # 1. Load, timed.
        t0 = time.time()
        try:
            post("/api/generate", {"model": tag, "prompt": "hi", "stream": False,
                                   "think": False,
                                   "options": {"num_predict": 8, "num_ctx": num_ctx},
                                   "keep_alive": "20m"}, timeout=900)
        except Exception as e:
            rec.update(verdict="load_failed", error=str(e)[:300],
                       load_s=round(time.time() - t0, 1))
            return finish(rec, smi)
        rec["load_s"] = round(time.time() - t0, 1)
        size_gb, vram_gb, pct, ctx = ps_for(tag)
        rec.update(resident_gb=size_gb, vram_gb=vram_gb, pct_gpu=pct, ps_context_length=ctx)

        # 2. Generation rate at empty context.
        try:
            r = post("/api/generate", {"model": tag, "stream": False, "think": False,
                                       "prompt": "Explain how a write-ahead log makes a "
                                                 "database crash-safe, in detail.",
                                       "options": {"num_predict": 300, "num_ctx": num_ctx},
                                       "keep_alive": "20m"}, timeout=900)
            rec["gen_tps_empty"] = round(r["eval_count"] / (r["eval_duration"] / 1e9), 2)
        except Exception as e:
            rec["gen_tps_empty"] = None
            rec["empty_error"] = str(e)[:200]

        # 3. Fill to ~90% of num_ctx and measure prompt rate, gen rate, TTFT.
        target = int(num_ctx * 0.90)
        body = make_fill(target - 400)
        prompt = (body + "\n\nQuestion: in two sentences, what does the document above "
                         "record and how are its entries ordered?\n")
        t0 = time.time()
        try:
            r = post("/api/generate", {"model": tag, "stream": False, "think": False,
                                       "prompt": prompt,
                                       "options": {"num_predict": 200, "num_ctx": num_ctx},
                                       "keep_alive": "20m"}, timeout=fill_timeout)
        except Exception as e:
            rec.update(verdict="spill", fill_error=str(e)[:200],
                       fill_wall_s=round(time.time() - t0, 1),
                       fill_target_tokens=target)
            return finish(rec, smi)
        rec["fill_wall_s"] = round(time.time() - t0, 1)
        rec["fill_prompt_tokens"] = r.get("prompt_eval_count")
        rec["fill_target_tokens"] = target
        ped = r.get("prompt_eval_duration") or 1
        rec["prompt_tps_fill"] = round(r["prompt_eval_count"] / (ped / 1e9), 1)
        rec["gen_tps_fill"] = round(r["eval_count"] / (r["eval_duration"] / 1e9), 2)
        rec["ttft_fill_s"] = round((r.get("load_duration", 0) + ped) / 1e9, 1)
        rec["out_tokens_fill"] = r.get("eval_count")
        s2, v2, p2, _ = ps_for(tag)
        if s2 is not None:
            rec["resident_gb"] = max(rec.get("resident_gb") or 0, s2)
            rec["vram_gb"] = max(rec.get("vram_gb") or 0, v2)
            rec["pct_gpu"] = p2

        # 4. Verdict -- the shared gate, so a rule added later applies to old records too.
        from gate import verdict_of, LINE_GB
        rec["over_resident_line"] = (rec.get("resident_gb") or 0) >= LINE_GB
        v, why = verdict_of(rec)
        rec["verdict"], rec["verdict_why"] = v, why
    finally:
        pass
    return finish(rec, smi)


def finish(rec, smi):
    smi.stop()
    smi.join(timeout=6)
    rec["nvidia_smi_peak_mib"] = smi.peak
    rec["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    data = []
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            data = json.load(f)
    data.append(rec)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    print(json.dumps(rec, indent=1))
    try:
        post("/api/generate", {"model": rec["tag"], "keep_alive": 0}, timeout=120)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
