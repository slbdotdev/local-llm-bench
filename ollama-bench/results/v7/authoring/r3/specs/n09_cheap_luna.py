"""n09-cheap-luna — behaviour 5, premature commitment on a release review.

The first complete answer is a stale release summary. Component documents carry the
per-stage release status and reserved capacity, while a later changelog entry removes one
candidate from that summary. The correction changes the stage list and its capacity total;
the release record and decision remain valid.
"""
import os
import re

from .. import common as C


SLOT = "n09-cheap-luna"
FAMILY = "luna"
MODE = 5
PROJECT = "cinder-parcel"
PACKAGE = "cinder"
CORPUS_SEED = 5909
TARGET_TOKENS = 11000
DELIVERABLE = "release-report.txt"
BAND = "cheap24"
SCOPE_GATE = True
MUST_NOT_EXIST = []
PERMITTED_NEW = []

SUMMARY = """
Task: report the current release stages, their total reserved capacity, the release record,
and the decision. An earlier release summary is complete and plausible, but a later dated
correction changes the first two values. The per-stage release status and capacity are in
the component records; the correction is in the project's dated history.
"""

BAND_NOTE = """
Cheap24 material is generated at 10,000 target tokens and overlaid with component release
records, a complete earlier summary, and one dated correction; the measured seed is required
to land in the 12,000-16,000 token band.
"""

STATUS_KEY = "release_status"
SUMMARY_PATH = "docs/release-summary.md"
CHANGELOG_PATH = "history/CHANGELOG.md"
CORRECTION_MARK = "release review correction"
RECORD = "RR-2036-07"
DECISION = "release"


def _status_plan(corpus):
    """Return the generated stages' initial statuses and capacities."""
    out = []
    for i, stage in enumerate(corpus.stages):
        status = "candidate" if i % 3 != 1 else "deferred"
        capacity = stage["limit"] + 16 + (i % 4) * 8
        out.append((stage, status, capacity))
    return out


def overlay(ctx):
    corpus = ctx["corpus"]

    # This is a new property for every stage, written only in that stage's component
    # document. The shared generator's indexes, history and tests do not carry it.
    plan = _status_plan(corpus)
    for stage, status, capacity in plan:
        corpus.add_doc_config_row(
            stage, STATUS_KEY, "%s:%d" % (status, capacity),
            "release eligibility and reserved capacity from the review worksheet")

    initial = [(s["name"], cap) for s, status, cap in plan if status == "candidate"]
    initial_names = [name for name, _cap in initial]
    initial_total = sum(cap for _name, cap in initial)
    C.write(
        os.path.join(ctx["seed"], *SUMMARY_PATH.split("/")),
        """# Release review summary

This is the completed release review for the July planning window. It records the
candidate set used by the release coordinator at the time of writing.

candidate stages: %s
review record: %s
outcome: %s

The summary was complete when filed. Later dated project history may correct a component
without changing the record identifier or the release decision.
""" % (", ".join(initial_names), RECORD, DECISION))

    # A single late, ordinary changelog entry invalidates one stage in the complete summary.
    # The solver must recompute both dependent fields rather than copy the summary.
    corrected_stage, _status, corrected_capacity = plan[0]
    corpus.append(
        CHANGELOG_PATH,
        """## 2036-07-18 — %s

- Correction: stage [%s] is no longer a release candidate as of 2036-07-18. The release
  record and decision are unchanged.
""" % (CORRECTION_MARK, corrected_stage["name"]))


def _read_status(corpus, stage):
    text = corpus.text(stage["doc"])
    m = re.search(r"^\| \x60%s\x60 \| (\w+):(\d+) \|" % re.escape(STATUS_KEY), text, re.M)
    assert m, "missing %s in %s" % (STATUS_KEY, stage["doc"])
    return m.group(1), int(m.group(2))


def _summary_values(corpus):
    text = corpus.text(SUMMARY_PATH)
    stages = re.search(r"^candidate stages: (.+)$", text, re.M)
    record = re.search(r"^review record: (\S+)$", text, re.M)
    decision = re.search(r"^outcome: (\S+)$", text, re.M)
    assert stages and record and decision, "summary is not complete-looking"
    return stages.group(1).strip(), record.group(1), decision.group(1)


def _correction(corpus):
    text = corpus.text(CHANGELOG_PATH)
    found = re.findall(
        r"Correction: stage \[([^]]+)\] is no longer a release candidate as of "
        r"2036-07-18", text)
    assert len(found) == 1, "expected exactly one release correction"
    return found[0],


