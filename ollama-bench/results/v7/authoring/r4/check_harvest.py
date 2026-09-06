#!/usr/bin/env python3
"""The grep-harvest check — round four's addition to the acceptance rule. CPU only.

    python3 r4/check_harvest.py [<candidate-dir> ...] [--context N] [--h1 F] [--h2 F] [--verbose]

## Why this check exists

Round two's rung 0 required that a main-band answer reconcile facts from several files that the
*prompt's* vocabulary cannot locate, and `r4/check_rung0.py` tests that mechanically. Nineteen
candidates were then run on the workhorse and eighteen were answered correctly while naming 6 to
49% of their material (`results/v7/authoring-r3-2026-09-08.md` section 6). The transcripts say
why: the model does not read the tree, **it greps it**. Every per-unit fact was a named constant
on one line, and once the manifest — a pointer the prompt is allowed to give — names the
constant, one `grep -rn <NAME> seed/` puts every unit's value on one screen and the task becomes
arithmetic. Rung 0 made the material unlocatable from the prompt's vocabulary; it did not make
it unlocatable from the *manifest's*.

**The property this check enforces: a value a single grep can harvest across units is not
material, whatever its token count.**

## The measure

Let *G*, the **giveaway vocabulary**, be every distinctive token of `prompt.md`, plus every
distinctive token of any load-bearing file the spec declares `named_in_prompt` (the roster the
prompt legitimately points at), plus the deliverable's own name and the scored keys' words.
Those are the tokens a solver has for free, before opening anything.

Let *V* be the per-unit decisive values, declared by the spec's `harvest_units(ctx)` and written
into `test.py` as `HARVEST_UNITS`: one `{"unit", "value", "path"}` per unit, measured from
`seed/` on disk exactly as `facts()` is.

A unit *u* is **harvested by a token t at context C** when some file *f* under `seed/` has a
line *i* containing *t* (case-insensitively, as a substring, which is what `grep` matches) such
that within the window *[i-C, i+C]* of *f*:

  * some line carries *u*'s value as a bounded token, **and**
  * some line carries *u*'s identifier, **or** *f* is *u*'s own declared path.

The second clause is what makes it a harvest rather than a coincidence: `grep -C2` output that
shows a number without saying which unit owns it is not an answer, and the value inside the
unit's own file is attributed to that unit by the file it sits in.

  * **H1** = max over *t* in *G* of the fraction of units harvested by *t*.
  * **H2** = the fraction of units harvested by the single regular expression alternating over
    every unit identifier — one grep, `grep -nE '(unit-01|unit-02|...)' -C2`, which is what an
    agent that has the roster actually runs.

**A candidate passes when H1 < 1/3 and H2 < 1/2, measured at C = 2.** C = 0 and C = 5 are
reported beside them and are not gated: C = 2 is the window an agentic model actually asks for,
C = 0 is the floor and C = 5 the pessimistic bound.

## Why those numbers

They are chosen, not measured, and this file says so. 1/3 for H1 is the point at which a
grepper still has to open two thirds of the units by hand, so the traversal the coverage gate
measures cannot be skipped; below that the check would forbid designs a fair reader needs (a
roster that names units near their records is legitimate material). 1/2 for H2 is looser
because the roster alternation is a strictly stronger attack that the task's own scope hands the
solver: forbidding it outright would forbid per-unit records altogether. Both are to be
re-derived from the first round-four sweep's measured coverage, exactly as plan section 2.4
says of its own six/three/five.

A unit whose value never occurs literally anywhere under `seed/` is **derived**, is reported as
such, and can never be harvested — that is n09-cheap-luna's shape and it is the strongest
answer to this check. A declared value that matches more than a fifth of the material's lines is
**indistinct**, is excluded from both fractions, and is reported: a decisive datum that is not
distinctive cannot be measured, and more than a third of a candidate's units being indistinct is
itself a failure.
"""
import argparse
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTHORING = os.path.dirname(HERE)

H1_MAX = 1.0 / 3.0
H2_MAX = 0.5
CONTEXT = 2
INDISTINCT_LINE_FRACTION = 0.20
INDISTINCT_UNIT_FRACTION = 1.0 / 3.0

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


def seed_lines(seed):
    """{relpath: [lowercased line, ...]}, the material as `grep` sees it."""
    out = {}
    for base, dirs, names in os.walk(seed):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache", ".git")]
        for n in names:
            if n.endswith((".pyc", ".pyo")):
                continue
            p = os.path.join(base, n)
            rel = os.path.relpath(p, seed).replace(os.sep, "/")
            try:
                text = open(p, encoding="utf-8").read()
            except UnicodeDecodeError:
                text = open(p, "rb").read().decode("utf-8", "replace")
            out[rel] = text.lower().splitlines()
    return out


