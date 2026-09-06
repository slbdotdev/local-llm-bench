#!/usr/bin/env python3
"""Stage the round-3 candidates into one directory, because pibench takes one --tasks-dir.

    python3 r3/stage_gate_suite.py [--check]

Writes `r3/gate-suite/<slot>/` for every slot a round-3 spec declares, copied from its
`cand-<family>/<slot>/`. It is a staging area for the acceptance sweep of plan section 2.2 and
nothing else: **it is not the suite**. A candidate enters `authoring/suite/` only after it
clears the gate and its row is written into `authoring/roundtable.md`'s register, which is what
`assemble_suite.py` reads.

`--check` reports what would be staged and writes nothing.
"""
import argparse
import importlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORING = os.path.dirname(HERE)
sys.path.insert(0, AUTHORING)

STAGE = os.path.join(HERE, "gate-suite")


def slots():
    out = []
    for n in sorted(os.listdir(os.path.join(HERE, "specs"))):
        if n.startswith("n") and n.endswith(".py"):
            spec = importlib.import_module("r3.specs." + n[:-3])
            out.append((spec.SLOT, spec.FAMILY))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    rows = []
    missing = []
    for slot, family in slots():
        src = os.path.join(AUTHORING, "cand-" + family, slot)
        if not os.path.isdir(src):
            missing.append(slot)
            continue
        rows.append((slot, src))

    for slot, src in rows:
        mp = os.path.join(src, "MANIFEST.json")
        man = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
        print("%-20s %-7s %6d tokens  %3d files  %3d in the files map"
              % (slot, man.get("family", "?"), man.get("material_tokens", 0),
                 man.get("seed_files", 0), len(man.get("files") or {})))
    if missing:
        print("\nnot built yet: " + ", ".join(missing))
    if a.check:
        print("\n--check, so nothing was written")
        return 1 if missing else 0

    if os.path.isdir(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE)
    for slot, src in rows:
        shutil.copytree(src, os.path.join(STAGE, slot))
    print("\nstaged %d candidate(s) into %s" % (len(rows), STAGE))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
