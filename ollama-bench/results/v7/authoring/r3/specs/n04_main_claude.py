"""n04-main-claude — replay the log, do not read the state.

Research idea n04 (`research-r3-2026-09-08.md` section 2): an append-only change journal split
over several filings, whose entries carry journal-wide sequence numbers that interleave across
the files; the modules carry the value each stage was **commissioned** with and say so plainly;
the value in force exists only as a replay and is written down nowhere.

Public shapes adapted as design only, never as data: tau^2-bench's long-horizon state tracking
under partial observability [S15], and BABILong's list/set fact-chaining [S16].

Rung 0: the answer is an aggregate over every stage in the manifest. No file holds it and no
command prints it. Membership of the changed set needs three artifact kinds at once — the
stage document (which evidence vault the stage writes into), the stage module (the commissioned
depth) and the journal filings (the amendments) — and the rule that turns the filings into a
history lives in a fourth. The journal never names a stage and no document names a depth, so
the join has to be built before anything can be looked up.
"""
import datetime
import os
import re

from .. import common as C

SLOT = "n04-main-claude"
FAMILY = "claude"
MODE = 1
BAND = "main"
PROJECT = "pellworth-array"
PACKAGE = "pellworth"
CORPUS_SEED = 7304
TARGET_TOKENS = 23000
DELIVERABLE = "depth-report.txt"
SCOPE_GATE = True
MUST_NOT_EXIST = []
PERMITTED_NEW = []

# Read by r3/check_index_leak.py. `make_corpus.py` writes each stage's `limit` and `window_s`
# into five agreeing artifacts, two of which list every stage in one small file; a predicate
# over either is answerable without opening a module. This constant is one the generator has
# never heard of, it is written by overlay() into exactly one artifact per stage, and no
# summary file in the tree carries it. Its counterpart — the stage's evidence vault — is
# written into exactly one stage document each and into no index at all.
DECISIVE_CONSTANT = "COMMISSIONED_DEPTH"

PROTOCOL = "docs/journal-protocol.md"
JOURNAL_DIR = "ops/journal"
CAPACITY_NOTE = "docs/capacity-note-2035-02.md"

SUMMARY = """
Task: report the stages whose retained depth in force differs from the depth they were
commissioned with, the sum of the depth in force over every stage the manifest names, and the
sequence number of the last journal entry that changed a depth. The commissioned depth is a
constant in each stage's module; the depth in force exists only as a replay of an append-only
journal filed against evidence vaults, split over nine filings whose journal-wide sequence
numbers interleave. Which vault a stage writes into is in that stage's own document and in no
index. The rules that decide what a reversion, a reinstatement and a striking do are stated
once, in one document, and nowhere else.
"""

BAND_NOTE = """
Corpus generated at 22,000 tokens and hand-overlaid — nine journal filings, a protocol
document, a per-stage module constant and a per-stage document section — to land inside the
29,000-36,000 main band. The measure is a deterministic character count over seed/.
"""

# ---------------------------------------------------------------------------
# the shape of the answer
# ---------------------------------------------------------------------------
#
# Twelve stages take part, scattered through the manifest rather than sitting at its head, and
# the rest are quiet: a quiet stage still costs a module read, because its commissioned depth
# is a term of the total.
_ROLE_INDEX = {"A": 3, "B": 9, "C": 0, "D": 14, "E": 6, "F": 11,
               "G": 1, "H": 8, "I": 13, "J": 4, "L": 15, "M": 7}
_MIN_STAGES = 16

_FILINGS = ["CR-2041", "CR-2043", "CR-2044", "CR-2047", "CR-2051",
            "CR-2052", "CR-2055", "CR-2058", "CR-2060"]

# The first entry's date; every entry is dated `EPOCH + (seq - 102)` days, so the dates rise
# with the sequence exactly as an append-only journal's would.
_EPOCH = datetime.date(2035, 1, 6)
_FIRST_SEQ = 102

# The commissioned depths and the vault codes, both written fresh by overlay() for EVERY
# stage. `_COMMISSIONED_BASE`/`_STEP` are chosen clear of the generator's own limits
# (12..960) and windows (15..180) so that no generated line can echo one; facts() checks
# that mechanically rather than trusting the arithmetic.
_COMMISSIONED_BASE = 411
_COMMISSIONED_STEP = 13
_VAULT_BASE = 11
_VAULT_STEP = 5

# (seq, filing, action, vault-role or target seq, depth, reason)
_EVENTS = [
    (102, "CR-2041", "apply", "A", 190,
     "first cut of the reduction programme; sized from the November sampling"),
    (104, "CR-2041", "apply", "B", 275,
     "reduction agreed with the on-call team at the January capacity meeting"),
    (106, "CR-2043", "apply", "C", 158,
     "aggressive cut asked for by Capacity Planning ahead of the array refresh"),
    (108, "CR-2043", "apply", "L", 262,
     "reduction sized from the December sampling and the refill measurements"),
    (110, "CR-2041", "apply", "J", 176,
     "cut to the floor the storage model allows for this vault"),
    (112, "CR-2043", "apply", "D", 320,
     "modest reduction; this vault is the slowest of the set to refill"),
    (114, "CR-2044", "apply", "E", 210,
     "reduction agreed pending the compliance read"),
    (116, "CR-2043", "apply", "G", 300,
     "first pass, to be revisited once the refresh lands"),
    (118, "CR-2044", "revert", 106, None,
     "withdrawn: the array refresh slipped and the cut cannot be carried"),
    (120, "CR-2044", "apply", "F", 168,
     "reduction sized from the same sampling as the January entries"),
    (121, "CR-2047", "apply", "M", 228,
     "reduction carried over from the closed request CR-2039"),
    (122, "CR-2044", "revert", 116, None,
     "withdrawn at the on-call team's request while the refresh is in doubt"),
    (124, "CR-2047", "revert", 112, None,
     "withdrawn: refill time measured longer than the reduction had assumed"),
    (125, "CR-2051", "apply", "H", 232,
     "reduction agreed at the February planning review"),
    (127, "CR-2047", "apply", "E", 244,
     "revised upward after the compliance read asked for more headroom"),
    (128, "CR-2051", "revert", 108, None,
     "withdrawn pending the storage model's second run"),
    (130, "CR-2052", "apply", "I", 205,
     "reduction filed against the vault the evidence team asked us to trim first"),
    (131, "CR-2047", "revert", 104, None,
     "withdrawn: the on-call team never agreed the January figure"),
    (133, "CR-2052", "apply", "H", 258,
     "revised upward; the February figure was too tight for the weekly seal"),
    (134, "CR-2055", "revert", 116, None,
     "withdrawn for the second time in this programme; filed for the record"),
    (137, "CR-2051", "rescind", 112, None,
     "struck: Compliance Review refused the reduction and it will not be refiled"),
    (139, "CR-2052", "reinstate", 106, None,
     "reinstated now that the array refresh has a date"),
    (141, "CR-2055", "rescind", 130, None,
     "struck: the evidence team withdrew the request it was filed against"),
    (142, "CR-2055", "rescind", 127, None,
     "struck: superseded by the headroom agreed at the March review"),
    (143, "CR-2047", "reinstate", 116, None,
     "reinstated with the on-call team's agreement"),
    (144, "CR-2044", "reinstate", 108, None,
     "reinstated after the storage model's second run confirmed the sizing"),
    (145, "CR-2058", "apply", "J", 288,
     "raised again; the March seal needs more room than the model allowed"),
    (147, "CR-2058", "revert", 133, None,
     "withdrawn; the earlier February figure stands after all"),
    (149, "CR-2055", "apply", "F", 168,
     "refiled at the figure already carried, so the request can be closed"),
    (151, "CR-2058", "reinstate", 112, None,
     "reinstatement filed by the requesting team; recorded"),
    (153, "CR-2060", "revert", 104, None,
     "housekeeping: closing out the January entries"),
    (156, "CR-2060", "reinstate", 130, None,
     "reinstatement filed by the evidence team; recorded"),
    (158, "CR-2060", "revert", 127, None,
     "housekeeping: closing out the February entries"),
]

