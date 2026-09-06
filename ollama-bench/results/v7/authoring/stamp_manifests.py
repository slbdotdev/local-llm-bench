#!/usr/bin/env python3
"""Restamp every candidate's MANIFEST.json material fields from the seed on disk.

    python3 stamp_manifests.py [--check] [<candidate-dir> ...]

`material_chars`, `material_tokens` and `seed_files` are measurements, and a measurement written
down once goes stale the first time anyone edits the seed. Two did tonight: `m02-main-luna` gained
a history entry and a changed configuration table, `m10-main-claude` gained a policy page, and
both manifests still reported the counts from before the repair. Same failure `stamp_notes.py`
exists to prevent for the near-miss table, one file over.

`--check` reports drift without writing, which is what a validator wants.

Since v7 round 2 it also stamps **`files`**, the per-file token map plan-2026-09-07.md section
2.5 requires: material coverage is the sum of `material_tokens` for the files a trial's
`read_paths` names, over the candidate's own `material_tokens`, and no other field in the tree
carries a per-file count. It is a measurement like the other four, so it drifts like them and
is restamped with them. With no directory arguments every `cand-*` candidate is stamped; named
directories are stamped instead, which is how the `suite/` copies are kept in step.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHARS_PER_TOKEN = 4.664
JUNK = ("__pycache__", ".pytest_cache", ".git")


def per_file(seed):
    """path -> tokens. Sorted and forward-slashed, so the map is stable across hosts."""
    out = {}
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in JUNK]
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
            out[os.path.relpath(p, seed).replace(os.sep, "/")] = int(round(c / CHARS_PER_TOKEN))
    return dict(sorted(out.items()))


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


def candidates(args):
    if args:
        return [os.path.abspath(a) for a in args]
    out = []
    for fam in sorted(d for d in os.listdir(HERE) if d.startswith("cand-")):
        base = os.path.join(HERE, fam)
        for slot in sorted(os.listdir(base)):
            out.append(os.path.join(base, slot))
    return out


def main():
    check = "--check" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    drifted = 0
    for cand in candidates(args):
        slot = os.path.basename(cand)
        mp = os.path.join(cand, "MANIFEST.json")
        seed = os.path.join(cand, "seed")
        if not (os.path.isdir(seed) and os.path.exists(mp)):
            continue
        man = json.load(open(mp, encoding="utf-8"))
        files, chars = measure(seed)
        want = {"material_chars": chars,
                "material_tokens": int(round(chars / CHARS_PER_TOKEN)),
                "seed_files": files,
                "chars_per_token": CHARS_PER_TOKEN,
                "files": per_file(seed)}
        if all(man.get(k) == v for k, v in want.items()):
            continue
        drifted += 1
        what = {k: man.get(k) for k in ("material_tokens", "seed_files")}
        what["files"] = len(man.get("files") or {})
        now = {k: want[k] for k in ("material_tokens", "seed_files")}
        now["files"] = len(want["files"])
        print("%-20s %s -> %s" % (slot, what, now))
        if not check:
            man.update(want)
            with open(mp, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(man, fh, indent=1, ensure_ascii=False)
                fh.write("\n")
    print("\n%d manifest(s) %s" % (drifted, "drifted" if check else "restamped"))
    return 1 if (check and drifted) else 0


if __name__ == "__main__":
    sys.exit(main())
