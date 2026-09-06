"""n03-main-luna: resolve a three-way capacity disagreement by a prose tiebreak.

The generated project contains up to one independently written handoff capacity in each stage
document, module, and migration row.  The engineering record gives the precedence for the
row's neutral resolution class.  The answer is computed from all stages, rather than being
stored in one report-shaped artifact.
"""
import csv
import hashlib
import io
import os
import re

from .. import common as C


SLOT = "n03-main-luna"
FAMILY = "luna"
MODE = 5
PROJECT = "cinder-arch"
PACKAGE = "cinder"
CORPUS_SEED = 5303
TARGET_TOKENS = 26500
BAND = "main"
DELIVERABLE = "handoff-report.txt"
SUMMARY = """
Task: resolve the project's handoff_capacity disagreement for every stage.  Each stage has up to
three independently written values, plus a neutral resolution class.  An engineering record
states the precedence for each class, including a named exception where the migration row
outranks the module.  Report the effective value and selected source for every stage, their
total, and the artifact kind that governs the exception.
"""
BAND_NOTE = """
Generated at 26,500 tokens and overlaid with hash-derived per-stage values, selected absent
records, and a prose engineering ruling; the built seed is measured into the main-band interval.
"""
SCOPE_GATE = True
MUST_NOT_EXIST = []
PERMITTED_NEW = []

# The checker treats this as the per-stage decisive module constant.  Its numeric values are
# deliberately not copied into any index or summary file; the other two values differ.
DECISIVE_CONSTANT = "HANDOFF_CAPACITY"

ROW_KEY = "handoff_capacity"
LEDGER = "data/handoff-capacity-ledger.csv"
RECORD = "docs/engineering/capacity-resolution.md"

_CLASSES = ("amber", "indigo", "slate")
_EXCEPTION_CLASS = "slate"
_SOURCE_NAMES = {
    "component document": "document",
    "Python module constant": "module",
    "migration ledger": "migration-ledger",
}
_DISPLAY_SOURCE = {"document": "document", "module": "implementation",
                   "migration-ledger": "migration-ledger"}


def _stage_hash(name):
    """A stable per-stage digest, independent of manifest position."""
    return hashlib.sha256(name.encode("utf-8")).digest()


def _capacity(stage, base):
    # The disjoint ranges keep the three sources visibly plausible but distinct.  The
    # digest, rather than the manifest index, supplies the per-stage variation.
    return base + (int.from_bytes(_stage_hash(stage["name"])[0:8], "big") % 211)


def _missing_source(stage):
    """Return the source whose per-stage record is intentionally unavailable, or None."""
    return ("document", "module", "migration-ledger", None)[
        int.from_bytes(_stage_hash(stage["name"])[2:4], "big") % 4]


def _plan(corpus):
    """Assign neutral resolution classes in a stable hash order."""
    ordered = sorted(corpus.stages, key=lambda s: _stage_hash(s["name"]))
    return {stage["name"]: _CLASSES[i % len(_CLASSES)]
            for i, stage in enumerate(ordered)}


def overlay(ctx):
    corpus = ctx["corpus"]
    classes = _plan(corpus)

    # The three values are all plausible capacities, but each is in a different artifact kind.
    # None is copied to a summary.  The module values are also outside the generator's legacy
    # range, so the index-leak check cannot mistake an old generated value for this datum.
    ledger_rows = ["stage,property,resolution_class,capacity,recorded_on,operator_note"]
    for i, stage in enumerate(corpus.stages):
        missing = _missing_source(stage)
        doc_value = _capacity(stage, 900)
        module_value = _capacity(stage, 700)
        ledger_value = _capacity(stage, 1100)
        if missing != "document":
            corpus.append(
                stage["doc"],
                """\n## Per-stage handoff review\n\nFor the `%s` stage, the component owner's reviewed transfer ceiling is **%d** units.\nThis per-stage figure is recorded in the document narrative for reconciliation.\n""" % (stage["name"], doc_value))
        if missing != "module":
            corpus.set_module_constant(stage, DECISIVE_CONSTANT, str(module_value))
        if missing == "migration-ledger":
            capacity_cell = ""
            note = "no migration capacity was recorded for this stage"
        else:
            capacity_cell = str(ledger_value)
            note = "capacity migration review recorded this value"
        ledger_rows.append(
            "%s,%s,%s,%s,2035-%02d-%02d,%s"
            % (stage["name"], ROW_KEY, classes[stage["name"]], capacity_cell,
               1 + (i % 9), 2 + ((i * 3) % 26), note))

    C.write(os.path.join(ctx["seed"], *LEDGER.split("/")),
            "\n".join(ledger_rows) + "\n")
    _write_record(ctx)
    corpus.append("README.md", _readme_addendum())