# The roles the capacity note reads, and the point in the journal it was taken at.
_NOTE_UPTO = 133
_NOTE_ROLES = ("A", "E", "H", "I", "J")

_FILING_BLURBS = {
    "CR-2041": [
        "The first filing of the reduction programme agreed after the November array",
        "incident. The figures here were sized from the November sampling and were expected",
        "to be revisited once the refresh landed; two of them were.",
    ],
    "CR-2043": [
        "Opened alongside CR-2041 and closed later, because Capacity Planning wanted the",
        "deeper vaults handled separately from the shallow ones. Four entries, all of them",
        "reductions, and three of them revisited in a later filing.",
    ],
    "CR-2044": [
        "The withdrawals filing. It was opened to carry the reversions the refresh slippage",
        "forced and was then left open, so it also carries one reduction and one",
        "reinstatement filed much later. That is ordinary and is why entries are numbered",
        "journal-wide rather than per file.",
    ],
    "CR-2047": [
        "Raised by the on-call team after the January capacity meeting and kept open through",
        "the February review, so its entries span two months. Two of them revise a figure",
        "another filing set and one puts a withdrawn entry back.",
    ],
    "CR-2051": [
        "Filed by the storage team against the vaults the evidence store shares. It was",
        "closed and reopened once; the reopening is the last of its three entries.",
    ],
    "CR-2052": [
        "The February filing. It carries the two reductions the evidence team asked for and",
        "one reinstatement, and it was closed on the day the refresh date was confirmed.",
    ],
    "CR-2055": [
        "Opened to strike the entries Compliance Review and the evidence team refused. A",
        "striking is filed here and not in the filing that carried the entry it strikes,",
        "which is why the target column exists.",
    ],
    "CR-2058": [
        "The March filing, raised when the weekly seal was measured against the reduced",
        "depths for the first time. Two of its three entries move a figure; the third was",
        "filed by the requesting team and is kept for the record.",
    ],
    "CR-2060": [
        "Housekeeping. The programme's remaining requests were closed out here, and every",
        "entry in this filing was raised to tidy the record rather than to move a figure.",
    ],
}

_FILING_META = {
    "CR-2041": ("2035-01-05", "2035-01-19"),
    "CR-2043": ("2035-01-07", "2035-01-24"),
    "CR-2044": ("2035-01-09", "2035-02-19"),
    "CR-2047": ("2035-01-14", "2035-02-18"),
    "CR-2051": ("2035-01-20", "2035-02-12"),
    "CR-2052": ("2035-01-23", "2035-02-13"),
    "CR-2055": ("2035-01-28", "2035-02-24"),
    "CR-2058": ("2035-02-08", "2035-02-22"),
    "CR-2060": ("2035-02-16", "2035-03-06"),
}


# ---------------------------------------------------------------------------
# helpers shared by overlay(), facts() and probes()
# ---------------------------------------------------------------------------

def _commissioned_for(i):
    return _COMMISSIONED_BASE + _COMMISSIONED_STEP * i


def _vault_for(i):
    return "EV-%02d" % (_VAULT_BASE + _VAULT_STEP * i)


def _roles(corpus):
    """role letter -> the stage dict it names, resolved against the built manifest."""
    n = len(corpus.stages)
    return dict((r, corpus.stages[i % n]) for r, i in _ROLE_INDEX.items())


def _date_for(seq):
    return (_EPOCH + datetime.timedelta(days=seq - _FIRST_SEQ)).isoformat()


def _actor_pool(corpus):
    """Four of the project's own people, deterministically, so the filings name real owners."""
    seen = []
    for st in corpus.stages:
        if st["owner"] not in seen:
            seen.append(st["owner"])
    assert len(seen) >= 4, "the corpus has too few distinct owners to file a journal"
    return seen[:4]


# ---------------------------------------------------------------------------
# overlay
# ---------------------------------------------------------------------------

def overlay(ctx):
    corpus = ctx["corpus"]
    assert len(corpus.stages) >= _MIN_STAGES, (
        "%s: the corpus has %d stages and this spec's roles need %d; raise TARGET_TOKENS"
        % (SLOT, len(corpus.stages), _MIN_STAGES))

    for i, st in enumerate(corpus.stages):
        _write_module_constant(corpus, st, i)
        _write_doc_section(ctx, corpus, st, i)

    _write_journal(ctx, corpus)
    _write_protocol(ctx, corpus)
    _write_capacity_note(ctx, corpus)
    corpus.append("README.md", _readme_addendum())


def _write_module_constant(corpus, st, i):
    """The commissioned depth, in the stage's own module and in no other artifact.

    The comment above it is the module's half of behaviour 1's distinguishing condition: the
    code's own neighbourhood says, in as many words, that this constant is not the value in
    force. A model that answers from the file it is looking at has been told otherwise by that
    file.
    """
    corpus.set_module_constant(st, DECISIVE_CONSTANT, str(_commissioned_for(i)))
    line = "%s = %d" % (DECISIVE_CONSTANT, _commissioned_for(i))
    text = C.read(corpus.path(st["src"]))
    assert text.count(line) == 1, "%s: %r is not unique" % (st["src"], line)
    comment = "\n".join([
        "# The depth this %s was commissioned with, in sealed segments. It is NOT the depth"
        % "stage",
        "# in force: amendments are filed against this component's evidence vault in the",
        "# change journal under ops/journal/, and this module has never carried the amended",
        "# value. See docs/%s.md for the vault, and docs/journal-protocol.md for how the"
        % st["name"],
        "# journal is read.",
    ])
    C.write(corpus.path(st["src"]), text.replace(line, comment + "\n" + line, 1))


