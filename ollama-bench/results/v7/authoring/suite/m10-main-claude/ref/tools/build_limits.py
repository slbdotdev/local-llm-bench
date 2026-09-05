#!/usr/bin/env python3
"""Write report/limits.csv from config/manifest.json, filtered by the reporting policy.

`docs/policy/capacity-report.md` says the report covers the stages Capacity Planning is
accountable for — every stage except those on Platform Reliability's rota — and says that the
rota is recorded only in the on-call column of `docs/operations.md`. Both are read here, at run
time, so the report follows the repository rather than a list written down once.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def excluded():
    path = os.path.join(ROOT, "docs", "operations.md")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    out = set()
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[3] == "Platform Reliability":
            out.add(cells[0])
    return out


def main():
    with open(os.path.join(ROOT, "config", "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    skip = excluded()
    rows = sorted((s for s in man["stages"] if s["name"] not in skip),
                  key=lambda s: (-s["limit"], s["name"]))
    out = os.path.join(ROOT, "report")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "limits.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("stage,limit,window_s\n")
        for s in rows:
            fh.write("%s,%d,%d\n" % (s["name"], s["limit"], s["window_s"]))


if __name__ == "__main__":
    main()
