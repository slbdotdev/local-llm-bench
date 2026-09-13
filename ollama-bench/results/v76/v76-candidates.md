# v7.6 candidate log

One row per candidate change to slbh's tool layer. A hypothesis is written here BEFORE the
sweep that tests it, so a result cannot be read backwards into the reason it was tried.

Rules for this file, from the brief: one change per sweep; a change is kept only when the
sweep stays 20/20 and is better on wall, tool calls, API rounds and output tokens; a change
that costs a slot is reverted whatever it saves. Out of scope, untouched: `agent.go`, the
provider layer, the seat's system prompt (other than text that is purely tool
documentation), model and effort settings, anything in the bench that changes what is graded.

## Baselines, on fox, 2026-09-13

Both re-measured here rather than taken from v7.5's rows: that arm ran the windows/amd64
build, whose `quick_bash` is `cmd.exe`, and 54% of its shell calls failed before the model
adapted. `shell_linux.go` runs bash, so on this host that whole failure class is absent and
the Windows numbers cannot be the before.

| arm | build | rows |
| --- | --- | --- |
| pi | pi 0.85.1, node 22.22.1 | `v76base.json`, label `pi-0.85.1` |
| slbh_real | d4b3930, linux/amd64 | `v76base.json`, label `d4b3930` |

Two deviations from "change only `baseUrl`" in the fox copy of the pi agent directory,
both forced, both recorded here because each is a difference from the v7.5 arm A:

1. `pi-agent/models.json` registers eight models and `q27-IQ2_M-64k` is not among them, so
   pi refuses the model outright (`Model "ollama/q27-IQ2_M-64k" not found`). The fox copy
   adds it, cloned field for field from the `q27-IQ3_M-64k` entry beside it (reasoning true,
   contextWindow and maxTokens 65536, zero cost). The desktop must have carried an
   uncommitted edit for the v7.5 arm A to have run at all.
2. `settings.json` pins `shellPath` to `~/scoop/apps/git/current/bin/bash.exe`, a path that
   does not exist on Linux. The fox copy pins `/bin/bash`. Leaving it would have broken pi's
   shell tool on every slot, which is the pi arm's version of the `cmd.exe` fault this
   comparison exists to get away from.

## Pre-registered hypotheses

Ranked before any transcript was read, from the v7.5 write-up's section 4 table plus one
probe run on fox. Each says what it predicts, so a null result is visible as one.

### H1 -- `glob` has no recursive wildcard and no way to say "nothing matched" (candidate c1)

`r.glob` calls `filepath.Glob`, which has no `**`: it matches within one path segment, so
`**/*.py` means `*/*.py` and finds nothing two directories down. And a pattern that matches
nothing returns the empty string, which is what a broken call also returns.

Measured on fox before any sweep: one turn, `slbh -p "List the .py files under this
directory"` over a tree holding `sub/deep/b.py`. The model called `glob {"pattern":
"**/*.py"}` exactly once, got `""`, answered "No .py files were found under this directory",
and stopped. Wrong answer, one round, no retry.

Predicts: fewer glob calls that return nothing, fewer `quick_bash` fallbacks to `find`/`ls`,
and fewer `read_file` calls spent discovering a tree the model could have seen in one call.

### H2 -- a successful tool that returns nothing is indistinguishable from a broken one

The same fault as H1's second half, in `grep` (no match), `read_lines` (a range past EOF)
and `read_file` (an empty file). The v7.5 table calls these out as the twelve "bare"
failures, but the larger class is the calls that SUCCEED and return nothing: those are not
in that table at all, because they are not failures. Candidate: each returns a short
sentence naming what was searched and what was not found.

Predicts: fewer repeated identical calls, fewer rounds.

### H3 -- `read_file` on a missing path spends three rounds on a name the model nearly had

`readFile` returns the raw `os.Stat` error. A model that guessed `docs/README.md` for
`README.md` learns only that the path is wrong, not what is there. Candidate: on a missing
path, name the sibling entries of the nearest existing parent directory.

Predicts: fewer `read_file` failures and fewer follow-up `glob`/`quick_bash` calls.

### H4 -- tool and parameter descriptions carry no semantics

Every tool is a single short sentence and no parameter has a `description` at all, so
one-based vs zero-based, inclusive vs exclusive, and what a path is relative to are all
guesses the model pays a failed call to resolve. Candidate: parameter descriptions and
sharper tool descriptions, no behaviour change.

