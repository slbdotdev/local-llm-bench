#!/usr/bin/env python3
"""The GLM reference arm: GLM 5.3 Flash through pi on the Z.ai GLM Coding Plan, one trial.

    python3 run_pi_arm.py [--trial 0] [--concurrency 4] [--timeout 1800]

Uses the managed `pi-run` wrapper with no `--model`, which is the plan default and the fleet's
ruling for GLM. Prep and grade come from `sanity.py`, so this arm's numbers are comparable with
the Claude arms and with the Luna arm.

BEFORE RUNNING: check the Z.ai 5-hour window. If it is above 80%, pause GLM work until it
resets. `scripts/plan-usage.py` in ansible-slb reads it, or:

    GET https://api.z.ai/api/monitor/usage/quota/limit   (bearer ZAI_API_KEY, numbers only)

Never print the key.
"""
import argparse
import json
import os
import subprocess
import threading
import time

import sanity

WRAPPER = os.path.expanduser("~/.claude/skills/pi-run/scripts/pi-run")
ARM = "glm"
MODEL_ARGS = []

_slots = None


def run_one(task, trial, timeout):
    sb = os.path.join(sanity.sandbox_dir(ARM, trial), task)
    prompt = open(os.path.join(sanity.SUITE, task, "prompt.md"), encoding="utf-8").read()
    logp = os.path.join(sanity.trial_dir(ARM, trial), "%s.pi.log" % task)
    finalp = os.path.join(sanity.trial_dir(ARM, trial), "%s.final.txt" % task)
    cmd = ["bash", WRAPPER, "--cwd", sb, "--timeout", str(timeout), "--idle", "90",
           "--no-context-files"] + MODEL_ARGS + ["--", prompt]
    with _slots:
        t0 = time.time()
        with open(finalp, "wb") as fout, open(logp, "wb") as ferr:
            p = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=fout, stderr=ferr)
        wall = time.time() - t0
    print("[run] %-20s rc=%s wall=%.0fs" % (task, p.returncode, wall), flush=True)
    return {"wall_s": round(wall, 1), "pi_rc": p.returncode, "timed_out": p.returncode == 124}


def main():
    global _slots, ARM, MODEL_ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial", default="0")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--tasks", nargs="*", help="re-run only these tasks, merging into results.json")
    ap.add_argument("--arm", default=ARM, help="results directory under sanity/ (default glm)")
    ap.add_argument("--model", help="OpenRouter model id passed to pi-run (default: plan GLM)")
    ap.add_argument("--uncapped", action="store_true", help="pass --uncapped to pi-run")
    ap.add_argument("--effort", help="thinking level passed to pi-run (default: managed)")
    a = ap.parse_args()
    ARM = a.arm
    if a.model:
        MODEL_ARGS = ["--model", a.model] + (["--uncapped"] if a.uncapped else [])
    if a.effort:
        MODEL_ARGS = MODEL_ARGS + ["--effort", a.effort]
    _slots = threading.Semaphore(a.concurrency)

    sanity.prep(ARM, a.trial, a.tasks or None)
    meta = {}
    threads = []
    t0 = time.time()
    for task in sanity.tasks():
        if a.tasks and task not in a.tasks:
            continue
        th = threading.Thread(target=lambda t=task: meta.__setitem__(
            t, run_one(t, a.trial, a.timeout)))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
    print("[run] arm complete in %.0fs" % (time.time() - t0), flush=True)

    out = sanity.grade(ARM, a.trial, a.tasks or None)
    for task, rec in out.items():
        rec.update(meta.get(task, {}))
    path = os.path.join(sanity.trial_dir(ARM, a.trial), "results.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
