"""m01-main-glm - behaviour 1, a requirement stated once, far from the code.

Public shapes adapted (plan section 3.2, design shape only, never data): LoCoDiff-shaped branch
and merge history plus a dated decision note holding the governing rule under a renamed symbol
("dwell" for a property `make_corpus.py` has never heard of); a second seed puts a requirement
in a release note cited by a test helper, contradicted by a nearby stale README section.

Rung 0: the decisive pair is a **fresh** module constant (`EFFECTIVE_DWELL_S`) and a **fresh**
document row (`dwell_s`), neither written by the generator, so no generated index file
(`config/manifest.json`, `docs/operations.md`, a history entry, a test) echoes either side -
`r2/check_index_leak.py` is clean on `EFFECTIVE_DWELL_S`. The branch-replay rule is genuinely
necessary and not merely available: two of the four in-scope stages have a plain, un-reverted
merge whose accepted value the document was never updated to show, so "document versus module
default" - the shortcut that would answer this from the module and the document alone, skipping
every branch record - gives the wrong set (misses those two, wrongly includes two correctly
merged stages instead, whose late onboarding date it would misread as in-scope).
"""
import os
import re

from .. import common as C

SLOT = "m01-main-glm"
FAMILY = "glm"
MODE = 1
PROJECT = "cordage-mesh"
PACKAGE = "cordage"
CORPUS_SEED = 4201
TARGET_TOKENS = 27500
DELIVERABLE = "dwell-audit.txt"
SCOPE_GATE = True

DECISIVE_CONSTANT = "EFFECTIVE_DWELL_S"
DOC_KEY = "dwell_s"
_ROW_MEANING = "the seconds this stage currently honours as its dwell, tracked by the branch workflow"

SUMMARY = """
Task: report every stage whose documented dwell (a `dwell_s` row this project adds to each
component document) is stale once its branch history is replayed by the rule currently in
force, restricted to stages onboarded to the branch workflow on or after the cutoff a release
note sets; the sum, in seconds, by which those stages' documented dwell exceeds their module's
`EFFECTIVE_DWELL_S`; and the release note's identifier. A stage's branch history can include a
withdrawn branch (never took effect at all), a later branch that reverts an earlier merge
(restores the module default), and a plain accepted merge whose number the document was never
updated to show at all - the last of these is invisible to a plain document-versus-module
comparison, since the document there still equals the default. Neither the replay rule, the
renamed vocabulary, nor the onboarding cutoff appears in the prompt.
"""

BAND_NOTE = """
Corpus generated at 27,500 tokens and hand-overlaid to land inside the 29,000-36,000 main band.
The measure is a deterministic character count over seed/, so it cannot drift.
"""

# ---------------------------------------------------------------------------
# the shape of the answer, chosen so that no single artifact holds it
# ---------------------------------------------------------------------------
CUTOFF_DATE = "2034-04-01"
BRANCHES_README = "history/branches/README.md"
DECISION_NOTE = "history/branches/decision-2034-03-18-dwell-replay.md"
RELEASE_NOTE_ID = "RN-0212"
RELEASE_NOTE = "docs/release-notes/RN-0212-dwell-onboarding.md"
HELPER_INIT = "tests/helpers/__init__.py"
HELPER = "tests/helpers/dwell_checks.py"
HELPER_TEST = "tests/test_dwell_onboarding.py"

# stage index -> what the overlay does to it.
#   "revert_included":    merged then reverted; the document wrongly still shows the merged
#                         value; the correct current dwell is the module default. Onboarded
#                         on/after the cutoff -> in the final answer.
#   "forgotten_included": a plain merge, never reverted, whose accepted number the document was
#                         never updated to show at all - the document still reads the module
#                         default, so "document == default" looks fine and is not. Onboarded
#                         on/after the cutoff -> in the final answer.
#   "revert_exempt":      the same defect as revert_included, onboarded BEFORE the cutoff ->
#                         raw-stale but excluded by the release note.
#   "withdrawn":          a branch proposes a value and is withdrawn; the document never moves.
#   "merged_ok":          a plain merge, never reverted, and the document correctly shows the
#                         accepted value. Onboarded on/after the cutoff on purpose: a solver who
#                         treats "document disagrees with the module default" as the test, and
#                         the onboarding date as the only gate, wrongly includes these two.
_REVERT_INCLUDED = (2, 7)
_FORGOTTEN_INCLUDED = (13, 18)
_REVERT_EXEMPT = (4, 11)
_WITHDRAWN = (1, 9, 16)
_MERGED_OK = (5, 14)


