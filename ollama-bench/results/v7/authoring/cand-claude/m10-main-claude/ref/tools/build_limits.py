#!/usr/bin/env python3
"""Write report/limits.csv from config/manifest.json."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    with open(os.path.join(ROOT, "config", "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    rows = sorted(man["stages"], key=lambda s: (-s["limit"], s["name"]))
    out = os.path.join(ROOT, "report")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "limits.csv"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("stage,limit,window_s\n")
        for s in rows:
            fh.write("%s,%d,%d\n" % (s["name"], s["limit"], s["window_s"]))


if __name__ == "__main__":
    main()