def _write_record(ctx):
    # This is intentionally prose rather than a machine-readable policy table.  The record
    # has enough ordinary reasoning around the decisive paragraph to make source plausibility
    # and recency tempting, while the facts reader extracts and checks the paragraph itself.
    lines = [
        "# Capacity reconciliation record CR-27",
        "",
        "- Status: **in force**",
        "- Applies to: every stage named by the repository's current assembly manifest",
        "- Supersedes: CR-19 (the module was treated as authoritative for all handoffs)",
        "",
        "## Purpose",
        "",
        "The platform team has found three honest records of a stage's handoff capacity. The",
        "component owner writes a capacity in the stage document, the implementation carries a",
        "capacity in its Python module, and the migration operator records a capacity when the",
        "handoff review is performed. They are often edited at different points in a rollout.",
        "A disagreement is therefore evidence to reconcile, not permission to choose the value",
        "that appears newest or the value that looks most operationally plausible.",
        "",
        "The property covered by this record is `handoff_capacity`. The migration row also carries",
        "a resolution class. That class is metadata about how the three records are to be read",
        "and is not itself a fourth capacity. Do not infer a class from the order of the files,",
        "from the date, or from which team owns the artifact.",
        "",
        "## What the three records mean",
        "",
        "A component document is the owner's stated operating expectation. The Python module",
        "constant is the value the implementation has been configured to use. The migration",
        "ledger is the operator's value recorded during the reconciliation exercise. All three",
        "are retained because each explains a different part of a disagreement.",
        "",
        "The ledger is not generally stronger merely because it has a date. A date orders",
        "events; it does not change the precedence that this record sets out below. Likewise,",
        "the module is not generally stronger merely because it controls runtime behaviour.",
        "The report must apply the class attached to each stage's migration row.",
        "",
        "## Resolution rules",
        "",
        "The labels amber, indigo, and slate are neutral labels defined only by the rules below.",
        "They do not identify an artifact kind, a team, or a preferred source by themselves.",
        "",
        "Rule amber: for `handoff_capacity`, precedence is component document, then Python",
        "module constant, then migration ledger.",
        "",
        "Rule indigo: for `handoff_capacity`, precedence is Python module constant, then",
        "component document, then migration ledger.",
        "",
        "Rule slate: for `handoff_capacity`, precedence is migration ledger, then Python",
        "module constant, then component document.",
        "",
        "The slate rule is the only exception: the migration ledger outranks the Python",
        "module constant only for the named `handoff_capacity` property. No other property in",
        "the repository receives that treatment. The exception is about the property name, not",
        "about a particular stage, operator, date, or directory.",
        "",
        "The words *first*, *then*, and *last* above describe precedence, not an instruction to",
        "edit anything. If a stage has no record of the kind named at one position, continue",
        "to the next available kind in that class's order; an absent record is not a zero.",
        "",
        "## Reporting convention",
        "",
        "A capacity resolution is a reading of the repository at the time of the review. It",
        "does not repair the document or module, and it does not rewrite the migration ledger.",
        "The report names the selected source for each stage so a later operator can explain",
        "why two records were not selected. The total is the sum of the selected effective",
        "capacities, not the sum of all three copies and not the sum of legacy limits.",
        "",
        "Stage names in a report are written in alphabetical order. This is a presentation",
        "convention only; the class remains attached to the stage named by its own ledger row.",
        "",
        "## Review history",
        "",
        "CR-19 treated the implementation as the answer and caused owner documentation to drift.",
        "CR-22 tried to use the latest recorded value, which made a later review overwrite an",
        "earlier decision without explaining the change. Both records remain as history because",
        "they explain why this record calls out precedence explicitly.",
        "",
        "The current record was approved after the capacity migration review. Its status is in",
        "force, and its three class rules are the governing interpretation for this report.",
        "",
        "## Terms retained for searchability",
        "",
        "A legacy limit is a generated assembly setting and is not a handoff capacity. A",
        "window is a timeout and is not a precedence class. A review date is evidence about",
        "when a row was recorded and is not a fourth source. These terms appear in nearby",
        "material because operators routinely confuse them with the property in this record.",
        "",
    ]
    C.write(os.path.join(ctx["seed"], *RECORD.split("/")), "\n".join(lines))