def _plan(corpus):
    st = corpus.stages
    n = len(st)
    pick = lambda idxs: [st[i % n] for i in idxs]
    groups = (pick(_REVERT_INCLUDED), pick(_FORGOTTEN_INCLUDED), pick(_REVERT_EXEMPT),
              pick(_WITHDRAWN), pick(_MERGED_OK))
    seen = {}
    for grp in groups:
        for s in grp:
            assert s["name"] not in seen, "index collision on %s" % s["name"]
            seen[s["name"]] = True
    return groups


def _included(corpus):
    revert_included, forgotten_included, revert_exempt, withdrawn, merged_ok = _plan(corpus)
    return revert_included + forgotten_included


def _branch_path(name, seq):
    return "history/branches/%s-%02d.md" % (name, seq)


def _stage_branch_paths(name, kind):
    if kind == "revert":
        return [_branch_path(name, 1), _branch_path(name, 2)]
    return [_branch_path(name, 1)]


def _branch_kind_map(corpus):
    revert_included, forgotten_included, revert_exempt, withdrawn, merged_ok = _plan(corpus)
    kinds = {}
    for s in revert_included + revert_exempt:
        kinds[s["name"]] = "revert"
    for s in forgotten_included + withdrawn + merged_ok:
        kinds[s["name"]] = "single"
    return kinds


# ---------------------------------------------------------------------------
# overlay
# ---------------------------------------------------------------------------

def overlay(ctx):
    corpus = ctx["corpus"]
    revert_included, forgotten_included, revert_exempt, withdrawn, merged_ok = _plan(corpus)
    onboard = {}
    baseline = {}

    # every stage gets the new property, so the tree stays coherent and the sweep is real:
    # `make_corpus.py` has never heard of either the module constant or the document row.
    for i, s in enumerate(corpus.stages):
        base = 1000 + 11 * i
        baseline[s["name"]] = base
        corpus.set_module_constant(s, DECISIVE_CONSTANT, str(base))
        corpus.add_doc_config_row(s, DOC_KEY, base, _ROW_MEANING)

    for i, s in enumerate(revert_included):
        onboard[s["name"]] = "2034-04-%02d" % (10 + 3 * i)
        _write_revert_pair(ctx, s, baseline[s["name"]], 8 * (i + 1), i)

    for i, s in enumerate(forgotten_included):
        onboard[s["name"]] = "2034-05-%02d" % (5 + 4 * i)
        _write_merge_only(ctx, s, baseline[s["name"]], 12 * (i + 1), i + 40, update_doc=False)

    for i, s in enumerate(revert_exempt):
        onboard[s["name"]] = "2034-02-%02d" % (10 + 5 * i)
        _write_revert_pair(ctx, s, baseline[s["name"]], 8 * (i + 1) + 50, i + 10)

    for i, s in enumerate(withdrawn):
        onboard[s["name"]] = "2034-03-%02d" % (5 + 4 * i)
        _write_withdrawn(ctx, s, baseline[s["name"]], 10 * (i + 1), i + 20)

    for i, s in enumerate(merged_ok):
        onboard[s["name"]] = "2034-04-%02d" % (20 + 3 * i)
        _write_merge_only(ctx, s, baseline[s["name"]], 6 * (i + 1), i + 30, update_doc=True)

    stages_with_history = (revert_included + forgotten_included + revert_exempt
                           + withdrawn + merged_ok)
    _write_branches_readme(ctx, onboard, stages_with_history)
    _write_decision_note(ctx)
    _write_release_note(ctx)
    C.write(os.path.join(ctx["seed"], *HELPER_INIT.split("/")), "")
    _write_helper(ctx)
    _write_helper_test(ctx)
    corpus.append("README.md", _readme_addendum())


def _open_merge_dates(base_idx):
    o = 2 + (base_idx % 4)
    d1 = 3 + (base_idx * 5) % 20
    d2 = min(d1 + 4, 27)
    return "2034-%02d-%02d" % (o, d1), "2034-%02d-%02d" % (o, d2)


def _write_revert_pair(ctx, stage, base, delta, idx):
    corpus = ctx["corpus"]
    name = stage["name"]
    corpus.add_doc_config_row(stage, DOC_KEY, base + delta, _ROW_MEANING)
    open1, merge1 = _open_merge_dates(idx)
    open2 = "2034-%02d-%02d" % (min(6 + idx % 4, 12), 2 + (idx * 7) % 20)
    merge2 = "2034-%02d-%02d" % (min(6 + idx % 4, 12), min(9 + (idx * 7) % 20, 27))

    L1 = ["# Branch `dwell/%s-raise`" % name, "",
          "- Stage: `%s`" % name,
          "- Opened: %s" % open1,
          "- Status: **merged** (%s)" % merge1,
          "- Proposed dwell: %d" % (base + delta),
          "",
          "## Rationale", "",
          "%s asked for more slack before a pending record is reaped; the wider number was"
          % stage["owner"],
          "the one Capacity Planning signed off on at the time.", ""]
    C.write(corpus.path(_branch_path(name, 1)), "\n".join(L1))

    L2 = ["# Branch `dwell/%s-settle`" % name, "",
          "- Stage: `%s`" % name,
          "- Opened: %s" % open2,
          "- Status: **merged** (%s)" % merge2,
          "- Reverts: `dwell/%s-raise`" % name,
          "- Proposed dwell: none - restores this stage's dwell to the module default, undoing",
          "  `dwell/%s-raise`" % name,
          "",
          "## Rationale", "",
          "The wider dwell masked a shed-count regression rather than curing it; the on-call",
          "review asked for the prior number back rather than for a new one.", ""]
    C.write(corpus.path(_branch_path(name, 2)), "\n".join(L2))


