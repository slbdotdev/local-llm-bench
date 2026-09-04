# v5 benchmark plan, revision 5.5 (focused, adaptive)

Written 2026-09-03 by the control session after the owner stopped the local quant smoke.
Revised ~17:15 on owner notes: no fp8 through OpenRouter (too expensive), and a much tighter GPU
budget, so the GPU schedule is adaptive: critical probes first, every next run chosen from what
the real hardware and quants just showed. Rev 5.2 ~17:50 folds in Luna's adversarial review (`review-luna-rev5.1.md`): task-level verdict
rule, sentinel set against selection bias, GLM at throughput, g05 sized to the sweep, VRAM
residency recorded per trial. Supersedes the scope of `plan-2026-09-03.md` (rev 4). Rev 4 stays on disk as the reference for
harness details, the three-editor loop, fixture rules and risks; this file is the plan to execute.
Rev 5.3 (2026-09-03, owner ruling): **u04 is cut** — three Unity tasks, nine in the suite — with the
verdict arity in section 7 and the B0 trial count in section 8 following from it. The B0 probe quant
is still open, and section 5 now carries the gpu-tune finding that rev 5.2 predates.
Rev 5.4 (2026-09-03, owner rulings): the B0 probe is **IQ3_M at 32k**, followed by a **q8_0 KV
control**; IQ3_M is where the search starts and explicitly not the org's quality answer, so B1
gives Q3_K_M and Q2_K_L the full headline set instead of a sentinel subset; and **"is 2-bit
viable for any real work" becomes a verdict line of its own**. Sections 5 to 9 rewritten
against `results/gpu-tune/summary.md`. Q3_K_L dropped.
Rev 5.5 (2026-09-03, measured — not an owner ruling): today's direct 16k/24k KV probe
saturated its recall score and killed the asymmetric path on measured throughput, so q8_0
versus q4_0 stays open for the 64k variants; the rerun is specified in
`kv-probe-plan-2026-09-03.md`, which predicts on measured VRAM deltas that q8_0 does not fit
at 64k and that capacity, not quality, may settle it.
Status: plan only. Nothing here has been run.

## 1. Mission

Find out whether any real portion of the owner's work, Unity and general programming first, can be
offloaded to a local 27B model on the RTX 5080 (16 GB), and if so at which quant, at which context
window, and at what tokens and wall per solved task. The exploration is for the owner's curiosity,
so the deliverable is a clear ranking and a verdict, not a research programme.

## 2. What v4 taught us (do not repeat)

- v4 tasks need 40 to 50k output tokens even from fp8 and the frontier models pass under half.
  Every local trial hit the 1200 s wall: 0/4, 0/4, 0/4 across Q3_K_S medium, Q3_K_S low, Q2_K_L low.
  The wall censors everything, so quant quality was never measured.
- Local end-to-end throughput is 35 to 45 tok/s at 32k on a 13 to 15 GB quant. Cloud fp8 finishes
  the same appetite in about 12 minutes; the card cannot.
- Thinking level does not rescue it: low emits more tokens and scores lower.
- Contestants write their own tests, call them green and blame the spec. Graders must never use a
  contestant's tests as evidence.
- Three v4 task defects (52 rule 2 vs example list, 56 length sign, 56 stuck mutant) become
  selfcheck rules: execute every example list, state sign handling, bisect fixed-seed buckets.

## 3. Design rules

1. **Sonnet passes it or it is out.** Every task must pass 3/3 on Sonnet (free on subscription)
   and at least 2/3 on GLM 5.3 Flash (cents) before it enters the suite. No fp8 27B reference:
   OpenRouter pricing for it is out of proportion to the question. Tasks the reference models
   fail measure nothing about a quant.
2. **Small appetite.** Reference solution under 5k output tokens on Sonnet. Target wall on local
   under 300 s per trial. Timeout 900 s, and a timeout is a fail, recorded as such.
3. **Binary pass plus partial credit** from a hidden checker, exactly as v4. Contestant-authored
   tests never count.
4. **Trials are earned, not scheduled.** One trial first; three only where a single result would
   change a verdict. Report pass rate, median output tokens to pass, median wall to pass, and
   timeout count beside every mean, with the trial count.
5. **One model on the GPU at a time.** Hashes frozen once the suite is accepted.
6. **Every pi change bench-local** through `PI_CODING_AGENT_DIR` (Q8 = B stands). Nothing under
   `~/.pi` or deployed skill roots.
