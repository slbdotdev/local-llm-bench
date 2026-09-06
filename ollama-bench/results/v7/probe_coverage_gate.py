#!/usr/bin/env python3
"""Prove the coverage gate fires and holds, on synthetic trials. CPU only, no GPU, no model.

    python3 results/v7/probe_coverage_gate.py [<candidate-dir> ...]

`--verify-calibration` proves the gate reads the same fields the calibration report was written
from. It cannot prove the gate *discriminates*, because no scored record in the tree carries
`read_paths` yet. This does, by fabricating the trials that the sweep will produce:

  sweep        a trial that read the candidate's whole sweep set   -> PASS
  targeted     a trial that read only the load-bearing files       -> FAIL: coverage short
  bulk-half    half the material by token weight, heaviest first    -> coverage clears 50%,
               and the row passes only if that bulk happens to include five load-bearing
               files. On three of the nine candidates it does not, and the row FAILS. That
               is the gate working: plan section 2.2 is a **pair**, and a trial that read a
               lot of the tree without reaching the files the answer turns on has not
               traversed it, it has skimmed it.
  half-plus-lb half the material, chosen to include the whole load-bearing set -> PASS
  grep-only    a trial that named only a directory, never a file   -> FAIL, with the
               expanded upper bound reported beside it so the row is not misread
  nothing      a trial that opened no file at all                  -> FAIL
  uninstrumented  a record with no read_paths at all               -> `n/a`, never 0%

The last is the one that matters most. An absent instrument is not a measurement of zero, and
reading it as one turns a capacity result into a quality one — which is the error calibration
section 1 exists to stop the next round making.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import coverage_gate as G                                      # noqa: E402

AUTHORING = os.path.join(HERE, "authoring")


def candidates(args):
    if args:
        return [os.path.abspath(a) for a in args]
    out = []
    for fam in sorted(d for d in os.listdir(AUTHORING) if d.startswith("cand-")):
        base = os.path.join(AUTHORING, fam)
        for slot in sorted(os.listdir(base)):
            man = os.path.join(base, slot, "MANIFEST.json")
            if not os.path.exists(man):
                continue
            with open(man, encoding="utf-8") as fh:
                if (json.load(fh) or {}).get("round") == "v7r2-traversal":
                    out.append(os.path.join(base, slot))
    return out


def synth(task, paths, expanded=None, instrumented=True):
    run = {"task": task, "verdict": "correct", "score": 1.0, "timed_out": False,
           "stop_reason": "stop", "turns": 9, "tool_calls": 12, "out_tokens": 700,
           "tools": {"bash": 9, "read": 3}, "achieved_fill_prompt_tokens": 14000}
    if instrumented:
        run["read_paths"] = sorted(paths)
        run["read_paths_expanded"] = sorted(set(expanded if expanded is not None else paths))
        run["tool_arg_keys"] = {"command": 9, "path": 3}
    return run


def sweep_of(cand):
    """The spec's own sweep set, re-derived by importing the spec and re-reading the seed."""
    import importlib
    sys.path.insert(0, AUTHORING)
    slot = os.path.basename(cand)
    modname = "r2.specs." + slot.replace("-", "_")
    spec = importlib.import_module(modname)
    corpus = importlib.import_module("r2.common").Corpus(os.path.join(cand, "seed"))
    ctx = {"seed": os.path.join(cand, "seed"), "corpus": corpus, "spec": spec}
    ctx["facts"] = spec.facts(ctx)
    return list(spec.sweep_paths(ctx))


def main():
    cands = candidates(sys.argv[1:])
    if not cands:
        print("no round-2 candidates built yet")
        return 1
    bad = 0
    print("%-20s %-14s %-9s %-11s %-8s %s"
          % ("slot", "case", "cover%", "cover+x%", "lb", "gate"))
    for cand in cands:
        slot = os.path.basename(cand)
        task = G.load_task_dirs([os.path.dirname(cand)])[slot]
        files = {k.lower(): v for k, v in (task["manifest"].get("files") or {}).items()}
        lb = [p["path"].lower() for p in (task["load_bearing"] or [])]
        try:
            sweep = [p.lower() for p in sweep_of(cand)]
        except Exception as exc:                      # a spec that will not import
            print("%-20s could not re-derive its sweep set: %s" % (slot, exc))
            bad += 1
            continue

        ordered = sorted(set(sweep), key=lambda p: -files.get(p, 0))
        total = task["manifest"].get("material_tokens") or 1

        def take_half(seed_paths):
            got, acc = list(seed_paths), 0
            for p in got:
                acc += files.get(p, 0)
            for p in ordered:
                if acc >= total * 0.5:
                    break
                if p in got:
                    continue
                got.append(p)
                acc += files.get(p, 0)
            return got

        half = take_half([])
        half_lb = take_half(lb)

        dirs = sorted(set(p.rsplit("/", 1)[0] for p in sweep if "/" in p))
        expanded_all = [p for p in files if any(p.startswith(d + "/") for d in dirs)]

        cases = [
            ("sweep", synth(slot, sweep), "PASS", None),
            ("targeted", synth(slot, lb), "FAIL", None),
            # The bulk-half row is asserted on the COVERAGE half only. Whether it also clears
            # the load-bearing half is the thing being measured, not a thing being required.
            ("bulk-half", synth(slot, half), None, "coverage>=50"),
            ("half-plus-lb", synth(slot, half_lb), "PASS", None),
            ("grep-only", synth(slot, [], expanded_all), "FAIL", None),
            ("nothing", synth(slot, []), "FAIL", None),
            ("uninstrumented", synth(slot, [], instrumented=False), "n/a", None),
        ]
        for name, run, want, assertion in cases:
            r = G.gate_run(run, task)
            if assertion == "coverage>=50":
                ok = r["coverage_pct"] is not None and r["coverage_pct"] >= 50.0
                want = "%s (coverage %s%%, lb %s/%s)" % (
                    r["gate"], r["coverage_pct"], r["lb_touched"], r["lb_paths"])
            else:
                ok = r["gate"] == want
            if not ok:
                bad += 1
            print("%-20s %-14s %-9s %-11s %-8s %s%s"
                  % (slot, name, G._pct(r["coverage_pct"]),
                     G._pct(r["coverage_expanded_pct"]),
                     ("%s/%s" % (r["lb_touched"], r["lb_paths"])
                      if r["lb_touched"] is not None else "n/a"),
                     r["gate"], "" if ok else "   <== wanted %s" % want))
    print("\n%d candidate(s) probed, %d unexpected gate verdict(s)" % (len(cands), bad))
    if bad:
        return 1
    print("\nThe gate passes a trial that swept the material, fails one that read only the\n"
          "load-bearing files, fails one that named a directory and no file, and reports a\n"
          "record with no read_paths as n/a rather than as zero. On the bulk-half row it\n"
          "shows why section 2.2 is a pair: reading half the tree by weight is not the same\n"
          "as reaching the files the answer turns on, and on some candidates it is not even\n"
          "close.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
