#!/usr/bin/env python3
"""refprobe - grade every item 1 reference answer through its own test.py.

    python3 refprobe.py                 # all six slots
    python3 refprobe.py --task t2-apply-patch-bytes
    python3 refprobe.py --json out.json  # also write a machine-readable result
    python3 refprobe.py -v               # print each grader's full stdout

This is v7's D7-31 check, narrowed to what it actually asks: **the grader is
verified on the interpreter that will run it.** Phase 2 runs from WSL against
the desktop clone with the Windows interpreter, so this is the probe the
desktop-side preflight runs, under

    /mnt/c/Users/slb/scoop/apps/python/current/python.exe refprobe.py

WHAT IT DOES, AND DELIBERATELY DOES NOT DO
------------------------------------------
For each task slot it copies `seed/` to a fresh temporary sandbox, runs
`ref/solve.py` there with the sandbox as the working directory, removes it, and
runs that slot's own hidden `test.py` with the sandbox as the working directory.
It expects `SCORE n/n`, `PASS`, `VERDICT correct` and exit 0.

It **rebuilds nothing and regenerates no corpus**. `build_tasks.py` is not
imported or invoked; `make_corpus.py` is not touched; no fixture is written. The
only inputs are the files already in this checkout, so it is safe to run against
a clone whose sole contents are the repository - in particular it assumes
nothing under `/home/slb/` exists, and resolves every path from this file's own
location.

It writes only inside a temporary directory of its own making, which it removes.
Nothing in the repository is modified.

PORTABILITY
-----------
Everything here is `os.path`-based with no POSIX-only call and no shell. The
temporary directory comes from `tempfile`, which on Windows is on `C:` while the
repo may be on `D:`; no path is ever relativised across the two, because
`ntpath.relpath` raises on a cross-drive pair.

EXIT
----
0 when every probed slot graded `correct`; 1 otherwise, naming the slots that
did not. A slot whose `ref/solve.py` fails to run is a failure, not a skip.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TASKS_DIR = os.path.join(HERE, "tasks")

TASK_NAMES = [
    "t1-locate-report",
    "t2-apply-patch-bytes",
    "t3-command-output",
    "t4-long-job-poll",
    "t5-error-recovery",
    "t6-multifile-consistency",
]


def probe(task, verbose=False):
    """Returns a result dict for one slot. Never raises for a task-level fault."""
    slot = os.path.join(TASKS_DIR, task)
    seed = os.path.join(slot, "seed")
    solve = os.path.join(slot, "ref", "solve.py")
    test = os.path.join(slot, "test.py")
    out = {"task": task, "ok": False, "verdict": None, "score": None, "exit": None,
           "solve_exit": None, "note": None}

    for needed in (seed, solve, test):
        if not os.path.exists(needed):
            out["note"] = "missing %s" % needed
            return out

    work = tempfile.mkdtemp(prefix="refprobe-")
    box = os.path.join(work, "sandbox")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        shutil.copytree(seed, box)
        # The reference is run INSIDE the sandbox and then removed, which is
        # v7's convention (plan section 2): ref/ is never part of the material.
        local_solve = os.path.join(box, "solve.py")
        shutil.copy(solve, local_solve)
        try:
            sp = subprocess.run([sys.executable, "solve.py"], cwd=box, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=300)
        except subprocess.TimeoutExpired:
            out["note"] = "ref/solve.py exceeded 300 s"
            return out
        out["solve_exit"] = sp.returncode
        solve_text = sp.stdout.decode("utf-8", "replace")
        os.remove(local_solve)
        if sp.returncode != 0:
            out["note"] = "ref/solve.py exited %d: %s" % (
                sp.returncode, solve_text.strip()[-400:])
            return out

        try:
            tp = subprocess.run([sys.executable, test], cwd=box, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=300)
        except subprocess.TimeoutExpired:
            out["note"] = "test.py exceeded 300 s"
            return out
        text = tp.stdout.decode("utf-8", "replace").replace("\r\n", "\n")
        if verbose:
            print(solve_text + text)
        m = re.search(r"^SCORE (\d+)/(\d+)$", text, re.M)
        v = re.search(r"^VERDICT (\w+)$", text, re.M)
        passed = bool(re.search(r"^PASS$", text, re.M))
        out["exit"] = tp.returncode
        out["score"] = [int(m.group(1)), int(m.group(2))] if m else None
        out["verdict"] = v.group(1) if v else None
        if m is None or v is None:
            out["note"] = "grader printed no SCORE/VERDICT line: %s" % text.strip()[-400:]
            return out
        if "Traceback (most recent call last)" in text:
            out["note"] = "grader traceback"
            return out
        full = out["score"][0] == out["score"][1]
        out["ok"] = bool(out["verdict"] == "correct" and passed and full and tp.returncode == 0)
        if not out["ok"]:
            out["note"] = "expected correct/PASS/full/exit 0"
        return out
    except Exception as exc:  # noqa: BLE001 - a slot-level fault is a failure, not a crash
        out["note"] = "%s: %s" % (type(exc).__name__, exc)
        return out
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--task", default=None, help="probe one slot by name")
    ap.add_argument("--json", default=None, help="write the machine-readable result here")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    tasks = [t for t in TASK_NAMES if not args.task or args.task == t]
    if not tasks:
        ap.error("unknown task %s" % args.task)
    if not os.path.isdir(TASKS_DIR):
        print("FAIL no tasks/ directory beside %s" % os.path.basename(__file__))
        return 1

    print("refprobe - v8 item 1 reference answers, graded by each slot's own test.py")
    print("interpreter  %s" % sys.executable)
    print("version      %s" % sys.version.replace("\n", " "))
    print("platform     %s" % sys.platform)
    print("item1        %s" % HERE)
    print("tempdir      %s" % tempfile.gettempdir())
    print("")

    results = []
    for task in tasks:
        r = probe(task, verbose=args.verbose)
        results.append(r)
        score = "%s/%s" % tuple(r["score"]) if r["score"] else "-/-"
        print("%-26s %s  SCORE %-7s VERDICT %-18s %s" % (
            task, "ok  " if r["ok"] else "FAIL", score, r["verdict"],
            r["note"] or ""))

    bad = [r["task"] for r in results if not r["ok"]]
    import datetime
    payload = {
        "probe": "v8-item1-refprobe",
        "passed": len(results) - len(bad),
        "failed": len(bad),
        "when": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "python": sys.version,
        "platform": sys.platform,
        "executable": sys.executable,
        "complete": not args.task,
        "ok": not bad and not args.task,
        "tasks": tasks,
        "results": results,
    }
    if args.json:
        d = os.path.dirname(os.path.abspath(args.json))
        if d:
            os.makedirs(d, exist_ok=True)
        with open(args.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    print("")
    print("%d/%d reference answers graded correct" % (payload["passed"], len(results)))
    if bad:
        print("REFPROBE FAILED: " + ", ".join(bad))
        return 1
    print("REFPROBE OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
