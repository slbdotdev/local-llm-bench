"""ZCode reference arm driver for the v5 gate suite (tiny + large), one trial.

prep -> run (z-run, pool of 4) -> grade. The prep and grade halves mirror
prep_gate_sandboxes.py exactly, so the numbers mean the same thing as every other arm:

  prep   sandbox <- seed/ only. Never ref/, never test.py, never NOTES.md.
  grade  test.py -> _hidden_test.py, run with cwd=sandbox, PYTHONUTF8=1,
         PYTHONIOENCODING=utf-8, 60 s; pass iff rc == 0 and "PASS" in stdout;
         SCORE n/m and VERDICT word parsed out.

Usage:
  python3 run_zcode_gate.py <band>          # band in {tiny, large}

Requires ZAI_API_KEY in the environment (see run_band.sh). The key is never printed.
"""
import datetime, json, os, re, shutil, subprocess, sys, threading, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))       # .../authoring/gate-zcode
AUTH = os.path.dirname(HERE)                            # .../authoring
BANDS = {
    "tiny": os.path.join(AUTH, "round2", "suite-0"),
    "large": os.path.join(AUTH, "round3", "suite"),
}
TASKS = ["g01", "g02", "g03", "g04", "t01", "t02", "t03", "t04"]
ZRUN = os.path.expanduser("~/.claude/skills/z-run/scripts/z-run")
RUNS = os.path.expanduser("~/.agent-runs")

MODEL = "GLM-5.3-Flash"
EFFORT = "high"
TIMEOUT = 900
IDLE = 5
# Concurrency is read live from conc.txt before every launch, so the pool can be
# dropped (4 -> 2 -> 1) mid-band without restarting and losing in-flight runs.
CONC_FILE = os.path.join(HERE, "conc.txt")
DEFAULT_CONC = 2

# Plan gate. The 5-hour window is shared with the pi prompt campaign and the v7
# roundtable's GLM worker, so this arm stops launching well short of the cap and
# waits for the window to reset rather than racing the other two workloads.
QUOTA_URL = "https://api.z.ai/api/monitor/usage/quota/limit"
QUOTA_STOP_PCT = 85.0
QUOTA_MIN_INTERVAL = 5.0    # seconds; short, because the check now sits at launch

SCORE_RE = re.compile(r"^SCORE\s+(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*$", re.M)
VERDICT_RE = re.compile(r"^VERDICT\s+(\w+)\s*$", re.M)
RUNID_RE = re.compile(r"z-run: run (\S+) started")
# provider-side quota/rate refusals, as ZCode's telemetry spells them
RATE_RE = re.compile(r"rate.?limit|quota|insufficient.balance|\b429\b", re.I)
# a 1302 throttle, in either supervisor spelling (see classify)
RATE1302_RE = re.compile(r"\b1302\b|rate.?limit|\b429\b", re.I)
# a genuine credit/balance refusal, which keeps the quota name
QUOTA_RE = re.compile(r"\b402\b|balance|insufficient|quota exceeded|out of credit", re.I)

lock = threading.Lock()
cond = threading.Condition(lock)
state = {"max_conc": DEFAULT_CONC, "active": 0, "rate_events": [],
         "conc_history": [], "quota_readings": [], "quota_reset": None,
         "gated": []}


