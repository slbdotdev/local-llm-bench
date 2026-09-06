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
Each component carries three decisive data, and each is defended the way research section 2
says to defend it:

- the **protection horizon** (newest acknowledgement + the term) is derived — the date string
  occurs nowhere under `seed/`, so no grep can harvest it;
- the **newest acknowledged date** and the **shelf-line through-date** are stated raw
  records, so they are declared as their own harvest units and made unharvestable the
  mechanism-1 way: the log rows are bare `DLV-… <day>` pairs under a heading each page
  picks for itself, and each module's two dates sit on bare labelled lines (`ran:` /
  `through:`) under that component's own sentence. No value-bearing line carries any
  letter-word, so the frame harvest has nothing to match; no fixed table header, no fixed
  sweep-comment frame, and no giveaway token within five lines of a value line in any
  unit's own file — all asserted at build time, with the check's own frame and window
  rules computed here rather than predicted in NOTES.

Revision note (2026-09-09, after the first build was reaped). Three defects were fixed:

1. **Fairness.** The `while _iso(swept) in taken` collision loop walked a category-2
   component's sweep run-date past its own horizon (digest 2035-01-22 vs horizon
   2035-01-18, rollup 2035-01-26 vs 2035-01-11), so on the face of its own record the
   store was cleared only after protection had run out, and an honest reader dating the
   clearing from the sweep it can see answered 4 of the 6 affected components. The sweep
   run-date is now chosen inside the design's own invariant — below the horizon for a
   violating stage, at or after it for a lawful one, below the oldest table row for an
   untouched one — and `facts()` asserts the invariant from the records read back off the
   disk, so the build dies rather than shipping the contradiction.
2. **Declaration.** `harvest_units()` declared only the derived horizon and nothing it
   could bite on; the two stated per-unit facts are now declared as their own entries,
   18 x 3 units in all.
3. **Harvest.** The fixed `| delivery | acknowledged |` table header and the fixed
   `last sweep …, cleared through …` comment let one grep (or one frame) carry all
   eighteen of each record; both fixed shapes are gone.
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
a store emptied of a delivery while the promise still protected it, the record's
identifier, the term as the record words it, and, for every component in scope, the day
its final acknowledged delivery stopped being protected. The per-component facts are
replayed from each component's signature log (its page under docs/) and its shelf line
(its module under src/); the horizons themselves are computed, not read, and occur
nowhere in the tree.
"""

BAND_NOTE = """
Corpus generated at 26,000 tokens and hand-overlaid to land inside the 29,000-36,000 main
band. The overlay is deliberately fat per component — every component page gains a
signature log and every module a shelf line, in that component's own words — because the
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
ROWS_PER_STAGE = 6

_ACK_ROW = re.compile(r"^- (DLV-\d+) (\d{4}-\d{2}-\d{2})$", re.M)

# The two generated-file boilerplate lines that carried the giveaway token `module` within
# five lines of unrelated 2034/2035 dates (the changelog's own entry headings), reworded so
# the changelog dates stop sitting beside a prompt word. The replacement is generated-tree
# boilerplate either way; the material still reads as itself.
_CHLOG_OLD = "brought in line with the module constants"
_CHLOG_NEW = "brought in line with the constants in code"


def _iso(d):
    return d.isoformat()


def _plus_s(iso, days):
    d = datetime.date(*[int(x) for x in iso.split("-")])
    return _iso(d + datetime.timedelta(days=days))


def _free(cand, taken, lo=None, hi=None, spread=90):
    """The nearest free recorded date to `cand`, searched 0, +1, -1, +2, -2 ...

    A recorded date must never spell a horizon (the horizon is derived and occurs
    nowhere) and must never repeat a stated date (every stated date stays
    single-source). The search is bounded and stays inside [lo, hi) when the
    category's invariant gives it a window, so a collision can never push a record
    out of the design's own invariant the way the first build's open-ended walk did.
    """
    seen = set()
    for k in range(spread):
        for d in (cand + datetime.timedelta(days=k),
                  cand - datetime.timedelta(days=k)):
            if d in seen:
                continue
            seen.add(d)
            if lo is not None and d < lo:
                continue
            if hi is not None and d >= hi:
                continue
            if _iso(d) not in taken:
                return d
    raise AssertionError("no free recorded date near %s in [%s, %s)"
                         % (cand, lo, hi))


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
#
# The sweep RUN-DATE is chosen inside the design's own invariant, and the invariants
# are re-asserted from disk in facts(): a violating stage's run happened while the
# newest delivery was still protected (wl <= swept < horizon), a lawful stage's run
# happened at or after its horizon (swept >= horizon), and an untouched stage's run
# happened before the oldest row its table still holds (swept < oldest). No recorded
# run may contradict the ruling on the face of the record.
# ---------------------------------------------------------------------------
def _stated_dates(corpus):
    """Every date the generated tree already states on a line of its own.

    The changelog's entry headings and the history proposals' Date lines are the
    generated tree's own calendar; a recorded waterline or run-date that repeated one
    would make the recorded date two-source. The plan refuses them.
    """
    rels = [CHANGELOG]
    hdir = os.path.join(corpus.seed, "history")
    for n in sorted(os.listdir(hdir)):
        if n.endswith(".md"):
            rels.append("history/" + n)
    out = set()
    for rel in rels:
        out.update(re.findall(r"\d{4}-\d{2}-\d{2}", corpus.text(rel)))
    return out