7. **Residency recorded per local trial, and never trusted on its own.** `ollama ps` processor
   split and `nvidia-smi` peak memory are logged with every trial; a trial with any CPU share is
   flagged offloaded and never counts toward a resident-context or concurrency claim. That is
   necessary and not sufficient: on Windows/WDDM an oversized allocation raises no OOM, it
   silently spills to system RAM while `/api/ps` still reports `100% GPU` and the log still says
   `offloaded 66/66`, while generation collapses to unusable speeds — see "the fit ceiling, and
   why 100% GPU can still be a lie" in `results/gpu-tune/summary.md`. So every local trial also
   records measured gen tok/s, and a trial whose throughput falls well below that quant's known
   resident curve is flagged **thrashing** whatever residency claims. Judge by tok/s, never by
   reported residency alone.
8. **Endpoint failures are not model failures.** Cloud rows record the serving provider and
   separate stalls and 5xx from wrong answers, as the GLM audit required.

## 4. The suite: nine tasks

Unity tasks run against the bench-C project (`D:\VRCA-Bench\projects\bench-C`).
**The mechanism is open — see `findings-2026-09-03-unity-harness.md` and section 9.** This line
previously cited "the batchmode compile loop from rev 4 section 8": rev 4 has no Unity content
at all, and no batchmode compile loop exists in the bench tooling. What exists is the
VRCA-Bench runner's live three-editor MCP loop, which `decisions.md:11` had already ruled is
how Unity gates. The checker column below is written against the batchmode claim and is
provisional until that is settled.
General tasks are plain Python or C# with a hidden checker.

| id | class | task | checker |
| --- | --- | --- | --- |
| u01 | Unity edit | Fix a null-reference in a MonoBehaviour given the stack trace; must compile | batchmode compile + play-mode test |
| u02 | Unity API | Implement a component using three named Unity APIs; no invented members | compile + reflection check of members used |
| u03 | Unity refactor | Move a serialized field into a ScriptableObject across three files | compile + asset reference check |
| g01 | single function | Implement a spec'd function from docstring and examples | hidden unit tests |
| g02 | bug fix | Fix a failing test in a 300-line module without breaking others | full test run |
| g03 | refactor | Mechanical rename and signature change across three modules | tests + grep for stragglers |
| g04 | lint loop | Drive a linter to zero on a provided file using the tool | linter exit code, diff size bound |
| g05 | doc ingest | Answer eight graded facts from a 12k-token document | rubric with accepted variants |
| g06 | tool protocol | Twenty sequential tool calls with strict argument formats | count of well-formed calls |

Weighting: u01 to u03 and g01 to g04 are the headline (seven tasks: three Unity, four general). g05 and g06 are diagnostic rows reported
separately, because they measure context use and harness reliability, not coding. g06 is graded
as the count of well-formed calls, never all-or-nothing. Discrimination check at gate time: a
headline task Haiku also passes 3/3 is kept but flagged saturated, and at most three saturated
tasks stay in the headline; replace the rest with harder variants.

Selfcheck before freezing: execute every example list in every prompt; each task authored by
Sonnet, checked by Haiku x3 for prompt defects, then gated by Sonnet 3/3 and GLM 2/3.

## 5. Arms

Four cloud and subscription reference rows, every one run on the full suite, three trials, so
the local ranking sits inside a real ladder rather than against a single bar.

| arm | where | purpose |
| --- | --- | --- |
| Sonnet | claude -p | gate and ceiling row, free on subscription |
| Haiku | claude -p | the bar the owner cares about beating, free on subscription |
| Luna (gpt-5.6-luna) | codex-run, effort high | the subscription adversarial reviewer; costs plan window, no dollars |
| GLM 5.3 Flash | pi, throughput routing, provider recorded, thinking high | the cheap cloud tier local must beat on something; throughput so a Relace stall never fails a gate |
| q27 IQ3_M first; then Q3_K_M and Q2_K_L on the full headline set, Q3_K_S on the sentinel set | local, thinking medium | the ranking |

### The local quants, re-measured

Every figure is from `results/gpu-tune/summary.md` (2026-09-03), fully resident at
`OLLAMA_KV_CACHE_TYPE=q4_0` with `num_gpu 66` forced. Those two levers only work combined and
are worth up to 2.3x: Ollama's scheduler parks 2-7 layers on the CPU while leaving ~600 MiB of
VRAM unused, and this model keeps KV for only **16 of its 66 layers**, so q4_0 halves an already
cheap cache and buys exactly the headroom the forcing needs. The live desktop setting is now
`OLLAMA_KV_CACHE_TYPE=q8_0`; the two exact 64k variants, `q27-IQ3_M-64k` and
`q27-Q3_K_S-64k`, were built assuming q4_0 and are the open capacity/quality conflict to
measure, not a reason to call q4_0 live.