def _readme_addendum():
    return """## Capacity reconciliation

The engineering record for capacity reconciliation explains how a component document, Python
module, and migration ledger may disagree. The current migration ledger retains one
`handoff_capacity` row for each stage and records its resolution class. The record's prose is
the authority for selecting among those three sources.
"""


def _read_rules(corpus):
    """Parse the three precedence rules from the engineering record on disk."""
    text = C.read(corpus.path(RECORD))
    rules = {}
    # The record is intentionally formatted as ordinary wrapped prose.  Join its physical
    # lines before extracting the three complete sentences so wrapping cannot become a hidden
    # part of the task's semantics.
    flat = " ".join(text.splitlines())
    pattern = re.compile(
        r"Rule (amber|indigo|slate): .*?precedence is (.+?)\.")
    aliases = {
        "component document": "document",
        "Python module constant": "module",
        "migration ledger": "migration-ledger",
    }
    for match in pattern.finditer(flat):
        names = [x.strip() for x in match.group(2).split(", then ")]
        assert len(names) == 3, "rule does not name three sources: %s" % match.group(0)
        assert all(x in aliases for x in names), "unknown source in rule: %s" % names
        rules[match.group(1)] = [aliases[x] for x in names]
    assert set(rules) == set(_CLASSES), "record did not provide all three resolution rules"
    assert rules["amber"] == ["document", "module", "migration-ledger"]
    assert rules["indigo"] == ["module", "document", "migration-ledger"]
    assert rules["slate"] == ["migration-ledger", "module", "document"]
    exception = re.search(
        r"only exception: the migration ledger outranks the Python module constant only for "
        r"the named `([^`]+)` property", flat)
    assert exception and exception.group(1) == ROW_KEY, "exception prose is not present"
    return rules, exception.group(1)


def _ledger_values(corpus):
    rows = list(csv.DictReader(io.StringIO(C.read(corpus.path(LEDGER)))))
    assert rows and all(set(("stage", "property", "resolution_class", "capacity",
                             "recorded_on", "operator_note")) <= set(r) for r in rows)
    out = {}
    for row in rows:
        assert row["property"] == ROW_KEY
        assert row["resolution_class"] in _CLASSES
        assert row["stage"] in corpus.by_name
        assert row["stage"] not in out, "duplicate migration row for %s" % row["stage"]
        value = row["capacity"].strip()
        out[row["stage"]] = {"class": row["resolution_class"]}
        if value:
            out[row["stage"]]["value"] = int(value)
    assert set(out) == set(s["name"] for s in corpus.stages)
    assert len(rows) == len(corpus.stages)
    return out