def _plan(corpus):
    st = corpus.stages
    n = len(st)
    assert 12 <= n <= 18, ("this design wants a dozen-plus components and one record "
                           "vocabulary per component: got %d" % n)
    newest0 = datetime.date(2034, 12, 24)
    recs = []
    for i, s in enumerate(st):
        newest = newest0 - datetime.timedelta(days=i)
        acks = [(5110 + 10 * i + j, newest - datetime.timedelta(days=11 * j + i % 5))
                for j in range(ROWS_PER_STAGE)]
        recs.append({"stage": s, "acks": acks, "cat": i % 3})
    # a recorded date must never spell a horizon (the horizon is derived and occurs
    # nowhere) and must never repeat a stated date (every stated date stays single-source)
    taken = set(_plus_s(_iso(r["acks"][0][1]), TERM_DAYS) for r in recs)
    taken.update(_iso(d) for r in recs for _dlv, d in r["acks"])
    taken.update(_stated_dates(corpus))
    for i, rec in enumerate(recs):
        newest = rec["acks"][0][1]
        oldest = rec["acks"][-1][1]
        horizon = newest + datetime.timedelta(days=TERM_DAYS)
        if rec["cat"] == 0:
            wl = _free(newest - datetime.timedelta(days=95 + (i * 7) % 20),
                       taken, hi=oldest)
            assert wl < oldest, "%s: untouched stage was swept" % rec["stage"]["name"]
            swept = _free(wl + datetime.timedelta(days=6 + i % 5),
                          taken, lo=wl + datetime.timedelta(days=1), hi=oldest)
            assert swept < oldest, "%s: untouched stage's run postdates its table" % (
                rec["stage"]["name"])
        elif rec["cat"] == 1:
            wl = _free(newest + datetime.timedelta(days=33 + (i * 5) % 9),
                       taken, lo=horizon)
            assert wl >= horizon, "%s: lawful stage cleared inside the term" % (
                rec["stage"]["name"])
            swept = _free(wl + datetime.timedelta(days=6 + i % 5), taken, lo=horizon)
            assert swept >= horizon, "%s: lawful stage's run predates its horizon" % (
                rec["stage"]["name"])
        else:
            wl = _free(newest + datetime.timedelta(days=(3, 15)[i % 2]),
                       taken, lo=newest, hi=horizon)
            assert newest <= wl < horizon, (
                "%s: violating stage is not inside the term" % rec["stage"]["name"])
            try:
                swept = _free(wl + datetime.timedelta(days=6 + i % 5),
                              taken, lo=wl + datetime.timedelta(days=1), hi=horizon)
            except AssertionError:
                # every day above the waterline inside the term is tiled by other
                # stages' horizons: step the waterline back a day (the day it frees
                # up is then available to the run) so the run-date and the
                # through-date stay distinct
                wl = _free(wl - datetime.timedelta(days=1), taken,
                           lo=newest, hi=wl)
                swept = _free(wl + datetime.timedelta(days=6 + i % 5),
                              taken, lo=wl + datetime.timedelta(days=1), hi=horizon)
            assert wl <= swept < horizon, (
                "%s: violating stage's run is not inside the term it broke"
                % rec["stage"]["name"])
        rec["waterline"] = wl
        rec["swept_on"] = swept
        taken.add(_iso(wl))
        taken.add(_iso(swept))
    return recs


# ---------------------------------------------------------------------------
# overlay: the two per-component record kinds, each in the component's own words.
#
# The first build used one fixed table (header `| delivery | acknowledged |`) and one
# fixed sweep comment (`last sweep …, cleared through …`), so one grep — or, without any
# vocabulary at all, one shared literal frame — carried all eighteen of each record.
# Both fixed shapes are gone, and the value-bearing lines themselves now carry no words
# at all: a page's log rows are bare `DLV-… <day>` pairs under a heading each page picks,
# and a module's two dates sit on their own labelled lines (`ran:` / `through:`) under a
# sentence in that component's own words. With no letter-words on any value-bearing line,
# the frame harvest has nothing to match, and no word of the giveaway vocabulary (the
# prompt, the manifest, the deliverable, the scored keys) occurs within five lines of a
# value line; facts() asserts both with the check's own rules.
# ---------------------------------------------------------------------------
_ACK_HEADINGS = [
    "Taken in",
    "Signed-off items",
    "Receipts",
    "Signatures collected",
    "Accepted and logged",
    "Received for keeping",
    "Marked as handled",
    "Signed for",
    "Entries taken on",
    "Items receipted",
    "Confirmed arrivals",
    "Batches signed off",
    "Logged sign-offs",
    "Handled and signed",
    "Signed, oldest last",
    "Incoming, signed",
    "The signature ledger",
    "This half's signatures",
]

_ACK_INTRO = """*What this page's engine has signed for in the current half-year, oldest
signature last. The log grows as each signature lands; what the shelf is
still holding is a separate matter, kept beside the engine itself.*"""