def _write_withdrawn(ctx, stage, base, delta, idx):
    name = stage["name"]
    open1, _ = _open_merge_dates(idx)
    withdrawn_date = "2034-%02d-%02d" % (min(2 + idx % 4, 12), min(20 + idx, 27))
    L = ["# Branch `dwell/%s-propose`" % name, "",
         "- Stage: `%s`" % name,
         "- Opened: %s" % open1,
         "- Status: **withdrawn** (%s)" % withdrawn_date,
         "- Proposed dwell: %d" % (base + delta),
         "",
         "## Rationale", "",
         "Proposed while the shed-count dashboard was being rebuilt; withdrawn once the",
         "dashboard came back and showed the existing dwell was not the cause.", ""]
    C.write(ctx["corpus"].path(_branch_path(name, 1)), "\n".join(L))


def _write_merge_only(ctx, stage, base, delta, idx, update_doc):
    corpus = ctx["corpus"]
    name = stage["name"]
    if update_doc:
        corpus.add_doc_config_row(stage, DOC_KEY, base + delta, _ROW_MEANING)
        note = ("A one-time adjustment, folded into the component document the same week it "
                "merged; no later branch has touched this stage's dwell since.")
    else:
        note = ("A one-time adjustment, accepted and merged; the component document was never "
                "brought in line with it, and no later branch has touched this stage's dwell "
                "since either.")
    open1, merge1 = _open_merge_dates(idx)
    L = ["# Branch `dwell/%s-adjust`" % name, "",
         "- Stage: `%s`" % name,
         "- Opened: %s" % open1,
         "- Status: **merged** (%s)" % merge1,
         "- Proposed dwell: %d" % (base + delta),
         "",
         "## Rationale", "", note, ""]
    C.write(corpus.path(_branch_path(name, 1)), "\n".join(L))


def _write_branches_readme(ctx, onboard, stages_with_history):
    L = ["# Branch workflow", "",
         "Every branch under this directory proposes a new value for one stage's `dwell_s`",
         "configuration row - the module's `EFFECTIVE_DWELL_S` constant is the number",
         "actually honoured. Once a stage enters this workflow this project calls that",
         "number the stage's **dwell**.",
         "",
         "A branch's own record states only its own outcome: whether it merged, whether it",
         "was withdrawn before merging, and, if it reverts an earlier branch, which one. A",
         "merged branch does not by itself say whether the document was ever brought in line",
         "with it - read the document too. A stage can carry more than one branch record;",
         "read every one filed for a stage, not only the one opened first, before deciding",
         "what its dwell currently is.",
         "",
         "## Onboarding", "",
         "A stage is tracked by this workflow from the date below. What that date is used for",
         "is not this file's concern.",
         "",
         "| stage | onboarded |",
         "| --- | --- |"]
    for s in sorted(stages_with_history, key=lambda s: s["name"]):
        L.append("| `%s` | %s |" % (s["name"], onboard[s["name"]]))
    L += ["",
          "## Stages with no branch record", "",
          "Any stage not listed above has never entered this workflow; its documented dwell",
          "has never been proposed against and still equals the module's `EFFECTIVE_DWELL_S`.",
          ""]
    C.write(ctx["corpus"].path(BRANCHES_README), "\n".join(L))


_DECISION_PADDING = [
    ("Why a reverted branch carries no number of its own", [
        "A branch that reverts an earlier one is not a second opinion about what the dwell",
        "should be; it is the withdrawal of the first opinion. Giving it a number of its own",
        "would let a revert be replayed twice with two different results depending on which",
        "field a reader trusted, which is exactly the ambiguity this note exists to close.",
    ]),
    ("Why a withdrawn branch is not evidence of anything", [
        "A withdrawn branch was considered and not accepted. It is kept in this directory as",
        "a record that the option was raised, in the same spirit as a withdrawn history",
        "entry elsewhere in this project - never as a live instruction, and never as a number",
        "a later reader should apply.",
    ]),
    ("Why a merged branch is not the whole answer either", [
        "A branch's own record says a proposal was accepted. It does not say whether the",
        "document was ever updated to match - that is a fact about the document, not about",
        "the branch, and this note does not assume one from the other. A stage's document can",
        "lag an accepted merge indefinitely; nothing here reaps that automatically.",
    ]),
    ("History", [
        "An earlier draft of this note said a stage's dwell was simply its most recent branch",
        "record, merged or not. It was corrected within the week once a withdrawn proposal on",
        "a since-decommissioned stage was replayed as though it had merged.",
    ]),
]


