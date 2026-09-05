#!/usr/bin/env python3
"""The ZCode reference arm — READY TO RUN, NOT RUN. This one is the control session's.

    python3 run_zcode_arm.py [--trial 0] [--concurrency 4] [--timeout 1800]

WHY IT IS NOT RUN HERE. The manager brief for this campaign says `z-run` is not to be used
tonight, and the org map says a ZCode run happens only when the control session says the
runtime is live. So this driver exists, is written against the same prep/grade halves as every
other arm, and is deliberately left unexecuted. Nothing about it is a placeholder except the
running of it.

WHAT IT MEASURES, AND WHY IT IS WORTH RUNNING AT ALL. The `glm` arm and this arm are the *same
model* — GLM 5.3 Flash on the same Z.ai plan — reached through two different harnesses. Any
difference between the two rows is therefore a harness effect and not a model effect, which is
the one comparison neither arm can make alone. Two known differences to expect and to read
against:

  * pi runs under `pi-resilience.ts`, which middle-truncates any single tool output above
    24,000 characters and retries a provider-error turn. ZCode does not. Failure mode 9 is
    the task family where that should show, if it shows anywhere.
  * plan metering differs: the pi route is metered in plan credits (2.3x input, 8x output),
    ZCode's Flash campaign is not. Check the 5-hour window before and after.

BEFORE RUNNING
  1. Confirm with the control session that z-run is live.
  2. Check the Z.ai 5-hour window; pause above 80%.
  3. `python3 assemble_suite.py --check-only` must pass, so the suite has not drifted since
     the other arms ran. An arm measured against a different suite is not a comparison.
"""
import argparse
import json
import os
import subprocess
import threading
import time

import sanity

WRAPPER = os.path.expanduser("~/.claude/skills/z-run/scripts/z-run")
ARM = "zcode"

_slots = None


def run_one(task, trial, timeout):
    sb = os.path.join(sanity.trial_dir(ARM, trial), task)
    prompt = open(os.path.join(sanity.SUITE, task, "prompt.md"), encoding="utf-8").read()
    logp = os.path.join(sanity.trial_dir(ARM, trial), "%s.z.log" % task)
    finalp = os.path.join(sanity.trial_dir(ARM, trial), "%s.final.txt" % task)
    cmd = ["bash", WRAPPER, "--cwd", sb, "--timeout", str(timeout), "--", prompt]
    with _slots:
        t0 = time.time()
        with open(finalp, "wb") as fout, open(logp, "wb") as ferr:
            p = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=fout, stderr=ferr)
        wall = time.time() - t0
    print("[run] %-20s rc=%s wall=%.0fs" % (task, p.returncode, wall), flush=True)
    return {"wall_s": round(wall, 1), "z_rc": p.returncode, "timed_out": p.returncode == 124}


def main():
    global _slots
    ap = argparse.ArgumentParser()
    ap.add_argument("--trial", default="0")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=1800)
    a = ap.parse_args()
    if not os.path.exists(WRAPPER):
        raise SystemExit("z-run wrapper not found at %s; is the skill deployed on this host?"
                         % WRAPPER)
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
    print("\nRead it against the `glm` arm with:  python3 sanity.py tally glm zcode")


if __name__ == "__main__":
    main()
