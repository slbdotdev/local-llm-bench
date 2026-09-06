#!/usr/bin/env python3
"""The Luna reference arm: GPT-5.6 Luna through native `codex exec`, one trial over the suite.

    python3 run_codex_arm.py [--trial 0] [--concurrency 6] [--timeout 1800]

Same shape as v5's `results/v5/authoring/gate-luna/run_luna_gate.py`, which is the invocation
this fleet has already measured, with three changes for v7: the suite is `authoring/suite/`,
prep and grade come from `sanity.py` so every arm's numbers mean the same thing, and the
per-task record carries the verdict column as well as the pass flag.

It calls the `codex` binary directly rather than `codex-run`, deliberately: this is a reference
*arm* being measured, not a delegated task, so it must not carry the worker instruction set or
a repository AGENTS.md chain into the model's context. `project_doc_max_bytes=0` is what
enforces that.
"""
import argparse
import json
import os
import subprocess
import threading
import time

import sanity

HERE = os.path.dirname(os.path.abspath(__file__))
ARM = "luna"

_lock = threading.Lock()
_slots = None


def run_one(task, trial, timeout):
    sb = os.path.join(sanity.sandbox_dir(ARM, trial), task)
    prompt = os.path.join(sanity.SUITE, task, "prompt.md")
    finalp = os.path.join(sanity.trial_dir(ARM, trial), "%s.final.txt" % task)
    logp = os.path.join(sanity.trial_dir(ARM, trial), "%s.codex.log" % task)
    cmd = ["timeout", str(timeout), "codex", "exec", "--skip-git-repo-check",
           "-C", sb, "-m", "gpt-5.6-luna", "-c", "model_reasoning_effort=high",
           "-c", "project_doc_max_bytes=0", "--color", "never", "-o", finalp, "-"]
    with _slots:
        t0 = time.time()
        with open(prompt, "rb") as fin, open(logp, "wb") as fout:
            p = subprocess.run(cmd, stdin=fin, stdout=fout, stderr=subprocess.STDOUT)
        wall = time.time() - t0
    print("[run] %-20s rc=%s wall=%.0fs" % (task, p.returncode, wall), flush=True)
    return {"wall_s": round(wall, 1), "codex_rc": p.returncode,
            "timed_out": p.returncode == 124}


def main():
    global _slots
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial", default="0")
    ap.add_argument("--concurrency", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=1800)
    a = ap.parse_args()
    _slots = threading.Semaphore(a.concurrency)

    sanity.prep(ARM, a.trial)
    meta = {}
    threads = []
    t0 = time.time()
    for task in sanity.tasks():
        th = threading.Thread(target=lambda t=task: meta.__setitem__(
            t, run_one(t, a.trial, a.timeout)))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
    print("[run] arm complete in %.0fs" % (time.time() - t0), flush=True)

    out = sanity.grade(ARM, a.trial)
    for task, rec in out.items():
        rec.update(meta.get(task, {}))
    path = os.path.join(sanity.trial_dir(ARM, a.trial), "results.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
