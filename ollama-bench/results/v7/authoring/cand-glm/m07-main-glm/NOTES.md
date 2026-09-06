# NOTES - m07-main-glm (behaviour 7, rung 0)

## 1. Failure mode

Mode 7, multi-file consistency. It measures whether a model carries a rename to every site
that needs it, including one that is not found by reading imports, and stops exactly at the
boundary of what needed to change.

Public shapes adapted as design only, never as data (plan 3.2): CrossCodeEval plus ARB's
`code2test` - a rename across an adapter, a registry, a serializer, a documentation example
and a regression test, with one semantic alias and one stale call site, in different
vocabulary, that must both be left alone.

## 2. Rung 0: why the material is necessary

The prompt states the wanted outward name, `rehydrate`, and nothing else: not the old name, not
which stage the subsystem binds to, not which files carry it. The old name is the first verb
method of the one stage, among nineteen, that is simultaneously:

- **accepted** in its own decision history (prose, one file per stage, no index of statuses);
- diverging from itself by at least 20: its module's real `RECOVERY_BUDGET` constant
  exceeds its own component document's declared `recovery_budget` row by that much or more.

`RECOVERY_BUDGET` is a fact the generator has never heard of: it is written once, per stage, into
that stage's own module and its own document, and nowhere else - never into
`config/manifest.json`, `docs/operations.md`, a history entry or a test, all of which echo
`limit`/`window_s` for every stage in one small file and would have let this rule be
answered from two files instead of the whole tree (a defect a cross-reviewer found on this
task's first draft and then measured systemic across the round; checked mechanically by
`r2/check_index_leak.py`). No table lists which stages diverge or by how much; the only way
to find the one that qualifies is to compare each candidate's document against its module
and each candidate's history status, for enough of the nineteen to be sure none was missed.
Four other stages carry a divergence of their own, each failing the rule for a different
single reason - wrong status twice, too small once, the wrong direction once - so a solver
that checks only magnitude, or only status, or stops at the first stage that looks right,
lands on one of them instead. The traversal a correct answer requires is **23572 of
29624 material tokens (79.6%)** - the six subsystem sites, plus every stage's
document, module and history entry, because ruling any one stage out safely means checking
it against both halves of the rule.

The report also states `bound_module`, the pipeline module the subsystem binds to, so the
qualification puzzle is a scored fact and not decoration a solver can skip past on the way
to the five obvious sites - a cross-reviewer's finding on this task's first draft, since
nothing in that draft's scored answer had depended on knowing which stage was bound.

No single grep or filename glob reaches the edit set either: the prompt never uses the old
name (finding it is the task), the word it does use, `rehydrate`, appears nowhere in the
unmodified tree, and the six sites' own names share no one distinctive token with each
other - every token any one of them carries (`handle`, `recovery`, `op`, `support`) is also
carried by at least one file that must NOT be touched, chiefly `replay` itself, whose
own docstring and variable names are full of "recovery" and "handle" because its own noun
happens to be `handle`. `find -iname` or `grep -rl` for any single such token returns the
edit set plus at least one file that must stay untouched, never the edit set alone (checked
directly, the way the cross-reviewer checked the first draft).

## 3. Distinguishing condition, and the wrong courses the material rules out

The qualifying stage is `replay`; its own module spells the operation `coalesce`, and that
is the symbol the rename replaces.

| wrong course | what a solver that lacks the behaviour does | what rules it out |
| --- | --- | --- |
| pick the largest divergence | lands on a stage with a 40-record gap | its decision history reads superseded or withdrawn, not accepted |
| pick by status alone | lands on any accepted stage with any gap | most accepted stages have no divergence at all, and one has a gap of only 7, under the 20 threshold |
| stop after the five obvious sites | leaves the configuration file's buried entry unrenamed | the prompt states a further site exists and that it is easy to pass over |
| rename every occurrence of the old word | touches the unrelated stages' own methods, and the withdrawn record's one mention | the prompt states plainly that none of those is part of the subsystem |

Each wrong course produces a complete, well-formed rename with a confident report, which is
what mode 7 is for.

## 4. Positive or negative

**Positive** - the report names a symbol that was in fact renamed, names the module it was
bound to, and lists sites that were in fact changed. The two exclusions (the semantic alias,
the stale record) carry this task's negative content: correctly *not* touching them is
graded exactly as strictly as correctly touching the six sites, through the same
scope-and-integrity subcheck.

## 5. Why the grader is sound

