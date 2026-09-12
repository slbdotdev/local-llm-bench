# The Z.ai unlimited-Flash campaign, tested on this plan

Manager: Opus 5 subagent for the 2026-09-06 control session, WSL, plan tier
`lite`. Research: Luna, `codex-run` run `wr-wsl-20260906T081629Z-417659155253`,
verified against the cited Z.ai pages by the session itself. Probes: `pi-run`
run `wr-wsl-20260906T081711Z-fce51ad44fd2` and `z-run` run
`wr-wsl-20260906T081844Z-bb2af259b479`.

## The claims as posted

A Z.ai employee (Lou, `@louszbd`) posted on 2026-09-03, quoting Zixuan Li
(`@ZixuanLi_`):

1. "We increased GLM-5.3-Flash usage for all coding plan users to unlock more
   workloads in ZCode, with unlimited usage from 8 AM to 6 PM PT."
   The quoted post reads "8 AM-6 PM PT every day, Sep 3-20".
2. "And we heard your feedback about usage limits in coding agents like Hermes
   and OpenClaw, so we doubled the standard Flash quota in other agents. The
   increased usage applies automatically."

## What Z.ai's own documents say

`https://docs.z.ai/devpack/notice/event-glm-5.3-flash`, fetched 2026-09-06
(the page states no publication date), read directly by the session:

- Campaign period "September 3, 2026 to September 20, 2026".
- "Every day from 23:00 to 09:00 the following day", "Singapore Time (UTC+8)".
  23:00 SGT is 15:00 UTC is 08:00 PDT; 09:00 SGT is 01:00 UTC is 18:00 PDT.
  The post's "8 AM to 6 PM PT" is therefore an accurate conversion.
- ZCode: "Zero quota consumption" for "unlimited usage". The mechanism is
  stated as *zero consumption*, which is directly observable on the quota
  endpoint rather than as an unmeasurable allowance.
- Other agents: available quota is "doubled" against standard plan quota.
- Exclusion: "if GLM-5.3 is selected, quota will still be consumed according
  to the standard rules". The campaign is GLM-5.3-Flash only.

`https://docs.z.ai/devpack/overview`, fetched 2026-09-06, read directly:

| tier | 5-hour credits | weekly credits |
| --- | --- | --- |
| Lite | 2,000 | 10,000 |
| Pro | 12,000 | 60,000 |
| Max | 28,000 | 140,000 |

"Model credit usage = (Input tokens x Input multiplier + Cached Input tokens x
Cached Input multiplier + Output tokens x Output multiplier) / 10,000", with
GLM-5.3-Flash at 2.3 input, 0.56 cached input, 8 output. The page publishes no
per-tier concurrency number.

`https://docs.z.ai/devpack/tool/others`, fetched 2026-09-06, read directly:
18 supported coding agents are listed, ZCode and **Pi** among them, plus three
general-purpose agents. The page offers three endpoints —
`https://api.z.ai/api/anthropic`, `https://api.z.ai/api/coding/paas/v4`,
`https://api.z.ai/api/v1` — and assigns none of them to a particular tool. So
**the endpoint is not the discriminator**: Z.ai publishes no rule by which a
request is recognised as coming from ZCode rather than from another agent.
Luna searched for one and reported NO SOURCE FOUND for a user agent, a header,
a model-name rule or an endpoint rule; the ZCode docs say only that a ZCode
client authorised against an account uses that account's plan and quota.

Luna additionally reports, unverified by the session: legacy V2 prompt quotas
(Lite ~80 prompts per 5 hours, ~400 per week), a Zixuan Li claim of an
8.2-billion-token weekly Flash limit for Max during the event, error 1313 as
the Fair Usage code, and that `https://api.z.ai/api/monitor/usage/quota/limit`
is undocumented in Z.ai's public API reference while Z.ai's own
`glm-plan-usage` plugin calls it. No source was found for a permanent quota
increase after 2026-09-20.

## This fleet's two arms hit the same endpoint

