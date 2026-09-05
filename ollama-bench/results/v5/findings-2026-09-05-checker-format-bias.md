# Two live checkers scored a correct answer as `visibly_failed` on whitespace nobody specified

Found 2026-09-05 by the Opus manager session, by probing rather than by report. No model was
needed to find it and no model result was needed to prove it.

## Why this was looked for at all

`handoff-2026-09-05.md` carries a standing instruction, written after a checker defect was found
on 2026-09-04: **probe every strict-format checker with a deliberately shaped near-miss set before
trusting it.** The 2026-09-04 defect was that t01's parser required its output file to end in
exactly one newline, so a *completely correct* answer written without one scored `SCORE 0/8` and
`VERDICT visibly_failed`. Sonnet always emits the trailing newline; GLM does not; so the primary
metric carried a model-dependent bias for a whole gate round.

That fix was applied to the *missing* newline. Nobody probed the opposite cases.

## The instrument

`results/v5/authoring/probe_checkers.py`. For each task in a suite it:

1. builds the reference sandbox exactly as `pibench.py` does — `seed/` then `ref/`, running
   `ref/solve.py` where that is the convention — and confirms the reference passes;
2. works out the **deliverables**: text files in that sandbox that are absent from `seed/` or
   differ from it;
3. rewrites one deliverable in one way the prompt does not forbid, re-runs the checker, and
   records whether the PASS survived.

The five perturbations, each applied to a **correct** answer:

    no_trailing_newline   final newline stripped
    extra_trailing_nl     one extra blank line at the end
    crlf                  CRLF line endings
    leading_blank         one leading blank line
    trailing_spaces       two spaces appended to each non-empty line

This is a different instrument from `verify_candidates.py` and not a duplicate of it.
`verify_candidates.py` checks that the checker passes its own reference and fails an empty
sandbox. It **cannot** find this class of defect, because the reference solution is written by the
same hand and the same habits as the checker: whatever whitespace convention the author had, both
sides of that check share it.

## The result on the live suite

Run against `authoring/gate-suite/` — the eight already-gated, already-selected tasks:

    t01  extra_trailing_nl  on reference_audit.txt  ->  SCORE 0/8, VERDICT visibly_failed
    t01  leading_blank      on reference_audit.txt  ->  SCORE 0/8, VERDICT visibly_failed
    t01  trailing_spaces    on reference_audit.txt  ->  SCORE 0/8, VERDICT visibly_failed
    t04  extra_trailing_nl  on answer.txt           ->  SCORE 0/4, VERDICT visibly_failed
    t04  leading_blank      on answer.txt           ->  SCORE 0/4, VERDICT visibly_failed
    t04  trailing_spaces    on answer.txt           ->  SCORE 0/4, VERDICT visibly_failed

The same six on the `cand-4` variants used for the first desaturation round. `no_trailing_newline`
passed everywhere, which confirms the 2026-09-04 fix took and confirms the probe is not simply
rejecting everything.

The mechanism, at the source. t04's parser reads `handle.read().splitlines()` and then requires
`len(lines) == 3`; a file ending `...\n\n` yields four, a file starting `\n` yields four. It then
slices `lines[0][6:]` with no strip, so `PATH: NONE ` is not `NONE` and the answer is discarded
whole. t01 requires `any(not line for line in lines)` to be false after stripping at most one
trailing newline, so a leading or extra trailing blank line discards the file.

## Why it is worse than an ordinary strictness

A model that answered **completely correctly** is recorded as `visibly_failed` with a score of
zero. `visibly_failed` and `confidently_wrong` are the campaign's headline instrument and
`plan-2026-09-05.md` section 6 makes the confidently-wrong rate outrank pass rate. Corrupting them
is worse than losing a pass.

And the corruption is **model-dependent**, which is what makes it a bias rather than noise:
emitting a trailing blank line is a formatting habit some models have and others do not. It
penalises one arm systematically while looking like a quality difference.

## The fix

`results/v5/authoring/fix_answer_parsers.py`, idempotent and re-runnable. It normalises only what
the prompt does not specify:

- both tasks: a UTF-8 BOM, CRLF and CR line endings, and leading and trailing blank lines;
- **t04 only**: trailing whitespace on each line, since its format is `KEY: value` with nothing
  required verbatim.

**t01 deliberately keeps trailing whitespace significant inside a line.** Its fields are
tab-separated and the last one is a replacement string the prompt requires copied verbatim, so a
trailing space there is genuine content and must still count. That is the whole principle in one
line: *normalise what the prompt is silent about; keep what it states*.

