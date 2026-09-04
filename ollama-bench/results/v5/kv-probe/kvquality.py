"""T2: does KV cache quantization cost long-context recall, and does asymmetric K/V help?

Runs llama-server directly (Ollama's own vendored build) so K and V can be given
different types -- something Ollama itself cannot express, since it sets both from the
single OLLAMA_KV_CACHE_TYPE. Ollama must have nothing loaded before this runs.

For each (cache_type_k, cache_type_v) config: launch a server, fill the context with a
fixed haystack of records, ask N needle questions with greedy decoding, score exact
match on the needle value. Records VRAM peak and throughput beside the score.

Usage: python kvquality.py --model <blob> --ctx 16384 --configs f16:f16,q8_0:q8_0,q4_0:q4_0,q8_0:q4_0
"""
import argparse, csv, json, os, random, re, socket, subprocess, sys, time, urllib.request, urllib.error

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


def vram_mib(timeout=30):
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used",
                            "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=timeout)
        return int(o.stdout.strip().splitlines()[0])
    except Exception:
        return -1


def _llama_server_pids(timeout=60):
    """Return llama-server.exe PIDs from tasklist; INFO's no-tasks line is not CSV."""
    try:
        o = subprocess.run(["tasklist", "/FI", "IMAGENAME eq llama-server.exe",
                            "/FO", "CSV", "/NH"],
                           capture_output=True, text=True, timeout=timeout)
    except Exception as e:
        return None, str(e)
    pids = []
    try:
        for row in csv.reader(o.stdout.splitlines()):
            if len(row) >= 2 and row[0].lower() == "llama-server.exe":
                pids.append(int(row[1]))
    except (ValueError, csv.Error) as e:
        return None, str(e)
    return pids, None


def _port_is_free():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # SO_REUSEADDR would let this bind test lie about an in-use Windows port.
            sock.bind(("127.0.0.1", PORT))
        return True
    except OSError:
        return False


def cleanup_barrier(proc=None, *, reason="", idle_ceiling=4000, timeout=180):
    """Stop all server trees and prove the port, GPU, and process list are quiescent."""
    started = time.monotonic()
    deadline = started + timeout
    result = {"ok": False, "reason": "", "waited_s": 0.0,
              "vram_samples": [], "port_free": False, "killed_pids": [],
              "stray_pids_remaining": []}
    print(f"  [cleanup] start ok=pending waited_s=0.0 reason={reason or 'unspecified'}",
          flush=True)

    def finish(ok, why=""):
        result["ok"] = ok
        result["reason"] = "" if ok else why
        result["waited_s"] = round(time.monotonic() - started, 1)
        print(f"  [cleanup] finish ok={result['ok']} waited_s={result['waited_s']} "
              f"reason={result['reason'] or 'none'}", flush=True)
        return result

    def remaining():
        return max(0.0, deadline - time.monotonic())

    def command_timeout(limit):
        return min(limit, max(0.001, remaining()))

    try:
        if proc is not None:
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                proc.wait(timeout=min(5, max(0.001, remaining())))
            except (subprocess.TimeoutExpired, ValueError):
                if remaining() <= 0:
                    return finish(False, "timeout waiting for server process")
                try:
                    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                                   capture_output=True,
                                   timeout=command_timeout(60))
                except Exception:
                    pass
            try:
                proc.wait(timeout=min(5, max(0.001, remaining())))
            except (subprocess.TimeoutExpired, ValueError):
                return finish(False, "server process did not exit")

        pids, tasklist_error = _llama_server_pids(timeout=command_timeout(60))
        if tasklist_error:
            return finish(False, f"could not enumerate llama-server.exe: {tasklist_error}")
        for pid in pids:
            if remaining() <= 0:
                return finish(False, "cleanup timeout")
            result["killed_pids"].append(pid)
            try:
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                               capture_output=True,
                               timeout=command_timeout(60))
            except Exception:
                pass

        while remaining() > 0 and not _port_is_free():
            time.sleep(min(0.2, remaining()))
        result["port_free"] = _port_is_free()
        if not result["port_free"]:
            return finish(False, "port 18080 did not become free")

        # One low sample is not a drain: require three consecutive quiescent readings.
        consecutive = 0
        while consecutive < 3 and remaining() > 0:
            sample = vram_mib(timeout=command_timeout(30))
            result["vram_samples"].append(sample)
            if sample != -1 and sample <= idle_ceiling:
                consecutive += 1
            else:
                consecutive = 0
            if consecutive < 3 and remaining() > 0:
                time.sleep(min(2, remaining()))
        if consecutive < 3:
            return finish(False, "VRAM did not reach three consecutive quiescent samples")

        pids, tasklist_error = _llama_server_pids(timeout=command_timeout(60))
        if tasklist_error:
            return finish(False, f"could not recheck llama-server.exe: {tasklist_error}")
        result["stray_pids_remaining"] = pids
        if pids:
            return finish(False, "llama-server.exe reappeared after VRAM drain")
        return finish(True)
    except BaseException as e:
        return finish(False, f"cleanup error: {e}")


