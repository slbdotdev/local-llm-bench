#!/usr/bin/env python3
"""Grade a candidate's own reference solution the way pibench does, under whichever
interpreter runs this file.

    python3   results/v7/probe_scope_gate.py m05-main-luna     # WSL / Linux python
    "$PY"     results/v7/probe_scope_gate.py m05-main-luna     # the Windows interpreter

The point is the comparison between those two lines. Every check in this campaign —
`probe_candidate.py`, `probe_idempotence.py`, `validate_all.py`, `sanity.py` — has run the
graders under Linux python3, while **pibench runs them under the Windows interpreter**, because
that is where the daemon and the pi harness live. A grader that behaves differently on the two
is clean under every instrument the campaign owns and broken on every scored row.

The sandbox is built outside every git checkout (D7-18) and removed afterwards.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SUITE = os.environ.get("V7_PROBE_BASE") or os.path.join(HERE, "authoring", "suite")


def build(slot, sandbox):
    cand = os.path.join(SUITE, slot)
    shutil.copytree(os.path.join(cand, "seed"), sandbox, dirs_exist_ok=True)
    ref = os.path.join(cand, "ref")
    solve = os.path.join(ref, "solve.py")
    if os.path.isfile(solve):
        shutil.copy(solve, os.path.join(sandbox, "solve.py"))
        subprocess.run([sys.executable, "solve.py"], cwd=sandbox, check=False,
                       env=dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1"))
        os.remove(os.path.join(sandbox, "solve.py"))
    else:
        for base, dirs, names in os.walk(ref):
            rel = os.path.relpath(base, ref)
            for n in names:
                dest = os.path.join(sandbox, rel, n) if rel != "." else os.path.join(sandbox, n)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(os.path.join(base, n), dest)
    shutil.copy(os.path.join(cand, "test.py"), os.path.join(sandbox, "_hidden_test.py"))


def main():
    # --breach adds one stray file to the reference sandbox before grading, so the same probe
    # proves the gate still has teeth after the normcase repair. A gate that stops firing is
    # as wrong as one that always fires, and only the first is comfortable to discover.
    args = [a for a in sys.argv[1:] if a != "--breach"]
    breach = "--breach" in sys.argv
    print("interpreter: %s  (os.name=%s, sep=%r)%s"
          % (sys.executable, os.name, os.sep, "  [breach probe]" if breach else ""))
    for slot in args:
        sandbox = tempfile.mkdtemp(prefix="scopeprobe_")
        try:
            build(slot, sandbox)
            if breach:
                with open(os.path.join(sandbox, "scratch_notes.txt"), "w",
                          encoding="utf-8") as fh:
                    fh.write("a file the prompt did not ask for\n")
            p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sandbox,
                               capture_output=True, text=True, timeout=120,
                               env=dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8"))
            out = (p.stdout or "") + (p.stderr or "")
            print("%-18s rc=%d | %s" % (slot, p.returncode,
                                        " / ".join(l for l in out.splitlines() if l.strip())[:300]))
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)


if __name__ == "__main__":
    main()