| quant | max resident ctx | GB there | gen empty | gen near-full | prompt tok/s |
| --- | --- | --- | --- | --- | --- |
| Q2_K_L (2-bit) | 96k | 13.07 | 58.2 | 39.3 @94k | 1231 |
| IQ3_M | 64k | 14.11 | 52.8 | 41.0 @60k | 2039 |
| Q3_K_S | 64k | 13.70 | 53.5 | 41.4 @60k | 1495 |
| Q3_K_M | 48k | 14.16 | 51.3 | 42.5 @44k | 1648 |
| Q3_K_L | 24k | 14.25 | 47.1 | 45.0 @20k | 1747 |

### KV cache probe, 2026-09-03

The direct Q3_K_S probe at 16k and 24k scored **24/24** for both symmetric q8_0 and q4_0;
the 8k pass scored 24/24 only for its f16 first config and then hit three startup failures,
which are harness failures, not model findings. The 24k q8_0/q4_0 run never completed,
having been killed during recovery from the asymmetric hang. That recall is a ceiling, not
evidence that q4_0 is safe: the exact-match checksum needle could not discriminate. The raw records are [8k](kv-probe/kv-8k-Q3_K_S.json),
[16k](kv-probe/kv-16k-Q3_K_S.json), and [24k](kv-probe/kv-24k-Q3_K_S.json).

Asymmetric K/V is dead. Ollama cannot express it, and the direct runner measured 7.1 gen
tok/s and 18.3 prompt tok/s for q8_0/q4_0 at 16k despite normal 14422 MiB VRAM; the likely
fused flash-attention fallback is an inference, while the timings are measured. The q8_0
versus q4_0 choice therefore remains open pending the 64k run on `q27-IQ3_M-64k` and
`q27-Q3_K_S-64k`, planned in [the KV probe rerun plan](kv-probe-plan-2026-09-03.md).
External Qwen2.5-7B evidence points to most KLD damage being in K (same-top-p 11.6% for
q4_0/q4_0 versus 96.7% for q8_0/q4_0 and 98.0% for q8_0/q8_0), but that is a different
model and issue 21591 reports architecture-dependent effects; it does not settle this 27B.

On model bytes the study records IQ3_M at 12.95 GB against Q3_K_M's 13.60 — smaller *and*
longer-context, which is the whole reason it goes first. Configs above about **14.2 GB are
fair-weather**: they thrash when the desktop reclaims VRAM, which drifted 1.0 to 2.9 GB across
that session, and Q3_K_L @28k passed once then thrashed on an identical rerun. Every run in
section 6 is sized to stay under that line.

**Q3_K_L is dropped from v5.** Largest, slowest, caps at 24k, fair-weather at every context
worth using; nothing it could show would move a verdict line. Recorded as a decision, not an
omission. Q4 does not fit. fp8 is gone.

**IQ3_M is where the search starts, not what it concludes.** The owner is explicitly unconvinced
it is the right quality choice for the org, so it is given no privilege in section 6 beyond
going first: B1 runs Q3_K_M and Q2_K_L over the **full headline set** rather than a sentinel
subset derived from IQ3_M's own passes, precisely so IQ3_M's B0 result cannot quietly define
what the suite measures.
DeepSeek V4 Flash is not a v5 arm: its v4 column (9/21, USD 4.61, ~87k output tokens per trial)
bought two extra passes for five times GLM's cost, and v5's small-appetite tasks are exactly
where its appetite gives it nothing. It stays on the roster for on-demand throughput work.

## 6. Phases, adaptive

GPU time is the scarce resource. The control session keeps `results/v5/schedule.md`: the next
three GPU runs queued with a one-line reason each, rewritten after every result. The rule for
choosing the next run: prefer the run whose result could flip a verdict line in section 7; never
spend a trial confirming what two trials already showed.

**Phase A, author and gate (cloud and subscription only, about half a day, no GPU).** Nine tasks,
selfcheck, Sonnet 3/3 and GLM 2/3 gate, then the Haiku and Luna rows on the frozen suite, three
trials each. Any task Sonnet
fails is fixed or replaced. Freeze hashes. Output: a per-task table of Sonnet, Haiku, Luna and
GLM pass rate, output tokens and wall, which also sizes the local timeouts. Luna runs are free on the plan window (all use to date took 3% of a week), so they
run whenever convenient.

