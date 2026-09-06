"""n05-main-luna — behaviour 5, the join key must be computed before it is searched.

The task is ordinary release-operations maintenance material.  Human stage labels live in
the component documents, the two inputs to an opaque allocation key live in different kinds
of artifact, and one record per key carries the decision.  No file tabulates the label-to-key
mapping and the decision records deliberately carry no labels.
"""
import os
import re

from .. import common as C

SLOT = "n05-main-luna"
FAMILY = "luna"
MODE = 9
PROJECT = "cinder-parcel"
PACKAGE = "parcel"
CORPUS_SEED = 5105
TARGET_TOKENS = 27000
BAND = "main"
DELIVERABLE = "allocation-report.txt"
SUMMARY = """
Report the human labels of all stages whose computed allocation record has `Disposition:
reroute`, the count of those stages, and the canonical join formula.  The record is found by
multiplying the deployment ordinal in the stage document by the region offset in that stage's
module; the result is a four-digit key used in the allocation-record filename.  The formula,
the two inputs, and the decisions are all stated in the seed material and are not inferred.
"""
BAND_NOTE = """
Main-band corpus generated at 27,000 tokens and overlaid with one join-policy record, one
allocation record per stage, and per-stage ordinal/offset fields; material is measured at build.
"""
SCOPE_GATE = True
MUST_NOT_EXIST = []
PERMITTED_NEW = []

POLICY = "docs/architecture/allocation-keys.md"
ALLOCATION_DIR = "ops/allocation-records"
ORDINAL_ROW = "deployment_ordinal"
OFFSET_CONSTANT = "REGION_OFFSET"
DECISION = "reroute"
FORMULA = "deployment_ordinal * region_offset"

# The overlay gives four stages the positive decision.  The values are only a construction
# plan; facts() reads the resulting files back and derives the reference from them.
_REROUTE = (1, 5, 9, 13)


def _ordinal(i):
    return 10 + 2 * i


def _offset(i):
    # A deterministic permutation keeps filename order from accidentally matching the roster.
    return 101 + 4 * ((7 * i) % 17)


def _join_code(i):
    return _ordinal(i) * _offset(i)


def _record_path(code):
    return "%s/allocation-%04d.md" % (ALLOCATION_DIR, code)


def overlay(ctx):
    corpus = ctx["corpus"]
    assert len(corpus.stages) > max(_REROUTE)
    for i, stage in enumerate(corpus.stages):
        corpus.add_doc_config_row(
            stage, ORDINAL_ROW, _ordinal(i),
            "the deployment sequence number used by the allocator")
        corpus.set_module_constant(stage, OFFSET_CONSTANT, str(_offset(i)))

        code = _join_code(i)
        assert 1000 <= code <= 9999
        disposition = DECISION if i in _REROUTE else "retain"
        body = """# Allocation decision

This record is addressed by the four-digit allocation key in its filename.  It is an
append-only operations record, not a roster: the human stage label is deliberately kept in
the stage material that produced the key.

Disposition: %s
Review: the allocator review for this key is complete.
""" % disposition
        C.write(os.path.join(ctx["seed"], *_record_path(code).split("/")), body)

    policy = """# Allocation keys

## Purpose

The parcel pipeline has several names for the same operational stage.  Component documents
use a human-readable stage label because those pages are read during deployment review.  The
allocation archive uses an opaque four-digit key because keys remain stable when prose labels
are revised.  These are two views of one stage, not two independent rosters.

## Inputs

Every stage document records a `deployment_ordinal` in its configuration table.  Every stage
module records a `REGION_OFFSET` constant.  An ordinal is local to this deployment plan; the
offset is local to the region adapter.  Neither input is an allocation decision, and neither
is copied into the manifest or the operations summary.

## Canonical join rule

The canonical join formula is: deployment_ordinal * region_offset.

The product is written as a four-digit decimal key.  To follow a stage from its human label
to the archive, read both inputs for that stage, perform the multiplication, preserve all
digits of the product, and search for the allocation record whose filename contains that key.
Do not pair records by directory order, by the order of modules, or by the order in which a
reviewer happened to open files.  A record without a computed key is not evidence about any
stage.

## Reading a decision

The allocation record is authoritative for the disposition of the key it names.  `reroute`
means that the stage needs the alternate parcel route; `retain` means that it stays on its
current route.  This page defines the join, not the disposition of any particular stage.

## Maintenance note

When a label changes, update the component page and its normal cross-references.  Do not add a
label-to-key table: the absence of such a table is intentional, since a table copied from one
deployment plan becomes stale when ordinals or region adapters change.  A later reviewer can
reproduce the join from the two inputs and the record name.
"""
    C.write(os.path.join(ctx["seed"], *POLICY.split("/")), policy)
    corpus.append("README.md", """## Allocation review material

The allocation-key policy and its per-key operations records are part of the deployment
review material.  Stage pages and stage modules remain the sources for their local inputs.
""")


