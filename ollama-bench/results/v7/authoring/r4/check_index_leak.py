#!/usr/bin/env python3
"""Is a per-stage module constant echoed anywhere else in the tree? CPU only.

    python3 r4/check_index_leak.py [<candidate-dir> ...]

The defect this exists for, found by cross-review of `m05-main-claude` and `m08-main-claude`
on 2026-09-07 and then measured to be systemic:

`make_corpus.py` writes each stage's `limit` and `window_s` into **five** artifacts — the
module constant, `config/manifest.json`, the `docs/operations.md` table, the stage's history
entry and the stage's test — all agreeing by construction. A task whose predicate is "the
stage document's table disagrees with the module constant" can therefore be answered by
comparing the document against **any** of the other four, and `config/manifest.json` and
`docs/operations.md` are each a single small file listing every stage.

So a solver reads two files, not forty, and the whole rung-0 property is defeated while every
other check in the toolchain stays green: `check_rung0.py`'s part B looks for one file holding
the answer and part C for one selective grep, and this is neither — it is a two-artifact
substitution.

The check: for every stage, take the value of the spec's `DECISIVE_CONSTANT` in that stage's
own module, and count the other seed files that mention the stage (by name or by module name)
**on the same line as** that value. One such file is an echo; the predicate has a second
source and the modules need not be opened.

A spec declares `DECISIVE_CONSTANT` as a template, e.g. `"DEFAULT_%s_LIMIT"` or
`"ENFORCED_CEILING"`, where `%s` is the stage name upper-cased. A spec whose decisive fact is
not a module constant declares nothing and is skipped with a line saying so.
"""
import argparse
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORING = os.path.dirname(HERE)
sys.path.insert(0, AUTHORING)


def specs():
    out = []
    for n in sorted(os.listdir(os.path.join(HERE, "specs"))):
        if n.startswith("p") and n.endswith(".py"):
            out.append(importlib.import_module("r4.specs." + n[:-3]))
    return out


def check(spec, override=None):
    cand = os.path.join(AUTHORING, "cand-" + spec.FAMILY, spec.SLOT)
    seed = os.path.join(cand, "seed")
    if not os.path.isdir(seed):
        return spec.SLOT, ["not built"], []
    tmpl = override or getattr(spec, "DECISIVE_CONSTANT", None)
    if not tmpl:
        return spec.SLOT, [], ["declares no DECISIVE_CONSTANT; not checked"]

    common = importlib.import_module("r4.common")
    corpus = common.Corpus(seed)
    texts = {}
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache", ".git")]
        for n in names:
            p = os.path.join(base, n)
            rel = os.path.relpath(p, seed).replace(os.sep, "/")
            try:
                texts[rel] = open(p, encoding="utf-8").read()
            except UnicodeDecodeError:
                texts[rel] = open(p, "rb").read().decode("utf-8", "replace")

    problems, notes = [], []
    leaks = {}
    for st in corpus.stages:
        name = tmpl % st["name"].upper() if "%s" in tmpl else tmpl
        m = re.search(r"^%s\s*=\s*(\S+)\s*$" % re.escape(name),
                      texts.get(st["src"], ""), re.M)
        if not m:
            continue
        value = m.group(1).strip()
        needles = (st["name"], st["module"])
        for rel, text in texts.items():
            if rel == st["src"]:
                continue
            for line in text.splitlines():
                if value in line and any(nd in line for nd in needles):
                    leaks.setdefault(rel, []).append("%s=%s" % (st["name"], value))
                    break
    for rel in sorted(leaks):
        n = len(leaks[rel])
        problems.append("%s echoes the decisive constant for %d stage(s) beside the stage's "
                        "own name (%s%s)" % (rel, n, ", ".join(leaks[rel][:3]),
                                             ", ..." if n > 3 else ""))
    if not problems:
        notes.append("the decisive constant %r appears only in each stage's own module" % tmpl)
    return spec.SLOT, problems, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slots", nargs="*")
    ap.add_argument("--constant", help="override DECISIVE_CONSTANT, e.g. 'DEFAULT_%%s_LIMIT' — for surveying a class of leak across every candidate")
    a = ap.parse_args()
    bad = 0
    for spec in specs():
        if a.slots and spec.SLOT not in a.slots:
            continue
        slot, problems, notes = check(spec, a.constant)
        print("%-20s %s" % (slot, "clean" if not problems else "%d LEAK(S)" % len(problems)))
        for n in notes:
            print("    - " + n)
        for p in problems:
            print("    ! " + p)
        if problems:
            bad += 1
    print("\n%d candidate(s) leak their decisive constant into an index" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