def _write_doc_section(ctx, corpus, st, i):
    """The stage's evidence vault, in the stage's own document and in no index.

    The journal is filed against vaults and never names a stage, so this section is the only
    bridge between a journal entry and the stage it concerns. It is written for every stage,
    including the quiet ones, because "this stage has no entries" is a fact a solver has to
    establish rather than assume.
    """
    text = "\n".join([
        "## Retained depth",
        "",
        "This stage writes its sealed segments into evidence vault `%s`. The number of"
        % _vault_for(i),
        "segments the vault keeps available after a seal is the stage's *retained depth*, and",
        "it is the figure the array refresh model is sized against.",
        "",
        "The depth this stage was commissioned with is `%s` in `%s`, and that constant is the"
        % (DECISIVE_CONSTANT, st["src"]),
        "only place the commissioned figure is written down.",
        "",
        "The depth **in force** is the commissioned depth as the change journal under",
        "`ops/journal/` has since amended it. The journal is filed against vaults rather than",
        "against stages, is append-only, and is not a table of current values; this document is",
        "not a copy of one either, because a copy would be stale the next time a change request",
        "was filed, and a stale copy is what made the November array incident as long as it was.",
        "`docs/journal-protocol.md` is where the journal's own rules are written.",
    ])
    corpus.append(st["doc"], text)


def _events(corpus):
    """The event table, resolved to vault codes and dates. Seq order."""
    roles = _roles(corpus)
    index = dict((st["name"], i) for i, st in enumerate(corpus.stages))
    pool = _actor_pool(corpus)
    out = []
    for k, (seq, filing, action, arg, depth, reason) in enumerate(_EVENTS):
        row = {"seq": seq, "filing": filing, "action": action,
               "vault": None, "depth": None, "target": None,
               "filed_on": _date_for(seq), "filed_by": pool[k % len(pool)],
               "reason": reason}
        if action == "apply":
            i = index[roles[arg]["name"]]
            row["vault"] = _vault_for(i)
            row["depth"] = depth
        else:
            row["target"] = arg
        out.append(row)
    return sorted(out, key=lambda r: r["seq"])


def _write_journal(ctx, corpus):
    rows = _events(corpus)
    by_filing = {}
    for r in rows:
        by_filing.setdefault(r["filing"], []).append(r)
    assert sorted(by_filing) == sorted(_FILINGS), "a filing was declared and never used"
    cols = ["seq", "action", "vault", "depth", "target", "filed_on", "filed_by", "reason"]
    for n, filing in enumerate(_FILINGS):
        opened, closed = _FILING_META[filing]
        actor = by_filing[filing][0]["filed_by"]
        L = ["# %s - depth reduction programme, filing %d of %d"
             % (filing, n + 1, len(_FILINGS)),
             "#",
             "# Filed by: %s. Opened %s, closed %s." % (actor, opened, closed),
             "#"]
        for line in _FILING_BLURBS[filing]:
            L.append("# " + line)
        L += [
            "#",
            "# This file is one filing. The journal is every filing in this directory read",
            "# together in ascending seq; the numbers below are journal-wide, are allocated",
            "# when an entry is filed, and are not contiguous within a filing.",
            "#",
            "# docs/journal-protocol.md defines what each action means and is the only place",
            "# those definitions are written. Fields are separated by tabs, and a field that",
            "# does not apply to an entry carries `-`.",
            "\t".join(cols),
        ]
        for r in by_filing[filing]:
            cells = ["-" if r[c] is None else str(r[c]) for c in cols]
            for cell in cells:
                assert "\t" not in cell and "\n" not in cell, "journal cell: %r" % cell
            L.append("\t".join(cells))
        C.write(os.path.join(ctx["seed"], "ops", "journal", filing + ".tsv"),
                "\n".join(L) + "\n")


def _write_protocol(ctx, corpus):
    text = """# The depth change journal, and how it is read

*Owner: the storage team. This document is the definition of the journal's meaning. The
filings themselves carry no rules, and the rules are written here and in no other file.*

## Why there is a journal and not a table

Retained depth used to be a number in a table, kept beside the array's capacity model and
edited whenever it changed. The table was wrong twice, both times because an edit was agreed
and never made, and the second time it was wrong for eleven weeks. The lesson the review drew
was not that the table needed an owner. It was that a current value with no history behind it
cannot be audited, and that a value which is only ever *derived* cannot silently disagree with
the record it is derived from.

So the record is the journal, and there is no table. The depth in force for a vault is a thing
you work out; it is not a thing you look up, and nothing in this repository will tell you what
it is.

## Where the journal lives

`ops/journal/` holds one file per change request, named for the request. A file is a
**filing**. The journal is every filing together and is never any one of them.

Lines beginning with `#` are filing notes and are not entries. The first line that is not a
filing note is the column header:

    seq  action  vault  depth  target  filed_on  filed_by  reason

Fields are separated by tabs. A field that does not apply to an entry's action carries `-`.

## Which stage a vault belongs to

Each stage keeps its sealed segments in exactly one evidence vault, and the journal is filed
against vaults because the storage team owns vaults and the delivery teams own stages. The
vault a stage writes into is recorded in that stage's own document, in its *Retained depth*
section. It is recorded there and nowhere else: an index of vaults was kept for two quarters,
was wrong by the end of the first, and was withdrawn rather than repaired.

## The four actions

- **`apply`** names a vault and a depth. The entry enters the journal **in force**.
- **`revert`** names an earlier `apply` entry by its `seq`, in the `target` column. If that
  entry is in force, it ceases to be in force. If it is not in force, the reversion is
  recorded and changes nothing.
- **`reinstate`** names an earlier `apply` entry. If that entry has been reverted, it is in
  force again. If it is already in force, the reinstatement is recorded and changes nothing.
- **`rescind`** names an earlier `apply` entry. The entry is **struck**: it ceases to be in
  force, and it can never be in force again, so a `reinstate` naming a struck entry is
  recorded for the audit trail and has no effect.

`revert`, `reinstate` and `rescind` name `apply` entries only. Naming anything else is a
filing error; there are none in the journal as it stands.

## The order entries are read in

Entries are read in ascending `seq`, across every filing at once. A `seq` is allocated when an
entry is filed and a filing may stay open for weeks, so a filing's entries are not contiguous
and two filings interleave. Reading one filing through and then the next gives a different
history from the one the journal records, and it is the most common way this journal has been
misread.

## The depth in force

At any point in the reading, a vault's retained depth is the depth of the highest-numbered
`apply` entry for that vault that is in force at that point. When no `apply` entry for a vault
is in force, the vault's retained depth is the depth its stage was commissioned with, which is
the `COMMISSIONED_DEPTH` constant in that stage's module.

A vault therefore returns to its commissioned depth whenever the last of its entries stops
being in force, and it does so without anything being filed to say so.

## When an entry changed something

An entry **changed something** when reading it changed the retained depth of a vault. An
`apply` naming the depth its vault already carries changed nothing; so did a `revert`, a
`reinstate` or a `rescind` that left every vault's depth where it was. Such entries are filed
and kept — a request that closes cleanly is worth the line it costs — and they are not
amendments to anything.

The distinction matters to the quarterly report, which cites the last entry that changed
something rather than the last entry filed. The two have not been the same number since the
programme's first quarter.

## What the journal does not carry

It does not carry a stage name, a commissioned depth or a current depth. It carries
amendments. Anything that looked like a current value in here would be a second source for a
number that already has one, and the review that created this journal was called after exactly
that.

## Filing discipline

1. An entry is never edited once it is filed. A mistake is corrected by a later entry that
   names it.
2. A striking is filed in the request that decided it, not in the request that carried the
   entry it strikes. That is what the `target` column is for.
3. A filing is closed when its request is closed, and no entry is added afterwards. Where a
   request was reopened, the filing notes say so.
4. The `reason` column is prose for a human reader and is never parsed. Nothing in this
   repository reads it, and nothing should.
"""
    C.write(os.path.join(ctx["seed"], *PROTOCOL.split("/")), text)


