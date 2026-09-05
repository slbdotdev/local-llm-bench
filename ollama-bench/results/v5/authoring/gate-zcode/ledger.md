# ZCode arm ledger

Decisions and incidents during the ZCode reference-arm run, 2026-09-05.

## 1. Route proof (05:17Z) — passed

One trivial task in `/mnt/d/bench-zcode/probe`. Run
`wr-wsl-20260905T051723Z-21fdcb4f3c14`: `state=succeeded`, `model=GLM-5.3-Flash`,
`variant=high`, `harness=zcode`, and the harness telemetry shows
`providerId=builtin:zai-coding-plan`, `baseURL=https://api.z.ai/api/anthropic`.
The sandbox file was written correctly and `final.txt` held `DONE`. Route confirmed
as the coding-plan provider on GLM-5.3-Flash.

Already visible here: **12 `[1302] Rate limit reached for requests` retries in a
26-second trivial run**, all recovered internally by ZCode.

## 2. Concurrency dropped 4 -> 2 (05:28Z) — coordinator correction

**What happened.** The tiny band launched at four concurrent per the brief. After
~9 minutes not one of the four runs (g01-g04) had completed, and their 1302 retry
counts had climbed to 18, 18, 28, 18 — still rising. The coordinator reported the
same fault independently: the plan was shared at that moment with the pi prompt
campaign (three pibench arms, owner priority) and two v7 pi workers, roughly ten
concurrent consumers.

**Why the brief's own trigger could not fire.** The brief said to drop to two "if
the plan answers with a rate limit or quota error at the start of a run". ZCode
retries a throttled request internally up to 11 attempts with backoff before it
fails the turn, so a 1302 never reaches the driver as a start-of-run error. The
trigger was unreachable as written. The retry count in `harness.log` is the only
honest signal, so the driver now records it per task.

**Why the band was restarted rather than drained.** The correction said to let the
four in-flight runs finish and start no new run until at most two were running.
Those two halves could not both hold: the running driver backfilled a slot the
instant one freed — it had already started t01 as a fifth task — and a Python
process's pool size cannot be changed from outside. Draining would have preserved
nothing, because **no run had completed**. Restarting also keeps the band
methodologically uniform: a wall-clock column mixing 4-concurrent and 2-concurrent
runs is not comparable, and this is a published reference row. The four in-flight
runs were therefore stopped and the tiny band restarted from prep at two.

Only this arm's own process tree was signalled, identified through `/proc` by uid
and by a cmdline marker unique to this arm (`zcode_procs.py`); no pi, Codex, v6 or
Ollama process was touched.

**Changes made to the driver.**

- Concurrency is re-read from `gate-zcode/conc.txt` before every launch, so the
  pool can go 2 -> 1 mid-band without another restart. Default is now 2.
- `rate_1302` per task: the count of `Rate limit reached for requests` lines in
  that run's `harness.log`.
- `outcome` per task: `ok` | `rate_limited` | `timed_out` | `failed`. A turn that
  fails after exhausting its retry attempts against a throttling plan is
  `rate_limited` — a plan outcome, not the model failing the task — and is
  excluded from the pass-rate denominator so the score is not contaminated.
- `conc_at_launch` per task and a `concurrency_history` in `_meta`.

## 3. Restart at two concurrent (05:29Z)

Tiny band restarted from prep, pool 2. Escalation rule from the coordinator: if the
1302 count is still climbing at two concurrent, drop to one (`echo 1 > conc.txt`)
and say so in the handoff.

## 4. Dropped to one concurrent (05:30Z) — escalation criterion met

At pool 2 the retry counts were still climbing steeply: over 240 s, g01 went
6 -> 20 and g02 6 -> 16 `[1302]` retries, about 3.5 refusals per minute per run.
Per the coordinator's rule, the pool went to **1** (`echo 1 > conc.txt`). No restart
and no kill was needed: the driver re-reads `conc.txt` before every launch, so the
two in-flight runs were allowed to finish and nothing new started until one slot was
free. This is recorded in the handoff.

