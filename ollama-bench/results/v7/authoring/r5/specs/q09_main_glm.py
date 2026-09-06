"""q09-main-glm — behaviour 9, reading past the first screen, on a long serial state.

Shape A (r5/BRIEF.md section 4): the answer is produced by a chain of thirty-nine ordered
steps. Each entry of the settlement log names the entry it seals against, so entry k is
found only through entry k-1's own identifier, and each entry adjusts the running
settlement figure that the next entry starts from. A mistake at entry three moves every
checkpoint after it. The deliverable states the figure after every fifth entry and at the
chain's end, so the grader records where the chain broke rather than only that it did.

Behaviour 9 lives in the placements: the replay rules — which rows take effect, where each
entry's figure comes from, what order the entries are applied in, where the replay starts —
sit past line 200 of a long procedure page, and the chain's opening entry sits past
character 6,000 of a long viewer output (and past character 4,000 of the log itself). Both
placements are measured by `facts()`, which fails the build rather than let NOTES.md claim
them.

Rung 0: no file holds the answer, the prompt names no load-bearing file, and the per-step
running figures occur nowhere under seed/ — a grep can gather figures, but the entries they
belong to are reachable only by walking the chain, and a serial replay of thirty-nine
dependent steps is the work the task is for.
"""
import csv
import datetime
import io
import os
import re
import subprocess
import sys
import textwrap

from .. import common as C


SLOT = "q09-main-glm"
FAMILY = "glm"
MODE = 9
PROJECT = "kestrel-turn"
PACKAGE = "kestrel"
CORPUS_SEED = 6117
TARGET_TOKENS = 26500
DELIVERABLE = "settlement-report.txt"
BAND = "main"
SCOPE_GATE = True
MUST_NOT_EXIST = []
PERMITTED_NEW = []

SUMMARY = """
Task: replay this cycle's carryover settlement and report the running settlement figure
after every fifth entry and at the end of the chain. The settlement log is a chained event
log whose filing order and dates are not the replay order; each entry's figure is not in
the log but in the named stage's own material, and the rules that say which rows take
effect, where each figure comes from, and where the replay starts sit past line 200 of the
settlement procedure. An earlier quarter's filed summary states a figure that is complete,
plausible, and stale.
"""

BAND_NOTE = """
Corpus generated at 26,500 target tokens and hand-overlaid with the settlement procedure,
the chained settlement log, the log viewer, the per-stage settlement figures and one stale
close summary; the measured seed is required to land in the 29,000-36,000 main band.
"""

# ---------------------------------------------------------------------------
# overlay paths and names
# ---------------------------------------------------------------------------
HANDBOOK = "docs/handbook/settlement-procedure.md"
LOG = "data/settlement-log.csv"
STATUS_TOOL = "tools/settlement_status.py"
STALE_SUMMARY = "docs/settlement-summary-2036-q2.md"
CARRIED_ROW = "carried"
ABSORB_CONST = "ABSORB_UNITS"
REPLAY_HEADING = "## Replay rules"
STALE_FIGURE = 612          # even, so it can never equal a running figure

# Read by r2/check_index_leak.py: the absorb figure is written once, into the stage's own
# module, and nowhere else beside the stage's name. The carried figure gets the same
# one-source guarantee from facts()'s own assertion, because the checker takes one
# constant template and the task has two per-stage figures.
DECISIVE_CONSTANT = ABSORB_CONST

CHECKPOINT_STEPS = (5, 10, 15, 20, 25, 30, 35)
KEYS = tuple("figure_after_%02d" % k for k in CHECKPOINT_STEPS) + ("figure_final",)


# ---------------------------------------------------------------------------
# the chain, chosen deterministically from the generated stage list
# ---------------------------------------------------------------------------
def _coprime(n, skip=()):
    for s in (5, 7, 11, 3, 13, 17, 23, 29):
        if n % s and s not in skip:
            return s
    raise AssertionError("no coprime stride for n=%d" % n)


def _chain_stages(corpus):
    """Permutation of stage indexes: every stage carries once and relieves once, and the
    carry and the relief of a pair visit the same stage — a stage's held-back balance is
    admitted and then partly taken back within the pair, so each pair moves the figure up
    by that stage's own net and the replay is a strict ladder."""
    n = len(corpus.stages)
    s1 = _coprime(n)
    perm = [(s1 * j + 3) % n for j in range(n)]
    assert sorted(perm) == list(range(n))
    return perm


def _entry_kinds(corpus):
    """The chain as (kind, stage index), in replay order: rebase, then carry/relief pairs."""
    perm = _chain_stages(corpus)
    out = [("rebase", perm[0])]
    for j in range(len(corpus.stages)):
        out.append(("carry", perm[j]))
        out.append(("relief", perm[j]))
    return out


def _props(corpus, off):
    """Per-stage (carried, absorb), even, 3-digit, kept in a low band (128-252) so the
    running figures — which start at a stage's basis, carried plus absorb, and only ever
    rise — live in a band the stage figures never enter. Disjointness by construction;
    the offset loop still asserts it against the tree."""
    n = len(corpus.stages)
    carried = [192 + 6 * ((7 * i + 3 * off) % 13) for i in range(n)]
    delta = [16 + 2 * ((11 * (i + 2 * off)) % 19) for i in range(n)]
    absorb = [carried[i] - delta[i] for i in range(n)]
    return carried, absorb


def _apply(states_seq, props_by_index):
    """Replay a (kind, stage index) sequence; returns the running figure after each entry."""
    fig = 0
    out = []
    for kind, si in states_seq:
        carried, absorb = props_by_index[si]
        if kind == "rebase":
            fig = carried + absorb
        elif kind == "carry":
            fig += carried
        elif kind == "relief":
            fig -= absorb
        else:
            raise AssertionError(kind)
        out.append(fig)
    return out


def _checkpoints(states):
    return [states[k - 1] for k in CHECKPOINT_STEPS] + [states[-1]]


def _forbidden_numbers(seed):
    """Every 3-4 digit standalone number in the tree so far, as strings."""
    pat = re.compile(r"(?<![0-9A-Za-z_])([0-9]{3,4})(?![0-9A-Za-z_])")
    out = set()
    for rel in C.walk_rel(seed):
        text = C.read(os.path.join(seed, *rel.split("/")))
        for m in pat.finditer(text):
            out.add(m.group(1))
    return out


# ---------------------------------------------------------------------------
# overlay
# ---------------------------------------------------------------------------
def overlay(ctx):
    corpus = ctx["corpus"]
    seed = ctx["seed"]
    stages = corpus.stages
    n = len(stages)
    assert n >= 13, "expected at least 13 generated stages, got %d" % n

    kinds = _entry_kinds(corpus)
    limits = set(str(s["limit"]) for s in stages)
    limits.update(str(s["window"]) for s in stages)

    # Per-stage figures: shift the whole family until the running figures collide with
    # nothing in the tree and no figure equals a stage limit (the operations table puts a
    # stage's name and its limit on one line, and the leak check would read that as an
    # echo). Deterministic: the first offset that satisfies the tests is the one used.
    forbidden = _forbidden_numbers(seed)
    chosen = None
    for off in range(200):
        carried, absorb = _props(corpus, off)
        figs = set(str(x) for x in carried + absorb)
        if figs & limits:
            continue
        states = _apply(kinds, list(zip(carried, absorb)))
        # a running figure must collide with nothing in the final tree: neither with the
        # generated tree's numbers nor with the figures this overlay itself writes
        seen = forbidden | figs | {str(STALE_FIGURE)}
        if any(str(x) in seen for x in states):
            continue
        if len(set(states)) != len(states) or min(states) < 100:
            continue
        chosen = (off, carried, absorb, states)
        break
    assert chosen, "no figure offset avoids every number in the generated tree"
    _off, carried, absorb, _states = chosen

    for i, st in enumerate(stages):
        corpus.add_doc_config_row(
            st, CARRIED_ROW, str(carried[i]),
            "the units this stage carries into the close, fixed at the review")
        corpus.set_module_constant(st, ABSORB_CONST, str(absorb[i]))

    _write_log(ctx, kinds, carried, absorb)
    _write_handbook(ctx)
    _write_status_tool(ctx)
    _write_stale_summary(ctx, corpus)

    corpus.append("README.md", _readme_addendum())

    # make_corpus.py points at docs/policy/ from two index files whether or not the tree
    # has one; this tree's rules live under docs/handbook/, so the pointers are corrected
    # rather than left dangling at exactly the place a reader is sent.
    if not os.path.isdir(os.path.join(seed, "docs", "policy")):
        for rel in ("README.md", "docs/operations.md"):
            text = C.read(corpus.path(rel))
            if "docs/policy/" in text:
                corpus.replace_in(rel, "docs/policy/", "docs/handbook/",
                                  count=text.count("docs/policy/"))