def _policy_formula(corpus):
    text = corpus.text(POLICY)
    m = re.search(r"^The canonical join formula is:\s*(.+?)\.\s*$", text, re.M)
    assert m, "canonical join formula is missing"
    return m.group(1).strip()


def _stage_join(corpus, stage):
    ordinal = int(corpus.doc_config_row(stage, ORDINAL_ROW))
    offset = int(corpus.module_constant(stage, OFFSET_CONSTANT))
    code = ordinal * offset
    assert 1000 <= code <= 9999, "%s produced non-four-digit key %d" % (stage["name"], code)
    return ordinal, offset, code


def _decision(corpus, stage, code):
    rel = _record_path(code)
    text = corpus.text(rel)
    m = re.search(r"^Disposition:\s*(\w+)\s*$", text, re.M)
    assert m, "%s has no disposition" % rel
    return m.group(1), rel


def _joined_rows(ctx):
    corpus = ctx["corpus"]
    rows = []
    codes = set()
    for stage in corpus.stages:
        ordinal, offset, code = _stage_join(corpus, stage)
        assert code not in codes, "duplicate allocation key %d" % code
        codes.add(code)
        disposition, rel = _decision(corpus, stage, code)
        rows.append({"stage": stage, "ordinal": ordinal, "offset": offset,
                     "code": code, "disposition": disposition, "record": rel})
    assert len(rows) == len(corpus.stages)
    assert len(codes) == len(rows)
    return rows


def facts(ctx):
    rows = _joined_rows(ctx)
    formula = _policy_formula(ctx["corpus"])
    assert formula == FORMULA
    selected = sorted(r["stage"]["name"] for r in rows if r["disposition"] == DECISION)
    assert selected
    assert len(selected) == len(_REROUTE)
    return {
        "keys": ["reroute_stages", "reroute_count", "join_formula"],
        "expect": {
            "reroute_stages": ", ".join(selected),
            "reroute_count": str(len(selected)),
            "join_formula": formula,
        },
        "kinds": {"reroute_stages": "set", "reroute_count": "int", "join_formula": "ci"},
        "groups": [
            {"name": "stages whose allocation says reroute", "keys": ["reroute_stages"]},
            {"name": "number of reroute stages", "keys": ["reroute_count"]},
            {"name": "canonical join formula", "keys": ["join_formula"]},
        ],
        "selected": selected,
        "rows": rows,
        "formula": formula,
    }


def prompt(ctx):
    return """# Allocation review report

You are working at the root of the `cinder-parcel` checkout.  The stages in
`config/manifest.json` are the complete scope of this review.

Prepare a report of the allocation review.  For every stage, use its human-readable label as
the name you report.  The repository's allocation-key policy explains how to compute the
four-digit key: first obtain that stage's deployment ordinal and region offset, multiply them,
and then search for the allocation record whose filename contains the resulting key.  Read the
record's `Disposition` line.  Do this for every stage; do not match records by directory order,
module order, or opening order.

Report the labels of the stages whose disposition is exactly `reroute`, the number of those
stages, and the canonical join formula stated by the policy; copy the formula verbatim from
the policy, field names and all.  Put the labels in one comma-
separated value; their order is not significant.

Write a new file `allocation-report.txt` in the checkout root with exactly these three keys,
in this order:

    reroute_stages: <comma-separated human stage labels>
    reroute_count: <plain integer>
    join_formula: <the canonical formula>

No header, quotes, explanation, or other lines.  Whitespace around values is not significant.

Do not modify or delete any existing file, and create no file other than the report.
"""


