# v4 authoring brief (2026-09-03 00:55)

Goal: a task suite where OR qwen/qwen3.8-27b (fp8, Parasail ZDR) at MEDIUM thinking passes 40-70% of trials,
or earns partial credit (SCORE n/m), so that local quants (Q2_K_L, Q3_K_S, Q3_K_M) can be ranked against it.
Three prior rounds ("harder in general") saturated: v1 22/22, v3 round 1 46/48, v3 round 2 8/8 so far.

## What actually fails (from tasks-v2, OR low and medium, 5 trials)
| task | low | medium | how it fails |
|---|---|---|---|
| 12_regex | 4/5 | 3/5 | randomized differential vs `re` on nested quantifiers/alternation, e.g. `a(b|(a*[^a]+)?)+` vs `a`; one infinite loop |
| 15_diff | 2/5 | 3/5 | violates "no difflib" constraint (uses forbidden module) |
| 17_interp | 1/2 | 3/5 | randomized higher-order lambda/let cases: `(fn f -> 8) (let x = fn g -> fn f -> f in fn x -> x)` returns err |
| 21_query | 1/3 | 4/4 | NULL handling in group-by/aggregates (None ordering, count(*)) |
| 23_glob | 1/3 | 0/3 | bracket-class edge cases: `[z-a]`, escaped `\]`, `[!...]`, `**` vs `?*` on paths |
| 24_fixed | 4/5 | 3/5 | decimal quantize rounding modes / sign of results at 0 (`-0.6`->`-1` vs `0`, truncation vs half-up) |
| 25_undo | 4/5 | 5/5 | randomized undo/redo/move sequences on an editor buffer: cursor and text after undo |

Pattern: the model writes plausible code that passes the visible examples and fails a RANDOMIZED DIFFERENTIAL
hidden test against an oracle (stdlib `re`, `decimal`, `fnmatch`, a reference interpreter, a naive simulator),
mostly on semantic edge cases (empty matches, nesting, escaping, NULL/sign/rounding corner cases, state after
compound operations). "Harder" algorithmic tasks do NOT fail: it solves VMs, parsers, schedulers fine.

## Design rules for v4 tasks
1. Every hidden test.py is a randomized differential test with a fixed seed against an oracle, hundreds of cases,
   PLUS partial credit: print `SCORE passed/total` and `PASS` only if all pass. The oracle must be stdlib or a
   <60-line reference in ref/ (never shipped to the model).
2. Visible examples in the prompt/seed are few (3-6) and do not cover the edge cases; the spec states the semantics
   precisely enough that the edge cases are derivable (the test must be fair: the spec decides every case).
3. Target domains with dense semantic corner cases: regex/glob/pattern engines, decimal/rounding/money math,
   date/time arithmetic (month ends, leap days, DST-free), string escaping/quoting (CSV, shell-like, JSON edge
   cases), NULL-tolerant sorting/aggregation, text-editor/undo state machines, interval/range algebra, versioned
   comparisons, unicode-aware width/wrapping, path normalization.
4. Spec-constraint tasks are fine (e.g. "do not import difflib/re/fnmatch"), enforced in the hidden test.
5. Must run under `python selftest2.py tasks-v4` (ref passes hidden test, seed fails it). Task dir layout identical
   to tasks-v2/tasks-v3 (prompt.md, seed/, ref/, test.py). Hidden test must finish in <60 s and never loop forever
   on a bad solution (use per-case timeouts or bounded inputs; the harness kills the tree after 60 s).
6. Keep filter (REVISED 01:35 after pi audit; PASS implies SCORE 1.0, so "3/3 with mean SCORE<0.9" was unreachable):
   compute mean SCORE over the 3 fp8-medium smoke trials (a trial with no SCORE line scores 0; PASS scores 1.0).
   keep iff 0.25 <= mean SCORE <= 0.85; ALSO keep 0 < mean SCORE < 0.25, flagged "hard, quant-discriminating";
   reject mean SCORE == 0 (broken or unfair test, fix or drop) and mean SCORE > 0.85 (saturated). Stop at 10 keepers.

## 7. Haiku smoke gate (owner rule, 2026-09-03 09:40) — REQUIRED before any OpenRouter run
Every new or revised v4 candidate is first probed with 3 Claude Code Haiku subagents (Agent tool,
model "haiku"), the same brief a pi run gets (prompt.md + seed copied into a sandbox as TASK.md, bans
stated, no hidden tests, no ref/), graded with the task's own hidden test.py exactly as pibench does
(tree-killed 60 s grader, pass iff rc 0 and PASS, SCORE parsed). The runner and layout are in
results/haiku-v4/ (grades.json keyed "<task>/t<k>", report.md); reuse them.
- Haiku passes 3/3, or mean SCORE > 0.95: the task is probably too easy; do NOT spend cloud money on it.
  Revise it (more un-self-testable strictness, see rule 6 and the v3 finding) and re-probe.
- Haiku fails at least one taker: the task may proceed to the fp8 smoke on OpenRouter (rule 6 keep filter).
- Record the Haiku k/3 and mean SCORE next to the fp8 numbers in report.md for every task.
Rationale: Haiku subagents cost no API spend; in the 2026-09-03 probe Haiku failed exactly the tasks fp8
also dropped, far more often, with partial-credit spread, so it is a usable proxy for a weaker model.

## 8. Sonnet feasibility check (owner rule, 2026-09-03 10:50) — pairs with the Haiku gate
Haiku shows a task is hard enough; Sonnet shows it is still possible for a smaller but capable model.
After a candidate clears the Haiku gate, probe it with 3 Claude Code Sonnet subagents (model "sonnet"),
same sandbox brief and grading as section 7; runner and layout in results/sonnet-v4/ (run.py, grades.json
keyed "<task>/t<k>", report.md), batches of at most 6 takers at a time on this host.
- Sonnet passes at least one taker, or mean SCORE >= 0.85: the task is achievable; proceed to the fp8 smoke.
- Sonnet 0/3 with mean SCORE < 0.85: suspect the task (ambiguous prose, over-strict or buggy grader) before
  blaming the model; review the failing checks and revise, or justify in report.md why it should stay.
- A task Sonnet saturates (3/3, 1.000) is fine for the local ladder; it only stops discriminating among
  frontier models, which is not v4's job.
- Record Haiku k/3 and mean, Sonnet k/3 and mean, and fp8 k/3 and mean side by side in report.md.
Reference numbers from the 2026-09-03 probes on the seven keepers: Haiku 1/21 mean 0.658; Sonnet 13/21
mean 0.968; both cost no API spend.