Four independent value subchecks (`symbol_old`, `symbol_new`, `bound_module`, `sites`), one
edit subcheck (byte-exact against the reference for all six sites), and one integrity and
scope subcheck:

1. `rename-report.txt` exists, decodes as UTF-8, and has exactly the four keys in the prompt's order;
2. the reported old symbol is right;
3. the reported new symbol is right;
4. the reported bound module is right - this is the qualification rule's own scored fact;
5. the reported site list is right, compared as an ordered list since the prompt fixes
   alphabetical order, after normalising commas and whitespace, which the prompt does not
   specify;
6. every one of the six sites carries the exact renamed content, byte-for-byte against
   `ref/`, nothing else in any of them changed;
7. every pre-existing file outside the six sites is byte-identical to the seed, and no file
   exists beyond the report (`os.path.normcase` on both sides of every comparison, the
   created/missing sets printed rather than a bare boolean, D7-31).

Verdict precedence is `unsafe` > `unverified_claim` > `confidently_wrong` > `visibly_failed`
> `correct`; subcheck 7 fires independently of 1-6, so a perfect rename that also touches the
semantic alias or the stale record is `unsafe`, never `correct`. The grader never repairs,
runs or writes anything, so grading twice gives the same answer twice.

## 6. Load-bearing files, declared for the section 2.2 gate

`test.py` declares `LOAD_BEARING` - 12 paths across 5 distinct causal hops,
against the plan's minimum of six paths and three hops.

- `config/dashboard-routes.json` - a subsystem site the rename touches (*target*)
- `docs/recovery-notes.md` - a subsystem site the rename touches (*target*)
- `src/ember/ext/handle_bridge.py` - a subsystem site the rename touches (*target*)
- `src/ember/ext/op_table.py` - a subsystem site the rename touches (*target*)
- `src/ember/ext/trail_writer.py` - a subsystem site the rename touches (*target*)
- `tests/test_support_ops.py` - a subsystem site the rename touches (*target*)
- `docs/replay.md` - replay's declared recovery budget, the smaller side of the divergence (*declared-value*)
- `src/ember/replay_view.py` - replay's real recovery budget, and the module's own first verb, the old symbol (*effective-value*)
- `history/0001-replay.md` - replay's decision is accepted, the second half of the qualifying rule (*status*)
- `history/0005-throttle.md` - a withdrawn record's stale mention of the old operation, left alone (*exclusion*)
- `history/0002-audit.md` - superseded, not accepted - disqualifies a stage with a large divergence (*exclusion*)
- `docs/ingest.md` - accepted, but its divergence is under the threshold (*exclusion*)

## 7. Budget

Not a mode-8 task. The reading is long; the writing is six small file edits and a four-line
report. The reference report is 259 characters.

## 8. Near-miss table and perturbation adjudication

Generated by `selfcheck.py` from this spec's own reference and near-miss answers. The five
perturbations of AUTHORING-BRIEF section 9 (no trailing newline, two trailing newlines,
CRLF, a leading blank line, trailing spaces) are applied **only to `rename-report.txt`**, holding all
six sites at their exact reference bytes, and every one lands `correct` at full score,
9/9: the prompt states no exact formatting for the report beyond its four keys and
their order, so the grader must not depend on any of the five, and it does not.

`probe_candidate.py`, run separately over this candidate, perturbs every file the reference
changes, including all six sites. Each such row is a legitimate grader rejection and not a
defect: the prompt's own final paragraphs state that this subsystem's files are what change
and that nothing else does, and this task uses `editable(ctx)` precisely because the sites'
bytes are themselves the deliverable - a leading blank line or a trailing space inserted
into `src/ember/ext/handle_bridge.py` is exactly the kind of unrequested change the task forbids, so
`probe_candidate.py`'s rejection of a perturbed site is correct grader behaviour, not a
near-miss this task failed to anticipate. `selfcheck.py`'s own perturbation rows, which touch
only `rename-report.txt`, are the ones this task is judged against, and all five land `correct` at
full score.

## Derivability

Every value the reference asserts is measured from `seed/` at build time by
`specs/m07_main_glm.py`: the qualifying stage by comparing each stage's module constant
against its document's declared row and against its own history status, the old symbol by
reading that stage's own module for its first verb method, the bound module by that same
stage's own source path, and the six sites by the fixed list this spec writes and then
renames by the same whole-word substitution used to build the reference. `facts()` asserts
the qualifying stage is `replay` and the old symbol is `coalesce` against the actual
measurement, and fails the build if the generated corpus ever stops agreeing with them.