**Phase B0, critical probe (GPU, about 1 h).** `q27-IQ3_M` at **32k**, thinking medium, every
task, one trial. 32k rather than IQ3_M's full 64k because 32k is 13.39 GB with about 2 GB of
margin while 64k is 14.11 GB and fair-weather; B0 is the quality gate and Phase C is where
context is bought deliberately. Run the plain `q27-IQ3_M` with `num_ctx 32768, num_gpu 66`, not
the baked `q27-IQ3_M-64k`. This is the run that says whether the suite is in reach at all and
which tasks discriminate.

*Gate:* zero headline passes means one more pass at thinking low on the three tasks with the
highest partial score, then the same three on **Q3_K_M** — if the suite is out of reach the
question is whether more quality rescues it, not more speed, which is why the fallback is the
a-priori quality pick and not Q3_K_S. If all of that is still zero, stop and write the verdict
as **not viable on this suite**, with every untested quant named as untested rather than failed.
One or more passes means continue.

**Phase B0-control, KV precision (GPU, deferred to the 64k rerun).** Today's direct probe
settled asymmetric K/V as unusable but did not settle symmetric q8_0 versus q4_0: both scored
24/24 at 16k and 24k, which is a recall ceiling from an undiscriminating checksum probe.
The old 32k subset control is superseded by the four-cell 64k plan in
[the KV probe rerun plan](kv-probe-plan-2026-09-03.md), using the exact
`q27-IQ3_M-64k` and `q27-Q3_K_S-64k` variants. Keep the desktop at its current q8_0 setting
outside the direct per-server test; do not leave a q4_0 experiment's environment change
unrecorded.

**Phase B1, quant differentiation and the 2-bit question (GPU, 2 to 3 h).** Two shapes, because
two different questions are being asked.

- **Full headline set, one trial each: Q3_K_M and Q2_K_L** (seven tasks, about 35 min per
  quant). Q3_K_M because it is the a-priori quality challenger the owner is not ready to
  discard, and the full set is what stops IQ3_M's B0 result defining the suite. Q2_K_L because
  **"is 2-bit viable for any real work" is a verdict line in its own right**, and a sentinel
  subset chosen from a 3-bit quant's passes cannot answer it.
- **Sentinel set only: Q3_K_S.** The tasks IQ3_M passed or scored 0.5 or better on, plus one
  zero-score B0 task per class so nothing silently disappears. Q3_K_S sits between IQ3_M and
  Q2_K_L on both quality and bytes and adds the least new information, so it earns the cheap
  shape.

Then a second and third trial only where a quant disagreed with IQ3_M on a task. A quant that
fails a task IQ3_M passed cleanly, twice, is dropped from that task. Output: pass rate and
tokens to pass per quant on the tasks that can tell them apart, plus the 2-bit verdict line.

*Optional, owner's call, not scheduled:* if Q2_K_L lands marginal rather than clearly dead,
**IQ2_M** is the single run most likely to flip 2-bit from marginal to viable — IQ3_M showed
imatrix carries no dequant penalty at 3-bit, so the same plausibly holds a bit lower. It costs a
~12 GB pull against 68 GB free. Raise it as a decision when the Q2_K_L result is in, never
before.

**Phase B2, confirm the winner (GPU, about 1.5 h).** Best quant from B1 **on the evidence, not
by seniority** — IQ3_M has no claim here beyond having gone first — three trials on every
headline task it has fewer than three trials on. This is the headline row.

**Phase C, context sweep (GPU, about 1.5 h).** Winner on the discriminating tasks at **16k, 32k
and 48k**, one trial each, three on g05 (a 12k document, so it fits from the 16k step up). A 64k
row only where that config stays under 14.2 GB — IQ3_M's 64k is 14.11 and fair-weather, so if
IQ3_M wins, its 64k row is taken only in the low-VRAM regime and labelled as such. 8k only if
16k holds within five points of 32k, and g05 is excluded at 8k. Residency is judged by rule 7:
measured tok/s first, reported residency second. Output: the smallest window at which the
headline pass rate holds, which is the usable context number for the final configuration.

**Phase D, concurrency probe (GPU, about 1 h).** Winner at the Phase C window, llama-server with
two parallel slots, g01 to g04 concurrently, one trial each. Four slots only if two held the
single-stream pass rate and KV fits. This model is unusually friendly to it — KV for 16 of 66
layers at q4_0 is roughly 544 MiB per 32k — so slot count is bounded by model bytes, not by
cache. **If 2-bit proves viable in B1, Q2_K_L is the natural concurrency candidate whatever won
B2**: it is the smallest and fastest of the set, and concurrency is exactly where its spare
gigabytes convert into slots. Report aggregate tok/s, per-stream tok/s and pass rate against the
single-stream row, and say which quant the concurrency row was taken on.