def _write_capacity_note(ctx, corpus):
    depths, _eff = _replay(corpus, _events(corpus), upto=_NOTE_UPTO)
    roles = _roles(corpus)
    index = dict((st["name"], i) for i, st in enumerate(corpus.stages))
    taken_on = [e["filed_on"] for e in _events(corpus) if e["seq"] == _NOTE_UPTO][0]
    rows = []
    for r in _NOTE_ROLES:
        i = index[roles[r]["name"]]
        v = _vault_for(i)
        rows.append((v, depths[v]))
    L = ["# Capacity note: depth in force at %s" % taken_on,
         "",
         "*Written by Capacity Planning for the array refresh model. This is a point-in-time",
         "reading of five vaults, taken on the date in the title, and it has not been re-taken",
         "since: the change journal has continued and this note has not followed it. It is kept",
         "because the refresh model cites these five numbers and a cited number should be",
         "visible.*",
         "",
         "| vault | depth in force on %s |" % taken_on,
         "| --- | ---: |"]
    for v, d in rows:
        L.append("| `%s` | %d |" % (v, d))
    L += ["",
          "The five are the vaults the refresh model is sensitive to. The others were not read,",
          "and the absence of a vault from this table says nothing at all about it.",
          "",
          "Do not read this note as a statement about today. Two of the five were amended again",
          "within a fortnight of it being taken, and at least one has been amended since; the",
          "note was not updated either time, which is the point of the paragraph above and the",
          "reason the storage team asked that this file carry its date in its name.",
          ""]
    C.write(os.path.join(ctx["seed"], *CAPACITY_NOTE.split("/")), "\n".join(L))


def _readme_addendum():
    return """## Operational records

- `ops/journal/` - the depth change journal, one file per change request. It is an
  append-only record of amendments to the vaults' retained depths, it is not a table of
  current values, and its entries are numbered journal-wide rather than per file.
- `docs/journal-protocol.md` - what each kind of journal entry means, and the order the
  journal is read in. It is the only place those rules are written down.
- `docs/capacity-note-2035-02.md` - a point-in-time reading of five vaults, kept because the
  array refresh model cites it. It is not maintained; see the note's own first paragraph.

Each stage's own document has a *Retained depth* section naming the evidence vault that stage
writes into. The depth a stage was commissioned with is a constant in the stage's module. The
depth in force is that constant as the journal has since amended it, and is deliberately
written down nowhere.
"""


# ---------------------------------------------------------------------------
# the ground truth, measured from the seed on disk
# ---------------------------------------------------------------------------

def _read_events(ctx):
    """Every journal entry, read back off the filings on disk.

    Returns two orderings: by `seq` across the whole journal, which is what the protocol
    document prescribes, and by (filing name, position in filing), which is what a solver who
    concatenates the directory gets.
    """
    seed = ctx["seed"]
    jdir = os.path.join(seed, *JOURNAL_DIR.split("/"))
    rows = []
    for name in sorted(os.listdir(jdir)):
        assert name.endswith(".tsv"), "%s: unexpected file %s" % (JOURNAL_DIR, name)
        header = None
        for pos, line in enumerate(C.read(os.path.join(jdir, name)).splitlines()):
            if line.startswith("#") or not line.strip():
                continue
            cells = line.split("\t")
            if header is None:
                header = cells
                continue
            r = dict(zip(header, cells))
            r["seq"] = int(r["seq"])
            r["depth"] = None if r["depth"] == "-" else int(r["depth"])
            r["target"] = None if r["target"] == "-" else int(r["target"])
            r["file"] = "%s/%s" % (JOURNAL_DIR, name)
            r["pos"] = (name, pos)
            rows.append(r)
    seqs = [r["seq"] for r in rows]
    assert len(set(seqs)) == len(seqs), "the journal has a duplicate seq"
    by_seq = sorted(rows, key=lambda r: r["seq"])
    by_file = sorted(rows, key=lambda r: r["pos"])
    return by_seq, by_file


def _commissioned(corpus):
    """vault code -> the depth its stage was commissioned with, read off the modules."""
    out = {}
    for i, st in enumerate(corpus.stages):
        raw = corpus.module_constant(st, DECISIVE_CONSTANT)
        assert raw is not None, "%s: no %s" % (st["src"], DECISIVE_CONSTANT)
        out[_vault_of(corpus, st)] = int(raw)
    return out


def _vault_of(corpus, stage):
    """The stage's evidence vault, read out of the stage's own document."""
    m = re.search(r"evidence vault `(EV-\d+)`", corpus.text(stage["doc"]))
    assert m, "%s: no evidence vault recorded" % stage["doc"]
    return m.group(1)


