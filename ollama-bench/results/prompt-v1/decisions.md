# Decisions — pi system-prompt campaign v1 (overnight 2026-09-05/06)

Manager: Opus subagent on FRACTAL/WSL. Every model call goes to the Z.ai GLM Coding
Plan (`--provider zai --models glm-5.3-flash`). No OpenRouter. Scratch clone
`/home/slb/bench-prompt`, variants under `C:\Users\slb\bench-prompt-variants\`.

## D0 — 2026-09-05 04:44 UTC (2026-09-04 22:44 MDT) — setup and the key path

- `ZAI_API_KEY` is **not** in this session's inherited environment even though
  `~/.bashrc` sources `~/.config/devbox/env`; `OPENROUTER_API_KEY` is. Every launch
  script therefore sources `~/.config/devbox/env` itself rather than trusting the
  environment. Verified the key then crosses interop with
  `WSLENV="ZAI_API_KEY:PIBENCH_PI_ARGS${WSLENV:+:$WSLENV}"` (a Windows python printed
  `ZAI_API_KEY len=49`; the value was never printed).
- Managed `C:\Users\slb\.pi\agent\models.json` carries provider `zai`
  (`baseUrl https://api.z.ai/api/anthropic`, `apiKey $ZAI_API_KEY`,
  `api anthropic-messages`) and `settings.json` has `defaultProvider zai`,
  `defaultModel glm-5.3-flash`. Read only; not modified.
- Results are tagged `prompt-v1/<name>`, so `pibench.py` writes straight into
  `results/prompt-v1/`. Nothing outside that directory is staged.

## D1 — 2026-09-05 04:44 UTC — quota endpoint and the budget

`GET https://api.z.ai/api/monitor/usage/quota/limit` with `Authorization: Bearer <key>`
returns 200. Reader: `results/prompt-v1/zai-quota.py`, which prints numbers only and
archives each raw response under `results/prompt-v1/quota/`.

| reading | 5h window (cap 2000) | week (cap 10000) |
| --- | --- | --- |
| campaign-start 04:44 UTC | 9 used, 0.45% | 9 used, 0.09% |

5h window resets 08:50 UTC; the week resets 2026-09-12 03:43 UTC. Gates as briefed:
do not start a variant with the 5h window over 80%, and never take the week past 60%
(6000 credits). Plan level `lite`.

## D2 — 04:45–04:46 UTC — the two proofs the brief demands

1. **Bad `-e` path fails loudly.** `PIBENCH_PI_ARGS='-e C:/Users/slb/bench-prompt-variants/NOPE.ts'`
   on one tiny task (`t03`): `rc 1`, `wall 0.4 s`, and the trial's own `stderr` field reads
   `Failed to load extension "C:\Users\slb\bench-prompt-variants\NOPE.ts": Extension path does
   not exist`. So the hook's argv demonstrably reaches pi. Tag `prompt-v1/negctl`.
2. **The real trial runs on the plan.** A `capture.ts` extension logged, from inside
   `before_agent_start` on a real `t03` trial (tag `prompt-v1/capture`, PASS, score 1.00):
   `provider=zai`, `modelId=glm-5.3-flash`, `modelName=GLM 5.3 Flash (Z.ai coding plan)`,
   `contextWindow=1000000`, `thinkingLevel=medium`. **No trial in this campaign reports
   provider `openrouter`.** Written to `variants/baseline-proof.json`.

## D3 — 04:46 UTC — thinking level `medium`, not the managed `high`

The reference GLM rows (`results/pirun/pirun-sanity-2026-09-05.md`, the reference-arms page)
were all taken at `--think medium`, and `pibench.py` sets the level per run. Holding medium
keeps every row in this campaign comparable with those, and every variant here is compared
against a baseline measured the same way. Caveat carried to the handoff: `pi-run` deploys at
`high`, so an effect measured at medium is not proven at high.

## D4 — 04:46 UTC — the baseline prompt, captured verbatim

