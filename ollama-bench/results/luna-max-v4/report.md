# luna-max-v4 campaign report

Taker: Codex CLI, model `gpt-5.6-luna`, reasoning effort **max**. Tasks: 56_tmpl, 57_stateful,
55_minilang (three longest prompts in tasks-v4), 2 trials each. Driver `_driver.sh` finished all
six runs on its own; no relaunch was needed.

## a. Per-run table (from `runs.json` and `grades.json`)

| Task        | Trial | Pass  | Score  | Wall s | Total tokens | Nested-call refusals |
|-------------|-------|-------|--------|--------|--------------|----------------------|
| 56_tmpl     | 1     | FAIL  | 0.7931 | 1800.0 | (none — timed out, rc=124) | 0 |
| 56_tmpl     | 2     | PASS  | 1.0000 | 1478.0 | 278,949      | 2* |
| 57_stateful | 1     | PASS  | 1.0000 | 513.0  | 102,819      | 1 |
| 57_stateful | 2     | PASS  | 1.0000 | 533.0  | 83,300       | 1 |
| 55_minilang | 1     | PASS  | 1.0000 | 1171.0 | 167,219      | 1 |
| 55_minilang | 2     | FAIL  | 0.9677 | 711.0  | 102,088      | 1 |

\* run.py counted 2, but one match is a false positive — see section g.2. The real count is 1.

Codex reported no input/output/reasoning split on any run (the "tokens used" line is a bare total
only), so no per-category token figures exist.

## b. Per-task results

| Task        | Pass rate | Mean score |
|-------------|-----------|------------|
| 56_tmpl     | 1/2       | 0.897      |
| 57_stateful | 2/2       | 1.000      |
| 55_minilang | 1/2       | 0.984      |

## c. Tokens across the six runs

- Total: **734,375** tokens (sum of the five runs that reported; 56_tmpl/t1 timed out before
  Codex printed its usage line, so it contributes 0 measurable tokens).
- Mean over all six runs: **122,396** tokens. Mean over the five reporting runs: 146,875.

## d. Comparison on the same three tasks

| Task        | This campaign (luna, **max**, 2 trials) | codex-luna-v4 (luna, medium, 3 trials) | sonnet-v4 (3 trials) | haiku-v4 (3 trials) | v4-ref-medium-1800 (qwen3.8-27b local fp8, 3 trials) |
|-------------|----------------|----------------|-----------|-----------|------------|
| 56_tmpl     | 1/2, mean 0.897 | **not run** — cell missing | 0/3, mean 0.920 | 0/3, mean 0.460 | 0/3, mean 0.816 |
| 57_stateful | 2/2, mean 1.000 | 1/3, mean 0.808 | 3/3, mean 1.000 | 0/3, mean 0.308 | 2/3, mean 0.885 |
| 55_minilang | 1/2, mean 0.984 | 1/3, mean 0.946 | 0/3, mean 0.968 | 0/3, mean 0.796 | 2/3, mean 0.989 |

All comparison figures were read from the corresponding files, not taken on trust:
`../codex-luna-v4/grades.json`, `../sonnet-v4/grades.json`, `../haiku-v4/grades.json`, and
`../v4-ref-medium-1800.json` (key `qwen/qwen3.8-27b`, `runs` list filtered to the three tasks).
The medium-effort luna figures I measured (1/3 & 0.946 for 55_minilang, 1/3 & 0.808 for
57_stateful) match the values quoted in the campaign brief.

Missing cells: 56_tmpl was never run in codex-luna-v4. The local fp8 reference has no token
comparison basis here (its usage is in/out split, not Codex's total line); its per-task mean
scores above are computed from its own `runs` entries. This campaign's 56_tmpl/t1 token figure
is missing (timeout).

Headline: effort max turned 57_stateful from 1/3 to 2/2 and kept 55_minilang's scores high, but
56_tmpl/t1 burned the full 1800 s wall clock and still failed grading — the only score below
1.0 besides a 30/31 slip on 55_minilang/t2 (failed "parse-time errors beat runtime errors", the
same single test the medium-effort runs also missed).

## e. Nesting guard

Background: on 2026-09-02 Codex takers discovered the deployed codex-run skill and called it
recursively, up to 11 nested calls in one run. Since commit 3ce8f44 the codex-run and pi-run
wrappers export `AGENT_RUN_DEPTH` and refuse nested calls with "refusing nested run" on stderr,
exit 2.

Measured across the six `_codex_stderr.log` files:

- run.py collect counted **6** refusals in total (0 + 2 + 1 + 1 + 1 + 1). Grep on the raw logs
  shows **5 real refusal events** and **1 false positive**: in 56_tmpl/t2 the taker read
  `run.py`'s own source, which contains the literal string `refusing nested run`, and the
  substring counter matches it. The real events, one per offending run, are:
  - 56_tmpl/t2: `pi-run: refusing nested run (AGENT_RUN_DEPTH=1)`
  - 57_stateful/t1: `pi-run: refusing nested run (AGENT_RUN_DEPTH=1)`
  - 57_stateful/t2: `codex-run: refusing nested run (AGENT_RUN_DEPTH=1)`
  - 55_minilang/t1: `pi-run: refusing nested run (AGENT_RUN_DEPTH=1)`
  - 55_minilang/t2: `pi-run: refusing nested run (AGENT_RUN_DEPTH=1)`
  Five of six runs found the deployed skill and tried to call it (four targeted pi-run, one
  codex-run); the guard refused every attempt. Only 56_tmpl/t1 never tried — it was busy until
  the wall-clock kill.
- "tokens used" blocks: exactly **1** in each of the five completed logs
  (278949, 102819, 83300, 167219, 102088) and **0** in the timed-out log 56_tmpl/t1. A naive
  substring grep hits wrapper/source text inside the logs, but run.py's block parser (exact bare
  line `tokens used` followed by a numeric-only line) is immune to that. Exactly one real block
  per completed log means **no nested Codex run actually executed anywhere** — the guard held.

## f. Overseer note

This campaign needed two overseer pi runs. The first one started the campaign correctly and then
ended its turn while polling, which killed that pi run; the driver kept running detached and was
unaffected. This report is written by the resume overseer.

## g. Problems and anomalies

1. **56_tmpl/t1 timed out** at the 1800 s wall clock (rc=124, driver killed it mid-task). Its
   stderr ends in a patch hunk with no Codex usage line, so its token count is genuinely missing,
   and its score 0.7931 comes from grading the partial work (failed 4 of 5 differential buckets).
   No other run misbehaved.
2. **run.py's `nested_refusals` for 56_tmpl/t2 is off by one** (2 counted, 1 real): the substring
   counter also matches the literal `refusing nested run` inside run.py's own source, which the
   taker had read into its log. All other counts are exact. A stricter counter (e.g. anchor on
   `pi-run:`/`codex-run:` prefixes) would fix this; I did not modify run.py, per instructions.
3. Nothing else failed. The driver was never relaunched, no usage-window exhaustion occurred, and
   no run needed the fallback paths.