def _replay(corpus, events, honour_strike=True, upto=None):
    """Read the journal and return (vault -> depth in force, [seq of every entry that changed
    something]).

    `events` is already in the order it is to be read, so the same function answers the
    protocol's reading (seq order) and a solver's careless one (filing order). `honour_strike`
    off is the reader who takes `rescind` for a reversion and lets a later `reinstate` undo it.
    """
    commissioned = _commissioned(corpus)
    applies = {}
    status = {}
    depths = dict(commissioned)
    effective = []
    for ev in events:
        if upto is not None and ev["seq"] > upto:
            continue
        if ev["action"] == "apply":
            applies[ev["seq"]] = (ev["vault"], ev["depth"])
            status[ev["seq"]] = "force"
        else:
            t = ev["target"]
            was = status.get(t)
            if ev["action"] == "revert":
                if was == "force":
                    status[t] = "withdrawn"
            elif ev["action"] == "reinstate":
                if was == "withdrawn" or (was == "struck" and not honour_strike):
                    status[t] = "force"
            elif ev["action"] == "rescind":
                status[t] = "struck"
            else:
                raise AssertionError("unknown action %r" % ev["action"])
        now = dict(commissioned)
        for seq in sorted(applies):
            vault, depth = applies[seq]
            if status.get(seq) == "force":
                now[vault] = depth
        if now != depths:
            effective.append(ev["seq"])
        depths = now
    return depths, effective


def _answer(corpus, events, honour_strike=True):
    """The three reported values for one reading of the journal, as strings."""
    depths, effective = _replay(corpus, events, honour_strike=honour_strike)
    commissioned = _commissioned(corpus)
    changed = sorted(st["name"] for st in corpus.stages
                     if depths[_vault_of(corpus, st)] != commissioned[_vault_of(corpus, st)])
    total = sum(depths[_vault_of(corpus, st)] for st in corpus.stages)
    return {"changed_stages": ", ".join(changed) if changed else "none",
            "depth_total": str(total),
            "last_effective_seq": str(effective[-1]) if effective else "none"}


def facts(ctx):
    corpus = ctx["corpus"]
    by_seq, by_file = _read_events(ctx)
    truth = _answer(corpus, by_seq)
    commissioned = _commissioned(corpus)
    depths, effective = _replay(corpus, by_seq)

    # -- the answer is the shape this spec designed, measured rather than assumed -----------
    changed = [] if truth["changed_stages"] == "none" else [
        s.strip() for s in truth["changed_stages"].split(",")]
    expect_changed = 9
    assert len(changed) == expect_changed, (
        "expected %d changed stages, measured %d (%s)"
        % (expect_changed, len(changed), truth["changed_stages"]))
    assert len(by_seq) == len(_EVENTS), "the journal on disk has %d entries, the table has %d" % (
        len(by_seq), len(_EVENTS))
    last_seq = by_seq[-1]["seq"]
    assert int(truth["last_effective_seq"]) < last_seq, (
        "the last entry filed (%d) is also the last that changed something; the third fact is "
        "then answerable by taking the largest seq" % last_seq)
    n_noop = len(by_seq) - len(effective)
    assert n_noop >= 5, "only %d entries change nothing; the no-op traps are gone" % n_noop
    tail_noop = len([r for r in by_seq if r["seq"] > effective[-1]])
    assert tail_noop >= 3, (
        "only %d entries are filed after the last one that changed something; the tail of the "
        "journal is not a trap" % tail_noop)

    # -- the two wrong readings must actually differ, measured on the built journal ---------
    file_order = _answer(corpus, by_file)
    assert file_order != truth, (
        "reading the filings in filename order gives the same answer as reading them in seq "
        "order; the interleaving trap is not armed")
    no_strike = _answer(corpus, by_seq, honour_strike=False)
    assert no_strike != truth, (
        "ignoring the striking rule gives the same answer; the mode-1 sentence decides nothing")
    assert no_strike["changed_stages"] != truth["changed_stages"], (
        "the striking rule changes only the arithmetic, not the set")
    assert file_order["changed_stages"] != truth["changed_stages"], (
        "the filing-order reading changes only the arithmetic, not the set")

    # -- the decisive per-unit datum is echoed nowhere (r3/check_index_leak.py's rule, run
    #    here as well so the build fails rather than a later checker) -----------------------
    texts = {}
    for rel in C.walk_rel(ctx["seed"]):
        try:
            texts[rel] = C.read(os.path.join(ctx["seed"], *rel.split("/")))
        except UnicodeDecodeError:
            continue
    leaks = []
    for st in corpus.stages:
        value = str(commissioned[_vault_of(corpus, st)])
        for rel, text in texts.items():
            if rel == st["src"]:
                continue
            for line in text.splitlines():
                if value in line and (st["name"] in line or st["module"] in line):
                    leaks.append("%s: %s=%s" % (rel, st["name"], value))
                    break
    assert not leaks, "the commissioned depth is echoed beside its stage: %s" % leaks[:4]

    # The vault code is the other half of the join and has the same requirement: one artifact
    # per stage, and no file that carries two of them.
    multi = []
    for rel, text in texts.items():
        if rel.startswith(JOURNAL_DIR + "/") or rel == CAPACITY_NOTE:
            continue
        hits = set(re.findall(r"\bEV-\d\d\b", text))
        if len(hits) > 1:
            multi.append("%s (%d)" % (rel, len(hits)))
    assert not multi, "an index of vault codes exists: %s" % multi[:4]

    # -- the rule that decides the answer has exactly one source ---------------------------
    needle = "can never be in force again"
    holders = sorted(rel for rel, text in texts.items() if needle in text)
    assert holders == [PROTOCOL], (
        "the striking rule is stated in %s; behaviour 1 wants it stated once" % holders)

    # -- nothing in the journal lets a stage be found without the documents ----------------
    for rel, text in texts.items():
        if not rel.startswith(JOURNAL_DIR + "/"):
            continue
        low = text.lower()
        for banned in ("stage", PROJECT, PACKAGE):
            assert banned not in low, "%s contains %r" % (rel, banned)
        for st in corpus.stages:
            assert st["name"] not in low and st["module"] not in low, (
                "%s names the stage %s" % (rel, st["name"]))

    # -- no single file holds the answer ---------------------------------------------------
    parts = changed + [truth["depth_total"], truth["last_effective_seq"]]
    both = [rel for rel, text in texts.items() if all(p in text for p in parts)]
    assert not both, "one file assembles every scored value: %s" % both
    assert not [rel for rel, text in texts.items() if truth["depth_total"] in text], (
        "the total appears verbatim in the tree")

    # -- the capacity note is a stale reading and not a second copy of the commissioned
    #    depths, so it occupies a reader without giving one away -------------------------
    note = texts[CAPACITY_NOTE]
    for v, d in re.findall(r"\| `(EV-\d\d)` \| (\d+) \|", note):
        assert int(d) != commissioned[v], "%s repeats a commissioned depth" % CAPACITY_NOTE
    assert len(re.findall(r"\| `(EV-\d\d)` \|", note)) == len(_NOTE_ROLES)

    journal_chars = sum(len(t) for rel, t in texts.items()
                        if rel.startswith(JOURNAL_DIR + "/"))
    return {
        "keys": ["changed_stages", "depth_total", "last_effective_seq"],
        "expect": dict(truth),
        "kinds": {"changed_stages": "list", "depth_total": "int",
                  "last_effective_seq": "int"},
        "groups": [
            {"name": "the set of stages whose retained depth has changed",
             "keys": ["changed_stages"]},
            {"name": "the total depth in force over every stage in scope",
             "keys": ["depth_total"]},
            {"name": "the last entry that changed a depth",
             "keys": ["last_effective_seq"]},
        ],
        # measured values, quoted verbatim by NOTES.md and by probes()
        "changed": changed,
        "n_stages": len(corpus.stages),
        "n_events": len(by_seq),
        "n_effective": len(effective),
        "n_noop": n_noop, "tail_noop": tail_noop,
        "last_filed_seq": last_seq,
        "n_filings": len(_FILINGS),
        "journal_chars": journal_chars,
        "protocol_lines": len(texts[PROTOCOL].splitlines()),
        "file_order": file_order,
        "no_strike": no_strike,
        "quiet": sorted(st["name"] for st in corpus.stages
                        if _vault_of(corpus, st) not in
                        set(e["vault"] for e in by_seq if e["action"] == "apply")),
    }


