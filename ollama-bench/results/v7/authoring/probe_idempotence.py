#!/usr/bin/env python3
"""Does grading a candidate twice give the same answer twice?

    python3 probe_idempotence.py [cand-claude/m10-main-claude ...]

With no arguments it checks every candidate under every `cand-*` directory.

Why this exists. A grader is allowed to *run* the solver's work — that is how mode 4 and mode 10
are measured at all, and how `m10`'s "derives it from the manifest" subcheck tells a real program
from a printed table. But a grader that runs the work must put the tree back, and one of the
first fourteen candidates did not: it mutated `config/manifest.json`, ran the solver's generator
against the mutation, restored the manifest and left the *generated file* holding fabricated data.
Graded once, a correct answer scored 9/9 `correct`. Graded again, the same untouched sandbox
scored 8/9 `confidently_wrong`.

Nothing else in the toolchain could see that. `selfcheck.py` runs once. `probe_candidate.py`
builds a fresh sandbox for every perturbation and grades each one once. The near-miss table was
honest and complete and still said "clean", because the defect is not in any single grading — it
is in the *second* one, and a bench that ever re-grades a sandbox (a fairness re-read, a repeat
trial, a re-tally after a grader patch) would have silently converted correct answers into
confidently-wrong ones.

The check: build the reference answer in a sandbox, grade it, grade the identical sandbox again,
and require the score and the verdict to match. Anything else is a grader that eats its evidence.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import probe_candidate as pc  # noqa: E402


def grade(cand, sb):
    """Grade a sandbox in place, exactly as sanity.py does, and leave it as the grader left it."""
    hidden = os.path.join(sb, "_hidden_test.py")
    shutil.copy(os.path.join(cand, "test.py"), hidden)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    try:
        p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sb, env=env,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
        so = p.stdout
    except subprocess.TimeoutExpired:
        so = ""
    finally:
        if os.path.exists(hidden):
            os.remove(hidden)
    score = verdict = None
    for line in so.splitlines():
        if line.startswith("SCORE "):
            score = line[6:].strip()
        elif line.startswith("VERDICT "):
            verdict = line[8:].strip()
    return {"score": score, "verdict": verdict}


def check(cand):
    slot = os.path.basename(cand)
    seed = os.path.join(cand, "seed")
    ref = os.path.join(cand, "ref")
    tmp = tempfile.mkdtemp(prefix="v7-idem-")
    try:
        sb = os.path.join(tmp, "sb")
        shutil.copytree(seed, sb)
        pc.apply_answer(sb, ref)
        first = grade(cand, sb)
        second = grade(cand, sb)
        ok = (first["score"] == second["score"] and first["verdict"] == second["verdict"])
        print("%-22s %-10s %-18s -> %-10s %-18s  %s"
              % (slot, first["score"], first["verdict"],
                 second["score"], second["verdict"],
                 "ok" if ok else "NOT IDEMPOTENT"))
        return ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    args = sys.argv[1:]
    if args:
        cands = [a if os.path.isabs(a) else os.path.join(HERE, a) for a in args]
    else:
        cands = []
        for fam in sorted(d for d in os.listdir(HERE) if d.startswith("cand-")):
            base = os.path.join(HERE, fam)
            for name in sorted(os.listdir(base)):
                if os.path.isdir(os.path.join(base, name, "seed")):
                    cands.append(os.path.join(base, name))
    bad = 0
    for c in cands:
        try:
            if not check(c):
                bad += 1
        except Exception as exc:
            print("%-22s ERROR %s" % (os.path.basename(c), exc))
            bad += 1
    print("\n%d candidate(s), %d not idempotent" % (len(cands), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