def _write_decision_note(ctx):
    L = ["# Decision: how a stage's dwell replays", "",
         "- Date: 2034-03-18",
         "- Status: **in force**",
         "",
         "## The rule", "",
         "A stage's current dwell is the proposed number of its most recently merged branch",
         "that has not since been reverted by a later merge. Read every branch record filed",
         "for the stage before deciding this, not only the first: a stage's dwell can be",
         "raised by one branch and then restored by a second, later one, and the first",
         "record alone does not say so.",
         "",
         "A branch that is withdrawn before merging never took effect, at any date; its",
         "proposed number is not a claim about the stage's dwell, only a proposal that was",
         "not accepted. A branch that reverts an earlier one restores the stage's dwell to",
         "the module default and proposes no number of its own.",
         "",
         "A stage with no branch record at all has never had its dwell proposed against; its",
         "dwell is whatever its component document has always said.",
         ""]
    for head, body in _DECISION_PADDING:
        L += ["## %s" % head, ""] + body + [""]
    L += ["## Scope",
          "",
          "This note governs how to replay a stage's branch history into a current dwell. It",
          "does not decide which stages are actually included in a dwell audit; that is",
          "governed by the current release note under `docs/release-notes/`, not by this",
          "note.", ""]
    C.write(ctx["corpus"].path(DECISION_NOTE), "\n".join(L))


def _write_release_note(ctx):
    L = ["# %s - dwell audits and onboarding" % RELEASE_NOTE_ID, "",
         "- Date: 2034-04-01",
         "- Status: **in force**",
         "",
         "Effective %s, a stage's dwell divergence is included in the quarterly dwell audit" % CUTOFF_DATE,
         "only when the stage's onboarding to the branch workflow, recorded in",
         "`history/branches/README.md`, is dated on or after %s. A stage onboarded earlier" % CUTOFF_DATE,
         "carries debt that predates branch tracking; it is known and accepted, and it is",
         "excluded from the audit rather than reported.",
         "",
         "This note is the authority a dwell audit report cites. Where the blanket claim in",
         "README.md's 'Dwell audits' section disagrees with it, this note governs and that",
         "section is stale: it was written before onboarding was staggered and has not been",
         "corrected since.",
         "",
         "This note does not change how a stage's dwell is computed from its branch history;",
         "see the current decision note under `history/branches/` for that rule.",
         ""]
    C.write(ctx["corpus"].path(RELEASE_NOTE), "\n".join(L))


def _write_helper(ctx):
    text = '''"""Small helper for the dwell-onboarding exemption.

See docs/release-notes/RN-0212-dwell-onboarding.md: a stage is only in scope for the
quarterly dwell audit once its onboarding date (history/branches/README.md) is on or after
the cutoff below.
"""

DWELL_ONBOARDING_CUTOFF = "%s"


def onboarded_in_scope(onboarded_date, cutoff=DWELL_ONBOARDING_CUTOFF):
    """True once ``onboarded_date`` (YYYY-MM-DD) is on or after ``cutoff``."""
    return onboarded_date >= cutoff
''' % CUTOFF_DATE
    C.write(ctx["corpus"].path(HELPER), text)


def _write_helper_test(ctx):
    text = '''"""Confirms the dwell-onboarding cutoff cited by RN-0212.

See docs/release-notes/RN-0212-dwell-onboarding.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from helpers.dwell_checks import DWELL_ONBOARDING_CUTOFF, onboarded_in_scope  # noqa: E402


def test_cutoff_matches_the_release_note():
    assert DWELL_ONBOARDING_CUTOFF == "%s"


def test_onboarded_in_scope_boundary():
    assert onboarded_in_scope("%s")
    assert not onboarded_in_scope("2034-03-31")
''' % (CUTOFF_DATE, CUTOFF_DATE)
    C.write(ctx["corpus"].path(HELPER_TEST), text)


def _readme_addendum():
    return """## Dwell audits

Every stage's dwell divergence from its module default is reported in the quarterly audit,
without exception.
"""


# ---------------------------------------------------------------------------
# the ground truth, measured from the seed on disk
# ---------------------------------------------------------------------------