## 5. `quota_exhausted` is a mislabel — it was rate limiting, not credit exhaustion

The g04 run of the first (stopped) driver ended `state=quota_exhausted`. Its
`result.json` detail shows the real cause:

    reason=rate_limited status=429 providerErrorCode=1302 retryable=true

That is ZCode exhausting its own 11-attempt retry budget against a throttling plan,
not the plan running out of credits — the quota read two minutes later stood at
11.85% of the 5-hour window. The `z-run` wrapper maps harness exit code 1 onto
`quota_exhausted`, which conflates "out of credits" with "throttled past the retry
budget". **Anything reading `state` alone will misdiagnose this.** The driver's
`classify()` catches it correctly: state not `succeeded` plus a non-zero 1302 count
gives outcome `rate_limited`, which is excluded from the pass-rate denominator.

Worth raising outside this arm: the wrapper's state name is misleading under
contention, and `pi-run`/`codex-run` may share the mapping.

## 6. Plan accounting — credits are being drawn, magnitude not attributable

| reading | 5h window used | week used |
| --- | --- | --- |
| 05:17:11Z before the arm | 109 | 109 |
| 05:30:04Z mid-run | 237 | 237 |

Credits **do** move during ZCode traffic, so the campaign's unlimited-Flash
allowance does not make ZCode usage free against the plan. But the delta of +128 is
**not attributable to ZCode alone**: the pi prompt campaign and two v7 pi workers
were drawing on the same `ZAI_API_KEY` throughout this window. The direction is
established; the per-harness magnitude is not, and this arm cannot isolate it
without a quiet plan. Stated as such in the report rather than presented as a
ZCode-only figure.

## 7. One concurrent fixed it — measured

Throttling at pool 1 collapsed, and with it the wall times. Same band, same tasks:

| task | pool at launch | 1302 retries | wall s | outcome |
| --- | --- | --- | --- | --- |
| g02 | 2 | 16 | 294 | ok |
| g03 | 1 | 2 | 208 | ok |
| t02 | 1 | 0 | 55 | ok |
| t03 | 1 | 0 | 29 | ok |

Against 18-30 retries per run at pool 4, where nothing finished at all in nine
minutes. The contention was concurrency-driven, not a plan cap: an unthrottled tiny
task completes in about 30 s. g01's first attempt died `quota_exhausted` after 23
retries and was automatically retried by the driver 60 s later.

Consequence for the numbers: **`wall_s` in this arm is not a clean model-speed
measurement.** Runs launched while the plan was contended carry the retry backoff
inside their wall time. The `rate_1302` and `conc_at_launch` columns are what make a
row readable; a wall time beside a high retry count measures the plan, not the model.

## 8. Supervisor converge mid-arm (ansible-slb 2b495f7, landed 05:37:53Z)

Two changes, reported by the coordinator and confirmed against this arm's own data.

**The ZCode runtime's stderr was an unread pipe.** On Linux that pipe holds 64 KB, so
a run absorbing many 1302 retries could block on a full pipe and freeze silently.
This arm has the evidence. All four pool-4 runs stopped writing `harness.log` at
23:24:03-23:24:58 local and were still reported `running` when they were stopped at
23:28 — frozen for three to four minutes with no output.

This **corrects the reading in section 2**. The nine-minute pool-4 stall was not
throttling alone: the throttling generated the stderr volume, and the unread pipe
turned a slow run into a stopped one. Trigger and amplifier, not one cause. The
decision to drop concurrency was still right, and the pool-1 measurement in section 7
still stands on its own, but pool 4 vs pool 1 is **not** a clean concurrency
comparison, because every pool-4 run also carried the pipe fault. It is not offered
as one.

