# v4 authoring report (final, 2026-09-03)

Target: `qwen/qwen3.8-27b` via OpenRouter, Parasail pinned (ZDR, fp8), MEDIUM thinking, agent dir
`results/pi-agent-v4` (sort=price + Parasail pin), `--timeout 1500`, `--tasks-dir tasks-v4`,
tag `v4-ref-medium`. Grading: hidden `test.py` copied in as `_hidden_test.py` after the agent exits;
pass iff rc 0 and `PASS` in stdout; partial credit from a `SCORE n/m` line.

Keep filter (revised brief rule 6): mean SCORE over the smoke trials (no SCORE line = 0, PASS = 1.0);
keep `0 < mean <= 0.85`; reject `mean == 0` (broken/unfair) and `mean > 0.85` (saturated).

## KEEPERS

| task | domain | fp8 trials | fp8 mean SCORE | Haiku mean | why it discriminates |
|---|---|---|---|---|---|
| 52_reengine | regex engine from scratch, `re`/`eval`/`exec` banned | 1 | **0.677** | 0.677 (0/3) | 12 of 31 buckets are strictness: 10-value `.kind` error table with a stated validation order, `$` before trailing newline, `\b` as backspace inside a class but `\B` an error there, `{,3}` a real repeat while `a{x}` is a literal brace, last-iteration-wins group retention, empty-iteration guard. fp8 also hit the 1500 s wall. |

**One confirmed keeper.** The target of 8-10 was not reached — see "Why this stopped short".

## Validated but NOT SMOKED (no fp8 evidence; budget exhausted)

Haiku probe (`results/haiku-v4/grades.json`) shows all six discriminate on a weaker model, so they are
the strongest remaining candidates, but no fp8 number exists for them.

| task | domain | Haiku passes | Haiku mean SCORE |
|---|---|---|---|
| 57_stateful | protocol replay state machine | 0/3 | 0.308 |
| 56_tmpl | template engine, whitespace control | 0/3 | 0.460 |
| 60_numlit | strict numeric literal scan/format | 0/3 | 0.611 |
| 55_minilang | expression-language interpreter | 0/3 | 0.796 |
| 61_codecs | strict base64/base32/QP codecs | 0/3 | 0.867 |
| 59_uri | RFC 3986 parse/normalize/resolve | 1/3 | 0.889 |

## REJECTS (moved to `tasks-v4-rejected/`, all kept on disk)

| task | domain | fp8 passes | fp8 mean SCORE | Haiku mean | reason |
|---|---|---|---|---|---|
| 40_shquote | shell word splitting/quoting | 3/3 | 1.000 | - | saturated |
| 41_csvdialect | CSV dialect quoting | 3/3 | 1.000 | - | saturated |
| 42_pathnorm | path normalization/relpath | 3/3 | 1.000 | - | saturated |
| 43_wildmatch | glob/brace/bracket matcher | 1/3 | 0.931 | - | saturated: failed 2 of 3 trials yet scored 0.93, because the rubric spread credit over behaviour the model self-tests successfully |
| 44_money | decimal/rounding/money | 3/3 | 1.000 | - | saturated |
| 45_datecalc | date/business-day/ISO week | 3/3 | 1.000 | - | saturated |
| 46_vercmp | version compare + constraints | 2/3 | 0.952 | - | saturated |
| 47_nullagg | NULL-tolerant sort/aggregate | 2/2 | 1.000 | - | saturated (halted at 2 trials on budget) |
| 48_editor | editor undo/redo + selection | not smoked | - | - | round-1 design; smoke cancelled on budget, same self-testable pattern as 40-42 |
| 49_ranges | open/closed interval algebra | not smoked | - | - | same |
| 50_wrap | unicode width / wrapping | not smoked | - | - | same |
| 51_jsonesc | JSON escaping / number formatting | not smoked | - | - | same |
| 53_gitattr | gitattributes resolver + macros | 0/1 | 0.900 | 0.800 (0/3) | above the 0.85 band on one trial. UNRESOLVED: 0.90 sits in the (0, 0.95) second-trial window, so it was owed a second trial that the budget cap prevented. Best re-test candidate. |
| 54_sedlite | sed-like line editor | 0/1 | 0.967 | 0.611 (0/3) | above the band; outside the second-trial window |
| 58_bencode | canonical bencode codec | not smoked | - | 1.000 (3/3) | saturated on the Haiku probe, so skipped on fp8 |

## Per-run detail for the strictness stage

| task | trial | SCORE | wall s | in tok | out tok | timed out | USD (ub) |
|---|---|---|---|---|---|---|---|
| 52_reengine | 0 | 0.6774 | 1500.2 | 1,367,824 | 68,611 | **yes** | 0.493 |
| 53_gitattr | 0 | 0.9000 | 822.2 | 2,316,642 | 60,389 | no | 0.712 |
| 54_sedlite | 0 | 0.9667 | 839.0 | 4,505,841 | 60,278 | no | 1.259 |

## OR cost ledger (Parasail: USD 0.25/M input, 2.20/M output)

`in_tokens` sums `usage.input + usage.cacheRead`, so cached prefill is priced at full input rate.
These are UPPER BOUNDS; real billed spend is lower. Input dominates every line.

| stage | runs | in tok | out tok | USD (upper bound) |
|---|---|---|---|---|
| round-1 smoke (40-47, 3 trials, halted mid-47) | 23 | 13,831,896 | 498,772 | 4.555 |
| strictness stage (52, 53, 54, 1 trial) | 3 | 8,190,307 | 189,278 | 2.464 |
| **total v4** | **26** | **22,022,203** | **688,050** | **7.019** |