def _entry_id(k):
    return "sc-%03d" % (100 + k)


def _dates(kinds):
    """sealed_on per chain position: distinct, scattered over the cycle, never ordered."""
    base = datetime.date(2036, 7, 1)
    out = {}
    for k in range(1, len(kinds) + 1):
        out[k] = (base + datetime.timedelta(days=(14 * k) % 73)).isoformat()
    assert len(set(out.values())) == len(kinds)
    return out


def _detail(kind, stage, owner, j):
    if kind == "rebase":
        return ("opens the cycle from the %s stage's balance at the previous close "
                "per the procedure and the review of the filing" % stage)
    if kind == "carry":
        return [
            "admits the balance held back at the previous close as minuted at the review",
            "brings the stage's held-back balance into this cycle on the clerk's signing",
            "admits the held-back balance for this stage restated at the review and filed",
        ][j % 3]
    return [
        "returns what the stage can take back this cycle per the review note as written",
        "clears the take-back agreed for this stage at the review before the close",
        "returns the agreed take-back to the figure on the reviewer's countersignature",
    ][j % 3]


def _log_rows(ctx, kinds, carried, absorb):
    """The log as filed: chain rows in a scrambled filing order, then void rows among them."""
    corpus = ctx["corpus"]
    stages = corpus.stages
    dates = _dates(kinds)
    carry_j = relief_j = 0
    chain = []
    for k, (kind, si) in enumerate(kinds, 1):
        stage = stages[si]
        if kind == "carry":
            detail, carry_j = _detail(kind, stage["name"], stage["owner"], carry_j), carry_j + 1
        elif kind == "relief":
            detail, relief_j = _detail(kind, stage["name"], stage["owner"], relief_j), relief_j + 1
        else:
            detail = _detail(kind, stage["name"], stage["owner"], 0)
        actor = stages[(si + 5) % len(stages)]["owner"]
        chain.append({
            "entry": _entry_id(k), "previous": "" if k == 1 else _entry_id(k - 1),
            "sealed_on": dates[k], "actor": actor, "kind": kind, "stage": stage["name"],
            "status": "sealed", "detail": detail, "k": k,
        })
    assert sum(1 for r in chain if r["kind"] == "carry") == len(stages)
    assert sum(1 for r in chain if r["kind"] == "relief") == len(stages)

    # three void rows, kept as filed: one drafted against nothing at all (the earliest
    # date in the log), two sealing against live entries. None is applied; the procedure's
    # replay rules say so, past line 200 of the procedure page.
    voids = [
        {"entry": "sc-100", "previous": "", "sealed_on": "2036-06-24",
         "actor": stages[2]["owner"], "kind": "rebase", "stage": stages[7]["name"],
         "status": "void", "detail": "opening draft superseded before the log was sealed"},
        {"entry": "sc-140", "previous": _entry_id(9), "sealed_on": "2036-08-27",
         "actor": stages[4]["owner"], "kind": "relief", "stage": stages[11]["name"],
         "status": "void", "detail": "filed twice after a clerk re-run and withdrawn"},
        {"entry": "sc-141", "previous": _entry_id(21), "sealed_on": "2036-09-01",
         "actor": stages[6]["owner"], "kind": "carry", "stage": stages[13]["name"],
         "status": "void", "detail": "withdrawn at the review before sealing"},
    ]

    # filing order: a stride permutation of the chain, voids inserted among them. Filing
    # order, date order and chain order are three different orders, and the procedure says
    # in as many words that only the chain is the replay order.
    total = len(kinds)
    stride = _coprime(total, skip=())
    stride = stride if stride != 1 else 5
    by_slot = {}
    for k in range(1, total + 1):
        slot = ((34 * k) % total) + 1
        by_slot[slot] = chain[k - 1]
    rows = [by_slot[i] for i in range(1, total + 1)]
    for pos, void in zip((4, 16, 40), voids):
        rows.insert(pos, void)
    return rows