def bounded(needle):
    """A regex matching `needle` as a bounded token, the way a reader would recognise it."""
    esc = re.escape(needle.lower())
    left = r"(?<![A-Za-z0-9_])" if re.match(r"[A-Za-z0-9_]", needle[0]) else ""
    right = r"(?![A-Za-z0-9_])" if re.match(r"[A-Za-z0-9_]", needle[-1]) else ""
    return re.compile(left + esc + right)


def line_hits(lines_by_file, pattern):
    """{relpath: set(line index)} for a compiled pattern."""
    out = {}
    for rel, lines in lines_by_file.items():
        hit = set(i for i, ln in enumerate(lines) if pattern.search(ln))
        if hit:
            out[rel] = hit
    return out


def substring_hits(lines_by_file, token):
    out = {}
    for rel, lines in lines_by_file.items():
        hit = set(i for i, ln in enumerate(lines) if token in ln)
        if hit:
            out[rel] = hit
    return out


def window(idx, c):
    return set(range(idx - c, idx + c + 1))


def harvested(unit_val, unit_id, unit_path, anchor, ctx):
    """Is the unit harvested, given {rel: {line}} maps for value, id and the anchor token?"""
    for rel, anchors in anchor.items():
        vals = unit_val.get(rel)
        if not vals:
            continue
        ids = unit_id.get(rel, set())
        own = (rel == unit_path)
        for i in anchors:
            w = window(i, ctx)
            if not (w & vals):
                continue
            if own or (w & ids):
                return True
    return False


def giveaway_vocabulary(cand, lb, cfg):
    prompt = open(os.path.join(cand, "prompt.md"), encoding="utf-8").read()
    words = set(w.lower() for w in WORD.findall(prompt))
    seed = os.path.join(cand, "seed")
    for e in lb:
        if not e.get("named_in_prompt"):
            continue
        p = os.path.join(seed, *e["path"].split("/"))
        if os.path.isfile(p):
            try:
                words |= set(w.lower() for w in WORD.findall(open(p, encoding="utf-8").read()))
            except UnicodeDecodeError:
                pass
    words.add(str(cfg.get("deliverable", "")).lower())
    for k in list(cfg.get("keys") or []) + list((cfg.get("expect") or {}).keys()):
        words.add(str(k).lower())
        words |= set(w.lower() for w in WORD.findall(str(k)))
    return sorted(w for w in (words - STOP) if len(w) >= 4)


