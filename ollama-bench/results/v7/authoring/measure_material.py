#!/usr/bin/env python3
"""Measure a candidate's seed material, at the constant this suite measured: 4.664 chars/token.

    python3 measure_material.py <candidate-dir> [<candidate-dir> ...]

Prints one line per candidate and, when MANIFEST.json is present beside seed/, checks the
declared band against the measured size. Bands (v7 plan section 3):

    main    29,000 - 36,000 tokens    runs in a 48k window
    cheap    4,000 -  7,000 tokens    runs in a 24k window
"""
import json
import os
import sys

CHARS_PER_TOKEN = 4.664
BANDS = {"main": (29000, 36000), "cheap": (4000, 7000)}


def measure(seed):
    chars = 0
    files = 0
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", ".pytest_cache")]
        for n in names:
            if n.endswith((".pyc", ".pyo")):
                continue
            p = os.path.join(base, n)
            try:
                with open(p, encoding="utf-8") as fh:
                    chars += len(fh.read())
            except UnicodeDecodeError:
                with open(p, "rb") as fh:
                    chars += len(fh.read())
            files += 1
    return files, chars


def main():
    bad = 0
    for cand in sys.argv[1:]:
        seed = os.path.join(cand, "seed")
        if not os.path.isdir(seed):
            print("%-28s NO seed/ DIRECTORY" % os.path.basename(cand))
            bad += 1
            continue
        files, chars = measure(seed)
        tokens = int(round(chars / CHARS_PER_TOKEN))
        band = None
        mpath = os.path.join(cand, "MANIFEST.json")
        if os.path.exists(mpath):
            with open(mpath, encoding="utf-8") as fh:
                band = json.load(fh).get("band")
        note = ""
        if band in BANDS:
            lo, hi = BANDS[band]
            if not (lo <= tokens <= hi):
                note = "  <== OUT OF BAND %s (%d-%d)" % (band, lo, hi)
                bad += 1
        elif band is not None:
            note = "  <== UNKNOWN BAND %r" % band
            bad += 1
        else:
            note = "  (no MANIFEST.json)"
        print("%-28s files=%-5d chars=%-8d tokens=%-7d band=%-6s%s"
              % (os.path.basename(cand), files, chars, tokens, band, note))
    print("\n%d candidate(s) need attention" % bad if bad else "\nall measured candidates in band")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