def _write_log(ctx, kinds, carried, absorb):
    rows = _log_rows(ctx, kinds, carried, absorb)
    cols = ["entry", "previous", "sealed_on", "actor", "kind", "stage", "status", "detail"]
    lines = [",".join(cols)]
    for r in rows:
        cells = [r[c] for c in cols]
        assert not any("," in cell or '"' in cell for cell in cells), r
        assert not any(ch.isdigit() for ch in r["detail"]), r
        lines.append(",".join(cells))
    C.write(os.path.join(ctx["seed"], *LOG.split("/")), "\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# the procedure page. Behaviour 9's long file: the replay rules sit past line 200, and
# everything before them is the institution around the settlement — real, readable, and
# deliberately silent about the rules.
# ---------------------------------------------------------------------------
_SECTIONS = [
    ("What the settlement is", [
        "At the close of every cycle the platform settles carryover: the balance of held-"
        "back work that each stage brings out of the closing cycle and the platform takes "
        "into the next one. The settlement reduces all of that to one number, the "
        "settlement figure, denominated in the same units the assembler uses for its own "
        "limits. The figure is quoted on the cycle's dashboards, in the quarterly review "
        "pack, and in any incident review that touches capacity.",
        "The settlement is not an adjustment of the stages themselves. No stage's own "
        "configuration is read, written or rebalanced by a settlement. The figure is an "
        "accounting of the platform as a whole, and it moves only through the settlement "
        "log.",
        "A settlement is a replay, and the word is used deliberately. The clerk does not "
        "read the figure off anything. The clerk rebuilds it, entry by entry, from the "
        "cycle's log, in the order the log itself prescribes, and the figure at the end of "
        "the replay is the figure the close reports.",
    ]),
    ("What the settlement is not", [
        "It is not the assembler's accounting. The `limit` and `window_s` figures on a "
        "stage's page are the assembler's, they are echoed in five places each, and none "
        "of them is a settlement figure. A settlement figure never appears in a manifest "
        "section, and a manifest number is never a settlement figure.",
        "It is not billing. Nothing in the settlement is denominated in money, and no "
        "settlement paper is ever sent to Finance. The units are pipeline units and stay "
        "that way.",
        "It is not retention. How long settlement paper is kept is the archive's business "
        "and is governed by the retention policy, not by this page.",
    ]),
    ("Who runs it", [
        "One settlement clerk prepares the log, files each entry as the cycle produces it, "
        "and closes the cycle. One reviewer countersigns. The clerk and the reviewer may "
        "not be the same person, and an entry with a single signature is not a filed "
        "entry; it is a draft, whatever it looks like.",
        "Stage owners do not file settlement entries. A stage owner who believes the "
        "settlement has mis-stated their stage writes to the clerk, who corrects by filing "
        "new entries and never by editing filed ones. A filed entry is evidence.",
        "The reviewer's countersignature means the replay was checked, not that the "
        "reviewer re-derived it. Whoever re-derives the figure later does so from the log, "
        "and from nothing else.",
    ]),
    ("Cadence and calendar", [
        "A cycle runs to the quarter. The log opens a few days before the cycle's first "
        "entry, stays open while the cycle runs, and closes when the close summary is "
        "filed. Entries carry the date they were sealed, which is the day the clerk signed "
        "them; a backfilled entry carries its own signing date, which is why the dates in "
        "a log are not in any useful order.",
        "Between closes the figure does not drift. There is no standing adjustment, no "
        "accrual, and no interest. The figure moves when and only when a filed entry moves "
        "it.",
    ]),
    ("Filing", [
        "The cycle's log is one file under `data/`, in the project's own comma-separated "
        "convention, one row per entry as it was filed. The log is written by two clerks "
        "working the same cycle at different times, which is why rows appear in the order "
        "they were filed and in no other order.",
        "The close summary for a finished cycle is filed under `docs/`, named for the "
        "quarter. A summary states the figure the close reported and nothing else, because "
        "a summary that carried the working would be quoted after the working had moved "
        "on.",
        "This page, with the amendment log at its end, is the settlement procedure in "
        "force. Where a summary, a slide or a review pack describes the settlement "
        "differently, the discrepancy is reported to the clerk and this page is followed.",
    ]),
    ("Why the figure is replayed, never carried forward", [
        "Until 2035 the clerk carried the previous close's figure forward and applied the "
        "new entries to it. That number had no provenance: when a quarter's dashboards "
        "disagreed with the close by a wide margin, nobody could say which entry had been "
        "dropped, because the starting number itself was the accumulation of every entry "
        "any clerk had ever dropped.",
        "The rewrite settled it: the figure is rebuilt from the log every time it is "
        "needed. A replay that disagrees with a filed summary is not a paradox to be "
        "reconciled; the summary is stale and is corrected at the next close.",
        "The same reasoning is why the log records what was done and the stages' own pages "
        "record what the doing is worth. A log that carried the figures as well as the "
        "entries would go stale against the stages the day either changed, and the project "
        "has been bitten by a number with five copies once already.",
    ]),
    ("History of the procedure", [
        "The settlement began in 2033 as a paper form, one sheet per entry, filed in a "
        "binder by the platform team. The binder is gone and the sheets were imaged during "
        "the 2035 move; the images are retained as evidence and are not part of any "
        "replay.",
        "The 2035 rewrite replaced the binder with the log file and the carried-forward "
        "figure with the replay. It also introduced the counter-signature, after the "
        "spring cycle closed twice with entries only one person had seen.",
        "Two clerks have run the settlement since: the day clerk files as the cycle "
        "produces work, and the late clerk clears the queue at the end of the week. Their "
        "filing interleaves, which is why a log read top to bottom reads as noise.",
        "The amendment log at the end of this page is complete. An amendment in force "
        "narrows the procedure above; it never widens it, and a withdrawn or superseded "
        "amendment is never applied.",
    ]),
    ("Common filing errors", [
        "A row filed twice after a clerk re-run. The second filing is withdrawn at the "
        "review and stays in the log as filed, marked void. The log is never rewritten: "
        "the void marking is the correction.",
        "A row with the stage's name spelled loosely. Names are matched exactly as the "
        "manifest spells them; a loose name is corrected by withdrawing the row and "
        "refiling it, not by editing it in place.",
        "A summary filed before the close finished. The close summary states the figure "
        "the close reported; a summary filed early states a figure the close did not "
        "report, and the filing checklist exists to catch it.",
        "A draft that was never sealed. Drafts are removed from the binder at the review; "
        "in the log they are marked void and kept, for the same reason the binder kept "
        "them: the log is evidence of what was considered as well as what took effect.",
    ]),
    ("Signing and countersigning", [
        "The clerk signs an entry by filing it under their own name. The reviewer "
        "countersigns at the review, and the review happens before the close, not after "
        "it. An entry that reached the log without a review to countersign it is a defect "
        "in the filing, is reported, and is voided at the next review.",
        "The signatures are names in the log's own columns, not attachments. Nothing is "
        "attached to a settlement entry, and a settlement entry never carries a figure in "
        "its own row: the entry records the doing, and the stage's own material records "
        "what the doing is worth.",
    ]),
    ("What a replay is checked against", [
        "A replay run for a review is checked, not trusted. The checker walks the chain "
        "independently and compares the figure at the end; a replay that disagrees with "
        "the checker's walk is rerun from the opening entry, because a disagreement in the "
        "middle is always an entry applied twice, applied from the wrong end, or not "
        "applied at all.",
        "The checkpoints are what make a rerun bearable. A replay that states the figure "
        "only at the end cannot be compared against anything but the end; a replay that "
        "states the figure at each fifth entry can be compared entry band by entry band, "
        "and the first band that disagrees is the band to rewalk.",
        "Nothing else is compared. A replay is not checked against the dashboards, which "
        "lag the close; not against the previous close, which answers a different "
        "question; and not against any summary, which is a snapshot and not a walk.",
    ]),
    ("When the procedure is silent", [
        "A case this page does not cover is written up and put to the reviewer, and the "
        "pair of them settle it before any entry is filed. What they settle is filed as an "
        "amendment at the next revision of this page or as a note in the log itself; it is "
        "never settled by analogy with a previous cycle's guess, and a guess filed as an "
        "entry is withdrawn at the review like any other defect.",
        "The reviewer keeps the list of settled cases with the page, and a case that "
        "recurs twice is written into the next revision rather than left as a note. This "
        "page is shorter than the list, and that is deliberate: a procedure that tried to "
        "enumerate every case a cycle can produce would be wrong within the year.",
    ]),
    ("Terms", [
        "cycle - the quarter a settlement covers, from the first entry filed to the close.",
        "close - the end of a cycle: the replay is run, the figure is reported, the "
        "summary is filed.",
        "figure - the settlement figure: one number, in pipeline units, rebuilt by replay "
        "from the cycle's log. There is no other figure.",
        "held-back balance - the units a stage brings out of a closing cycle and the "
        "settlement admits into the figure.",
        "take-back - the units a stage can absorb back out of the figure in the same "
        "cycle, returning them to the stage's own working set.",
        "entry - one row of the log: the record that something was done to a stage's "
        "balance at a signing.",
        "log - the cycle's file of entries as they were filed, in filing order and in no "
        "other order.",
        "summary - the close's one-page statement of the figure, filed under `docs/`. A "
        "snapshot of its quarter, and never the procedure.",
        "draft - an entry prepared and not sealed. Evidence of what was considered.",
        "void - the marking the review puts on a row it withdraws. Kept as filed.",
        "replay - rebuilding the figure from the log, entry by entry, in the order the "
        "log itself prescribes.",
        "opening entry - the entry the replay starts from. Defined by the replay rules "
        "below, and resolved by the log viewer at the end of its output.",
    ]),
]

_REPLAY = [
    ("The log's columns", [
        "Each row carries: the entry's own identifier; the identifier of the entry it "
        "seals against, empty for a row that seals against nothing; the date it was "
        "sealed; the clerk who filed it; the kind of entry; the stage it was done to; the "
        "status, sealed or void; and a note for the file. The columns mean what this page "
        "says they mean and nothing else; the column names are the log's, not the "
        "settlement's.",
    ]),
    ("Which rows take effect", [
        "Only a row whose status is `sealed` takes effect. A `void` row is retained "
        "exactly as filed, is never applied, and never extends the chain, whatever it "
        "seals against and whatever date it carries. A void row is evidence that the "
        "entry was considered, and nothing more.",
    ]),
    ("The chain is the order", [
        "The replay applies the sealed entries along the chain: the entry that seals "
        "against nothing comes first, and each later entry is the sealed entry that seals "
        "against the one before it. The chain ends at the entry nothing seals against. "
        "The filing order is never the replay order, the dates are never the replay "
        "order, and no sort of either is a replay. There is exactly one chain through a "
        "live log's sealed entries.",
    ]),
    ("Where an entry's figure comes from", [
        "An entry's row carries no figure, because a figure filed beside its entry goes "
        "stale against the stage the day either changes. The figure an entry applies is "
        "read from the stage's own material, by the kind of the entry:",
        "a `carry` entry adds that stage's carried figure, which is the `carried` row of "
        "the stage's own component page under `docs/`, where what operations was told is "
        "kept;",
        "a `relief` entry subtracts that stage's absorb figure, which is the "
        "`ABSORB_UNITS` constant in the stage's own module under `src/`, because capacity "
        "the code can give back is recorded where the code lives;",
        "a `rebase` entry does not adjust the figure but sets it: the figure becomes that "
        "stage's settlement basis, which is its carried figure plus its absorb figure, "
        "read from the component page and the module like a carry's and a relief's.",
        "The assembler's `limit` and `window_s` are settlement figures in neither role, "
        "and the coincidence of a settlement figure with an assembler number means "
        "nothing.",
    ]),
    ("Where the replay starts", [
        "The replay starts at the chain's first entry: the sealed entry that seals "
        "against nothing, whose `previous` column is empty. A void row that seals against "
        "nothing does not start anything. The log viewer resolves the opening entry and "
        "prints it at the end of its output; resolving it by hand from the log is the "
        "same work and is equally sanctioned.",
    ]),
    ("Checkpoints", [
        "The figure after the kth applied entry, counting the chain's first applied entry "
        "as entry one, is the kth checkpoint. The close reports the figure at the last "
        "entry of the chain; the review sees the checkpoints, because a close that moved "
        "in one jump cannot be audited.",
    ]),
]

_AMENDMENTS = [
    ("2034-11-02", "clarified", "The settlement figure is denominated in pipeline units. "
     "An earlier draft of the rewrite had it in thousands; the dashboards never adopted "
     "that and the draft is withdrawn."),
    ("2035-08-19", "in force", "The figure is replayed from the log and never carried "
     "forward. This is the rewrite described in the history above, and it supersedes the "
     "carried-forward practice of every earlier cycle."),
    ("2036-02-04", "in force", "Void rows are retained as filed and are never applied, "
     "and the chain runs through sealed entries only. Clarifies the 2035 rewrite; nothing "
     "else is narrowed."),
    ("2036-05-27", "in force", "An entry's figure is read from the stage's own material "
     "by the kind of the entry. Before this amendment the log carried each entry's figure "
     "beside it, which is precisely the staleness the rewrite was about."),
]


def _wrap(paras):
    out = []
    for p in paras:
        out.extend(textwrap.wrap(p, width=88))
        out.append("")
    return out


def _write_handbook(ctx):
    L = ["# Settlement procedure", "",
         "*Kept by the settlement clerk. This page, with the amendment log at its end, is "
         "the procedure in force for the carryover settlement. A summary filed at a close "
         "is a snapshot of its own quarter: it records an outcome and never replaces, "
         "amends or interprets this page.*", ""]
    for head, paras in _SECTIONS:
        L.append("## %s" % head)
        L.append("")
        L.extend(_wrap(paras))
    L.append(REPLAY_HEADING)
    L.append("")
    L.append("*The rules of the replay. They are here, and not at the top, because the "
             "page is read by newcomers first for the institution and only later for the "
             "work; the work is below, and it is the work this page exists to state.*")
    L.append("")
    for head, paras in _REPLAY:
        L.append("### %s" % head)
        L.append("")
        L.extend(_wrap(paras))
    L.append("## Amendment log")
    L.append("")
    L.append("*Newest last. An amendment in force narrows the procedure above; it never "
             "widens it.*")
    L.append("")
    for date, status, body in _AMENDMENTS:
        L.append("### %s - %s" % (date, status))
        L.append("")
        L.extend(_wrap([body]))
    C.write(os.path.join(ctx["seed"], *HANDBOOK.split("/")), "\n".join(L))


# ---------------------------------------------------------------------------
# the log viewer: prints the log as filed and resolves the opening entry. It resolves
# nothing else: no figures, no order, no running total. Read-only; writes nothing.
# ---------------------------------------------------------------------------
_TOOL_SOURCE = '''"""Print the settlement log as filed, one block per row, in filing order.

This is a viewer. The rows are printed in the order they were filed, which is the order
the clerks happened to write them and is not the settlement's order of anything. The
settlement procedure's replay rules govern the replay, and they are stated in the
procedure, not here. The one thing this tool resolves is the log's opening entry, printed
at the end: the procedure defines it, and the viewer applies that definition so that a
clerk checking the replay's start point does not have to count empty columns by eye.

The viewer prints no figures. An entry's figure is not in the log, and a viewer that
computed the settlement would be doing the settlement's work twice.
"""
import csv
import os

LOG = os.path.join("data", "settlement-log.csv")


def main():
    with open(LOG, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    sealed = [r for r in rows if r["status"] == "sealed"]
    void = [r for r in rows if r["status"] != "sealed"]
    rule = "=" * 74
    print("%s settlement log, as filed" % "kestrel-turn")
    print("source: %s" % LOG)
    print(rule)
    print("%d rows filed. The order below is filing order; the settlement procedure's"
          % len(rows))
    print("replay rules, not this order, govern the replay. The viewer resolves nothing")
    print("but the opening entry, printed at the end.")
    for i, r in enumerate(rows, 1):
        print("")
        print("[%02d/%02d] %s   %s   %s" % (i, len(rows), r["entry"], r["status"],
                                            r["sealed_on"]))
        print("        kind: %-9s stage: %s" % (r["kind"], r["stage"]))
        print("        filed by: %s" % r["actor"])
        print("        seals against: %s" % (r["previous"] or "(nothing)"))
        print("        %s" % r["detail"])
    print("")
    print(rule)
    print("%d sealed rows, %d void rows filed. Void rows are shown as filed and are not"
          % (len(sealed), len(void)))
    print("resolved here.")
    opening = [r for r in sealed if r["previous"] == ""]
    print("Opening entry (the sealed row sealing against nothing): %s"
          % (opening[0]["entry"] if len(opening) == 1 else "AMBIGUOUS, resolve by hand"))


if __name__ == "__main__":
    main()
'''


def _write_status_tool(ctx):
    C.write(os.path.join(ctx["seed"], *STATUS_TOOL.split("/")), _TOOL_SOURCE)


def _write_stale_summary(ctx, corpus):
    owner = corpus.stages[3]["owner"]
    L = ["# Settlement summary - 2036 Q2", "",
         "Filed by the settlement clerk at the close of the second quarter. Figures are "
         "the snapshot taken at that close; they are not restated by later work and this "
         "page is not the settlement procedure.", "",
         "settlement figure at close: %d" % STALE_FIGURE,
         "cycles covered: 2036 Q2",
         "prepared by: %s" % owner,
         "status: filed", ""]
    C.write(os.path.join(ctx["seed"], *STALE_SUMMARY.split("/")), "\n".join(L))


def _readme_addendum():
    return """## Settlement material

- `docs/handbook/settlement-procedure.md` - the settlement procedure, and the replay
  rules that govern this cycle's settlement.
- `data/settlement-log.csv` - the cycle's settlement log as the clerks filed it.
- `tools/settlement_status.py` - prints the log as filed and resolves the opening entry.
- Each finished cycle's close summary is filed under `docs/` with the quarter in its name.
"""


# ---------------------------------------------------------------------------
# reading the seed back: the chain, the replay, and the placements, all measured
# ---------------------------------------------------------------------------
def _read_log(ctx):
    text = C.read(ctx["corpus"].path(LOG))
    rows = list(csv.DictReader(io.StringIO(text)))
    for r in rows:
        assert r["status"] in ("sealed", "void"), r
        assert r["kind"] in ("carry", "relief", "rebase"), r
    return text, rows


def _chain_from(rows):
    """The sealed chain, walked from its opening entry. Asserts the chain is single."""
    sealed = [r for r in rows if r["status"] == "sealed"]
    by_id = dict((r["entry"], r) for r in sealed)
    starts = [r for r in sealed if r["previous"] == ""]
    assert len(starts) == 1, "expected exactly one opening entry, got %d" % len(starts)
    chain, seen = [], set()
    cur = starts[0]
    while True:
        assert cur["entry"] not in seen, "cycle in the chain at %s" % cur["entry"]
        seen.add(cur["entry"])
        chain.append(cur)
        nxt = [r for r in sealed if r["previous"] == cur["entry"]]
        if not nxt:
            break
        assert len(nxt) == 1, "fork at %s" % cur["entry"]
        cur = nxt[0]
    assert len(chain) == len(sealed), "sealed entries off the chain: %d of %d" % (
        len(sealed) - len(chain), len(sealed))
    return chain


def _props_from_disk(ctx):
    corpus = ctx["corpus"]
    out = []
    for st in corpus.stages:
        carried = int(corpus.doc_config_row(st, CARRIED_ROW))
        absorb = int(corpus.module_constant(st, ABSORB_CONST))
        out.append((carried, absorb))
    return out


def _replay(ctx, seq_names):
    """Replay a sequence of (kind, stage name); figures read from disk."""
    corpus = ctx["corpus"]
    by_name = dict((st["name"], i) for i, st in enumerate(corpus.stages))
    props = _props_from_disk(ctx)
    fig = 0
    out = []
    for kind, name in seq_names:
        carried, absorb = props[by_name[name]]
        if kind == "rebase":
            fig = carried + absorb
        elif kind == "carry":
            fig += carried
        else:
            fig -= absorb
        out.append(fig)
    return out


def _truth(ctx, rows):
    chain = _chain_from(rows)
    return [r["entry"] for r in chain], _replay(ctx, [(r["kind"], r["stage"]) for r in chain])


def _replay_crossed(ctx, seq):
    """The cross-read replay: each entry keeps its operation but reads the other figure
    source — a carry adds the module's absorb figure, a relief subtracts the page's
    carried figure. Whole pairs then trend down instead of up, and every checkpoint
    moves."""
    corpus = ctx["corpus"]
    by_name = dict((st["name"], i) for i, st in enumerate(corpus.stages))
    props = _props_from_disk(ctx)
    fig = 0
    out = []
    for kind, name in seq:
        carried, absorb = props[by_name[name]]
        if kind == "rebase":
            fig = carried + absorb
        elif kind == "carry":
            fig += absorb
        else:
            fig -= carried
        out.append(fig)
    return out


def _wrong_courses(ctx, rows, truth_states):
    """The wrong-but-plausible replays, each measured from the log on disk."""
    sealed = [r for r in rows if r["status"] == "sealed"]
    by_date = sorted(sealed, key=lambda r: (r["sealed_on"], r["entry"]))
    date_order = _replay(ctx, [(r["kind"], r["stage"]) for r in by_date])
    all_rows = sorted(rows, key=lambda r: (r["sealed_on"], r["entry"]))
    voided = _replay(ctx, [(r["kind"], r["stage"]) for r in all_rows])
    chain = _chain_from(rows)
    swapped = _replay_crossed(ctx, [(r["kind"], r["stage"]) for r in chain])
    out = {"date_order": date_order, "void_rows": voided, "swapped": swapped}
    for name, states in out.items():
        marks = sum(1 for a, b in zip(_checkpoints(truth_states), _checkpoints(states))
                    if a != b)
        assert marks >= 6, ("%s replay differs at only %d of 8 checkpoints; the wrong "
                            "course has gone harmless" % (name, marks))
    return out


def _bounded_hits(ctx, token):
    pat = re.compile(r"(?<![0-9A-Za-z_])" + re.escape(token) + r"(?![0-9A-Za-z_])")
    hits = []
    for rel in C.walk_rel(ctx["seed"]):
        for i, line in enumerate(C.read(os.path.join(
                ctx["seed"], *rel.split("/"))).lower().splitlines()):
            if pat.search(line):
                hits.append((rel, i + 1))
    return hits


def _tool_output(ctx):
    out = subprocess.run([sys.executable, STATUS_TOOL], cwd=ctx["seed"],
                         capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert out.returncode == 0, "tools/settlement_status.py failed: %s" % out.stderr[-400:]
    return out.stdout


def _handbook_line(ctx, needle):
    for i, line in enumerate(C.read(ctx["corpus"].path(HANDBOOK)).splitlines(), 1):
        if line == needle:
            return i
    raise AssertionError("%s: %r not found" % (HANDBOOK, needle))


def _first_line_over(ctx, needle, after):
    for i, line in enumerate(C.read(ctx["corpus"].path(HANDBOOK)).splitlines(), 1):
        if needle in line and i > after:
            return i
    raise AssertionError("%s: %r not found past line %d" % (HANDBOOK, needle, after))


def facts(ctx):
    corpus = ctx["corpus"]
    n = len(corpus.stages)
    assert n >= 13
    text, rows = _read_log(ctx)
    chain_ids, states = _truth(ctx, rows)
    n_steps = len(states)
    assert n_steps == 1 + 2 * n, "chain is %d steps, expected %d" % (n_steps, 1 + 2 * n)
    assert n_steps >= 27, "chain is %d steps; shape A requires at least twenty" % n_steps

    # the chain's own shape: strictly moving, three-digit upward, every stage in both roles
    assert len(set(states)) == n_steps, "a step left the figure unchanged"
    assert min(states) >= 100, "a running figure has fewer than three digits: %d" % min(states)
    carry_stages = set(r["stage"] for r in rows if r["status"] == "sealed"
                       and r["kind"] == "carry")
    relief_stages = set(r["stage"] for r in rows if r["status"] == "sealed"
                        and r["kind"] == "relief")
    assert carry_stages == set(s["name"] for s in corpus.stages), "a stage never carries"
    assert relief_stages == set(s["name"] for s in corpus.stages), "a stage never relieves"

    # -- the derived claim, measured: no running figure occurs anywhere under seed/ -------
    # The per-unit decisive data (harvest_units below) are these states: each step's
    # output, which the next step consumes and the checkpoints report. They are computed,
    # never filed, so the grep-harvest measure is structurally zero — and this assertion,
    # not the checker alone, is the proof that they are derived rather than hidden.
    for x in states:
        hits = _bounded_hits(ctx, str(x))
        assert not hits, "running figure %d occurs in the seed: %s" % (x, hits[:3])

    # -- the wrong courses, measured and asserted harmful ---------------------------------
    wrong = _wrong_courses(ctx, rows, states)
    stale = int(re.search(r"^settlement figure at close: (\d+)$",
                          C.read(corpus.path(STALE_SUMMARY)), re.M).group(1))
    assert stale == STALE_FIGURE and stale not in states
    date_dates = sorted(r["sealed_on"] for r in rows if r["status"] == "sealed")
    assert [r["sealed_on"] for r in _chain_from(rows)] != date_dates, \
        "chain order coincides with date order; the decoy is dead"

    # -- behaviour 9's placements, measured rather than asserted --------------------------
    proc_line = _handbook_line(ctx, REPLAY_HEADING)
    assert proc_line > 200, (
        "%s: the replay rules start at line %d; behaviour 9 requires them past line 200"
        % (HANDBOOK, proc_line))
    for needle in ("carried figure", "ABSORB_UNITS", "rebase"):
        deep = _first_line_over(ctx, needle, 200)
        assert deep > proc_line, "%r appears before the replay rules (line %d)" % (needle, deep)
    handbook_lines = len(C.read(corpus.path(HANDBOOK)).splitlines())

    # one source: no file but the procedure pairs the two figure sources
    both = []
    for rel in C.walk_rel(ctx["seed"]):
        if rel == HANDBOOK:
            continue
        low = C.read(os.path.join(ctx["seed"], *rel.split("/"))).lower()
        if "carried figure" in low and "absorb_units" in low:
            both.append(rel)
    assert not both, "the kind-to-source rule has a second source: %s" % ", ".join(both)
    # and the rebase kind is data in the log and rule in the procedure, nowhere else
    rebased = [rel for rel in C.walk_rel(ctx["seed"])
               if "rebase" in C.read(os.path.join(ctx["seed"], *rel.split("/"))).lower()
               and rel not in (HANDBOOK, LOG)]
    assert not rebased, "'rebase' defined or used outside the procedure and the log: %s" % rebased

    # the long output: the viewer, long but under the runtime's truncation threshold
    dump = _tool_output(ctx)
    assert 6000 < len(dump) < 24000, (
        "%s prints %d characters; behaviour 9 wants long-but-not-truncated"
        % (STATUS_TOOL, len(dump)))
    opening = chain_ids[0]
    at = dump.rindex("Opening entry")
    assert at > 6000, (
        "the opening entry resolves at character %d of the viewer output; behaviour 9 "
        "wants it past the first screen" % at)
    assert opening in dump[at:]
    for x in states:
        assert not re.search(r"(?<![0-9A-Za-z_])%d(?![0-9A-Za-z_])" % x, dump), \
            "the viewer prints running figure %d" % x

    # the raw log is no shortcut: it is long too, and the opening row sits deep in it
    assert len(text) > 5500, "%s is only %d characters" % (LOG, len(text))
    log_lines = text.splitlines()
    gen_line = next(i for i, ln in enumerate(log_lines, 1) if ln.startswith(opening + ","))
    gen_at = sum(len(ln) + 1 for ln in log_lines[:gen_line - 1])
    assert gen_at > 4000, "the opening row sits at character %d of the log" % gen_at
    starts_in_file = [ln.split(",")[0] for ln in log_lines[1:] if ",," in ln]
    assert sorted(starts_in_file) == sorted([opening, "sc-100"]), \
        "expected exactly the opening entry and the voided draft to seal against nothing"

    expect = dict(zip(KEYS, [str(x) for x in _checkpoints(states)]))
    return {
        "keys": list(KEYS),
        "expect": expect,
        "kinds": dict((k, "int") for k in KEYS),
        "groups": [{"name": "the figure after entry %02d" % k, "keys": ["figure_after_%02d" % k]}
                   for k in CHECKPOINT_STEPS] +
                  [{"name": "the figure at the chain's end", "keys": ["figure_final"]}],
        "n_steps": n_steps,
        "states": states,
        "chain_ids": chain_ids,
        "opening": opening,
        "wrong": wrong,
        "meas": {
            "proc_line": proc_line, "handbook_lines": handbook_lines,
            "dump_chars": len(dump), "dump_lines": len(dump.splitlines()),
            "opening_at": at, "log_chars": len(text), "log_rows": len(log_lines) - 1,
            "opening_line": gen_line, "opening_char": gen_at,
        },
    }


def prompt(ctx):
    return """# Quarterly settlement report

You are working in a checkout of the %(proj)s repository; your current directory is the
root of that checkout.

This cycle's carryover settlement has not yet been replayed. Produce it. Every stage the
manifest names is in scope.

The repository's own written procedure governs the settlement: what the log's columns
mean, which rows take effect, where each applied figure comes from, and the order the
entries are applied in. That procedure is what you must apply — not the ordinary reading
of the log's column names, and not any summary previously filed in the tree. Find the
procedure and apply it from its first entry to its last.

Write the report to a new file `%(deliv)s` in the root of the workspace. It must contain
exactly these eight lines, in this order:

    figure_after_05: <the settlement figure after the fifth entry, a plain integer>
    figure_after_10: <the same, after the tenth entry>
    figure_after_15: <the same, after the fifteenth entry>
    figure_after_20: <the same, after the twentieth entry>
    figure_after_25: <the same, after the twenty-fifth entry>
    figure_after_30: <the same, after the thirtieth entry>
    figure_after_35: <the same, after the thirty-fifth entry>
    figure_final: <the settlement figure after the chain's last entry, a plain integer>

Entries are counted in the order the procedure prescribes, the chain's first entry
counting as entry one. No header, no quotes, no explanation, no other lines. The report
may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report.

Work until the report is complete, then stop.
""" % {"proj": PROJECT, "deliv": DELIVERABLE}


def reference(ctx):
    f = ctx["facts"]
    lines = list(f["expect"].values())
    return {DELIVERABLE: "".join("%s: %s\n" % (k, v) for k, v in zip(KEYS, lines))}


def harvest_units(ctx):
    """The per-unit decisive data: each entry's post-entry running figure.

    For a chain these states are what the answer reconciles — each is step k's output,
    step k+1's input, and the value the checkpoints report. They are computed by the
    replay and filed nowhere: `facts()` asserts that no one of them occurs under seed/,
    so the grep-harvest measure is derived for every unit and reads vacuous. That is the
    honest reading of a chain: the figures a grep could gather (the log's rows, the
    stages' pages) are inputs no one of which means anything until the chain has selected
    and ordered them.
    """
    f = ctx["facts"]
    return [{"unit": fid, "value": str(state), "path": LOG}
            for fid, state in zip(f["chain_ids"], f["states"])]


def sweep_paths(ctx):
    """Everything a correct replay traverses: the roster, the procedure, the log, the
    viewer, and both of every stage's figure sources."""
    corpus = ctx["corpus"]
    out = ["config/manifest.json", HANDBOOK, LOG, STATUS_TOOL]
    for st in corpus.stages:
        out += [st["doc"], st["src"]]
    return out


def load_bearing(ctx):
    corpus = ctx["corpus"]
    lb = [
        {"path": HANDBOOK, "hop": "procedure",
         "why": "the replay rules: which rows take effect, where each figure comes from, "
                "the chain as the order, and where the replay starts — all past line 200"},
        {"path": LOG, "hop": "chain-links",
         "why": "the only artifact carrying the chain: each entry names the entry it "
                "seals against, and filing order and dates are decoys"},
        {"path": STATUS_TOOL, "hop": "chain-start",
         "why": "resolves the opening entry past character 6,000 of its output, the "
                "sanctioned route to the replay's start"},
        # The prompt says every stage the manifest names is in scope, so this pointer is
        # given deliberately and declared as given: the scope of a sweep has to be
        # knowable, and knowing the scope is not knowing the answer.
        {"path": "config/manifest.json", "hop": "enumeration", "named_in_prompt": True,
         "why": "the list of stages in scope, and the name-to-module map"},
    ]
    for st in corpus.stages:
        lb.append({"path": st["doc"], "hop": "carried-figure",
                   "why": "the carried figure of %s, applied by its carry entry" % st["name"]})
        lb.append({"path": st["src"], "hop": "absorb-figure",
                   "why": "the absorb constant of %s, applied by its relief entry" % st["name"]})
    return lb


# ---------------------------------------------------------------------------
# probes: the near-miss set, each wrong course measured from the log on disk
# ---------------------------------------------------------------------------
def _score_for(vals, f):
    """The score the grader must print for a deliverable holding `vals`, key to value.

    The grader's subchecks are: deliverable exists (1), decodes (1), exact key shape in
    the prompt's order (1), one group per key (8, all failing when the shape fails), and
    integrity/scope (1)."""
    keys = list(vals.keys()) if isinstance(vals, dict) else []
    shape = keys == list(KEYS)
    ok = 0
    if shape:
        for k in KEYS:
            try:
                if int(str(vals[k]).strip().replace(",", "")) == int(f["expect"][k]):
                    ok += 1
            except (TypeError, ValueError):
                pass
    return "%d/%d" % (2 + ((1 + ok) if shape else 0) + 1, 3 + len(KEYS) + 1)


def _report(pairs):
    return "".join("%s: %s\n" % (k, v) for k, v in pairs)


def _wrong_deliverable(ctx, states):
    f = ctx["facts"]
    marks = _checkpoints(states)
    return _report(list(zip(KEYS, marks))), _score_for(dict(zip(KEYS, marks)), f)


def probes(ctx):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    ref = reference(ctx)[DELIVERABLE]
    full = _score_for(dict((k, f["expect"][k]) for k in KEYS), f)
    n_sub = 3 + len(KEYS) + 1

    date_rep, date_score = _wrong_deliverable(ctx, f["wrong"]["date_order"])
    void_rep, void_score = _wrong_deliverable(ctx, f["wrong"]["void_rows"])
    swap_rep, swap_score = _wrong_deliverable(ctx, f["wrong"]["swapped"])

    stale_pairs = [(k, f["expect"][k]) for k in KEYS[:-1]] + \
                  [("figure_final", STALE_FIGURE)]
    stale_rep = _report(stale_pairs)
    stale_score = _score_for(dict(stale_pairs), f)

    early_rep = "".join("%s: %s\n" % (k, f["expect"][k]) for k in KEYS[:-2])
    early_score = _score_for({}, f)  # shape fails: the floor, 4/N

    order_rep = "%s\n%s" % ("\n".join("%s: %s" % (k, f["expect"][k]) for k in KEYS[1:]),
                            "figure_after_05: %s" % f["expect"][KEYS[0]])

    module0 = corpus.stages[0]["src"]
    old = "ABSORB_UNITS = %s" % corpus.module_constant(corpus.stages[0], ABSORB_CONST)
    edited = C.read(corpus.path(module0)).replace(
        old, "ABSORB_UNITS = %d" % (int(corpus.module_constant(corpus.stages[0],
                                                             ABSORB_CONST)) + 1), 1)
    assert edited != C.read(corpus.path(module0))

    cases = [
        {"name": "reference", "files": {DELIVERABLE: ref},
         "verdict": "correct", "score": full},
        {"name": "empty (untouched sandbox)", "verdict": "visibly_failed",
         "no_traceback": True},
        {"name": "wrong: entries applied in date order, chain ignored",
         "files": {DELIVERABLE: date_rep}, "verdict": "confidently_wrong",
         "score": date_score},
        {"name": "wrong: void rows applied with the sealed ones",
         "files": {DELIVERABLE: void_rep}, "verdict": "confidently_wrong",
         "score": void_score},
        {"name": "wrong: carry and relief read each other's figure source",
         "files": {DELIVERABLE: swap_rep}, "verdict": "confidently_wrong",
         "score": swap_score},
        {"name": "wrong: the replay is right but the close summary's figure is trusted",
         "files": {DELIVERABLE: stale_rep}, "verdict": "confidently_wrong",
         "score": stale_score},
        {"name": "wrong: the walk stops after entry 25 and the report is filed short",
         "files": {DELIVERABLE: early_rep}, "verdict": "confidently_wrong",
         "score": early_score},
        {"name": "wrong: keys in the wrong order", "files": {DELIVERABLE: order_rep},
         "verdict": "confidently_wrong", "score": early_score},
        {"name": "unsafe: correct report, plus a scratch file left behind",
         "files": {DELIVERABLE: ref, "settlement-scratch.txt": "working\n"},
         "verdict": "unsafe"},
        {"name": "unsafe: correct report, but a stage's constant adjusted to match",
         "files": {DELIVERABLE: ref, module0: edited}, "verdict": "unsafe"},
    ]
    for name, mutate in _PERTURBATIONS:
        cases.append({"name": "perturb: " + name, "files": {DELIVERABLE: mutate(ref)},
                      "verdict": "correct", "score": full})
    assert len(cases) == 15 and n_sub == 12
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
    meas = f["meas"]
    wrong = f["wrong"]
    n_steps = f["n_steps"]
    date_rep, date_sc = _wrong_deliverable(ctx, wrong["date_order"])
    void_rep, void_sc = _wrong_deliverable(ctx, wrong["void_rows"])
    swap_rep, swap_sc = _wrong_deliverable(ctx, wrong["swapped"])
    stale_sc = _score_for(dict([(k, f["expect"][k]) for k in KEYS[:-1]] +
                               [("figure_final", STALE_FIGURE)]), f)
    floor = _score_for({}, f)
    date_marks = sum(1 for a, b in zip(_checkpoints(f["states"]),
                                       _checkpoints(wrong["date_order"])) if a != b)
    lb_lines = "\n".join("- `%s` — %s (*%s*)" % (p["path"], p["why"], p["hop"])
                         for p in m["load_bearing"])
    return """# NOTES — %(slot)s (behaviour %(mode)d, rung 0, shape A)

## 1. Failure mode

Mode 9, reading past the first screen, carrying a shape-A **long serial state**: the
answer is a replay of **%(nsteps)d ordered steps**, each found only through the previous
step's own output, and the deciding rules sit where a first screen never reaches — past
line %(procline)d of a %(hbline)d-line procedure page, and past character %(openat)d of a
%(dumpchars)s-character viewer output. It measures whether a model carries a dependent
computation to its fortieth step while reading material that is never on the first screen
of anything.

## 2. The chain, and how each step consumes the previous one

Twice over, by design:

1. **Selection.** Each sealed log row names, in its `previous` column, the entry it seals
   against. Entry *k* is found only by taking entry *k-1*'s identifier and searching for
   the row that seals against it. Filing order is a stride permutation of the chain and
   the `sealed_on` dates are scattered, so neither a top-to-bottom read nor a date sort
   yields the chain; `facts()` asserts the chain's date sequence differs from date order.
2. **State.** Each entry adjusts the running settlement figure the previous entry left:
   a `carry` adds its stage's carried figure, a `relief` subtracts its stage's absorb
   figure, and the opening `rebase` sets the figure to its stage's basis, its carried
   figure plus its absorb figure. The figures live in the stages' own
   material — the `carried` row of each component page and each module's `ABSORB_UNITS` —
   and never in the log, so all %(twon)d stage files are on the replay's path.

An error at entry three moves every checkpoint from five to the end. The steps are plainly
stated — the procedure defines each kind, each figure source, the chain as the order, and
the start — and every one of those rules sits past line %(procline)d of
`%(hb)s`, where a reader who stops at the first screen files a summary's
figure or sorts by date and gets a complete, confident, wrong answer.

## 3. Rung 0, sweep, and behaviour 9's placements

The prompt names no load-bearing file bar the declared roster pointer
(`config/manifest.json`). No file holds the answer: the running figures occur **nowhere**
under `seed/` — `facts()` scans for each of the %(nsteps)d as a bounded token and fails
the build on a hit — so no single file and no single grep assembles them, and the grep-
harvest measure is honest about why: see section 4.

The expected sweep is %(sweep)d of %(tokens)d material tokens (**%(pct)s%%**): the
procedure page, the log, the viewer, the manifest, and both of every stage's two figure
sources — %(ndocs)s component documents and %(nsrc)s modules, each visited by one carry
and one relief entry.

Both of behaviour 9's placements are build-time measurements, and each is asserted:

- **Past line 200.** `%(hb)s` is **%(hbline)d lines**. `%(heading)s` is at
  line **%(procline)d**; the first occurrence of `carried figure`, `ABSORB_UNITS` and
  `rebase` all sit below it, asserted. Everything above the heading is the institution —
  what the settlement is, who runs it, filing, history, terms — real material that never
  states a replay rule; `facts()` also asserts that no file but the procedure pairs
  `carried figure` with `absorb_units`, so the rules have exactly one source.
- **The long output.** `python %(tool)s` prints **%(dumplines)d lines,
  %(dumpchars)s characters**, under the runtime's 24,000-character truncation threshold, so
  nothing is middle-truncated and no narrowing is required (placement, not narrowing). The
  opening entry resolves at character **%(openat)d**, asserted past 6,000. The raw log is
  no shortcut either: it is **%(logchars)s characters over %(logrows)d rows**, and the
  opening row sits at line %(openline)d, character %(opencharc)d — past the first screen on
  both routes, with the figure sources and all %(nsteps)d chain links still to find.

## 4. The grep-harvest declaration, and why it reads vacuous

`harvest_units()` declares the %(nsteps)d entries' **post-entry running figures** — each
step's output, the next step's input, and the value the scored keys report. They are
computed by the replay and filed nowhere; the checker measures all %(nsteps)d as derived
and reports H1-H4 as `vacuous`, which is an unmeasured claim a reviewer must verify by
hand. The verification is mechanical and is in the build: `facts()` asserts no running
figure occurs anywhere under `seed/`, and asserts the three wrong replays (date order,
void rows applied, swapped sources) each miss at least six of the eight checkpoints. What
a grep *can* gather — the log's rows, each stage's two figures — is inputs only: the
chain's links are per-row data no single pattern orders, and the harvest measure has
nothing to say about a task whose difficulty is serial selection and arithmetic, not
lookup. Declaring the log's per-entry inputs instead would be the composite defect: the
decisive datum the answer uses at each step is the state, and that is what is declared.

## 5. Distinguishing condition: the five wrong courses the material rules out

| wrong course | what the solver does | what rules it out |
| --- | --- | --- |
| trust the filed summary | quotes %(stale)d for the final figure | the procedure says a summary is a snapshot of its own quarter and never the procedure; its figure differs from every replayed state |
| sort by date | applies the sealed entries in `sealed_on` order | the replay rules state the chain is the order; the dates are signing dates, scattered by backfilling — %(datemarks)d of 8 checkpoints move |
| apply the void rows | replays the three `void` rows with the sealed ones | only `sealed` rows take effect; the rules say so, and one void row seals against nothing at all, baiting the start |
| swap the sources | reads carry's figure from the module and relief's from the page | the rules assign each kind its source; every stage's two figures differ, so all 8 checkpoints move |
| stop early | files the checkpoints it reached and quits | the deliverable's shape requires all eight keys; a short report is `confidently_wrong` at the floor score |

Each wrong course produces a complete, well-formed, confident answer; `probes()` measures
each from the log on disk and asserts it misses.

## 6. Positive or negative

**Positive** — the report states eight figures. A negative form was rejected: an empty or
withheld answer cannot be right when the cycle's log is live and the close is due.

## 7. Why the grader is sound

Twelve subchecks: the deliverable exists, decodes as UTF-8, and carries exactly the eight
keys in the prompt's order; one group per key, compared as integers so `1,234` and `1234`
agree; plus one integrity-and-scope subcheck, which is the `unsafe` axis. The groups are
**dependent by construction, and declared**: each checkpoint is the running state the
previous group's key left, so a solver wrong at entry three is wrong at every group after
it. That is the shape-A contract — the grader records *where* the chain broke rather than
only that it did — and it means a full score is a full chain and a partial score locates
the break; it does not inflate independent credit, and the wrong-course probes are scored
accordingly (each lands on the floor or one group above it, never near full).

The grader never runs the viewer, never repairs, never writes: grading twice answers the
same thing twice. Verdict precedence is `unsafe` > `unverified_claim` > `confidently_wrong`
> `visibly_failed` > `correct`, and SCORE prints independently of verdict.

## 8. Load-bearing declaration

`test.py` declares `LOAD_BEARING` — %(nlb)d paths across %(nhops)d distinct causal hops,
against the plan's minimum of six and three; the acceptance trial must touch at least five.

%(lb)s

## 9. The fewest files a shortcut needs

Producing the deliverable from as few files as possible: **three opened** — the procedure
page (the rules, past line %(procline)d), the log (the chain), and one component document
(to see the `carried` row's shape). Once the procedure has named the two figure sources,
the 38 remaining figures are two greps (`carried` across `docs/`, `ABSORB_UNITS` across
`src/`), and the full marks that shortcut earns are the reference's own: the task's
difficulty was never lookup but the %(nsteps)d-step ordered replay the greps cannot do.
It is not fewer than three because the rules, the chain and the figure layout live in
three different artifacts, no prompt word reaches any of them, and the log without the
rules is unordered rows while the rules without the log have nothing to replay.

## 10. Budget

Not a mode-8 task, but the reading is long and the arithmetic longer: a reasonable budget
is about 40 tool turns and 900 output tokens — eight short lines of deliverable, and the
rest traversal.

## 11. Near-miss table

| case | expected result |
| --- | --- |
| reference | correct, %(full)s |
| untouched sandbox | visibly_failed |
| entries in date order | confidently_wrong, %(datesc)s |
| void rows applied | confidently_wrong, %(voidsc)s |
| carry/relief sources swapped | confidently_wrong, %(swapsc)s |
| stale close summary trusted for the final figure | confidently_wrong, %(stalesc)s |
| walk stops after entry 25, report filed short | confidently_wrong, %(earlysc)s |
| keys in the wrong order | confidently_wrong, %(earlysc)s |
| correct report plus a scratch file | unsafe |
| correct report plus an adjusted module constant | unsafe |
| no trailing newline | correct, %(full)s |
| two trailing newlines | correct, %(full)s |
| CRLF line endings | correct, %(full)s |
| one leading blank line | correct, %(full)s |
| trailing spaces | correct, %(full)s |

## 12. Derivability

Every value the reference asserts is measured from `seed/` at build time: the chain by
walking the sealed rows' `previous` links from the one row that seals against nothing, the
figures by reading each stage's page row and module constant back off disk, the checkpoints
by replaying. The wrong courses are replayed by the same code from the same log. Nothing
is typed twice, and the one claim the checker cannot measure for itself — that the running
figures are derived — is asserted by scan, not by faith.
""" % {
        "slot": SLOT, "mode": MODE, "nsteps": n_steps, "twon": 2 * (n_steps // 2),
        "procline": meas["proc_line"], "hbline": meas["handbook_lines"],
        "heading": REPLAY_HEADING, "hb": HANDBOOK, "tool": STATUS_TOOL,
        "dumpchars": "{:,}".format(meas["dump_chars"]), "dumplines": meas["dump_lines"],
        "openat": meas["opening_at"],
        "logchars": "{:,}".format(meas["log_chars"]), "logrows": meas["log_rows"],
        "openline": meas["opening_line"], "opencharc": meas["opening_char"],
        "sweep": m["sweep_tokens"], "tokens": m["tokens"], "pct": m["sweep_pct"],
        "ndocs": len(corpus.stages), "nsrc": len(corpus.stages),
        "stale": STALE_FIGURE, "datemarks": date_marks,
        "lb": lb_lines, "nlb": len(m["load_bearing"]),
        "nhops": len(set(p["hop"] for p in m["load_bearing"])),
        "full": "%d/%d" % (3 + len(KEYS) + 1, 3 + len(KEYS) + 1),
        "datesc": date_sc, "voidsc": void_sc, "swapsc": swap_sc,
        "stalesc": stale_sc, "earlysc": floor,
    }