`skills/agent-runtime/scripts/agent-supervisor` pins
`ZcodeAdapter.ZCODE_BASE_URL = "https://api.z.ai/api/anthropic"` and
`PiPaths.ZAI_BASE_URL = "https://api.z.ai/api/anthropic"`, both
`anthropic-messages`, both taking `$ZAI_API_KEY`. `z-run` sends that provider
registry inline to ZCode's own `zcode.cjs` app-server. **The ZCode arm and the
pi arm are the same account, the same key, the same endpoint and the same API
shape**; the only differences are the runtime that speaks it, whatever client
identification that runtime sends of its own accord, and the model-id spelling
(`GLM-5.3-Flash` against `glm-5.3-flash`). If the campaign discriminates at
all, it must do so on something the ZCode runtime adds.

## Quota readings

Read with `python3 scripts/plan-usage.py` and with a helper that dumps the raw
`https://api.z.ai/api/monitor/usage/quota/limit` body (the script's own
`zai_key()` and `request_json()`; no key is ever printed). `plan-usage.py`
reports Z.ai as `plan_level`, `used_percent` and `resets_at` only, so the raw
body is needed for the cap: `currentValue` is credits used, `usage` is the
cap, `remaining` the balance, `unit` 3 the five-hour window and `unit` 6 the
week.

| reading | at (UTC) | 5h used | 5h cap | 5h % | weekly used | weekly cap | weekly % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pi-before | 2026-09-06T08:17:11Z | 96 | 2000 | 4 | 3984 | 10000 | 39 |
| pi-after | 2026-09-06T08:18:09Z | 97 | 2000 | 4 | 3985 | 10000 | 39 |
| z1-before | 2026-09-06T08:18:44Z | 97 | 2000 | 4 | 3985 | 10000 | 39 |
| z1-after | 2026-09-06T08:19:58Z | 98 | 2000 | 4 | 3986 | 10000 | 39 |
| settle-check | 2026-09-06T08:21:30Z | 98 | 2000 | 4 | 3986 | 10000 | 39 |

### The cap has not moved

`zcode-arm-2026-09-05.md` records cap 2000 on the five-hour window and 10000
on the week, taken on 2026-09-05. Today's readings are **2000 and 10000, the
same numbers**, and they are also exactly the Lite figures Z.ai still
publishes for the standard plan. Those are the only earlier Z.ai cap readings
anywhere in `org/`; no other page records one, and `plan-usage.py` keeps no
history. So on this account the campaign is **not** implemented as a doubled
cap on the quota endpoint. It is either implemented as halved consumption, or
not applied to this account or this route, or applied somewhere the endpoint
does not show.

## Probes outside the window

Both probes ran at about 01:17-01:20 PT on 2026-09-06, that is **outside** the
announced 08:00-18:00 PT window and outside the 23:00-09:00 SGT window, so
they are the campaign-off baseline. Identical task in both arms: a fixture
directory `C:\Users\slb\zai-probe` holding `data.csv` (six rows) and `task.md`
asking for the sum of the `count` column and the name of the largest row; the
prompt was "Read task.md in this directory and do exactly what it says."

```bash
bash ~/.claude/skills/pi-run/scripts/pi-run --cwd /mnt/c/Users/slb/zai-probe \
  --timeout 600 --idle 20 "Read task.md in this directory and do exactly what it says."
bash ~/.claude/skills/z-run/scripts/z-run --cwd /mnt/c/Users/slb/zai-probe \
  --timeout 600 --idle 20 -- "Read task.md in this directory and do exactly what it says."
```

| arm | wall | exit | answer | non-cached input | cached input | output | credits by the published formula | credits observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pi, GLM-5.3-Flash on the plan | 33 s | 0 | 125, bravo (correct) | 7,959 | 128 | 129 | 1.94 | **+1** |
| ZCode through `z-run` | 49 s | 0 | 125, bravo (correct) | 9,003 | 37,952 | 234 | 4.38 | **+1** |

Token counts are the harnesses' own: pi's from its session JSONL `message.usage`
records (three model requests), ZCode's from its `step-finish` events (three
model requests). Neither arm hit a 1302; `grep -c 'Rate limit'` on the ZCode
run log is 0.

