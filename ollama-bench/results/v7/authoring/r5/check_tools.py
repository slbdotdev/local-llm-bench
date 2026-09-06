#!/usr/bin/env python3
"""Run every executable tool in a candidate's seed with no arguments, and fail the candidate
if any of them prints a scored value.

    python3 r5/check_tools.py [<candidate-dir> ...] [--verbose] [--timeout N]

`handoff-2026-09-09.md` pickup 2 asks for exactly this check, and says why:

> Rung 0 is what kills candidates, and only a reader finds it. Four of eight authored
> candidates were dropped because a blind cross-reviewer reproduced the reference from two
> files or fewer -- twice from **zero** files -- after every mechanical check passed. Two of
> the four were defeated by a tool in the seed that computed the answer [...] If one thing is
> built next round, build the check that runs the seed's own tools with no arguments and
> asserts none of them prints a scored value.

`p09-main-luna` was dropped on precisely this: `README.md` told the solver to run
`python3 tools/retention_audit.py`, and the tool printed `-> verified_on = <date>
(countersigned)` and the declared/effective windows for all nineteen regions. A blind
reviewer reproduced `ref/retention-report.txt` byte for byte with **no file opened**.
`r4/BRIEF.md` section 6 already forbade it ("No tool in the seed may print the answer");
nothing enforced it, and two reviewers had to find it by hand.

## What it does

For each candidate:

1. Copy `seed/` to a scratch tree, so a tool that writes cannot touch the candidate.
2. Collect every **tool**: any `*.py` or `*.sh` under the seed that is not a test
   (`tests/`, `test_*.py`, `conftest.py`) and not a package marker. A file whose first line
   is a shebang counts wherever it lives.
3. Run each one with **no arguments** -- `python3 <path>` or `bash <path>` -- from the seed
   root, with a timeout, stdin closed, and capture stdout and stderr together. A tool that
   fails, refuses, prints usage or tracebacks is fine: this check is not about whether the
   tool works, it is about what it hands a solver that types its name.
4. Search that output for:
   * every **scored value** the grader compares (`CONFIG["expect"]`), as a bounded token,
     and for a `list`/`set` kind, every member of it separately;
   * every **per-unit decisive datum** the spec declared (`HARVEST_UNITS`), which is the
     material the answer reconciles. A tool that prints those has done the traversal for the
     solver even if it stops short of the final answer.

A scored value found in a tool's output is a **failure**. A harvest value found is a failure
once the tool reaches more than a quarter of the units -- one unit's datum is what a fair
helper legitimately validates, and the whole roster is the answer in pieces. The quarter is
`H1`'s own limit, deliberately: the two measures are asking the same question of two
different channels, a grep and a program.

Exit code 0 when every candidate is clean, 1 otherwise. CPU only; no model, no GPU.
"""
import argparse
import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORING = os.path.dirname(HERE)
HARVEST_SHARE_MAX = 0.25
SKIP_DIRS = {"__pycache__", ".git", ".pytest_cache", "tests", "test"}


def const(path, name):
    """Read one module-level constant out of `test.py` without importing it.

    Importing `test.py` runs the grader against the authoring directory as its sandbox, which
    prints a few megabytes of scope-gate output and grades the wrong tree. Every constant the
    check needs is a literal, so `ast.literal_eval` on the assignment is both safe and exact.
    """
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id == name:
            return ast.literal_eval(node.value)
    return None


def bounded(value):
    return re.compile(r"(?<![0-9A-Za-z_])" + re.escape(str(value)) + r"(?![0-9A-Za-z_])")


def scored_values(cfg):
    """Every string a grader compares, one entry per independently gradable piece."""
    out = []
    expect = (cfg or {}).get("expect") or {}
    kinds = (cfg or {}).get("kinds") or {}
    for key, val in expect.items():
        val = str(val).strip()
        if not val:
            continue
        if kinds.get(key) in ("list", "set"):
            for part in re.split(r"[,\s]+", val):
                if len(part.strip()) >= 2:
                    out.append((key, part.strip()))
        out.append((key, val))
    return out