# One sentence per component, above that component's two labelled dates. The sentence
# carries no date, so it is never a value-bearing line and no frame is ever counted on
# it; its job is to say, in the component's own words, what the two lines below mean.
# The labels themselves (`ran:` / `through:`) are single words, so the two value-bearing
# lines form no two-word run either.
_KEEPER_PROSE = [
    # routing
    "# the last purge struck everything logged at or before the through-date;",
    # replay
    "# the pass took all items up to and including that boundary off the racks;",
    # backfill
    "# the rotation reached this crate and hauled off everything older than the line below;",
    # envelope
    "# kept current: the scrubber's last run removed all items from earlier than the line below;",
    # ingest
    "# the nightly pass stripped this rack of receipts dated before that line;",
    # digest
    "# the cleanup removed every signature from no later than the line below;",
    # attestation
    "# the sweep took each signature this ledger had accepted at or before the boundary;",
    # tenancy
    "# the purge flushed all signatures from dates up to and including the line below;",
    # watermark
    "# the janitor cleared out items logged at or earlier than the through-date;",
    # retention
    "# the vacuum swept this shelf down to everything logged since that line;",
    # reconcile
    "# sweeper's entry: signatures dated no later than the boundary were expunged;",
    # rollup
    "# the flush carried off all signatures at or before the line below;",
    # dispatch
    "# nightly prune: items signed for by the through-date are gone;",
    # checkpoint
    "# the pass wiped this locker of signatures up to and including the line below;",
    # quota
    "# the scrub struck the drawer of signatures at or before the boundary;",
    # drain
    "# the rotation took the bin of signatures logged at or before the line below;",
    # shard
    "# the purge stripped this stack of signatures dated at or before the boundary;",
    # schema
    "# swept clear: signatures up to and including the line below went to the archive.",
]

_KEEPER_HEAD = ["# Shelf line for this engine, kept current and rewritten after every pass.",
                "# The two dated lines at the foot are all there is to it."]
_KEEPER_TAIL = ["# Older passes are not shown here; only the latest one is. Earlier",
                "# ledger lines went to the archive."]


def _keeper_lines(i, rec):
    """The component's shelf-line block, appended at the foot of its module."""
    return [_KEEPER_HEAD[0],
            _KEEPER_HEAD[1],
            _KEEPER_PROSE[i],
            "#     ran: %s" % _iso(rec["swept_on"]),
            "#     through: %s" % _iso(rec["waterline"]),
            _KEEPER_TAIL[0],
            _KEEPER_TAIL[1]]


def _keeper_block(i, rec):
    return "\n".join(_keeper_lines(i, rec))


def _ack_block(i, rec):
    rows = []
    for dlv, d in reversed(rec["acks"]):          # oldest first, newest last
        rows.append("- DLV-%d %s" % (dlv, _iso(d)))
    return "\n".join(["## " + _ACK_HEADINGS[i], "", _ACK_INTRO, ""] + rows)


# ---------------------------------------------------------------------------
# overlay
# ---------------------------------------------------------------------------
def overlay(ctx):
    corpus = ctx["corpus"]
    recs = _plan(corpus)

    for i, rec in enumerate(recs):
        _append_ack_log(ctx, i, rec)
        _insert_sweep_state(ctx, i, rec)
    _write_release_notes(ctx)
    corpus.append(README, _readme_addendum())
    corpus.append(CHANGELOG, _changelog_releases())
    # the generated changelog bullets sit two lines under their own `## <date>` headings;
    # with the giveaway token `module` in them, the changelog's unrelated 2034/2035
    # headings were within one grep of every derived horizon's bare year. Reworded.
    corpus.replace_in(CHANGELOG, _CHLOG_OLD, _CHLOG_NEW, count=64)
    text = C.read(corpus.path(CHANGELOG))
    assert _CHLOG_OLD not in text, "the changelog rewording did not take"


def _append_ack_log(ctx, i, rec):
    ctx["corpus"].append(rec["stage"]["doc"], _ack_block(i, rec))


def _insert_sweep_state(ctx, i, rec):
    ctx["corpus"].append(rec["stage"]["src"], _keeper_block(i, rec))


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
question about each stage's own records - the acknowledged deliveries its page logs and
the shelf line its module keeps - and is answered there, not here. This record does not
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
- Every component page under `docs/` ends with the log of the deliveries its stage has
  acknowledged, oldest signature last, under a heading the page picks for itself. The log
  is the stage's record of what it has acknowledged; it is not a list of what its evidence
  store is still holding.
- Every module under `src/` closes with a shelf line at the foot of the file: the nightly
  sweep empties the stage's evidence store of every delivery acknowledged on or before the
  through-date the line records, on the run-date it records, and nothing newer.
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
def _keeper_reads(ctx, recs):
    """Read each component's two recorded dates back off the disk.

    The block's lines are asserted present verbatim first, so the regexes below run
    over text the build knows is there; the dates themselves are still read, not
    assumed.
    """
    swept, waterline = {}, {}
    for i, rec in enumerate(recs):
        lines = _keeper_lines(i, rec)
        text = C.read(ctx["corpus"].path(rec["stage"]["src"]))
        for ln in lines:
            assert ln in text, "%s: its shelf line is not on disk as written\n%r" % (
                rec["stage"]["name"], ln)
        ran = re.search(r"ran: (\d{4}-\d{2}-\d{2})", text)
        thru = re.search(r"through: (\d{4}-\d{2}-\d{2})", text)
        assert ran and thru, "%s: its two dated lines are not on disk" % rec["stage"]["name"]
        swept[rec["stage"]["name"]] = ran.group(1)
        waterline[rec["stage"]["name"]] = thru.group(1)
    return swept, waterline


