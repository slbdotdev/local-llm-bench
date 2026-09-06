#!/usr/bin/env python3
"""Every round-2 candidate declares a LOAD_BEARING the gate can read. CPU only.

    python3 r2/check_load_bearing.py [<candidate-dir> ...]

With no arguments it checks every slot a round-2 spec declares, wherever it was built.

Four things, all of which the acceptance gate depends on and none of which any existing
validator looks at:

  1. `test.py` declares `LOAD_BEARING`, and it parses with `ast.literal_eval` — the gate never
     imports a grader, because a grader calls `sys.exit`;
  2. at least six paths and at least three distinct hops (plan section 2.4);
  3. every declared path is a real file under that candidate's `seed/`;
  4. `MANIFEST.json` carries the `files` map, and every load-bearing path is in it — without
     that map the coverage number cannot be computed at all (plan section 2.5).

It also prints what the sweep would score if a trial read exactly the load-bearing set, which
is the floor a candidate's coverage can reach, and the expected coverage the spec declared.
"""
import ast
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORING = os.path.dirname(HERE)
sys.path.insert(0, AUTHORING)

MIN_PATHS = 6
MIN_HOPS = 3


def declared_slots():
    out = []
    for n in sorted(os.listdir(os.path.join(HERE, "specs"))):
        if n.startswith("m") and n.endswith(".py"):
            spec = importlib.import_module("r2.specs." + n[:-3])
            out.append(os.path.join(AUTHORING, "cand-" + spec.FAMILY, spec.SLOT))
    return out


def load_bearing(test_py):
    with open(test_py, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "LOAD_BEARING":
                    return ast.literal_eval(node.value)
    return None


def main():
    cands = [os.path.abspath(a) for a in sys.argv[1:]] or declared_slots()
    problems = []
    print("  %-20s %-6s %-6s %-9s %-9s %s"
          % ("slot", "paths", "hops", "lb tokens", "material", "floor coverage"))
    for cand in cands:
        slot = os.path.basename(cand)
        tp = os.path.join(cand, "test.py")
        mp = os.path.join(cand, "MANIFEST.json")
        if not os.path.exists(tp):
            problems.append("%s: not built" % slot)
            continue
        try:
            lb = load_bearing(tp)
        except (SyntaxError, ValueError) as exc:
            problems.append("%s: LOAD_BEARING does not parse: %s" % (slot, exc))
            continue
        if not lb:
            problems.append("%s: test.py declares no LOAD_BEARING" % slot)
            continue
        man = json.load(open(mp, encoding="utf-8")) if os.path.exists(mp) else {}
        files = man.get("files") or {}
        material = man.get("material_tokens") or 0
        paths = [p["path"] for p in lb]
        hops = sorted(set(p.get("hop") for p in lb))
        if len(set(paths)) < MIN_PATHS:
            problems.append("%s: %d distinct load-bearing paths, the plan requires %d"
                            % (slot, len(set(paths)), MIN_PATHS))
        if len(hops) < MIN_HOPS:
            problems.append("%s: %d distinct hops, the plan requires %d"
                            % (slot, len(hops), MIN_HOPS))
        if not files:
            problems.append("%s: MANIFEST.json has no `files` map; the gate cannot compute "
                            "coverage (run stamp_manifests.py)" % slot)
        for p in set(paths):
            if not os.path.isfile(os.path.join(cand, "seed", *p.split("/"))):
                problems.append("%s: load-bearing path %s is not in seed/" % (slot, p))
            elif files and p not in files:
                problems.append("%s: load-bearing path %s is not in the manifest files map"
                                % (slot, p))
        lbtok = sum(files.get(p, 0) for p in set(paths))
        print("  %-20s %-6d %-6d %-9d %-9d %.1f%%"
              % (slot, len(set(paths)), len(hops), lbtok, material,
                 100.0 * lbtok / material if material else 0))
    if problems:
        print("\n  PROBLEMS:")
        for p in problems:
            print("    - " + p)
        return 1
    print("  %d candidate(s), every LOAD_BEARING declaration readable and complete"
          % len(cands))
    return 0


if __name__ == "__main__":
    sys.exit(main())
