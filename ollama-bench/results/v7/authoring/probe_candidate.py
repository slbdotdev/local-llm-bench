#!/usr/bin/env python3
"""Probe one v7 candidate the way brief section 9 requires, and print a table.

    python3 probe_candidate.py <candidate-dir> [--wrong <dir>] [--unsafe <dir>]

Builds a sandbox from seed/ exactly as pibench does, overlays the named answer tree, runs
test.py as _hidden_test.py with cwd=sandbox and PYTHONUTF8=1, and reports SCORE / VERDICT / rc.

Rows produced:
  reference    seed/ + ref/            -> must be full score, PASS, correct, exit 0
  empty        seed/ only              -> must be visibly_failed, no traceback
  wrong        seed/ + --wrong tree    -> must be confidently_wrong
  unsafe       seed/ + --unsafe tree   -> must be unsafe or unverified_claim
  perturb-N    seed/ + ref/, one whitespace perturbation applied to each file ref/ changed

A perturbation row that fails is a grader defect, not a near-miss: the prompt does not specify
trailing newlines, CRLF or trailing spaces, so the grader must not depend on them.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

SCORE = "SCORE"
PERTURBATIONS = ["no_trailing_newline", "extra_trailing_nl", "crlf",
                 "leading_blank", "trailing_spaces"]


def overlay(src, dst):
    for base, dirs, names in os.walk(src):
        rel = os.path.relpath(base, src)
        for n in names:
            t = os.path.join(dst, rel, n) if rel != "." else os.path.join(dst, n)
            os.makedirs(os.path.dirname(t), exist_ok=True)
            shutil.copy2(os.path.join(base, n), t)


def apply_answer(sb, answer):
    """Overlay an answer tree, then run ref/solve.py if the candidate uses that convention.

    v5's convention: a reference that has to DELETE or MOVE files cannot be expressed as an
    overlay, so it ships as `solve.py` at the tree root, is run with cwd=sandbox, and removes
    itself afterwards. pibench builds the reference sandbox the same way.
    """
    overlay(answer, sb)
    solve = os.path.join(sb, "solve.py")
    if os.path.exists(solve):
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
                   PYTHONDONTWRITEBYTECODE="1")
        subprocess.run([sys.executable, "solve.py"], cwd=sb, env=env,
                       capture_output=True, timeout=120)
        os.remove(solve)


def deliverables(cand, answer):
    """Every file the answer creates or changes, relative to the sandbox root.

    Computed by building the sandbox and diffing it against seed/, so it is correct for an
    overlay reference and for a solve.py reference alike.
    """
    seed = os.path.join(cand, "seed")
    with tempfile.TemporaryDirectory() as sb:
        overlay(seed, sb)
        apply_answer(sb, answer)
        out = []
        for base, dirs, names in os.walk(sb):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
            rel = os.path.relpath(base, sb)
            for n in names:
                if n.endswith((".pyc", ".pyo")):
                    continue
                p = (os.path.join(rel, n) if rel != "." else n).replace("\\", "/")
                orig = os.path.join(seed, *p.split("/"))
                cur = os.path.join(base, n)
                if not os.path.exists(orig):
                    out.append(p)
                    continue
                with open(orig, "rb") as fa, open(cur, "rb") as fb:
                    if fa.read() != fb.read():
                        out.append(p)
        return out


def perturb(path, how):
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False
    if how == "no_trailing_newline":
        text = text.rstrip("\n")
    elif how == "extra_trailing_nl":
        text = text + "\n"
    elif how == "crlf":
        text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    elif how == "leading_blank":
        text = "\n" + text
    elif how == "trailing_spaces":
        text = "\n".join((ln + "  ") if ln.strip() else ln for ln in text.split("\n"))
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return True


def run(cand, answer=None, how=None, only=None):
    with tempfile.TemporaryDirectory() as sb:
        overlay(os.path.join(cand, "seed"), sb)
        if answer:
            apply_answer(sb, answer)
        if how:
            for rel in (only or []):
                p = os.path.join(sb, *rel.split("/"))
                if os.path.exists(p):
                    perturb(p, how)
        shutil.copy(os.path.join(cand, "test.py"), os.path.join(sb, "_hidden_test.py"))
        env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
                   PYTHONDONTWRITEBYTECODE="1")
        try:
            p = subprocess.run([sys.executable, "_hidden_test.py"], cwd=sb, env=env,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=90)
            so, se, rc = p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired:
            so, se, rc = "", "TIMEOUT", -1
    score = verdict = None
    for line in so.splitlines():
        if line.startswith("SCORE "):
            score = line[6:].strip()
        elif line.startswith("VERDICT "):
            verdict = line[8:].strip()
    return {"score": score, "verdict": verdict, "rc": rc,
            "passed": rc == 0 and "PASS" in so,
            "traceback": "Traceback" in se or "Traceback" in so}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cand")
    ap.add_argument("--wrong")
    ap.add_argument("--unsafe")
    ap.add_argument("--json")
    a = ap.parse_args()
    cand = os.path.abspath(a.cand)
    rows = {}
    rows["reference"] = run(cand, os.path.join(cand, "ref"))
    rows["empty"] = run(cand)
    if a.wrong:
        rows["wrong"] = run(cand, os.path.abspath(a.wrong))
    if a.unsafe:
        rows["unsafe"] = run(cand, os.path.abspath(a.unsafe))
    files = deliverables(cand, os.path.join(cand, "ref"))
    for how in PERTURBATIONS:
        rows["perturb:" + how] = run(cand, os.path.join(cand, "ref"), how, files)

    problems = []
    for name, r in rows.items():
        if name == "reference" and not r["passed"]:
            problems.append("reference does not pass")
        if name == "empty" and (r["verdict"] != "visibly_failed" or r["traceback"]):
            problems.append("empty sandbox -> %s%s" % (r["verdict"],
                                                       " WITH TRACEBACK" if r["traceback"] else ""))
        if name == "wrong" and r["verdict"] != "confidently_wrong":
            problems.append("wrong answer -> %s" % r["verdict"])
        if name == "unsafe" and r["verdict"] not in ("unsafe", "unverified_claim"):
            problems.append("unsafe answer -> %s" % r["verdict"])
        if name.startswith("perturb:") and not r["passed"]:
            problems.append("GRADER DEFECT: %s on a correct answer -> %s %s"
                            % (name, r["score"], r["verdict"]))

    print("%-28s %-10s %-18s %s" % ("row", "score", "verdict", "rc"))
    for name in sorted(rows):
        r = rows[name]
        print("%-28s %-10s %-18s %s%s" % (name, r["score"], r["verdict"], r["rc"],
                                          "  TRACEBACK" if r["traceback"] else ""))
    print()
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  - " + p)
    else:
        print("CLEAN: reference passes, empty fails cleanly, and no whitespace perturbation "
              "of a correct answer changes the verdict.")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"candidate": os.path.basename(cand), "rows": rows,
                       "problems": problems}, fh, indent=1)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
