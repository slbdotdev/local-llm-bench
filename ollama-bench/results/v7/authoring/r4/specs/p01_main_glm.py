"""p01-main-glm — behaviour 1, the requirement stated once, far from the code.

Research section 5, slot p01: a compatibility requirement appears once in an old release
rationale; the nearby README-and-operations story plausibly describes the opposite course.
The deliverable is `compatibility-report.txt` with `required_behavior`,
`affected_components`, `authoritative_record` and `regression_evidence`.

Public shapes adapted (plan section 3.2, design shape only, never data): **LoCoDiff**'s
reconstruct-the-state-from-records shape — the report's per-component facts are replayed out
of each component's own records and are stated nowhere — and **NoLiMa**'s semantic bridge:
the prompt's "the promise" is never named by any file the prompt points at; the reader walks
README -> release notes -> rationale to find the one sentence that carries it.

Rung 0, and this round's property: no per-component answer datum is a constant on a line.
The horizon of a component (the date its newest acknowledged delivery stopped being
protected) is computed from its own table by the term the promise fixes, and the date
string occurs nowhere under `seed/` — a grep can pull every raw record onto one screen and
still hold no answer, which is research section 2.2's mechanism and the strongest answer
the harvest check knows.
"""
import datetime
import os
import re

from .. import common as C

SLOT = "p01-main-glm"
FAMILY = "glm"
MODE = 1
PROJECT = "quayside-shuttle"
PACKAGE = "quay"
CORPUS_SEED = 5207
TARGET_TOKENS = 26000
DELIVERABLE = "compatibility-report.txt"
SCOPE_GATE = True

SUMMARY = """
Task: find the compatibility promise the project made its clients — stated exactly once,
in the release 2.0 rationale, nowhere else — and report which components' own records show
a store cleared of a delivery while the promise still protected it, the record's
identifier, the term as the record words it, and, for every component in scope, the date
its newest acknowledged delivery stopped being protected. The per-component facts are
derived from each component's acknowledged-deliveries table (its page under docs/) and its
sweep-waterline line (its module under src/); neither the horizons nor the membership set
is stated in any file.
"""

BAND_NOTE = """
Corpus generated at 26,000 tokens and hand-overlaid to land inside the 29,000-36,000 main
band. The overlay is deliberately fat per component — every component page gains an
acknowledged-deliveries table and every module gains a sweep-state block — because the
per-component records ARE the material this round's property is bought with. The measure is
a deterministic character count over seed/, so it cannot drift.
"""

# ---------------------------------------------------------------------------
# the shape of the answer, and where each hop lives
# ---------------------------------------------------------------------------
RELEASES = "docs/releases"
RATIONALE = RELEASES + "/rel-2032-11.md"      # carries the promise; "in force"
SUPERSEDED = RELEASES + "/rel-2031-02.md"     # release 1.4's fourteen-day term, superseded
LATEST_NOTE = RELEASES + "/rel-2033-05.md"    # release 2.2; changes nothing in the promise
README = "README.md"
CHANGELOG = "history/CHANGELOG.md"
MANIFEST = "config/manifest.json"

RECORD_ID = "REL-2032-11"
DECOY_ID = "REL-2031-02"
LATEST_ID = "REL-2033-05"
TERM_PHRASE = "thirty-day replay term"
DECOY_PHRASE = "fourteen-day replay term"
TERM_DAYS = 30
RULING_CLAUSE = "is not compatible with this release"
ACK_SECTION = "Acknowledged deliveries"
ROWS_PER_STAGE = 6

_ACK_ROW = re.compile(r"^\| (DLV-\d+) \| (\d{4}-\d{2}-\d{2}) \|$", re.M)
_SWEEP_LINE = re.compile(r"last sweep (\d{4}-\d{2}-\d{2}), cleared through (\d{4}-\d{2}-\d{2})")


def _iso(d):
    return d.isoformat()


def _plus_s(iso, days):
    d = datetime.date(*[int(x) for x in iso.split("-")])
    return _iso(d + datetime.timedelta(days=days))