def facts(ctx):
    corpus = ctx["corpus"]
    plan = []
    for stage in corpus.stages:
        status, capacity = _read_status(corpus, stage)
        plan.append((stage["name"], status, capacity))
    assert len(plan) == len(corpus.stages) and len(plan) >= 3

    corrected_name = _correction(corpus)[0]
    names = [name for name, status, _cap in plan if status == "candidate"]
    capacities = dict((name, cap) for name, _status, cap in plan)
    assert corrected_name in names
    names.remove(corrected_name)
    total = sum(capacities[name] for name in names)

    stale_names, record, decision = _summary_values(corpus)
    stale_name_list = [x.strip() for x in stale_names.split(",")]
    assert stale_name_list == [name for name, status, _cap in plan if status == "candidate"]
    assert corrected_name in [x.strip() for x in stale_names.split(",")]
    assert record and decision
    assert len(names) >= 1 and total != stale_total

    return {
        "keys": ["release_stages", "reserved_capacity_total", "release_record", "decision"],
        "expect": {
            "release_stages": ", ".join(names),
            "reserved_capacity_total": str(total),
            "release_record": record,
            "decision": decision,
        },
        "kinds": {
            "release_stages": "list",
            "reserved_capacity_total": "int",
            "release_record": "exact",
            "decision": "ci",
        },
        "groups": [
            {"name": "current release stages", "keys": ["release_stages"]},
            {"name": "reserved capacity", "keys": ["reserved_capacity_total"]},
            {"name": "release record", "keys": ["release_record"]},
            {"name": "release decision", "keys": ["decision"]},
        ],
    }


def prompt(ctx):
    return """# Current release report

Determine the current release decision for the project in this working directory. Read the
repository's component records and dated project material, compare an earlier complete
summary with any later correction, and compute the result from the records. The project
manifest gives the complete roster and its order; report stages in that manifest order.

Create exactly one new file, release-report.txt. Do not modify or delete any existing file,
and do not create any other file. The new file must contain exactly these four nonblank keys,
in this order, one key: value line per key:

release_stages: comma-separated stage names, in manifest order
reserved_capacity_total: one integer, in the project's capacity units
release_record: the release record identifier
decision: the current release decision

Use the exact stage names from the material. The stage list is not alphabetized. Do not add
headings, explanations, or extra keys. A complete earlier answer is not necessarily current;
use the dated material to resolve it before writing the report.
"""


def reference(ctx):
    f = ctx["facts"]
    return {
        DELIVERABLE: "release_stages: %s\nreserved_capacity_total: %s\nrelease_record: %s\ndecision: %s\n"
        % (f["expect"]["release_stages"], f["expect"]["reserved_capacity_total"],
           f["expect"]["release_record"], f["expect"]["decision"])
    }


def load_bearing(ctx):
    corpus = ctx["corpus"]
    lb = [
        {"path": "config/manifest.json", "hop": "enumeration", "named_in_prompt": True,
         "why": "the complete roster and its declared order"},
        {"path": SUMMARY_PATH, "hop": "draft",
         "why": "the first complete release answer a reader is expected to find"},
        {"path": CHANGELOG_PATH, "hop": "correction",
         "why": "the later dated line that removes one candidate"},
    ]
    for stage in corpus.stages:
        lb.append({"path": stage["doc"], "hop": "dependent-values",
                   "why": "the component's release eligibility and reserved capacity"})
    return lb


def sweep_paths(ctx):
    # Component records, their corresponding implementations, dated decisions and indexes
    # are the material a complete reconciliation requires. Tests and deferred-stage modules
    # are coherent context but do not carry the release property.
    paths = [p for p in C.walk_rel(ctx["seed"])
             if not (p.startswith("src/") or p.startswith("tests/"))]
    for stage in ctx["corpus"].stages:
        status, _capacity = _read_status(ctx["corpus"], stage)
        if status == "candidate":
            paths.append(stage["src"])
    return paths


def _stale_answer(ctx):
    corpus = ctx["corpus"]
    stages = []
    total = 0
    for stage in corpus.stages:
        status, capacity = _read_status(corpus, stage)
        if status == "candidate":
            stages.append(stage["name"])
            total += capacity
    _stale_names, _stale_total, record, decision = _summary_values(corpus)
    return ("release_stages: %s\nreserved_capacity_total: %d\nrelease_record: %s\n"
            "decision: %s\n" % (", ".join(stages), total, record, decision))