## 7. Verdict rule

Predeclared, task-level, because a class has only three or four headline tasks and a percentage
gap would be all-or-nothing. A task is **solved** by a quant when two of three trials pass under
the 900 s wall. A class is **viable** when the best quant solves three quarters of its headline
tasks at the Phase C window, rounded up, and **marginal** at half, rounded up — so **general
(four tasks) is viable at three and marginal at two, and Unity (three tasks, u04 cut) is viable
at three and marginal at two**. Below marginal is **not viable**. Requiring 3/3 for Unity is
deliberate: with three tasks a 2-of-3 bar would let one task carry a whole class. Raw
per-task pass rates with trial counts are printed beside every verdict line, and wall to pass is
reported over solved tasks only and labelled as such. Beating GLM on tokens to pass or wall is
reported but never required. Report one line per
class: viable, marginal, not viable. Beating Haiku on the headline is the headline sentence.

**The 2-bit line is a verdict of its own**, asked for by the owner and reported whatever the
ranking says. It answers "is 2-bit viable for any real work" directly: whether Q2_K_L solves any
headline task at all, which class it does best in, and the same viable / marginal / not-viable
word under the same arity rule — stated beside its context reach, because 96k fully resident is
a capability no other quant on this card has. "Not viable for coding, and the only 96k option on
this hardware" is a real and reportable outcome, not a failure to report. If Q2_K_L solves
nothing, the line says so plainly and names what it was tested on.

## 8. Budget

Cloud: about 30 GLM trials in Phase A, expected under USD 2 at v4 rates. Sonnet, Haiku and Luna
are subscription and unrestricted. GPU: about 9 trials in B0 plus 3 in the q8_0 control, 25 to 35
in B1 (14 of them the two full-headline passes), 20 in B2, 14 in C, 8 in D, at about 5 minutes
each — roughly 6.5 to 8 hours, spread over the schedule file rather than run as a block. Every
phase after B0 can be cut short by its gate, and the B1 full-headline passes are the one place
the plan deliberately spends trials on breadth rather than confirmation.

## 9. Open questions for the owner

**One, reopened 2026-09-03 by the control session on restart: the Unity harness for u01 to u03.**
The plan's section 4 described a batchmode compile loop that does not exist anywhere in the
tooling, citing a rev 4 section that has no Unity content. What exists is the VRCA-Bench runner's
live three-editor MCP loop against `D:\VRCA-Bench\projects\bench-C`, which `decisions.md:11`
already named as the Unity gate. The three options — adopt the live-editor loop, build a real
batchmode checker, or cut the Unity class — and the pi editor-selection limit that makes the
three-editor parallelism unavailable to the local arms are in
`findings-2026-09-03-unity-harness.md`. It blocks authoring u01 to u03 and nothing else; g01 to
g06 are unaffected.

Every question rev 5.2 carried is closed below, and authoring otherwise waits only on the
owner's go-ahead.

Two things stay flagged as decisions the plan will bring back rather than take on its own: the
**IQ2_M pull** (Phase B1, only if Q2_K_L lands marginal) and the **q8_0 versus q4_0 KV choice**,
which awaits the 64k rerun in [the KV probe plan](kv-probe-plan-2026-09-03.md) rather than the
saturated 16k/24k checksum result.

### Closed since rev 5.2

- **Thinking level for local arms** — never actually open. Ruling Q11c pins the 27B at medium,
  section 2 records that low emits more tokens and scores lower, and B0's own gate already
  falls back to low. Struck.
- **u04 (EditMode tests)** — **cut by the owner, 2026-09-03.** Three Unity tasks stand, and the
  EditMode test-runner fixture leaves Phase A with it.
- **B0 probe quant** — **IQ3_M, at 32k, decided by the owner 2026-09-03**, with the standing
  qualification that this is where the search *starts* and not the org's quality answer: the
  owner is unconvinced on quality grounds, so B1 explores the space around it rather than
  confirming it. Rev 5.2's Q3_K_M recommendation predated `results/gpu-tune/summary.md` and was
  withdrawn.
- **q8_0 KV control** — **yes, ordered by the owner 2026-09-03.** Phase B0-control.
- **The 2-bit question** — raised by the owner 2026-09-03: is 2-bit viable at all for any real
  work. Now a verdict line in section 7, a full-headline pass for Q2_K_L in B1, and the
  concurrency candidate in Phase D.
