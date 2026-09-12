#!/usr/bin/env python3
"""Grade every v8 item-2 slot's reference answer through that slot's own grader.

    python3 refprobe.py                 # every slot
    python3 refprobe.py agg-80k-abst    # named slots only
    python3 refprobe.py --json          # machine-readable, to stdout

Exit 0 only when all twelve references grade `correct` at full score with exit 0.

This is the cheapest check item 2 has and the only one the phase-2 preflight needs to run on
the desktop side. What it deliberately does **not** do:

  * it rebuilds nothing and regenerates no corpus -- the only inputs are the files already
    in the checkout, so it is safe against a clone that has just been pulled and cannot
    re-derive anything;
  * it writes nothing anywhere except a throwaway directory from the system temp space,
    which it removes again. No tracked file is opened for writing, at any point, on any
    path. Item 1's gate run cleared 89 tracked report files when it crashed midway and
    item 3's wiped a slot it could not then rebuild; this cannot, because it never holds a
    writable handle on anything inside the repository.

It imports nothing from this directory -- standard library only -- so it still runs when a
generator or `common.py` is mid-edit or broken.

Portability. v7's D7-31 rule is that a grader is verified on the interpreter that will run
it, and phase 2 runs the graders under the Windows Python at
`C:\\Users\\slb\\scoop\\apps\\python\\current\\python.exe` against the clone on `D:`. So:
`sys.executable` runs the graders, paths come from `__file__` and `os.path.join` only,
nothing is absolute, the grader environment carries `PYTHONUTF8=1` and
`PYTHONIOENCODING=utf-8` exactly as pibench sets them, and the temp tree may be on a
different drive from the repository.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SLOTS = os.path.join(HERE, "slots")


def grade_reference(slot_dir):
    """Copy seed/ to a scratch tree, drop ref/answer.json in as the deliverable, and run
    the slot's own test.py over it exactly as pibench does: hidden grader copied in last,
    scratch tree as the working directory, 60-second limit, UTF-8 forced."""
    required = [os.path.join(slot_dir, "seed"),
                os.path.join(slot_dir, "ref", "answer.json"),
                os.path.join(slot_dir, "test.py")]
    missing = [p for p in required if not os.path.exists(p)]
    if missing:
        return {"ok": False, "verdict": None, "score": None, "rc": None,
                "error": "missing: " + ", ".join(os.path.relpath(p, slot_dir)
                                                 for p in missing)}
    box = tempfile.mkdtemp(prefix="v8i2ref_")
    try:
        shutil.copytree(os.path.join(slot_dir, "seed"), box, dirs_exist_ok=True)
        shutil.copy(os.path.join(slot_dir, "ref", "answer.json"),
                    os.path.join(box, "answer.json"))
        shutil.copy(os.path.join(slot_dir, "test.py"),
                    os.path.join(box, "_hidden_test.py"))
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
                   PYTHONDONTWRITEBYTECODE="1")
        try:
            p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=box, env=env,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=120)
        except subprocess.TimeoutExpired:
            return {"ok": False, "verdict": None, "score": None, "rc": None,
                    "error": "grader timed out"}
        res = {"rc": p.returncode, "verdict": None, "score": None, "itemcode": None,
               "error": None}
        for line in p.stdout.splitlines():
            if line.startswith("VERDICT "):
                res["verdict"] = line.split(None, 1)[1].strip()
            elif line.startswith("SCORE "):
                res["score"] = line.split(None, 1)[1].strip()
            elif line.startswith("ITEMCODE "):
                res["itemcode"] = line.split(None, 1)[1].strip()
        full = False
        if res["score"] and "/" in res["score"]:
            got, want = res["score"].split("/", 1)
            full = got.strip() == want.strip()
        res["ok"] = (res["rc"] == 0 and res["verdict"] == "correct"
                     and "PASS" in p.stdout and full)
        if not res["ok"]:
            tail = (p.stdout + p.stderr).strip().splitlines()[-4:]
            res["error"] = " | ".join(tail)[:400]
        return res
    finally:
        shutil.rmtree(box, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slots", nargs="*", help="slot names; default every slot")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    if not os.path.isdir(SLOTS):
        print("no slots directory at %s" % SLOTS, file=sys.stderr)
        return 2
    names = a.slots or sorted(d for d in os.listdir(SLOTS)
                              if os.path.isdir(os.path.join(SLOTS, d)))
    if not names:
        print("no slots found under %s" % SLOTS, file=sys.stderr)
        return 2

    rows = []
    for name in names:
        res = grade_reference(os.path.join(SLOTS, name))
        res["slot"] = name
        rows.append(res)
        if not a.as_json:
            print("%-18s %-10s %-8s exit %-4s %s"
                  % (name, res.get("verdict") or "-", res.get("score") or "-",
                     "-" if res.get("rc") is None else res["rc"],
                     "ok" if res["ok"] else "FAIL: " + (res.get("error") or "")))

    bad = [r["slot"] for r in rows if not r["ok"]]
    if a.as_json:
        print(json.dumps({"item": 2, "check": "reference answers",
                          "passed": len(rows) - len(bad), "failed": len(bad),
                          "failed_slots": bad, "python": sys.version,
                          "platform": sys.platform, "rows": rows},
                         indent=1, sort_keys=True))
    else:
        print("\n%d of %d references graded correct at full score on %s"
              % (len(rows) - len(bad), len(rows), sys.platform))
        if bad:
            print("FAILING SLOTS: %s" % ", ".join(bad))
        else:
            print("ALL CLEAR")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
