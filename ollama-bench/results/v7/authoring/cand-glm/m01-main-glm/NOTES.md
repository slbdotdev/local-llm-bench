# NOTES - m01-main-glm (behaviour 1, rung 0)

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
clean on `EFFECTIVE_DWELL_S` for this reason - there is no second, cheaper artifact to read either side
from.

The branch-replay rule is not merely available, it is necessary: 2 of the
4 in-scope stale stages (`checkpoint`, `envelope`) have a plain, un-reverted merge whose accepted number
the document was never updated to show at all, so the document still equals the module default
and a "document versus module default" comparison sees nothing wrong with them. The same
shortcut also wrongly includes 2 correctly-merged stages (`throttle`, `retention`) whose document
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
  Python assignment (`src/cordage/<module>.py`'s `EFFECTIVE_DWELL_S`).

A solver who reads only the files the prompt's own words point at gets nothing: the prompt names
no file at all. The traversal a correct answer requires is **23134 of 32213 material
tokens (71.8%)** - every component document and every module, plus the branch records,
the two governing notes and the manifest.

No single grep assembles it either. `dwell` never appears in a stage's own document or module;
the generator-native name for the concept never appears in the decision note; the onboarding
dates are markdown table cells and the branch outcomes are markdown fields with no token in
common with either.

## 3. Distinguishing condition, and the four wrong courses the material rules out

Exactly **4** stages are stale: `checkpoint`, `envelope`, `replay`, `shard`.

| wrong course | what a solver that lacks the behaviour does | what rules it out |
| --- | --- | --- |
| trust the README's blanket claim | reports every stage whose branch history ever diverged (6 stages), the onboarding cutoff never applied | RN-0212 says the README's 'Dwell audits' section predates onboarding and is stale |
| stop at the first branch record | sees "merged", never opens the second record | the decision note: read every record filed for a stage, not only the first |
| replay a withdrawn branch | treats a withdrawn proposal as though it merged | the decision note: a withdrawn branch never took effect, at any date |
| document versus module default only | misses the 2 forgotten-merge stales, wrongly includes the 2 correctly-merged stages | the branch records are the only place a plain accepted merge is recorded at all |

Each wrong course produces a complete, well-formed, confident answer.

## 4. Positive or negative

**Positive** - the audit names stages. A negative form was rejected for the reason `m09`'s notes
give: an empty answer set is correct by luck for a solver that never opens the tree.

## 5. Why the grader is sound

Seven subchecks, each independent:

1. `dwell-audit.txt` exists at the exact path;
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

`test.py` declares `LOAD_BEARING` - 18 paths across 7 distinct causal hops, against
the plan's minimum of six paths and three hops. Every in-scope stale stage's own document,
module and deciding branch record(s) are declared, both the reverted-merge kind and the
forgotten-merge kind, per the cross-review finding that a partial declaration understates what a
correct answer actually touches. `config/manifest.json` is declared `named_in_prompt`: the
prompt says the manifest names the stages in scope, which is a scope pointer, not the answer.

- `history/branches/README.md` - a branch's proposed number is the stage's dwell; records the onboarding date (*definition*)
- `history/branches/decision-2034-03-18-dwell-replay.md` - the replay rule: latest un-reverted merge, never a withdrawn proposal (*ruling*)
- `docs/release-notes/RN-0212-dwell-onboarding.md` - restricts the audit to stages onboarded on/after 2034-04-01; the authority cited (*exemption*)
- `config/manifest.json` - the stages in scope (*enumeration*)
- `docs/replay.md` - current documented dwell of a reverted-merge stale stage (*declared-dwell*)
- `src/cordage/replay_gate.py` - the module default the reverted merge should have restored (*baseline-dwell*)
- `history/branches/replay-01.md` - the merge, and the later revert, that decide this stage (*branch-record*)
- `history/branches/replay-02.md` - the merge, and the later revert, that decide this stage (*branch-record*)
- `docs/shard.md` - current documented dwell of a reverted-merge stale stage (*declared-dwell*)
- `src/cordage/shard_flow.py` - the module default the reverted merge should have restored (*baseline-dwell*)
- `history/branches/shard-01.md` - the merge, and the later revert, that decide this stage (*branch-record*)
- `history/branches/shard-02.md` - the merge, and the later revert, that decide this stage (*branch-record*)
- `docs/checkpoint.md` - the document, unchanged, for a stage whose merge it never reflects (*declared-dwell*)
- `src/cordage/checkpoint_gate.py` - the module default, which the document only coincidentally matches (*baseline-dwell*)
- `history/branches/checkpoint-01.md` - the accepted merge the document was never updated to show (*branch-record*)
- `docs/envelope.md` - the document, unchanged, for a stage whose merge it never reflects (*declared-dwell*)
- `src/cordage/envelope_view.py` - the module default, which the document only coincidentally matches (*baseline-dwell*)
- `history/branches/envelope-01.md` - the accepted merge the document was never updated to show (*branch-record*)

## 7. Budget

Not a mode-8 task. The reading is long and the writing is three lines; the reference answer is
89 characters.

## 8. Near-miss table

Generated by `selfcheck.py` from this spec's own reference and near-miss answers. Every
perturbation of a correct answer the prompt does not specify - no trailing newline, two trailing
newlines, CRLF, a leading blank line, trailing spaces - leaves the verdict `correct`; the key
**order** is stated in the prompt, so a swapped-order file fails, and it does, as
`confidently_wrong`. No perturbation is adjudicated as a legitimate failure for this task.

## Derivability

Every value the reference asserts is measured from `seed/` at build time by
`specs/m01_main_glm.py`: the stale set by replaying each stage's branch records against its
module's `EFFECTIVE_DWELL_S` and its onboarding date, the net change by summing documented-minus-module
for those stages, and the authority by reading the release note's own identifier. Nothing is
typed twice; `facts()` asserts the raw-stale count and the final set against the plan's own
intent before either is written anywhere.