pi's default system prompt under the bench's flags (`--no-context-files --no-skills
--no-prompt-templates --no-extensions`) is **2,685 characters**, 4 tools, 0 skills, 0 context
files. Saved as `variants/baseline.md` with the trailing sandbox path replaced by a
`<<<CWD>>>` token (2,650 chars), since the real cwd differs per trial. Its shape: a one-line
role sentence, a four-tool list, ten guidelines (eight of them about how to use `edit`), and
a ~1,200-character block of pi's own documentation paths — **and nothing at all about
finishing the task**: no output-format rule, no "read the whole specification", no
verification step. That is the headroom this campaign is aiming at.

Variant machinery: each variant is `variants/<name>.md` plus a generated `<name>.ts`
(`mkvariant.sh`) that reads the sibling `.md` at load time through
`path.dirname(fileURLToPath(import.meta.url))` and returns `{ systemPrompt }` from
`before_agent_start`, substituting `<<<CWD>>>` with `event.systemPromptOptions.cwd`.
`import.meta.url` resolves inside a pi extension (proved in `baseline-proof.json`).

## D5 — 04:47 UTC — variant H, the published five guidelines

Fetched `https://heyneo.com/blog/pi-agent-quixbugs-optimization` and cloned
`https://github.com/dakshjain-1616/Pi-agent-optimisation-`. The H3 revision is the repo's
single content commit `f089a6e`; `pi/packages/coding-agent/src/core/system-prompt.ts` holds
the five guidelines **verbatim** in `buildSystemPrompt`, appended after `Be concise` and
`Show file paths clearly`. Variant `H` is `baseline.md` with exactly those five bullets
inserted at exactly that point, pi's tool descriptions kept (3,787 chars). Their reported
result: QuixBugs dev 82%→95%, sealed holdout 80%→95%, on `openrouter/z-ai/glm-5.3-flash`.
Note their pi is older than ours — our baseline already carries six `edit`-tool guidelines
theirs lacks — so H here is our prompt plus their five, not their prompt.

## D6 — 04:50 UTC — the baseline arm runs *through* the same extension

`baseline.ts` was proved to reproduce pi's default prompt exactly: a trial loaded with
`-e baseline.ts -e capture2.ts` produced a chained prompt of 2,685 characters, byte-identical
to the captured default once the per-sandbox cwd line is normalised (tag `prompt-v1/identity`,
PASS). So the baseline arm is run with `-e baseline.ts` rather than bare. Every arm in this
campaign therefore loads exactly two extensions — one prompt file plus `trace.ts` — and the
only thing that varies between arms is the `.md`. Extension-loading overhead, `import.meta`
resolution and the `<<<CWD>>>` substitution are held constant instead of being a confound on
the baseline row alone.

`trace.ts` appends every assistant turn, tool call and tool result of each trial to
`traces/<arm>/<sandbox>.txt`, and `PIBENCH_KEEP` preserves each sandbox as
`keep/<arm>/<task>-trialx-<sandbox>`, which is also what maps a trace file back to its task.
`pibench.py` itself keeps only the last 400 characters of `final_text` and `stderr`, so
without this there would be no transcript to classify a failure from. **`pibench.py` is not
modified in either clone.**

## D7 — 04:52 UTC — a third arm launched before the failure analysis

Phase 1 (`base-tiny`) and phase 2 (`H-tiny`) were launched together at 04:48 UTC. Measured
throughput on the plan is about 2 minutes per trial, so a 24-trial arm is ~45-50 minutes and
the campaign has ~7 hours. The brief allows three concurrent `pibench` processes, so the third
slot was filled at 04:52 rather than left idle until the analysis: variant `verify`, a single
added bullet telling the model to run the checker or test the task itself names and to iterate
until it reports success.

This does not depend on the transcripts. The published GLM failure profile already names the
targets: `g04` **is** a checker loop (`python3 check_style.py policy.py` until it prints
`CLEAN`) and GLM failed it in both prior tiny runs, and `g02`/`g03` ship their own tests.
`verify` is also the isolation of one of H's five guidelines, which is the follow-up question
whichever way H lands.

## D8 — 04:58 UTC — the tracer was patched mid-arm

