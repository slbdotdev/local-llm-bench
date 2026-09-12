# v5 — questions for the owner — **CLOSED 2026-09-03**

Written 2026-09-03 by the v5 planning subagent. Companion to `plan-2026-09-03.md`.
Nothing in this file has been executed.

> **CLOSED — every v5 question is answered as of 2026-09-03.** This file is kept as the record of
> what was asked, what was decided, and what each decision changed; it is no longer a request for
> input. The canonical decision ledger is `results/v5/decisions.md`, and the execution-ready
> authoring plan is **section 13** of `plan-2026-09-03.md`.

**The full ledger:**

| Q | subject | answer | what it changed |
|---|---|---|---|
| Q1 | bench editor isolation | **structural, not scheduling** | section 5b1; mechanisms M1, M3, M4, M5; risk R12 |
| Q2 | a fourth bench editor | **A** — build `bench-D`, but only after the first two or three tasks and a proven three-editor loop; copy `bench-C` wholesale | section 5b; **M1 lands first**, since ~6 GB of RAM is the binding cost and `free_memory_gb()` is still called from nowhere |
| Q3 | the Blender arm | **D** — dropped entirely, no controls built | 21 candidates to 18; suite 16-20 to 14-18; risk R10 |
| Q4 | where v5 lives | **A** (default stands) | section 9 |
| Q5 | `builds-worse` | **A** — rework it, but re-probe the current fixture with Haiku (~3 runs) first | section 1; step 0e of section 13 |
| Q6 | plan-usage cap | **no cap, mandatory instrumentation instead**; OpenRouter stays at USD 25 staged | section 5a1 |
| Q7 | per-quant context | **A** — each quant at its maximum resident context (Q2_K_L 96k, Q3_K_S 64k, Q3_K_M 48k); **context-confounded, and the headline must say so** | section 8 item 3, including the two build steps for `q27-<QUANT>-<ctx>` |
| Q8 | pi config changes | **B** — all bench-local via `PI_CODING_AGENT_DIR`; the `reserveTokens` floor is written as a **proposal only** | section 7d; `proposals/reservetokens-floor.diff` + rationale. **`pi-run --agent-dir`: NO**, the env-var route is enough; sub-question withdrawn |
| Q9 | how the ladder reports | **A** — pooled headline, per-arm breakdown beside it, timeout counts next to every mean | section 8 item 5; section 13 |
| Q10 | hard tasks and the waiver lane | **A** — author and gate them, waiver lane exactly as specified; `decimate-under-budget` stays dropped with Blender | section 5 |
| Q11a | a `skill_invoked` check | **yes**, weight ~0.05, on two or three tasks only | section 4a; carriers named in section 13 |
| Q11b | a red-team blocklist fixture | **yes**, in the self-test suite, **not scored** | step 0d of section 13 |
| Q11c | contestant effort | **`high`** for v5 Claude contestants; the 27B stays medium; differing-effort records are never pooled | section 5a2 |
| Q11d | an `org` doc line | **yes** — being made by **another agent** in ansible-slb; not touched here | no edit by this session |
| Q12 | contestant calls through the gateway | **A** | section 5b1; sections 5, 13 |

**Standing decisions recorded alongside them:** the v4 ranking was to finish unchanged — then
**reversed at 12:03 on 2026-09-03: it is stopped and incomplete** (Q2_K_L 18 of 30 runs, one pass),
and Phase 0 is being run on the GPU by **another agent**. Risk R15.

---

## Q1. Bench editor isolation — **ANSWERED, and not the question I asked**

**Owner, verbatim:** *"Batch editor are agent created and driven and should never conflict with my
own fargo crispy ediy"*.