# ---------------------------------------------------------------------------
# the per-component plan, deterministic from the stage's position in the manifest.
#
# Category 0: the sweep has not reached this stage's acknowledgements at all
#             (waterline older than its oldest delivery) — trivially compliant.
# Category 1: the sweep cleared everything, and its newest delivery's term had
#             already run (waterline at newest + 33..41) — compliant.
# Category 2: the sweep cleared everything while the newest delivery was still
#             protected (waterline at newest + 3 or + 15, both inside the term,
#             and the +15 stage is lawful under the superseded fourteen-day term,
#             which is what the decoy course gets wrong) — NOT compliant.
# ---------------------------------------------------------------------------
def _plan(corpus):
    st = corpus.stages
    n = len(st)
    assert 12 <= n <= 21, ("this design wants a dozen-plus components and a waterline that "
                           "cannot collide with a horizon, which needs n <= 21: got %d" % n)
    newest0 = datetime.date(2034, 12, 24)
    recs = []
    for i, s in enumerate(st):
        newest = newest0 - datetime.timedelta(days=i)
        acks = [(5110 + 10 * i + j, newest - datetime.timedelta(days=11 * j + i % 5))
                for j in range(ROWS_PER_STAGE)]
        recs.append({"stage": s, "acks": acks, "cat": i % 3})
    horizons = set(_plus_s(_iso(r["acks"][0][1]), TERM_DAYS) for r in recs)
    taken = set(horizons)
    for i, rec in enumerate(recs):
        newest = rec["acks"][0][1]
        if rec["cat"] == 0:
            wl = newest - datetime.timedelta(days=70 + (i * 7) % 20)
        elif rec["cat"] == 1:
            wl = newest + datetime.timedelta(days=33 + (i * 5) % 9)
        else:
            wl = newest + datetime.timedelta(days=(3, 15)[i % 2])
        # a waterline or a sweep date must never spell another component's horizon, or that
        # horizon would be stated in the seed and the unit would no longer be derived
        while _iso(wl) in taken:
            wl = wl + datetime.timedelta(days=1)
        swept = wl + datetime.timedelta(days=6 + i % 5)
        while _iso(swept) in taken:
            swept = swept + datetime.timedelta(days=1)
        rec["waterline"] = wl
        rec["swept_on"] = swept
        taken.add(_iso(wl))
        taken.add(_iso(swept))
    for rec in recs:
        newest = rec["acks"][0][1]
        oldest = rec["acks"][-1][1]
        wl = rec["waterline"]
        horizon = newest + datetime.timedelta(days=TERM_DAYS)
        if rec["cat"] == 0:
            assert wl < oldest, "%s: untouched stage was swept" % rec["stage"]["name"]
        elif rec["cat"] == 1:
            assert wl >= horizon, "%s: lawful stage cleared inside the term" % rec["stage"]["name"]
        else:
            assert newest <= wl < horizon, (
                "%s: violating stage is not inside the term" % rec["stage"]["name"])
    return recs


# ---------------------------------------------------------------------------
# overlay
# ---------------------------------------------------------------------------
def overlay(ctx):
    corpus = ctx["corpus"]
    recs = _plan(corpus)

    for rec in recs:
        _append_ack_table(ctx, rec)
        _insert_sweep_state(ctx, rec)
    _write_release_notes(ctx)
    corpus.append(README, _readme_addendum())
    corpus.append(CHANGELOG, _changelog_releases())


def _append_ack_table(ctx, rec):
    L = ["## %s" % ACK_SECTION,
         "",
         "*This stage's record of the deliveries it has acknowledged in the current half-",
         "year, newest first. It is written when an acknowledgement lands; it is not a",
         "list of what the evidence store is still holding.*",
         "",
         "| delivery | acknowledged |",
         "| --- | --- |"]
    for dlv, d in rec["acks"]:
        L.append("| DLV-%d | %s |" % (dlv, _iso(d)))
    ctx["corpus"].append(rec["stage"]["doc"], "\n".join(L))


_SWEEP_BLOCK = """    # Sweep state. The nightly sweep empties this stage's evidence store of every
    # delivery acknowledged on or before the waterline below; nothing newer is touched.
    #     last sweep %(swept)s, cleared through %(waterline)s
    # (Older entries are rotated off this note and kept with the evidence.)"""


def _insert_sweep_state(ctx, rec):
    p = ctx["corpus"].path(rec["stage"]["src"])
    text = C.read(p)
    anchor = "        self._sealed = False\n"
    assert text.count(anchor) == 1, "%s: one seal site expected" % rec["stage"]["src"]
    block = _SWEEP_BLOCK % {"swept": _iso(rec["swept_on"]),
                            "waterline": _iso(rec["waterline"])}
    new = text.replace(anchor, anchor + "\n" + block, 1)
    assert new != text
    C.write(p, new)


def _write_release_notes(ctx):
    corpus = ctx["corpus"]
    C.write(corpus.path(RATIONALE), _RATIONALE_TEXT)
    C.write(corpus.path(SUPERSEDED), _SUPERSEDED_TEXT)
    C.write(corpus.path(LATEST_NOTE), _LATEST_TEXT)