def _values(corpus):
    """Read all three artifact kinds and the row class for every stage."""
    ledger = _ledger_values(corpus)
    rules, exception_property = _read_rules(corpus)
    values = {}
    for stage in corpus.stages:
        name = stage["name"]
        doc_text = corpus.text(stage["doc"])
        doc_match = re.search(
            r"^For the `%s` stage, the component owner's reviewed transfer ceiling is "
            r"\*\*(\d+)\*\* units\.$" % re.escape(name), doc_text, re.M)
        doc = int(doc_match.group(1)) if doc_match else None
        module_text = corpus.module_constant(stage, DECISIVE_CONSTANT)
        module = int(module_text) if module_text is not None else None
        row = ledger[name]
        csv_value = row.get("value")
        present = {"document": doc, "module": module, "migration-ledger": csv_value}
        available = [source for source, value in present.items() if value is not None]
        assert len(available) >= 2, "too few records for %s" % name
        assert len(set(present[source] for source in available)) == len(available), \
            "present values do not disagree for %s" % name
        chosen = next((source for source in rules[row["class"]]
                       if present[source] is not None), None)
        assert chosen is not None, "no available source for %s" % name
        values[name] = {
            "class": row["class"],
            "chosen": chosen,
        }
        values[name].update((source, value) for source, value in present.items()
                            if value is not None)
    class_counts = [sum(1 for v in values.values() if v["class"] == kind)
                    for kind in _CLASSES]
    assert min(class_counts) > 0 and max(class_counts) - min(class_counts) <= 1
    return values, exception_property


def _answer(ctx, selection):
    corpus = ctx["corpus"]
    pairs = []
    sources = []
    total = 0
    for name in sorted(selection):
        item = selection[name]
        value = item[item["chosen"]]
        pairs.append("%s=%d" % (name, value))
        sources.append("%s=%s" % (name, _DISPLAY_SOURCE[item["chosen"]]))
        total += value
    return pairs, sources, total


def facts(ctx):
    corpus = ctx["corpus"]
    values, exception_property = _values(corpus)
    rules, _ = _read_rules(corpus)
    pairs, sources, total = _answer(ctx, values)
    assert len(pairs) == len(corpus.stages)
    assert total == sum(values[n][values[n]["chosen"]] for n in values)
    source_totals = {
        source: sum(item.get(source, 0) for item in values.values())
        for source in ("document", "module", "migration-ledger")}
    assert all(source_totals[source] != total for source in source_totals)
    exception_source = rules[_EXCEPTION_CLASS][0]
    assert exception_source == "migration-ledger"
    return {
        "keys": ["effective_handoff_capacity", "effective_source_by_unit",
                 "effective_handoff_capacity_total", "exception_governing_artifact"],
        "expect": {
            "effective_handoff_capacity": ", ".join(pairs),
            "effective_source_by_unit": ", ".join(sources),
            "effective_handoff_capacity_total": str(total),
            "exception_governing_artifact": "migration ledger",
        },
        "kinds": {
            "effective_handoff_capacity": "list",
            "effective_source_by_unit": "list",
            "effective_handoff_capacity_total": "int",
            "exception_governing_artifact": "ci",
        },
        "groups": [
            {"name": "the effective handoff capacity for every stage",
             "keys": ["effective_handoff_capacity"]},
            {"name": "the selected source for every stage",
             "keys": ["effective_source_by_unit"]},
            {"name": "the total effective handoff capacity",
             "keys": ["effective_handoff_capacity_total"]},
            {"name": "the artifact governing the exception",
             "keys": ["exception_governing_artifact"]},
        ],
        "values": values,
        "exception_property": exception_property,
    }


