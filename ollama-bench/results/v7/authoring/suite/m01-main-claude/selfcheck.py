#!/usr/bin/env python3
"""Execute this task's prompt examples against ref/, and confirm the reference is correct.

    python3 selfcheck.py

Required by AUTHORING-BRIEF.md section 3. It is deliberately NOT the same instrument as
test.py: the grader asks "is this answer right", and this asks "does the reference actually
satisfy every example the prompt shows a reader". A prompt whose worked example disagrees with
its own reference is the defect this catches, and it has occurred in this benchmark before.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def build():
    sb = tempfile.mkdtemp(prefix="selfcheck-")
    shutil.copytree(os.path.join(HERE, "seed"), sb, dirs_exist_ok=True)
    ref = os.path.join(HERE, "ref")
    if os.path.isdir(ref):
        shutil.copytree(ref, sb, dirs_exist_ok=True)
    solve = os.path.join(sb, "solve.py")
    if os.path.exists(solve):
        subprocess.run([sys.executable, "solve.py"], cwd=sb, check=True,
                       env=dict(os.environ, PYTHONUTF8="1"), capture_output=True)
        os.remove(solve)
    return sb


def grade(sb):
    shutil.copy(os.path.join(HERE, "test.py"), os.path.join(sb, "_hidden_test.py"))
    p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sb,
                       env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.stdout, p.returncode


def main():
    sb = build()
    out, rc = grade(sb)
    problems = []
    if "PASS" not in out or rc != 0:
        problems.append("the reference does not pass its own grader: %r" % out.strip()[-200:])
    if "VERDICT correct" not in out:
        problems.append("the reference is not graded `correct`")
    m = re.search(r"SCORE (\d+)/(\d+)", out)
    if not m or m.group(1) != m.group(2):
        problems.append("the reference does not score full marks: %s" % (m.group(0) if m else "no SCORE"))

    # the prompt states: "A key in `ages` that the stage has never seen is ignored" and
    # "calling `reap` twice with the same argument reaps nothing the second time".
    import importlib
    import json as _json
    sys.path.insert(0, os.path.join(sb, "src"))
    man = _json.load(open(os.path.join(sb, "config", "manifest.json"), encoding="utf-8"))
    st = man["stages"][0]
    mod = importlib.import_module(man["package"] + "." + st["module"])
    eng = getattr(mod, st["class"])()
    if eng.reap({"never-seen": 10 ** 6}) != 0:
        problems.append("prompt example: an unknown key must be ignored, and is not")

    shutil.rmtree(sb, ignore_errors=True)
    if problems:
        print("SELFCHECK FAILED")
        for p in problems:
            print("  - " + p)
        return 1
    print("selfcheck ok: reference scores %s, VERDICT correct, and every prompt example holds"
          % m.group(0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