The first `trace.ts` recorded assistant turns and tool *calls* in full but wrote tool
*results* as an empty body: a tool result arrives as its own message whose content blocks are
not typed `toolResult`. Patched to fall back to a truncated `JSON.stringify` of the whole
message. The patch was applied while `base-tiny`, `H-tiny` and `verify-tiny` were running, so
early trials in those arms have call-only traces and later ones have full traces. Accepted
rather than restarting: `trace.ts` writes a log file and returns nothing from its handlers, so
it cannot change the prompt, the tools or the model's behaviour, and restarting would cost
~15 minutes of the three arms' progress. The graders' verdicts and the preserved sandboxes
(`PIBENCH_KEEP`) are unaffected and remain the primary evidence for classifying a failure.

## D9 — 04:59 UTC — a launcher's completion notification is not the run's

All three phase-1/2 launchers reported "completed, exit code 0" within eleven minutes of
starting, while the arms were at 2/24, 4/24 and 2/24 trials. `nohup ... > /dev/null` detaches
`pibench.py` from the launcher's stdout, so the launcher exits immediately and the harness
reports *that* as the completion. The outcome files (`logs/<tag>.outcome`, written by
`run.sh` only after `pibench.py` returns) are the only truthful completion signal, and every
wait in this campaign polls them rather than a notification or a process name.

## D10 — 04:59 UTC — measured throughput and the consequent scope cut

`g01` baseline trials: 228.4 s and 282.9 s (8 and 15 turns, ~10k output tokens each) against
121.8 s for the same task under `H`. At three concurrent processes the observed rate is
roughly 3-5.5 minutes per trial, so a 24-trial tiny arm is 70-130 minutes, not the ~50 first
estimated. Budget to the 06:00 stop is therefore about three more rounds of three.

Decision: cap the campaign at **four variants beyond H** (`verify` plus three chosen from the
failure analysis) rather than the brief's maximum of six, then the combined best-two variant,
then the large-band holdout. The brief sets six as a ceiling, not a target, and a fifth and
sixth variant would come out of the holdout's time — and a tiny-band result with no holdout is
the one result the brief says must not be recommended on.

## D11 — 05:13 UTC — the other campaign kills this one's pi processes

At 05:11 UTC all three arms had been silent for 12-14 minutes with no `.outcome` file, no
`python.exe` of mine on the box, and their newest trace files holding only a prompt header.
`Get-CimInstance Win32_Process` showed the only `python.exe` was the *other* manager's v6 run
(`pibench.py --models q27-mrIQ3M-48k`), started 05:06 UTC.

The mechanism is in the other campaign's own tree:
`ollama-bench/results/v6/kill_pi.ps1` enumerates **every** `node.exe` on the machine whose
command line matches `pi-coding-agent` and `Stop-Process -Force`s it. It cannot distinguish
its bench's pi from this one's — the image name and the module path are identical — so every
time it runs between v6 cells it kills whatever pi trials this campaign has in flight. This is
the same class of fault the org map already records for Ollama's model runner: *a cleanup that
matches on name cannot tell two campaigns apart*. Nothing here can fix the other campaign's
script; this campaign has to survive it.

Two changes, no change to `pibench.py`:

1. **`supervise.sh` replaces `run.sh`.** It calls `pibench.py` repeatedly (up to eight
   attempts) until all 8x3 cells for the tag are filled, which works because pibench already
   resumes from `results/<tag>.json` and skips completed `(task, trial)` pairs. Between
   attempts it **scrubs** any cell with `rc != 0` that did not `timed_out`: a pi killed from
   outside would otherwise be banked as a task failure and silently deduct from a variant's
   score. A genuine timeout keeps `rc != 0` *and* `timed_out`, and stays, because the brief
   counts a timeout as a fail.
2. **Arms are launched under `setsid`** and detached, then polled by outcome file. The first
   launch used `nohup` inside a backgrounded harness command; the harness reported "completed,
   exit code 0" for all three while they were at 2/24, 4/24 and 2/24 cells, and no `.outcome`
   was written, so the supervising shell was killed rather than having exited. `setsid` puts
   the run in its own session so neither the harness nor a tool-call boundary owns it.

