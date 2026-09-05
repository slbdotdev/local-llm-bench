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

    # the prompt fixes the header and the ordering; check the artifact against the prompt.
    with open(os.path.join(sb, "report", "limits.csv"), "rb") as fh:
        raw = fh.read()
    if b"\r\n" in raw:
        problems.append("prompt example: the CSV must use LF line endings")
    lines = raw.decode("utf-8").split("\n")
    if lines[0] != "stage,limit,window_s":
        problems.append("prompt example: header is %r" % lines[0])
    rows = [ln for ln in lines[1:] if ln]
    keys = [(-int(r.split(",")[1]), r.split(",")[0]) for r in rows]
    if keys != sorted(keys):
        problems.append("prompt example: rows are not sorted by limit desc then name asc")

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