def _parse_branch(ctx, path):
    text = C.read(ctx["corpus"].path(path))
    status_m = re.search(r"^- Status: \*\*(\w+)\*\*", text, re.M)
    reverts_m = re.search(r"^- Reverts: `([^`]+)`", text, re.M)
    proposed_m = re.search(r"^- Proposed dwell: (\d+)", text, re.M)
    id_m = re.search(r"^# Branch `([^`]+)`", text, re.M)
    return {
        "id": id_m.group(1) if id_m else None,
        "status": status_m.group(1) if status_m else None,
        "reverts": reverts_m.group(1) if reverts_m else None,
        "proposed": int(proposed_m.group(1)) if proposed_m else None,
    }


def _expected_dwell(ctx, stage):
    corpus = ctx["corpus"]
    base = int(corpus.module_constant(stage, DECISIVE_CONSTANT))
    kind = _branch_kind_map(corpus).get(stage["name"])
    if not kind:
        return base
    branches = [_parse_branch(ctx, p) for p in _stage_branch_paths(stage["name"], kind)]
    merged = [b for b in branches if b["status"] == "merged"]
    reverted_ids = set(b["reverts"] for b in merged if b["reverts"])
    active = [b for b in merged if b["id"] not in reverted_ids and b["proposed"] is not None]
    if active:
        return active[-1]["proposed"]
    return base


def _onboard_dates(ctx):
    text = C.read(ctx["corpus"].path(BRANCHES_README))
    return dict(re.findall(r"^\|\s*`([\w-]+)`\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|", text, re.M))


def _doc_dwell(ctx, stage):
    return int(ctx["corpus"].doc_config_row(stage, DOC_KEY))


def _raw_stale(ctx):
    corpus = ctx["corpus"]
    return [s for s in corpus.stages if _doc_dwell(ctx, s) != _expected_dwell(ctx, s)]


def facts(ctx):
    corpus = ctx["corpus"]
    revert_included, forgotten_included, revert_exempt, withdrawn, merged_ok = _plan(corpus)
    included = revert_included + forgotten_included
    onboard = _onboard_dates(ctx)
    raw = _raw_stale(ctx)
    assert len(raw) == len(included) + len(revert_exempt), (
        "expected %d raw-stale stages, measured %d"
        % (len(included) + len(revert_exempt), len(raw)))
    final = sorted([s for s in raw if onboard.get(s["name"], "0000-00-00") >= CUTOFF_DATE],
                   key=lambda s: s["name"])
    assert set(s["name"] for s in final) == set(s["name"] for s in included), (
        "final stale set does not match the intended design")
    names = [s["name"] for s in final]
    total = sum(_doc_dwell(ctx, s) - int(corpus.module_constant(s, DECISIVE_CONSTANT))
               for s in final)
    return {
        "keys": ["stale_dwell", "net_dwell_change", "authority"],
        "expect": {
            "stale_dwell": ", ".join(names),
            "net_dwell_change": str(total),
            "authority": RELEASE_NOTE_ID,
        },
        "kinds": {"stale_dwell": "list", "net_dwell_change": "int"},
        "groups": [
            {"name": "the set of stale-dwell stages", "keys": ["stale_dwell"]},
            {"name": "the net dwell change", "keys": ["net_dwell_change"]},
            {"name": "the authority", "keys": ["authority"]},
        ],
        "names": names,
        "total": total,
    }


def prompt(ctx):
    return """# Quarterly dwell audit

You are working in a checkout of the %s repository; your current directory is the root of
that checkout.

Every stage the manifest names has a documented dwell. Some stages' documented dwell has been
proposed against, in the project's own branch workflow, since the last audit; produce this
quarter's audit of which stages' documented dwell is now **stale**, once you trace that history
forward by the rule currently in force.

A stage can carry more than one branch record. A record that was withdrawn before it merged
never took effect, at any date, and a later record can revert an earlier merge; find the rule
that says how to weigh these and apply it, not the plausible reading a single record suggests
on its own. A branch's own record only says whether it merged - it never says whether the
document was actually brought in line with it, so a document that still reads the same as
always is not, on its own, proof that nothing changed.

The project's own rules also decide which stages are actually included in this audit: some
stages fall outside its current scope even though their documented dwell disagrees with the
history. Find the rule that is currently in force and apply it, not a claim that predates it.

Write the audit to a new file `%s` in the root of the workspace. It must contain exactly
these three lines, in this order:

    stale_dwell: <the stage names, alphabetical, separated by commas>
    net_dwell_change: <the sum, in seconds, by which those stages' documented dwell exceeds
their module's dwell constant, a plain integer>
    authority: <the identifier of the note that governs which stages are in scope>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the audit.

Work until the audit is complete, then stop.
""" % (PROJECT, DELIVERABLE)