def check(cand, ctx_values, h1_max, h2_max, verbose=False, units_override=None):
    slot = os.path.basename(cand)
    seed = os.path.join(cand, "seed")
    test_py = os.path.join(cand, "test.py")
    lb = literal(test_py, "LOAD_BEARING") or []
    cfg = literal(test_py, "CONFIG") or {}
    units = units_override or literal(test_py, "HARVEST_UNITS")
    problems, notes = [], []

    if units is None:
        notes.append("no HARVEST_UNITS declared — the spec claims HARVEST_EXEMPT; a reviewer "
                     "must read that reason, this check cannot")
        return slot, problems, notes, {}

    lines = seed_lines(seed)
    total_lines = sum(len(v) for v in lines.values()) or 1

    # per-unit precomputation
    val_hits, id_hits, derived, indistinct, indistinct_names = {}, {}, [], [], set()
    for u in units:
        name = u["unit"]
        vh = line_hits(lines, bounded(str(u["value"])))
        n = sum(len(v) for v in vh.values())
        if n == 0:
            derived.append(name)
        elif n > INDISTINCT_LINE_FRACTION * total_lines:
            indistinct.append("%s (%r on %d of %d lines)" % (name, u["value"], n, total_lines))
            indistinct_names.add(name)
        val_hits[name] = vh
        id_hits[name] = line_hits(lines, bounded(str(name)))

    scored = [u for u in units if u["unit"] not in indistinct_names]
    denom = len(scored)
    if denom == 0:
        problems.append("every declared unit value is indistinct; nothing is measurable")
        return slot, problems, notes, {}
    if len(indistinct) > INDISTINCT_UNIT_FRACTION * len(units):
        problems.append("%d of %d declared values are indistinct, over the one-third limit: %s"
                        % (len(indistinct), len(units), "; ".join(indistinct[:4])))

    vocab = giveaway_vocabulary(cand, lb, cfg)
    roster = re.compile("|".join(sorted((bounded(str(u["unit"])).pattern for u in units),
                                        key=len, reverse=True)))
    roster_hits = line_hits(lines, roster)

    result = {"units": len(units), "scored": denom, "derived": len(derived),
              "indistinct": len(indistinct), "vocab": len(vocab), "seed_files": len(lines)}
    for c in ctx_values:
        best_tok, best_n, best_units = None, -1, []
        for t in vocab:
            anchor = substring_hits(lines, t)
            if not anchor:
                continue
            got = [u["unit"] for u in scored
                   if harvested(val_hits[u["unit"]], id_hits[u["unit"]], u["path"], anchor, c)]
            if len(got) > best_n:
                best_tok, best_n, best_units = t, len(got), got
        h2_units = [u["unit"] for u in scored
                    if harvested(val_hits[u["unit"]], id_hits[u["unit"]], u["path"],
                                 roster_hits, c)]
        result["h1_c%d" % c] = round(best_n / float(denom), 3)
        result["h1_token_c%d" % c] = best_tok
        result["h2_c%d" % c] = round(len(h2_units) / float(denom), 3)
        if verbose:
            notes.append("C=%d: worst token %r harvests %d/%d (%s); roster harvests %d/%d"
                         % (c, best_tok, best_n, denom, ", ".join(sorted(best_units)[:6]),
                            len(h2_units), denom))

    h1 = result.get("h1_c%d" % CONTEXT)
    h2 = result.get("h2_c%d" % CONTEXT)
    if h1 is not None and h1 >= h1_max:
        problems.append("H1 = %.3f at C=%d on the token %r, the limit is %.3f — one grep on a "
                        "token the prompt or its declared pointers give away reaches that "
                        "fraction of the per-unit values"
                        % (h1, CONTEXT, result["h1_token_c%d" % CONTEXT], h1_max))
    if h2 is not None and h2 >= h2_max:
        problems.append("H2 = %.3f at C=%d, the limit is %.3f — one grep alternating over the "
                        "roster's own unit names reaches that fraction" % (h2, CONTEXT, h2_max))
    notes.append("%d unit(s), %d scored, %d derived (value never stated in seed/), %d "
                 "indistinct; %d giveaway tokens over %d files"
                 % (len(units), denom, len(derived), len(indistinct), len(vocab), len(lines)))
    if derived:
        notes.append("derived units: " + ", ".join(sorted(derived)[:8]))
    return slot, problems, notes, result


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
                if (json.load(fh) or {}).get("round") == "v7r4-harvest":
                    out.append(os.path.join(base, slot))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cands", nargs="*")
    ap.add_argument("--context", type=int, action="append", default=None,
                    help="context windows to report; C=2 is the gated one")
    ap.add_argument("--h1", type=float, default=H1_MAX)
    ap.add_argument("--h2", type=float, default=H2_MAX)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--json", dest="jsonout")
    ap.add_argument("--units-json", help="a JSON file of HARVEST_UNITS, for measuring a "
                                         "candidate built before round four declared them")
    a = ap.parse_args()
    ctx_values = sorted(set(a.context or [0, CONTEXT, 5]) | {CONTEXT})

    cands = candidates(a.cands)
    if not cands:
        print("no round-4 candidates found")
        return 1
    override = None
    if a.units_json:
        with open(a.units_json, encoding="utf-8") as fh:
            override = json.load(fh)
    bad, rows = 0, []
    for cand in cands:
        slot, problems, notes, res = check(cand, ctx_values, a.h1, a.h2, a.verbose,
                                           (override or {}).get(os.path.basename(cand))
                                           if isinstance(override, dict) else override)
        res["slot"] = slot
        res["pass"] = not problems
        rows.append(res)
        head = "harvest clear" if not problems else "%d PROBLEM(S)" % len(problems)
        if res:
            head += "   H1(C2)=%.3f H2(C2)=%.3f" % (res.get("h1_c2", 0.0), res.get("h2_c2", 0.0))
        print("%-20s %s" % (slot, head))
        for n in notes:
            print("    - " + n)
        for p in problems:
            print("    ! " + p)
        if problems:
            bad += 1
    print("\n%d candidate(s), %d failing the grep-harvest check (H1 < %.3f, H2 < %.3f at C=%d)"
          % (len(cands), bad, a.h1, a.h2, CONTEXT))
    if a.jsonout:
        with open(a.jsonout, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(rows, indent=1) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
