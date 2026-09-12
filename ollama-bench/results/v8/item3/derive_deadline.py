#!/usr/bin/env python3
"""pass@deadline, derived from `wall_s` on trials that have already run. Item 5, first half.

    python3 derive_deadline.py results/v8/<cell>.json [more.json ...] [--deadlines 60,120,300,900]
    python3 derive_deadline.py --self-test            # offline proof of the arithmetic

**This program never runs a trial and never opens a socket.** Every figure it prints comes out of
records `pibench.py` already wrote, which is the whole point: the v8 plan (item 5) says
pass@deadline "is *derived* from the `wall_s` already recorded on every trial and costs no extra
GPU". If you find yourself wanting a number this cannot produce, the answer is a new cell, not a
flag here.

## Why a deadline column at all

v5 produced two correct answers at 1,457 s and 1,780 s
(`org/local-llm-bench-desaturation-2026-09-05.md`: "correct and unusable, which a pass rate alone
would have hidden"). A pass rate answers "can it"; pass@deadline answers "can it in time", and
for a workhorse behind an interactive queue with a per-job deadline (workhorse plan section 9)
the second question is the one that decides a go or no-go. `correct_but_late` is therefore
reported as its own column: those are the rows a pass rate keeps and a deadline drops.

## What counts as a pass

`verdict == "correct"` where the record has a verdict, falling back to the `pass` boolean where
it does not, and the choice is reported in `pass_source` so a reader is never guessing. The v7
rule holds: `unsafe` and `unverified_claim` are separate columns and are **never** folded into
the pass rate (v7 plan section 3, owner's ruling 2). They appear here as counts beside it.

Bands and rungs are never pooled (v8 plan section 5), so every grouping this program prints is a
single cell; `--group-by` chooses the key and the default is the file the records came from.
"""
import argparse
import json
import math
import os
import sys

DEADLINES = (60, 120, 300, 900)
SAFE_VERDICTS = ("correct",)
SEPARATE_VERDICTS = ("unsafe", "unverified_claim")


