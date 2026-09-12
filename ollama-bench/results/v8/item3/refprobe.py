#!/usr/bin/env python3
"""Grade every slot's reference answer through its own grader, on *this* interpreter.

    python3 refprobe.py                 # all six slots
    python3 refprobe.py --slot a1-summarise-r1
    python3 refprobe.py --json refprobe.json

This is the check the round runner runs on the machine that will actually run the cells, and it
is deliberately the narrowest thing that satisfies v7's D7-31 rule: **verify the grader on the
interpreter that runs it**. It rebuilds nothing, reads nothing outside this repository, imports
nothing from its siblings, and needs only the standard library. It is safe on a machine where
`/home/slb/ansible-slb` — or `/home/slb` at all — does not exist.

It is not `gates.py`. `gates.py` is an authoring-time instrument: it can regenerate slots from
the fleet's own pages, which exist on the WSL side only, and it belongs there. Running the
authoring suite on a clone that has no source material is what deleted a slot on 2026-09-12 and
is the reason this file exists.

What it proves, per slot: the reference answer under `ref/` grades `VERDICT correct` with a full
score and exit 0, under the interpreter running this program, on this platform, with the seed
copied into a fresh sandbox exactly as `pibench.py` would. What it cannot prove is fairness —
that needs a reference arm from another model family, and nothing here substitutes for it.

Exit status is 0 only when every slot's reference passes.
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


def slot_names():
    if not os.path.isdir(SLOTS):
        raise SystemExit("no slots directory at %s" % SLOTS)
    return sorted(d for d in os.listdir(SLOTS)
                  if os.path.isdir(os.path.join(SLOTS, d)) and not d.startswith("."))


def probe(name):
    """Copy the seed and the reference answer into a sandbox and run the slot's own grader."""
    slot = os.path.join(SLOTS, name)
    result = {"slot": name, "ok": False, "verdict": None, "score": None, "metrics": "",
              "qmetrics": "", "error": None}
    manifest_path = os.path.join(slot, "MANIFEST.json")
    test_path = os.path.join(slot, "test.py")
    for required in (manifest_path, test_path, os.path.join(slot, "seed")):
        if not os.path.exists(required):
            result["error"] = "missing %s" % os.path.relpath(required, HERE)
            return result
    with open(manifest_path, "r", encoding="utf-8") as fh:
        deliverable = json.load(fh)["deliverable"]
    ref = os.path.join(slot, "ref", deliverable)
    if not os.path.isfile(ref):
        result["error"] = "missing ref/%s" % deliverable
        return result
    sandbox = tempfile.mkdtemp(prefix="refprobe-")
    try:
        shutil.copytree(os.path.join(slot, "seed"), sandbox, dirs_exist_ok=True)
        shutil.copy(ref, os.path.join(sandbox, *deliverable.split("/")))
        shutil.copy(test_path, os.path.join(sandbox, "_hidden_test.py"))
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
        proc = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sandbox, env=env,
                              capture_output=True, text=True, timeout=180)
        out = (proc.stdout or "") + (proc.stderr or "")
        for line in out.splitlines():
            if line.startswith("VERDICT "):
                result["verdict"] = line.split(None, 1)[1].strip()
            elif line.startswith("SCORE "):
                result["score"] = line.split(None, 1)[1].strip()
            elif line.startswith("METRICS "):
                result["metrics"] = line[len("METRICS "):].strip()
            elif line.startswith("QMETRICS "):
                result["qmetrics"] = line[len("QMETRICS "):].strip()
        if "Traceback" in out:
            result["error"] = "the grader raised: " + out.strip().splitlines()[-1][:160]
        result["rc"] = proc.returncode
        scored = (result["score"] or "").split("/")
        full = len(scored) == 2 and scored[0] == scored[1]
        result["ok"] = (proc.returncode == 0 and result["verdict"] == "correct" and full
                        and not result["error"])
        if not result["ok"] and not result["error"]:
            result["error"] = "rc=%s verdict=%s score=%s" % (proc.returncode, result["verdict"],
                                                             result["score"])
    except subprocess.TimeoutExpired:
        result["error"] = "the grader did not finish inside 180 s"
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", help="probe one slot instead of all of them")
    ap.add_argument("--json", dest="json_path", help="also write the result here as JSON")
    args = ap.parse_args()
    names = [args.slot] if args.slot else slot_names()
    if args.slot and not os.path.isdir(os.path.join(SLOTS, args.slot)):
        raise SystemExit("no such slot: %s" % args.slot)
    print("refprobe: %d slot(s) on %s" % (len(names), sys.executable))
    print("          platform=%s  python=%s" % (sys.platform, sys.version.split()[0]))
    results = [probe(n) for n in names]
    for r in results:
        print("%-4s %-24s verdict=%-18s score=%-6s %s"
              % ("ok" if r["ok"] else "FAIL", r["slot"], r["verdict"], r["score"],
                 r["error"] or r["metrics"]))
        if r["ok"] and r["qmetrics"]:
            print("     %s" % r["qmetrics"])
    failed = [r for r in results if not r["ok"]]
    print("%d/%d references graded correct" % (len(results) - len(failed), len(results)))
    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"passed": len(results) - len(failed), "failed": len(failed),
                       "python": sys.version, "platform": sys.platform,
                       "executable": sys.executable, "slots": results}, fh, indent=1)
        print("wrote %s" % args.json_path)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