def prompt(ctx):
    return """# Resolve the handoff capacity records

You are working in the root of the `%s` repository. Produce a capacity resolution for every
unit named by the repository's current manifest. The repository contains up to three records of
the same `handoff_capacity` property for each unit: a component document, a Python implementation
constant, and a migration row. The migration row also gives a resolution class; some individual
records are absent. Find the engineering record that defines the neutral class labels and their
precedence, then apply that prose exactly, continuing to the next available record when needed.
Do not choose by file order, date, or which source seems more plausible.

Write a new file `%s` in the repository root. It must contain exactly these four lines, in this
order:

    effective_handoff_capacity: <name=value pairs, alphabetical by name, separated by commas>
    effective_source_by_unit: <name=source pairs in the same order>
    effective_handoff_capacity_total: <sum of the selected values, as a plain integer>
    exception_governing_artifact: <the artifact kind named by the governing record for the
    named exception property>

For source values, use exactly one of `document`, `implementation`, or `migration-ledger`, as
appropriate to the selected artifact. Use the unit names exactly as written in the repository.
A pair is `name=value` with no spaces around `=`. The two pair lists must use the same alphabetical name
order. The artifact-kind value must use the governing record's own concise wording, not a path
or an explanation.

Do not modify or delete any existing file, and create no file other than `%s`. Work until the
four-line report is complete, then stop.
""" % (PROJECT, DELIVERABLE, DELIVERABLE)


def reference(ctx):
    f = ctx["facts"]
    return {DELIVERABLE:
            "effective_handoff_capacity: %s\n"
            "effective_source_by_unit: %s\n"
            "effective_handoff_capacity_total: %s\n"
            "exception_governing_artifact: %s\n" %
            (f["expect"]["effective_handoff_capacity"],
             f["expect"]["effective_source_by_unit"],
             f["expect"]["effective_handoff_capacity_total"],
             f["expect"]["exception_governing_artifact"])}


def editable(ctx):
    return []


def sweep_paths(ctx):
    corpus = ctx["corpus"]
    paths = [RECORD, LEDGER, "config/manifest.json"]
    for stage in corpus.stages:
        paths.extend([stage["doc"], stage["src"]])
    return paths


def load_bearing(ctx):
    corpus = ctx["corpus"]
    lb = [
        {"path": RECORD, "hop": "precedence",
         "why": "the engineering record states the prose tiebreak for all three classes"},
        {"path": LEDGER, "hop": "enumeration",
         "why": "one migration row per stage carries the class and a possible ledger value"},
        {"path": "config/manifest.json", "hop": "enumeration", "named_in_prompt": True,
         "why": "the repository's current roster defines the stages in scope"},
    ]
    # The full traversal remains in sweep_paths.  LOAD_BEARING is a concise causal sample:
    # representative stage documents and modules, plus the shared rule, roster, and row
    # artifacts.  This avoids turning generic words such as "document" into a rung-0 shortcut.
    for stage in corpus.stages[:3]:
        lb.append({"path": stage["doc"], "hop": "document-value",
                   "why": "the component document's handoff capacity for %s" % stage["name"]})
        lb.append({"path": stage["src"], "hop": "module-value",
                   "why": "the Python module's handoff capacity for %s" % stage["name"]})
    return lb


def _render(ctx, values, force_source=None):
    chosen = {}
    priority = {
        "document": ["document", "module", "migration-ledger"],
        "module": ["module", "document", "migration-ledger"],
        "migration-ledger": ["migration-ledger", "module", "document"],
    }
    for name, item in values.items():
        copy = dict(item)
        if force_source:
            copy["chosen"] = next(source for source in priority[force_source]
                                  if source in copy)
        chosen[name] = copy
    pairs, sources, total = _answer(ctx, chosen)
    return ("effective_handoff_capacity: %s\n"
            "effective_source_by_unit: %s\n"
            "effective_handoff_capacity_total: %d\n"
            "exception_governing_artifact: migration ledger\n" %
            (", ".join(pairs), ", ".join(sources), total))


_PERTURBATIONS = [
    ("no trailing newline", lambda text: text.rstrip("\n")),
    ("two trailing newlines", lambda text: text + "\n"),
    ("CRLF line endings", lambda text: text.replace("\n", "\r\n")),
    ("one leading blank line", lambda text: "\n" + text),
    ("trailing spaces on every line",
     lambda text: "\n".join((line + "  ") if line.strip() else line
                             for line in text.split("\n"))),
]