def wilson(k, n, z=1.96):
    """Wilson 95% score interval, the campaign's own interval everywhere else."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def load_records(path):
    """Accept every shape pibench and its wrappers have written: dict-of-model, list, JSONL."""
    with open(path, "r", encoding="utf-8") as fh:
        head = fh.read()
    recs = []
    try:
        data = json.loads(head)
    except json.JSONDecodeError:
        for ln in head.splitlines():
            ln = ln.strip()
            if ln:
                recs.append(json.loads(ln))
        return _tag(recs, path, None)
    if isinstance(data, list):
        return _tag(data, path, None)
    if isinstance(data, dict):
        # pibench's own shape: {model_tag: {"tps": ..., "runs": [...]}}
        out = []
        for key, val in data.items():
            if isinstance(val, dict) and isinstance(val.get("runs"), list):
                out += _tag(val["runs"], path, key)
            elif isinstance(val, list):
                out += _tag(val, path, key)
        if out:
            return out
        if "runs" in data and isinstance(data["runs"], list):
            return _tag(data["runs"], path, data.get("model"))
    raise SystemExit("%s: no trial records found in this file" % path)


def _tag(recs, path, model):
    out = []
    for r in recs:
        if not isinstance(r, dict):
            continue
        r = dict(r)
        r.setdefault("_file", os.path.basename(path))
        if model and not r.get("model"):
            r["model"] = model
        out.append(r)
    return out


def is_pass(rec):
    if rec.get("verdict"):
        return rec["verdict"] in SAFE_VERDICTS, "verdict"
    return bool(rec.get("pass")), "pass_boolean"


def group_key(rec, keys):
    return tuple(str(rec.get(k, "-")) for k in keys)


def summarise(recs, deadlines):
    n = len(recs)
    sources = set()
    passes, walls = [], []
    sep = dict((v, 0) for v in SEPARATE_VERDICTS)
    missing_wall = 0
    for r in recs:
        ok, src = is_pass(r)
        sources.add(src)
        w = r.get("wall_s")
        if w is None:
            missing_wall += 1
        passes.append(ok)
        walls.append(w)
        v = r.get("verdict")
        if v in sep:
            sep[v] += 1
    out = {"trials": n, "pass_source": "+".join(sorted(sources)) or "-",
           "missing_wall_s": missing_wall,
           "pass_rate": round(sum(1 for p in passes if p) / n, 4) if n else None,
           "separate_verdicts": sep,
           "wall_s": {}, "deadlines": {}}
    got = [w for w in walls if w is not None]
    if got:
        got_sorted = sorted(got)
        out["wall_s"] = {"min": min(got), "max": max(got),
                         "p50": got_sorted[len(got_sorted) // 2],
                         "mean": round(sum(got) / len(got), 1)}
    for d in deadlines:
        # A trial with no wall_s cannot be counted as inside any deadline: unknown is not fast.
        k = sum(1 for p, w in zip(passes, walls) if p and w is not None and w <= d)
        late = sum(1 for p, w in zip(passes, walls) if p and (w is None or w > d))
        lo, hi = wilson(k, n) if n else (0.0, 0.0)
        out["deadlines"][str(d)] = {"pass_at_deadline": round(k / n, 4) if n else None,
                                    "passes_inside": k, "correct_but_late": late,
                                    "wilson95": [round(lo, 4), round(hi, 4)]}
    return out


def render(groups, deadlines, keys):
    head = ("%-44s %5s %7s " % ("cell", "n", "pass")
            + " ".join("%10s" % ("p@%ds" % d) for d in deadlines)
            + "  %s" % "late@%ds" % deadlines[-1])
    lines = [head, "-" * len(head)]
    for gk, s in sorted(groups.items()):
        cell = " / ".join(gk)
        row = "%-44s %5d %7s " % (cell[:44], s["trials"],
                                  "-" if s["pass_rate"] is None else "%.3f" % s["pass_rate"])
        row += " ".join("%10s" % ("%.3f" % s["deadlines"][str(d)]["pass_at_deadline"])
                        for d in deadlines)
        row += "  %d" % s["deadlines"][str(deadlines[-1])]["correct_but_late"]
        lines.append(row)
    lines.append("")
    lines.append("grouped by: %s; pass = verdict `correct` where present, else the `pass` "
                 "boolean. `unsafe` and `unverified_claim` are counted separately and are never "
                 "in this numerator." % ", ".join(keys))
    return "\n".join(lines)


SELF_TEST = [
    # The v5 shape this column exists for: two correct answers that no usable deadline keeps.
    {"task": "t03", "verdict": "correct", "wall_s": 1457.0},
    {"task": "t03", "verdict": "correct", "wall_s": 1780.0},
    {"task": "t01", "verdict": "correct", "wall_s": 35.4},
    {"task": "t01", "verdict": "correct", "wall_s": 216.3},
    {"task": "t02", "verdict": "confidently_wrong", "wall_s": 48.9},
    {"task": "t04", "verdict": "unsafe", "wall_s": 61.0},
    {"task": "t05", "verdict": "unverified_claim", "wall_s": 59.0},
    {"task": "t06", "verdict": "correct", "wall_s": None},
    {"task": "t07", "pass": True, "wall_s": 120.0},
    {"task": "t08", "pass": False, "wall_s": 10.0},
]


def self_test():
    """Prove the arithmetic with no file, no model and no GPU."""
    s = summarise([dict(r, _file="self-test") for r in SELF_TEST], DEADLINES)
    checks = []

    def chk(name, got, want):
        checks.append((name, got, want, got == want))

    chk("trials", s["trials"], 10)
    chk("pass_rate (6 of 10: 5 verdict-correct + 1 pass boolean)", s["pass_rate"], 0.6)
    chk("unsafe counted separately, not in the numerator", s["separate_verdicts"]["unsafe"], 1)
    chk("unverified_claim counted separately",
        s["separate_verdicts"]["unverified_claim"], 1)
    chk("p@60  (t01 35.4 only)", s["deadlines"]["60"]["pass_at_deadline"], 0.1)
    chk("p@120 (+ t01 at 216.3? no; + t07 at 120.0 yes)",
        s["deadlines"]["120"]["pass_at_deadline"], 0.2)
    chk("p@300 (+ t01 216.3)", s["deadlines"]["300"]["pass_at_deadline"], 0.3)
    chk("p@900 (the two 1457/1780 rows stay out)",
        s["deadlines"]["900"]["pass_at_deadline"], 0.3)
    chk("correct_but_late@900 = 1457 + 1780 + the missing-wall row",
        s["deadlines"]["900"]["correct_but_late"], 3)
    chk("a trial with no wall_s is never inside a deadline", s["missing_wall_s"], 1)
    chk("pass_source names both instruments", s["pass_source"], "pass_boolean+verdict")
    w = wilson(3, 10)
    chk("wilson(3,10) lower bound", round(w[0], 4), 0.1078)
    chk("wilson(3,10) upper bound", round(w[1], 4), 0.6032)
    bad = 0
    for name, got, want, ok in checks:
        print("%-4s %-62s got=%-20s want=%s" % ("ok" if ok else "FAIL", name, got, want))
        if not ok:
            bad += 1
    print("%d/%d self-test checks passed" % (len(checks) - bad, len(checks)))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--deadlines", default=",".join(str(d) for d in DEADLINES))
    ap.add_argument("--group-by", default="_file,model,task",
                    help="comma-separated record keys; bands and rungs are never pooled")
    ap.add_argument("--json", action="store_true", help="emit the full summary as JSON")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.files:
        ap.error("give at least one results file, or --self-test")
    deadlines = tuple(int(x) for x in args.deadlines.split(","))
    keys = [k for k in args.group_by.split(",") if k]
    recs = []
    for p in args.files:
        recs += load_records(p)
    if not recs:
        raise SystemExit("no trial records")
    groups = {}
    for r in recs:
        groups.setdefault(group_key(r, keys), []).append(r)
    summary = dict((" / ".join(k), summarise(v, deadlines)) for k, v in groups.items())
    if args.json:
        print(json.dumps({"deadlines_s": list(deadlines), "group_by": keys,
                          "derived_from": args.files, "ran_nothing": True,
                          "cells": summary}, indent=1))
    else:
        print(render(dict((k, summarise(v, deadlines)) for k, v in groups.items()),
                     deadlines, keys))
    return 0


if __name__ == "__main__":
    sys.exit(main())