def _stage_records(ctx, recs):
    """Read every component's signature log and shelf line back off the seed."""
    acks, waterlines = {}, {}
    for i, rec in enumerate(recs):
        st = rec["stage"]
        rows = _ACK_ROW.findall(ctx["corpus"].text(st["doc"]))
        assert len(rows) == ROWS_PER_STAGE, (
            "%s: expected %d acknowledged deliveries, found %d"
            % (st["name"], ROWS_PER_STAGE, len(rows)))
        ids = [dlv for dlv, _d in rows]
        dates = [d for _dlv, d in rows]
        assert ids == sorted(ids, reverse=True), (
            "%s: its log is not oldest-first" % st["name"])
        assert dates == sorted(dates), "%s: its log is not oldest-first" % st["name"]
        assert [int(dlv.split("-")[1]) for dlv in ids] \
            == [d for d, _day in reversed(rec["acks"])], (
            "%s: its log's delivery ids are not the designed ones" % st["name"])
        acks[st["name"]] = dates
    swept, waterlines = _keeper_reads(ctx, recs)
    return acks, waterlines, swept


def facts(ctx):
    corpus = ctx["corpus"]
    recs = _plan(corpus)
    acks, sweeps, swept = _stage_records(ctx, recs)

    names = sorted(corpus.by_name)
    newest = dict((n, acks[n][-1]) for n in names)
    oldest = dict((n, acks[n][0]) for n in names)
    horizons = dict((n, _plus_s(newest[n], TERM_DAYS)) for n in names)
    affected = sorted(n for n in names if newest[n] <= sweeps[n] < horizons[n])

    # the design and the disk must agree
    expected = sorted(r["stage"]["name"] for r in recs if r["cat"] == 2)
    assert affected == expected, "measured %s, designed %s" % (affected, expected)
    assert len(affected) >= 6, "only %d components do not meet the promise" % len(affected)

    # -- the sweep run-dates must agree with the ruling, on the face of the record -------
    # (the fairness defect of the first build: the collision loop had pushed digest's and
    # rollup's run-dates past their own horizons, contradicting the ruling for them)
    for rec in recs:
        n = rec["stage"]["name"]
        h = horizons[n]
        s = swept[n]
        w = sweeps[n]
        if rec["cat"] == 0:
            assert s < oldest[n], "%s: untouched stage's run postdates its table" % n
        elif rec["cat"] == 1:
            assert s >= h, "%s: lawful stage's run predates its horizon" % n
            assert w >= h, "%s: lawful stage cleared inside the term" % n
        else:
            assert newest[n] <= w < h, "%s: violating stage is not inside the term" % n
            assert w <= s < h, ("%s: violating stage's run is not inside the term it "
                                "broke" % n)

    # -- the round-four property, asserted rather than hoped: no horizon is stated -------
    all_text = _read_all(ctx)
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
    assert RECORD_ID in all_text[CHANGELOG] and RECORD_ID in all_text[RATIONALE]
    assert RELEASES + "/" in all_text[README], "README no longer points at the release notes"

    # -- the first build's fixed record shapes are gone and stay gone --------------------
    for gone in ("cleared through", "last sweep", "## Acknowledged deliveries",
                 "| delivery | acknowledged |", _CHLOG_OLD):
        assert _files_with(gone) == [], "%r is stated in %s" % (gone, _files_with(gone))

    # -- each stated per-unit date is single-source; each page/module carries exactly ----
    #    its own record vocabulary, and no two components share a template
    for i, rec in enumerate(recs):
        n = rec["stage"]["name"]
        heading = "## " + _ACK_HEADINGS[i]
        assert _files_with(heading) == [rec["stage"]["doc"]], (
            "%s's log heading is not single-source: %s" % (n, _files_with(heading)))
        ran_line = "ran: %s" % swept[n]
        assert _files_with(ran_line) == [rec["stage"]["src"]], (
            "%s's run-date line is not single-source: %s" % (n, _files_with(ran_line)))
        thru_line = "through: %s" % sweeps[n]
        assert _files_with(thru_line) == [rec["stage"]["src"]], (
            "%s's through-date line is not single-source: %s" % (n, _files_with(thru_line)))
    for n in names:
        # every recorded waterline and run-date is globally unique (the plan refuses to
        # place one on any acknowledged day), so each occurs in exactly one file; the
        # newest acknowledgement sits on the last row of its own page's log; older log
        # rows may legitimately share a day across components, and do
        for d in (sweeps[n], swept[n]):
            where = _files_with(d)
            assert len(where) == 1, "%s's date %s occurs in %s" % (n, d, where)
        assert acks[n][-1] in all_text[corpus.by_name[n]["doc"]]
        assert acks[n][-1] == sorted(acks[n])[-1]
    assert len(set(_ACK_HEADINGS[:len(names)])) == len(names)
    assert len(set(_KEEPER_PROSE[:len(names)])) == len(names)

    # -- delivery ids are unique across the tree ------------------------------------------
    seen = set()
    for n in names:
        for dlv, _d in _ACK_ROW.findall(corpus.text(corpus.by_name[n]["doc"])):
            assert dlv not in seen, "%s repeated" % dlv
            seen.add(dlv)

    # -- the harvest measures, computed here with the check's own rules -------------------
    #    (a build-time measurement, never a prediction: the same windows, the same part
    #    splitting, the same frame rule that r4/check_harvest.py applies after the build)
    units, h1, h2, h3, frame_n, frame_text, own_clean = _harvest_measures(
        ctx, names, acks, sweeps, horizons)
    assert h1 < 0.25, "build-time H1 = %.3f, over the one-quarter limit" % h1
    assert h2 < 0.40, "build-time H2 = %.3f, over the two-fifths limit" % h2
    assert h3 < 1.0 / 3.0, "build-time H3 = %.3f, over the one-third limit" % h3
    assert frame_n < 0.25 * len(units), (
        "the widest shared frame reaches %d of %d units" % (frame_n, len(units)))
    assert own_clean, "a giveaway token sits within five lines of a value line in a " \
                      "unit's own file"

    # -- where the promise sits in its file, measured for NOTES.md -------------------------
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
        "swept_on": swept,
        "newest_acks": newest,
        "oldest_acks": oldest,
        "promise_line": promise_line,
        "rationale_lines": len(rat_lines),
        "units": units,
        "h1_build": h1,
        "h2_build": h2,
        "h3_build": h3,
        "frame_n": frame_n,
        "frame_text": frame_text,
    }


