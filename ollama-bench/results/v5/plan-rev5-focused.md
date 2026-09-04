# v5 benchmark plan, revision 5.9 (focused, adaptive)

Written 2026-09-03 by the control session after the owner stopped the local quant smoke.
Revised ~17:15 on owner notes: no fp8 through OpenRouter (too expensive), and a much tighter GPU
budget, so the GPU schedule is adaptive: critical probes first, every next run chosen from what
the real hardware and quants just showed. Rev 5.2 ~17:50 folds in Luna's adversarial review (`review-luna-rev5.1.md`): task-level verdict
rule, sentinel set against selection bias, GLM at throughput, g05 sized to the sweep, VRAM
residency recorded per trial. Supersedes the scope of `plan-2026-09-03.md` (rev 4). Rev 4 stays on disk as the reference for
harness details, the three-editor loop, fixture rules and risks; this file is the plan to execute.
Rev 5.3 (2026-09-03, owner ruling): **u04 is cut** — three Unity tasks, nine in the suite — with the
verdict arity in section 7 and the first probe's trial count in section 8 following from it.
The first probe's quant is still open, and section 5 now carries the gpu-tune finding that rev 5.2 predates.
Rev 5.4 (2026-09-03, owner rulings): the first probe is **IQ3_M at 32k**, followed by a **q8_0 KV
control**; IQ3_M is where the search starts and explicitly not the org's quality answer, so
differentiation gives Q3_K_M and Q2_K_L the full core set instead of a sentinel subset; and
**"is 2-bit viable for any real work" becomes a verdict line of its own**. Sections 5 to 9 rewritten
against `results/gpu-tune/summary.md`. Q3_K_L dropped.
Rev 5.5 (2026-09-03, measured — not an owner ruling): today's direct 16k/24k KV probe
saturated its recall score and killed the asymmetric path on measured throughput, so q8_0
versus q4_0 stays open for the 64k variants; the rerun is specified in
`kv-probe-plan-2026-09-03.md`, which predicts on measured VRAM deltas that q8_0 does not fit
at 64k and that capacity, not quality, may settle it.
Rev 5.6 (2026-09-03, owner rulings): Unity uses the VRCA-Bench live-editor MCP loop; every
differentiation path supplies three trials; and Q3_K_L's 24k figure is its reliable limit, not a hard cap.
Rev 5.7 (2026-09-04, owner rulings): **authoring becomes a managed overnight authoring session.**
Luna authors; an Opus manager subagent runs the loop and holds the judgment; Sonnet and GLM
gate only and neither is a scored row; authoring now uses the GPU, for calibration and never for
selection (section 4a). Codex gains the Unity and Blender MCP servers through ansible. Written
against the worker runtime in `ansible-slb/org/worker-runtime-plan-2026-09-03.md`, which the
manager uses and which must be converged and acceptance-tested first. (The MCP change to Codex
stands as a fleet change on the owner's ruling; rev 5.8 removed its v5 rationale by cutting the
Unity class, so it is no longer a precondition for this plan.)
Also rev 5.7, on the owner's ruling: **phase names are gone** — this is one plan with an order,
not six numbered stages — the seven weighted tasks are the **core set** rather than the
"headline", and the language that pre-committed the report to a conclusion has been removed.
**No third reference row**; Fable is ruled out, so Sonnet as ceiling and Haiku as the one
comparison is the accepted shape, and section 7 says plainly what that costs.
Rev 5.8 (2026-09-04, owner rulings, after a measurement): **the Unity class is cut and MCP is
out of scope for local models entirely.** Measured on the desktop: pi's Unity MCP surface is
28,492 tokens of tool schemas across 47 tools, 31,592 with the builtins and system prompt, on a
card where an open editor already takes ~4 GB and leaves 11.9 GB free. No quant can hold that
floor plus a task. Agentic Unity work is therefore **out of reach for a 27B on this hardware by
capacity, not by quality**, and that is a result, recorded in section 9 rather than left as an
open question. What replaces it: the suite becomes short-context work the owner would actually
delegate, with **no MCP on any arm**; the axis of interest becomes **quality against context
from 24k to 64k**; the **confidently-wrong rate is a first-class verdict line**; and the
concurrency probe is dropped. Target context is **32k minimum** — enough to read several things
and think — which excludes Q3_K_L on its 24k reliable limit.
Rev 5.9 (2026-09-04, owner rulings, after the worker runtime's acceptance test): the plan is
**unchanged in scope** and is now cleared to run. Three things are recorded rather than changed.
**(a) The precondition is met.** The worker runtime was acceptance-tested with a real `codex-run`
and a real `pi-run`; it found three defects, all fixed and verified, one of which was that live
messaging to a Codex worker had never worked at all
(`ansible-slb/org/worker-runtime-acceptance-2026-09-04.md`). **(b) The manager starts from a
handoff in a fresh session**, not as a subagent spawned mid-session by the session that wrote
this — an overnight run should not inherit a control session's spent context, and a handoff is
re-readable after a restart where a spawn is not. **(c) The owner's restatement of the mission is
recorded in section 1a**, with the one place it differs from this plan called out, because that
difference is the plan's central guardrail and a manager reading only the restatement would
breach it.
Also rev 5.9, a standing rule for everything below: **this plan removes items from
`ansible-slb/org/pending.md` as they are finished and never adds one.** An issue found on the way
is written to a dated findings page, not parked as a new pending item.

Status: plan only. Nothing here has been run.

## 1. Mission

Find out whether any real portion of the owner's work can be offloaded to a local 27B model on
the RTX 5080 (16 GB), and if so at which quant, at which context window, and at what tokens and
wall per solved task. The exploration is for the owner's curiosity, so the deliverable is a
clear ranking and a verdict, not a research programme.

**Rev 5.8 narrows this to the question that is still open.** Unity is answered and the answer is
no, on capacity (section 9). What remains is short-context work the owner would otherwise hand
to a paid worker: reading a few files and answering something specific, mechanical
transformations, verification. The realistic role being tested is **the worker that still exists
when the ChatGPT window is exhausted and weekly-all is spent** — its value is not cost, since
Luna is off weekly-all and GLM is cents, but that it has no window to run out of and nothing
leaves the machine. The measurement runs on an **idle GPU**: the owner's Unity work and a
resident quant cannot share this card, and the owner's other work mostly is not Unity.

## 1a. The mission as the owner restated it, 2026-09-04

Recorded in the owner's own framing, because it is shorter than section 1 and a manager will
work from it:

> A benchmark for the optimal quantization and KV settings for the work the model might actually
> be good at here, with quant driving available context, and data gathered on performance on the
> tests, on whether capability grows with context, and on whether the quants needed to achieve
> longer context windows destroy model performance too much. The manager has free rein to spot
> test, iterate and trial things, to spend GPU time on the most meaningful runs first. The tests
> will be developed over time as we learn what the model can and can't do.

That is this plan, with three clarifications. Two are wording; the third is the guardrail.

- **KV is pinned, not optimized.** Quant is the axis being searched. The whole grid runs at
  `q4_0` and states its results as conditional on it; the `q8_0` versus `q4_0` question is
  settled separately by the 64k rerun in `kv-probe-plan-2026-09-03.md`, on capacity as much as
  quality. So the deliverable is an optimal quant *at a stated KV setting*, plus a separate
  answer on the cache.
- **The context axis measures holding, not growing.** More context means more material can be
  handed over in one go; it is not expected to make the model better. What is measured is where
  quality *stops* holding as the window fills — and section 7 expects that to show up first as
  fabrication rather than as refusal, which is why the confidently-wrong rate is a verdict line
  of its own.
- **Tests are developed during authoring, and never in response to what the quant can do.** This
  is section 4a and it is the one place the restatement, read literally, would break the
  benchmark. Tasks are authored, calibrated for *fit* (window, appetite, wall, checker), and
  gated on Sonnet 3/3 and GLM 2/3 — all before any scored row runs. Learning what the local model
  can and cannot do is the **result**, not an input: a task is never kept, dropped, reworded or
  reordered because a quant passed or failed it. A suite tuned against the contestant reports
  the tuning back and measures nothing.

The manager's free rein is real and it is bounded by exactly that: it chooses what to run next
and in what order (section 6), and it does not let a quant's result decide what the suite
contains.

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
   fail measure nothing about a quant. **A model that gates does not score.** A gate drops or
   rewrites the tasks it fails, so a gate model's own pass rate is a floor it was handed by
   construction, not a measurement. Sonnet is the exception and only as a declared ceiling, where
   ~100% is the point; its number is never a competitive comparison. GLM gates and is not a row.
2. **Small appetite.** Reference solution under 5k output tokens on Sonnet. Target wall on local
   under 300 s per trial. Timeout 900 s, and a timeout is a fail, recorded as such.
3. **Binary pass plus partial credit** from a hidden checker, exactly as v4. Contestant-authored
   tests never count.
4. **Verdict inputs get three trials.** Every task on every differentiation path is run for
   three trials because differentiation feeds section 7; one trial is permitted only for an
   exploratory probe that is not used as a section 7 verdict. Additional trials beyond a
   required three are earned only where a single result would change a verdict. Report pass
   rate, median output tokens to pass, median wall to pass, and timeout count beside every mean,
   with the trial count.
5. **One model on the GPU at a time.**
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
9. **The author does not compete.** Luna authors the suite (rev 5.7) and therefore takes no
   scored row: a task is phrased in idioms its author finds natural, and a score on it stops
   measuring capability. No GPT-family row is taken for the same reason while Luna is the author.

## 4. The suite: eight tasks, no MCP

Every task is plain Python or C# against a hidden checker, run through the harness with **no MCP
server on any arm** (rev 5.8). The Unity class is gone with it; the capacity finding that removed
it is in section 9. The floor is therefore pi's system prompt plus AGENTS.md, about 2k tokens,
which is what makes a 24k-to-64k context sweep meaningful at all.

Two classes, four tasks each. **Transformation** is mechanical work with a right answer.
**Comprehension** is reading and judging, which is the half that actually models delegation —
and it is where the traps live.

| id | class | task | checker |
| --- | --- | --- | --- |
| g01 | transformation | Implement a spec'd function from docstring and examples | hidden unit tests |
| g02 | transformation | Fix a failing test in a 300-line module without breaking others | full test run |
| g03 | transformation | Mechanical rename and signature change across three modules | tests + grep for stragglers |
| g04 | transformation | Drive a linter to zero on a provided file using the tool | linter exit code, diff size bound |
| t01 | comprehension | Sweep a doc set for references to a moved path and classify each as a live pointer to fix or correct history to leave | per-reference confusion matrix; **trap** |
| t02 | comprehension | Say whether a function does what its docstring claims | binary plus the cited line; **trap in half the variants** |
| t03 | comprehension | Extract eight graded facts from a 12k-token document into JSON | rubric with accepted variants |
| t04 | comprehension | Locate where a behaviour is implemented across a tree and explain it | cited path and span; **trap variant where it is absent** |

**Traps are load-bearing, not decoration.** A confidently-wrong rate cannot be measured on tasks
whose plausible answer is the correct one, so at least half the comprehension variants have a
correct answer that is negative: nothing found, claim false, leave it alone. t01 is taken from
life — a real sweep for a moved path on 2026-09-04 found four references, of which **two were
correct history that fixing would have damaged**. A model that rewrites all four looks
productive and is wrong, and no pass/fail score distinguishes it from one that rewrites none.

All eight are the core set: with MCP gone there is no diagnostic/coding split left to make, and
t03 earns its place on the context axis rather than beside it. Discrimination check at gate
time: a task Haiku also passes 3/3 is kept but flagged saturated, and at most three saturated
tasks stay in the set; replace the rest with harder variants.

Selfcheck on every candidate: execute every example list in every prompt; each task **authored by
Luna** (rev 5.7, several candidates per task, the manager picking), checked by Haiku x3 for
prompt defects, then gated by Sonnet 3/3 and GLM 2/3.

## 4a. Calibration is not selection

authoring now runs the GPU, which is new in rev 5.7 and is the sharpest hazard in this plan.
Feeding a contestant's results back into the suite it will be scored on is how a benchmark
quietly stops measuring anything. The line, and the manager holds it:

- **Calibration, allowed.** Use local runs to size a task: does it fit the context window, does
  a reference solution land under the 5k-token appetite, does a trial finish inside 300 s, is
  the prompt unambiguous to a small model, does the checker fire correctly on a real transcript.
  These are properties of the *task*, and rule 2 cannot be satisfied without measuring them.
- **Selection, forbidden.** Never keep, drop, reword or reorder a task because of whether a
  local quant **passed** it. Difficulty is the thing being measured; tuning it against the
  contestant makes the grid report the tuning back. A task the quant fails cleanly is a
  perfectly good task, and may well be the most informative one in the suite.

If a task cannot be calibrated without knowing whether the quant passed, it is the wrong task;
say so and author another. The manager records, per task, which local runs informed it and
which property they settled, so the record can be audited rather than trusted.

## 5. Arms

**Two scored reference rows** (rev 5.7, down from four), run on the full suite at three trials,
plus two arms that shape the suite without being scored on it. The ladder is shorter than rev
5.6's deliberately: every model that authors or gates has been removed from the scoring, because
a row a model handed itself measures the construction and not the model.

| arm | where | scored? | purpose |
| --- | --- | --- | --- |
| Sonnet | claude -p | **ceiling row only** | gate at 3/3, and a declared ceiling where ~100% is the point. Never quoted as a competitive comparison. |
| Haiku | claude -p | **yes** | the nearest cloud comparison, free on subscription. Read section 7's caveat before quoting it. |
| GLM 5.3 Flash | pi, thinking high, provider recorded | **no — gate only** | gate at 2/3, and the cheap-cloud sanity check that a task is solvable off the frontier. Its gate pass rate is reported as gate evidence, never as a row. |
| Luna (gpt-5.6-luna) | codex-run, effort high | **no — author** | authors the suite; see rule 9. |
| q27 Q2_K_L, Q3_K_S, IQ3_M, Q3_K_M across the 24k-64k grid | local, thinking medium, `q4_0` KV, `num_gpu 66` | yes | the ranking. Q3_K_L is excluded by the 32k floor |

GLM's routing is chosen per run rather than left at the default: take whichever of `pi-run`'s
four preferences — `price`, `balanced`, `throughput`, `latency` — is the best trade at the time,
reading the live endpoint spread with `or-price z-ai/glm-5.3-flash`, and record which endpoint
actually served every gate run. No named provider is pinned; the sort is the only lever, which
keeps this a per-run flag rather than an ansible change. The managed `max_price` ceiling applies
whichever preference is used and is not to be lifted for this.

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
| Q3_K_L | 24k (reliable) | 14.25 | 47.1 | 45.0 @20k | 1747 |

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

**Q3_K_L is dropped from v5.** Largest and slowest, with a **24k reliable operating limit rather
than a hard cap** ([tuning summary](../gpu-tune/summary.md)): it succeeded once at 28k, but that
configuration thrashed on an identical rerun. It is fair-weather at every context worth using;
nothing it could show would move a verdict line. Recorded as a decision, not an omission. Q4 does
not fit. fp8 is gone.

**IQ3_M gets no privilege.** The owner is explicitly unconvinced it is the right quality choice
for the org, and rev 5.8 removes the last structural reason it might have got one: there is no
first probe any more and no sentinel set derived from its passes. Every quant runs the same
eight tasks at the same context steps, so no single quant's result can quietly define what the
suite measures.
DeepSeek V4 Flash is not a v5 arm: its v4 column (9/21, USD 4.61, ~87k output tokens per trial)
bought two extra passes for five times GLM's cost, and v5's small-appetite tasks are exactly
where its appetite gives it nothing. It stays on the roster for on-demand throughput work.

## 6. Run order, adaptive

GPU time is the scarce resource. The control session keeps `results/v5/schedule.md`: the next
three GPU runs queued with a one-line reason each, rewritten after every result. The rule for
choosing the next run: prefer the run whose result could flip a verdict line in section 7; outside
the mandatory three-trial differentiation paths, never spend an optional trial confirming what
two trials already
showed.

**Authoring and gating — a managed overnight session (rev 5.7). Goal 8 h, hard limit 12 h.**

One **Opus manager subagent** runs it and holds the judgment — this is a deliberate, scoped
exception to the fleet rule that a control session invokes `codex-run` itself. The manager
briefs and reads its own workers. It is not a dispatcher: picking among candidate tasks, reading
a failed calibration run and deciding what it means, and knowing when a task is wrong rather
than hard are the whole job, and they are why an Opus sits there rather than a script.

The loop, run against the worker runtime so authoring and calibration overlap:

0. **Send one Luna run off for inspiration first** (owner's ruling, rev 5.9, and explicitly low
   priority). Web search is on by default: ask what published or open-source evaluations suit
   *this narrow scope* — small local quants, long-context degradation, fabrication under context
   pressure, short mechanical-transformation and read-and-judge tasks with hidden checkers. Ask
   for a shortlist with what each would contribute and what disqualifies it, not summaries. Read
   it whenever it lands. It is inspiration and never authority: nothing it returns overrides
   section 4a, the gate rules, or the trap requirement in section 4.
1. **Author in parallel.** Several concurrent Luna runs per task, several candidates each; the
   manager picks. Luna is off weekly-all entirely and has banked resets, so breadth here is
   close to free — prefer more candidates over fewer.
2. **Mechanical selfcheck**, needing no model: execute every example list in every prompt.
3. **Calibrate on the GPU** under section 4a, one model on the card at a time. Sizing only.
4. **Gate**: Haiku x3 for prompt defects, then Sonnet 3/3 and GLM 2/3. A task Sonnet fails is
   fixed or replaced, and that is a *task* defect, never evidence about a quant.
5. Refine and repeat. GLM may be used sparingly inside the loop as a second reader.

Standing rules for an unattended run:

- **The GPU must be idle, not merely serial.** Parallel Luna authoring never assumes the card;
  GPU work is queued, one model at a time, and the watchdog's `models=0` alert during a direct
  sweep is a known false positive rather than a fault to chase. Beyond that, rev 5.8 requires an
  **idle** card: one open Unity editor takes ~4 GB and leaves 11.9 GB free, which is less than
  every quant under test needs. Close the editors before any local trial, and treat a trial taken
  with one open as void rather than merely suspect.

- **Bank, do not block.** An ambiguous call is written to the decision log and the manager
  carries on with everything that does not depend on it. It never blocks waiting on a human, and
  it never takes a structural decision alone — dropping a task class, moving a verdict arity, or
  changing what a class measures all get banked, not decided.
- **Stop conditions.** 8 h is the goal and 12 h the hard limit; stop early on repeated harness
  failure rather than burning the window retrying a wedged card.
- **A scored row is void if its task changed under it.** Record the task revision every scored
  row — reference or local — was measured against, and never carry a row forward across an edit
  to its own task.

Output, and it has to survive a session restart: the candidate suite, a per-task decision log
recording which local runs informed which property, the banked questions, and a per-task table
of Sonnet and Haiku pass rate, output tokens and wall, which also sizes the local timeouts.
GLM's gate results are recorded beside it, labelled as gate evidence.

**Precondition — the runtime half is met (rev 5.9); the harness half is not.** The manager uses
the worker runtime (`ansible-slb/org/worker-runtime-plan-2026-09-03.md`) for background runs and
live messaging. That runtime has now been acceptance-tested with a real `codex-run` and a real
`pi-run`, which found and fixed three defects — including that `agent-msg` to a Codex run had
never once delivered, because the resume was invoked with two flags `codex exec resume` does not
accept. Evidence and the fixes: `ansible-slb/org/worker-runtime-acceptance-2026-09-04.md`. Take
that page's method with you: give a worker a task whose answer you can compute independently, and
size the task to the race you are testing.
**Still owed before the first GPU trial:** the KV probe harness faults in `kv-probe-plan-2026-09-03.md`
are fixed and supervised first. An unattended overnight loop is the worst possible consumer of a
harness that turns a teardown failure into three indistinguishable `server did not become
healthy` errors. Fixing them clears that item out of `org/pending.md` in the same commit.

**The quality-versus-context grid (GPU, the bulk of the run).** This replaces the first probe,
differentiation, the context sweep and the concurrency probe, all of which existed to find a
context/quality frontier under an MCP floor that no longer applies. One question now: **how does
each quant's quality hold up as its context fills, from 24k to 64k?**

The capacity map is ragged, so it is fifteen cells rather than a clean grid. Every figure is from
`results/gpu-tune/summary.md` at `q4_0` KV with `num_gpu 66` forced:

| quant | 24k | 32k | 48k | 64k |
| --- | --- | --- | --- | --- |
| Q2_K_L | yes | yes | yes | yes, 13.07 GB at 96k so comfortable throughout |
| Q3_K_S | yes | yes | yes | yes, 13.70 GB |
| IQ3_M | yes | yes | yes | 14.11 GB — fair-weather, flag every trial |
| Q3_K_M | yes | yes | 14.16 GB, fair-weather | no |
| Q3_K_L | 24k only | — | — | excluded by the 32k floor |

**The context must actually be occupied.** `num_ctx 64k` allocates the KV up front, but a short
prompt still only uses a few thousand tokens, so a "64k" trial on a short prompt measures
nothing about 64k. Each task is therefore embedded in realistic-but-irrelevant filler — other
source files, other documents — to the cell's size. The material needed to answer is present and
must be found *and* used, which is what the 2026-09-03 KV probe could not test: an exact-match
checksum needle is binary and saturated at 24/24, so it had no resolution to show degradation.

Order: **one trial per task across all fifteen cells first**, to find where the curve bends;
then three-trial passes only on the cells at and around the bend. A uniform three-trial grid
would consume the whole night and spend most of it confirming the flat parts.

*Gate:* if no quant solves anything at 24k, stop and write the verdict as **not viable on this
suite**, naming every untested quant as untested rather than failed.

**KV precision rides along.** Every cell above is at `q4_0`, and the desktop's live setting is
`q8_0`, which is predicted not to fit at 64k at all. The grid therefore pins `q4_0` explicitly,
carries the documented revert (env var back to `q8_0`, restart Ollama) and states its results as
conditional on that cache setting. This subsumes much of the rerun in
[the KV probe plan](kv-probe-plan-2026-09-03.md); what it does not subsume is the direct
per-server comparison, which stays as specified there.

**Confirming the winner (GPU, about 1.5 h).** Best quant from the grid **on the evidence, not by
seniority** — three trials on every task it has fewer than three trials on, at the context the
grid showed it holds. This is the ranking row.

*Optional, owner's call, not scheduled:* if Q2_K_L lands marginal rather than clearly dead,
**IQ2_M** is the single run most likely to flip 2-bit from marginal to viable — IQ3_M showed
imatrix carries no dequant penalty at 3-bit, so the same plausibly holds a bit lower. It costs a
~12 GB pull against 68 GB free. Raise it as a decision when the Q2_K_L result is in, never
before.

## 7. Verdict rule

Predeclared and task-level, because a class has only four tasks and a percentage gap would be
all-or-nothing. A task is **solved** by a quant when two of three trials pass under the 900 s
wall. A class is **viable** when the best quant solves three quarters of its tasks at its held
context, rounded up, and **marginal** at half — so each class of four is **viable at three,
marginal at two**, and below that **not viable**. Raw per-task pass rates with trial counts are
printed beside every verdict line, and wall to pass is reported over solved tasks only and
labelled as such. Report one line per class — transformation, comprehension — and the Haiku
comparison beside them as one measurement among several, not as the conclusion the report is
written toward.

**The confidently-wrong rate is a verdict line of its own (rev 5.8), and it outranks pass rate
for the decision the owner is actually making.** Every trial is scored into three outcomes, not
two: **correct**, **visibly failed** (refused, crashed, timed out, obviously broken output), or
**confidently wrong** — a fluent, plausible, incorrect answer delivered without hedging. The
distinction is the whole point of delegating: a worker that fails visibly costs a retry, while
one that is confidently wrong costs the verification the delegation was meant to save, and is
worse than no worker at all. Report the rate per quant per context cell. A quant with a good
pass rate and a meaningful confidently-wrong rate is **not** recommended, and the report says so
in those words.

Expect this to be the most sensitive instrument on the context axis. Long-context degradation in
small quants tends to appear as fabrication rather than refusal — it stops finding the material
and starts inventing it, fluently — so the bend in the curve will likely show here before it
shows in pass rate.

**The context curve is reported, not just the winning cell.** For each quant: the context at
which its pass rate and confidently-wrong rate hold, and where they break. "Good at 24k,
fabricates at 48k" is a more useful sentence to the owner than any single ranking, because it
says how much material may safely be handed over in one go.

**The Haiku comparison carries a construction caveat and must never be quoted without it.**
Section 4's discrimination check keeps at most three tasks that Haiku passes 3/3 and replaces
the rest with harder variants, so most of the suite is tasks Haiku did *not* pass cleanly.
Haiku's rate is therefore suppressed by the way the suite was built, and "local beat Haiku" is
to that extent circular. The check is still right — a task everything passes cannot rank quants,
and ranking quants is the mission — but the two goals genuinely conflict. So: report Haiku's
rate on the suite as run *and* on every task authored including the saturated ones, and let the
second number carry the comparison. If they disagree, the honest sentence is the one from the
unfiltered set. **Superseded by `plan-2026-09-05.md` section 2.6**, which replaces this caveat.

**The 2-bit line is a verdict of its own**, asked for by the owner and reported whatever the
ranking says. It answers "is 2-bit viable for any real work" directly: whether Q2_K_L solves any
task at all, which class it does best in, and the same viable / marginal / not-viable word under
the same arity rule — stated beside its context reach, because 96k fully resident is a capability
no other quant on this card has, and rev 5.8 makes context reach the axis of interest. "Not
viable for real work, and the only 96k option on this hardware" is a real and reportable
outcome, not a failure to report. If Q2_K_L solves nothing, the line says so plainly and names
what it was tested on.

## 8. Budget

Cloud: about 30 GLM gate trials in authoring, expected under USD 2 at v4 rates, plus whatever the
manager spends using GLM sparingly as a second reader — the only real-dollar line in the plan, so
it is the one to watch overnight. Sonnet and Haiku are subscription and draw weekly-all; Haiku is
cheap enough there to run before a reset. Sonnet was "the one to schedule around", and **that
restriction is lifted as of 2026-09-04 by the owner: the weekly reset lands in the morning, so
Sonnet may be spent freely for the rest of this session.** Restore the constraint after the reset
unless told otherwise; the reason it existed has not changed, only tonight's headroom. Luna is off
weekly-all entirely, rides the ChatGPT window and has banked resets, which is why rev 5.7 puts
the parallel breadth there. The Opus manager also draws weekly-all and, running 8 to 12 h with
the intelligence deliberately in it, is the largest subscription line in the authoring work.

GPU, rev 5.8: the grid is fifteen cells x eight tasks at one trial to find the bend, which is 120
trials, then three-trial passes only at and around the bend. At the section 3 rule 2 target of
under 300 s per trial that first pass is the shape of one night on its own, so the bend-finding
pass is the thing to protect and the three-trial passes are what gets cut if time runs out.
Confirming the winner adds three trials per unconfirmed task at one context. The old 25-35
differentiation estimate, the context sweep and the concurrency probe are all superseded. The
total is not restated here because the bend's location decides it; recompute after the
bend-finding pass, which is exactly what `schedule.md` is for.

## 9. Open questions for the owner

**Unity harness — settled 2026-09-03, then superseded 2026-09-04.** Rev 5.6 put u01-u03 on the
VRCA-Bench runner's live Unity-editor MCP loop against `D:\VRCA-Bench\projectsench-C`. Rev 5.8
cuts the class outright on the capacity measurement below, so that harness decision no longer
applies to v5 and the u01-u03 graders are not authored. The runner and the finding in
`findings-2026-09-03-unity-harness.md` stand for whatever later work wants them.

**Unity is answered, and the answer is no — closed 2026-09-04 by measurement.** Not a deferral
and not a quality judgement: pi's Unity MCP surface measures **28,492 tokens across 47 tools**,
31,592 with the four builtins and the system prompt, against quant windows of 24k to 96k on a
card that has 11.9 GB free while a single editor is open. At the 32k configuration the plan had
been going to probe first, the tool schemas alone would consume the entire window before the task
prompt, before one file is read and before any thinking. So **agentic Unity work is out of reach
for a 27B on this hardware by capacity**. Two consequences: MCP is out of scope for every local
arm, and the Unity class leaves the suite. The measurement also stands as the answer to the
mission's Unity half, which is a result rather than a gap.

**The concurrency probe is dropped — owner's ruling, 2026-09-04.** Two streams would double the
volume of output needing verification, which is negative value while the confidently-wrong rate
is unknown, and the quality-versus-context question is the better use of the same GPU hours. The
2-stream arithmetic is preserved in `decisions.md` if it is ever wanted: derived from measured
components, only Q2_K_L could hold two 64k streams (~13.6 GB), and Q3_K_S could not (~14.8 GB).

**Unity and Blender MCP reach Codex — settled by the owner 2026-09-04.** Both servers are added
to the managed `~/.codex/config.toml` through ansible-slb (Blender is not needed for v5 and is
added because later work wants it). Rev 5.8 removed its v5 rationale — it existed to let
Luna author the Unity tasks against a live editor, and those tasks are cut — so this stands as a
fleet change on the owner's ruling, not a precondition for this plan. It still carries the
constraint: port 8080 is one machine-wide endpoint, so a Codex run can seize an editor another
agent is using.
The change joins the same converge as the worker runtime; neither is deployed by hand.

Every question rev 5.2 carried is closed below, and authoring otherwise waits only on the
owner's go-ahead.

Three things stay flagged as decisions the plan will bring back rather than take on its own: the
**IQ2_M pull** (differentiation, only if Q2_K_L lands marginal); the **q8_0 versus q4_0 KV choice**,
which awaits the 64k rerun in [the KV probe plan](kv-probe-plan-2026-09-03.md) rather than the
saturated 16k/24k checksum result.

**The reference ladder is two rows, and that is settled, not overlooked (rev 5.7).** Removing
every author and every gate from the scoring left Sonnet as a declared ceiling and Haiku as the
single comparison, where rev 5.6 had four rows. Fable was considered as an uncontaminated third
and ruled out by the owner. So the ladder is thinner than the "real ladder rather than a single
bar" section 5 originally promised, and the report says so rather than implying more support
than it has: with one comparison row, a local quant's standing against Haiku is one measurement,
not a ranking.

### Closed since rev 5.2

- **Thinking level for local arms** — never actually open. Ruling Q11c pins the 27B at medium,
  section 2 records that low emits more tokens and scores lower, and the first probe's own gate already
  falls back to low. Struck.
- **u04 (EditMode tests)** — **cut by the owner, 2026-09-03.** Three Unity tasks stand, and the
  EditMode test-runner fixture leaves authoring with it.
- **The first probe's quant** — **IQ3_M, at 32k, decided by the owner 2026-09-03**, with the standing
  qualification that this is where the search *starts* and not the org's quality answer: the
  owner is unconvinced on quality grounds, so differentiation explores the space around it rather than
  confirming it. Rev 5.2's Q3_K_M recommendation predated `results/gpu-tune/summary.md` and was
  withdrawn.
- **q8_0 KV control** — **yes, ordered by the owner 2026-09-03.** the KV control.
- **The 2-bit question** — raised by the owner 2026-09-03: is 2-bit viable at all for any real
  work. Now a verdict line in section 7, a full-core pass for Q2_K_L in differentiation, and the
  concurrency candidate in the concurrency probe.