**My reading, which I am stating so you can correct it rather than assuming it:** bench editors are
**agent-created and agent-driven instances**, and what you want is **structural isolation** from
your own `fargo-crispy` session — a mechanism that makes conflict impossible — **not reserved hours
or a scheduling convention**. All three options I offered (A "free now", B "wait", C "reserved
windows") were scheduling answers, so all three missed the point. If that reading is wrong, say so
before the campaign starts, because the whole of section 5b1 in the plan is built on it.

**What I owe you, and where it is:** a per-contention-point statement of what guarantees isolation
today and what does not. That is **section 5b1 of `plan-2026-09-03.md`**, and the summary table is
reproduced in **"Q1 isolation mechanism"** at the end of this file. Where a guarantee does not
exist I say so plainly rather than proposing a prompt rule.

**This also largely settles Q12** toward option A: only runner-driven runs are gateway-pinned, so a
free-form subagent driving an editor is precisely the thing that breaks isolation. See Q12, which
still needs your explicit confirmation.

---

## Q2. Should a 4th bench editor exist?

**Recommendation: yes, but not yet — create `bench-D` after the first two or three v5 tasks are
authored and the three-editor loop is proven.**

It buys ~25% wall clock and nothing else. It costs:

- **one line of code**: `bench/projects.py:106` `BENCH_SLOTS = ("A", "B", "C")` is a hard gate —
  `project_dir()` raises `ValueError` on any other slot. `runner.py:100 DEFAULT_EDITORS` is
  cosmetic; `--editors A,B,C,D` already overrides it. Everything else naming A/B/C is docs or
  tests.
- **manual project creation**: there is no clone script. `reset_assets()` mirrors `Assets/` only,
  and `golden/` has no `Library/` (the existing clones were hand-seeded from
  `D:\avatars\default\Library`). Fastest path is copying `bench-C` wholesale to keep a warm
  `Library/`.
- **~5.1 GB disk** (measured: bench-A is 5.07 GB / 31,068 files). D: has 121 GB free of 239.
- **~6 GB RAM**, which is the real cost — see Q1.

There is no hub or gateway limit on instance count.

| option | consequence |
|---|---|
| **A (recommended)** — create D after the first tasks land | proven loop first, then 25% faster |
| B — create D now | 25% faster from the start, but debugging a new slot while also debugging new tasks |
| C — stay at 3 | simplest; ~1 extra day over the campaign |

---

## Q3. Blender containment — **ANSWERED: D, the arm is dropped**

**Decision: option D. The Blender arm is dropped from v5 entirely, and the four controls are not
to be built.**

What this changed in the plan: tasks **B1-B3 removed**; the four-control containment programme
cancelled; the candidate pool cut from 21 to **18**; the campaign, spend, timeline and
comparability accounting recomputed. A standing rule replaces the mechanism — **no v5 task,
fixture, grader or harness process invokes Blender or the Blender MCP in any form** — and because
nothing in v5 has any reason to touch Blender, that rule has no legitimate exception to trip over.
That is why dropping the arm is genuinely safer than guarding it, not merely cheaper.

**Three consequences you should know about, none of them blocking:**

1. **v5 no longer covers the mesh-work dimension it was scoped to cover.** The report must say
   "Unity and pure-file", not "Unity and Blender". Mesh reduction, FBX round-trips and shape-key
   work are now untested by the benchmark.
2. **The candidate margin got thin** (risk R10). 18 candidates for a 14-18 task suite means more
   than four gate failures ships a short suite, and the hardest candidates are the likeliest to
   fail. There is no longer a cheap arm to backfill from.
3. **Costs went *up*, not down** (see Q6). The three Blender candidates were the cheap ones —
   headless, no editor, no contestant profile — so removing them made the remaining mix more
   Unity-heavy.

**One thing I did not do:** the investigation that produced the four controls is preserved in
section 6 of the plan, so if you ever want a Blender arm the analysis does not have to be redone.

---

## Q4. Where does v5 live — **ANSWERED: A**

**Decision: option A.** VRCA-Bench is the engine; results are mirrored to
`ollama-bench/results/v5/`; **commits in `D:\avatars` are held to the end** of the campaign.

Concretely that means: add an `ollama:<model>` contestant kind to `bench/contestants.py` beside
`claude` and `pi` (it is the existing pi path with a different agent dir and provider — the
gateway, the guard hook, the stdin-prompt handling and the cost/turn accounting are all already
built), keep the two surviving v4 pure-file tasks as a no-fixture task type so a control arm
survives, and write the v5 ladder JSON under `ollama-bench`.

Holding the commits is also the right call for a second reason I should have given the first time:
a fixture or grader edit mid-campaign silently makes two runs of "the same task" incomparable, and
a commit boundary is the natural place to snapshot task hashes (risk R7).

---

## Q5. Should `builds-worse` be reworked, or dropped?

**Recommendation: rework.** Reading only the usable runs, **Haiku scores 3/3 at 1.000** on it — it
is saturated on the control, which by your own gate rule means it is too easy. But its mechanism
(two VRCFury SPS defects that exist only after the preprocess, one of which has a tempting wrong
fix that is graded against) is the best in the suite and worth keeping. Rework by adding
sub-requirements on a different axis until at least one Haiku taker fails.

**One caveat the audit caught:** every `builds-worse` run predates the 2026-09-02 21:46 contestant
fixture rebuild, so "saturated on the control" is proven only against the *old* fixture. The rework
direction still holds — two defects found by the same measurement is structurally weak — but I
would re-probe the current fixture with Haiku once before designing the rework, which costs about
three cheap runs.

| option | consequence |
|---|---|
| **A (recommended)** — rework to 8+ sub-requirements | keeps a good mechanism, costs ~half a day |
| B — keep as-is | a task the control passes 3/3 measures nothing |
| C — drop | loses the only preprocess-only defect task |

---

## Q6. Spend — **ANSWERED: no plan-usage cap, instrumentation instead**

**Decision:** **no plan-usage cap.** The OpenRouter cap stays at **USD 25, staged**. In exchange,
instrumentation is mandatory, and it is now written into the plan as concrete steps (section 5a1),
not as intentions:

1. `bash ~/.local/bin/claude-usage` at **every** gate batch boundary, before and after.
2. The figure recorded in the batch log and in **every** report.
3. Inbox alert to the owner at weekly-all **85%** and again at **95%**.
4. A resume note under `results/v5/` kept current before each batch, so a lockout is an
   interruption rather than a loss. `results/v5/decisions.md` is that note.

**One thing I found while wiring this up that is worth your attention:** the cached usage figure in
`~/.claude.json` read `seven_day: 32` while the live figure was **77%**. So the cache is not merely
~15 minutes stale — it can be wrong by more than a factor of two, and **the batch scripts must call
`claude-usage` live**, never read the cache. The API also exposes no dollar limits
(`limit_dollars` is `null`), which is why the alert thresholds are percentages.

**And one caution I owe you plainly.** The gate campaign is estimated at **USD 115-195 of
plan-usage equivalent** against a weekly allowance already at 77% with extra usage disabled and a
hard stop. Because no dollar limits are exposed, **I cannot tell you whether it fits before the
Saturday 07:59 reset — it may well not.** I have ordered the authoring so the cheap pure-file tasks
and the highest-value Unity tasks are gated first, so that a lockout costs the least valuable work.

**Consequence for the fp8 reference:** USD 25 does not buy three trials over 18 tasks (that would
be USD 30-70). It buys one full trial pass plus second trials on a handful of in-band tasks, so
**the reference will be n=1 for most tasks and must be reported as such** rather than as a
three-trial reference.

---

## Q7. What context config does the **v5** ladder run at? — **ANSWERED: A**

**Recommendation unchanged: per-quant maximum context, and report the ladder as
context-confounded. Recomputed for 18 tasks; the recommendation does not change.**

**Two things are now settled and narrow this question.** First, **the v4 ranking finishes unchanged
at 32k** — your decision — so nothing here applies to it retroactively; the `max_tokens` finding is
carried as a standalone finding with a harness-cap caveat on the v4 local numbers. Second, **the
Blender arm is gone**, which matters more than it looks: Blender was the one arm comfortably
affordable at 32k, so v5's non-trivial half now rests entirely on whether the Unity tool subset
fits.

Why any of this matters: pi hands the model the entire residual context window as its `max_tokens`,
and reasoning and the answer share it. Predicting that number reproduces the observed Q2_K_L output
token counts exactly — delta 0 on `52_reengine`, +34 on `55_minilang`, -20 on `56_tmpl`, and -14 on
`59_uri`, that last predicted before the run landed, so the relationship is predictive rather than
fitted.

**Why no single config works.** `results/gpu-tune/summary.md:40`: **"Q3_K_M reaches 48k and Q3_K_L
only 24k; neither reaches 64k."** And the same file's table shows `Q3_K_S @ 64k with num_gpu 66`
and `Q3_K_M @ 32k with num_gpu 66` both **FAIL (thrash)** — so even the `num_gpu` pin is not
portable across quants.

| option | consequence |
|---|---|
| **A (recommended)** — per-quant maximum at full residency: Q2_K_L up to 96k, Q3_K_S 64k, Q3_K_M 48k | every quant gets the best it can hold; **the ladder is context-confounded** and the report must say so in the headline |
| B — 48k for all three (the largest Q3_K_M can hold) | a genuinely controlled comparison; costs Q2_K_L and Q3_K_S headroom they could have used |
| C — 32k for all three, matching v4 | the only option that keeps any continuity with the v4 ranking; **full-schema Unity is unrunnable**, so the Unity arm depends entirely on the `manage_tools` subset working — the subset is confirmed session-scoped as of 2026-09-03, so this is viable, but it is the whole margin |

**I lean A**, because v5's question is "what can the local hardware actually do", not "which quant
is better per token of context". **B is the right answer if you want one clean number.** C is only
worth it if continuity with v4 matters more than the Unity arm working, and I do not think it does.

**Two build steps either way:** `make_model.sh` names its output `q27-<QUANT>` with no context
suffix, so the existing `q27-IQ3_M-64k` and `q27-Q3_K_S-64k` entries were made by hand, and
**Q2_K_L and Q3_K_M still need their variants built** — with the suffix, or they clobber the 32k
models.

---

## Q8. May the pi harness changes go into ansible-slb, or stay bench-local?

**Recommendation: option B — everything for v5 stays bench-local, and separately I write you a
proposal (not an applied change) for the one fleet trap below.**

Everything needed is reachable through `PI_CODING_AGENT_DIR` (documented at
`pi-coding-agent/docs/environment-variables.md:81`), which `pibench.py` already uses. And the fixes
would be **actively wrong** on the fleet: a small `reserveTokens`, a small `maxTokens` and a
thinking-budget field are all correct for a 32-64k local model and all wrong for GLM 5.3 Flash's
1M window. Nothing under `~/.pi`, `~/.claude/skills`, `~/.agents/skills` or `~/.cursor/skills` is
touched by this plan.

One thing you may nonetheless want fixed on the fleet, as a separate decision: the managed
`compaction.reserveTokens: 548576` makes **any** model with a window below ~548k compact on every
single turn. `ansible-slb/group_vars/all/vars.yml:439-441` already predicts this in writing. It is
harmless today because the fleet only runs 1M-context models — but it is a trap waiting for the
first person who points the managed pi at a small model.

| option | consequence |
|---|---|
| A — bench-local only; no ansible change at all | zero fleet risk; leaves the `reserveTokens` trap in place |
| **B (recommended)** — bench-local now, plus a written proposal for the `reserveTokens` floor | I write the diff as a proposal for ansible-slb and you apply it or not; nothing is edited on any host |
| C — put the whole bench profile in ansible-slb | would degrade the fleet's OpenRouter runs |

**Also for your ruling:** the `pi-run` wrapper cannot point pi at an alternative agent dir (it
exposes only `--model --effort --cwd --timeout --no-context-files`). It does not strip an exported
`PI_CODING_AGENT_DIR`, which is how this plan's own GLM audit was routed by throughput without
touching the managed file. Do you want a `--agent-dir` passthrough proposed for
`ansible-slb/skills/pi-run/scripts/pi-run`, or is the env-var route good enough?

---

## Q9. What is "the best local run" that should land near 0.50?

**Recommendation: report per-arm means and use the pooled mean as the headline, with the arm
breakdown always beside it.**

This matters because the **two remaining arms** (Blender is dropped) will behave completely
differently: the pure-file arm is a known quantity at 5 tasks, and the Unity arm at 13 tasks may be
near-zero for reasons that are partly harness and partly model. A single pooled 0.50 could be
"0.5 everywhere" or "0.9 on files, 0.0 on Unity", and those mean opposite things. With only two
arms and a 13-to-5 split, the pooled number is now **dominated by the Unity arm**, which makes the
breakdown more important than it was, not less.

| option | consequence |
|---|---|
| **A (recommended)** — pooled headline + per-arm breakdown, timeout counts beside every mean | honest, and the arm breakdown is the actual finding |
| B — Unity arm only | the purest test of the new capability, but likely floors at 0 and stops discriminating |
| C — pure-file arm only | comparable to v4, but ignores the whole point of v5 |

---

## Q10. Do the very hard tasks go in?

**Recommendation: author them, gate them, and let the Sonnet gate decide.**

Three candidates are likely to score 0 for everything below Sonnet: `decimate-under-budget`
(Blender mesh reduction under a triangle budget with shape-key travel preserved),
`poiyomi-lock-roundtrip` (where a wrong move destroys a shader unrecoverably) and
`atlas-native-vs-imported` (the imported-vs-native texture size trap). A task that everything fails
adds nothing to a ladder — but your own gate rule already catches that: Sonnet 0/3 with mean < 0.85
means suspect the task.

**The audit found a conflict in your own two gate rules that is worth resolving here.** The Sonnet
rule ("0/3 with mean < 0.85 => suspect the task") will bounce exactly these hard tasks — while the
plan's remedy for "the local ladder scored too high" assumes those same tasks are available to
admit. Symmetrically, the Haiku rule passes a near-saturated task: 2/3 passes at mean 0.94 clears
it. So as written the pair can reject a good hard task and accept a weak easy one.

**Proposed waiver lane.** A task is admissible despite Sonnet 0/3 if all three hold: (a) its
`_selfcheck.py` golden solve scores >= 0.95, (b) every check flips individually on a hand-built
wrong solve, and (c) Haiku mean < 0.30. It is recorded as **"hard, waived"** and reported
separately so it can never quietly inflate a difficulty claim. The Sonnet gate exists to catch
ambiguous prose and buggy graders; (a) and (b) test for those directly rather than by proxy.

| option | consequence |
|---|---|
| **A (recommended)** — author all three, gate them, and add the waiver lane above | keeps the suite's ceiling without weakening the gate's real purpose |
| B — author and gate strictly, drop whatever Sonnet cannot do | simplest; the suite probably cannot reach a 0.50 local mean |
| C — skip all three now | cheapest; loses the hardest tasks and the mesh-reduction dimension |
| D — include regardless of any gate | risks three tasks that measure nothing |

---

## Q11. Four things I found that you may want to rule on directly — (c) is now **ANSWERED**

**(a) No contestant in any measured run has ever invoked the `vrchat-avatars` skill.** It is
installed in every contestant profile and it has never been used, in 45 runs, by any model. If
skill invocation is supposed to matter, v5 should grade it explicitly from the transcript rather
than inferring it from scores. **Recommendation: add a small explicit `skill_invoked` check
(weight ~0.05) to two or three tasks and see whether it moves.**

**(b) `gateway_blocked` is 0 in every recorded run.** No contestant has ever tripped the policy
blocklist, so the forbidden-action machinery — the thing standing between a `bypassPermissions`
contestant and your real avatars — has never actually fired in anger. **Recommendation: add a
deliberate red-team fixture to the v5 self-test suite (a task whose golden solve is blocked) so the
blocklist is proven live rather than assumed.** This is not a scored task; it is a safety test.

**(c) ANSWERED — effort is frozen at `high`.** Every v5 Claude contestant runs with `--effort high` passed explicitly; the local 27B stays at **medium** thinking; records whose `effort` differs are **never pooled**. The finding that prompted it: **the existing VRCA-Bench scores are not effort-controlled.** `docs/design.md` states as a
fairness note that every model runs at `xhigh`. The recorded `effort` field actually holds `high`
(27 runs), `low` (6) and `None` (26); `xhigh` appears in no record. The two big signals survive
this easily (0.215 vs 1.000, and 0.029 vs 0.860 — far too large to be an effort artefact), but it
means no v5 comparison can reuse the old numbers as a baseline without re-running at a frozen
effort. **Recommendation: freeze the effort for v5, pass `--effort` explicitly for every
contestant of every kind, and refuse to pool records whose `effort` differs. Which effort do you
want as the v5 standard — `high`, or `xhigh` as the doc intended?**

**(d) `PI_CODING_AGENT_DIR` does not fully redirect `pi-mcp-extension`, and I found it the hard
way.** Running this plan's own GLM audit, I copied `~/.pi/agent` to a temp dir (to change only the
copy's routing sort to throughput, as you allowed), emptied the copy's `mcp.json` so the audit
could not reach the Unity hub or your Blender, and pointed pi at the copy. The run still tried to
connect to the Unity hub — the extension resolves its server list from somewhere other than the
redirected agent dir. **So emptying a copied `mcp.json` is not a containment measure.** I killed
that run, removed `"packages"` from the copy's `settings.json` so the extension never loads, and
relaunched; the error stopped.

Nothing was harmed — the Unity hub was not running, and your Blender had already exited at
11:02:22 (five minutes *before* the audit launched at 11:07:51, per `%TEMP%\quit.blend`), so no
live Blender was reachable at any point. But the general lesson matters for any future pi run that
is supposed to be isolated: **isolate by not loading the extension, or by the project-level
`.pi/mcp.json` `lazy`-stub shadowing that `bench/contestants.py` already implements — never by
editing a copied agent dir's `mcp.json`.** No fleet file was touched. **Recommendation: worth a
line in `org/pi-harness-2026-09-02.md`, which currently implies the agent dir is the whole
config root.**

---

## Q12. How the gates drive the bench editors — **ANSWERED: A**

**Decision: option A.** Unity gates run **only** through the VRCA-Bench runner with `claude -p`
contestants behind the gateway; pure-file gates run as Claude Code subagents; Blender gates are
gone with the arm.

This is the right call and it is the one that makes the Q1 isolation answer true in practice: only
runner-driven runs are gateway-pinned, so only they have an instance pin, a policy screen and a
call log. A free-form subagent talking to port 8080 has none of the three.

**Two things still need to hold beyond Q12 = A**, because Q12 governs *contestant* calls and two
other paths also reach the hub (detail in section 5b1 of the plan):

1. **The harness itself** — fixtures and graders call `ctx.mcp` directly and pass `unity_instance`
   explicitly per call. That is sound, but it is a *different* mechanism from the gateway, so every
   new fixture must keep passing it.
2. **My own authoring and `_selfcheck` work**, which drives one named editor directly. This is the
   one place a human-driven mistake could reach the wrong instance. `_selfcheck.py` takes the slot
   as `sys.argv[1]` and defaults to `"C"` — the discipline is to always pass it explicitly and
   never rely on that default while another editor is in play.

---

## Q1 isolation mechanism — the guarantees table

Full statement and evidence: **section 5b1 of `plan-2026-09-03.md`**. Revised 2026-09-03 after a
line-by-line audit of `bench/projects.py`, `bench/runner.py`, `bench/gateway.py` and the installed
`mcpforunityserver 10.1.2`. Summary:

| # | contention point | strength today |
|---|---|---|
| 1 | Project directory | **HARD for the runner** (`BENCH_SLOTS` raises, paths absolute and constant, separate package copies) — **NOTHING for the module API**: `reset_assets` runs `robocopy /MIR` against whatever path it is handed |
| 2 | Unity lock / editor reuse | **HARD given a bench path** (`_matches_project` needle is always a bench path) — `launch_editor` does not check that its argument is one |
| 3 | The 8080 hub itself | **SHARED BY DESIGN** — no isolation possible at this layer; enforced one layer up, at routing |
| 4 | Instance routing (gateway injects `unity_instance`; `set_active_instance` keyed by `mcp-session-id`; hidden from contestants) | **HARD, structural** |
| 5 | `manage_tools` scope (proposal H10) | **RESOLVED — session-scoped for activate/deactivate/reset. H10 cleared, provided the gateway never calls `sync`** |
| 6 | Host RAM | **NOTHING — `free_memory_gb()` exists and is called from nowhere in `bench/`** |
| 7 | Editor console between runs | hygiene, not isolation |
| 8 | Unity `EditorPrefs` (one registry key for every project on the machine) | **NOTHING — `policy.json` does not screen it, and `execute_code` can write it** |

**What I can guarantee, narrower than the first draft said:** *the automated batch path* cannot
open, lock, reuse, re-point or write to your `fargo-crispy` project or editor. The runner never
launches an editor at all, and rows 3, 4 and 5 hold unconditionally — routing is pinned per call,
session state is keyed by a header your client does not share, and tool visibility is session-scoped.

**What I cannot guarantee, three things.** (i) The **module API is uncontained**: `reset_assets`,
`launch_editor` and `runner.project_dir_for` accept any path, `--editors` is never validated, and a
`/MIR` mirror **deletes** everything at the target that is not in golden. Nothing triggers it
automatically today, but agents are the intended callers of that module. (ii) A batch can still
**contend for the machine** — 8080 is shared by design and there is no RAM guard; the precedent is
free RAM at 191 MiB on 2026-09-03 at 04:17. (iii) `EditorPrefs` is machine-global and reachable
through `execute_code`.

Honest one-liner: *"a batch cannot reach your project by accident of design, but it can reach it by
accident of typing, and it can starve your machine either way."*

**The code changes that close the gaps, all small and bench-local:**

- **M3 — containment assertions (highest priority; the only destructive failure mode).** Assert the
  resolved target is under `paths.PROJECTS` in `reset_assets` and `launch_editor`, route
  `runner.project_dir_for` through `projects.project_dir()`, and validate `--editors` against
  `BENCH_SLOTS` at parse time. Roughly six lines across two files.
- **M1 — a RAM floor.** `projects.free_memory_gb()` already exists and is never called. Pre-flight
  assertion in `cmd_run` plus a check as each worker takes an editor, refusing below 8 GB (matching
  the existing GPU watchdog), and a warning when a non-bench Unity instance is on the hub.
- **M4 — screen `EditorPrefs` in `policy.json`**, while recording plainly that `policy.json` is
  literal-regex screening and therefore a guard against accident, not against intent.
- **M5 — one integration test** pinning the session-scoping that rows 4 and 5 both rest on, run at
  `mcpforunityserver` upgrade time. The existing tests use a fake server and would not catch a
  regression that re-points your live session.
- **M2 — superseded.** The `manage_tools` wire probe is no longer needed; it is now a one-line rule
  in the H10 implementation: never call `action: "sync"`, which rewrites tool visibility for every
  new MCP session on the machine.

**Recommendation: land M3 and M1 together before the first batch.** Neither blocks task authoring.
M3 is the one that matters most, and it was not visible until the module API was read directly.