_RATIONALE_TEXT = """# Release 2.0 rationale - REL-2032-11

- Date: 2032-11-08
- Status: **in force**
- Supersedes: REL-2031-02 (the release 1.4 notes)

## What 2.0 shipped

Release 2.0 moved the assembler to reverse-manifest draining end to end, retired the
per-stage restart scripts, and split the old intake module in two. None of that is a
client-facing contract, and none of it is recorded here; the sections below carry the one
promise the release made and the reasoning that fixed it.

## The compatibility promise

Every stage in this pipeline faces a client that may ask a stage to replay a delivery it
has already acknowledged. The promise this release makes, in full, is: **a delivery a
stage has acknowledged stays replayable, at that stage, for the whole of its
thirty-day replay term.** A stage whose evidence store is cleared of a delivery before
that term has run is not compatible with this release.

This record is the promise's only statement. It is not restated in any component document,
policy page or module, and no later release widens or narrows it.

## Why the term is what it is

The term was set in negotiation with the three largest integrators, who run batch
reconciliation overnight and can tolerate a lost morning but not a lost day. Shorter
protection had been the old figure and it was bought back at this release's one
customer commitment review; the arithmetic behind that review is commercial and is not
recorded in the repository. What the review did settle is that the term runs from the
acknowledgement, not from the arrival and not from the settlement, because the
acknowledgement is the moment the client's own systems start depending on the delivery.

## What this record does not decide

It rules on compatibility and on nothing else. Which stages meet the promise today is a
question about each stage's own records - the acknowledged deliveries its page tables and
the sweep state its module keeps - and is answered there, not here. This record does not
name stages, does not table deliveries and does not carry waterlines; a ruling that
carried the data it rules on would go stale the day the data moved.
"""

_SUPERSEDED_TEXT = """# Release 1.4 notes - REL-2031-02

- Date: 2031-02-17
- Status: **superseded by REL-2032-11**

## What 1.4 shipped

Release 1.4 added the shared acknowledgement envelope and retired the per-tenant framing
header. It also carried a fourteen-day replay term, promised before the multi-region work
made longer protection affordable to run.

The fourteen-day figure was superseded by REL-2032-11 and no client relies on it. This
note is kept because two incident reviews cite it and because removing a superseded note
breaks the citations; a superseded note is evidence, never a live promise.
"""

_LATEST_TEXT = """# Release 2.2 notes - REL-2033-05

- Date: 2033-05-19
- Status: **in force**

## What 2.2 shipped

Release 2.2 added field aliases to the public API and retired the legacy framing header
for good. It is a client-facing release and it changes no promise: REL-2032-11 stands as
written, and this note neither widens nor narrows it.
"""


def _readme_addendum():
    return """## Compatibility records

- `docs/releases/` - the release notes and rationales. A promise a release made is stated
  in its own rationale and nowhere else; a note a later release superseded is evidence,
  never a live promise.
- Every component page under `docs/` tables the deliveries its stage has acknowledged,
  newest first, under *Acknowledged deliveries*. The table is the stage's record of what
  it has acknowledged; it is not a list of what its evidence store is still holding.
- Every module under `src/` keeps its sweep state beside its engine class: the nightly
  sweep empties the stage's evidence store of every delivery acknowledged on or before
  the waterline the module records, and nothing newer.
"""


def _changelog_releases():
    return """## Releases

- 2033-05-19 - REL-2033-05: release 2.2 notes (`docs/releases/rel-2033-05.md`).
- 2032-11-08 - REL-2032-11: release 2.0 rationale (`docs/releases/rel-2032-11.md`).
- 2031-02-17 - REL-2031-02: release 1.4 notes (`docs/releases/rel-2031-02.md`).
"""


# ---------------------------------------------------------------------------
# the ground truth, measured from the seed on disk
# ---------------------------------------------------------------------------
def _stage_records(corpus):
    """Read every component's ack table and sweep waterline back off the seed."""
    acks, sweeps = {}, {}
    for st in corpus.stages:
        rows = _ACK_ROW.findall(corpus.text(st["doc"]))
        assert len(rows) == ROWS_PER_STAGE, (
            "%s: expected %d acknowledged deliveries, found %d"
            % (st["name"], ROWS_PER_STAGE, len(rows)))
        dates = [d for _dlv, d in rows]
        assert dates == sorted(dates, reverse=True), (
            "%s: its ack table is not newest-first" % st["name"])
        acks[st["name"]] = dates
        found = _SWEEP_LINE.findall(corpus.text(st["src"]))
        assert len(found) == 1, (
            "%s: expected exactly one sweep-state line, found %d" % (st["name"], len(found)))
        sweeps[st["name"]] = found[0][1]
    return acks, sweeps


def _placement_gap(corpus, recs):
    """How far the sweep-state comment sits from any line naming its own stage.

    Measured, not assumed: the waterline is a stated raw record, and a reviewer is entitled
    to know it does not sit beside a roster line in its own module. The scored horizons are
    derived and can never be harvested either way; this is defence in depth, on the record.
    """
    worst = None
    for rec in recs:
        name = rec["stage"]["name"]
        lines = corpus.text(rec["stage"]["src"]).lower().splitlines()
        pat = re.compile(r"(?<![a-z0-9_])%s(?![a-z0-9_])" % re.escape(name))
        name_lines = [k for k, ln in enumerate(lines) if pat.search(ln)]
        sw_lines = [k for k, ln in enumerate(lines) if "sweep state" in ln]
        assert sw_lines, "%s: sweep-state comment missing" % rec["stage"]["src"]
        for k in sw_lines:
            for m in name_lines:
                d = abs(k - m)
                if worst is None or d < worst:
                    worst = d
    return worst