def tools(seed):
    """Every runnable helper in the seed, tests excluded."""
    out = []
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in sorted(names):
            rel = os.path.relpath(os.path.join(base, n), seed)
            if n in ("__init__.py", "conftest.py") or n.startswith("test_"):
                continue
            full = os.path.join(base, n)
            runner = None
            if n.endswith(".py"):
                runner = [sys.executable]
            elif n.endswith(".sh"):
                runner = ["bash"]
            else:
                try:
                    with open(full, "rb") as fh:
                        head = fh.read(2)
                    if head == b"#!":
                        with open(full, encoding="utf-8", errors="replace") as fh:
                            line = fh.readline()
                        runner = ["bash"] if "sh" in line else [sys.executable]
                except OSError:
                    runner = None
            if runner:
                out.append((rel, runner))
    return out


def check(cand, timeout, verbose):
    slot = os.path.basename(cand.rstrip("/"))
    seed = os.path.join(cand, "seed")
    tpath = os.path.join(cand, "test.py")
    problems, notes = [], []
    if not os.path.isdir(seed) or not os.path.exists(tpath):
        return slot, ["no seed/ or test.py under %s" % cand], notes, []

    cfg = const(tpath, "CONFIG") or {}
    units = const(tpath, "HARVEST_UNITS") or []
    scored = scored_values(cfg)
    harvest = [(u.get("unit"), str(u.get("value")).strip()) for u in units
               if str(u.get("value", "")).strip()]

    found = tools(seed)
    notes.append("%d tool(s) run with no arguments; %d scored value(s), %d declared unit(s)"
                 % (len(found), len(scored), len(harvest)))
    if not found:
        notes.append("no runnable tool in the seed at all, so nothing can print the answer")
        return slot, problems, notes, []

    rows = []
    scratch = tempfile.mkdtemp(prefix="v7r5-tools-")
    work = os.path.join(scratch, "seed")
    try:
        shutil.copytree(seed, work)
        for rel, runner in found:
            try:
                with open(os.devnull, "rb") as devnull:
                    r = subprocess.run(runner + [rel], cwd=work, stdin=devnull,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       timeout=timeout)
                out = r.stdout.decode("utf-8", "replace")
                rc = r.returncode
            except subprocess.TimeoutExpired as exc:
                out = (exc.output or b"").decode("utf-8", "replace")
                rc = "timeout"
            hit_scored = sorted({"%s=%s" % (k, v) for k, v in scored
                                 if bounded(v).search(out)})
            hit_units = sorted({u for u, v in harvest if bounded(v).search(out)})
            rows.append({"tool": rel, "rc": rc, "bytes": len(out),
                         "scored_hits": hit_scored, "unit_hits": hit_units})
            if hit_scored:
                problems.append("%s prints a scored value with no arguments: %s — a solver "
                                "that types the tool's name has the answer without opening a "
                                "file (r5/BRIEF.md section 6, handoff pickup 2)"
                                % (rel, ", ".join(hit_scored[:4])))
            if harvest and len(hit_units) > HARVEST_SHARE_MAX * len(harvest):
                problems.append("%s prints the decisive datum of %d of %d declared units "
                                "(%.0f%%, the limit is %.0f%%) with no arguments: %s — the "
                                "tool does the traversal the task is for"
                                % (rel, len(hit_units), len(harvest),
                                   100.0 * len(hit_units) / len(harvest),
                                   100.0 * HARVEST_SHARE_MAX, ", ".join(hit_units[:6])))
            if verbose:
                notes.append("%-40s rc=%s %6d bytes  scored=%d units=%d/%d"
                             % (rel, rc, len(out), len(hit_scored), len(hit_units),
                                len(harvest)))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return slot, problems, notes, rows


def candidates(args):
    if args:
        return [os.path.abspath(a) for a in args]
    out = []
    for fam in sorted(d for d in os.listdir(AUTHORING) if d.startswith("cand-")):
        base = os.path.join(AUTHORING, fam)
        for slot in sorted(os.listdir(base)):
            if slot.startswith("q") and os.path.isdir(os.path.join(base, slot)):
                out.append(os.path.join(base, slot))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cands", nargs="*")
    ap.add_argument("--timeout", type=float, default=30.0)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    cands = candidates(a.cands)
    if not cands:
        print("no round-5 candidates found")
        return 1
    bad = 0
    for cand in cands:
        slot, problems, notes, _rows = check(cand, a.timeout, a.verbose)
        print("%-20s %s" % (slot, "tools clear" if not problems
                            else "%d PROBLEM(S)" % len(problems)))
        for n in notes:
            print("    - " + n)
        for p in problems:
            print("    ! " + p)
        if problems:
            bad += 1
    print("\n%d candidate(s), %d whose seed tools print scored or per-unit values"
          % (len(cands), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