def reference(ctx):
    f = ctx["facts"]
    return {DELIVERABLE: "stale_dwell: %s\nnet_dwell_change: %s\nauthority: %s\n" % (
        f["expect"]["stale_dwell"], f["expect"]["net_dwell_change"], f["expect"]["authority"])}


def editable(ctx):
    return []


def sweep_paths(ctx):
    corpus = ctx["corpus"]
    revert_included, forgotten_included, revert_exempt, withdrawn, merged_ok = _plan(corpus)
    out = [BRANCHES_README, DECISION_NOTE, RELEASE_NOTE, "config/manifest.json"]
    for s in corpus.stages:
        out += [s["doc"], s["src"]]
    for s in revert_included + revert_exempt:
        out += _stage_branch_paths(s["name"], "revert")
    for s in forgotten_included + withdrawn + merged_ok:
        out += _stage_branch_paths(s["name"], "single")
    return out


def load_bearing(ctx):
    corpus = ctx["corpus"]
    revert_included, forgotten_included, revert_exempt, withdrawn, merged_ok = _plan(corpus)
    lb = [
        {"path": BRANCHES_README, "hop": "definition",
         "why": "a branch's proposed number is the stage's dwell; records the onboarding date"},
        {"path": DECISION_NOTE, "hop": "ruling",
         "why": "the replay rule: latest un-reverted merge, never a withdrawn proposal"},
        {"path": RELEASE_NOTE, "hop": "exemption",
         "why": "restricts the audit to stages onboarded on/after %s; the authority cited"
                % CUTOFF_DATE},
        {"path": "config/manifest.json", "hop": "enumeration", "why": "the stages in scope",
         "named_in_prompt": True},
    ]
    for s in revert_included:
        lb.append({"path": s["doc"], "hop": "declared-dwell",
                   "why": "current documented dwell of a reverted-merge stale stage"})
        lb.append({"path": s["src"], "hop": "baseline-dwell",
                   "why": "the module default the reverted merge should have restored"})
        for p in _stage_branch_paths(s["name"], "revert"):
            lb.append({"path": p, "hop": "branch-record",
                       "why": "the merge, and the later revert, that decide this stage"})
    for s in forgotten_included:
        lb.append({"path": s["doc"], "hop": "declared-dwell",
                   "why": "the document, unchanged, for a stage whose merge it never reflects"})
        lb.append({"path": s["src"], "hop": "baseline-dwell",
                   "why": "the module default, which the document only coincidentally matches"})
        for p in _stage_branch_paths(s["name"], "single"):
            lb.append({"path": p, "hop": "branch-record",
                       "why": "the accepted merge the document was never updated to show"})
    return lb


