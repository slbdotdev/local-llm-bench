"""Luna reference arm driver for the v5 gate suite (tiny + large), one trial.

prep -> run (codex exec, pool of 8) -> grade, mirroring prep_gate_sandboxes.py exactly on
the prep and grade halves.

Usage:
  python3 run_luna_gate.py <band>        # band in {tiny, large}
"""
import json, os, re, shutil, subprocess, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(HERE) == "gate-luna":
    HERE = os.path.dirname(HERE)  # archived copy: the suites live one level up
BANDS = {
    "tiny": os.path.join(HERE, "round2", "suite-0"),
    "large": os.path.join(HERE, "round3", "suite"),
}
GATE = os.path.join(HERE, "gate-luna")
TASKS = ["g01", "g02", "g03", "g04", "t01", "t02", "t03", "t04"]

SCORE_RE = re.compile(r"^SCORE\s+(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$", re.M)
VERDICT_RE = re.compile(r"^VERDICT\s+(\w+)\s*$", re.M)
TOKENS_RE = re.compile(r"^tokens used[:\s]*\n?\s*([\d,]+)\s*$", re.M)
RATE_RE = re.compile(r"usage limit|rate limit|\b429\b", re.I)

TIMEOUT = 900

lock = threading.Lock()
state = {"max_conc": 8, "active": 0, "rate_events": []}
cond = threading.Condition(lock)


def band_dir(band):
    return os.path.join(GATE, band, "trial-0")


def prep(band):
    suite = BANDS[band]
    for t in TASKS:
        sb = os.path.join(band_dir(band), t)
        if os.path.exists(sb):
            shutil.rmtree(sb)
        os.makedirs(sb)
        seed = os.path.join(suite, t, "seed")
        if os.path.isdir(seed):
            shutil.copytree(seed, sb, dirs_exist_ok=True)
    print(f"[prep] {band}: {len(TASKS)} sandboxes under {band_dir(band)}", flush=True)


def parse_tokens(log):
    m = TOKENS_RE.findall(log)
    if m:
        return int(m[-1].replace(",", ""))
    m2 = re.findall(r"tokens used\s*\n\s*([\d,]+)", log)
    if m2:
        return int(m2[-1].replace(",", ""))
    return None


def rate_limited_at_start(log, rc, finalp):
    """Usage/rate limit reported before any work.

    The transcript echoes the prompt and every file the model reads, so both are stripped:
    the echoed user block is dropped, everything from the first tool call onward is cut,
    and only the remaining head is searched. A run that finished with a final message is
    never treated as rate-limited.
    """
    keep, skipping = [], False
    for ln in log.splitlines():
        s = ln.strip()
        if s == "user":
            skipping = True
            continue
        if skipping:
            if s in ("codex", "thinking") or s.startswith("exec ") or s.startswith("tokens used"):
                skipping = False
            else:
                continue
        if s.startswith("exec ") or s.startswith("apply_patch"):
            break  # work has started
        keep.append(ln)
    head = "\n".join(keep)[:1500]
    if not RATE_RE.search(head):
        return False
    got_final = os.path.exists(finalp) and os.path.getsize(finalp) > 0
    return rc != 0 or not got_final


def acquire():
    with cond:
        while state["active"] >= state["max_conc"]:
            cond.wait()
        state["active"] += 1


def release():
    with cond:
        state["active"] -= 1
        cond.notify_all()


def run_one(band, task, attempt=1):
    suite = BANDS[band]
    sb = os.path.join(band_dir(band), task)
    prompt = os.path.join(suite, task, "prompt.md")
    finalp = os.path.join(band_dir(band), f"{task}.final.txt")
    logp = os.path.join(band_dir(band), f"{task}.codex.log")
    cmd = ["timeout", str(TIMEOUT), "codex", "exec", "--skip-git-repo-check",
           "-C", sb, "-m", "gpt-5.6-luna", "-c", "model_reasoning_effort=high",
           "-c", "project_doc_max_bytes=0", "--color", "never",
           "-o", finalp, "-"]
    acquire()
    try:
        t0 = time.time()
        with open(prompt, "rb") as fin, open(logp, "wb") as fout:
            p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=subprocess.STDOUT)
        wall = time.time() - t0
    finally:
        release()
    log = open(logp, encoding="utf-8", errors="replace").read()
    rec = {"wall_s": round(wall, 1), "codex_rc": p.returncode,
           "timed_out": p.returncode == 124, "tokens_used": parse_tokens(log),
           "attempt": attempt}
    if rate_limited_at_start(log, p.returncode, finalp) and attempt == 1:
        with lock:
            state["rate_events"].append({"band": band, "task": task,
                                         "at": time.strftime("%H:%M:%S")})
            state["max_conc"] = 4
        print(f"[rate-limit] {band}/{task}: backing off 60 s, concurrency -> 4", flush=True)
        time.sleep(60)
        with cond:
            cond.notify_all()
        return run_one(band, task, attempt=2)
    print(f"[run] {band}/{task} rc={p.returncode} wall={wall:.0f}s "
          f"tokens={rec['tokens_used']}", flush=True)
    return rec


def grade(band, runmeta):
    suite = BANDS[band]
    out = {}
    for t in TASKS:
        sb = os.path.join(band_dir(band), t)
        rec = dict(runmeta.get(t, {}))
        if not os.path.isdir(sb):
            rec.update({"error": "no sandbox", "pass": False})
            out[t] = rec
            continue
        shutil.copy(os.path.join(suite, t, "test.py"),
                    os.path.join(sb, "_hidden_test.py"))
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        try:
            p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sb, env=env,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=60)
            so, rc = p.stdout, p.returncode
        except subprocess.TimeoutExpired:
            so, rc = "", -1
        sc = SCORE_RE.findall(so)
        vd = VERDICT_RE.findall(so)
        os.remove(os.path.join(sb, "_hidden_test.py"))
        rec.update({"pass": rc == 0 and "PASS" in so,
                    "score": f"{sc[-1][0]}/{sc[-1][1]}" if sc else None,
                    "verdict": vd[-1] if vd else None, "rc": rc,
                    "tail": so.strip()[-160:]})
        out[t] = rec
        print(f"{t:5s} {'PASS' if rec['pass'] else 'FAIL':4s} score={rec['score']} "
              f"verdict={rec['verdict']}", flush=True)
    out["_meta"] = {"band": band, "rate_limit_events": state["rate_events"],
                    "final_max_concurrency": state["max_conc"]}
    p = os.path.join(band_dir(band), "results.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    n = sum(1 for k, v in out.items() if k != "_meta" and v.get("pass"))
    print(f"\n{band}: {n}/{len(TASKS)} passed -> {p}", flush=True)


def main():
    band = sys.argv[1]
    prep(band)
    results = {}
    threads = []

    def worker(t):
        results[t] = run_one(band, t)

    t_start = time.time()
    for t in TASKS:
        th = threading.Thread(target=worker, args=(t,))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
    print(f"[run] {band} band complete in {time.time()-t_start:.0f}s", flush=True)
    grade(band, results)


if __name__ == "__main__":
    main()