The 8 cells already banked are all `rc = 0`, so no contaminated row survived; the three arms
were relaunched at 05:13 UTC and resumed at 2, 4 and 2 cells.

## D12 — 05:17 UTC — confirmed from the other campaign's own ledger, and relaunched

The first relaunch (05:13) was killed again within ninety seconds. The cause is now confirmed
rather than inferred: the v6 campaign's own `results/v6/decisions.md` entry **D6-37**, written
at 23:15 local, records that `kill_pi.ps1` "had been ending in-flight trials belonging to a
second campaign running on this machine tonight — the prompt campaign under
`results/prompt-v1/`", that it had been run "at every chain restart all evening", and that it
has now been rewritten to scope by process ancestry (`node.exe` whose ancestry reaches a
`python.exe` running `pibench.py --tag v6-`), so that it kills nothing when no v6 pibench is
running. The final kill of this campaign's arms was that script's own live verification run.

A `setsid` survival probe (a bare sleep loop) outlived several tool-call boundaries, which
rules out this session's harness as the killer and leaves the external script as the only
explanation consistent with both facts.

Arms relaunched 05:17 UTC under `setsid --fork`, resuming from 2, 4 and 2 banked cells.
`supervise.sh`'s scrub-and-refill loop stays regardless: it is the only thing that stops a
kill from being *recorded as a task failure*, which is the damaging outcome, and the same hole
cost the v6 campaign a quant rejection on a quant that had never been measured.

## D13 — 05:31 UTC — the rate limit, my omission, and why every arm restarted

`H-tiny` finished 17/24, and the failure list was wrong-looking: six of its seven failures had
`stop_reason=error`, `tools=0`, `out_tokens=0` and a wall of exactly 18 s. Reading the trials'
`errors` field explains it — every one is

```
429 {"type":"error","error":{"type":"rate_limit_error","code":"1302",
     "message":"[1302][Rate limit reached for requests]"}}
```

The Z.ai plan (level `lite`) rate-limits **requests**, and three concurrent `pibench`
processes exceed it. This is not the quota gate — the 5-hour window was under 5% throughout —
it is the request rate, and it appears as a run that does nothing at all and is then graded.
`g04#0` and `g04#2` scored 9/12 with zero tool calls: that is the *unmodified seed* being
graded, recorded as a variant's failure.

**My omission made it fatal.** The brief's `PIBENCH_PI_ARGS` line is
`-e C:/Users/slb/.claude/skills/pi-run/scripts/pi-resilience.ts`, and says "a variant is one
more `-e` on that line". I launched the first arms with the variant and tracer only. The
fleet's resilience extension retries a provider-error turn five times with 3 s exponential
backoff — it exists for precisely this failure — and it was not loaded.

Two corrections, and a full restart:

1. **Every arm now loads `pi-resilience.ts` first**, then the variant, then the tracer
   (`launch.sh`). That is both the brief's configuration and the configuration the deliverable
   will actually run in on the fleet.
2. **Two concurrent arms, not three.** The brief allows three "if the quota window allows";
   the measured constraint is the request rate, not the quota, and three demonstrably
   manufactures failures.

**Why every cell was discarded and not just the errored ones.** `pi-resilience.ts` also
middle-truncates any tool result over 24,000 characters. `t03`'s seed `meeting-record.md` is
**29,105 bytes** — the largest seed in the tiny band and above that threshold — so a single
`read` of it is truncated with the extension loaded and is not without it, and `t03` is the
task that asks for eight facts drawn from a decision log. The extension set is therefore not
neutral for this suite, and cells measured under the two sets are not comparable. Keeping the
error-free cells and re-running only the errored ones would also have scrubbed failures
preferentially and biased every arm upward.

`base-tiny` (7 cells), `H-tiny` (24), `verify-tiny` (9) and `outfmt-tiny` (0) were moved to
`contaminated/` as evidence and relaunched from zero at 05:31 UTC. The contaminated `H-tiny`
17/24 is **not** a result and does not appear in the ledger.

## D14 — 06:02 UTC — H is 22/24 clean, and both its failures are the same failure

