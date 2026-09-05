#!/usr/bin/env python3
"""The ZCode reference arm — GLM 5.3 Flash through ZCode's own supervised runtime.

**NOT RUN FOR v7, BY THE OWNER'S INSTRUCTION.** The instruction was withdrawn and then reinstated
during the night; the standing position at the end of the campaign is that the ZCode row is not
run for this campaign, and the sanity table says so rather than leaving a gap. Nothing about this
driver is a placeholder except the running of it: it is written against the same prep and grade
halves as every other arm, so the row it would produce is comparable with the four that exist.

The window conditions that shaped it are worth keeping, because they will be the same next time:
the Z.ai five-hour window stood at 98-99% for the last two hours of this campaign and was due to
reset at 2026-09-05T08:50:42Z. Every launch is gated on `plan-usage.py` for that reason.

    python3 run_zcode_arm.py [--trial 0] [--timeout 900] [--idle 5]
                             [--stage /mnt/d/bench-zcode] [--gate 85] [--only m01-main-claude]

**One run at a time, never more.** The Z.ai plan rate-limits concurrent requests with error
`1302`, and the ZCode runtime answers a 1302 by retrying up to eleven times with about a minute
of backoff — so concurrency does not fail fast, it turns into a slow run that looks like a slow
model. Serial is the only honest setting, and it is the owner's instruction.

**Sandboxes live on D:, not in WSL.** ZCode is Windows-only on this fleet; a WSL invocation
drives the Windows runtime through interop, so `--cwd` has to be a path Windows can see. The
sandboxes are staged under `--stage` (default `/mnt/d/bench-zcode/trial-<n>/<slot>`) and graded
there in place. Only `results.json` comes back into the repository.

**The plan window gates every launch.** `plan-usage.py` is read before each run and the arm
stops rather than launching at or above `--gate` percent of the five-hour window. A run that
ends `failed` with `1302` in its detail is **rate limited, not a miss**: it is recorded as
`rate_limited` and excluded from the denominator, the same treatment a real `quota_exhausted`
(402 / balance) gets. A row that is excluded is not a zero; it is an absence, and the handoff
says how many rows the window carried.

WHAT IT MEASURES, AND WHY IT IS WORTH RUNNING AT ALL. The `glm` arm and this arm are the *same
model* on the same plan, reached through two different harnesses. Any difference between the two
rows is a harness effect, not a model effect, and that is the one comparison neither arm can make
alone. Two known differences to read against:

  * pi runs under `pi-resilience.ts`, which middle-truncates any single tool output above 24,000
    characters and retries a provider-error turn; ZCode does not. Failure mode 9 is where that
    should show if it shows anywhere.
  * the answer is read from the run's `final.txt`, never from the wrapper's stdout tail.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

import sanity

WRAPPER = os.path.expanduser("~/.claude/skills/z-run/scripts/z-run")
PLAN_USAGE = os.path.expanduser("~/ansible-slb/scripts/plan-usage.py")
RUNS = os.path.expanduser("~/.agent-runs")
ARM = "zcode"
RUNID_RE = re.compile(r"\b(wr-[A-Za-z0-9]+-\d{8}T\d{6}Z-[0-9a-f]+)\b")


def window():
    """(used_percent, resets_at) for the Z.ai five-hour window, or (None, None)."""
    try:
        r = subprocess.run([sys.executable, PLAN_USAGE, "--json"],
                           capture_output=True, text=True, timeout=120)
        for src in json.loads(r.stdout).get("sources", []):
            if src.get("source", "").startswith("Z.ai"):
                fh = src.get("details", {}).get("five_hour", {}) or {}
                return fh.get("used_percent"), fh.get("resets_at")
    except Exception as exc:
        print("[gate] could not read the plan window: %s" % exc, flush=True)
    return None, None


def stage(stage_root, trial):
    """Copy every task's seed to a Windows-visible sandbox; return {task: path}."""
    root = os.path.join(stage_root, "trial-%s" % trial)
    out = {}
    for t in sanity.tasks():
        sb = os.path.join(root, t)
        if os.path.exists(sb):
            shutil.rmtree(sb)
        os.makedirs(sb)
        seed = os.path.join(sanity.SUITE, t, "seed")
        if os.path.isdir(seed):
            shutil.copytree(seed, sb, dirs_exist_ok=True)
        out[t] = sb
    print("[stage] %d sandboxes under %s" % (len(out), root), flush=True)
    return out


def outcome(runid):
    """The run's terminal state and detail, from result.json — never from stdout."""
    if not runid:
        return {"state": "unknown", "detail": ""}
    p = os.path.join(RUNS, runid, "result.json")
    try:
        d = json.load(open(p, encoding="utf-8"))
        return {"state": d.get("state", "unknown"), "detail": str(d.get("detail", ""))[:400]}
    except Exception:
        return {"state": "unknown", "detail": ""}