def _read_all(ctx):
    all_text = {}
    for rel in C.walk_rel(ctx["seed"]):
        p = os.path.join(ctx["seed"], *rel.split("/"))
        try:
            all_text[rel] = C.read(p)
        except UnicodeDecodeError:
            with open(p, "rb") as fh:
                all_text[rel] = fh.read().decode("utf-8", "replace")
    return all_text


# ---------------------------------------------------------------------------
# the harvest measures, with the check's own rules (r4/check_harvest.py)
# ---------------------------------------------------------------------------
_STOP = set("""a an and are as at be been before but by can do does for from has have if in into
is it its may must never no not of on one only or other our over same shall should so some
such than that the their them then there these they this those to two under until up upon use
used using was were what when where which while who why will with within without you your
work working current directory root new file files line lines write written writes exactly
order value values name names each every all any more most also just plainly stop nothing
create created creates modify modified delete deleted existing task prompt project repository
checkout report list plain integer comma separated alphabetical header quotes explanation
newline end ends may not do does""".split())

_GWORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")
_WORDY = re.compile(r"[A-Za-z]{2,}")


def _bounded(needle):
    esc = re.escape(needle.lower())
    left = r"(?<![A-Za-z0-9_])" if re.match(r"[A-Za-z0-9_]", needle[0]) else ""
    right = r"(?![A-Za-z0-9_])" if re.match(r"[A-Za-z0-9_]", needle[-1]) else ""
    return re.compile(left + esc + right)


def _giveaway(ctx, keys):
    words = set(w.lower() for w in _GWORD.findall(prompt(ctx)))
    words |= set(w.lower() for w in _GWORD.findall(ctx["corpus"].text(MANIFEST)))
    words.add(DELIVERABLE.lower())
    for k in keys:
        words.add(str(k).lower())
        words |= set(w.lower() for w in _GWORD.findall(str(k)))
    return sorted(w for w in (words - _STOP) if len(w) >= 4)


def _declared_units(f, corpus):
    """The 54-entry declaration: three decisive data per component.

    Per r4/BRIEF section 4, a unit with two decisive data is two harvest-unit entries:
    the derived horizon, the stated newest acknowledgement, and the stated shelf-line
    through-date are three entries each.
    """
    out = []
    for n in f["names"]:
        doc = corpus.by_name[n]["doc"]
        src = corpus.by_name[n]["src"]
        out.append({"unit": n, "value": f["horizons"][n], "path": doc})
        out.append({"unit": n + " ack", "value": f["newest_acks"][n], "path": doc})
        out.append({"unit": n + " waterline", "value": f["waterlines"][n], "path": src})
    return out