def reference(ctx):
    f = ctx["facts"]["expect"]
    return {DELIVERABLE: "reroute_stages: %s\nreroute_count: %s\njoin_formula: %s\n" % (
        f["reroute_stages"], f["reroute_count"], f["join_formula"])}


def editable(ctx):
    return []


def sweep_paths(ctx):
    corpus = ctx["corpus"]
    out = [POLICY, "config/manifest.json"]
    for stage in corpus.stages:
        _ordinal_value, _offset_value, code = _stage_join(corpus, stage)
        out.extend([stage["doc"], stage["src"], _record_path(code)])
    return out


def load_bearing(ctx):
    corpus = ctx["corpus"]
    rows = _joined_rows(ctx)
    lb = [
        {"path": POLICY, "hop": "rule",
         "why": "states the canonical multiplication rule and rejects positional matching"},
        {"path": "config/manifest.json", "hop": "enumeration", "named_in_prompt": True,
         "why": "the complete roster of human-labeled stages in scope"},
    ]
    # Two complete examples make the three input/join/decision hops concrete while the sweep
    # still declares every file required for the aggregate.
    for r in (rows[1], rows[5]):
        lb.extend([
            {"path": r["stage"]["doc"], "hop": "ordinal",
             "why": "the human-labeled stage's deployment ordinal"},
            {"path": r["stage"]["src"], "hop": "offset",
             "why": "the same stage's region offset"},
            {"path": r["record"], "hop": "decision",
             "why": "the decision reached only through that computed key"},
        ])
    assert len(lb) == 8
    assert len(set(p["hop"] for p in lb)) == 5
    return lb


def _file_order_wrong(ctx):
    """Assign decisions in filename order to labels in manifest order: a plausible shortcut."""
    corpus = ctx["corpus"]
    rows = _joined_rows(ctx)
    decisions = [r["disposition"] for r in sorted(rows, key=lambda r: r["record"])]
    # Keep this explicit rather than relying on a hidden answer: the wrong mapping is computed
    # from the same records, but pairs their lexical filename order with manifest order.
    names = [stage["name"] for stage, decision in zip(corpus.stages, decisions)
             if decision == DECISION]
    return names


def _ordinal_only_wrong(ctx):
    corpus = ctx["corpus"]
    names = []
    for stage in corpus.stages:
        ordinal = int(corpus.doc_config_row(stage, ORDINAL_ROW))
        if os.path.exists(corpus.path(_record_path(ordinal))):
            names.append(stage["name"])
    return names


_PERTURBATIONS = [
    ("no trailing newline", lambda t: t.rstrip("\n")),
    ("two trailing newlines", lambda t: t + "\n"),
    ("CRLF line endings", lambda t: t.replace("\n", "\r\n")),
    ("one leading blank line", lambda t: "\n" + t),
    ("trailing spaces on every line",
     lambda t: "\n".join((line + "  ") if line.strip() else line for line in t.split("\n"))),
]


def probes(ctx):
    f = ctx["facts"]
    ref = reference(ctx)[DELIVERABLE]
    full = "7/7"
    wrong_order = _file_order_wrong(ctx)
    wrong_ordinal = _ordinal_only_wrong(ctx)
    truth = set(f["selected"])
    assert set(wrong_order) != truth
    assert set(wrong_ordinal) != truth
    wrong_a = "reroute_stages: %s\nreroute_count: %d\njoin_formula: %s\n" % (
        ", ".join(wrong_order), len(wrong_order), f["formula"])
    wrong_b = "reroute_stages: %s\nreroute_count: %d\njoin_formula: %s\n" % (
        ", ".join(wrong_ordinal), len(wrong_ordinal), f["formula"])
    cases = [
        {"name": "reference", "files": {DELIVERABLE: ref},
         "verdict": "correct", "score": full},
        {"name": "empty (untouched sandbox)", "verdict": "visibly_failed", "no_traceback": True},
        {"name": "wrong: pair decisions by filename order", "files": {DELIVERABLE: wrong_a},
         "verdict": "confidently_wrong"},
        {"name": "wrong: search with ordinal alone", "files": {DELIVERABLE: wrong_b},
         "verdict": "confidently_wrong"},
        {"name": "shape: keys in the wrong order", "files": {DELIVERABLE:
            "join_formula: %s\nreroute_stages: %s\nreroute_count: %s\n" % (
                f["formula"], f["expect"]["reroute_stages"], f["expect"]["reroute_count"])},
         "verdict": "confidently_wrong"},
    ]
    for name, mutate in _PERTURBATIONS:
        cases.append({"name": "perturb: " + name, "files": {DELIVERABLE: mutate(ref)},
                      "verdict": "correct", "score": full})
    return cases