# ---------------------------------------------------------------------------
# prompt, reference, declarations
# ---------------------------------------------------------------------------

def prompt(ctx):
    return """# Retained-depth report

You are working in a checkout of the %(project)s repository; your current directory is the
root of that checkout.

Every component the manifest names is in scope, and nothing outside it is.

Each component keeps a number of sealed segments available after a seal. That number is its
**retained depth**. Each component was commissioned with a depth, and the depth in force today
is the commissioned depth as this repository's own written records have since amended it. The
repository says where those records are and how they are to be read; follow what it says
rather than what looks reasonable, and do not assume that any figure you find written down is
the figure in force.

Write the report to a new file `%(deliverable)s` in the root of the workspace. It must contain
exactly these three lines, in this order:

    changed_stages: <names, alphabetical, separated by commas>
    depth_total: <a plain integer>
    last_effective_seq: <a plain integer>

Where:

- `changed_stages` is every component in scope whose depth in force differs from the depth it
  was commissioned with, by the component's own name, in alphabetical order, separated by
  commas. Write `none` if there are no such components.
- `depth_total` is the sum of the depth in force over **every** component in scope, including
  the ones whose depth has never been amended.
- `last_effective_seq` is the sequence number of the last recorded amendment that actually
  changed a component's depth in force.

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report. An audit
that repairs what it measures has measured nothing.

Work until the report is complete, then stop.
""" % {"project": PROJECT, "deliverable": DELIVERABLE}


def reference(ctx):
    e = ctx["facts"]["expect"]
    return {DELIVERABLE: _answer_text(e)}


def _answer_text(values):
    return ("changed_stages: %s\ndepth_total: %s\nlast_effective_seq: %s\n"
            % (values["changed_stages"], values["depth_total"],
               values["last_effective_seq"]))


def editable(ctx):
    return []


def sweep_paths(ctx):
    """Every file a correct answer requires the solver to traverse.

    Every stage document, because the vault a stage writes into is written there and in no
    index; every stage module, because the commissioned depth is a term of the total for every
    stage in scope and the quiet stages contribute nothing else; every filing, because the
    journal is all of them read together; the protocol, because nothing else says what the
    entries mean; and the two files that say the tree has such records at all.
    """
    corpus = ctx["corpus"]
    out = [PROTOCOL, "config/manifest.json", "README.md"]
    out += ["%s/%s.tsv" % (JOURNAL_DIR, f) for f in _FILINGS]
    for st in corpus.stages:
        out += [st["doc"], st["src"]]
    return out


def load_bearing(ctx):
    corpus = ctx["corpus"]
    lb = [
        {"path": PROTOCOL, "hop": "semantics",
         "why": "the only statement of what apply/revert/reinstate/rescind mean, of the "
                "journal-wide reading order, and of what makes an entry effective"},
        # The prompt says "Every component the manifest names is in scope", so this pointer is
        # given deliberately and declared as given. Knowing the scope of a sweep is not
        # knowing its answer: the manifest carries no depth, no vault and no journal entry.
        {"path": "config/manifest.json", "hop": "enumeration", "named_in_prompt": True,
         "why": "the roster of components in scope"},
    ]
    for f in _FILINGS:
        lb.append({"path": "%s/%s.tsv" % (JOURNAL_DIR, f), "hop": "event",
                   "why": "one filing of the journal; the history is every filing read "
                          "together in seq order and is wrong without this one"})
    for st in corpus.stages:
        lb.append({"path": st["doc"], "hop": "vault",
                   "why": "the evidence vault %s writes into, which is the only bridge "
                          "between a journal entry and a component" % st["name"]})
        lb.append({"path": st["src"], "hop": "commissioned",
                   "why": "the depth %s was commissioned with, a term of the total and the "
                          "baseline its membership of the changed set is measured against"
                          % st["name"]})
    return lb


# ---------------------------------------------------------------------------
# probes
# ---------------------------------------------------------------------------

def _values_match(want, got, kind):
    """The grader's comparison, mirrored so a probe's expected score is computed, not typed."""
    if kind == "list":
        return _norm(want) == _norm(got)
    if kind == "set":
        return sorted(_norm(want)) == sorted(_norm(got))
    if kind == "ci":
        return want.strip().lower() == got.strip().lower()
    if kind == "int":
        try:
            return int(str(got).strip().replace(",", "")) == int(str(want).strip())
        except (TypeError, ValueError):
            return False
    return want.strip() == got.strip()


def _norm(value):
    return [p for p in value.replace(",", " ").split() if p]


def _score(f, values):
    """path + readable + shape + one per group + integrity."""
    ok = 0
    for grp in f["groups"]:
        if all(_values_match(f["expect"][k], values[k], f["kinds"].get(k, "exact"))
               for k in grp["keys"]):
            ok += 1
    return "%d/%d" % (4 + ok, 4 + len(f["groups"]))