def _harvest_measures(ctx, names, acks, sweeps, horizons):
    corpus = ctx["corpus"]
    f = {"names": names, "horizons": horizons,
         "newest_acks": dict((n, acks[n][-1]) for n in names),
         "waterlines": sweeps}
    units = _declared_units(f, corpus)
    lines_by_file = dict((rel, text.lower().splitlines())
                         for rel, text in _read_all(ctx).items())

    vocab = _giveaway(ctx, ["required_behavior", "affected_components",
                            "authoritative_record", "regression_evidence"])

    def line_hits(pattern):
        out = {}
        for rel, lines in lines_by_file.items():
            hit = set(i for i, ln in enumerate(lines) if pattern.search(ln))
            if hit:
                out[rel] = hit
        return out

    def sub_hits(token):
        out = {}
        for rel, lines in lines_by_file.items():
            hit = set(i for i, ln in enumerate(lines) if token in ln)
            if hit:
                out[rel] = hit
        return out

    # per-unit value/identifier line maps, exactly as the check derives them
    val_hits, id_hits = {}, {}
    for u in units:
        parts = []
        for part in re.split(r"\s*(?:->|=>|\|\||[|,;=/\\.\-_]|\s)\s*", str(u["value"]).strip()):
            part = part.strip().strip(":=")
            if len(part) < 3:
                continue
            pl = part.lower()
            ul = str(u["unit"]).lower()
            if pl == ul or (ul and ul in pl and len(pl) - len(ul) < 3):
                continue
            parts.append(part)
        whole = str(u["value"]).strip()
        if len(whole) >= 10 and whole.lower() not in [x.lower() for x in parts]:
            parts = parts + [whole]
        vh = {}
        for part in parts:
            for rel, hit in line_hits(_bounded(part)).items():
                vh.setdefault(rel, set()).update(hit)
        val_hits[u["unit"]] = vh
        id_hits[u["unit"]] = line_hits(_bounded(str(u["unit"])))

    def harvested(u, anchor, c):
        for rel, anchors in anchor.items():
            vals = val_hits[u["unit"]].get(rel)
            if not vals:
                continue
            ids = id_hits[u["unit"]].get(rel, set())
            own = (rel == u["path"])
            for i in anchors:
                w = set(range(i - c, i + c + 1))
                if not (w & vals):
                    continue
                if own or (w & ids):
                    return True
        return False

    best1 = (0, None)
    best5 = (0, None)
    for t in vocab:
        anchor = sub_hits(t)
        if not anchor:
            continue
        n2 = sum(1 for u in units if harvested(u, anchor, 2))
        n5 = sum(1 for u in units if harvested(u, anchor, 5))
        if n2 > best1[0]:
            best1 = (n2, t)
        if n5 > best5[0]:
            best5 = (n5, t)
    h1 = best1[0] / float(len(units))
    h3 = best5[0] / float(len(units))
    roster = re.compile("|".join(sorted((_bounded(str(u["unit"])).pattern for u in units),
                                        key=len, reverse=True)))
    roster_anchor = line_hits(roster)
    h2 = sum(1 for u in units if harvested(u, roster_anchor, 2)) / float(len(units))

    # the frame harvest, with the check's own rule
    def frames(line, value, unit):
        text = line.lower().replace(str(value).lower(), " ").replace(str(unit).lower(), " ")
        words = _WORDY.findall(text)
        out = set()
        for n in range(2, 7):
            for i in range(len(words) - n + 1):
                frag = " ".join(words[i:i + n])
                if len(frag) >= 10:
                    out.add(frag)
        return out

    frame_count = {}
    frame_units = {}
    for u in units:
        seen = set()
        for rel, idxs in val_hits[u["unit"]].items():
            for i in idxs:
                seen |= frames(lines_by_file[rel][i], u["value"], u["unit"])
        for fr in seen:
            frame_count[fr] = frame_count.get(fr, 0) + 1
            frame_units.setdefault(fr, []).append(u["unit"])
    frame_text, frame_n = max(frame_count.items(), key=lambda kv: kv[1]) if frame_count \
        else ("", 0)

    # no giveaway token within five lines of a value line in any unit's own file
    own_clean = True
    for u in units:
        own = u["path"]
        bans = sub_hits_any(vocab, lines_by_file.get(own, []))
        for i in val_hits[u["unit"]].get(own, ()):
            if any(abs(i - j) <= 5 for j in bans):
                own_clean = False
    return units, h1, h2, h3, frame_n, frame_text, own_clean


def sub_hits_any(vocab, lines):
    out = []
    for i, ln in enumerate(lines):
        if any(t in ln for t in vocab):
            out.append(i)
    return out