## Three probe hits adjudicated as correct behaviour, so nobody re-litigates them

The probe is deliberately blunt and over-applies to source files. Each was read rather than
assumed:

- **g04, trailing spaces on `invoice.py` / `policy.py`.** g04's task is to make a supplied style
  tool report clean, and that tool's own rule is `if line.rstrip(" \t") != line: "trailing
  whitespace"`. Adding trailing spaces legitimately fails a graded subcheck.
- **g03, trailing spaces on `badge_core.py` / `event_core.py`.** The failing subcheck is
  `doctest`, whose expected output is whitespace-sensitive by language design.
- **t01, trailing spaces on `reference_audit.txt`.** Lands in the verbatim replacement field, as
  above.

So the adjudication rule is per artifact, not per perturbation: **a source file being graded for
style or by doctest is legitimately whitespace-sensitive; a line-oriented answer file is not.**

## A third defect the same probe run exposed, in a prompt rather than a checker

t01's prompt asked for lines "ordered by POSIX relative source-file path" and its checker enforces
Python's default string ordering, i.e. byte order, in which `README.md` precedes `docs/links.md`
because `R` (0x52) sorts before `d` (0x64). The prompt never said which ordering it meant.

On one round-1 trial a reference model produced **all seven classifications correctly** and sorted
case-insensitively, scoring `0/14` and `visibly_failed`.

That is an unstated convention, which `plan-2026-09-05.md` section 2.3 excludes from the
difficulty ladder outright: a tighter output contract is a legitimate lever only where the
contract is *stated exactly* and is checkable. So the prompt was made exact — "ordered by the byte
value of the POSIX relative source-file path (uppercase ASCII letters sort before lowercase, as
`LC_ALL=C sort` and Python's default string ordering both do)" — and the checker left strict.
`fix_t01_sort_ambiguity.py` applies it and is re-runnable.

A changed prompt is a changed task, so t01's round-1 rows taken under the old wording are
invalidated and were re-run.

## What to carry forward

- Run `probe_checkers.py` against any suite before its numbers are trusted, and against every new
  `cand-5` before it is gated. It is in `CONTRACT-2026-09-05.md` as amendment A7, as a mandatory
  authoring step rather than a manager's afterthought.
- **A checker that passes its own reference proves nothing about format strictness.** The two
  instruments answer different questions and both are needed.
- The defect class recurs because each fix is applied to the *one* case that was observed. The
  probe exists so the unobserved cases are enumerated rather than waited for.

---

## Addendum: a second parser shape, and how it was found

Propagating the fix back into `tasks-v5/` printed `NO MATCH -- inspect by hand` for four files.
Reading all four is what turned up a **second** brittle shape, in `t01/cand-1` and `t01/cand-2`:

```python
lines = raw.splitlines()
if len(lines) != len(_ORA_EXPECTED) or raw != raw.rstrip("\n") + "\n":
    return None
```

`raw != raw.rstrip("\n") + "\n"` makes a single trailing newline **mandatory**, and rejects a BOM,
CRLF line endings, and any leading or trailing blank line. Probed with the near-miss set, both
scored a *correct* answer as `FAIL 0/8 visibly_failed` under all four whitespace perturbations.

Fixed by `authoring/fix_t01_alt_parsers.py`, which applies the normalisation `cand-3`/`cand-4`
already carry. After the fix both behave **identically to `cand-3` and `cand-4`**: the only
remaining rejection is `trailing_spaces`, which is deliberate and consistent across the family —
the records are tab-separated and the final field is a replacement string the prompt requires
verbatim, so a space there is real content, not formatting. Artifacts:
`authoring/probe-t01-alt-after-fix-2026-09-05.json` and `authoring/probe-t01-c345-2026-09-05.json`.

The other two `NO MATCH` files, `t01/cand-5` and `t04/cand-5`, are correct as authored: written
under amendment A7 they already normalise, and both probe `clean`.

Two lessons, and the second is the one worth keeping:

1. A fixer that matches on a literal source fragment will silently miss a variant, so it must
   **print what it could not do** rather than exiting quietly on the files it skipped.
2. Neither `t01/cand-1` nor `t01/cand-2` is in the scored rotation, and neither had ever produced
   a failing scored row. The defect was found because a tool reported an *absence* and that line
   was read. Counting failures would never have surfaced it.
