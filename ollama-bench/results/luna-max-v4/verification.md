# Verification of the luna-max-v4 campaign

Written by the control session (Claude Code) after the GLM overseer finished. Nothing here is
taken from `report.md`; every figure below was recomputed from the sandboxes and the raw logs.

Method:

* Independent re-grade with `%TEMP%\luna-max-verify\verify.py`. It does **not** import
  `run.py`: it re-derives the six sandboxes from the task/trial layout, copies each hidden test in
  itself as `_vtest.py`, runs it with `subprocess.run` (not `pibench.run_tree`), and parses SCORE
  with its own anchored regex. A bug in `run.py`, or a doctored `grades.json`, would show up as a
  mismatch.
* Token re-extraction with the same script's own parser, plus a by-hand `grep -n -A1 '^tokens used'`
  on two logs (`57_stateful/t2`, `55_minilang/t1`).
* `sha256sum -c results/v4-test-hashes.txt --quiet` before the campaign and after grading.
* mtime sweep over `results/luna-max-v4` and the rest of `ollama-bench`.

## Task-file integrity

`sha256sum -c results/v4-test-hashes.txt --quiet` passed at 13:44 (before launch) and again after
grading. `tasks-v4` was not touched. `run.py` (13:42) and `_driver.sh` (13:43) both predate the
first overseer launch at 13:44, so neither the overseer nor any taker modified them.

## Independent re-grade

| key | verify.py | grades.json | agree |
|---|---|---|---|
| 56_tmpl/t1 | FAIL 0.7931 | FAIL 0.7931 | yes |
| 56_tmpl/t2 | PASS 1.0 | PASS 1.0 | yes |
| 57_stateful/t1 | PASS 1.0 | PASS 1.0 | yes |
| 57_stateful/t2 | PASS 1.0 | PASS 1.0 | yes |
| 55_minilang/t1 | PASS 1.0 | PASS 1.0 | yes |
| 55_minilang/t2 | FAIL 0.9677 | FAIL 0.9677 | yes |

Six of six agree on pass and on score. Pass rate 4/6; per task 56_tmpl 1/2 (mean 0.8966),
57_stateful 2/2 (1.000), 55_minilang 1/2 (0.9839).

## Token extraction rechecked by hand

`codex-cli` 0.153.0 prints a bare line `tokens used`, then the total with thousands separators,
then `done`. No input/output/reasoning split exists, so `run.py collect`'s optional split fields
are absent from every run - correctly, not by omission.

* `57_stateful/t2/_codex_stderr.log:5316-5317` -> `tokens used` / `83,300`; the only such block in
  the file. runs.json says 83300. Correct.
* `55_minilang/t1/_codex_stderr.log:27455-27456` -> `tokens used` / `167,219`; the only such block.
  runs.json says 167219. Correct.

Every other run matches too: 278,949 (56_tmpl/t2), 102,819 (57_stateful/t1), 102,088
(55_minilang/t2). `56_tmpl/t1` has no block at all - its log ends with
`codex-run: codex timed out after 1800 seconds.`, so the wrapper killed Codex before it printed a
usage line. Its token cost is genuinely unmeasured, not zero.

Totals: **734,375** tokens over the five runs that reported, mean **146,875** over those five and
**122,396** if the timed-out run is counted as zero. Both figures appear in report.md, correctly
labelled.

## Usage window

No log contains the wrapper's real message
`codex-run: the ChatGPT plan usage window is exhausted` (grep count 0 in all six). A naive grep for
"usage window is exhausted" *does* hit all six logs, but only because Codex read
`~/.agents/skills/codex-run/SKILL.md` and echoed that sentence into its transcript. The plan window
was never hit.

## Nesting guard - it fired, and it held

Real refusal events, one per line, ANSI stripped:

| run | line | wrapper refused |
|---|---|---|
| 56_tmpl/t1 | - | none (busy until the 1800 s kill) |
| 56_tmpl/t2 | 733 | pi-run |
| 57_stateful/t1 | 880 | pi-run |
| 57_stateful/t2 | 404 | codex-run |
| 55_minilang/t1 | 862 | pi-run |
| 55_minilang/t2 | 853 | pi-run |

**Five of six takers tried to start a nested subagent within the first few minutes** - four reached
for `pi-run`, one for `codex-run` - and every attempt was refused with
`refusing nested run (AGENT_RUN_DEPTH=1)` and exit 2. Each log has exactly one `tokens used` block,
which is independent proof that no nested Codex process ever ran: in the pre-guard 2026-09-02
campaign the same logs carried up to 5 blocks each. The guard from 3ce8f44 works, and this is the
first campaign where its effect is measured rather than assumed.

Note that the takers now reach for `pi-run` (OpenRouter, per-token) more often than `codex-run`.
The guard covers both, but if it were ever relaxed the spend would land on the OpenRouter account,
not only on the plan window.