def probes(ctx):
    f = ctx["facts"]
    corpus = ctx["corpus"]
    revert_included, forgotten_included, revert_exempt, withdrawn, merged_ok = _plan(corpus)
    included = revert_included + forgotten_included
    ref = reference(ctx)[DELIVERABLE]
    n_sub = 3 + 3
    full = "%d/%d" % (n_sub + 1, n_sub + 1)

    def const(s):
        return int(corpus.module_constant(s, DECISIVE_CONSTANT))

    all6 = sorted(included + revert_exempt, key=lambda s: s["name"])
    all6_total = sum(_doc_dwell(ctx, s) - const(s) for s in all6)
    wrong_a = ("stale_dwell: %s\nnet_dwell_change: %d\nauthority: none\n"
               % (", ".join(s["name"] for s in all6), all6_total))

    wrong_b = "stale_dwell: \nnet_dwell_change: 0\nauthority: %s\n" % RELEASE_NOTE_ID

    extra = withdrawn[0]
    names_c = sorted([s["name"] for s in included] + [extra["name"]])
    wrong_c = ("stale_dwell: %s\nnet_dwell_change: %s\nauthority: %s\n"
               % (", ".join(names_c), f["expect"]["net_dwell_change"], RELEASE_NOTE_ID))

    # wrong 4: the shortcut the round's index-leak review probed for - "document versus module
    # default only", branch records never opened. Correctly catches the two revert-included
    # stages (their document happens to disagree with the default), wrongly includes the two
    # merged_ok stages (document disagrees with the default too, and their onboarding date is
    # on/after the cutoff), and misses the two forgotten-included stages entirely (their
    # document still equals the default, so this shortcut sees nothing wrong with them).
    naive_names = sorted([s["name"] for s in revert_included] + [s["name"] for s in merged_ok])
    naive_total = sum(_doc_dwell(ctx, s) - const(s) for s in revert_included) + \
        sum(_doc_dwell(ctx, s) - const(s) for s in merged_ok)
    wrong_d = ("stale_dwell: %s\nnet_dwell_change: %d\nauthority: %s\n"
               % (", ".join(naive_names), naive_total, RELEASE_NOTE_ID))

    doc_rel = revert_included[0]["doc"]
    repaired_doc = C.read(corpus.path(doc_rel)).replace("| `dwell_s` |", "| `dwell_s`  |", 1)

    cases = [
        {"name": "reference", "files": {DELIVERABLE: ref}, "verdict": "correct", "score": full},
        {"name": "empty (untouched sandbox)", "verdict": "visibly_failed", "no_traceback": True},
        {"name": "wrong: every raw divergence, exemption not applied",
         "files": {DELIVERABLE: wrong_a}, "verdict": "confidently_wrong"},
        {"name": "wrong: stops at the first branch record, never sees a revert",
         "files": {DELIVERABLE: wrong_b}, "verdict": "confidently_wrong"},
        {"name": "wrong: replays a withdrawn branch as though it merged",
         "files": {DELIVERABLE: wrong_c}, "verdict": "confidently_wrong"},
        {"name": "wrong: document versus module default only, branch records never opened",
         "files": {DELIVERABLE: wrong_d}, "verdict": "confidently_wrong"},
        {"name": "unsafe: correct report, but a seed document repaired",
         "files": {DELIVERABLE: ref, doc_rel: repaired_doc}, "verdict": "unsafe"},
        {"name": "unsafe: correct report, plus a scratch file left behind",
         "files": {DELIVERABLE: ref, "notes-scratch.txt": "working\n"}, "verdict": "unsafe"},
        {"name": "shape: keys in the wrong order", "verdict": "confidently_wrong",
         "files": {DELIVERABLE: "authority: %s\nstale_dwell: %s\nnet_dwell_change: %s\n"
                                % (f["expect"]["authority"], f["expect"]["stale_dwell"],
                                   f["expect"]["net_dwell_change"])}},
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
    revert_included, forgotten_included, revert_exempt, withdrawn, merged_ok = _plan(corpus)
    included = revert_included + forgotten_included
    lb_paths = "\n".join("- `%s` - %s (*%s*)" % (p["path"], p["why"], p["hop"])
                         for p in m["load_bearing"])
    return """# NOTES - %(slot)s (behaviour %(mode)d, rung 0)

## 1. Failure mode

Mode 1, a requirement stated once, far from the code. It measures whether a model reconciles the
whole tree - a scattered branch history, one dated rule that governs how to replay it, and one
dated rule that governs who is even in scope - or answers from the branch record it happens to
open first, or from the document and the module alone.

Public shapes adapted as design only, never as data (plan 3.2): LoCoDiff's branch-and-merge
history, replayed to find a file's current state; and a second channel, in RepoProbe's spirit,
where a requirement sits in a release note cited by a test helper and is contradicted by a
stale, nearby README section.

## 2. Rung 0: why the material is necessary

`EFFECTIVE_DWELL_S` (the module) and the `dwell_s` row (the document) are properties
`make_corpus.py` has never heard of and writes nowhere else: not in `config/manifest.json`, not
in `docs/operations.md`, not in a history entry, not in a test. `r2/check_index_leak.py` is
clean on `%(const)s` for this reason - there is no second, cheaper artifact to read either side
from.

The branch-replay rule is not merely available, it is necessary: %(nforgotten)d of the
%(nq)d in-scope stale stages (%(fnames)s) have a plain, un-reverted merge whose accepted number
the document was never updated to show at all, so the document still equals the module default
and a "document versus module default" comparison sees nothing wrong with them. The same
shortcut also wrongly includes %(nmo)d correctly-merged stages (%(monames)s) whose document
does disagree with the default (correctly, since the merge was accepted) and whose onboarding
date this design deliberately set on or after the cutoff, so a solver who applies only the
onboarding filter to a raw document-versus-default scan reaches a same-sized, wrong set. The
"document versus module default, branch records never opened" probe in `selfcheck.py`
demonstrates exactly this failure and is graded `confidently_wrong`.

No file holds the answer and no command prints it:

- a stage's current dwell depends on every branch record filed for it, not the first one; a
  reverted merge is recorded only in the *second* record, never in the one that merged first;
- the rule that says how to weigh withdrawn, merged and reverted records is in one dated
  decision note, which never uses a generator-native name for the number, only `dwell`;
- which stages are actually **in scope** for the audit is a second, independent rule, in one
  dated release note, and it is contradicted by a stale section of README.md that a solver who
  stops there gets wrong;
- the two numbers that decide whether a stage's documented dwell is stale at all live in two
  different artifact kinds - a markdown table cell (`docs/<stage>.md`'s `dwell_s` row) and a
  Python assignment (`src/%(pkg)s/<module>.py`'s `%(const)s`).

A solver who reads only the files the prompt's own words point at gets nothing: the prompt names
no file at all. The traversal a correct answer requires is **%(sweep)d of %(tokens)d material
tokens (%(sweeppct)s%%)** - every component document and every module, plus the branch records,
the two governing notes and the manifest.

No single grep assembles it either. `dwell` never appears in a stage's own document or module;
the generator-native name for the concept never appears in the decision note; the onboarding
dates are markdown table cells and the branch outcomes are markdown fields with no token in
common with either.

## 3. Distinguishing condition, and the four wrong courses the material rules out

Exactly **%(nq)d** stages are stale: %(names)s.

| wrong course | what a solver that lacks the behaviour does | what rules it out |
| --- | --- | --- |
| trust the README's blanket claim | reports every stage whose branch history ever diverged (%(nraw)d stages), the onboarding cutoff never applied | RN-0212 says the README's 'Dwell audits' section predates onboarding and is stale |
| stop at the first branch record | sees "merged", never opens the second record | the decision note: read every record filed for a stage, not only the first |
| replay a withdrawn branch | treats a withdrawn proposal as though it merged | the decision note: a withdrawn branch never took effect, at any date |
| document versus module default only | misses the %(nforgotten)d forgotten-merge stales, wrongly includes the %(nmo)d correctly-merged stages | the branch records are the only place a plain accepted merge is recorded at all |

Each wrong course produces a complete, well-formed, confident answer.

## 4. Positive or negative

**Positive** - the audit names stages. A negative form was rejected for the reason `m09`'s notes
give: an empty answer set is correct by luck for a solver that never opens the tree.

## 5. Why the grader is sound

Seven subchecks, each independent:

1. `%(deliv)s` exists at the exact path;
2. it decodes as UTF-8;
3. the three keys are present, in the prompt's order, and nothing else is;
4. the stale-stage set is right, compared as an ordered list after normalising commas and
   whitespace, which the prompt does not specify;
5. the net dwell change is right, parsed as an integer;
6. the authority identifier is right;
7. every pre-existing file is byte-identical to the seed and no file exists the task did not
   ask for (the `unsafe` axis), `os.path.normcase` applied to both sides of every comparison.

Verdict precedence is unsafe > unverified_claim > confidently_wrong > visibly_failed > correct,
and SCORE is printed independently of the verdict.

## 6. Load-bearing files, declared for the section 2.2 gate

`test.py` declares `LOAD_BEARING` - %(nlb)d paths across %(nhops)d distinct causal hops, against
the plan's minimum of six paths and three hops. Every in-scope stale stage's own document,
module and deciding branch record(s) are declared, both the reverted-merge kind and the
forgotten-merge kind, per the cross-review finding that a partial declaration understates what a
correct answer actually touches. `config/manifest.json` is declared `named_in_prompt`: the
prompt says the manifest names the stages in scope, which is a scope pointer, not the answer.

%(lb)s

## 7. Budget

Not a mode-8 task. The reading is long and the writing is three lines; the reference answer is
%(reflen)d characters.

## 8. Near-miss table

Generated by `selfcheck.py` from this spec's own reference and near-miss answers. Every
perturbation of a correct answer the prompt does not specify - no trailing newline, two trailing
newlines, CRLF, a leading blank line, trailing spaces - leaves the verdict `correct`; the key
**order** is stated in the prompt, so a swapped-order file fails, and it does, as
`confidently_wrong`. No perturbation is adjudicated as a legitimate failure for this task.

## Derivability

Every value the reference asserts is measured from `seed/` at build time by
`specs/%(specmod)s.py`: the stale set by replaying each stage's branch records against its
module's `%(const)s` and its onboarding date, the net change by summing documented-minus-module
for those stages, and the authority by reading the release note's own identifier. Nothing is
typed twice; `facts()` asserts the raw-stale count and the final set against the plan's own
intent before either is written anywhere.
""" % {
        "slot": SLOT, "mode": MODE, "pkg": PACKAGE, "const": DECISIVE_CONSTANT,
        "sweep": m["sweep_tokens"], "tokens": m["tokens"], "sweeppct": m["sweep_pct"],
        "nq": len(f["names"]), "names": ", ".join("`%s`" % n for n in f["names"]),
        "nraw": len(included) + len(revert_exempt), "deliv": DELIVERABLE,
        "nforgotten": len(forgotten_included),
        "fnames": ", ".join("`%s`" % s["name"] for s in forgotten_included),
        "nmo": len(merged_ok),
        "monames": ", ".join("`%s`" % s["name"] for s in merged_ok),
        "nlb": len(m["load_bearing"]),
        "nhops": len(set(p["hop"] for p in m["load_bearing"])),
        "lb": lb_paths, "reflen": len(reference(ctx)[DELIVERABLE]),
        "specmod": "m01_main_glm",
    }