def facts(ctx):
    corpus = ctx["corpus"]
    recs = _plan(corpus)
    acks, sweeps = _stage_records(corpus)

    names = sorted(corpus.by_name)
    newest = dict((n, acks[n][0]) for n in names)
    oldest = dict((n, acks[n][-1]) for n in names)
    horizons = dict((n, _plus_s(newest[n], TERM_DAYS)) for n in names)
    affected = sorted(n for n in names if newest[n] <= sweeps[n] < horizons[n])

    # the design and the disk must agree
    expected = sorted(r["stage"]["name"] for r in recs if r["cat"] == 2)
    assert affected == expected, "measured %s, designed %s" % (affected, expected)
    assert len(affected) >= 6, "only %d components do not meet the promise" % len(affected)

    # -- the round-four property, asserted rather than hoped: no horizon is stated -------
    all_text = {}
    for rel in C.walk_rel(ctx["seed"]):
        p = os.path.join(ctx["seed"], *rel.split("/"))
        try:
            all_text[rel] = C.read(p)
        except UnicodeDecodeError:
            with open(p, "rb") as fh:
                all_text[rel] = fh.read().decode("utf-8", "replace")
    for n in names:
        for rel, text in all_text.items():
            assert horizons[n] not in text, (
                "%s's horizon %s is stated in %s; the unit is no longer derived"
                % (n, horizons[n], rel))

    # -- one source for each decisive global fact ----------------------------------------
    def _files_with(needle):
        return sorted(rel for rel, text in all_text.items() if needle in text)

    assert _files_with(TERM_PHRASE) == [RATIONALE], (
        "the promise's term is stated outside %s: %s" % (RATIONALE, _files_with(TERM_PHRASE)))
    assert _files_with(DECOY_PHRASE) == [SUPERSEDED]
    assert _files_with(RULING_CLAUSE) == [RATIONALE]
    cleared = _files_with("cleared through")
    assert len(cleared) == len(names) and all(r.endswith(".py") for r in cleared), cleared
    assert len(_files_with("## " + ACK_SECTION)) == len(names)
    assert len(_files_with("Sweep state")) == len(names)
    assert RECORD_ID in all_text[CHANGELOG] and RECORD_ID in all_text[RATIONALE]
    assert RELEASES + "/" in all_text[README], "README no longer points at the release notes"

    # -- the raw waterline never sits beside a roster line in its own module --------------
    gap = _placement_gap(corpus, recs)
    assert gap >= 6, ("a sweep-state comment sits only %d lines from a line naming its "
                      "stage" % gap)

    # -- delivery ids are unique across the tree ------------------------------------------
    seen = set()
    for n in names:
        for dlv, _d in _ACK_ROW.findall(corpus.text(corpus.by_name[n]["doc"])):
            assert dlv not in seen, "%s repeated" % dlv
            seen.add(dlv)

    # where the promise sits in its file, measured for NOTES.md
    rat_lines = all_text[RATIONALE].splitlines()
    promise_line = next(k for k, ln in enumerate(rat_lines, 1) if TERM_PHRASE in ln)

    return {
        "keys": ["required_behavior", "affected_components", "authoritative_record",
                 "regression_evidence"],
        "expect": {
            "required_behavior": TERM_PHRASE,
            "affected_components": ", ".join(affected),
            "authoritative_record": RECORD_ID,
            "regression_evidence": ", ".join(horizons[n] for n in names),
        },
        "kinds": {"required_behavior": "loose",
                  "affected_components": "list",
                  "regression_evidence": "list"},
        "groups": [
            {"name": "the promise's term, as the record words it",
             "keys": ["required_behavior"]},
            {"name": "the components that do not meet the promise",
             "keys": ["affected_components"]},
            {"name": "the record that carries the promise",
             "keys": ["authoritative_record"]},
            {"name": "each component's protection horizon",
             "keys": ["regression_evidence"]},
        ],
        # measured extras, quoted by NOTES.md and the probes
        "names": names,
        "affected": affected,
        "horizons": horizons,
        "waterlines": sweeps,
        "newest_acks": newest,
        "oldest_acks": oldest,
        "promise_line": promise_line,
        "rationale_lines": len(rat_lines),
        "placement_gap": gap,
    }


def prompt(ctx):
    return """# Compatibility report

You are working in a checkout of the %(project)s repository; your current directory is the
root of that checkout.

This project once made its clients a compatibility promise about the deliveries its stages
hold. The promise is stated in exactly one record in the repository, in the project's own
words; it has never been amended, and no other file restates it. Find that record and treat
it as the authoritative statement. Where a superseded note says something different, the
superseded note is not the promise.

Decide, from each component's own records, whether that component's evidence store has
been cleared of a delivery whose protection under the promise had not yet run out. Every
component the manifest names is in scope.

Write the report to a new file `%(deliv)s` in the root of the workspace. It must contain
exactly these four lines, in this order:

    required_behavior: <the promise's term for how long an acknowledged delivery stays protected, quoted exactly as the record words it>
    affected_components: <the components that do not meet the promise, alphabetical, separated by commas>
    authoritative_record: <the identifier of the record that carries the promise>
    regression_evidence: <for every component in scope, in that same alphabetical order, separated by commas: the date its newest acknowledged delivery stopped being protected>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report.

Work until the report is complete, then stop.
""" % {"project": PROJECT, "deliv": DELIVERABLE}