def _log_tail(path, lines=40):
    try:
        with open(path, "rb") as fh:
            return b"\n".join(fh.read().splitlines()[-lines:]).decode(errors="replace")
    except Exception as e:
        return f"<could not read server log: {e}>"


def run_config(model, ctk, ctv, ctx, corpus, facts, logdir, idle_ceiling=4000,
               cleanup_timeout=180):
    tag = f"{ctk}-{ctv}"
    pre_cleanup = cleanup_barrier(reason="before launch", idle_ceiling=idle_ceiling,
                                  timeout=cleanup_timeout)
    if not pre_cleanup["ok"]:
        return {"config": tag,
                "error": f"cleanup barrier failed before launch: {pre_cleanup['reason']}",
                "cleanup": pre_cleanup}
    logf = open(os.path.join(logdir, f"server-{tag}.log"), "wb")
    cmd = [SERVER, "--model", model, "--port", str(PORT), "--host", "127.0.0.1",
           "--no-webui", "--offline", "-c", str(ctx), "-np", "1",
           "-ngl", "99", "--flash-attn", "on",
           "--cache-type-k", ctk, "--cache-type-v", ctv,
           "-b", "512", "-ub", "512", "--no-warmup"]
    print(f"\n### {tag}  (ctx {ctx})", flush=True)
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, env=server_env())
    try:
        healthy = wait_health(proc)
    except BaseException as e:
        healthy = False
        health_error = str(e)
    else:
        health_error = ""
    if not healthy:
        cleanup = cleanup_barrier(proc, reason="health failure", idle_ceiling=idle_ceiling,
                                  timeout=cleanup_timeout)
        logf.close()
        tail = _log_tail(os.path.join(logdir, f"server-{tag}.log"))
        error = "server did not become healthy"
        if health_error:
            error += f": {health_error}"
        return {"config": tag, "error": error, "log_tail": tail, "cleanup": cleanup}
    load_s = round(time.time() - t0, 1)
    vram_loaded = vram_mib()

    results, peak = [], vram_loaded
    sys_msg = ("You answer questions about a configuration dump. Answer with the exact value "
               "only -- no explanation, no punctuation, no restating the question.")
    gen_toks = gen_time = prompt_toks = prompt_time = 0

    try:
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
    except BaseException as e:
        logf.close()
        cleanup = cleanup_barrier(proc, reason="question loop failure",
                                  idle_ceiling=idle_ceiling, timeout=cleanup_timeout)
        return {"config": tag, "error": f"question loop failed: {e}", "cleanup": cleanup}

    logf.close()
    cleanup = cleanup_barrier(proc, reason="normal completion", idle_ceiling=idle_ceiling,
                              timeout=cleanup_timeout)

    n_ok = sum(1 for r in results if r["ok"])
    return {"config": tag, "cache_type_k": ctk, "cache_type_v": ctv, "ctx": ctx,
            "load_s": load_s, "vram_loaded_mib": vram_loaded, "vram_peak_mib": peak,
            "score": f"{n_ok}/{len(results)}", "accuracy": round(n_ok / len(results), 3),
            "gen_tok_s": round(gen_toks / gen_time, 1) if gen_time else None,
            "prompt_tok_s": round(prompt_toks / prompt_time, 1) if prompt_time else None,
            "prompt_tokens": results[0].get("prompt_tokens") if results else None,
            "results": results, "cleanup": cleanup}