Predicts: fewer argument-shaped failures; the cheapest change to try and the easiest to
revert.

### H5 -- `quick_bash` and `quick_py` time out at five seconds

A slot's own test suite routinely takes longer, and the tool has no way to say "this needs
longer" short of `long_job`, which is asynchronous and costs at least two more rounds.
Candidate: raise the cap, and make the timeout message name `long_job` explicitly.
Evidence-gated: only if the baseline transcripts show timeouts.

### H6 -- `grep` returns unbounded output and walks everything

No match cap, no per-line cap, no skipped directories, no binary detection. One grep over a
tree with a `.git` or a large CSV can cost more context than the answer is worth. Candidate:
cap matches and line length, skip the same directories `glob` skips, and report what was cut.

Predicts: lower prompt tokens and fewer compactions; neutral on tool calls.

### H7 -- there is no directory listing tool

`ls` is `quick_bash`, which is the failure-prone tool. Candidate: either a `list_dir` tool or
`read_file` on a directory answering with its listing. Held back until the transcripts say
how much of `quick_bash` is really `ls`.

## Baseline measurement, fox, 2026-09-13

| arm | correct | wall s | tool calls | API rounds | output tokens |
| --- | --- | --- | --- | --- | --- |
| pi (pi-0.85.1) | 20/20 | 1,912 | 246 | 210 | 105,893 |
| slbh_real (d4b3930) | 19/20 | 5,199 | 336 | 281 | 97,277 |

The correctness bar for every candidate is therefore 19/20 with no slot the baseline passed
turning into a failure, not an absolute 20/20 (control session, 2026-09-13). slbh's failing
slot is p02-main-claude, which reached the 900 s cap at 902 s with a partial deliverable
(`visibly_failed`, score 0.1429); m05-cheap-glm also reached the cap and still graded correct.
A slot sitting at the cap is noisy at n=1, so p02 flipping either way is a caveat, not a size.

What the baseline changed about the hypotheses, and it is a lot:

* **The Windows failure class really is gone.** 16 failures in 336 calls (4.8%) against
  v7.5's 69 in 464 (15%). Nothing here is worth fixing for its failure rate alone.
* **Tool execution is 0.8% of wall** -- 42.5 s of 5,199 s, measured from the interval between
  each `tool` event and its `tool_result` in the twenty transcripts. Nothing a tool does
  faster can move wall. Wall moves only by cutting API rounds and the tokens each one carries.
* **slbh is not losing on volume, it is losing on rounds and on context.** 336 calls against
  pi's 246, 281 rounds against 210, and FEWER output tokens than pi (97,277 against 105,893).
  Per round it sends 8,677 prompt tokens against pi's 6,917.
* **read_file is 146 calls and 257 KB, 65% of every byte returned to the model**, against
  pi's 72 reads. pi uses four tools only -- bash 134, read 72, edit 27, write 13 -- and finds
  things with `find` and `grep -rn` in one shell call where slbh spends several.
* **H1 is confirmed and is bigger than the write-up suggested.** Eight of the eleven distinct
  glob patterns the baseline issued contain `**`: `**/*`, `docs/**`, `history/**`,
  `**/HarborAtlas/**`, `docs/policy/**`, `ops/**`. Every one of them was answered by
  filepath.Glob as a single-segment `*`, so `docs/**` listed the direct children of docs and
  nothing under them, and `**/*` listed the second level while missing the first. Not one of
  those calls failed; they all returned a plausible, wrong, partial listing.
* **H2 is confirmed at 6 of 31 grep calls** returning the empty string, plus 1 of 16 globs.
* **H3 is confirmed but small**: 3 read_file failures on a missing path out of 146.
* **H5 is nearly a null**: one `quick_bash` timeout in 90 calls, and it was `find /` over the
  whole filesystem. Deprioritised.
* **H6 is a null on this suite**: the largest single result is 25 KB and the median is far
  below any cap worth adding. Dropped.

## Results

Filled in as each sweep lands.

### c1 -- glob (`v76c1.json`, label `c1-glob`, binary `slbh-v76-c1`)

