#!/usr/bin/env python3
"""Test plan section 2.1's acceptance rule mechanically, on the candidate on disk. CPU only.

    python3 r3/check_rung0.py [<candidate-dir> ...]

The rule, in full:

  > A main-band task's answer requires reconciling facts from several files that the prompt's
  > own vocabulary cannot locate. No single file assembles it, and no grep over the prompt's
  > own words assembles it either.

Nothing in the toolchain tested that. The round-1 authoring brief tested only that no single
grep token finds the answer, and calibration's finding was that it "did not test that a
handful of targeted reads cannot assemble it" (D7-32). This is the missing test, in four
parts, each mechanical and each read out of the candidate's own files:

  A  **the prompt names no load-bearing file.** Its path, its basename and its basename
     without extension are all searched for in `prompt.md`. A `LOAD_BEARING` entry may carry
     `"named_in_prompt": true` to declare a pointer the prompt legitimately gives — the list
     of stages in scope, say — and every such declaration is printed, so a reviewer sees
     exactly which doors the prompt opens rather than having to take the author's word.
  B  **no single file assembles the answer.** The answer is every scored value together, so
     the test is whether one file under `seed/` contains all of them at once. Per-key holders
     are printed as a note and are not a failure: the file that carries one hop is supposed to
     carry it, and a corpus index that happens to list every stage name has not given away
     which four of them qualify.
  C  **no single SELECTIVE grep over the prompt's own words assembles it.** Every distinctive
     word in `prompt.md` is grepped over `seed/`. A word that covers the load-bearing set only
     because it covers the whole tree is not a shortcut — it is the traversal, spelled
     differently — so a covering word fails the check only when it is also narrow: at most
     twice the load-bearing count, or a fifth of the tree. The narrowest covering word is
     printed either way.
  D  **the load-bearing set spans several files and several hops** — at least six and three,
     plan section 2.4, checked here as well as in the builder so a hand-edited grader cannot
     slip past.

A failure of A, B or C is a rung-0 failure: the task can be answered without traversing the
material, and no amount of hardening on the v5 ladder will change that (D7-37, D7-38).
"""
import argparse
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORING = os.path.dirname(HERE)
MIN_PATHS = 6
MIN_HOPS = 3

STOP = set("""a an and are as at be been before but by can do does for from has have if in into
is it its may must never no not of on one only or other our over same shall should so some
such than that the their them then there these they this those to two under until up upon use
used using was were what when where which while who why will with within without you your
work working current directory root new file files line lines write written writes exactly
order value values name names each every all any more most also just plainly stop nothing
create created creates modify modified delete deleted existing task prompt project repository
checkout report list plain integer comma separated alphabetical header quotes explanation
newline end ends may not do does""".split())

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")


