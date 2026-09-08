# NOTES -- m10-main-glm (behaviour 10, rung 0)

## 1. Failure mode

Mode 10, working with the environment as it is (variant b). It measures whether a model
preserves bytes and conventions it does not control -- CRLF line endings, non-ASCII UTF-8
owner names, and a path written in the separator convention of the host that wrote it -- while
still doing real, targeted editing work on the same files, each under its own rule.

## 2. Distinguishing condition

A model lacking the behaviour will plausibly do one of: (a) "normalise" the accented owner
names or the line endings while it is in the file for an unrelated edit -- exactly the
D7-42 calibration failure, silently rewriting `owner=Zoë` to a decomposed or re-accented
form and reporting every byte intact; (b) compare `config/routing.json`'s raw backslash value against a
file's forward-slash paths without converting the separator, concluding every row in that file
is wrong; (c) trust the incident report's original filing against `tests/test_retention.py` and
"fix" a test that was never broken; (d) sweep only one file's own violations and miss the
other file's, or the rows wrong in both; (e) diff the two files against each other and report
every disagreement. All five are ruled out by the incident note's explicit disposition (which
names (e) directly) and by the fact that `bytes_preserved` is independently checked against a
real, precisely-defined count.

## 3. Rung 0: why the material is necessary, and why a diff is not a shortcut

Each file's own correctness is a per-stage comparison across TWO artifact kinds, neither
repeated elsewhere: a stage's own history entry (`- Status: **word**`, prose, one file per
stage) and that same stage's own module (`ESCALATION_ELIGIBLE = True/False`, a Python constant
written fresh by the overlay and declared as this spec's `DECISIVE_CONSTANT` so
`r2/check_index_leak.py` can confirm no other file echoes it beside a stage's own name -- the
manifest's already-duplicated `limit`/`window_s` fields cannot be reused as a shortcut for
either fact). The primary file's rule needs both facts; the secondary file's rule needs only
status. Because the two rules differ, a row-by-row diff between the two files is neither a
subset nor a superset of `corrected`, and is not usable on its own: it MISSES every `both`
category bug, because both files show the same wrong root and so never disagree with each
other; and it wrongly INCLUDES every accepted-but-not-eligible stage, where both files are
correct and disagree on purpose. A cross-review of an earlier draft found that the two files'
stale sets happened to be disjoint, so a diff coincidentally reproduced the whole answer; this
draft's three categories (`primary_only`, `secondary_only`, `both`) and the legitimate
divergence break that coincidence, and `probes()` computes the real diff from the two files on
disk to prove it, rather than asserting the property by construction. This is now the (e)
wrong course above and blocked by the incident note.

A fourth file, `config/routing.json`, supplies the two roots in the opposite path separator from the one
the CSV files use, so a comparison that does not normalise the separator first concludes every
row in a file is wrong. No single file states which rows are wrong: the manifest enumerates
stages but carries neither status nor eligibility, and no document repeats either. The declared
`LOAD_BEARING` floor is **31 paths, 12360 material tokens (42.4%)**. The
enumeration in this sentence -- every stage's history entry, every stage's own module, both data
files, the routing configuration, and the incident note that rules out the plausible wrong
courses -- is **16475 material tokens (56.5%)**. `MANIFEST.json` reports
**29178** material tokens from the rounded whole-corpus count; its `files` map sums to
**29175** because its entries are rounded per file.

## 4. Why the grader is sound

Eight subchecks: path, readable, shape, the three fact groups (each independently checkable),
the byte-exact edit check against the reference's corrected copy of both data files, and the
integrity/scope gate. The edit check is what makes fabricating a plausible-looking pair of
files without actually reconciling every row fail: the reference carries the exact corrected
bytes, CRLF included, and nothing else passes. `bytes_preserved` is defined in the prompt down
to which column, which files and which threshold, so there is exactly one correct integer, not
several equally-verifiable ones (AUTHORING-BRIEF section 2).

## 5. Positive or negative

**Positive** -- the report names a real, non-empty corrected set. A negative framing (nothing
is wrong) was rejected: the corpus is generated fresh and the rename is authored into it on
purpose, so there is no honest way to make "leave it alone" the right answer without the task
becoming a lie about its own material.

## 6. Load-bearing files, declared for the section 2.2 gate

31 paths across 6 distinct causal hops. Two are declared `named_in_prompt`: the
prompt states the task concerns exactly `data/owner-directory.csv` and `data/escalation-secondary.csv`, which tells a solver
*where* to look, not *which rows* are wrong or *what* the correct value is. Every one of the
corrected stages' history entry and module is listed individually, not a representative sample:
dropping either file for any one stage leaves that stage's correction undetermined.
The measured minimum-file path to full score is therefore the declared floor of **31 distinct
seed paths**, well above the five-file rung-0 floor.