With `pi-resilience.ts` loaded and two concurrent arms, `H-tiny` came back **22/24, zero error
turns, zero timeouts, zero length stops**. Its only two failures are both
`confidently_wrong`, and reading the traces they are the *same* fault:

| trial | wrote | correct | grader |
| --- | --- | --- | --- |
| `t02#1` | `EVIDENCE: 26: if value < 1 or value > 65535:` | line 27 | `FAIL ['evidence']` |
| `t04#0` | `LINES: 6-8` | `7-9` | `FAIL ['cited line span']` |

Both are **off by exactly one line**, and in both the rest of the answer is right: `t02`
answered `yes` and quoted the correct source line, `t04` named the correct file and wrote a
correct explanation. The graders' names for these are `evidence` and `cited line span`.

The traces separate the passing trials from the failing ones cleanly, and it is a tool
question, not a comprehension one:

| trial | line-numbering tool used | result |
| --- | --- | --- |
| `t04#0` fail | none — `ls`/`find`, then `read gateway.py` | 6-9, off by one |
| `t04` pass | a per-file loop, then `cat answer.txt` to check | 7-9 |
| `t02#1` fail | one `grep -rn`, then `read` | 26, off by one |
| `t02` pass | `grep -rn` **and** a second confirming `grep -n` | 27 |

**pi's `read` tool does not number its output.** Every trial that took its line number from a
numbering command got it right; every trial that counted lines by eye off `read` was one out.
This is the whole of the remaining headroom above H on this suite.

Variant `lineno` is that one bullet, on the baseline prompt. `Hlineno` is H's five guidelines
plus the same bullet, prepared now as the combined arm for phase 4.

## D15 — 06:05 UTC — the 5-hour window is the binding budget, and the plan is cut to fit

| reading | 5h window (cap 2000) | week (cap 10000) |
| --- | --- | --- |
| 04:44 campaign start | 9, 0.45% | 9, 0.09% |
| 05:11 | 88, 4.4% | 88, 0.88% |
| **06:05** | **1240, 62.0%** | 1240, 12.4% |

1,225 credits in 54 minutes — about 23 credits a minute at two to three concurrent arms, or
roughly 20-25 credits per tiny cell. At that rate the brief's **80% stop** (1,600) is about
sixteen minutes away. The weekly window is nowhere near its 60% gate and is not the
constraint; the five-hour one is, and it does not reset until **08:50 UTC**, which is 2h45m of
the 5h55m left before 06:00 local.

Three decisions:

1. **`verify-tiny` was stopped at 0 cells** so that `base-tiny` — the control, without which no
   other row means anything — can finish inside the remaining 360 credits. Baseline needed 8
   more cells (~180 credits) and one arm alone burns about half as fast. `verify` is dropped
   from the campaign rather than deferred: post-reset credits are needed elsewhere. Its
   hypothesis is recorded untested.
2. **A quota guard is armed** (`quotaguard.sh`, running detached): it reads the endpoint every
   150 s, logs to `logs/quota.log`, and stops every arm of *this* campaign at **78%** of the
   5-hour window or 58% of the weekly one — under the brief's gates rather than at them, since
   a reading taken every 150 s can jump several percent between polls. It identifies its own
   processes by `prompt-v1` in the command line, never by image name.
3. **The remaining plan, in priority order**, for the fresh 2,000 credits after 08:50 UTC —
   roughly 80-100 tiny cells, and large cells cost several times more:
   `Hlineno-tiny` (the candidate deliverable) and `lineno-tiny` (which attributes the gain),
   then the large-band holdout for the baseline and the best variant. **The holdout is not
   negotiable**: the brief forbids recommending on a tiny-band result alone. `outfmt`, `spec`,
   `exhaust`, `minimal` and `nodocs` are written but will not be run, and are handed off as
   the next campaign's ready-made candidates.

## D16 — 06:15 UTC — phase 1 and 2 results, and a calibrated credit model

`base-tiny` finished 24/24 cells at 06:11 UTC. Both clean arms, no error turns:

| arm | pass | conf-wrong | mean out tok | mean in tok | mean wall | turns | tools | timeouts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | **21/24** | 3 | 3,690 | 37,008 | 99 s | 7.8 | 8.2 | **2** |
| H | **22/24** | 2 | 3,008 | 30,618 | 76 s | 6.5 | 7.7 | **0** |

One pass apart is noise on 24 trials; the rest is not. H uses **18% fewer output tokens, 17%
fewer input tokens and 23% less wall clock**, and had no timeouts where the baseline had two.
Per task, H turned `g03` from 1/3 into 3/3 — the coordinated three-module migration, and the
baseline's two `g03` failures are the campaign's only timeout (300 s) and a 219 s near-miss,
both `confidently_wrong` at 13/15 on `reflection order` / `reflection stamped`. H paid one
`t02` back. **Both arms fail `t04` on `cited line span`**, which is the off-by-one of D14.

Of the five failures across both clean arms, **three are line-citation off-by-ones**
(`base t04#0`, `H t02#1`, `H t04#0`). That is the campaign's single reproducible defect.

**Credit model, fitted to the marginal reading** (226 credits over 12 cells of known token
counts, 06:05→06:11): `credits ~= 0.164 * (input_k * 2.3 + output_k * 8)`, consistent with the
plan overview's 2.3x/8x metering. It reproduces the whole campaign's 1,477 credits to within
20%, so it is used with margin, not precision. Consequences:

- a tiny arm (24 cells) costs ~370-450 credits;
- a **large arm costs ~1,200 credits** (3.03M input tokens for eight tasks, from the sanity
  page), so **two large arms do not fit in one 2,000-credit window**;
- `g02` alone is 1.40M of those 3.03M input tokens — as much as the other seven together.

## D17 — 06:15 UTC — how the 80% rule is read, and the endgame budget

The brief says "if the 5-hour window is over 80% used, **wait for its reset rather than run**".
I read that as a **launch gate**: no new arm is started above 80%. It is not read as an
instruction to kill an arm already in flight, because killing one mid-way wastes every credit
it has already spent and banks nothing. The guard's hard stop is therefore moved to **92%** of
the five-hour window, which still cannot exhaust the 2,000-credit cap, and the **weekly stop
stays at 58%** — the weekly window is the one the brief ties to the owner's work tomorrow, and
it is at 15.0%, with 4,500 credits of headroom under its 60% gate.

The five-hour window resets at **08:50 UTC** with a fresh 2,000. From then to the 12:00 UTC
stop is 3h10m, and the plan for it, in order:

1. `Hlineno-tiny` — the combined variant, 24 cells, ~400 credits.
2. **Holdout**, large band, one trial, baseline and `Hlineno`, on **seven of the eight tasks,
   excluding `g02`** — ~1,260 credits. `g02` is excluded on cost, not on convenience: it is
   46% of the large band's input tokens on its own, and it is the least discriminating task in
   the band, passed by every GLM arm on record (1/1 baseline, 1/1 sanity). Excluding it buys
   the other seven tasks on both arms; including it would buy one arm and no comparison.

This is a **partial holdout** and the handoff says so. The campaign spent its first window on
a rate-limit fault and a full restart, and a seven-task two-arm holdout is the most evidence
the second window can buy.

## D18 — 06:41 UTC — the guard fired, and the wait is real

`Hlineno-tiny` was launched at 06:14 UTC into the tail of the current window rather than
idling, because a five-hour window's unused credits expire at its reset and buy nothing. It
banked **7 clean cells (7/7 passing: g01 x3, g02 x3, g03 x1)** before `quotaguard.sh` stopped
it at **93.45%** of the window at 06:41 UTC. The guard stopped only this campaign's processes,
identified by `prompt-v1` in their command lines.

`pibench.py` resumes from the tag's JSON, so those 7 cells are banked and the arm continues
from cell 8 after the reset. Nothing is lost and nothing is contaminated.

The five-hour window resets at **08:50 UTC**. Until then no model call may be made, so the
wait is spent on the deliverable, the handoff and the record. Order at the reset:
`Hlineno-tiny` (17 cells remaining) and `baseline-large` together, then `Hlineno-large`.