The strictness stage was stopped at USD 2.464 of its USD 3.0 cap: mean cost was 0.82/run and the
next run would have overshot. 55, 56, 57, 59, 60 and 61 were never reached.

## Why round 1 saturated, and what fixed it

At MEDIUM thinking the model is not limited by spec difficulty. It writes its own tests and iterates
until they pass, so any behaviour a competent developer would think to test gets fixed. Precise, fair,
rule-dense specs are not enough — 40-47 were all of those and 7 of 8 scored >= 0.93.

The v3 campaign's finding, confirmed here: the only real failures are (a) un-self-testable strictness
(rejecting inputs the spec forbids, exact error precedence and error class, sign/rounding on ties,
NULL semantics, exact canonical output form) and (b) bans the model violates.

Rounds 2 and 3 were re-authored to that mandate: 5-10 explicit strictness requirements per task, each
its own SCORE bucket, with strictness / error-precedence / canonical-form buckets weighted at a third
to a half of TOTAL. Each author verified a "correct on valid input, lax on invalid input" mutant lands
at 0.53-0.63 rather than 0.95 — the property round 1 lacked. That change is what produced the only
keeper and the sub-0.85 Haiku spread across all ten strictness tasks.

## Why this stopped short of 8 keepers

Budget, not authoring. 22 tasks were written and validated; 15 were smoked or probed on fp8. The
account had ~USD 5 of credit left when the strictness stage began, and these tasks cost 0.49-1.26 per
run (long agentic loops with large prompts), roughly 4x the round-1 average. Nine tasks at even one
trial each was not affordable. Six validated, Haiku-discriminating candidates are ready and unsmoked;
resuming needs roughly USD 5-6 for one trial each plus second trials for those in band.

## Caveats

- `results/v4-ref-medium.json` contains 26 runs and DOES include rejects (40-47 at 3 trials, 53 and 54
  at 1 trial). It was never hand-edited. The single keeper 52_reengine has ONE trial, not three.
- Trial counts are not uniform (3 for 40-47, 1 for 52-54) because of the staged budget instructions.
- `--timeout 1500` throughout. It bound on exactly one run: 52_reengine timed out at 1500 s, so its
  0.677 reflects a truncated agent run. That makes the keeper's score partly a time artefact and it
  should be re-measured at 1800 s before the number is used to rank quants.
- 48-51 and 58 are rejected without fp8 evidence (58 on Haiku evidence, 48-51 by pattern).

## Suite integrity

`python selftest2.py tasks-v4` is clean (7 tasks: ref PASS, seed FAIL). `python selftest2.py
tasks-v4-rejected` is also clean (15 tasks), so nothing was broken by the moves. Every hidden test:
oracle inlined in `test.py` (never imports `ref/`), fixed seed, hundreds to tens of thousands of
bounded randomized differential cases, a `threading.Timer(45 s)` watchdog printing a partial SCORE
then `os._exit(1)` rather than hanging, and a graceful `SCORE 0/TOTAL` + FAIL on a missing module.
No `signal.alarm`, no third-party imports, no stray files.

## POST-HOC ORACLE AUDIT (found after the smoke; read this before using the suite)

Brief rule 1 requires each hidden test's oracle to be stdlib or an INDEPENDENT reference, so that the
randomized differential can actually catch a bug in the candidate. I checked every remaining task by
un-renaming the oracle symbols in `test.py` and measuring verbatim overlap with its own `ref/`:

| task | ref code lines | verbatim in test.py | verdict |
|---|---|---|---|
| 52_reengine | 265 | 5 (2%) | sound — oracle is stdlib `re` |
| 55_minilang | 378 | 32 (8%) | sound |
| 57_stateful | 176 | 18 (10%) | sound |
| 56_tmpl | 469 | 105 (22%) | sound (convergent structure) |
| 60_numlit | 213 | 70 (33%) | acceptable — formatter oracle is `decimal`-based |
| 61_codecs | 137 | 70 (51%) | NEEDS REVIEW |
| 59_uri | 219 | 142 (65%) | **BROKEN — oracle is a renamed copy of ref** |

**59_uri is not brief-compliant.** Its task dir still contains the generator that did it:
`_mkoracle.py` reads `ref/uriref.py`, rewrites every symbol to an `_o_*` name, and that output is the
"independent reference" inlined in `test.py`. Oracle and ref are therefore the same implementation, so
the differential is vacuous: any bug in ref is mirrored in the oracle and can never be detected. The
task still functions as a spec-conformance test (its Haiku probe found real failures at mean 0.889),
but its differential guarantee is void. It must NOT be used to rank quants until the oracle is
rewritten from the prompt alone. It was never smoked on fp8, so no result in `v4-ref-medium.json` is
affected. `_mkoracle.py`, `_oracle.txt` and `_tpl.py` are left in place as evidence for the rewrite;
they are never copied into a candidate sandbox (pibench copies only `seed/`).

**61_codecs at 51% is lower risk but unverified.** There is no generator script, the overlap is
largely short generic lines plus spec-fixed constant tables and the public signatures (which must
match), and the author cross-checked the codec paths against stdlib `base64` during authoring. Treat
it as needs-review rather than broken.

**The keeper is unaffected**: 52_reengine's oracle is stdlib `re` at 2% overlap.

Also removed after the last author writes: a stray `ref/__pycache__` in 59_uri. `selftest2 tasks-v4`
re-verified clean afterwards (7 tasks).