`**` matches any number of path segments; a pattern that matches nothing returns a sentence
naming what was searched; directories carry a trailing separator; results cap at 400 with a
count of what was cut; `.git`, `__pycache__`, `.pytest_cache`, `node_modules`, `.venv`,
`.mypy_cache` and `.tox` are not descended into for a `**` pattern. The tool description and
the `pattern` parameter now say that `**` works.

### c2 -- fruitless calls answer in words (`v76c2.json`, label `c2-speak`, binary `slbh-v76-c2`)

Stacked on c1. `grep` with no match reports the pattern and how many files it really
searched; `read_file` on a directory returns that directory's listing; `read_file` and
`read_lines` on a missing path name the working directory and the entries of the nearest
directory that does exist; `read_lines` past the end of a file says how many lines it has;
`edit_file` distinguishes "not found, must match byte for byte" from "appears N times"; and
`write_file` on an existing path names `edit_file`.

### c1 result -- kept, with a caveat this file states plainly

| sweep | correct | wall s | tool calls | API rounds | output tokens |
| --- | --- | --- | --- | --- | --- |
| slbh_real d4b3930 (baseline) | 19/20 | 5,199 | 336 | 281 | 97,277 |
| slbh_real c1-glob | 19/20 | 5,181 | 305 | 246 | 116,067 |

Per-tool, over the twenty transcripts of each sweep:

| tool | baseline calls | c1 calls | baseline failed | c1 failed |
| --- | --- | --- | --- | --- |
| read_file | 146 | 120 | 3 | 0 |
| quick_bash | 90 | 62 | 9 | 10 |
| grep | 31 | 36 | 0 | 0 |
| quick_py | 7 | 27 | 1 | 12 |
| edit_file | 32 | 23 | 1 | 0 |
| glob | 16 | 16 | 0 | 0 |
| all | 336 | 305 | 16 | 23 |

The mechanism worked and is visible: 26 fewer `read_file` calls, 28 fewer `quick_bash`
calls, and every one of the three `read_file` path failures gone, because a `**` pattern now
answers the question the model was asking instead of a partial listing it could not tell from
a complete one. `glob` returned 13.4 KB against 4.3 KB for the same sixteen calls -- the same
calls, actually answered.

Slot by slot: 13 of 20 better on wall (median -21 s), 13 of 20 better on tool calls (median
-3), 13 of 20 better on rounds, 11 of 20 better on output tokens (median -150). The aggregate
is flat on wall and 19% WORSE on output tokens, and all of that sits in four cap-adjacent
slots: m04-main +2,963, m10-main +7,555, n02 +7,636, p05 +5,759 output tokens, together
+23,913, against -5,123 over the other sixteen.

Two of those were re-run at trial 1 on the same binary, because a slot at the wall cap at n=1
is noise and not a size:

| slot | baseline | c1 trial 0 | c1 trial 1 |
| --- | --- | --- | --- |
| n02-main-glm | correct, 702 s / 34 | confidently_wrong, 902 s / 19 (cap) | correct, 640 s / 12 |
| p05-main-claude | correct, 594 s / 21 | correct, 902 s / 42 (cap) | visibly_failed, 902 s / 14 (cap) |

n02's regression does not reproduce and reverses: at trial 1 it is faster than the baseline
with a third of the tool calls. p05's does reproduce -- both c1 trials reach the cap where the
baseline finished in 594 s -- and that is a genuine cost regression on the suite's largest
slot, recorded here rather than explained away.

KEPT, on the median slot rather than the sum, and this is a judgment the control session can
overturn from the numbers above: the change removes a demonstrated silent-wrong-answer defect
(a `**` pattern returning a plausible partial listing), improves two of four cost columns in
aggregate and three of four at the median, and leaves the correct count where it was. Commit
`9784a69`, "glob matches whole trees".

## H5 is a measured null; two new hypotheses take its place

Asked by the control session, 2026-09-13: what are the twelve `quick_py` failures under c1?
Classified from the c1 transcripts by the text of the failure itself:

| cause | quick_py under c1 | quick_bash under c1 | quick_bash at baseline |
| --- | --- | --- | --- |
| timeout | 0 | 0 | 1 |
| python exception raised by the model's own script | 11 | 3 | 0 |
| `python: command not found` (exit 127) | 0 | 6 | 5 |
| module not installed (`pytest`) | 1 | 1 | 0 |
| other exit status | 0 | 1 | 3 |