def read_quota():
    """(pct_of_5h_window, used, cap, reset_iso) or None if unreadable.

    Numbers only; the key is never printed or logged.
    """
    key = os.environ.get("ZAI_API_KEY")
    if not key:
        return None
    req = urllib.request.Request(QUOTA_URL, headers={"Authorization": "Bearer " + key,
                                                     "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read().decode())
    except Exception:
        return None
    for lim in d.get("data", {}).get("limits", []):
        if lim.get("unit") == 3:        # the 5-hour window
            used, cap = lim["currentValue"], lim["usage"]
            pct = 100.0 * used / cap if cap else 0.0
            reset = datetime.datetime.fromtimestamp(
                lim["nextResetTime"] / 1000, datetime.timezone.utc)
            return pct, used, cap, reset.isoformat(timespec="seconds")
    return None


def quota_gate_open():
    """False when the 5-hour window is at or above the stop threshold.

    Read once per launch at most; an unreadable quota is treated as open rather
    than stalling the arm on a monitoring failure, and is recorded either way.
    """
    with lock:
        last = state.get("quota_last_read", 0)
        cached = state.get("quota_cached")
        if time.time() - last < QUOTA_MIN_INTERVAL and cached is not None:
            return cached
    q = read_quota()
    with lock:
        state["quota_last_read"] = time.time()
        if q is None:
            state["quota_cached"] = True
            state["quota_readings"].append({"at": time.strftime("%H:%M:%SZ", time.gmtime()),
                                            "error": "unreadable"})
            return True
        pct, used, cap, reset = q
        openq = pct < QUOTA_STOP_PCT
        state["quota_cached"] = openq
        state["quota_readings"].append({"at": time.strftime("%H:%M:%SZ", time.gmtime()),
                                        "pct": round(pct, 2), "used": used,
                                        "cap": cap, "reset": reset, "open": openq})
        state["quota_reset"] = reset
        if not openq:
            print("[quota] 5h window at %.2f%% (%s/%s) >= %.0f%% - launching nothing "
                  "more; window resets %s" % (pct, used, cap, QUOTA_STOP_PCT, reset),
                  flush=True)
        return openq


def desired_conc():
    """Live concurrency cap. conc.txt wins if present, else the running value."""
    try:
        with open(CONC_FILE) as fh:
            n = int(fh.read().strip())
        if 1 <= n <= 8:
            return n
    except Exception:
        pass
    return state["max_conc"]


def band_dir(band):
    return os.path.join(HERE, band, "trial-0")


def prep(band, tasks=None):
    suite = BANDS[band]
    for t in (tasks or TASKS):
        sb = os.path.join(band_dir(band), t)
        if os.path.exists(sb):
            shutil.rmtree(sb)
        os.makedirs(sb)
        seed = os.path.join(suite, t, "seed")
        if os.path.isdir(seed):
            shutil.copytree(seed, sb, dirs_exist_ok=True)
    print("[prep] %s: %d sandboxes under %s" % (band, len(tasks or TASKS),
                                                band_dir(band)), flush=True)


def reconstruct(band, task):
    """Rebuild a completed task's run record from its durable artifacts alone.

    Every finished run leaves <task>.result.json and <task>.zrun.log beside the band,
    so a band interrupted part-way (a quota pause, a stopped driver) can be resumed
    without re-running work that already succeeded. wall_s comes from the run's own
    started/ended stamps, which is why nothing is lost when the driver's memory is.
    """
    bd = band_dir(band)
    rp = os.path.join(bd, "%s.result.json" % task)
    if not os.path.exists(rp):
        return None
    try:
        d = json.load(open(rp, encoding="utf-8"))
    except Exception:
        return None
    st = d.get("state")
    wall0 = None
    try:
        _a = datetime.datetime.fromisoformat(d["started"].replace("Z", "+00:00"))
        _b = datetime.datetime.fromisoformat(d["ended"].replace("Z", "+00:00"))
        wall0 = round((_b - _a).total_seconds(), 1)
    except Exception:
        pass
    # A timeout is terminal: the brief makes it a fail and forbids resuming it, so it
    # is kept as a finished record rather than handed a fresh attempt. Re-running it
    # would be trial-shopping, and this arm is one trial.
    if st == "timed_out":
        return {"wall_s": wall0, "run_id": d.get("run_id"), "zrun_rc": 124,
                "timed_out": True, "attempt": 1, "state": st,
                "model": d.get("model"), "variant": d.get("variant"),
                "detail": (d.get("detail") or "")[:600],
                "rate_1302": count_1302(d.get("run_id")),
                "outcome": "timed_out", "reconstructed": True,
                "sandbox_lost": True}
    if st != "succeeded":
        return None
    sb = os.path.join(bd, task)
    if not os.path.isdir(sb) or not os.listdir(sb):
        return None
    wall = None
    try:
        t0 = datetime.datetime.fromisoformat(d["started"].replace("Z", "+00:00"))
        t1 = datetime.datetime.fromisoformat(d["ended"].replace("Z", "+00:00"))
        wall = round((t1 - t0).total_seconds(), 1)
    except Exception:
        pass
    u = d.get("usage") or {}
    return {"wall_s": wall, "run_id": d.get("run_id"), "zrun_rc": 0,
            "timed_out": False, "attempt": 1, "state": d.get("state"),
            "model": d.get("model"), "variant": d.get("variant"),
            "resumes": d.get("resumes"), "detail": (d.get("detail") or "")[:600],
            "in_tokens": u.get("input"), "out_tokens": u.get("output"),
            "cache_read": u.get("cacheRead"), "reasoning_tokens": u.get("reasoning"),
            "model_requests": u.get("modelRequestCount"),
            "rate_1302": count_1302(d.get("run_id")),
            "conc_at_launch": None, "outcome": "ok", "reconstructed": True}


def acquire():
    with cond:
        while True:
            want = desired_conc()
            if want != state["max_conc"]:
                state["conc_history"].append({"at": time.strftime("%H:%M:%S"),
                                              "from": state["max_conc"],
                                              "to": want})
                print("[conc] pool %d -> %d" % (state["max_conc"], want), flush=True)
                state["max_conc"] = want
            if state["active"] < state["max_conc"]:
                break
            cond.wait(timeout=10)   # wake to re-read conc.txt even if nothing freed
        state["active"] += 1
        return state["max_conc"]    # pool in force at launch, not at finish


def release():
    with cond:
        state["active"] -= 1
        cond.notify_all()


def read_run_state(run_id):
    """Pull state, usage, model and variant out of the run's own result.json."""
    rec = {"state": None, "model": None, "variant": None, "resumes": None,
           "in_tokens": None, "out_tokens": None, "cache_read": None,
           "reasoning_tokens": None, "model_requests": None}
    if not run_id:
        return rec
    p = os.path.join(RUNS, run_id, "result.json")
    if not os.path.exists(p):
        return rec
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return rec
    u = d.get("usage") or {}
    rec.update({"state": d.get("state"), "model": d.get("model"),
                "variant": d.get("variant"), "resumes": d.get("resumes"),
                "detail": (d.get("detail") or "")[:600],
                "in_tokens": u.get("input"), "out_tokens": u.get("output"),
                "cache_read": u.get("cacheRead"),
                "reasoning_tokens": u.get("reasoning"),
                "model_requests": u.get("modelRequestCount")})
    return rec


def count_1302(run_id):
    """How many times the plan answered this run with [1302] Rate limit reached.

    ZCode retries a 429 internally with backoff (maxAttempts 11) before it fails the
    turn, so the refusal never surfaces to the driver as a start-of-run error. The
    count is the only honest measure of how hard the plan throttled the run.
    """
    if not run_id:
        return None
    p = os.path.join(RUNS, run_id, "harness.log")
    if not os.path.exists(p):
        return None
    n = 0
    with open(p, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            if "Rate limit reached for requests" in ln:
                n += 1
    return n


def classify(rec, zrun_rc, n1302):
    """ok | rate_limited | quota_exhausted | timed_out | failed.

    A turn that failed after exhausting its 1302 retry attempts against a throttling
    plan is `rate_limited`: a harness/plan outcome, not the model failing the task,
    so it is reported separately and never contaminates the pass rate.

    Two supervisor spellings have to be accepted, because runs on both sides of the
    ansible-slb 2b495f7 converge appear in this arm:
      before: state=quota_exhausted, detail carries reason=rate_limited / 1302
      after:  state=failed,          detail carries the 1302 text
    Both are `rate_limited`. The `quota_exhausted` outcome is reserved for a genuine
    402/balance refusal, which is what the new supervisor uses that state to mean.
    """
    st = rec.get("state")
    detail = rec.get("detail") or ""
    if zrun_rc == 0 and st == "succeeded":
        return "ok"
    if rec.get("timed_out") or zrun_rc == 124 or st == "timed_out":
        return "timed_out"
    if n1302 or RATE1302_RE.search(detail):
        return "rate_limited"
    if st == "quota_exhausted":
        # no 1302 evidence: a real credit refusal only if it says so
        return "quota_exhausted" if QUOTA_RE.search(detail) else "rate_limited"
    return "failed"


def rate_limited_start(run_id, rec, zrun_rc):
    """True only when the plan refused and the run produced no answer."""
    if zrun_rc == 0 and rec.get("state") == "succeeded":
        return False
    # A 900 s timeout is a fail and is never resumed (arm brief). Without this the
    # heuristic fires on any timed-out run whose log happens to mention a 1302 and
    # buys the task a second attempt it is not entitled to.
    if rec.get("timed_out") or zrun_rc == 124 or rec.get("state") == "timed_out":
        return False
    if not run_id:
        return False
    p = os.path.join(RUNS, run_id, "harness.log")
    if not os.path.exists(p):
        return False
    with open(p, encoding="utf-8", errors="replace") as fh:
        head = fh.read(200000)
    return bool(RATE_RE.search(head))


def run_one(band, task, attempt=1, prev=None):
    suite = BANDS[band]
    sb = os.path.join(band_dir(band), task)
    prompt = os.path.join(suite, task, "prompt.md")
    bd = band_dir(band)
    outp = os.path.join(bd, "%s.stdout.txt" % task)
    logp = os.path.join(bd, "%s.zrun.log" % task)
    cmd = ["bash", ZRUN, "--cwd", sb, "--model", MODEL, "--effort", EFFORT,
           "--timeout", str(TIMEOUT), "--idle", str(IDLE)]
    # The gate is checked AFTER acquire, immediately before the subprocess starts.
    # Checking it before acquire evaluates it at thread start, so with a pool of 1
    # every queued task inherits one stale reading taken minutes or hours earlier and
    # the gate never fires again. That is exactly what happened on the large band.
    pool_at_launch = acquire()
    if not quota_gate_open():
        release()
        with lock:
            state["gated"].append(task)
        print("[gated] %s/%s not launched: 5h window at or above %.0f%%"
              % (band, task, QUOTA_STOP_PCT), flush=True)
        return {"skipped": "quota_gate", "outcome": "not_run", "attempt": attempt}
    try:
        t0 = time.time()
        with open(prompt, "rb") as fin, open(outp, "wb") as fout, \
                open(logp, "wb") as ferr:
            p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=ferr)
        wall = time.time() - t0
    finally:
        release()

    log = open(logp, encoding="utf-8", errors="replace").read(4000)
    m = RUNID_RE.search(log)
    run_id = m.group(1) if m else None
    rec = read_run_state(run_id)
    n1302 = count_1302(run_id)
    rec.update({"wall_s": round(wall, 1), "run_id": run_id, "zrun_rc": p.returncode,
                "timed_out": p.returncode == 124 or rec.get("state") == "timed_out",
                "attempt": attempt, "rate_1302": n1302,
                "conc_at_launch": pool_at_launch})
    rec["outcome"] = classify(rec, p.returncode, n1302)
    if prev:
        # a retried task's first attempt is still evidence of how hard the plan
        # throttled it; keep it rather than let the retry hide it
        rec["attempt1"] = prev

    # copy the run's durable answer next to the band results
    if run_id:
        for name, dest in (("final.txt", "%s.final.txt" % task),
                           ("result.json", "%s.result.json" % task)):
            src = os.path.join(RUNS, run_id, name)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(bd, dest))

    if rate_limited_start(run_id, rec, p.returncode) and attempt == 1:
        with lock:
            state["rate_events"].append({"band": band, "task": task,
                                         "at": time.strftime("%H:%M:%S"),
                                         "run_id": run_id})
            state["max_conc"] = 2
        print("[rate-limit] %s/%s: waiting 60 s, concurrency -> 2" % (band, task),
              flush=True)
        time.sleep(60)
        with cond:
            cond.notify_all()
        return run_one(band, task, attempt=2,
                       prev={"run_id": run_id, "rate_1302": n1302,
                             "state": rec.get("state"),
                             "wall_s": rec.get("wall_s"),
                             "outcome": rec.get("outcome"),
                             "conc_at_launch": pool_at_launch})

    print("[run] %s/%s rc=%s outcome=%s wall=%.0fs in=%s out=%s reqs=%s 1302=%s"
          % (band, task, p.returncode, rec["outcome"], wall, rec.get("in_tokens"),
             rec.get("out_tokens"), rec.get("model_requests"), n1302), flush=True)
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
                    "score": "%s/%s" % (sc[-1][0], sc[-1][1]) if sc else None,
                    "verdict": vd[-1] if vd else None, "rc": rc,
                    "tail": so.strip()[-160:]})
        out[t] = rec
        print("%-5s %-4s score=%s verdict=%s outcome=%s 1302=%s"
              % (t, "PASS" if rec["pass"] else "FAIL", rec["score"], rec["verdict"],
                 rec.get("outcome"), rec.get("rate_1302")), flush=True)
    # A plan refusal is not the model failing the task, so neither a 1302 throttle
    # nor a real 402/quota stop nor an ungraded task counts in the denominator.
    EXCLUDE = ("rate_limited", "quota_exhausted", "not_run")
    rl = [t for t in TASKS if out.get(t, {}).get("outcome") in EXCLUDE]
    graded = [t for t in TASKS if out.get(t, {}).get("outcome") not in EXCLUDE]
    n = sum(1 for t in graded if out.get(t, {}).get("pass"))
    tot1302 = sum(out.get(t, {}).get("rate_1302") or 0 for t in TASKS)
    out["_meta"] = {"band": band, "harness": "zcode", "model": MODEL,
                    "effort": EFFORT, "timeout_s": TIMEOUT, "idle_s": IDLE,
                    "rate_limit_events": state["rate_events"],
                    "final_max_concurrency": state["max_conc"],
                    "concurrency_history": state["conc_history"],
                    "excluded_tasks": rl,
                    "total_1302_retries": tot1302,
                    "scored_denominator": len(graded),
                    "quota_readings": state["quota_readings"],
                    "quota_gated_tasks": state["gated"],
                    "quota_reset": state["quota_reset"]}
    p = os.path.join(band_dir(band), "results.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("\n%s: %d/%d passed (rate_limited excluded: %s), 1302 retries total %d -> %s"
          % (band, n, len(graded), rl or "none", tot1302, p), flush=True)