def final_text(runid):
    p = os.path.join(RUNS, runid or "", "final.txt")
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return ""


def run_one(task, sb, trial, timeout, idle):
    tdir = sanity.trial_dir(ARM, trial)
    os.makedirs(tdir, exist_ok=True)
    prompt = open(os.path.join(sanity.SUITE, task, "prompt.md"), encoding="utf-8").read()
    logp = os.path.join(tdir, "%s.z.log" % task)
    cmd = ["bash", WRAPPER, "--cwd", sb, "--timeout", str(timeout), "--idle", str(idle),
           "--", prompt]
    t0 = time.time()
    with open(logp, "wb") as ferr:
        p = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=ferr)
    wall = time.time() - t0
    err = open(logp, encoding="utf-8", errors="replace").read()
    m = RUNID_RE.search(err)
    runid = m.group(1) if m else None
    oc = outcome(runid)
    answer = final_text(runid)
    if answer:
        with open(os.path.join(tdir, "%s.final.txt" % task), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(answer)
    limited = ("1302" in oc["detail"] or "1302" in err[-4000:]) and oc["state"] != "succeeded"
    exhausted = oc["state"] == "quota_exhausted"
    rec = {"wall_s": round(wall, 1), "z_rc": p.returncode, "run_id": runid,
           "run_state": oc["state"], "timed_out": p.returncode == 124,
           "rate_limited": bool(limited), "quota_exhausted": bool(exhausted),
           "answer_chars": len(answer)}
    print("[run] %-20s rc=%-4s state=%-16s wall=%-6.0fs answer=%d%s"
          % (task, p.returncode, oc["state"], wall, len(answer),
             "  RATE LIMITED (excluded)" if limited else
             "  QUOTA EXHAUSTED (excluded)" if exhausted else ""), flush=True)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial", default="0")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--idle", type=int, default=5)
    ap.add_argument("--stage", default="/mnt/d/bench-zcode")
    ap.add_argument("--gate", type=float, default=85.0)
    ap.add_argument("--only", action="append")
    a = ap.parse_args()

    if not os.path.exists(WRAPPER):
        raise SystemExit("z-run wrapper not found at %s" % WRAPPER)

    used, resets = window()
    print("[gate] Z.ai five-hour window %s%%, resets %s" % (used, resets), flush=True)
    if used is not None and used >= a.gate:
        raise SystemExit("[gate] window at %s%% is at or above the %.0f%% gate; not launching"
                         % (used, a.gate))

    tasks = [t for t in sanity.tasks() if not a.only or t in a.only]
    sandboxes = stage(a.stage, a.trial)

    meta = {}
    t0 = time.time()
    for task in tasks:
        used, resets = window()
        if used is not None and used >= a.gate:
            print("[gate] window reached %s%% (resets %s); stopping after %d of %d"
                  % (used, resets, len(meta), len(tasks)), flush=True)
            break
        meta[task] = run_one(task, sandboxes[task], a.trial, a.timeout, a.idle)
    print("[run] arm ran %d of %d task(s) in %.0fs" % (len(meta), len(tasks), time.time() - t0),
          flush=True)

    out = {}
    for task in tasks:
        if task not in meta:
            out[task] = {"error": "not run: the plan window did not carry it",
                         "pass": False, "verdict": None, "excluded": True}
            continue
        rec = sanity.grade_one(task, sandboxes[task])
        rec.update(meta[task])
        # A rate-limited or quota-exhausted run never produced an answer to grade, so its row
        # is an absence rather than a failure and is out of the denominator entirely.
        rec["excluded"] = bool(rec.get("rate_limited") or rec.get("quota_exhausted"))
        if rec["excluded"]:
            rec["verdict"] = None
        out[task] = rec
        print("%-20s %-4s score=%-8s verdict=%s%s"
              % (task, "PASS" if rec.get("pass") else "FAIL", rec.get("score"),
                 rec.get("verdict"), "  EXCLUDED" if rec["excluded"] else ""), flush=True)

    path = os.path.join(sanity.trial_dir(ARM, a.trial), "results.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    scored = [r for r in out.values() if not r.get("excluded")]
    n = sum(1 for r in scored if r.get("pass"))
    print("\nzcode trial %s: %d/%d correct (%d row(s) excluded) -> %s"
          % (a.trial, n, len(scored), len(out) - len(scored), path))
    print("Read it against the `glm` arm with:  python3 sanity.py tally glm zcode")


if __name__ == "__main__":
    sys.exit(main())