def literal(test_py, name):
    with open(test_py, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return ast.literal_eval(node.value)
    return None


def seed_texts(seed):
    out = {}
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache", ".git")]
        for n in names:
            if n.endswith((".pyc", ".pyo")):
                continue
            p = os.path.join(base, n)
            rel = os.path.relpath(p, seed).replace(os.sep, "/")
            try:
                out[rel] = open(p, encoding="utf-8").read()
            except UnicodeDecodeError:
                out[rel] = open(p, "rb").read().decode("utf-8", "replace")
    return out


def tokens(value):
    return [t for t in re.split(r"[,\s]+", value.strip()) if t]


def check(cand):
    slot = os.path.basename(cand)
    seed = os.path.join(cand, "seed")
    prompt = open(os.path.join(cand, "prompt.md"), encoding="utf-8").read()
    plow = prompt.lower()
    lb = literal(os.path.join(cand, "test.py"), "LOAD_BEARING") or []
    cfg = literal(os.path.join(cand, "test.py"), "CONFIG") or {}
    texts = seed_texts(seed)
    problems = []
    notes = []

    lb_paths = sorted(set(p["path"] for p in lb))
    hops = sorted(set(p["hop"] for p in lb))

    # D — shape of the declaration
    if len(lb_paths) < MIN_PATHS:
        problems.append("D: %d load-bearing paths, the plan requires %d"
                        % (len(lb_paths), MIN_PATHS))
    if len(hops) < MIN_HOPS:
        problems.append("D: %d distinct hops, the plan requires %d" % (len(hops), MIN_HOPS))

    # A — the prompt names no load-bearing file, bar the pointers it declares
    declared = sorted(set(e["path"] for e in lb if e.get("named_in_prompt")))
    for d in declared:
        notes.append("prompt declares the pointer %s (named_in_prompt)" % d)
    for p in lb_paths:
        if p in declared:
            continue
        base = p.rsplit("/", 1)[-1]
        stem = base.rsplit(".", 1)[0]
        for form in (p, base, stem):
            if len(form) >= 5 and form.lower() in plow:
                problems.append("A: prompt.md names the load-bearing file %s (as %r) and "
                                "does not declare it as a pointer" % (p, form))
                break

    # B — no single file assembles the answer, which is every scored value together
    expect = cfg.get("expect") or {}
    every = []
    for want in expect.values():
        every.extend(tokens(want))
    if every:
        holders = [rel for rel, text in texts.items()
                   if all(part in text for part in every)]
        if holders:
            problems.append("B: one file assembles every scored value at once: %s"
                            % holders[:3])
    for key, want in sorted(expect.items()):
        parts = tokens(want)
        if len(parts) < 2:
            continue
        h = [rel for rel, text in texts.items() if all(part in text for part in parts)]
        if h:
            notes.append("%s: %d file(s) contain every member of that value (%s) — a note, "
                         "not a failure" % (key, len(h), ", ".join(sorted(h)[:3])))

    # C — no single grep over the prompt's own words assembles it
    words = sorted(set(w.lower() for w in WORD.findall(prompt)) - STOP)
    # A declared pointer (the roster the prompt legitimately names) holds no scored value, so
    # a word that reaches every *other* load-bearing file is the shortcut: 2026-09-08, a
    # reviewer found a prompt token reaching 8 of 9 and the ninth was the manifest pointer.
    lbset = set(lb_paths) - set(declared)
    keynames = set()
    for k in list((cfg.get("expect") or {}).keys()) + list(cfg.get("keys") or []):
        keynames.update(w.lower() for w in WORD.findall(str(k)))
        keynames.add(str(k).lower())
    locators = []
    selective = max(2 * len(lbset), int(0.2 * len(texts)))
    best, best_n = None, None
    widest, widest_cover = None, 0
    for w in words:
        hits = set(rel for rel, text in texts.items() if w in text.lower())
        cover = len(lbset & hits)
        if cover > widest_cover:
            widest, widest_cover = w, cover
        # C2 — a prompt word that greps to one or two files, one of them load-bearing, is a
        # one-hop locator for a decisive file (2026-09-08: `correction` -> the changelog that
        # held the whole delta). A declared pointer is exempt.
        if 0 < len(hits) <= 2 and (hits & lbset):
            if w in keynames:
                problems.append("C2: the deliverable's key %r appears in the prompt and greps "
                                "to only %d file(s), one load-bearing: %s"
                                % (w, len(hits), sorted(hits & lbset)))
            else:
                locators.append((w, sorted(hits & lbset)[0]))
        if lbset and lbset <= hits:
            if best_n is None or len(hits) < best_n:
                best, best_n = w, len(hits)
            if len(hits) <= selective:
                problems.append("C: the prompt's own word %r greps to all %d load-bearing "
                                "files and only %d files in all — that is a shortcut"
                                % (w, len(lbset), len(hits)))
    if locators:
        bylb = {}
        for w, f in locators:
            bylb.setdefault(f, []).append(w)
        for f, ws in sorted(bylb.items()):
            notes.append("locator words: %d prompt word(s) grep to <=2 files including %s "
                         "(%s) — a note; a reviewer should try each as a one-hop shortcut"
                         % (len(ws), f, ", ".join(ws[:6])))
    if best is not None:
        notes.append("narrowest covering prompt word %r hits %d of %d files; a word must hit "
                     "at most %d to count as a shortcut" % (best, best_n, len(texts), selective))
    else:
        notes.append("no prompt word reaches every load-bearing file; the widest, %r, reaches "
                     "%d of %d" % (widest, widest_cover, len(lb_paths)))
    notes.append("%d distinctive prompt words tested over %d seed files"
                 % (len(words), len(texts)))
    return slot, problems, notes


def candidates(args):
    if args:
        return [os.path.abspath(a) for a in args]
    out = []
    for fam in sorted(d for d in os.listdir(AUTHORING) if d.startswith("cand-")):
        base = os.path.join(AUTHORING, fam)
        for slot in sorted(os.listdir(base)):
            mp = os.path.join(base, slot, "MANIFEST.json")
            if not os.path.exists(mp):
                continue
            with open(mp, encoding="utf-8") as fh:
                if (json.load(fh) or {}).get("round") == "v7r3-difficulty":
                    out.append(os.path.join(base, slot))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cands", nargs="*")
    a = ap.parse_args()
    cands = candidates(a.cands)
    if not cands:
        print("no round-3 candidates found")
        return 1
    bad = 0
    for cand in cands:
        slot, problems, notes = check(cand)
        print("%-20s %s" % (slot, "rung 0 clear" if not problems
                            else "%d PROBLEM(S)" % len(problems)))
        for n in notes:
            print("    - " + n)
        for p in problems:
            print("    ! " + p)
        if problems:
            bad += 1
    print("\n%d candidate(s), %d failing plan section 2.1" % (len(cands), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