## What GLM got right

* Every number in `report.md` reproduces. Pass/score table, per-task rates, the 734,375 / 146,875 /
  122,396 token figures, and all comparison cells (`codex-luna-v4` 57_stateful 1/3 0.8077 and
  55_minilang 1/3 0.9462; sonnet 0.9196 / 1.000 / 0.9677; haiku 0.4598 / 0.3077 / 0.7957; fp8
  qwen3.8-27b 0/3 0.8161, 2/3 0.8846, 2/3 0.9892) recompute exactly from the source files.
* It marked the two genuinely missing cells (56_tmpl in `codex-luna-v4`; the token figure for the
  timed-out run) as missing instead of inventing them.
* It obeyed every hard rule: it did not call `codex-run` or `pi-run` itself, did not modify
  `run.py`, `_driver.sh` or anything outside this directory, ran no writing git command, and did
  not retry or work around the timeout.
* **It found a real bug in my `run.py` that I had not.** `nested_refusals` for 56_tmpl/t2 is 2, but
  only one is a refusal: the taker had read `run.py`'s own source into its log, and line 41631 of
  that log contains the counter's own literal string `'refusing nested run'`. I confirmed this by
  hand (`grep -an`, lines 733 and 41631). GLM diagnosed it precisely, gave the right fix (anchor on
  the `pi-run:` / `codex-run:` prefix), and correctly declined to edit `run.py` because it had been
  told not to. `runs.json` therefore over-counts by one; the true total is 5, not 6.

## What GLM got wrong

Nothing material was found. Two small things:

1. `report.md` says "Driver `_driver.sh` finished all six runs on its own; no relaunch was needed",
   which is true of the driver but reads as if one overseer ran throughout. Section f does state
   the two-run history, so this is a wording overlap, not an error.
2. It described 56_tmpl/t1's failure as "failed 4 of 5 differential buckets" from the grader tail.
   The tail is truncated at 300 characters by `run.py`, so that list is the visible end of a longer
   failure list; the score 0.7931 (23/29) is the reliable figure. Minor over-reading of a truncated
   string.

It did not spot that `results/v4-ref-medium-1800.json` is being written by another live process on
this machine, so its fp8 comparison is against a file that can still change. My re-read agrees with
its numbers, so the comparison is sound as of now.

## Integration-test verdict

**A pi-hosted GLM 5.3 Flash overseer did drive Codex takers end to end, but not in one run.**

What worked: GLM ran `run.py setup`, launched `_driver.sh` detached, polled, ran `collect` and
`grade`, read four comparison files, and wrote a report whose every number verifies. Cross-harness
control - pi/OpenRouter driving codex-cli/ChatGPT-plan - is real, and the quality of the audit was
better than the brief required.

What failed: **the first overseer run died at 1490 s because pi's print mode ends the run the moment
the model emits a message with no tool call**, and GLM, while polling, wrote "First run done
(57_stateful/t1). Continuing to poll:" as a plain message. The campaign survived only because the
driver had been launched with `nohup` and was detached from that process, and because `_driver.sh`
skips sandboxes that already have a `_done` marker. A second overseer run, given an explicit
"every message you produce MUST contain a tool call" instruction and a five-minute blocking wait
command, resumed and finished cleanly in 912 s. This is the main finding for the owner: a long
poll-and-wait phase is the weak point of any pi-hosted overseer, and the mitigations are (a) a
blocking wait inside a single tool call, (b) a resume-safe driver, (c) launching the work detached.

Nesting guard: fired in five of six runs, refused every attempt, no nested run executed. Verdict on
3ce8f44: confirmed working under real load.

Containment: no file outside `results/luna-max-v4` was written by the overseer or the takers, and
`tasks-v4` hashes are unchanged. But one taker (56_tmpl/t2) did read `../../results/luna-max-v4/run.py`
- the harness that grades it - and every taker read the deployed `codex-run` SKILL.md. Codex runs
with `danger-full-access` by design, so this is expected rather than a breach, but a taker that can
read its own grader is a benchmark-integrity concern worth a decision: the hidden test was not
present in the sandbox at taker time, so no answer leaked, and `run.py` contains no test content.

## Overseer cost

| run | wall s | input | cacheRead | output | reasoning | total tokens | cost |
|---|---|---|---|---|---|---|---|
| overseer 1 (started the campaign, died polling) | 1490 | 24,499 | 137,792 | 4,589 | 3,134 | 166,880 | $0.00505 |
| overseer 2 (resume, wrote the report) | 912 | 94,187 | 114,240 | 6,909 | 2,974 | 215,336 | $0.01050 |
| **total** | **2402** | | | | | **382,216** | **$0.01555** |

GLM 5.3 Flash oversight cost about one and a half US cents for a campaign that consumed 734k Codex
tokens against the ChatGPT plan. 34 tool calls across the two runs.