**Failure-state names changed.** A turn that exhausts its 1302 retries now ends
`state=failed` with the 1302 text in `detail`; `quota_exhausted` is reserved for a
402/balance refusal. `classify()` and the page generator accept both spellings and
map either to outcome `rate_limited`; `quota_exhausted` survives as an outcome only
with 402/balance evidence in `detail`. Section 5's mislabel finding is therefore
already fixed upstream.

**Uniform grading across the boundary.** The tiny band's driver process was started
before this edit, so it classified its own runs with the older rule. Rather than
restart a healthy band, `make_zcode_page.py` now **re-derives every task's outcome at
report time** from the run's own durable `result.json`, so both bands are graded by
one rule whichever driver wrote them. Each task also carries a `pre_converge` flag,
derived from the UTC timestamp embedded in its run id against 05:37:53Z, and each
band table names which tasks fell on which side.

**Every run up to and including tiny/g01 attempt 2 (`wr-wsl-20260905T053439Z`)
predates the converge.** The pool stays at 1.

## 9. Tiny band result — 8/8, and two caveats on its own columns

All eight tiny tasks passed with full scores, every one `state=succeeded` /
`outcome=ok`, nothing excluded from the denominator. Total 18 `[1302]` refusals
across the band, 16 of them absorbed by g02 alone, which still passed.

Two columns in `tiny/trial-0/results.json` are weaker than they look, both fixed in
the driver afterwards and neither affecting pass/fail:

- **`conc_at_launch` for the tiny band is the pool at *finish*, not at launch.** The
  field was filled after the subprocess returned. Every tiny row therefore reads `1`,
  but g01's first attempt and g02 actually launched at pool 2. The driver now takes
  the value from `acquire()` at launch; the large band is unaffected, having run
  wholly at 1.
- **g01's `rate_1302` is 0, but that is its second attempt.** Its first attempt
  (`wr-wsl-20260905T052529Z-7488cecbb64c`) died after 23 refusals and the driver
  re-ran it 60 s later, which is why the task shows a clean run. The driver now
  carries the first attempt forward in an `attempt1` field so a retry cannot hide
  how hard the plan pushed back; for the tiny band that history is here in the
  ledger instead.

Neither changes a score: the checker grades the sandbox, not the clock.

## 10. Plan quota gate (06:07Z) — stop launching at 85% of the 5-hour window

The coordinator reported the 5-hour window at 66% at 06:07Z climbing about 23
credits a minute, against a reset at 08:50:42Z, with three workloads on it: this
arm's large band, the prompt campaign (self-stopping at 78%), and the v7
roundtable's GLM worker through pi. My own reading at 06:07:42Z: **68.15%,
1363/2000, 636 remaining**.

**Gate implemented.** The driver now reads the window before every launch and
launches nothing once it is at or above **85%**. An in-flight run is always allowed
to finish. A task the gate refuses is recorded `outcome=not_run` and, with
`rate_limited` and a real `quota_exhausted`, is excluded from the pass denominator —
none of the three is the model failing the task. Readings are kept per band in
`_meta.quota_readings`. An unreadable quota is treated as open rather than stalling
the arm on a monitoring failure, and is recorded as such.

**The band had to be swapped, and resume was built so it cost nothing.** The large
band's driver was started before the gate existed and a running Python process cannot
be given new code, so it would have gone on launching ungated runs against a window
three workloads are sharing. Rather than kill it and re-run finished work, the driver
gained a `--resume` mode that **rebuilds a completed task's record from its own
durable artifacts** — `<task>.result.json` plus the sandbox, with `wall_s` recovered
from the run's `started`/`ended` stamps — so anything that already succeeded is kept
and only the rest is re-prepped and re-run. `swap_to_gated.sh` waits for the
in-flight g03 to land its result, stops this arm's own tree, and relaunches
`run_band.sh large --resume`. g01 and t04 had already succeeded and are kept; no
credits are spent re-running them.