def prompt(ctx):
    return """# Compatibility report

You are working in a checkout of the %(project)s repository; your current directory is the
root of that checkout.

This project once made its clients a compatibility promise concerning the deliveries its
stages keep. The promise is written in exactly one record in the repository, in the project's
own words; it has never been amended, and no other file restates it. Find that record and
treat it as the authoritative source. Where a superseded note says something different, the
superseded note is not the promise.

Work out, from each component's own records, whether that component's evidence store has
been emptied of a delivery while its protection under the promise had yet to expire. Every
component the manifest names is in scope.

Write the report to a new file `%(deliv)s` in the root of the workspace. It must contain
exactly these lines, in this order:

    required_behavior: <the promise's term for the span an acknowledged delivery remains protected, quoted exactly as the record words it>
    affected_components: <the components the promise rules out, alphabetical, separated by commas>
    authoritative_record: <the identifier of the record that carries the promise>
    regression_evidence: <for every component in scope, in that same alphabetical order, separated by commas: the day its final acknowledged delivery stopped being protected>

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
# harvest_units: three entries per component — the derived horizon, the stated newest
# acknowledgement, and the stated shelf-line through-date. The first build declared only
# the horizon, which the re-review called dishonest: the two stated per-unit facts are
# each one grep away and each decisive, and a unit with two decisive data is two entries
# (r4/BRIEF section 4). The measures that bite on the two stated kinds are answered by
# the record shapes above (bare log rows, per-component shelf-line prose), not by the
# declaration; facts() computes the check's own measures over all 54 entries and asserts
# them under the round's limits at build time.
# ---------------------------------------------------------------------------
def harvest_units(ctx):
    return ctx["facts"]["units"]


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
         "why": "points at docs/releases/ and states the log and shelf-line conventions"},
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
                   "why": "%s: its signature log, oldest last - the dates the horizon is "
                          "computed from" % s["name"]})
        lb.append({"path": s["src"], "hop": "waterline",
                   "why": "%s: its shelf line - how far its store has been emptied"
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

    # wrong 1: trusts the nearby sweep story - every emptied store is reported and the
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
    # newest - the reader who takes the log's first row rather than its last.
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
        {"name": "wrong: every emptied store, the term never applied",
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
    frame_txt = ("0 — no value-line frame is shared by any two of the %d units"
                 % len(f["units"])) if f["frame_n"] < 2 else (
        "the widest shared value-line frame reaches %d units (%.3f of %d, under the "
        "one-quarter limit) — %r"
        % (f["frame_n"], f["frame_n"] / float(len(f["units"])), len(f["units"]),
           f["frame_text"][:60]))
    cat2_runs = ", ".join(
        "%s ran %s, %d day(s) before its horizon %s"
        % (s, f["swept_on"][s],
           (datetime.date(*[int(x) for x in f["horizons"][s].split("-")])
            - datetime.date(*[int(x) for x in f["swept_on"][s].split("-")])).days,
           f["horizons"][s])
        for s in f["affected"][:3])
    return """# NOTES — %(slot)s (behaviour %(mode)d, rung 0)

## 1. Failure mode

Mode 1: a requirement stated once, far from the code. The promise that decides the answer
— a delivery a stage has acknowledged stays replayable for the whole of its
%(term)s — occurs in exactly one sentence of one file, `%(rationale)s`
(the release 2.0 rationale, dated 2032-11-08, **in force**), at **line %(pline)d of
%(rlines)d**; `facts()` fails the build if the phrase appears in any other seed file, so
"never repeated" is a measurement, not a wish. The tree's own neighbourhood — the
operations and README story of a nightly sweep that empties stores, and every module's
shelf line saying what was taken — describes a fire-and-forget pipeline and never
mentions the promise. It measures whether a model reconciles the whole tree or answers
from the files it happened to open.

Public shapes adapted as design only (plan 3.2): **LoCoDiff**'s reconstruct-state-from-
records shape (the per-component answer is replayed out of records and stated nowhere) and
**NoLiMa**'s bridge (prompt → README/changelog → release folder → the one rationale; no
file the prompt's vocabulary can reach names it).

## 2. Rung 0: why the material is necessary

The answer is an aggregate over **every** component of three facts that live in two
different artifact kinds per component:

- its acknowledged deliveries — a %(rows)d-row log, oldest signature last, appended to the
  component's own page under `docs/`;
- its sweep waterline and its last sweep run-date — the two dated lines of the shelf line
  in the component's own module under `src/`.

A component does not meet the promise exactly when its waterline has passed its newest
acknowledgement while that acknowledgement's term — fixed only by the promise — had not
run out, and its own shelf line dates the run inside that window. No file assembles the
answer: `check_rung0.py` part B confirms it, the manifest names components and limits
only, the rationale names no component, and each of the %(n)d components' facts is split
across its page and its module. The prompt names no load-bearing file; the only pointer
it gives is the manifest (declared `named_in_prompt`), which is the roster and not the
answer. The smallest assembly the answer needs is %(nasm)d files: the manifest, the
rationale, and every component's page and module.

The measured traversal — the manifest, the two pointers that make `docs/releases/`
findable, the rationale, and every component page and module — is **%(sweep)d of
%(tokens)d material tokens (%(sweeppct)s%%)**. The index-leak trap is designed out: the
generator has never heard of waterlines, shelf lines or signature logs, each is written
once, in one artifact kind, and no index file lists any of them — asserted at build
time: every waterline and run-date occurs in exactly one seed file, every horizon string
in none, and each newest acknowledgement sits on the last row of its own page's log.

## 3. The harvest declaration, honestly

`harvest_units()` declares **%(nunit)d entries — three per component** — because each
component carries three decisive data, and the round's brief says a unit with two
decisive data is two harvest-unit entries:

- unit `<name>`, value = its **protection horizon** (its newest acknowledgement plus the
  term), e.g. %(sample)s. Derived: `facts()` fails the build if any horizon string
  occurs anywhere under `seed/`, so the full value is stated nowhere and no grep can
  harvest it;
- unit `<name> ack`, value = its **newest acknowledged date**, stated on the last row of
  its page's log (measured: each sits on that last row, which is what the answer reads);
- unit `<name> waterline`, value = its **shelf-line through-date**, stated in its module
  (measured: exactly one file each).