def main():
    band = sys.argv[1]
    resume = "--resume" in sys.argv[2:]
    if band not in BANDS:
        print("usage: run_zcode_gate.py {tiny|large} [--resume]")
        sys.exit(2)
    if not os.environ.get("ZAI_API_KEY"):
        print("ZAI_API_KEY absent")
        sys.exit(3)

    results, todo = {}, list(TASKS)
    if resume:
        todo = []
        for t in TASKS:
            r = reconstruct(band, t)
            if r:
                results[t] = r
                print("[resume] %s/%s already terminal (%s, run %s), kept"
                      % (band, t, r.get("outcome"),
                         (r.get("run_id") or "")[-12:]), flush=True)
            else:
                todo.append(t)
        print("[resume] %s: %d kept, %d to run: %s"
              % (band, len(results), len(todo), " ".join(todo) or "none"), flush=True)
    if todo:
        prep(band, todo)
    threads = []

    def worker(t):
        try:
            results[t] = run_one(band, t)
        except Exception as e:
            results[t] = {"driver_error": "%s: %s" % (type(e).__name__, str(e)[:200])}

    t_start = time.time()
    for t in todo:
        th = threading.Thread(target=worker, args=(t,))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
    print("[run] %s band pass complete in %.0fs" % (band, time.time() - t_start),
          flush=True)
    if state["gated"]:
        print("[quota] PAUSED: %d task(s) not launched (%s). Window resets %s; "
              "resume with: run_band.sh %s --resume"
              % (len(state["gated"]), " ".join(state["gated"]),
                 state["quota_reset"], band), flush=True)
    grade(band, results)


if __name__ == "__main__":
    main()