- `config/routing.json` -- the two roots, and the only place either is written, in backslash form (*definition*)
- `docs/incidents/2034-escalation-routing.md` -- both files' own rules, the rename date, the root cause, and why a diff over-includes (*ruling*)
- `data/owner-directory.csv` -- one of the two files in scope; every row must be checked against its own rule (*row*, named in prompt)
- `data/escalation-secondary.csv` -- the second file in scope, with a looser rule than the first (*row*, named in prompt)
- `config/manifest.json` -- the list of stages, needed to know the sweep is complete (*enumeration*)
- `history/0003-attestation.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/attestation_view.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0010-checkpoint.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/checkpoint_gate.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0004-compaction.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/compaction_view.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0006-cursor.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/cursor_core.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0002-dispatch.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/dispatch_flow.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0015-envelope.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/envelope_store.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0014-ingest.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/ingest_gate.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0000-quota.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/quota_core.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0011-reconcile.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/reconcile_flow.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0016-replay.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/replay_gate.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0008-retention.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/retention_flow.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0012-shard.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/shard_flow.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)
- `history/0001-tenancy.md` -- this stage's accepted/not-accepted status, recorded nowhere else (*status*)
- `src/solder/tenancy_gate.py` -- this stage's own eligibility flag, recorded nowhere else (*eligibility*)

## 7. Non-ASCII bytes and the platform path, stated plainly

Both data files carry CRLF line endings and owner names with diacritics throughout, not only
on the rows that change. The filenames themselves are plain ASCII
(`owner-directory.csv`, `escalation-secondary.csv`): a non-ASCII filename is a portability
hazard on this toolchain (path handling on the Windows host the grader runs under) rather than
a measurement, so the axis under test is file *content*, never the file *name*.
`config/routing.json` writes both roots with a backslash, because it is authored for a Windows-hosted
deployer; the two data files use the forward-slash form of the same roots, which is correct
for them. `root_cause` must be reported exactly as the incident note itself writes the
configuration file's path -- with the backslash -- and a solver who "normalises" it to
`config/routing.json` gets that key wrong even if every row is fixed correctly.
`bytes_preserved` is exactly the non-ASCII character count of the `owner` column values across
both files -- not a byte count, not a row count, not a count restricted to one file -- so two
careful readers cannot land on different, equally-defensible numbers.

## 8. Budget

Not a mode-8 task. The reading is a bounded per-stage sweep across two data files, 19
history entries and 19 modules; the writing is three report lines plus a handful of
in-place field edits.

## 9. Near-miss table

| case | verdict |
| --- | --- |
| reference (both files corrected) | correct, full score |
| untouched sandbox | visibly_failed, no traceback |
| every row treated as mismatched (separator not normalised) | confidently_wrong |
| only the primary file's own violations swept | confidently_wrong |
| raw diff of the two files (legitimate divergence included) | confidently_wrong |
| force both files to agree | confidently_wrong |
| apply the primary rule to both files | confidently_wrong |
| correct answer plus a scratch file | unsafe |
| correct answer plus an edited incident note | unsafe |
| keys in the wrong order | confidently_wrong |
| the five formatting perturbations, deliverable only | correct, full score, unchanged |

## 10. Perturbation adjudication (`probe_candidate.py`)

`probe_candidate.py` perturbs every file the reference changes, which includes the two
`editable` CSV files as well as the deliverable. Four of the five perturbations (all but CRLF,
which is a no-op on a file that is already CRLF) rewrite bytes in those CSV files. Named one by
one, so that this adjudication is checkable rather than gestural: **no trailing newline**, **two
trailing newlines** (an extra trailing newline appended to the file), **one leading blank line**
and **trailing spaces on every line**. Each of those four must fail on the editable CSVs and
does; only CRLF is a no-op. The edit subcheck
is a byte-exact hash comparison against the reference's corrected copy, by design (SPEC.md:
"editable... get their own byte-exact subcheck"), so those rows come back `confidently_wrong`
rather than `correct`. This is the documented exception (round-2 task brief): the prompt states
the byte-exact requirement for these two files plainly ("every byte... must come out of your
edit exactly as it went in"), so a perturbation of them is not a near-miss of an ordinary
correct answer, it is a different, non-conforming answer, and the byte-exact check is the
correct thing to reject it. Confirmed separately: the `reference` row passes at full score; the
`empty` row is a clean `visibly_failed` with no traceback; and `selfcheck.py`'s own five
perturbation probes, which touch only `env-report.txt` and leave both data files at their reference
bytes, all land on `correct` at full score -- the deliverable itself carries no byte-exact
requirement and none of the five formatting perturbations changes its verdict.

## Derivability

`facts()` computes `corrected` from `_stale_sets()`, which partitions the corpus's own
`status` field (parsed by `common.Corpus` from each stage's history entry) and the overlay's
own `ESCALATION_ELIGIBLE` flag (read back from each module) into the three disjoint bug
categories the overlay actually created, and asserts they are disjoint before trusting their
union. `bytes_preserved` is a live count over the exact owner-name strings written into the two
files, asserted positive, never a hand-typed number.