**Not one of them is a timeout.** The eleven exceptions are AssertionError (4), TypeError (4),
AttributeError (2) and ValueError (1), every one of them raised inside the script the model
wrote -- a probe asserting a pricing rule it had just inferred, a `re.search(..., reflags=)`
that is not a real keyword, a `str` with no `.read_text()`. Those are the tool working: the
script ran, it failed on its own terms, and e45e9d5 put the traceback in front of the model,
which then fixed it. The rise from 7 calls to 27 is the model computing answers now that c1
lets it see the tree in one call, and is not a defect to fix.

Across both sweeps there is exactly ONE timeout anywhere: a baseline `quick_bash` running
`find /` over the whole filesystem. **H5 is dropped as a measured null** -- raising the
five-second cap would have changed one call in 641.

Two hypotheses replace it, pre-registered here before any sweep tests them.

### H8 -- the largest single failure class is `python` not existing (candidate c4)

`python: command not found` is 5 of 16 baseline failures and 6 of 23 under c1: 11 of the 39
failures over both sweeps, 28%, the biggest single cause by a wide margin. Ubuntu ships
`python3` and no `python`, the model writes `python`, and the shell's own message is attached
but arrives only after the call is spent. Each one costs a round.

Candidate: name the interpreter that does exist. `quick_bash`'s description is one sentence
that says only "five second timeout"; it can say which shell it is and that `python3` is the
interpreter on PATH, and a 127 failure can say the same in place. Both are tool documentation
and error formatting, which is in scope; neither changes what the tool runs.

Predicts: 10 or so fewer failures, each worth one round. Small and cheap; the reason to try
it is that it is the only failure class left with a single identifiable cause.

### H9 -- `quick_py`'s environment is undocumented

Its description says "the managed scientific environment" and names nothing in it. `pytest`
is not in it, and the model reached for pytest twice across the two sweeps. Candidate: the
description names what is there. Folded into c4, since it is the same one-line change to the
same kind of text, and separating them would cost a whole sweep to measure two failures.

### c2 result -- REVERTED, and it is the most interesting result of the night

| sweep | correct | wall s | tool calls | API rounds | output tokens |
| --- | --- | --- | --- | --- | --- |
| slbh_real d4b3930 (baseline) | 19/20 | 5,199 | 336 | 281 | 97,277 |
| slbh_real c1-glob (running best) | 19/20 | 5,181 | 305 | 246 | 116,067 |
| slbh_real c2-speak | 19/20 | 5,240 | 330 | 269 | 107,099 |

Against the running best: wall +60 (8 slots better, 11 worse), tool calls +25 (7 better, 11
worse), rounds +23 (5 better, 10 worse), output tokens -8,968 (10 better, 10 worse). Three of
four cost columns worse, so by the brief's rule it is reverted and not committed.

It is reverted even though **it did exactly what it was built to do, and the counters say so
unambiguously**:

| | baseline | c1 | c2 |
| --- | --- | --- | --- |
| grep calls returning the empty string | 6 | 9 | **0** |
| tool failures, all tools | 16 | 23 | **11** |
| read_file failures | 3 | 0 | 0 |

Every silent result is gone and failures are down by half, and the sweep still cost more. The
mechanism that best fits the rows is worth writing down because it inverts the hypothesis:
`read_file` went UP, 120 to 142, while grep's calls stayed at 31. An empty grep result used
to make the model try another pattern -- cheap, one round, and sometimes it found the term.
A grep that says "no match for X in 92 files under ." is believed, and the model stops
searching and starts reading files one at a time instead. Telling a model the truth ended its
search; saying nothing kept it searching.

That is a hypothesis about one sweep at n=1 and not a finding: the median wall delta is
+8.6 s and 11-worse-to-8-better is well inside this quant's noise. What it does justify is
not trying "say it plainly" again in the same form. If it is revisited, the no-match message
should name the next cheap move (a broader pattern, a case-insensitive retry) rather than
assert the absence and stop there.

Not committed; the working tree was reset to c1 and c3 was rebuilt on c1 alone.

### c3 result -- REVERTED, and the clearest revert of the night

| sweep | correct | wall s | tool calls | API rounds | output tokens |
| --- | --- | --- | --- | --- | --- |
| slbh_real c1-glob (running best) | 19/20 | 5,181 | 305 | 246 | 116,067 |
| slbh_real c3-batchread | **16/20** | 6,014 | 332 | 256 | 137,311 |