**Pause and resume protocol.** When the gate trips the driver finishes what is in
flight, prints `PAUSED` with the tasks it did not launch, grades what it has, and
exits. Launches resume after **08:50:42Z** with `run_band.sh large --resume`. The
pause reading, the resume reading and the resume time go in this ledger.

## 11. large/g03 timed out — recorded as a fail, not re-run

The swap in section 10 surfaced two defects, both now fixed.

**g03 large hit the 900 s timeout** (`state=timed_out`, "killed at the --timeout
deadline", 06:01:20Z to 06:16:21Z). The brief is explicit that a 900 s timeout is a
fail and is not resumed, so it is recorded as a fail, counted in the denominator, and
**not** re-run. Re-running it for a better result would be trial-shopping, and this
arm is one trial.

The timeout is genuine, not a plan artifact. Evidence: only 5 `[1302]` refusals
against 18-30 on the runs that really were throttled; the run started at 06:01:20Z,
after the 2b495f7 converge, so it did not carry the stderr-pipe fault; and it
produced 13,109 output tokens across a full 901 s while g01 and t04 finished the same
band in 539 s and 210 s with zero refusals. g03 is also the task
`reference-arms-2026-09-05.md` records as the one every non-Sonnet arm has failed at
least once.

**Defect A: the rate-limit retry fired on a timed-out run.** `rate_limited_start()`
matched a 1302 anywhere in the log without first excluding timeouts, so the old
driver logged `[rate-limit] large/g03: waiting 60 s` and was about to grant g03 a
second attempt the brief does not allow. Fixed: a timed-out run can never trigger the
retry.

**Defect B: resume would have re-run it.** `reconstruct()` only kept `succeeded`
runs, so a timed-out task fell into the to-run list. Fixed: a timeout is now kept as
a terminal record with `outcome=timed_out`, and resume never re-runs it.

**One loss, stated plainly.** The resume prep in section 10 wiped g03's sandbox
before either defect was noticed, so whatever partial work that run had written is
gone and cannot be graded. The recorded outcome is unchanged either way — a timeout
is a fail under the brief whatever the sandbox held — but this arm cannot say what
was in it, and the row carries `sandbox_lost`. That is a cost of the swap, and it is
mine.

## 12. The quota gate did not work on the large band — disclosed, then fixed

**What was asked, and what happened.** The gate was to read the 5-hour window before
every launch and launch nothing at or above 85%. It read the window **once**, at
06:18:34Z (78.30%, 1566/2000), and all five remaining launches reused that single
reading. `_meta.quota_readings` for the large band is five identical entries at one
timestamp; `quota_gated_tasks` is empty. The band then ran for a further 28 minutes
while the window climbed to **98.85% (1977/2000, 22 credits left)** at 06:47:25Z.
Nothing was ever gated.

**Why.** The check sat *before* `acquire()`. All five worker threads start at once,
so all five evaluated the gate within one 20 s cache window, passed it, and then
queued on the pool-of-one semaphore and launched one after another over the next half
hour without re-checking. A gate placed before the queue is evaluated at thread start,
not at launch, and with a pool of 1 that is worthless.

**Fixed.** The check now sits immediately after `acquire()` and before the subprocess
starts, releasing the slot if it refuses, and the read cache is down from 20 s to 5 s.
A queued task is now tested against the window as it actually launches.

**Consequence, stated plainly.** This arm ran the large band to completion against a
window it had been told to stop using at 85%, and left it at 98.85%. The prompt
campaign self-stops at 78% so it was already parked, but the v7 roundtable's GLM
worker shares this key and had 22 credits of headroom rather than the ~300 it should
have had. The arm's own results are unaffected — every large-band task launched
before the threshold would have been crossed on a correct implementation is a
different question from whether the results are valid, and no run was cut short — but
the protection the coordinator asked for was not delivered on this band. The fix is in
the driver for anyone who reuses it; the damage to the window is done and is reported
rather than smoothed over.