def probes(ctx):
    f = ctx["facts"]
    ref = reference(ctx)[DELIVERABLE]
    values = f["values"]
    full = "8/8"
    # Each alternative is a complete, ordered answer.  It earns only the deliverable,
    # readability, shape, and the exception-source group; the three selected-value groups
    # are independently wrong for two thirds of the rotating classes.
    wrong_document = _render(ctx, values, "document")
    wrong_module = _render(ctx, values, "module")
    wrong_ledger = _render(ctx, values, "migration-ledger")
    cases = [
        {"name": "reference", "files": {DELIVERABLE: ref},
         "verdict": "correct", "score": full},
        {"name": "empty (untouched sandbox)", "verdict": "visibly_failed",
         "no_traceback": True},
        {"name": "wrong: document preferred for every class",
         "files": {DELIVERABLE: wrong_document}, "verdict": "confidently_wrong"},
        {"name": "wrong: module preferred for every class",
         "files": {DELIVERABLE: wrong_module}, "verdict": "confidently_wrong"},
        {"name": "wrong: migration row preferred for every class",
         "files": {DELIVERABLE: wrong_ledger}, "verdict": "confidently_wrong"},
        {"name": "shape: source list in the wrong order", "verdict": "confidently_wrong",
         "files": {DELIVERABLE: ref.replace(
             "effective_source_by_unit: ", "effective_source_by_unit: ", 1)
             .replace("effective_handoff_capacity: ", "effective_handoff_capacity: ", 1)}},
    ]
    # Replace the last case's content explicitly so it remains a real shape near miss rather
    # than relying on a no-op replacement above.
    names = f["expect"]["effective_source_by_unit"]
    pairs = f["expect"]["effective_handoff_capacity"]
    total = f["expect"]["effective_handoff_capacity_total"]
    cases[-1]["files"][DELIVERABLE] = (
        "effective_handoff_capacity: %s\n"
        "effective_source_by_unit: %s\n"
        "effective_handoff_capacity_total: %s\n"
        "exception_governing_artifact: migration ledger\n" % (pairs, names, total))
    # The explicit order is fixed by the prompt, so the shape probe swaps the first two keys.
    cases[-1]["files"][DELIVERABLE] = (
        "effective_source_by_unit: %s\n"
        "effective_handoff_capacity: %s\n"
        "effective_handoff_capacity_total: %s\n"
        "exception_governing_artifact: migration ledger\n" % (names, pairs, total))
    for name, mutate in _PERTURBATIONS:
        cases.append({"name": "perturb: " + name, "files": {DELIVERABLE: mutate(ref)},
                      "verdict": "correct", "score": full})
    return cases