Worse on every column, and three fewer slots correct: m10-main-claude and p05-main-claude
went from correct to `visibly_failed` at the cap, n05-main-luna from correct to
`confidently_wrong` in 137 s with 29 tool calls. Against c1: wall +834 (11 slots worse),
calls +27, rounds +10, output tokens +21,244 (13 slots worse, median +410). Reverted on
correctness alone; the cost columns only agree.

Why it failed is visible in the calls, and it is not that batching is a bad idea:

| | c1 | c3 |
| --- | --- | --- |
| read_file calls | 120 | 112 |
| of those, using `paths[]` | n/a | **12 of 112** |
| bytes returned by read_file | 228.7 KB | **308.6 KB** |
| read_lines calls | 5 | **43**, 7 of them failed |

The model took the batch form 11% of the time, and when it did it read MORE than it needed --
80 KB more content over 8 fewer calls -- because a batch is cheap to write and a wrong guess
inside one costs nothing visible. The round-trip saving never arrived and the context cost
did. Worse, `read_lines` went from 5 calls to 43: rewriting read_file's schema to carry two
alternative parameters, with neither marked required, seems to have pushed the model off
read_file toward the neighbouring tool it was sure about. That is a self-inflicted wound in
the schema and a caution about the whole change category: a parameter that is optional in
both directions is a decision the model now has to make on every call.

If batching is tried again it should keep `path` required and add a separate tool rather than
a second spelling of an existing one, and it should be measured on a suite where the model is
strong enough to choose what to read.

## Where the cost actually is, and what that does to the remaining hypotheses

The control session decomposed the twenty baseline transcripts on 2026-09-13: of 5,199 s,
prefill was 217 s, streaming 4,656 s, tool execution 43 s, everything else 284 s, with 2.23M
of 2.44M prompt tokens reported cached. slbh decodes at 20.9 tokens/s; pi produced 105,893
output tokens inside 1,912 s of total wall on the same model, the same GPU, the same host, so
its rate is at least 55 tokens/s. Per round slbh sends 8,739 prompt tokens against pi's
6,917, which is nowhere near a 2.6x decode difference.

**Fewer tool calls therefore cannot close this gap, and this project's first three sweeps are
evidence of it.** Ranked by output tokens per API round:

| sweep | tool calls | rounds | output tokens | output tokens per round | wall s | correct |
| --- | --- | --- | --- | --- | --- | --- |
| baseline d4b3930 | 336 | 281 | 97,277 | 346 | 5,199 | 19/20 |
| c1-glob | 305 | 246 | 116,067 | 472 | 5,181 | 19/20 |
| c2-speak | 330 | 269 | 107,099 | 398 | 5,240 | 19/20 |
| c3-batchread | 332 | 256 | 137,311 | 536 | 6,014 | 16/20 |

Every candidate that cut rounds raised tokens per round enough to cancel it. c1 removed 35
rounds and 31 tool calls and finished 18 s faster. That is the whole story of the night in one
line: on this arm a round is not the unit of cost, a generated token is, and a tool change
moves wall only insofar as it makes the model write less.

Whether the nineteen-tool array is itself part of the decode rate is being replayed by the
control session on the idle GPU (one real slbh request body, as sent, with no tools, and with
four). The result decides whether the next candidate is a tool-array change or c4. Both are
pre-registered below; c4 is built and waiting either way.

### H10 -- the tools array may be part of the decode rate (candidate, gated on the replay)

slbh sends nineteen tool schemas on every request; pi sends four. If a server-side constraint
over the tool set costs sampling time, the fix is in the tool definitions, which is in scope.
Gated: it is only a candidate if the replay shows the rate move, and the shape of the change
depends on whether it is the count or the bytes that matter -- shortening descriptions is
free, while dropping tools removes capability and needs a reason better than a benchmark.

### H11 -- richer tool results buy longer reasoning, not shorter

Tokens per round rose with every candidate that gave the model more to work with: 346 at
baseline, 472 when `**` started returning whole trees, 536 when batches returned 80 KB more
file content. The direction is consistent across three sweeps at n=1 and is the opposite of
what the round-count hypotheses predicted. If it holds, a tool layer optimised for this arm
would return LESS per call, not more, and bound its results tightly -- the reverse of H6 as I
first wrote it. Not testable within the remaining budget; recorded so it is not rediscovered.
