# Sonnet difficulty probe (tasks-v4: 52, 55-57, 59-61)

Takers: Claude Code subagents on Sonnet, 3 trials per task, 21 runs, run in parallel batches
of 6 (two tasks at a time). Zero OpenRouter spend, no pi and no ollama runs.

Layout and grading replicate `results/haiku-v4/` exactly. Each sandbox
`results/sonnet-v4/<task>/t<k>/` gets the task's `seed/` contents copied flat plus `prompt.md`
copied in as `TASK.md`. Grading is identical to `pibench.run_pi`: hidden `test.py` copied in as
`_hidden_test.py`, `python _hidden_test.py` with cwd=sandbox, `PYTHONUTF8=1
PYTHONIOENCODING=utf-8`, 60 s timeout with process-tree kill (`pibench.run_tree`); pass iff
rc==0 and "PASS" in stdout; score = last `SCORE n/m` as a fraction; grader timeout = fail,
score 0. Runner: `results/sonnet-v4/run.py` (`setup` / `grade` / `timeout`), grades in
`grades.json` keyed `<task>/t<k>`.

fp8 columns are qwen/qwen3.8-27b at medium reasoning, from existing files only. The 3-trial
parity run `results/v4-ref-medium-1800.json` (1800 s cap) is still in flight and has landed
only **52_reengine, 2 of 3 trials** so far; that is what the fp8 column shows, labelled below.
The older `results/v4-ref-medium.json` (1500 s) has a single 52_reengine trial (0/1, 0.677) and
otherwise covers only 40-47 and 53/54 — so 55, 56, 57, 59, 60 and 61 have **no fp8 runs at all**.

| task | Sonnet pass k/3 | Sonnet mean SCORE | Haiku pass | Haiku mean | fp8 medium pass | fp8 medium mean |
|---|---|---|---|---|---|---|
| 52_reengine | 2/3 | 0.914 | 0/3 | 0.677 | 1/2 (1800 s, partial) | 0.710 |
| 55_minilang | 0/3 | 0.968 | 0/3 | 0.796 | n/a | n/a |
| 56_tmpl | 0/3 | 0.920 | 0/3 | 0.460 | n/a | n/a |
| 57_stateful | 3/3 | 1.000 | 0/3 | 0.308 | n/a | n/a |
| 59_uri | 3/3 | 1.000 | 1/3 | 0.889 | n/a | n/a |
| 60_numlit | 2/3 | 0.978 | 0/3 | 0.611 | n/a | n/a |
| 61_codecs | 3/3 | 1.000 | 0/3 | 0.867 | n/a | n/a |

Sonnet overall: **13/21 pass (62%), mean SCORE 0.968**. Haiku on the same seven tasks:
1/21 pass (5%), mean SCORE 0.658. No Sonnet run hit the 60 s grader timeout or the 25 min
taker limit; grader walls were 0.1-13.9 s.

## Sonnet failure modes (from grader tails)

- **52_reengine** (2/3, 0.914): t1 is the only heavy failure in the whole probe — its engine
  raises `PatternError` on valid patterns across five randomised differential buckets
  (anchors/boundaries, groups/alternation, bounded quantifiers, non-greedy quantifiers, deeper
  nesting), i.e. an over-strict parser rejecting patterns it should compile. t2 and t3 are
  clean 31/31.
- **55_minilang** (0/3, 0.968): all three runs fail exactly one check, the same one —
  `parse-time errors beat runtime errors, in the stated order`. Error *precedence* between the
  two phases, stated only in prose. Everything else (30/31) is right in every trial.
- **56_tmpl** (0/3, 0.920): all three fail `randomised differential, mutated/malformed
  templates (bucket 1)`; t2 and t3 additionally fail `filters on odd inputs:
  upper/lower/trim/length/first` and `set scoping: leaks out of if, not out of for`. Again the
  losses are malformed-input kinds/positions and a scoping rule that no example demonstrates.
- **57_stateful** (3/3): clean. This was Haiku's worst task (0.308).
- **59_uri** (3/3): clean.
- **60_numlit** (2/3, 0.978): t1 misses `canonical text for integers, radix integers and floats`
  and the `scan differential: mutated literals, exact kind and pos`; t2 and t3 are 30/30.
- **61_codecs** (3/3): clean.

The residual failure surface is narrow and of one kind: exact error *precedence*, error
*kinds/offsets* on mutated input, and canonical text forms — the same prose-only parts of the
spec that sink Haiku, except Sonnet loses one or two checks there instead of ten. The single
structural failure (52_reengine/t1) is an over-strict pattern parser, not a partial
implementation. Nothing hung, nothing tripped a ban check, and no partial-credit collapse.

## Verdict

Sonnet sits far above Haiku (62% vs 5% pass, 0.968 vs 0.658 mean on the same seven tasks) and
at or above the 27B fp8 on the only task with fp8 coverage (52_reengine: 2/3 and 0.914 vs
1/2 and 0.710, the fp8 miss being a 1800 s timeout) — these v4 tasks discriminate Haiku from
fp8 but barely discriminate Sonnet, which is now scoring in the last-two-checks regime.

Saturating on Sonnet (3/3 or mean > 0.95): **57_stateful, 59_uri, 61_codecs** (3/3, 1.000),
**60_numlit** (2/3 but 0.978), and **55_minilang** (0/3 but 0.968 — saturated by score, held off
a pass by a single precedence check). Still discriminating: **52_reengine** (0.914) and
**56_tmpl** (0.920), and only barely.