Two things follow, and one does not. Outside the window, **ZCode traffic does
draw plan credits**, which agrees with `zcode-arm-2026-09-05.md`. A small
ordinary task costs about 1 credit in either arm, so the five-hour Lite window
of 2000 buys on the order of two thousand such tasks. What does *not* follow
is a clean per-run credit figure: the endpoint reports whole credits, the key
is shared with another manager's runs, and the observed +1 matches the
published formula for pi (1.94, or 0.97 if consumption really is halved) but
is four times under it for ZCode (4.38). Either the endpoint does not bill
ZCode's cached input the way the formula says, or it lags, or it rounds. This
page does not settle that.

## The load test inside the window

UNRUN AT THE TIME OF WRITING. The window opens at 09:00 MDT and this page was
written at 02:25 MDT, so the load test is launched detached
(`/tmp/zai-probe/loadtest.sh`) with a clock wait, the brief's 80% five-hour
gate before every probe, and a check of `agent-run list` for other managers'
running GLM runs before every probe; pools above two are skipped rather than
run while another manager's GLM run is live. It repeats the ZCode task three
times and the pi task three times, reading the quota around each, and then
probes ZCode concurrency at 2, 3 and 4. Its results belong in a dated addendum
to this page.

Recovery, for whichever session is resident when it lands. The script is
`/tmp/zai-probe/loadtest.sh`, its running log `/tmp/zai-probe/loadtest.log`,
and a second detached script, `/tmp/zai-probe/finish.sh`, waits on it, renders
`/tmp/zai-probe/addendum.md` through `/tmp/zai-probe/make-addendum.py`, copies
the whole scratch to `~/zai-probe`, and drops `/tmp/zai-probe/finish-complete.txt`
when it is done. Append that addendum to this page and commit it; the
verdicts table above is what it settles. WSL `/tmp` is boot-wiped, so if the
VM has restarted, `~/zai-probe` is the surviving copy and the load test did
not run.

## Verdicts

| claim | verdict | why |
| --- | --- | --- |
| 1. Unlimited GLM-5.3-Flash in ZCode, 08:00-18:00 PT, Sep 3-20 | **UNTESTED** | The vendor's own notice confirms the dates, hours and timezone, and states the mechanism as "zero quota consumption". Outside the window a small ZCode task cost 1 credit, which is the baseline the in-window run must beat. The window had not opened when this page was written. |
| 1a. The posted hours match the vendor's | **CONFIRMED** | Notice: 23:00-09:00 next day SGT, every day Sep 3-20. That is exactly 08:00-18:00 PT. |
| 1b. The offer covers GLM-5.3-Flash only | **CONFIRMED** | Notice: "if GLM-5.3 is selected, quota will still be consumed according to the standard rules". |
| 2. Doubled standard Flash quota in other agents | **REFUTED as a cap change on this account** | The Lite caps read 2000 / 10000 on 2026-09-06, identical to the 2026-09-05 reading in `zcode-arm-2026-09-05.md` and identical to the standard figures Z.ai still publishes. Nothing on the quota endpoint has doubled. Whether consumption is instead halved is UNTESTED: no pre-2026-09-03 per-task credit measurement exists anywhere in `org/`, so there is no baseline to halve against. |
| 2a. pi's route is covered by claim 2 | **UNTESTED** | Z.ai lists Pi as a supported tool and so an "other agent", but publishes no rule tying the campaign to a client or an endpoint, and this fleet's ZCode and pi arms use the *same* endpoint. |

## Recommendations, for the control session to decide

- **Routing.** Do not move GLM work to ZCode on the strength of the campaign
  until the in-window load test shows a zero credit delta. Outside the window
  the two arms cost the same, and ZCode is the slower of the two on a small
  task (49 s against 33 s), so the existing default — pi on the plan — needs
  no change today. If the in-window test does show zero, the rule worth
  writing is narrow: *between 09:00 and 19:00 MDT, GLM-5.3-Flash batch work
  goes to `z-run`; everything else stays on pi.*
- **Concurrency.** Leave the 2026-09-05 guidance in place (throttling above
  about two concurrent) until the concurrency probe reports. Nothing in the
  vendor's notice mentions concurrency, and its supported-agent language is
  best-effort.
- **The plan-usage gate.** `plan-usage.py` prints Z.ai percentages only. Every
  gate written against it therefore cannot see the cap, and cannot notice a
  cap change at all — which is exactly the fact this page had to go to the raw
  endpoint to establish. Worth considering: have `parse_zai` carry
  `currentValue`, `usage` and `remaining` through into the JSON output, so a
  future session can compare caps without a bespoke script. That is a change
  to a file this page's author may not edit, so it is a recommendation.