The first build declared only the horizon and left both stated facts undeclared — the
re-review called that correctly dishonest, and it was right twice over, because the fixed
`| delivery | acknowledged |` table header and the fixed `last sweep …, cleared through …`
comment made one grep (`-C2 acknowledged`, `-C2 cleared`) — and, with no vocabulary at
all, one shared frame, `sweep cleared through` — carry all eighteen of each record. Both
fixed shapes are gone and `facts()` asserts them absent. The log rows are now bare
`DLV-… <day>` pairs — no words at all on a page's value-bearing lines — under a heading
each page picks for itself, and each module's two dates sit on their own labelled lines
(`ran:` / `through:`) under a sentence in that component's own words — so no
value-bearing line anywhere carries a two-word run for the frame harvest to match; no
two components share a record template (asserted pairwise).

The harvest measures are **computed at build time with the check's own rules** — same
part splitting, same ±2/±5 windows, same frame rule — over all %(nunit)d declared units,
so this section measures rather than predicts: widest single giveaway token reaches
**%(h1pc)s** of the units at ±2 and **%(h3pc)s** at ±5; the roster regex reaches
**%(h2pc)s**; the frame harvest reads %(frame_txt)s Every unit's own file is
clean of giveaway tokens within five lines of a value line (asserted); the one remaining
coincidence is the generated history entries' own `Date:` lines sitting two lines under
their proposal titles, which the widest token reaches through the bare year alone. What
IS stated anywhere — raw log rows, shelf lines, the term, the record id — yields every
input and no answer: the horizons, the set, and which comparison to run exist in no file.

## 4. Distinguishing condition, and the wrong courses the material rules out

Exactly **%(naff)d** components do not meet the promise: %(affected)s. The build asserts
the ruling against each component's own recorded run-date, so no record contradicts it:
every violating stage's sweep ran inside the term it broke (%(cat2runs)s), every lawful
stage's run at or after its horizon, and every untouched stage's run before the oldest
row its log still holds.

| wrong course | what a solver that lacks the behaviour does | what rules it out |
| --- | --- | --- |
| report every emptied store (%(nnaive)d of %(n)d) | reads the README/operations sweep story and the shelf lines, never finds the promise, applies no term | the promise fixes the term; %(nlawful)d components' waterlines passed their newest delivery's horizon, so their clearing was lawful |
| apply the %(decoyd)s | greps for the term, finds both release notes, takes the older one | REL-2031-02 is marked **superseded by REL-2032-11**, and the rationale declares itself the promise's only statement; the set comes out smaller (the +15-day stages were lawful under the old term) and every horizon is fourteen days short |
| date the horizon from the oldest acknowledged delivery | takes the log's first row instead of its last | the prompt defines the evidence as the final acknowledged delivery's date; every horizon then predates its own waterline, so the set empties and every date moves |
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
the horizons by reading each page's log back and applying the term; the set by comparing
each horizon against the waterline and run-date read back from its module; the term and
the record id by locating the one file that carries them. Nothing is typed twice, and
`facts()` fails the build on any disagreement between the design and the disk — including
the fairness invariants: a violating stage's recorded run must sit inside the term it
broke, a lawful stage's at or after its horizon, an untouched stage's before its oldest
table row.

## 11. Departures from the research idea (section 5, p01)

- **Mechanism 2 for the horizons, mechanism 1 for the two stated records.** The sketch
  varies per-unit prose over eight components. Here the derived datum (the horizon) is
  computed and stated nowhere — the brief's strongest answer — and the two stated raw
  records (newest acknowledgement, waterline) are declared as their own harvest units and
  defended the prose way: bare log rows under per-component headings, and two bare
  labelled dates under a shelf-line sentence written in each component's own words. The
  first build's fixed table header and fixed sweep comment were harvested 18/18 by one
  frame; both are gone, asserted.
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
- **One generated-tree boilerplate reword.** The changelog's per-entry line "brought in
  line with the module constants" sat two lines under the changelog's own unrelated
  2034/2035 entry headings; with the giveaway token `module` in it, those headings were
  one grep from every horizon's bare year. It now reads "brought in line with the
  constants in code". No record, date or decision is touched.
- **No departure on `TARGET_TOKENS`:** it is %(gen)d, the main band's table value. The
  overlay carries the material the rest of the way because it is fat by design — every
  page and module gains the per-component records the answer replays. Measured material:
  %(tokens)d tokens, inside 29,000-36,000. Generated corpus before the overlay:
  %(genfiles)d files / %(genchars)s characters.
""" % {
        "slot": SLOT, "mode": MODE, "term": TERM_PHRASE, "rationale": RATIONALE,
        "pline": f["promise_line"], "rlines": f["rationale_lines"], "rows": ROWS_PER_STAGE,
        "n": n, "nasm": 2 * n + 2, "sweep": m["sweep_tokens"], "tokens": m["tokens"],
        "sweeppct": m["sweep_pct"], "naff": len(f["affected"]), "affected": affected,
        "sample": sample,
        "nunit": len(f["units"]),
        "h1pc": "%.3f" % f["h1_build"], "h2pc": "%.3f" % f["h2_build"],
        "h3pc": "%.3f" % f["h3_build"],
        "frame_n": f["frame_n"],
        "frame_max": "%.3f" % (f["frame_n"] / float(len(f["units"]))),
        "frame_ex": f["frame_text"][:60],
        "frame_txt": frame_txt,
        "cat2runs": cat2_runs,
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