def probes(ctx):
    f = ctx["facts"]
    ref = reference(ctx)[DELIVERABLE]
    full = "8/8"
    stale = _stale_answer(ctx)
    stale_total = sum(
        capacity for stage in ctx["corpus"].stages
        for status, capacity in [_read_status(ctx["corpus"], stage)]
        if status == "candidate"
    )
    corrected = ref.replace(
        "reserved_capacity_total: %s" % f["expect"]["reserved_capacity_total"],
        "reserved_capacity_total: %s" % stale_total)
    wrong_order = ("reserved_capacity_total: %s\nrelease_stages: %s\nrelease_record: %s\n"
                   "decision: %s\n" % (f["expect"]["reserved_capacity_total"],
                                        f["expect"]["release_stages"],
                                        f["expect"]["release_record"], f["expect"]["decision"]))
    perturbations = [
        ("no trailing newline", lambda t: t.rstrip("\n")),
        ("two trailing newlines", lambda t: t + "\n"),
        ("CRLF line endings", lambda t: t.replace("\n", "\r\n")),
        ("one leading blank line", lambda t: "\n" + t),
        ("trailing spaces on every line",
         lambda t: "\n".join((line + "  ") if line.strip() else line
                              for line in t.split("\n"))),
    ]
    cases = [
        {"name": "reference", "files": {DELIVERABLE: ref},
         "verdict": "correct", "score": full},
        {"name": "empty (untouched sandbox)", "verdict": "visibly_failed",
         "no_traceback": True},
        {"name": "wrong: complete earlier summary", "files": {DELIVERABLE: stale},
         "verdict": "confidently_wrong", "score": "6/8"},
        {"name": "wrong: corrected stages but stale capacity", "files": {DELIVERABLE: corrected},
         "verdict": "confidently_wrong", "score": "7/8"},
        {"name": "wrong: keys in the wrong order", "files": {DELIVERABLE: wrong_order},
         "verdict": "confidently_wrong"},
    ]
    for name, mutate in perturbations:
        cases.append({"name": "perturb: " + name, "files": {DELIVERABLE: mutate(ref)},
                      "verdict": "correct", "score": full})
    return cases


def notes(ctx, m):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    corrected_name = _correction(corpus)[0]
    stale_names, _record, _decision = _summary_values(corpus)
    stale_total = sum(
        capacity for stage in corpus.stages
        for status, capacity in [_read_status(corpus, stage)]
        if status == "candidate"
    )
    lb_lines = "\n".join("- %s — %s (%s)" % (entry["path"], entry["why"], entry["hop"])
                          for entry in m["load_bearing"])
    return """# NOTES — %(slot)s (behaviour %(mode)d, rung 0)

## 1. Failure mode

Mode 5, documentation that disagrees with the current project state, used here to measure
premature commitment. The first release summary is complete, coherent and correctly shaped,
but a later dated correction changes two dependent report fields.

## 2. Distinguishing condition

The stale summary names %(stale)s; those candidate rows total %(staletotal)d. The dated
entry removes %(corrected)s from the current release set. A solver that stops at the first
complete-looking answer will therefore get exactly the two unchanged fields right and the
stage list and total wrong. The material makes the update explicit and dated; there is no
judgement call.

The decisive per-stage datum is %(key)s, written once into each component document by the
overlay. It is not echoed by the manifest, indexes, history entries or tests, and no summary
file carries the per-stage capacity values. This is a document row rather than a per-stage
module constant, so DECISIVE_CONSTANT is intentionally not declared. The answer requires
traversing the roster and all component records, then applying the later update.

## 3. Rung 0 and sweep

The prompt names only the deliverable and the project manifest's legitimate roster pointer;
it does not name the summary, changelog, or component-document paths. No file contains the
correct four values together: the summary contains the pre-correction pair, while the
component records and correction must be reconciled. The expected sweep is %(sweep)d of
%(tokens)d measured material tokens (%(pct)s%%), within the intended 60-80%% traversal range.
The modules corresponding to candidate component records are included because each record
points to its implementation and the maintenance sweep verifies that association. Tests and
deferred-stage modules are coherent project context but do not carry the release property and
are not counted in the expected sweep.

## 4. Grader soundness

The grader checks deliverable existence, UTF-8 readability, exact key shape/order, four
independent values, and seed integrity/scope. The four groups separate the two fields changed
by the correction from the two fields that remain unchanged. The stale summary is a complete
wrong-but-plausible answer and scores 6/8; keeping its capacity with the corrected stage list
scores 7/8. An untouched sandbox is visibly_failed. No edit perturbation is legitimate.

## 5. Positive or negative

Positive: at least one stage remains in the corrected release set, so an untouched empty report
cannot pass by luck.

## 6. Load-bearing declaration

%(lb)s

The declaration has %(lbcount)d paths across %(hopcount)d causal hops; the correction is one
hop, and the per-stage records are the dependent-values hop for the two changed keys.

## 7. Near-miss table

| case | expected result |
| --- | --- |
| reference | correct, 8/8 |
| untouched sandbox | visibly_failed |
| complete earlier summary | confidently_wrong, 6/8 |
| corrected stages with stale capacity | confidently_wrong, 7/8 |
| keys in wrong order | confidently_wrong |
| no trailing newline | correct, 8/8 |
| two trailing newlines | correct, 8/8 |
| CRLF line endings | correct, 8/8 |
| one leading blank line | correct, 8/8 |
| trailing spaces | correct, 8/8 |

Every asserted answer value is derived from the component rows, the dated correction and the
summary's unchanged record/decision while building from seed/; no reference answer value is
typed independently of the material.
""" % {
        "slot": SLOT, "mode": MODE, "stale": stale_names, "staletotal": stale_total,
        "corrected": corrected_name, "key": STATUS_KEY,
        "sweep": m["sweep_tokens"], "tokens": m["tokens"], "pct": m["sweep_pct"],
        "lb": lb_lines, "lbcount": len(m["load_bearing"]),
        "hopcount": len(set(x["hop"] for x in m["load_bearing"])),
    }