def notes(ctx, m):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    lb_paths = "\n".join("- `%s` — %s (*%s*)" % (p["path"], p["why"], p["hop"])
                          for p in m["load_bearing"])
    records = len(f["rows"])
    return """# NOTES — %(slot)s (behaviour %(mode)d, rung 0)

## 1. Failure mode

Mode 9 in the round brief's slot table is the non-lexical join task: the model must compute an
opaque key before searching for the record it addresses.  It measures whether a model can carry
an arithmetic join across human labels, a prose rule, and two artifact kinds.

## 2. Distinguishing condition

A model that relies on lexical retrieval or directory order will search the allocation records
directly, pair them with the manifest order, or use an ordinal as if it were already a key.  The
material rules this out: the policy says the key is the product of the per-stage ordinal and
offset, and decision records contain no human labels.  `facts()` measured %(records)d unique
four-digit keys and one record per stage; the positive answer is %(selected)s.

## 3. Why the grader is sound

The grader independently checks existence, UTF-8 readability, exact key order, the stage set,
the count, the formula, and seed integrity/scope.  The set is compared order-insensitively and
the count numerically, while the prompt leaves whitespace unspecified.  Two complete wrong
answers are probed: filename-order pairing and ordinal-only searching.  An untouched workspace
is visibly_failed.  The five whitespace perturbations remain correct.

## 4. Positive or negative

Positive: the report names the stages whose computed records say `reroute`.

## 5. Rung 0 and material necessity

The answer is not stored in one file and no file maps labels to keys.  Every stage document is
needed for its ordinal, every module for its offset, every allocation record for its disposition,
and the policy is needed for the multiplication rule.  The prompt names only the complete roster
pointer, `config/manifest.json`, which is declared `named_in_prompt`; it does not name an answer
holder.  The sweep covers %(sweep)d of %(tokens)d measured seed tokens (%(pct)s%%), so the
generated repository is necessary context rather than prompt decoration.  No prompt word
selectively assembles the eight declared load-bearing paths.

## 6. Load-bearing paths

The declaration has %(lb)d paths across %(hops)d causal hops:

%(lbpaths)s

## 7. Near-miss table

| outcome | result |
| --- | --- |
| reference | correct, full score |
| untouched sandbox | visibly_failed, no traceback |
| filename-order pairing | confidently_wrong |
| ordinal-only search | confidently_wrong |
| swapped key order | confidently_wrong |
| no trailing newline | correct, full score |
| two trailing newlines | correct, full score |
| CRLF line endings | correct, full score |
| one leading blank line | correct, full score |
| trailing spaces | correct, full score |

## 8. Derivability

The reference is derived from `seed/` by multiplying each document's ordinal by its module's
offset, opening the computed record, and reading its disposition; the formula is read from the
policy.  No expected label, count, or key is typed into the reference.
""" % {
        "slot": SLOT, "mode": MODE, "records": records,
        "selected": ", ".join("`%s`" % n for n in f["selected"]),
        "sweep": m["sweep_tokens"], "tokens": m["tokens"],
        "pct": m["sweep_pct"], "lb": len(m["load_bearing"]),
        "hops": len(set(p["hop"] for p in m["load_bearing"])), "lbpaths": lb_paths,
    }