- **A gate reads the window once.** `zcode-arm-2026-09-05.md` records a large
  band running on to 98.85% because queued launches reused one reading. The
  load-test script here re-reads before every probe; any future GLM campaign
  work should do the same.
## Addendum: the load test inside the window, 2026-09-06

Window opened; reading at 2026-09-06T15:05:44+00:00: five-hour 287/2000 (14%), weekly 6181/10000 (61%).


### Repeated single tasks

| probe | arm | wall | exit | 5h before | 5h after | delta | weekly delta | answer correct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| za1 | ZCode | 42s | 0 | 287 | 287 | **+0** | +0 | yes |
| za2 | ZCode | 38s | 0 | 287 | 287 | **+0** | +0 | yes |
| za3 | ZCode | 34s | 0 | 287 | 287 | **+0** | +0 | yes |
| zp1 | pi | 31s | 0 | 287 | 287 | **+0** | +0 | yes |
| zp2 | pi | 32s | 0 | 287 | 288 | **+1** | +0 | yes |
| zp3 | pi | 28s | 0 | 288 | 288 | **+0** | +1 | yes |

### ZCode concurrency

| pool | wall | exit codes | 5h before | 5h after | delta | 1302 lines | answers correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 38s | 0 0 | 288 | 288 | **+0** | 0 | 2/2 |
| 3 | 51s | 0 0 0 | 288 | 288 | **+0** | 0 | 3/3 |
| 4 | 36s | 0 0 0 0 | 288 | 288 | **+0** | 0 | 4/4 |

End of load test, 2026-09-06T15:15:15+00:00: five-hour 288/2000 (14%), weekly 6182/10000 (61%).
Caps during the window: five-hour 2000, weekly 10000.

### Log

```
[2026-09-06T02:20:40-06:00] waiting for the window
[2026-09-06T09:05:43-06:00] window open; local 2026-09-06T09:05:43-06:00; PT 2026-09-06T08:05:43-07:00
[2026-09-06T09:05:44-06:00] gate za1: five-hour window at 14%
[2026-09-06T09:05:44-06:00] za1: 0 other GLM runs visible
[2026-09-06T09:06:52-06:00] za1: rc=0 wall=42s
[2026-09-06T09:06:52-06:00] gate za2: five-hour window at 14%
[2026-09-06T09:06:53-06:00] za2: 0 other GLM runs visible
[2026-09-06T09:07:57-06:00] za2: rc=0 wall=38s
[2026-09-06T09:07:57-06:00] gate za3: five-hour window at 14%
[2026-09-06T09:07:58-06:00] za3: 0 other GLM runs visible
[2026-09-06T09:08:57-06:00] za3: rc=0 wall=34s
[2026-09-06T09:08:58-06:00] gate zp1: five-hour window at 14%
[2026-09-06T09:08:58-06:00] zp1: 0 other GLM runs visible
[2026-09-06T09:09:56-06:00] zp1: rc=0 wall=31s
[2026-09-06T09:09:56-06:00] gate zp2: five-hour window at 14%
[2026-09-06T09:09:56-06:00] zp2: 0 other GLM runs visible
[2026-09-06T09:10:54-06:00] zp2: rc=0 wall=32s
[2026-09-06T09:10:54-06:00] gate zp3: five-hour window at 14%
[2026-09-06T09:10:55-06:00] zp3: 0 other GLM runs visible
[2026-09-06T09:11:49-06:00] zp3: rc=0 wall=28s
[2026-09-06T09:11:49-06:00] gate conc2: five-hour window at 14%
[2026-09-06T09:11:50-06:00] conc2: launching pool 2 (0 other GLM runs visible)
[2026-09-06T09:12:54-06:00] conc2: pool=2 rcs= 0 0 wall=38s
[2026-09-06T09:12:54-06:00] gate conc3: five-hour window at 14%
[2026-09-06T09:12:54-06:00] conc3: launching pool 3 (0 other GLM runs visible)
[2026-09-06T09:14:11-06:00] conc3: pool=3 rcs= 0 0 0 wall=51s
[2026-09-06T09:14:12-06:00] gate conc4: five-hour window at 14%
[2026-09-06T09:14:12-06:00] conc4: launching pool 4 (0 other GLM runs visible)
[2026-09-06T09:15:14-06:00] conc4: pool=4 rcs= 0 0 0 0 wall=36s
[2026-09-06T09:15:15-06:00] load test complete
```