def notes(ctx, m):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    values = f["values"]
    counts = {kind: sum(1 for v in values.values() if v["class"] == kind)
              for kind in _CLASSES}
    missing = {source: sum(1 for v in values.values() if source not in v)
               for source in ("document", "module", "migration-ledger")}
    lb_paths = "\n".join("- `%s` — %s (*%s*)" %
                          (entry["path"], entry["why"], entry["hop"])
                          for entry in m["load_bearing"])
    return """# NOTES — %(slot)s (behaviour %(mode)d, rung 0)

## 1. Failure mode

Mode 5, documentation that disagrees with the code, extended to a three-way disagreement with
a prose tiebreak. It measures whether a model can organize conflicting evidence by the stated
source-of-truth rule instead of selecting the newest, most familiar, or most operationally
plausible artifact.

The public design shape is a three-source precedence reconciliation, used here only as design
inspiration. The data and wording are ordinary capacity-review material authored for this
project.

## 2. Distinguishing condition

Each stage has at least two different `handoff_capacity` values. The markdown component document,
Python module constant, and CSV migration row each carry a possible value, and the CSV row alone
carries the neutral resolution class. The in-force engineering record says which source wins for
each class and how to fall back when one is absent. A model that follows artifact plausibility
instead of the record will commonly choose the document for all stages, the module for all
stages, or the latest migration value for all stages. The material rules those courses out by
stating the three class-specific orders and that the slate order is an exception only for
`handoff_capacity`.

The neutral classes occur %(amber)d, %(indigo)d, and %(slate)d times respectively among
%(nstages)d stages. Missing per-stage records are document=%(docmiss)d, module=%(modmiss)d, and
migration-ledger=%(ledmiss)d. The final answer is positive: it reports one selected value and
source for every stage.

## 3. Why the grader is sound

There are eight independent subchecks: the deliverable exists, is readable as UTF-8, and has
the four keys in the stated order and shape; then one group checks all selected capacities, one
checks all selected sources, one checks their total, and one checks the artifact governing the
exception. The integrity/scope check keeps every seed file unchanged and rejects any unrelated
file. A wrong precedence rule is a complete, well-formed report but fails the relevant value,
source, and total groups, so it is `confidently_wrong` rather than visibly incomplete.

The reference is generated from the seed after the overlay. It reads each available per-stage
prose figure, module constant, and ledger value, parses the three precedence sentences and
fallback rule from the record, and asserts that available values differ and that class counts
are balanced. The total is computed by summing the selected values. No report value is asserted
from a fact absent from the seed.

## 4. Rung 0: why the material is necessary

No seed file holds the answer. The record gives only the precedence rules; the ledger gives the
stage roster rows, class, and a possible value; each component document gives a possible second
value; and each module gives a possible third value. The output combines the winning available
value and source for every stage and then sums them. The values are hash-derived and intentionally
different; the fresh module constants are not echoed into any index, history, test, or summary
artifact; `r3/check_index_leak.py` verifies the module constant appears only in its own stage
module.

The prompt gives the scope as every stage in the current manifest, which is the one legitimate
roster pointer and is declared `named_in_prompt` in `LOAD_BEARING`. It names no answer-bearing
path and no value. A selective grep over prompt vocabulary cannot assemble the answer because
the three values use different artifact-specific names and the class-to-source mapping is prose.

The sweep covers %(sweeptok)d of %(tokens)d measured material tokens (%(sweeppct)s%%): the
engineering record, migration ledger, manifest roster, and every stage document and module.
That traversal is necessary because the selected source depends on each row's neutral class and
available records, and the report must aggregate all stages.

## 5. Load-bearing table

`test.py` declares %(nlb)d load-bearing paths across %(nhops)d causal hops; the acceptance gate
requires at least six paths and three hops, and must touch at least five paths.

%(lb)s

## 6. Near-miss table

The reference scores 8/8 with `PASS` and `VERDICT correct`. The untouched sandbox is
`visibly_failed` without a traceback. Three complete but wrong answers — document, module, or
migration row preferred for every class — are `confidently_wrong`. The swapped key order is also
`confidently_wrong`. No scope-forbidden near-miss is applicable to mode 5.

All five unspecified formatting perturbations pass 8/8 and remain `correct`: no trailing
newline, two trailing newlines, CRLF, one leading blank line, and trailing spaces. The prompt
fixes key order and pair order, so those order changes are intentionally not formatting
perturbations and fail.

## 7. Budget and derivability

This is not mode 8. The reference is %(reflen)d characters and is under the output limit. Every
value it asserts is derived from seed files: the available per-stage values from the three
artifact kinds, the winning source from the three rule sentences, each row's class, and fallback
availability, the total from those winners, and the exception artifact from the record's explicit
exception paragraph.
""" % {
        "slot": SLOT, "mode": MODE, "amber": counts["amber"],
        "indigo": counts["indigo"], "slate": counts["slate"],
        "docmiss": missing["document"], "modmiss": missing["module"],
        "ledmiss": missing["migration-ledger"],
        "nstages": len(corpus.stages), "sweeptok": m["sweep_tokens"],
        "tokens": m["tokens"], "sweeppct": m["sweep_pct"],
        "nlb": len(m["load_bearing"]),
        "nhops": len(set(x["hop"] for x in m["load_bearing"])),
        "lb": lb_paths, "reflen": len(reference(ctx)[DELIVERABLE]),
    }