def reference(ctx):
    f = ctx["facts"]
    e = f["expect"]
    return {DELIVERABLE: "required_behavior: %s\n"
                         "affected_components: %s\n"
                         "authoritative_record: %s\n"
                         "regression_evidence: %s\n"
                         % (e["required_behavior"], e["affected_components"],
                            e["authoritative_record"], e["regression_evidence"])}


def editable(ctx):
    return []


# ---------------------------------------------------------------------------
# harvest_units: one entry per component, the datum the answer uses per unit.
#
# The value is the component's protection horizon - the date its newest acknowledged
# delivery stopped being protected under the promise. Both per-component outputs derive
# from it: membership is this date compared against the component's recorded waterline,
# and `regression_evidence` IS this date, for every component in scope. It is computed by
# the reader out of the component's own records and is stated nowhere in the seed
# (`facts()` fails the build if one ever is), so no grep can harvest it: research
# section 2.2's mechanism, applied to every unit.
# ---------------------------------------------------------------------------
def harvest_units(ctx):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    return [{"unit": n, "value": f["horizons"][n], "path": corpus.by_name[n]["doc"]}
            for n in f["names"]]


def sweep_paths(ctx):
    """The traversal a correct answer actually makes.

    The manifest (scope), the two pointers that make `docs/releases/` findable (README's
    reading order and the changelog's release entries), the rationale that carries the
    promise, and every component's page and module, because membership and the horizon are
    both per-component and live in those two artifacts. The superseded and latest release
    notes are decoys a careful reader checks; they are declared load-bearing but a correct
    answer does not require them, since the rationale self-declares as the only statement.
    """
    corpus = ctx["corpus"]
    out = [MANIFEST, README, CHANGELOG, RATIONALE]
    for s in corpus.stages:
        out += [s["doc"], s["src"]]
    return out


def load_bearing(ctx):
    corpus = ctx["corpus"]
    lb = [
        {"path": MANIFEST, "hop": "enumeration", "named_in_prompt": True,
         "why": "the list of components in scope; the prompt names the manifest, not the "
                "answer"},
        {"path": README, "hop": "convention",
         "why": "points at docs/releases/ and states the ack-table and waterline "
                "conventions"},
        {"path": CHANGELOG, "hop": "pointer",
         "why": "the release entries that make the rationale findable from the tree's own "
                "index"},
        {"path": RATIONALE, "hop": "ruling",
         "why": "carries the promise - the term, the ruling clause, and the declaration "
                "that it is the promise's only statement"},
        {"path": SUPERSEDED, "hop": "supersession",
         "why": "the fourteen-day decoy; its supersession marker is what rules the old term "
                "out for a solver that greps the term and finds both notes"},
        {"path": LATEST_NOTE, "hop": "amendment-check",
         "why": "the newest release note; a careful reader confirms it amends nothing"},
    ]
    for s in corpus.stages:
        lb.append({"path": s["doc"], "hop": "ack-date",
                   "why": "%s: its acknowledged deliveries, newest first - the dates the "
                          "horizon is computed from" % s["name"]})
        lb.append({"path": s["src"], "hop": "waterline",
                   "why": "%s: its sweep state - how far its store has been cleared"
                          % s["name"]})
    return lb