def lifecycle_cycle(model, ctx, logdir, cycle, idle_ceiling, cleanup_timeout):
    logf = open(os.path.join(logdir, f"lifecycle-{cycle}.log"), "wb")
    cmd = [SERVER, "--model", model, "--port", str(PORT), "--host", "127.0.0.1",
           "--no-webui", "--offline", "-c", str(ctx), "-np", "1", "-ngl", "99",
           "--flash-attn", "on", "--cache-type-k", "f16", "--cache-type-v", "f16",
           "-b", "512", "-ub", "512", "--no-warmup"]
    proc = None
    t0 = time.time()
    healthy = False
    try:
        proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, env=server_env())
        try:
            healthy = wait_health(proc)
        except BaseException:
            healthy = False
    finally:
        health_s = round(time.time() - t0, 1) if proc is not None else None
        # Record what the card actually held WHILE THE SERVER WAS UP, before teardown.
        # Without this the artifact cannot distinguish "the drain branch waited for a real
        # multi-GB allocation to fall" from "VRAM was already under the ceiling and there was
        # nothing to drain" -- the post-teardown samples read the same idle baseline either
        # way, and a green result whose evidence does not cover its own claim is exactly the
        # failure mode this harness exists to avoid.
        resident_samples = []
        if healthy:
            for _ in range(3):
                resident_samples.append(vram_mib())
                time.sleep(1)
        cleanup = cleanup_barrier(proc, reason=f"lifecycle selftest cycle {cycle}",
                                  idle_ceiling=idle_ceiling, timeout=cleanup_timeout)
        logf.close()
    good = [v for v in resident_samples if v and v > 0]
    return {"launch_ok": proc is not None and healthy,
            "health_s": health_s,
            "vram_resident_samples_mib": resident_samples,
            "vram_peak_while_healthy_mib": max(good) if good else None,
            "drain_observed": bool(good and max(good) > idle_ceiling),
            "cleanup": cleanup}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--ctx", type=int, default=16384)
    ap.add_argument("--records", type=int, default=560)
    ap.add_argument("--needles", type=int, default=12)
    ap.add_argument("--configs", default="f16:f16,q8_0:q8_0,q4_0:q4_0,q8_0:q4_0")
    ap.add_argument("--out", default=None)
    ap.add_argument("--idle-vram-mib", type=int, default=4000)
    ap.add_argument("--cleanup-timeout", type=int, default=180)
    ap.add_argument("--lifecycle-selftest", action="store_true")
    a = ap.parse_args()

    logdir = os.path.dirname(os.path.abspath(a.out or "kv.json")) or "."
    os.makedirs(logdir, exist_ok=True)
    if a.lifecycle_selftest:
        pre_cleanup = cleanup_barrier(reason="lifecycle selftest pre",
                                      idle_ceiling=a.idle_vram_mib, timeout=a.cleanup_timeout)
        cycles = []
        if pre_cleanup["ok"]:
            cycles.append(lifecycle_cycle(a.model, a.ctx, logdir, 1, a.idle_vram_mib,
                                          a.cleanup_timeout))
            cycles.append(lifecycle_cycle(a.model, a.ctx, logdir, 2, a.idle_vram_mib,
                                          a.cleanup_timeout))
        verdict = {"lifecycle_selftest": True, "pre_cleanup": pre_cleanup,
                   "cycles": cycles,
                   "ok": pre_cleanup["ok"] and len(cycles) == 2 and
                   all(c["launch_ok"] and c["cleanup"]["ok"] for c in cycles),
                   # ok says the cycle completed; drain_branch_proven says the run actually
                   # exercised the branch that waits for a real allocation to fall. They are
                   # different claims and the artifact must carry both.
                   "drain_branch_proven": any(c.get("drain_observed") for c in cycles)}
        if a.out:
            with open(a.out, "w") as fh:
                json.dump(verdict, fh, indent=1)
        print(json.dumps(verdict, indent=1))
        return
    corpus, facts = make_corpus(a.records, a.needles)
    print(f"corpus {len(corpus)} chars, {a.records} records, {len(facts)} needles; "
          f"idle VRAM {vram_mib()} MiB")

    out = {"model": a.model, "ctx": a.ctx, "records": a.records,
           "idle_vram_mib": vram_mib(), "runs": []}
    for spec in a.configs.split(","):
        ctk, ctv = spec.split(":")
        out["runs"].append(run_config(a.model, ctk, ctv, a.ctx, corpus, facts, logdir,
                                       a.idle_vram_mib, a.cleanup_timeout))
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
