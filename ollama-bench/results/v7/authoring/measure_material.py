#!/usr/bin/env python3
"""Measure a candidate's seed material, at the constant this suite measured: 4.664 chars/token.

    python3 measure_material.py <candidate-dir> [<candidate-dir> ...]
    python3 measure_material.py --emit-files <candidate-dir> [...]

Prints one line per candidate and, when MANIFEST.json is present beside seed/, checks the
declared band against the measured size. `--emit-files` also writes the per-file token map
`files` into each MANIFEST.json: plan-2026-09-07.md section 2.5 requires it, because material
coverage is the sum of `material_tokens` for the files a trial touched over the candidate's
own `material_tokens`, and nothing else in the tree carries a per-file count. Bands (v7 plan
section 3):

    main    29,000 - 36,000 tokens    runs in a 48k window
    cheap    4,000 -  7,000 tokens    runs in a 24k window
"""
import json
import os
import sys

CHARS_PER_TOKEN = 4.664
BANDS = {"main": (29000, 36000), "cheap": (4000, 7000), "cheap24": (12000, 16000)}


def per_file(seed):
    """path -> tokens, at the suite's own measured constant. Sorted, forward-slashed."""
    out = {}
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", ".pytest_cache")]
        for n in sorted(names):
            if n.endswith((".pyc", ".pyo")):
                continue
            p = os.path.join(base, n)
            try:
                with open(p, encoding="utf-8") as fh:
                    c = len(fh.read())
            except UnicodeDecodeError:
                with open(p, "rb") as fh:
                    c = len(fh.read())
            rel = os.path.relpath(p, seed).replace(os.sep, "/")
            out[rel] = int(round(c / CHARS_PER_TOKEN))
    return dict(sorted(out.items()))


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
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    emit = "--emit-files" in sys.argv[1:]
    for cand in args:
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
                man = json.load(fh)
            band = man.get("band")
            if emit:
                man["files"] = per_file(seed)
                with open(mpath, "w", encoding="utf-8", newline="\n") as fh:
                    json.dump(man, fh, indent=1, ensure_ascii=False)
                    fh.write("\n")
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