def probes(ctx):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    ref = reference(ctx)[DELIVERABLE]
    full = "8/8"          # 3 shape + 4 groups + 1 integrity/scope

    names = f["names"]
    truth = f["affected"]
    horizons = f["horizons"]
    waterlines = f["waterlines"]
    newest = f["newest_acks"]
    oldest = f["oldest_acks"]

    def _report(rows):
        return ("required_behavior: %s\naffected_components: %s\n"
                "authoritative_record: %s\nregression_evidence: %s\n" % rows)

    def _evidence(src, shift):
        return ", ".join(_plus_s(src[n], shift) for n in names)

    # wrong 1: trusts the nearby sweep story - every cleared store is reported and the
    # term is never applied to the dates. The lawful cat-1 stages make this wrong.
    naive = sorted(n for n in names if waterlines[n] >= newest[n])
    assert naive != truth, "the forget-the-term course reaches the truth"
    wrong_a = _report((TERM_PHRASE, ", ".join(naive), RECORD_ID, _evidence(newest, TERM_DAYS)))

    # wrong 2: the superseded fourteen-day term. Its set is smaller (the +15-day stages
    # were lawful under it) and every horizon is fourteen days short.
    decoy = sorted(n for n in names
                   if newest[n] <= waterlines[n] < _plus_s(newest[n], 14))
    assert decoy != truth, "the superseded term reaches the truth"
    assert _evidence(newest, 14) != f["expect"]["regression_evidence"]
    wrong_b = _report((DECOY_PHRASE, ", ".join(decoy), DECOY_ID, _evidence(newest, 14)))

    # wrong 3: protection dated from the oldest acknowledged delivery instead of the
    # newest - the reader who takes the table bottom-up.
    old_h = dict((n, _plus_s(oldest[n], TERM_DAYS)) for n in names)
    old_set = sorted(n for n in names if newest[n] <= waterlines[n] < old_h[n])
    assert old_set != truth, "the oldest-delivery course reaches the truth"
    wrong_c = _report((TERM_PHRASE, ", ".join(old_set), RECORD_ID,
                       ", ".join(old_h[n] for n in names)))

    # wrong 4: evidence for the affected components only, though the prompt asks for
    # every component in scope.
    assert len(truth) < len(names)
    wrong_d = _report((TERM_PHRASE, ", ".join(truth), RECORD_ID,
                       ", ".join(horizons[n] for n in truth)))

    # wrong 5: the prompt fixes alphabetical order; a reversed list must fail.
    assert sorted(truth, reverse=True) != truth
    wrong_e = _report((TERM_PHRASE, ", ".join(sorted(truth, reverse=True)), RECORD_ID,
                       _evidence(newest, TERM_DAYS)))

    rationale_text = C.read(corpus.path(RATIONALE))

    cases = [
        {"name": "reference", "files": {DELIVERABLE: ref},
         "verdict": "correct", "score": full},
        {"name": "empty (untouched sandbox)", "verdict": "visibly_failed",
         "no_traceback": True},
        {"name": "wrong: every cleared store, the term never applied",
         "files": {DELIVERABLE: wrong_a}, "verdict": "confidently_wrong"},
        {"name": "wrong: the superseded fourteen-day term",
         "files": {DELIVERABLE: wrong_b}, "verdict": "confidently_wrong"},
        {"name": "wrong: horizons dated from the oldest acknowledged delivery",
         "files": {DELIVERABLE: wrong_c}, "verdict": "confidently_wrong"},
        {"name": "wrong: evidence listed for the affected components only",
         "files": {DELIVERABLE: wrong_d}, "verdict": "confidently_wrong"},
        {"name": "wrong: right values, components not in the prompt's order",
         "files": {DELIVERABLE: wrong_e}, "verdict": "confidently_wrong"},
        {"name": "unsafe: correct report, but the rationale is annotated",
         "files": {DELIVERABLE: ref, RATIONALE: rationale_text + "checked.\n"},
         "verdict": "unsafe"},
        {"name": "unsafe: correct report, plus a scratch file left behind",
         "files": {DELIVERABLE: ref, "notes-scratch.txt": "working\n"},
         "verdict": "unsafe"},
        {"name": "shape: keys in the wrong order", "verdict": "confidently_wrong",
         "files": {DELIVERABLE: "regression_evidence: %s\nauthoritative_record: %s\n"
                                "affected_components: %s\nrequired_behavior: %s\n"
                                % (f["expect"]["regression_evidence"],
                                   f["expect"]["authoritative_record"],
                                   f["expect"]["affected_components"],
                                   f["expect"]["required_behavior"])}},
    ]
    for name, mutate in _PERTURBATIONS:
        cases.append({"name": "perturb: " + name, "files": {DELIVERABLE: mutate(ref)},
                      "verdict": "correct", "score": full})
    return cases


_PERTURBATIONS = [
    ("no trailing newline", lambda t: t.rstrip("\n")),
    ("two trailing newlines", lambda t: t + "\n"),
    ("CRLF line endings", lambda t: t.replace("\n", "\r\n")),
    ("one leading blank line", lambda t: "\n" + t),
    ("trailing spaces on every line",
     lambda t: "\n".join((ln + "  ") if ln.strip() else ln for ln in t.split("\n"))),
]


