#!/usr/bin/env python3
"""Restamp every candidate's MANIFEST.json material fields from the seed on disk.

    python3 stamp_manifests.py [--check]

`material_chars`, `material_tokens` and `seed_files` are measurements, and a measurement written
down once goes stale the first time anyone edits the seed. Two did tonight: `m02-main-luna` gained
a history entry and a changed configuration table, `m10-main-claude` gained a policy page, and
both manifests still reported the counts from before the repair. Same failure `stamp_notes.py`
exists to prevent for the near-miss table, one file over.

`--check` reports drift without writing, which is what a validator wants.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHARS_PER_TOKEN = 4.664
JUNK = ("__pycache__", ".pytest_cache", ".git")


def measure(seed):
    chars = files = 0
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in JUNK]
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
    check = "--check" in sys.argv
    drifted = 0
    for fam in sorted(d for d in os.listdir(HERE) if d.startswith("cand-")):
        base = os.path.join(HERE, fam)
        for slot in sorted(os.listdir(base)):
            cand = os.path.join(base, slot)
            mp = os.path.join(cand, "MANIFEST.json")
            seed = os.path.join(cand, "seed")
            if not (os.path.isdir(seed) and os.path.exists(mp)):
                continue
            man = json.load(open(mp, encoding="utf-8"))
            files, chars = measure(seed)
            want = {"material_chars": chars,
                    "material_tokens": int(round(chars / CHARS_PER_TOKEN)),
                    "seed_files": files,
                    "chars_per_token": CHARS_PER_TOKEN}
            if all(man.get(k) == v for k, v in want.items()):
                continue
            drifted += 1
            print("%-20s %s -> %s"
                  % (slot,
                     {k: man.get(k) for k in ("material_tokens", "seed_files")},
                     {k: want[k] for k in ("material_tokens", "seed_files")}))
            if not check:
                man.update(want)
                with open(mp, "w", encoding="utf-8", newline="\n") as fh:
                    json.dump(man, fh, indent=1)
                    fh.write("\n")
    print("\n%d manifest(s) %s" % (drifted, "drifted" if check else "restamped"))
    return 1 if (check and drifted) else 0


if __name__ == "__main__":
    sys.exit(main())