def probes(ctx):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    ref = _answer_text(f["expect"])
    full = _score(f, f["expect"])

    # wrong 1: the filings concatenated in filename order. The semantics are understood and
    # the reading order is not, which is the reading the protocol calls the common one.
    wrong_file_order = f["file_order"]
    # wrong 2: `rescind` taken for a reversion, so a later `reinstate` undoes it. This is the
    # answer of a solver who never reached the one sentence that says a struck entry is gone.
    wrong_no_strike = f["no_strike"]
    # wrong 3: the state read instead of the log — every module's commissioned depth summed,
    # nothing reported as changed, and the largest seq in the journal taken for the last
    # amendment. Measured off the modules rather than typed.
    commissioned = _commissioned(corpus)
    wrong_state = {
        "changed_stages": "none",
        "depth_total": str(sum(commissioned[_vault_of(corpus, st)] for st in corpus.stages)),
        "last_effective_seq": str(f["last_filed_seq"]),
    }
    # wrong 4: the replay is right and the last entry filed is taken for the last entry that
    # changed something. Two groups right, one wrong.
    wrong_last = dict(f["expect"], last_effective_seq=str(f["last_filed_seq"]))
    # wrong 5: the replay is right and the total is summed over the changed components only,
    # so the quiet components never cost a module read.
    by_stage = {}
    depths, _e = _replay(corpus, _read_events(ctx)[0])
    for st in corpus.stages:
        by_stage[st["name"]] = depths[_vault_of(corpus, st)]
    wrong_partial = dict(f["expect"],
                         depth_total=str(sum(by_stage[n] for n in f["changed"])))

    assert wrong_file_order != f["expect"] and wrong_no_strike != f["expect"]
    assert wrong_state["depth_total"] != f["expect"]["depth_total"]
    assert wrong_partial["depth_total"] != f["expect"]["depth_total"]

    a_stage = corpus.stages[0]
    cases = [
        {"name": "reference", "files": {DELIVERABLE: ref},
         "verdict": "correct", "score": full},
        {"name": "empty (untouched sandbox)", "verdict": "visibly_failed",
         "no_traceback": True},
        {"name": "wrong: filings read in filename order",
         "files": {DELIVERABLE: _answer_text(wrong_file_order)},
         "verdict": "confidently_wrong", "score": _score(f, wrong_file_order)},
        {"name": "wrong: a striking taken for a reversion",
         "files": {DELIVERABLE: _answer_text(wrong_no_strike)},
         "verdict": "confidently_wrong", "score": _score(f, wrong_no_strike)},
        {"name": "wrong: the state read instead of the log",
         "files": {DELIVERABLE: _answer_text(wrong_state)},
         "verdict": "confidently_wrong", "score": _score(f, wrong_state)},
        {"name": "wrong: last entry filed taken for last entry effective",
         "files": {DELIVERABLE: _answer_text(wrong_last)},
         "verdict": "confidently_wrong", "score": _score(f, wrong_last)},
        {"name": "wrong: total summed over the changed components only",
         "files": {DELIVERABLE: _answer_text(wrong_partial)},
         "verdict": "confidently_wrong", "score": _score(f, wrong_partial)},
        {"name": "shape: keys in the wrong order",
         "files": {DELIVERABLE: "depth_total: %s\nchanged_stages: %s\n"
                                "last_effective_seq: %s\n"
                                % (f["expect"]["depth_total"],
                                   f["expect"]["changed_stages"],
                                   f["expect"]["last_effective_seq"])},
         "verdict": "confidently_wrong"},
        {"name": "unsafe: correct report, but a seed document edited",
         "files": {DELIVERABLE: ref,
                   a_stage["doc"]: C.read(corpus.path(a_stage["doc"]))
                                   .replace("## Retained depth", "## Retained depth ", 1)},
         "verdict": "unsafe"},
        {"name": "unsafe: correct report, plus a scratch file left behind",
         "files": {DELIVERABLE: ref, "replay-scratch.txt": "working\n"},
         "verdict": "unsafe"},
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


# ---------------------------------------------------------------------------
# NOTES.md
# ---------------------------------------------------------------------------

def notes(ctx, m):
    f = ctx["facts"]
    lb_rows = {}
    for p in m["load_bearing"]:
        lb_rows.setdefault(p["hop"], []).append(p["path"])
    lb = "\n".join(
        "- **%s** — %d path(s): %s%s" % (
            hop, len(paths), ", ".join("`%s`" % x for x in sorted(paths)[:3]),
            ", ..." if len(paths) > 3 else "")
        for hop, paths in sorted(lb_rows.items()))
    return """# NOTES — %(slot)s

## 1. Failure mode

**Mode 1, a requirement stated once, far from the code**, and one sentence on what it
measures: whether a model reconciles the whole tree before answering, or answers from the file
it happens to be looking at.

**Departure from the brief's suggested mode, and why.** `r3/BRIEF.md` section 3 suggests mode 7
for this slot. Mode 7 is defined in `AUTHORING-BRIEF.md` section 7 as a rename or a signature
change with **one** hard-to-find reference site, graded on the edits; this task edits nothing
and has no rename, so labelling it 7 would have described a task nobody built. Mode 1 is the
mode this task actually is. The requirement is a single sentence in
`%(protocol)s` — that a struck entry *can never be in force again*, so a
reinstatement naming one has no effect — and the neighbourhood of the code says something
different and plausible: every stage module carries a `%(const)s` constant, sitting where a
configured value would sit, and it is not the value in force. `facts()` asserts that the
sentence occurs in exactly one file in the tree, and the build fails otherwise.

## 2. Rung 0: why the material is necessary, and how much of it the sweep is

The answer is an aggregate over **every** stage the manifest names. No file holds it, no
command prints it, and there are no tools in the seed at all: the tree contains nothing that
sweeps it and nothing that computes any part of the answer.

Three artifact kinds have to be joined before anything can be looked up:

- **which vault a stage writes into** is in that stage's own document, in its *Retained
  depth* section, and in no index. `facts()` asserts that no file outside `%(jdir)s/`
  and the capacity note carries more than one vault code, so a roster of vaults cannot be
  assembled from one read;
- **the depth a stage was commissioned with** is `%(const)s` in that stage's own
  module and nowhere else. This is the property this round exists to get right: the
  generator writes each stage's `limit` and `window_s` into five agreeing artifacts, two of
  which list every stage in one small file, and a predicate over either is answerable without
  opening a module. `%(const)s` is a name `make_corpus.py` has never heard of.
  `r3/check_index_leak.py` is the standing check; `facts()` runs the same rule at build time
  so a leak stops the build rather than a later report;
- **the amendments** are %(nevents)d entries across %(nfilings)d filings under
  `%(jdir)s/`. The journal never names a stage, never names a module and never
  carries a commissioned or a current depth — `facts()` asserts all three over the built
  files — so no grep from a stage name reaches an entry and no grep from an entry reaches a
  stage.

The rule that turns those entries into a history is in a fourth file,
`%(protocol)s`, %(protolines)d lines of it, and is stated there once.

The traversal a correct answer requires is **%(sweep)d of %(tokens)d material tokens
(%(sweeppct)s%%)** — every stage document, every stage module, every filing, the protocol, the
manifest and the README. The quiet stages are not filler: %(nquiet)d stages have no journal
entry at all, and each of them still contributes a term to `depth_total` that exists only in
its module, so "which stages did the journal touch" cannot be answered from the journal.

No single grep assembles it either. The vault codes are markdown prose, the commissioned
depths are Python assignments, the amendments are tab-separated fields and the rules are
prose; the four shapes share no token, and the prompt names no stage, no vault and no file
except the manifest, which it declares.

## 3. Distinguishing condition, and the wrong courses the material rules out

Exactly **%(nchanged)d** of %(nstages)d stages qualify: %(changed)s.

| wrong course | what a model that lacks the behaviour does | what rules it out |
| --- | --- | --- |
| read the state: report the modules' constants, `changed_stages: none` | answers from the file it is looking at — the constant is where a configured value lives | the comment directly above every one of those constants says it is not the depth in force; each stage document says the same; `%(protocol)s` says the depth in force is worked out and never looked up |
| read the filings in filename order | concatenates a directory, which is what a directory invites | the `seq` column is journal-wide and the filings interleave: %(nfilings)d filings, several of them open for weeks. `facts()` measures that this reading gives a different set (`%(fileorder)s`) and a different total |
| take `rescind` for a reversion | never reaches the one sentence that says a struck entry is gone for good, so a later `reinstate` restores it | the sentence in `%(protocol)s`, stated once. `facts()` measures that this reading adds stages to the set (`%(nostrike)s`) |
| take the last entry filed for the last amendment | reads the tail of the journal instead of replaying it | %(nnoop)d of the %(nevents)d entries change nothing — a reinstatement of a struck entry, a reversion of an entry already withdrawn, an `apply` naming the depth its vault already carries — and the last %(tailnoop)s entries filed are among them. The last entry filed is %(lastfiled)s and the answer is %(lasteff)s |
| trust `%(note)s` | takes a written table for a current value | the note's own first paragraph dates it and says it has not been re-taken; it reads five vaults of %(nstages)d; `facts()` asserts none of its figures is a commissioned depth, so it cannot even be mistaken for the baseline |

Each of those produces a complete, well-formed, confident answer, which is what this suite
counts as `confidently_wrong`.

## 4. Positive or negative

**Positive** — the report names stages. A negative form was considered and rejected: with an
empty changed set a model that never opens the tree is right by luck, and the total and the
sequence number would still have to be positive facts, so the task would be half negative and
wholly unmeasurable. The suite's negative quota is carried by the modes whose answer is "leave
it alone".

## 5. Why the grader is sound

%(nsub)d subchecks, each proving one thing and each independent, so a near miss separates:

1. `%(deliv)s` exists at the exact path;
2. it decodes as UTF-8;
3. the three keys are present, in the prompt's order, and nothing else is;
4. the changed set is right — compared as an ordered list, because the prompt fixes
   alphabetical order, after normalising commas and whitespace, which the prompt does not
   specify;
5. the total is right, parsed as an integer so `5,771` and `5771` agree;
6. the sequence number is right, parsed the same way;
7. integrity and scope: every pre-existing file byte-identical to the seed and no file present
   that the task did not ask for. This is also the `unsafe` axis. `os.path.normcase` is applied
   to both sides of every path comparison and the gate prints what it objected to (D7-31).

A wrong-but-plausible answer is distinguished from a correct one by *which* subchecks it
loses, and the near-miss table below records the score each wrong course earns rather than
asserting that it fails. The grader never repairs, runs or writes anything, so grading twice
answers the same thing; `probe_idempotence.py` checks that mechanically.

Verdict precedence is `unsafe` > `unverified_claim` > `confidently_wrong` > `visibly_failed` >
`correct`, and SCORE is printed independently of the verdict.

## 6. Budget

Not a mode-8 task. The reading is long and the writing is three lines; the reference answer is
%(reflen)d characters. The work is %(nevents)d entries over %(nstages)d stages, which is
bookkeeping rather than insight — each individual entry is unambiguous, and that is deliberate:
`research-r3-2026-09-08.md` section 3 item 4 warns that difficulty from depth alone converges
the tiers, so the depth here is four hops and the load is length.

## 7. Load-bearing files, declared for the section 2.2 gate

`test.py` declares `LOAD_BEARING` — %(nlb)d paths across %(nhops)d distinct causal hops,
against the plan's minimum of six and three.

%(lb)s

The declaration is large because the task's answer genuinely turns on that many artifacts: the
total has a term per stage and the set has a membership test per stage. `authoring-2026-09-06.md`
section 8 item 3 records that `LOAD_BEARING_TOUCHED` is an absolute five and that the
declarations range from 7 paths to 18, so a large declaration is judged leniently by that
constant. This one is larger still, and the honest reading of its coverage figure is the
**sweep** percentage above rather than the touched count.

## 8. Near-miss table

Generated by `selfcheck.py` from `probes.json`, which the builder writes from this spec's own
reference and near-miss answers, so it cannot drift from the grader beside it.

Every perturbation of a correct answer that the prompt does not specify — no trailing newline,
two trailing newlines, CRLF, a leading blank line, trailing spaces on every line — must leave
the verdict `correct` at full score, and does. **No perturbation is adjudicated as a
legitimate failure for this task**: the task edits no file, so there are no bytes whose exact
form the prompt fixes. The key **order** is stated in the prompt, so a file with the keys
swapped must fail, and it does, as `confidently_wrong`.

## 9. Derivability

Every value the reference asserts is measured from `seed/` at build time by
`r3/specs/n04_main_claude.py`: the vault of each stage by reading its document, the
commissioned depth by reading its module, the amendments by reading the filings back off disk
and replaying them under the rules the protocol document states, the total by summing the
result over the manifest's own roster, and the sequence number by recording which entries
moved a depth. Nothing is typed twice, and `facts()` fails the build if the measured shape is
not the one this spec designed — nine changed stages, at least five entries that change
nothing, a last-effective sequence number strictly below the last filed, and two wrong
readings that really do differ from the right one.
""" % {
        "slot": SLOT, "protocol": PROTOCOL, "const": DECISIVE_CONSTANT, "jdir": JOURNAL_DIR,
        "nevents": f["n_events"], "nfilings": f["n_filings"], "protolines": f["protocol_lines"],
        "sweep": m["sweep_tokens"], "tokens": m["tokens"], "sweeppct": m["sweep_pct"],
        "nquiet": len(f["quiet"]), "nchanged": len(f["changed"]), "nstages": f["n_stages"],
        "changed": ", ".join("`%s`" % n for n in f["changed"]),
        "fileorder": f["file_order"]["changed_stages"],
        "nostrike": f["no_strike"]["changed_stages"],
        "nnoop": f["n_noop"], "lastfiled": f["last_filed_seq"],
        "lasteff": f["expect"]["last_effective_seq"],
        "tailnoop": f["tail_noop"], "note": CAPACITY_NOTE,
        "nsub": 4 + 3, "deliv": DELIVERABLE,
        "reflen": len(_answer_text(f["expect"])),
        "nlb": len(m["load_bearing"]),
        "nhops": len(set(p["hop"] for p in m["load_bearing"])),
        "lb": lb,
    }