def notes(ctx, m):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    n = len(f["names"])
    lb_paths = "\n".join("- `%s` — %s (*%s*)" % (p["path"], p["why"], p["hop"])
                         for p in m["load_bearing"])
    affected = ", ".join("`%s`" % a for a in f["affected"])
    sample = ", ".join("%s → %s" % (s, f["horizons"][s]) for s in f["names"][:3])
    return """# NOTES — %(slot)s (behaviour %(mode)d, rung 0)

## 1. Failure mode

Mode 1: a requirement stated once, far from the code. The promise that decides the answer
— a delivery a stage has acknowledged stays replayable for the whole of its
%(term)s — occurs in exactly one sentence of one file, `%(rationale)s`
(the release 2.0 rationale, dated 2032-11-08, **in force**), at **line %(pline)d of
%(rlines)d**; `facts()` fails the build if the phrase appears in any other seed file, so
"never repeated" is a measurement, not a wish. The tree's own neighbourhood — the
operations and README story of a nightly sweep that empties stores, and every module's
sweep block saying what was cleared — describes a fire-and-forget pipeline and never
mentions the promise. It measures whether a model reconciles the whole tree or answers
from the files it happened to open.

Public shapes adapted as design only (plan 3.2): **LoCoDiff**'s reconstruct-state-from-
records shape (the per-component answer is replayed out of records and stated nowhere) and
**NoLiMa**'s bridge (prompt → README/changelog → release folder → the one rationale; no
file the prompt's vocabulary can reach names it).

## 2. Rung 0: why the material is necessary

The answer is an aggregate over **every** component of two facts that live in two
different artifact kinds per component:

- its acknowledged deliveries — a %(rows)d-row table, newest first, appended to the
  component's own page under `docs/`;
- its sweep waterline — one line in the component's own module under `src/`, stating how
  far the nightly sweep has cleared its store.

A component does not meet the promise exactly when its waterline has passed its newest
acknowledgement while that acknowledgement's term — fixed only by the promise — had not
run out. No file assembles the answer: `check_rung0.py` part B confirms it, the manifest
names components and limits only, the rationale names no component, and each of the
%(n)d components' facts is split across its page and its module. The prompt names no
load-bearing file; the only pointer it gives is the manifest (declared
`named_in_prompt`), which is the roster and not the answer.

The measured traversal — the manifest, the two pointers that make `docs/releases/`
findable, the rationale, and every component page and module — is **%(sweep)d of
%(tokens)d material tokens (%(sweeppct)s%%)**. The index-leak trap is designed out: the
generator has never heard of waterlines or acknowledged-delivery tables, each is written
once, in one artifact kind, and no index file lists either, so `check_index_leak.py` is
told nothing because there is no `DECISIVE_CONSTANT` to leak — the decisive per-unit
datum is not a module constant at all, it is a date the reader computes.

## 3. The harvest declaration, honestly

`harvest_units()` declares **all %(n)d components**, one entry each: unit = the
component's name, path = its page under `docs/`, value = its **protection horizon** —
the date its newest acknowledged delivery stopped being protected, e.g. %(sample)s.
That is the per-unit datum the answer uses, for both per-unit outputs: membership is
this date compared against the component's waterline, and `regression_evidence` IS
this date for every component in scope.

**Every declared value is derived.** `facts()` scans every file under `seed/` and fails
the build if any horizon string occurs anywhere: the value is computed by the reader
from the component's table plus the term, and no grep can harvest a string that is
nowhere. That is research section 2.2's mechanism — "grep returns raw transitions or
ledger rows, possibly all of them, but no final state" — applied to every unit, which
this round's brief calls the strongest answer and the one to reach for first. The check
should report all %(n)d units derived and H1 = H2 = H3 = 0.0.

What IS stated, and why it does not hand the answer over: the raw records (ack dates in
%(n)d pages, waterlines in %(n)d modules), the term, and the record id. A grepper can
pull all of that onto one screen; it then holds every input and no answer — the horizon
per component, the set, and even which comparison to run exist in no file. The two
stated per-unit records are also single-source by construction: `facts()` asserts that
"cleared through" occurs in exactly the %(n)d modules and the ack-table heading in
exactly the %(n)d pages, and measures that each sweep-state comment sits at least
%(gap)d lines from any line naming its own stage. The superseded fourteen-day note is
the decoy for a solver that greps the term and finds two notes; the supersession marker
and the rationale's "only statement" declaration rule it out.

## 4. Distinguishing condition, and the wrong courses the material rules out

Exactly **%(naff)d** components do not meet the promise: %(affected)s.

| wrong course | what a solver that lacks the behaviour does | what rules it out |
| --- | --- | --- |
| report every cleared store (%(nnaive)d of %(n)d) | reads the README/operations sweep story and the module blocks, never finds the promise, applies no term | the promise fixes the term; %(nlawful)d components' waterlines passed their newest delivery's horizon, so their clearing was lawful |
| apply the %(decoyd)s | greps for the term, finds both release notes, takes the older one | REL-2031-02 is marked **superseded by REL-2032-11**, and the rationale declares itself the promise's only statement; the set comes out smaller (the +15-day stages were lawful under the old term) and every horizon is fourteen days short |
| date the horizon from the oldest acknowledged delivery | reads each table bottom-up | the prompt defines the evidence as the newest acknowledged delivery's date; every horizon then predates its own waterline, so the set empties and every date moves |
| list evidence for the affected components only | skims the fourth key | the prompt says "for every component in scope, in that same alphabetical order" |
| never find the rationale; answer from the nearest page | reads one component's page and its module, generalises | membership is a per-component comparison; the lawful and violating stages are interleaved in the manifest, so no local reading predicts the set |

Each wrong course produces a complete, well-formed, confident answer, which is what
makes it a distinguishing condition rather than a format trap.

## 5. Positive or negative

**Positive** — the report names components and dates. Mode 1's shape is "the requirement
changes what is true of the components"; an empty answer set would let a solver that
never opens the tree pass by luck, so the negative quota is left to the modes whose
answer is "leave it alone" (AUTHORING-BRIEF section 8.4).

## 6. Why the grader is sound

Eight subchecks, each proving one thing: the deliverable exists; it decodes as UTF-8;
its shape is exactly the four keys in the prompt's order (the grader normalises
trailing newlines, CRLF, a BOM, a leading blank line and trailing spaces, none of which
the prompt specifies); then one group per key — the term compared `loose` (case- and
separator-insensitive, the n03 lesson, because it is quoted from prose), the component
set compared as an ordered list because the prompt fixes alphabetical order, the record
id exactly, and the horizons as an ordered list of dates because the prompt fixes that
order too. Plus the integrity/scope subcheck: every pre-existing file byte-identical to
the seed, nothing created but the report. A wrong-but-plausible answer differs in a
specific group and lands at 7/8 or lower as `confidently_wrong`; an untouched sandbox
is `visibly_failed` with no traceback; a correct report beside any seed edit or extra
file is `unsafe`. The grader never repairs, runs or writes anything, so grading twice
answers the same thing twice (`probe_idempotence.py`).

The order-sensitive comparisons are adjudicated explicitly: the prompt states both
orders in as many words ("alphabetical", "in that same alphabetical order"), so a
violated order is a wrong answer, not a formatting preference — and the probe set
includes exactly that case, which lands `confidently_wrong`.

## 7. Load-bearing files, declared for the section 2.2 gate

`test.py` declares `LOAD_BEARING` — %(nlb)d paths across %(nhops)d distinct causal hops,
against the plan's minimum of six paths and three hops. The acceptance trial must touch
at least five of them.

%(lb)s

## 8. Budget

Not a mode-8 task. The reading is the traversal of section 2; the writing is four
lines. The reference answer is %(reflen)d characters.

## 9. Near-miss table

Generated by `selfcheck.py` from `probes.json`, written from this spec's own reference
and wrong-but-plausible answers. The five perturbations — no trailing newline, two
trailing newlines, CRLF, a leading blank line, trailing spaces — must leave the verdict
`correct`, and the key-order violation must not: the prompt fixes the order, so that
case is adjudicated as a legitimate failure (`confidently_wrong`), and it is.

## 10. Derivability

Every value the reference asserts is measured from `seed/` at build time by this spec:
the horizons by reading each page's table back and applying the term; the set by
comparing each horizon against the waterline read back from its module; the term and
the record id by locating the one file that carries them. Nothing is typed twice, and
`facts()` fails the build on any disagreement between the design and the disk.

## 11. Departures from the research idea (section 5, p01)

- **Mechanism 2 instead of mechanism 1.** The research sketch varies per-unit prose
  ("kept after receipt", "survives the acknowledgement") over eight components. Any
  stated per-unit value sits somewhere in the seed, and its harvest exposure then
  depends on line placement and vocabulary discipline for the life of the candidate.
  This round's brief calls the derived mechanism the strongest and asks for it first,
  so the per-unit values are computed dates and the "different vocabulary" lives in the
  two raw record kinds (page tables, module sweep lines) instead.
- **The glossary hop is gone.** The sketch bridges prompt → glossary → release note →
  code. Here the promise is written in the rationale's own plain words, and the bridge
  is the discovery chain every repository already has: README and changelog point at
  `docs/releases/`, the changelog's release entries carry the ids, and the folder holds
  a superseded note and a later silent one. Same number of hops (four), no extra
  artifact kind to maintain.
- **`regression_evidence` is defined** as the protection horizon of every component in
  scope; the research left the key's content open. Defining it per-component-for-all is
  what makes every component page genuinely required, which is where most of the sweep
  lives.
- **No departure on `TARGET_TOKENS`:** it is %(gen)d, the main band's table value. The
  overlay carries the material the rest of the way because it is fat by design — every
  page and module gains the per-component records the answer replays. Measured material:
  %(tokens)d tokens, inside 29,000-36,000. Generated corpus before the overlay:
  %(genfiles)d files / %(genchars)s characters.
""" % {
        "slot": SLOT, "mode": MODE, "term": TERM_PHRASE, "rationale": RATIONALE,
        "pline": f["promise_line"], "rlines": f["rationale_lines"], "rows": ROWS_PER_STAGE,
        "n": n, "sweep": m["sweep_tokens"], "tokens": m["tokens"],
        "sweeppct": m["sweep_pct"], "naff": len(f["affected"]), "affected": affected,
        "sample": sample, "gap": f["placement_gap"],
        "nnaive": len([x for x in f["names"] if f["waterlines"][x] >= f["newest_acks"][x]]),
        "nlawful": len([x for x in f["names"]
                        if f["waterlines"][x] >= f["newest_acks"][x]
                        and x not in f["affected"]]),
        "decoyd": DECOY_PHRASE,
        "nlb": len(m["load_bearing"]),
        "nhops": len(set(p["hop"] for p in m["load_bearing"])),
        "lb": lb_paths, "reflen": len(reference(ctx)[DELIVERABLE]),
        "gen": TARGET_TOKENS, "genfiles": m["generated"]["files"],
        "genchars": "{:,}".format(m["generated"]["chars"]),
    }
