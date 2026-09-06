#!/usr/bin/env python3
"""Build the v7 round-3 main-band candidates from their specs.

    python3 r3/build.py                 # every spec under r3/specs/
    python3 r3/build.py m09-main-luna   # one slot

Each candidate is written to `cand-<family>/<slot>/`, beside the round-1 candidates, which are
never touched. The suite on disk is not touched either: a round-3 candidate enters the suite
only after the acceptance sweep of plan section 2.2, which needs the GPU.

The generated corpora are cached under `r3/.corpus-cache/` so nine builds do not regenerate
nine trees; the cache is content-free scratch and is safe to delete.
"""
import argparse
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORING = os.path.dirname(HERE)
sys.path.insert(0, AUTHORING)

from r3 import common as C          # noqa: E402

CACHE = os.path.join(HERE, ".corpus-cache")


def specs():
    out = []
    for n in sorted(os.listdir(os.path.join(HERE, "specs"))):
        if n.startswith("n") and n.endswith(".py"):
            out.append(importlib.import_module("r3.specs." + n[:-3]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slots", nargs="*")
    ap.add_argument("--json", dest="jsonout")
    a = ap.parse_args()

    if not os.path.isdir(CACHE):
        os.makedirs(CACHE)
    rows = []
    for spec in specs():
        if a.slots and spec.SLOT not in a.slots:
            continue
        outdir = os.path.join(AUTHORING, "cand-" + spec.FAMILY)
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        rows.append(C.build(spec, outdir, corpus_cache=CACHE, quiet=True))

    print("%-18s %-7s %-5s %-8s %-6s %-4s %-5s %-9s %s"
          % ("slot", "family", "mode", "tokens", "files", "lb", "hops", "sweep_tok", "cov%"))
    bad = 0
    for r in rows:
        flag = "" if r["in_band"] else "  <== OUT OF BAND"
        if not r["in_band"]:
            bad += 1
        print("%-18s %-7s %-5d %-8d %-6d %-4d %-5d %-9d %-5s%s"
              % (r["slot"], r["family"], r["mode"], r["tokens"], r["files"],
                 r["load_bearing"], len(r["hops"]), r["sweep_tokens"],
                 r["expected_coverage_pct"], flag))
    print("\n%d candidate(s) built, %d out of band" % (len(rows), bad))
    if a.jsonout:
        C.write(a.jsonout, json.dumps(rows, indent=1) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
