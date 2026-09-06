#!/usr/bin/env python3
"""Prove `r4/check_harvest.py` has teeth, on two synthetic candidates built here. CPU only.

    python3 r4/probe_harvest.py [--keep]

The scope gate earned `probe_scope_gate.py --breach` because a gate that never fires is not a
gate (calibration section 5). The same argument applies to the grep-harvest check, so this probe
builds two minimal candidate directories in a temp dir outside every checkout and measures both:

  `harvestable`  every unit's decisive value is a named constant on one line, two lines under a
                 heading that repeats a word of the prompt.  One `grep -C2` on that word pulls
                 the lot.  Expected: H1 = 1.0, the check FAILS it.
  `derived`      no unit's value appears anywhere in the material; each unit's own record holds
                 the events the value has to be summed from, and the per-unit prose shares no
                 vocabulary with the prompt.  Expected: H1 = H2 = 0.0, every unit `derived`,
                 the check PASSES it.

Both trees carry the same units, the same roster and the same prompt shape, so the only variable
is the property under test.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UNITS = ["ingest-01", "ingest-02", "ingest-03", "ingest-04", "ingest-05",
         "ingest-06", "ingest-07", "ingest-08"]
CEILINGS = [480, 512, 640, 720, 800, 864, 960, 1024]

PROMPT = """# Reconcile the ingest ceilings

Write `conformance.txt` with one key per line, in this order: `over_ceiling`, `total_ceiling`.
The roster of ingest units in scope is `config/roster.md`. Do not create any other file and do
not modify an existing one.
"""


def w(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def build(root, harvestable):
    seed = os.path.join(root, "seed")
    w(os.path.join(root, "prompt.md"), PROMPT)
    w(os.path.join(seed, "config/roster.md"),
      "# Roster\n\nThe ingest units in scope this quarter:\n\n"
      + "".join("- %s\n" % u for u in UNITS))
    for u, c in zip(UNITS, CEILINGS):
        if harvestable:
            body = ("# %s\n\nThe ceiling for this unit is recorded below.\n\n"
                    "CEILING = %d\n\nOperators review this quarterly.\n" % (u, c))
        else:
            # the value is never stated: it is the sum of the unit's own accepted grants,
            # and the prose shares no word with the prompt.
            a, b = c - 137, 137
            body = ("# %s\n\nAllocation ledger. Each accepted grant adds to the standing "
                    "allowance;\nwithdrawn grants do not.\n\n"
                    "| grant | size | state |\n| --- | ---: | --- |\n"
                    "| g-a | %d | accepted |\n| g-b | %d | accepted |\n| g-c | %d | withdrawn |\n"
                    % (u, a, b, c + 91))
        w(os.path.join(seed, "units/%s.md" % u), body)
    for i in range(6):
        w(os.path.join(seed, "docs/background-%02d.md" % i),
          "# Background %d\n\n" % i + ("Operational narrative. " * 40) + "\n")
    lb = [{"path": "config/roster.md", "hop": "enumeration", "why": "the roster",
           "named_in_prompt": True}]
    for u in UNITS[:6]:
        lb.append({"path": "units/%s.md" % u, "hop": "record", "why": "the unit's own page"})
    units = [{"unit": u, "value": str(c), "path": "units/%s.md" % u}
             for u, c in zip(UNITS, CEILINGS)]
    cfg = {"deliverable": "conformance.txt", "keys": ["over_ceiling", "total_ceiling"],
           "expect": {"over_ceiling": "ingest-07, ingest-08",
                      "total_ceiling": str(sum(CEILINGS))}}
    w(os.path.join(root, "test.py"),
      "LOAD_BEARING = %r\n\nHARVEST_UNITS = %r\n\nCONFIG = %r\n" % (lb, units, cfg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="v7r4-harvest-probe-")
    rc = 0
    try:
        rows = {}
        for name, harvestable in (("harvestable", True), ("derived", False)):
            root = os.path.join(tmp, name)
            build(root, harvestable)
            out = os.path.join(tmp, name + ".json")
            p = subprocess.run([sys.executable, os.path.join(HERE, "check_harvest.py"), root,
                                "--json", out, "--verbose"],
                               capture_output=True, text=True)
            print(p.stdout.rstrip())
            if p.stderr.strip():
                print(p.stderr.rstrip(), file=sys.stderr)
            rows[name] = json.load(open(out, encoding="utf-8"))[0]
        h = rows["harvestable"]
        d = rows["derived"]
        print("\n%-14s H1(C2)=%.3f H2(C2)=%.3f derived=%d pass=%s"
              % ("harvestable", h["h1_c2"], h["h2_c2"], h["derived"], h["pass"]))
        print("%-14s H1(C2)=%.3f H2(C2)=%.3f derived=%d pass=%s"
              % ("derived", d["h1_c2"], d["h2_c2"], d["derived"], d["pass"]))
        ok = (not h["pass"]) and h["h1_c2"] >= 1.0 / 3.0 and d["pass"] \
            and d["h1_c2"] == 0.0 and d["h2_c2"] == 0.0 and d["derived"] == len(UNITS)
        print("\nPROBE %s — the check %s the harvestable tree and %s the derived one"
              % ("OK" if ok else "FAILED",
                 "rejects" if not h["pass"] else "ACCEPTS",
                 "accepts" if d["pass"] else "REJECTS"))
        rc = 0 if ok else 1
    finally:
        if a.keep:
            print("kept: " + tmp)
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