### What the load test settles

Twelve ZCode runs inside the window — three sequential, then pools of 2, 3 and
4 — moved the five-hour counter by **0 credits** and the weekly counter by
**0 credits**, against **+1 credit** for the identical task in the identical
arm at 01:18 PT the same morning. No other manager's GLM run was live at any
point (`agent-run list` reported 0 before every probe), so the reading is
unshared. **Claim 1 is CONFIRMED**: "zero quota consumption" is literally what
the counter shows, and it is the ZCode arm that gets it even though `z-run`
sends its requests to `https://api.z.ai/api/anthropic`, the same endpoint pi
uses, with the same key. The discrimination is therefore made on something the
ZCode runtime itself sends, not on the route, the key or the account.

Three pi runs inside the window cost **+1 credit** in total (five-hour 287 to
288, weekly 6181 to 6182 — one credit, observed at two different polls), about
a third of a credit each, against +1 for one such run outside. That is *not* a
clean refutation of a halved-consumption reading of claim 2, but it is not
evidence for it either: the outside-window pi reading shared the key with
another manager's live pi run, and the published formula predicts 1.94 credits
for this task, so the endpoint's accounting does not track the published
formula in either direction. **Claim 2 stays REFUTED as a cap change** (caps
read 2000 and 10000 during the window too) and **UNTESTED as a consumption
change**, for want of a pre-2026-09-03 baseline.

**The concurrency finding is the surprise.** Pools of 2, 3 and 4 finished in
38 s, 51 s and 36 s — indistinguishable from a single run at 34-42 s — with
`grep -c 'Rate limit'` returning **0** across every run log and every task
answered correctly. On 2026-09-05 the same plan gave 68 rate-limit refusals
across the v5 arm and four concurrent runs finished nothing in nine minutes
(`zcode-arm-2026-09-05.md`). Two things differ besides the campaign, and both
matter: these tasks are tiny (one file read, about 40 s), and the key was not
shared with two other workloads. So this measures that **small concurrent
ZCode work is not throttled inside the window at pool 4**, not that the plan's
concurrency limit has been lifted for real work.

### Verdicts, revised by the load test

| claim | verdict | why |
| --- | --- | --- |
| 1. Unlimited GLM-5.3-Flash in ZCode, 08:00-18:00 PT, Sep 3-20 | **CONFIRMED** | 12 in-window ZCode runs, 0 credits on both windows; the same task cost 1 credit outside the window that morning. |
| 2. Doubled standard Flash quota in other agents | **REFUTED as a cap change; UNTESTED as a consumption change** | Caps read 2000 / 10000 before, during and after; no pre-campaign per-task baseline exists to test halved consumption against. |

### Recommendations, revised

- **Routing.** The in-window ZCode arm is free and unthrottled to pool 4 on
  small tasks. Worth adopting, narrowly: *between 09:00 and 19:00 MDT until
  2026-09-20, GLM-5.3-Flash work goes to `z-run` rather than `pi-run`.*
  Outside those hours the two arms cost the same and pi is faster
  (28-33 s against 34-49 s), so the default should not move wholesale.
- **Concurrency.** Do not raise the fleet's general guidance on the strength
  of this: the 2026-09-05 throttling was measured on real v5 tasks with a
  shared key. What is safe to write down is that *inside the window, small
  ZCode tasks run four-up with no 1302 and no wall-time penalty.*
- **The plan-usage gate.** Unchanged and now more pointed: a gate reading
  percentages alone would have shown 14% before and 14% after twelve free
  runs and learned nothing. Carrying `currentValue`, `usage` and `remaining`
  through `parse_zai` is what makes a zero-consumption claim checkable.
- **Expiry.** The campaign ends 2026-09-20. Any routing rule adopted from
  this page needs that date in it, or the fleet will still be routing to the
  slower arm in October.
