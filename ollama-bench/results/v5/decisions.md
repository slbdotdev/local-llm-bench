# v5 owner decisions (relayed by the phone session, 2026-09-03 11:40-11:50)

Resume note: if this session is interrupted (plan-usage lockout resets Sat 2026-09-05 07:59 local), start here.

| item | ruling |
|---|---|
| v4 ranking (Decision 0) | A: let it finish unchanged; report carries the pi max_tokens harness-cap caveat; a three-way tie is an expected outcome, not a measurement |
| Codex/pi nesting | A: AGENT_RUN_DEPTH env guard in both wrappers, ansible-slb change, gates, converge, commit as owner (done: ansible-slb 3ce8f44, Windows converged 11:51) |
| Q3 Blender | D: Blender arm dropped entirely; re-plan around 18 tasks; no containment controls built |
| Q1 editors | not A/B/C. Owner verbatim: "Batch editor are agent created and driven and should never conflict with my own fargo crispy ediy". Read as structural isolation from the owner's fargo-crispy editor, no reserved hours. Mechanism statement (guarantees present / missing) owed BEFORE authoring starts |
| Q12 gates | A: Unity gates through the VRCA-Bench runner with claude -p contestants; file gates as subagents |
| Q6 spend | no plan-usage cap (owner chose it with live numbers: weekly-all 77%, Fable 89%, extra usage disabled, hard stop). Instrumentation required: claude-usage at every gate batch boundary, figure in every report, inbox alert at weekly-all 85% and 95%, resume note kept current here. OpenRouter cap USD 25 staged, unchanged |
| Q11c effort | v5 Claude contestants at high; 27B stays at medium thinking; never pooled |
| Q4 | default A stands: VRCA-Bench engine, results mirrored to ollama-bench/results/v5, D:\avatars commits held to the end |
| Q7, Q2, Q5, Q8, Q9, Q10, Q11a/b/d | unasked, held by the phone session; none block authoring. Q7 needed before the local ladder |

State at 11:50: campaign not started. v5 planner re-planning (18 tasks, isolation mechanism). Nesting guard agent working in ~/ansible-slb. Q2_K_L ranking ~15/30, boundary ~13:30.

## Sync from the v5 planner, 2026-09-03 (re-plan complete)

The rulings above are unchanged. What the planner learned while applying them, that this note
should carry:

- **Q1 is answered.** The mechanism statement is `plan-2026-09-03.md` section 5b1, summarised at the
  end of `questions.md`. **Guarantee given:** a bench batch cannot open, lock, reuse, re-point or
  write to the owner's `fargo-crispy` project or editor — rows 1, 2 and 4 are structural.
  **Guarantee refused:** a batch can still contend for the machine. Port 8080 is shared by design,
  and **there is no RAM guard at all** (`free_memory_gb()` is never called from `bench/`). Proposed
  fix **M1**, a few lines in `runner.py`; recommended before the first batch. Authoring may start;
  M1 should land before the first *batch*.
- **One open hole:** `manage_tools` scope is unverified. If proposal H10 is adopted to trim the
  Unity tool list, and that reshaping turns out to be per-editor or persisted rather than
  per-session, it would degrade the owner's own tooling. **H10 is not to be adopted until a wire
  probe settles it** (M2). This also makes Q7 option C — staying at 32k — not free, since the Unity
  arm at 32k depends on exactly that subset.
- **Nesting guard: the bench path is NOT covered by the ansible-slb wrapper work.**
  `bench/contestants.py` launches `pi` directly and `runner.py` launches `claude -p` directly.
  Worse, `contestant_env` deliberately *strips* nesting markers so a contestant looks like a fresh
  session, and no deny-list entry mentions `pi`, `codex`, `claude`, `node`, `npm` or `curl` — so a
  contestant can spawn a nested agent outside all cost accounting. Two-line bench-local fix in
  section 7f: add `AGENT_RUN_DEPTH` to `ENV_STRIP` **and** set it explicitly in `contestant_env`.
- **Usage instrumentation caveat:** the cached figure in `~/.claude.json` read `seven_day: 32`
  while the live figure was 77%. The batch scripts must call `claude-usage` **live**; the cache is
  not merely stale, it can be wrong by more than 2x. No dollar limits are exposed, so the 85%/95%
  alert thresholds are the right shape.
- **Budget reality check:** the gate campaign is ~USD 115-195 of plan-usage equivalent against an
  allowance already at 77% with a hard stop. **It may not fit before the Saturday 07:59 reset.**
  Authoring order is set so the cheap pure-file tasks and highest-value Unity tasks gate first.
  Note that dropping Blender *raised* this estimate — those three candidates were the cheap ones.
- **fp8 reference:** USD 25 does not buy 3 trials over 18 tasks (that is USD 30-70). Expect **n=1
  for most tasks** and label it as such.
- **Suite margin is thin (R10):** 18 candidates for a 14-18 suite. More than four gate failures
  ships a short suite, and there is no cheap arm left to backfill from.

State: plan, questions and `revision-log.md` are current as of this sync. Campaign still not
started. Nothing executed, nothing committed.

Owner note (11:53, direct): the v5 plan must schedule and verify fixes for the pi harness bugs v4 exposed (max_tokens/compaction, silent length stops in pibench, reserveTokens, schema budget), bench-local, before the local ladder. Sent to the v5 planner.

---

## Sync from the v5 planner, 2026-09-03 (second sync — isolation audit + harness-fix ruling)

- **The Q1 guarantee is narrower than the first sync said, and the correction matters.** The
  *runner* is contained. The *module API* is not: `projects.reset_assets` derives its `robocopy
  /MIR` target from its argument with no containment check, `projects.launch_editor` checks only
  that the target has an `Assets/` dir, `runner.project_dir_for` formats the path by hand instead
  of calling `projects.project_dir()`, and `--editors` is never validated against `BENCH_SLOTS`.
  `execute_run` then calls `reset_assets(project_dir)` unconditionally. Nothing triggers this
  automatically — the runner never launches an editor — but agents are the intended callers of
  `bench/projects.py`, and `/MIR` **deletes** everything at the target not in golden.
  **Mechanism M3 (about six lines, two files) is now the highest-priority pre-batch fix**, ahead of
  the RAM floor. Risk R12.
- **`manage_tools` is resolved and H10 is cleared.** `activate` / `deactivate` / `reset` are
  session-scoped in the vendor source (FastMCP `enable_components`, "this session only", session-
  prefixed state key). One hard constraint: the gateway must **never** call `action: "sync"`, which
  rewrites tool visibility on the shared hub for every new MCP session on the machine. M2 is
  therefore superseded — no wire probe needed, just the rule.
- **New gap: Unity `EditorPrefs`.** One registry key for every Unity project and version on the
  machine, holding the MCP URL, auto-start and every tool/resource toggle. `policy.json` does not
  screen it and `execute_code` can write it (M4). Related and worth knowing: `policy.json`'s
  `D:\avatars` bans are literal regexes, so a path built by concatenation evades all three
  spellings — it is a guard against accident, not a boundary.
- **M5:** rows 4 and 5 are both hard guarantees resting on a pinned third-party version, and
  `bench/tests/` uses a fake server. One integration test at upgrade time.
- **Harness fixes are now scheduled work, per the owner's 11:53 note.** New plan section **7g,
  Phase 0**: F1 (`maxTokens: 8192` against a 32768 window, in a new `pi-agent-v5/`), F2 (compaction
  on with `reserveTokens: 8192` — never the managed 548576), F3 (record `stopReason`, so a `length`
  stop stops reading as a clean FAIL), F4 (`prompt_overhead_tokens`), F5 (an MCP arm plus the raw
  `tools/list` dump, since pibench has never measured an MCP run at all), F6 (build the agent dir
  the way `contestants.py` does, per R9), F7 (document the turn bound instead of implying one).
  H3 (a reasoning-budget field) is explicitly **deferred** as unverified against Ollama 0.33.2.
- **The Phase 0 gate is binding:** `52_reengine` on `q27-Q2_K_L` at 32k must produce a tool call or
  a non-empty answer **and** record a `stopReason`. No local-ladder run before it passes. It needs
  the GPU, so it follows the v4 ranking; it blocks neither task authoring nor the Haiku/Sonnet
  gates. Risk R13 covers the temptation to skip it.
- **Non-comparability record:** every v5 record carries `harness_version: v5`, `pi-agent/` stays
  frozen as the v4 artefact, and the README names F1-F7 with their effect. The v4 ranking is not
  merged, re-scored or plotted against v5, and the `max_tokens` finding stays standalone with its
  harness-cap caveat.

State: plan (1647 lines), `questions.md` and `revision-log.md` current as of this sync. Campaign
still not started. Nothing executed, no editor driven, no model run, nothing committed, no managed
file touched.

12:03 (owner, desktop): Decision 0 reversed. v4 local ranking stopped (Q2_K_L 18/30, 1 pass; Q3_K_S killed at start). GPU
moves to a rapid smoke plan: pi-agent-v5 cap fix + gate on 52_reengine/Q2_K_L, then 4 tasks x 1 trial x 3 quants
(52,55,57,60), Q3_K_S first. v4 purity not required; initial quant conclusions are the goal.

12:35 (via phone), four rulings:
- Smoke gate conditional = A: if gate attempt 3 fails on Q2_K_L, run the 12-run quant smoke anyway on the instrumented
  harness; a Q2_K_L floor of zero is a result. Do not keep debugging first, do not drop Q2_K_L.
- Q7 = A: per-quant maximum context at full residency (Q2_K_L up to 96k, Q3_K_S 64k, Q3_K_M 48k); ladder is
  context-confounded and the headline must say so. Build suffixed q27-<QUANT>-<ctx> variants for Q2_K_L and Q3_K_M
  (make_model.sh has no ctx suffix; do not clobber the 32k models).
- Q10 = A: author the hard tasks, gate them, waiver lane exactly as specified (Sonnet 0/3 admissible only if golden
  selfcheck >= 0.95, every check flips on a wrong solve, Haiku mean < 0.30; recorded "hard, waived", reported
  separately). decimate-under-budget stays dropped with the Blender arm.
- Q8 = B: all pi changes bench-local via PI_CODING_AGENT_DIR; nothing under ~/.pi or deployed skill roots. The
  reserveTokens floor diff for ansible-slb is a PROPOSAL ONLY: write it, show the owner, do not apply/commit/converge.
Still coming: Q9, Q5, Q2, Q11a/b/d, pi-run --agent-dir sub-question.

12:40 (via phone), round 2; every v5 question is now answered:
- Q9 = A: pooled mean headline with per-arm breakdown beside it, timeout counts next to every mean.
- Q5 = A: rework builds-worse; first re-probe the current fixture with Haiku once (~3 cheap runs).
- Q2 = A: create bench-D after the first 2-3 v5 tasks are authored and the 3-editor loop is proven; copy bench-C
  wholesale for the warm Library; ~6 GB RAM is the real cost (nothing in bench/ calls free_memory_gb()).
- Q11a yes: explicit skill_invoked check, weight ~0.05, on two or three tasks.
- Q11b yes: red-team blocklist fixture in the SELF-TEST suite, not the scored suite.
- Q11d yes: add the PI_CODING_AGENT_DIR line to ansible-slb org/pi-harness-2026-09-02.md; hold the commit with the
  session's other work; run the org doc validator before committing.
- pi-run --agent-dir: NO; env-var route is enough.
- reserveTokens diff remains proposal only.

---

## Sync from the v5 planner, 2026-09-03 (third sync — revision 4, plan is execution-ready)

**All twelve questions plus the three Q11 sub-questions are answered; `questions.md` is closed** and
now carries a one-table ledger of every ruling and what it changed. The campaign start order is
**section 13** of the plan.

- **Q7 = A** is written up with the part that bites: `make_model.sh <QUANT> <ctx>` names its output
  `q27-<QUANT>` with **no context suffix**, so building a 96k variant the obvious way **overwrites
  the 32k model the v4 records were produced with**. The two build steps therefore specify the
  suffixed names (`q27-Q2_K_L-96k`, `q27-Q3_K_S-64k`, `q27-Q3_K_M-48k`) and registration in
  `pi-agent-v5/models.json` with `maxTokens` at about an eighth of the window — never equal to it.
  The context-confounding sentence is specified verbatim rather than left to paraphrase.
- **Q8 = B** done; `proposals/reservetokens-floor.diff` and `.md` are written, **proposal only, not
  applied, not committed, not converged**. `pi-run --agent-dir` = NO is recorded and the
  sub-question is removed from both files.
- **Q2 = A** carries one addition worth reading: `bench-D` costs ~6 GB of RAM, and **M1 must land
  before it**, because `free_memory_gb()` still has no call site in `bench/` and nothing would
  refuse a four-editor batch that overcommits.
- **Q5, Q9, Q10, Q11a/b/d** folded in; the `builds-worse` Haiku re-probe is step 0e and is a
  precondition of designing the rework, not an optional check.
- **The v4 stop (R15)** is recorded in the preamble to section 8 and in section 11: incomplete at
  18 of 30 runs with one pass, never to be presented as a finished ranking, still valid as the
  source of the `max_tokens` finding.
- **R14, and a real correction to finding 1.** The live gate attempts say the `maxTokens` cap is
  **necessary but not sufficient**: `finish=stop` with ~21k reasoning tokens under an 8,192 cap
  means reasoning tokens are not being charged against `max_tokens` on this serving path, and the
  model is ending its turn with an empty content channel. New fix **F8** distinguishes "the model
  had nothing to say" from "we threw the answer away" — raw response logged, Ollama `think` toggled
  off for one run, and the cap accounting established — and **no report may say Q2_K_L cannot
  answer until F8 is answered.**
- **The gate task moves to `59_uri`, and I verified why first-hand.** In
  `results/v4-local-medium.json`, of Q2_K_L's 18 runs, `59_uri` trial 1 scored **1.000 over 37
  turns** — the only unambiguous pass in the file. `52_reengine` is one of the four fingerprint
  tasks the quant has never passed, so a failure there proves nothing about the harness.
  `q27-Q3_K_S` is the secondary gate so one quant cannot block Phase 0 indefinitely. Caveat carried
  into the plan: `59_uri` must not rank anything (its oracle is a renamed copy of its own
  reference), which is fine for a liveness gate and is not evidence of capability. This also
  corrects my own earlier citation of `57_stateful` (0.6154, partial credit) as the best case.
- **Section 13 is new and is the thing to read before starting:** five pre-task steps (M3, M1, the
  `AGENT_RUN_DEPTH` fix, the red-team fixture, the `builds-worse` re-probe), then **P1
  `lfs-attributes`** (pure-file, proves the loop with no editor), **U4 `two-avatars-one-scene`**
  (editor A, proves the gateway path), **U2 `disabled-is-not-free`** (editor B, first trap, first
  `skill_invoked` carrier), then U7/U5/U8; `bench-D` after that; batch-boundary instrumentation and
  the Q9 reporting shape at the end.

State: plan 1868 lines, `questions.md` closed, `revision-log.md` at revision 4, two new files under
`proposals/`. Nothing executed by this session, no editor driven, no model run, nothing committed,
no managed file touched. Phase 0 on the GPU belongs to another agent.

13:52: M3 containment fix landed UNCOMMITTED in D:vatars	oolsench (projects.py assert_bench_project on reset_assets and launch_editor; runner project_dir_for via project_dir, --editors validated; 6 tests; suite 102/102). Length study (GLM, results/length-study) and Luna Max campaign (results/luna-max-v4) running. Prompt-length rule drafted into the v5 plan pending owner confirmation.

13:58 (owner, desktop): prompt-length authoring rule CONFIRMED (see plan, "Authoring rule: prompt length"). Ansible batch (Q/A instruction removal, remote control on, medium effort everywhere, org doc prune, pending doc edit) delegated to an Opus agent with commit + reconverge.

14:09 (owner, desktop): medium smoke legs early-exited (Q3_K_S 0/4 all timeouts, Q2_K_L medium partial). Low-thinking leg started: results/v5-smoke-low.sh, same 4 tasks x 1 trial, Q3_K_S then Q2_K_L then Q3_K_M, 1200 s, pi-agent-v5.

---

## Sync from the control session, 2026-09-03 ~16:15 (GLM v4 column, audit findings, fleet policy)

Full detail: **`results/v5/findings-2026-09-03-glm-audit.md`**. Summary:
- **GLM 5.3 Flash v4 column done** (medium, 1800 s, 3 trials, pi-agent-v4, price-sorted -> Relace): **7/21, mean 0.898, 0.952 excl. timeouts, USD 0.90**; of 14 failures 2 endpoint, 1 cap-censored, 11 deterministic wrong checks. **Owner: no reruns** - v5 planning input only.
- **One GLM-unique miss** (`61_codecs` quoted-printable differential, 3/3); every other miss is shared with fp8 or Sonnet, so those checks discriminate weakly.
- **Behaviour:** in three runs GLM wrote its own tests, called them green, and concluded the spec was wrong. v5 graders must never treat a contestant's own tests as evidence; consider penalising a "spec is wrong" conclusion the reference contradicts.
- **Three v4 defects confirmed** (v4 stays frozen): `52_reengine` rule 2 contradicts its own `a{,}` example list; `56_tmpl:176` defines integer `length` without the minus sign the oracle counts; `56_tmpl` mutation bucket 1 has a stuck fixed-seed mutant all three models fail. They become v5 selfcheck rules (execute every example list; state sign handling; bisect fixed-seed buckets).
- **Routing:** price endpoint ~24 tok/s with run-killing idle stalls, throughput ~85 tok/s at ~2x. Run v5 pi arms at throughput, record the serving provider per run, size timeouts from measured tok/s.
- **Fleet policy since 15:30:** GPT-5.6 Codex-only; adversarial review never the author's family (Luna, GLM fallback); Cursor retired; pi and codex-run default to high.

**Plan revision 4 needs a revision 5 pass to absorb items 3, 4 and 5 before authoring starts. Authoring remains WAITING on the owner's smoke go-ahead.**

## Sync from the control session, 2026-09-03 ~17:00 (smoke stopped, mission restated, plan rev 5)

- Owner stopped the local low-thinking smoke during q27-Q3_K_M. Final local smoke tally: Q3_K_S medium 0/4, Q3_K_S low 0/4, Q2_K_L low 0/4, every trial at the 1200 s wall; no quant ranking is possible from v4 tasks.
- Mission restated by the owner: find whether any real portion of Unity and general programming work can be offloaded to a local 27B; tokens and wall to solution and usable context matter; explore 2 to 4 concurrent local streams; exploration is for curiosity, verdict is the deliverable.
- `plan-rev5-focused.md` written: ten small tasks (four Unity, six general), fp8 3/3 gate, under 5k output tokens, four quants x three trials at 32k, then a context sweep and a two-hour concurrency probe. Rev 4 stays as the harness reference. Three open questions listed in its section 9.
- Owner notes ~17:10: no fp8 27B via OpenRouter any more (too expensive); GPU time budget much tighter, plan must be adaptive with critical probes first. Plan revised to rev 5.1: Sonnet 3/3 + GLM 2/3 gate replaces fp8; Q3_K_M single-trial probe of the whole suite first (B0), quant differentiation only on discriminating tasks with earned trials (B1), winner confirmation (B2), then context sweep and a two-slot concurrency probe; `schedule.md` will hold the next three GPU runs with reasons. GPU estimate about 7 to 8 h, every phase gated.
- Org plan (skills-policy-plan-2026-09-03.md) approved by the owner with all three recommendations; build under way in two Opus agents, commit held until verified.
- DeepSeek V4 Flash 0731 v4 column done 17:02 (high, throughput routing, 1800 s, 3 trials, pi-agent-v4-ds): 9/21, mean 0.862, 0.905 excl. timeouts, 3 timeouts (52 x2, 56 x1), 0 endpoint errors, mean 86.8k out tokens per trial (GLM ~2-3x less), USD 4.61 (GLM USD 0.90). Per task: 59 3/3, 61 3/3, 60 2/3, 52 1/3, 55 0/3 (0.968), 56 0/3, 57 0/3. Beats GLM on passes (9 vs 7) incl. the GLM-unique 61_codecs miss; loses on mean and on cost 5x. Roster row update pending the improvement agent's models.md edit.
- Owner ~17:40: all Luna use so far took 3% of the weekly ChatGPT window; Luna via codex-run at high is free to use without restriction whenever another model family's review or advice is wanted. Docs wording being softened by the build agents; v5 plan updated.
- Luna adversarial review of rev 5.1 (codex-run high, `review-luna-rev5.1.md`) folded into rev 5.2: task-level verdict rule (solved = 2/3 trials; viable = 3 of 4 headline tasks), sentinel set per quant against selection bias, "untested" vs "not viable" wording, GLM gate at throughput with provider recorded, g05 document cut to 12k so the 16k step fits, g06 graded by count, saturation flag at gate time, per-trial VRAM residency logged (Q3_K_M at 32k was already 10% CPU during the smoke).

## Sync from the control session, 2026-09-03 ~17:45 (session restart, owner rulings)

Control session restarted from `results/handoff-2026-09-03-evening.md`. State re-verified: both
ansible-slb clones at `71ee5b4`, clean; converges green on all three hosts; GPU idle.

- **Owner ruling: u04 (Unity EditMode tests) is CUT.** Suite is nine tasks, headline is seven
  (u01-u03, g01-g04). Plan taken to **rev 5.3**: section 4 table and heading, the weighting line,
  the Phase A task count, the B0 trial count (10 -> 9), and the section 7 verdict arity all follow.
  The EditMode test-runner fixture leaves Phase A with the task.
- **Verdict arity restated** (mechanical consequence, flagged to the owner): viable at three
  quarters of a class's headline tasks rounded up, marginal at half rounded up. General (4) is
  viable at 3, marginal at 2; Unity (3) is viable at 3, marginal at 2. Requiring 3/3 for Unity is
  deliberate - at three tasks a 2-of-3 bar lets one task carry a class.
- **Section 9 question 1 struck as never-open**: ruling Q11c already pins the 27B at medium,
  section 2 records low scoring worse while emitting more, and B0's gate falls back to low anyway.
- **B0 probe quant still open, and the recommendation CHANGED.** Rev 5.2 (and this session's first
  message to the owner) recommended Q3_K_M on a-priori quality. That recommendation predates
  `results/gpu-tune/summary.md`, which rev 5.2 never absorbed. On the measured evidence the pick is
  **IQ3_M at 64k** (`q27-IQ3_M-64k`, already baked with `num_ctx 65536`, `num_gpu 66`):
  12.95 GB against Q3_K_M's 13.60, 64k fully resident against 48k, 52.8 tok/s empty and 41.0 at
  60k, the best prompt throughput of any quant tested (2039 tok/s), no IQ dequant penalty, and
  4/4 with 32 s mean wall on the pibench sanity where Q3_K_M's 32k baseline was 80 s/run.
- **Two caveats carried to the owner.** IQ3_M's quality edge over Q3_K_M is nominal plus four easy
  v3-era tasks, not a measured head-to-head. And the entire gpu-tune study ran at
  `OLLAMA_KV_CACHE_TYPE=q4_0` - now the live desktop setting - with no quality measurement at that
  cache type, long-context recall being the usual casualty; so a weak B0 would confound quant
  against KV precision unless B0 spends one q8_0 control trial.
- Plan section 5 now carries a rev 5.3 note that sections 5, 6 and the Phase C window are stale
  against the gpu-tune study; they are rewritten in rev 5.4 once the B0 quant is chosen.
- **Usage flagged to owner:** weekly-all 84% (warning, one point under the handoff's 85% alert),
  and the binding limit is the **Fable-scoped weekly sub-limit at 94%, critical and active**,
  resetting 2026-09-05 ~08:00 MDT. Control stays on Opus through the reset.
- Improvement item 15 delegated to an Opus worker (precondition verified first: the four Cursor
  retired paths absent on WSL and devbox, `enabledModels` absent from pi settings on both,
  Windows `Verify_Retired_Agent_Removal` green in the 17:23 converge).

## Sync from the control session, 2026-09-03 ~18:05 (rev 5.4, B0 settled, 2-bit becomes a verdict)

Owner rulings, all applied to `plan-rev5-focused.md` (now **rev 5.4**) and to the new
`results/v5/schedule.md`:

- **q8_0 KV control in B0: YES.** New **Phase B0-control**, about 15 min: same quant, same 32k,
  same thinking level, single variable, on g05 plus the two highest-partial-score headline tasks
  that failed under q4_0. Written with its procedure and, importantly, its **revert** — the env
  var goes back to q4_0 and Ollama restarts, because the baked `q27-IQ3_M-64k` and
  `q27-Q3_K_S-64k` models exceed VRAM without it. Reading rule stated: a materially better q8_0
  result promotes cache precision to a swept variable in Phase C; no difference retires it.
- **B0 probe: IQ3_M at 32k**, the plain `q27-IQ3_M` with `num_ctx 32768, num_gpu 66` rather than
  the baked 64k model — 13.39 GB keeps ~2 GB margin where 64k is 14.11 GB and fair-weather.
- **IQ3_M is the starting point, NOT the org's quality answer.** The owner is explicitly
  unconvinced on quality grounds, so the plan gives IQ3_M no privilege beyond going first:
  **B1 now runs Q3_K_M and Q2_K_L over the full seven-task headline set**, not a sentinel subset
  derived from IQ3_M's own passes, so IQ3_M's B0 pattern cannot define what the suite measures.
  Q3_K_S keeps the cheap sentinel shape. B2 picks the winner "on the evidence, not by seniority".
  The B0 fallback gate also changed from Q3_K_S to Q3_K_M: if the suite is out of reach the
  question is whether more quality rescues it, not more speed.
- **"Is 2-bit viable at all for any real work" is now a verdict line of its own** (owner's
  curiosity, section 7). Q2_K_L gets the full headline set in B1; the line reports whether it
  solves any headline task, which class it does best in, the viable/marginal/not-viable word, and
  its context reach — 96k fully resident is a capability no other quant on this card has, so
  "not viable for coding, and the only 96k option on this hardware" is a reportable outcome
  rather than a failure. Q2_K_L is also named the natural Phase D concurrency candidate whatever
  wins B2, being smallest and fastest.
- **IQ2_M raised as a conditional, not scheduled.** If Q2_K_L lands marginal rather than clearly
  dead, IQ2_M is the single run most likely to flip 2-bit to viable (IQ3_M showed imatrix carries
  no dequant penalty at 3-bit). ~12 GB pull against 68 GB free. Brought back as a decision when
  the Q2_K_L result is in.
- **Q3_K_L dropped from v5** as a recorded decision: largest, slowest, reliable only to 24k, fair-weather
  at every useful context; nothing it could show would move a verdict line.
- **Plan rule 7 corrected** (rev 5.3, carried): residency from `ollama ps` and `nvidia-smi` is
  necessary and not sufficient. On Windows/WDDM an oversized allocation raises no OOM — it spills
  to system RAM while still reporting `100% GPU` and `offloaded 66/66` while generation
  collapses. Every local trial now also records gen tok/s and a trial below its quant's known
  resident curve is flagged thrashing. Without this a thrashing config would have been logged as
  resident.
- Budget retuned: 9 B0 trials + 3 control, 25-35 in B1 (14 of them the two full-headline passes),
  20 in B2, 14 in C, 8 in D — roughly 6.5 to 8 h.
- Section 9 now carries no open questions. Two decisions are deferred by design and will be
  brought back rather than taken unilaterally: the IQ2_M pull, and whether the q8_0 control
  promotes cache precision to a Phase C variable.

`results/v5/schedule.md` created: the three queued GPU runs (B0, B0-control, B1 Q3_K_M) with
reasons, the standing run rules, and a log.

## 2026-09-04, owner rulings (rev 5.7)

- **Luna authors the suite, and takes no scored row.** The authoring worker moves off weekly-all
  entirely, which was the largest subscription draw in the authoring work. It also fixes an
  independence flaw that was already present: rev 5.6 had an Opus worker authoring and Sonnet
  gating, which is one model family grading its own family's phrasing. Both gates are now
  cross-family. Recorded as design rule 9: the author does not compete, because a task is
  phrased in idioms its author finds natural and a score on it stops measuring capability.
- **A model that gates does not score.** GLM gates at 2/3 and is no longer a reference row: a
  gate drops or rewrites the tasks it fails, so its own pass rate is a floor handed to it by
  construction. Sonnet is the single exception and only as a declared ceiling, where ~100% is
  the point; its number is never quoted as a competitive comparison.
- **The reference ladder is two rows, and that is accepted rather than overlooked.** Removing
  every author and gate left Sonnet as ceiling and Haiku as the one comparison, down from four.
  **Fable was considered as an uncontaminated third row and ruled out by the owner.** The report
  states the limit rather than implying more support than it has.
- **The Haiku comparison carries a construction caveat.** Section 4's discrimination check keeps
  at most three core tasks Haiku passes 3/3, so at least four of seven are tasks it did not pass
  cleanly, and "local beat Haiku" is to that extent circular. The check is still right — a task
  everything passes cannot rank quants — but the two goals conflict. Resolution: report Haiku on
  the core set *and* on the full nine, and let the unfiltered number carry the comparison.
- **The authoring work becomes a managed overnight session.** One Opus manager subagent runs it
  and holds the judgment, briefing and reading its own workers — a deliberate, scoped exception
  to the fleet rule that a control session invokes `codex-run` itself. Goal 8 h, hard limit 12 h.
  Standing rules: bank ambiguous calls and carry on rather than block; never take a structural
  decision alone; the GPU is serial.
- **Calibration is not selection (new section 4a).** The authoring work now uses the GPU, which
  is the sharpest hazard in the plan. Local runs may size a task — context fit, appetite, wall,
  prompt ambiguity, checker behaviour — and may never keep, drop, reword or reorder a task
  because of whether a quant *passed* it. Difficulty is the thing being measured. Consequence:
  calibration runs happen on tasks not yet used for scored trials and can therefore never be scored
  trials, so the first probe still runs separately on its own. That duplicated GPU time is a known and
  accepted cost of authoring against the hardware.
- **Phase names are dropped.** One plan with an order, not six numbered stages; the seven
  weighted tasks are the **core set**, not the "headline"; and language that pre-committed the
  report to a conclusion is removed, including "beating Haiku is the headline sentence".
- **Codex gains the Unity and Blender MCP servers** through ansible-slb (Blender is not needed
  for v5 and is added because later work wants it). This is what makes Luna a credible author
  for u01-u03 rather than writing Unity tasks blind against a spec.
- **Unity editors compete for VRAM with the quant under test.** Four open editors is normal on
  this desktop, and rule 7 already records that a quant near the 14.2 GB fair-weather line
  thrashes when the desktop reclaims 1 to 2.9 GB. Unity calibration and local quant trials
  therefore do not overlap, and a trial taken with editors open is suspect on tok/s whatever
  residency reports.
- **GLM routing is chosen per run, not pinned.** Take whichever of `pi-run`'s four preferences is
  the best trade at the time and record which endpoint served each gate run; no named provider is
  pinned, so this stays a per-run flag rather than an ansible change. The `max_price` ceiling
  applies whichever preference is used.
- **Precondition on the whole authoring session:** the worker runtime must be committed,
  converged to all three hosts and acceptance-tested with a real `codex-run` and `pi-run` first,
  and the KV probe harness faults in `org/pending.md` fixed and supervised, before an unattended
  overnight loop is pointed at that hardware.

## 2026-09-04, owner rulings (rev 5.8) — the Unity result and the pivot

- **Agentic Unity work is out of reach for a 27B on this card, by capacity.** Measured on the
  desktop 2026-09-04 through the deployed `pi-run` with `--mode json` added to a copy: pi's
  system prompt + AGENTS.md + org skill = 1,958 tokens; the four builtin tools add 1,142; the
  **Unity MCP surface is 28,492 tokens across 47 tools**; Blender adds 4,532 across 26. A
  Unity-capable run therefore starts at ~31,600 tokens. Quant windows run 24k to 96k, and an open
  editor takes ~4 GB leaving 11.9 GB free of 16,303 MiB. At the 32k configuration the plan was
  going to probe first, the tool schemas alone exceed the window. This closes the Unity half of
  the mission with an answer rather than a gap.
- **MCP is out of scope for every local arm**, and the Unity class leaves the suite. The Codex
  MCP change stands as a fleet change on its own merits.
- **The concurrency probe is dropped.** Two streams double the output needing verification, which
  is negative value while the confidently-wrong rate is unknown. Preserved for later if wanted,
  derived from measured components: only Q2_K_L could hold two 64k streams (~13.6 GB against
  ~11.4 GB of model bytes plus 2x1088 MiB KV); Q3_K_S could not (~14.8 GB, over the 14.2 GB
  fair-weather line). Two 32k streams fit for both. Arithmetic, not a measurement.
- **The axis of interest is quality against context, 24k to 64k.** Fifteen cells, ragged because
  Q3_K_M tops out at 48k and Q3_K_L is excluded by the 32k floor. One trial per task across all
  cells to find where the curve bends, then three-trial passes only at the bend.
- **The context must be occupied to be measured.** `num_ctx 64k` allocates KV up front but a
  short prompt uses a few thousand tokens, so a "64k" trial on a short prompt measures nothing.
  Tasks are embedded in realistic-but-irrelevant filler to the cell size. This is the flaw that
  made the 2026-09-03 KV probe uninformative: an exact-match checksum needle is binary and
  saturated at 24/24, with no resolution to show degradation.
- **32k minimum context**, because the model must read several things and think. This excludes
  Q3_K_L on its 24k reliable limit — the same exclusion rev 5.4 recorded, now for a second and
  independent reason.
- **Idle GPU is the expectation**, not "alongside Unity work": the owner's other work mostly is
  not Unity, and no quant fits beside an open editor. A trial taken with an editor open is void.
- **The confidently-wrong rate is a first-class verdict line**, reported per quant per context
  cell, and it outranks pass rate for the decision being made. Three outcomes per trial: correct,
  visibly failed, confidently wrong. A worker that fails visibly costs a retry; one that is
  confidently wrong costs the verification the delegation was meant to save. Expected to be the
  most sensitive instrument on the context axis, since small-quant degradation tends to appear as
  fluent fabrication rather than refusal.
- **Traps are load-bearing.** A confidently-wrong rate cannot be measured on tasks whose
  plausible answer is correct, so at least half the comprehension variants have a negative
  correct answer: nothing found, claim false, leave it alone. t01 is drawn from life — a real
  sweep for a moved path on 2026-09-04 returned four hits, two of which were correct history that
  "fixing" would have damaged.
- **The suite is eight tasks in two classes of four**: transformation (g01-g04, kept) and
  comprehension (t01-t04, new). g05 becomes t03; g06 goes with the MCP decision. Verdict arity
  follows: viable at three of four, marginal at two.
- **The role being tested is the worker that still exists when the paid windows are gone.** Not a
  cost argument — Luna is off weekly-all and GLM is cents — but availability and locality.

## 2026-09-04, Opus manager session — startup findings and banked calls

Opened from `handoff-2026-09-04.md`. Skills `org`, `codex-run`, `pi-run`, `agent-runtime`
invoked before the first action, as instructed. Three deltas were handed down by the control
session at start and override the handoff where they differ: `~/ansible-slb` is busy and is not
this session's to touch at all (no writes, no commits, no converge, no playbook); a multi-turn
`pi-run` follow-up can report `succeeded` carrying a *stale* previous-turn answer when the
follow-up's turn dies upstream, so gate runs prefer a fresh one-shot and any follow-up answer is
checked against the question it was meant to answer rather than trusted on its `succeeded`
state; and no foreground `agent-run wait` is taken while other work exists.

### The working invocation for Windows-side GPU work, established and recorded

The handoff expected this to cost the first ten minutes and to need `ssh fractal` with `sh -lc`.
It does not. **Windows Python is executed directly from WSL, with no ssh, no PowerShell wrapper,
and no quoting layers:**

    /mnt/c/Users/slb/scoop/apps/python/current/python.exe kvquality.py …

run with cwd `/mnt/d/local-llm-bench/ollama-bench/results/v5/kv-probe`, which that interpreter
sees as `D:\local-llm-bench\ollama-bench\results\v5\kv-probe`. Verified live: Python 3.14.7;
`~/AppData/Local/Programs/Ollama/lib/ollama/llama-server.exe` and `cuda_v13` both resolve under
Windows `expanduser`; `nvidia-smi` and `tasklist` are reachable from that interpreter; `os.getcwd()`
returns the `D:\` path, so relative paths in the harness behave as the script expects.

`nvidia-smi` also works directly from WSL (`1297 MiB / 16303 MiB` used at session start), so VRAM
can be read without entering Windows at all. **Consequence: the "multi-line program never goes
inline" trap does not arise for this harness** — there is one process boundary, not three, and
no `ssh host '…'` or `wsl.exe -- bash -lc '…'` re-parsing. The ssh-to-`fractal` path stays
correct for anything that genuinely needs a Windows *shell*; it is not needed to drive this
benchmark and should not be reached for by habit.

### Machine state at session start

- GPU idle at 1297 MiB of 16303 MiB. No `llama-server.exe` process. `ollama ps` empty — the
  Windows Ollama service (0.33.3) is up with nothing loaded, which is the required state for the
  direct-server harness (the plan forbids the model service serving *concurrently*, not the
  service existing).
- `OLLAMA_KV_CACHE_TYPE=q8_0` confirmed live, as the plan predicted. **The grid must set `q4_0`
  and revert this to `q8_0` with an Ollama restart afterwards.** Recorded here so the revert
  survives a session restart.
- All grid quants are present locally: `q27-Q2_K_L`, `q27-Q3_K_S`, `q27-Q3_K_M`, `q27-Q3_K_L`,
  `q27-IQ3_M`, plus the pre-built 64k variants `q27-Q3_K_S-64k` and `q27-IQ3_M-64k`. No pull is
  needed to start the grid.
- `D:\local-llm-bench` clean on `main` at `97c2529`.

### Banked: the bench repo has no `CLAUDE.md`

The handoff and the fleet rule both say to read `D:\local-llm-bench\CLAUDE.md` as instructions
before touching this repo. **That file does not exist and never has** — `git log --all
--diff-filter=D -- '*CLAUDE.md'` returns nothing, and there is no `AGENTS.md` anywhere in the
tree either. So the repo's contract is `README.md` plus the v5 plan, and this session proceeded
on those. Not a blocker and not fixed here, because writing a repo contract is a structural
decision and section 6's "bank, do not block" applies: **a later session should decide whether
this repo wants a `CLAUDE.md`**, and if so it should at minimum carry the Windows-Python
invocation above, the `OLLAMA_KV_CACHE_TYPE` revert obligation, and section 4a. Until then the
handoff's instruction is unsatisfiable as written and the next manager will lose the same few
minutes discovering it.

### Banked: an OpenAI prompt-policy refusal is an endpoint failure, not a model failure

The first inspiration run (`wr-wsl-20260904T092849Z-64c512d80964`) ended `failed` before any
turn began:

    ERROR: Invalid prompt: your prompt was flagged as potentially violating our usage policy.

Nothing was wrong with `codex-run`, the supervisor, or the ChatGPT window. The trigger was
phrasing in the *brief*, not the subject: the refused version asked for constructions that
"resist being gamed", described a checker "the model never sees", and used trap/probe framing —
wording that reads as asking a model to help defeat an evaluation or safety system. Reworded into
plain academic terms (no probing, gaming, defeating or stress-testing; "control items whose
inputs do not support an answer" instead of "traps"), the identical request cleared moderation
and ran. Both briefs are kept at `results/v5/briefs/inspiration.txt` (current) for audit.

**This is plan section 3 rule 8 applied to worker runs rather than to scored rows**, and it
matters for the gate records: a provider-side refusal or 5xx must never be written down as a
model failing a task. Two further notes for whoever hits this next. The run's terminal detail
says only `codex exited 1`; the real cause is in `<run-dir>/harness.log`, and for a **pi** run it
is in `<run-dir>/pi-session/*.jsonl` and never in `harness.log`. And the control session has
taken the "surface the ERROR line in the terminal detail" gap as its own runtime finding, so it
is not this session's to fix.

### Method note carried forward from the runtime acceptance page

Give a worker a task whose answer can be computed independently, and size the task to the race
being tested. Applied here: the KV-probe lifecycle fix is authored by a worker but its proof —
a real start/stop/start cycle on the GPU — is run by this session, not by the worker, because
the card must stay serial under one controller and because a worker asserting its own fix works
is exactly the claim that needs independent checking.

### BLOCKING, found 2026-09-04: FRACTAL has no working CUDA backend

Full evidence: `findings-2026-09-04-gpu-cuda-broken.md`. In one line: **an interrupted Ollama
install on 2026-09-03 at 21:16-21:17 left `lib/ollama/cuda_v13` half-written with
`ggml-cuda.dll` absent, and Ollama now serves entirely on CPU — 3.2 tok/s against the 51-53
tok/s measured on 2026-09-03, `pct_gpu 0`, 0.00 GB VRAM.** The whole fifteen-cell grid, the 64k
KV rerun, and plan section 6's GPU calibration step are blocked until Ollama is reinstalled.

Found only because the KV-probe lifecycle proof was run on real hardware rather than reviewed as
a diff. Every cheap state check the handoff prescribed passes: the GPU reads idle, `nvidia-smi`
works, the driver is current, `ollama list` and `ollama ps` are normal, the version string is
right. **Nothing looks wrong until a model is actually loaded and its residency read.** That is
the reusable lesson and it is the same one plan rule 7 already states about `100% GPU` being a
lie under WDDM: residency is a measurement, never a report.

Banked decisions taken alone, all reversible and all recorded rather than assumed:

- **A minimal reversible repair was attempted and failed.** `cuda_v13` was renamed aside so
  Ollama could fall back to the complete `cuda_v12`; it stayed CPU-only, almost certainly because
  the RTX 5080 is Blackwell sm_120 and the shipped `cuda_v12` build has no sm_120 kernels. The
  rename was reverted and **the host is in exactly the state it was found in.** Script and both
  directions: `results/v5/repair-cuda.py`.
- **No reinstall was attempted, deliberately.** Reinstalling a managed Windows application is
  fleet-layer work; this session was barred from `~/ansible-slb` with another worker in flight
  there; and running an installer unattended on a machine whose last installer run died halfway
  is the wrong move without the owner. This is banked, not decided.
- **The GPU half of the night is abandoned and the cloud half continues.** Authoring, the
  mechanical selfcheck, and the Sonnet/GLM/Haiku gates need no GPU and are where the remaining
  time goes. Section 4a is unaffected — with no quant reachable, selection against a quant's
  results is not even possible.

**Consequence of outstanding local sizing, and it is the important one.** Plan section 6 loop step 3 sizes
each task against the local model: does a trial finish under 300 s, does the prompt read
unambiguously to a small model, does the window fit. **Those properties cannot be settled by
this session**, so local sizing remains outstanding. The per-task record notes, for every task,
that its local calibration is outstanding.

### Banked: two more preconditions the handoff did not list

`findings-2026-09-04-grid-harness-gap.md`, in short — and none of these change what the suite
measures:

1. **`pibench.py` does not pad the context at all.** The grid's whole premise is that a cell is
   run with its window filled; `run_pi()` pads nothing. Every cell would have received the same
   short prompt, the curve would have been flat by construction, and the flatness would have
   looked like a finding. This is the most expensive defect available in this plan, because it
   does not fail — it returns a confident wrong answer, which is precisely what the benchmark
   exists to measure.
2. **Thirteen of the fifteen cells had no model tag.** pi passes no options, so `num_ctx` and
   `num_gpu` reach Ollama only when baked into a tag; `pibench.py --num-ctx` sets only the
   throughput probe. A "48k cell" on a base tag would have silently run at 32768 and without the
   forced offload worth up to 2.3x. **Fixed**: `ollama-bench/make_grid_models.sh` builds all
   fifteen. Trap recorded there: Windows `ollama.exe` cannot read a WSL `/tmp` path and fails with
   "no Modelfile or safetensors files found" **and exit code 0**, so a script without an explicit
   check reports success.
3. **The headline instrument is not recorded per trial.** The v5 checkers emit a `VERDICT
   correct|visibly_failed|confidently_wrong` line (new in the authoring contract); `pibench.py`
   parses only `SCORE` and `PASS`. Additive one-line fix, cannot change any existing number.

### Banked: `VERDICT` added to the checker contract

Every v5 checker prints a third line, `VERDICT <word>`, decided mechanically from what the model
produced. Section 7 predeclared the three outcomes and made the confidently-wrong rate a verdict
line outranking pass rate; without this the rate would have to be reconstructed by a human
reading truncated grader tails across 120 trials. It is **additive** — `pass` and `score` keep
their exact current definitions — and it does not change what any class measures, so it is
authoring, not a structural decision. Recorded here so it can be reversed if needed.
Independent support, found afterwards and not used to justify it: SimpleQA grades three ways and
Abstain-QA's confusion matrix counts correct refusal separately
(`findings-2026-09-04-inspiration.md`).

### The suite: authored, verified, selected — 2026-09-04

Twenty-four candidates (eight tasks x three) authored by eight parallel Luna runs against
`results/v5/authoring/CONTRACT.md`. Picks with reasoning and the full section 4a audit record:
`results/v5/authoring/selection.md`. Gate results: `findings-2026-09-04-gate.md`.

**Every worker claim was recomputed rather than trusted**, by `verify_candidates.py` under the
same Windows interpreter the harness uses. It builds each candidate's sandbox exactly as
`pibench.py` does and checks two things per candidate: the checker passes its own reference
(`SCORE m/m`, `PASS`, `VERDICT correct`, exit 0), and a did-nothing sandbox yields
`VERDICT visibly_failed` without crashing the grader. Every authoring worker had reported all
three of its self-checks clean. **Two real defects were found anyway**, which is the whole
argument for the step:

- **Six checkers labelled a did-nothing sandbox `confidently_wrong`** (g02 and g03, all
  candidates). The rule was `visibly_failed if something raised else confidently_wrong`, so a
  model that never edited anything — gave up, ran out of time, produced no work — was counted as
  confidently wrong. In the grid that would have inflated the headline instrument with every
  non-attempt, which is exactly backwards: a non-attempt is the cheap, visible failure. Fixed by
  hashing the pristine seed into the checker so "unchanged" is detectable, without weakening the
  `confidently_wrong` detection itself.
- **My own verifier was wrong about t01**, reporting all three candidates as failing their
  reference. They were not: t01 ships `ref/solve.py`, a program that *produces* the artifact,
  while every other task ships the finished artifact. Recorded because the inconsistency is real
  and a later reader will hit it — **two `ref/` conventions coexist in this suite** and anything
  consuming `ref/` must handle both.

### Banked: the gate found two task defects, and both are fixed in the prompt not the checker

Sonnet passed 6 of 8 on the first trial. g03 and g04 failed, and under plan rule 1 a task Sonnet
fails is a *task* defect and never evidence about a quant. Both were, and in both cases the model
did something defensible given the text:

- **g03's checker tests a function its prompt never names.** The failing subcheck requires a
  reflective dispatch helper to accept and forward the new keyword-only options; the prompt
  contains that function's name **zero times**, asking only for propagation "through `forward` and
  `present`" plus updating "the string used by `getattr`". Renaming a string is not forwarding an
  argument.
- **g04's prompt contradicts its checker.** The seed has the classic shared mutable default; the
  checker requires per-call isolation, i.e. that the behaviour *change*; the prompt says public
  behaviour "must remain intact" and not to remove behaviour to silence a finding. Preserving the
  bug is what the prompt literally asks for.

**The diagnostic that separates ambiguity from difficulty, worth reusing:** Sonnet failed g04
while GLM passed it 3/3. Difficulty produces a consistent gradient across models; ambiguity
produces model-dependent readings of the same sentence. On g03, where the defect is a missing
requirement rather than a contradiction, both models struggle (Sonnet 0/1, GLM 1/3) — the other
signature, equally diagnostic. Fixes state the requirement without naming the sites, so the tasks
are not made easier in substance.

### Sizing is established for appetite and NOT established for the local wall

Completed gate trials: GLM 322-2,341 output tokens (median ~590) and 7-40 s wall; Sonnet 4-6 tool
calls, 12-74 s. Comfortably inside rule 2's 5,000-token appetite, so v4's failure — tasks needing
40-50k output tokens, every local trial hitting the wall before quality could be measured — has
been avoided. **But these are fast cloud models.** The local timeouts this data is meant to size
are for a 27B quant at ~45 tok/s that could not be run at all. Nothing here measures the local
model's reading of a filled 64k window, its tool-call overhead, or its turn count. Appetite:
established. Local wall: **not established**.

### Banked: never dispatch a worker onto a tree another worker still holds

Two runs died with exit 144 through a scheduling error of this session's. A worker was sent to fix
task checkers while an authoring worker was still rewriting the same files; it saw the seed
changing underneath it, judged the tree unstable, and **killed the other worker processes**,
destroying the authoring run, the in-flight GLM gate, and itself. No data was corrupted — the
verdict fix had already landed for five of its six targets.

Two rules out of it. First, check a run is terminal (`agent-run status`) before pointing another
run at the same files; the runtime makes this trivial and this cost two runs. Second, and more
general: **a Codex worker has no permission system and full access, and will take drastic action
when its assumptions break.** Killing processes was a defensible response to "the tree is moving
under me" and was still wrong. Every brief dispatched afterwards carries an explicit prohibition —
do not kill, terminate or signal any process you did not start; if something looks like it is
changing under you, stop and report. That line should be standing text in any brief for a worker
on a tree that others may touch.

### Banked: the pristine-seed digest is correct but brittle while seeds can change

The fix for "a did-nothing sandbox must read `visibly_failed`" works by hard-coding a hash of each
pristine seed file into the checker, so "unchanged from seed" is detectable without trusting
anything the model could have altered. That is the right mechanism and it has one property worth
writing down: **the digest goes stale the moment a seed file is edited**, and a stale digest makes
the checker think the model changed something when it did not. One was already found and
corrected in g02/cand-3 during this session.

Once the seed files stop changing this is a non-issue. While they can change it is a live hazard:
**any edit to a `seed/` file must be followed
by re-running `verify_candidates.py`**, whose EMPTY case is exactly what catches a stale digest.
Whoever runs the hash step should re-run it one final time immediately before taking the hashes, so
the digests and the seeds are known to agree.

### IMPORTANT for the KV harness: Ollama's own model runner is also called `llama-server.exe`

Found 2026-09-04 when the lifecycle selftest stalled on a card the GPU owner had just verified.
Measured, not inferred: with `q27-Q3_K_S` loaded through Ollama, `Get-CimInstance Win32_Process`
shows a **`llama-server.exe` (pid 9692) whose ParentProcessId is 19824 — the Ollama server
process itself.** Unloading the model with `keep_alive: 0` made that process disappear, which
confirms the parentage from the other direction.

`kvquality.py` launches its own `llama-server.exe` directly, and its cleanup barrier both (a)
enumerates every `llama-server.exe` by image name and `taskkill /T /F`s it, and (b) treats any
`llama-server.exe` still present after the VRAM drain as a failure. Neither step can tell its own
child from Ollama's runner. Two consequences:

- **Benign but confusing:** with a model loaded in Ollama, the barrier can never see three
  consecutive quiescent VRAM samples (the card holds ~15.3 GB), so it burns its full 180 s and
  reports "VRAM did not reach three consecutive quiescent samples". That is a *correct* refusal
  with a *misleading* reason: the real cause is "Ollama has a model loaded", not a drain failure.
- **Not benign:** in the ordering where the barrier reaches its kill step first, it would
  **`taskkill /T /F` Ollama's model runner** — killing another agent's work with no warning.

The harness docstring already says "Ollama must have nothing loaded before this runs", so this is
a documented precondition rather than a violated invariant, and the plan's "one model on the GPU
at a time" rule says the same. But a precondition the code cannot check is one that will
eventually be broken, and the failure mode is killing someone else's model.

**The fix, for whoever picks this up (not applied tonight):** the barrier should identify
`llama-server.exe` processes by **parent pid** — its own child is the one it spawned, anything
whose parent is the Ollama server is not its to touch — and should **refuse with the accurate
reason** ("Ollama has a model resident; unload it first") instead of killing it or timing out on a
drain that was never going to happen. Enumerating with `Win32_Process` gives `ParentProcessId`
alongside the pid, and the barrier already shells out to PowerShell-adjacent tooling, so this is a
small change to `_llama_server_pids`.

Workaround until then, and it is what the grid should do anyway: unload Ollama
(`{"model": ..., "keep_alive": 0}`) and confirm `nvidia-smi` is back near idle **before** any
direct-server run. Measured tonight: the card returned from 15,357 MiB to 1,230 MiB within 2
seconds of the unload.

### Gate status at end of session

**GLM 5.3 Flash, 3 trials x 8 tasks on the fixed suite: all 8 tasks pass the 2/3 gate**
(g01 3/3, g02 3/3, g03 2/3, g04 3/3, t01 2/3, t02 2/3, t03 3/3, t04 3/3). The pre-fix run is kept
for comparison at `authoring/gate-glm-prefix.json`, where g03 scored only 1/3.

**Sonnet: trial 0 6/8, trial 1 7/8.** g03 recovered to a clean 13/13 after its prompt was fixed.
g04 failed twice, was diagnosed as a task-shape problem rather than a wording one, and its
candidate was replaced; the replacement passed 8/8 first time. Sonnet still needs a third trial on
all eight to satisfy rule 1's 3/3, and the replaced g04 has only one trial.

Not run at all: **Haiku**, both the x3 prompt-defect check and the two rates section 7 requires
(on the selected set, and on every task authored including saturated ones). It needs no GPU.

### A green result must carry evidence for the thing it claims — the lifecycle proof, twice

The first `--lifecycle-selftest` run against the repaired GPU returned `ok: true` and was very
nearly recorded as closing the owed proof. It did not close it. Every VRAM sample in the artifact
read the idle 1230 MiB baseline and no peak was recorded anywhere, so the file could not
distinguish **"the drain branch waited for a real 14 GB allocation to fall"** from **"VRAM was
already under the ceiling and there was nothing to drain"**. The control session caught this;
the reasoning is worth keeping because it is the same failure shape as the day's main fault, where
a version check passed throughout and only a real load disproved it.

Two fixes, and the second matters more than the first:

1. `lifecycle_cycle` now samples `nvidia-smi` **while the server is healthy, before teardown**,
   and records `vram_resident_samples_mib` and `vram_peak_while_healthy_mib` in every cycle.
2. `drain_branch_proven` is a **separate top-level field from `ok`**. They are different claims —
   `ok` says the cycle completed, `drain_branch_proven` says the run exercised the branch that
   waits for a real allocation to fall — and merging them is precisely what produced an artifact
   that asserted more than it showed.

Re-run result, now self-evidencing: `vram_peak_while_healthy_mib: 14611` on both cycles, draining
to `[1230, 1230, 1230]`, `ok: true`, `drain_branch_proven: true`. The 6.6 s to healthy is genuine
for this model — an mmap-backed load off a warm page cache, not a short circuit.

**Process lesson, banked:** the run that *had* originally exercised the drain (samples climbing
13783 → 14581 → 14611 → 1230) was overwritten by re-running with the same `--out` path, so its
evidence survived only in a session transcript, which is where evidence must never live. Write
`--out` to a per-run filename.

### Final gate state — rule 1 is satisfied on all eight tasks

| task | pick | Sonnet | GLM |
| --- | --- | --- | --- |
| g01 | cand-2 | 3/3 | 3/3 |
| g02 | cand-3 | 3/3 | 3/3 |
| g03 | **cand-1** (replaced) | 3/3 | 3/3 |
| g04 | **cand-1** (replaced) | 3/3 | 3/3 |
| t01 | cand-3 | 3/3 | 3/3 |
| t02 | cand-2 | 3/3 | 2/3 |
| t03 | cand-3 | 3/3 | 3/3 |
| t04 | cand-3 | 3/3 | 3/3 |

Two tasks were replaced on gate evidence, which rule 1 explicitly provides for ("a task Sonnet
fails is fixed or replaced, and that is a *task* defect, never evidence about a quant"). In both
cases fixing was tried first and only replacement worked, and in both cases **no quant evidence
existed or could have existed** — the GPU was unusable throughout authoring, so section 4a's
prohibition was satisfied by circumstance as well as by discipline.

- **g04/cand-2 → cand-1.** Its checker demanded that a function named `remember`, called with no
  explicit table, must **not** persist anything. Sonnet preserved the persistence twice, once
  before and once after the prompt was reworded, each time saying plainly that it was keeping the
  documented behaviour. The task was asking which of two coherent readings the author had in
  mind, not whether the model could spot a silent defect.
- **g03/cand-3 → cand-1.** FAIL, PASS, FAIL across three Sonnet trials, and the two failures were
  on **different** subchecks — the prompt was amended to name the reflective dispatcher, that site
  then passed, and a bundling wrapper failed instead. The task threads a new option through five
  forwarding sites; a prompt short enough to meet the word limit cannot enumerate them, and
  enumerating them would turn it into a checklist. Wrong task, not a hard one.

**What Haiku still owes, and it is the last outstanding check:** three trials
rather than one, on the *current* suite (the single Haiku run predates both replacements); the x3
prompt-defect check, which is a different use of Haiku and must not be substituted by the scored
row; and section 7's second rate, over every task authored including the saturated ones. On its
one trial Haiku passed six of eight, and if that holds at 3/3 the suite exceeds section 4's limit
of three saturated tasks — a real risk to suite size, not a detail. All 24 candidates
remain on disk so the unfiltered rate can still be computed.

### Haiku discrimination check: FIVE saturated tasks against a limit of three

Full evidence: `findings-2026-09-04-haiku-saturation.md`. Section 4 gate-time check, not section
5's scored row.

Haiku passed **8/8 on both trial 1 and trial 2** of the current suite. Counting only trials valid
for each task (trial 0 is excluded for g03 and g04, which were replaced after it):

    saturated 3/3:  g01, g02, t01, t02, t03      -> FIVE
    likely (2/2):   g03, g04                     -> needs a third trial each
    not saturated:  t04 (2/3, and only because trial 0 produced no answer file)

**Section 4 allows at most three saturated tasks and says the rest are replaced with harder
variants. The suite is therefore too easy**, and this is the single most consequential
thing this session learned after the GPU fault.

**Banked, not decided**, because it is structural. There are two defensible readings and they
imply different amounts of work. Taken literally, most of the suite needs re-authoring. But the
Haiku used here is a Claude Code subagent with full tooling that iterates and runs `python3`
against its own work — far stronger than the local arm it is meant to be a yardstick for (a 3-bit
27B at 48k fill, ~45 tok/s, 900 s wall), so a task can be saturated for agentic-Haiku and still
discriminate sharply among quants. The alternative is to re-run this check in a configuration
comparable to the local arm, or to accept the saturation and report it as a stated limitation of
the ranking. **Report the saturation explicitly rather than implying the check had passed.**

Keep all 24 candidates: section 7 needs Haiku's rate over every task authored **including** the
saturated ones, because a set built by discarding what Haiku passes is circular, and that is the
number carrying the comparison.

### The x3 prompt-defect check found two real ambiguities

Three independent Haiku readers, given only the prompts and asked to find ambiguity rather than
attempt the tasks:

- **t01, flagged by two of three, on two different grounds** — the worked example uses
  single-slash paths while the material uses `//infra/handbook/oncall.md`, and "standalone
  occurrence" is used throughout and never defined. Both are checkable and both are real. **Tighten
  t01.**
- **t04, flagged by one** — "the smallest contiguous line span containing the implementation" has
  no correct answer for a split implementation. Latent rather than live: the current t04 candidate
  is the negative variant and never needs a span. Fix it if a positive variant is ever used.

g01-g04, t02 and t03 read CLEAR to all three. Neither finding invalidates any recorded gate
result. Three readers were used rather than one deliberately: a lone reader answering "CLEAR"
everywhere cannot be distinguished from one that did not look, and in the event two found
different things.

## 2026-09-04, later — saturation count corrected, and t01's gate rows invalidated

### Saturation is seven of eight, not five and not six

`findings-2026-09-04-haiku-saturation.md` has been corrected, with the evidence written onto the
page so the count can be re-checked without re-running anything. Two errors were fixed:

1. **g04's trial 0 was wrongly excluded.** g03 and g04 were replaced at *different* times, and
   trial 0 already ran g04's current cand-1. Evidence: `gate-haiku/trial-0/g04/` holds `invoice.py`
   (cand-1's seed; cand-2 is `router.py`, cand-3 is `report.py`), and `check_style.py` there is
   md5 `0232a79e3b5cef2e23d23dc910110834`, identical to `gate-suite/g04/seed/check_style.py`.
   g03's exclusion was correct by the same test (`note_*.py` = cand-3, current is `badge_*.py`).
2. **g03's third trial has since been run and passed** 12/12 `VERDICT correct`.

So g01, g02, g03, g04, t01, t02, t03 are saturated; only t04 is not, at 2/3, and its one failure is
genuine (identical `auth.py` md5 across all three trials; on trial 0 it reasoned correctly but
wrote no `answer.txt`). **Seven saturated against a section 4 limit of three.**

### The "broken proxy" explanation is now closed off

One-shot Haiku — explicitly forbidden to run `python3` or verify its own output — still passed
**8/8**, every task `VERDICT correct`. Compliance was verified, not assumed: zero `python`/`pytest`
calls across all eight runs' tool logs. The suite is therefore saturated against a Haiku with one
pass and no feedback, not merely against an agentic one. Recorded as a clearly-labelled third
condition; it does not replace the agentic numbers, which remain the basis of the section 4 flag.

**Still not this session's call to make.** The structural choice — take section 4 literally and
re-author most of the suite, or record saturation prominently as a limitation and rank anyway —
remains open. Both readings remain on the findings page.

### t01's previously recorded Sonnet and GLM gate rows are INVALIDATED

t01's prompt was tightened this session to fix two flagged defects (the undefined term "standalone
occurrence", and an under-specified verbatim-copy rule). **A changed prompt is a changed task, so
t01's earlier Sonnet and GLM gate rows no longer describe the task in the suite and must not be
cited.** They are superseded by the re-gate below; the old numbers stand only as history.

### A checker defect was scoring correct answers as `visibly_failed`

Re-gating t01 on GLM first returned 1/3, then 0/3, then 1/3 — 2/9 — against a pre-edit record of
5/6. **I wrote here that this was a regression my prompt edit had caused. That was wrong, and I am
retracting it.** The prompt edit was not the cause. The cause was a defect in t01's checker.

The diagnosis was made from evidence, not inference. `pibench.py` deletes each sandbox after
grading, so a `PIBENCH_KEEP` diagnostic hook was added to preserve them (default-off; the normal
path is unchanged) and GLM's actual `reference_audit.txt` bytes were captured across three trials.
**All three files were identical in content** — the correct four records, correct UPDATE/LEAVE,
correct paths, correct literal tabs. The only difference between the passing file and the two
failing ones was a **trailing newline**.

t01's parser contained this guard:

    if len(lines) != len(_ORA_EXPECTED) or raw != raw.rstrip("\n") + "\n":
        return None

which requires the file to end in exactly one newline. A file with no trailing newline was rejected
as `unparseable`, scored `SCORE 0/8`, and labelled **`VERDICT visibly_failed`** — while being a
completely correct answer. The prompt asks for "exactly four lines" and never says the file must
end in a newline, so both forms satisfy it.

**Why this mattered far beyond t01.** Section 7's headline instrument is the three-way split
`correct` / `visibly_failed` / `confidently_wrong`. A checker that files correct work under
`visibly_failed` corrupts that instrument directly, and it does so *selectively*: it penalises
whichever models happen not to emit a trailing newline. Sonnet emitted one in all three re-gate
runs, which is precisely why the defect stayed invisible through every earlier gate — the checker
had encoded a Sonnet-shaped habit as a correctness requirement. Had this reached the grid it would
have produced a systematic, model-dependent bias in the primary metric.

**Fix.** The parser now strips at most one optional trailing newline and stays strict about
everything else. Verified against five shaped inputs: no trailing newline → `correct`; one trailing
newline → `correct`; two trailing newlines → `visibly_failed`; a blank line inside → `visibly_failed`;
three records instead of four → `visibly_failed`. Propagated to `tasks-v5/t01/cand-3/test.py`;
`verify_candidates.py` re-run clean at **REF 24/24, EMPTY 24/24**.

Only t01 had this guard — the other seven checkers were grepped and none constrains trailing
newlines.

### t01's re-gate, after the checker fix

| model | result | status |
| --- | --- | --- |
| Sonnet, 3 trials (`gate-t01-regate/trial-{0,1,2}`) | 3/3, each 8/8 `VERDICT correct` | **rule 1 satisfied** |
| GLM 5.3 Flash, 3 trials (`gate-glm-t01-fixed`) | 3/3, each 8/8 `VERDICT correct` | **rule 1 satisfied** |

The Sonnet rows were re-graded against the fixed checker rather than assumed to carry over. t01
holds a valid gate on the tightened prompt, and **the suite is gate-complete again**: Sonnet 3/3 on
all eight, GLM ≥2/3 on all eight.

No section 4a question arises. Nothing was kept, dropped, reworded or reordered because a quant
passed or failed: a checker was mislabelling correct answers, and rule 1 governs that expressly —
"that is a *task* defect, never evidence about a quant". The gate models are not quants.

Diagnostic artefacts are kept under `authoring/t01-diag/` (the preserved sandboxes and the
`run_keep.py` wrapper) so the finding can be re-checked.

**Trap worth recording for later sessions.** `VAR=x /mnt/c/.../python.exe ...` does **not**
propagate `VAR` from WSL into a Windows process unless it is listed in `WSLENV`; the variable is
silently absent and the run looks like it simply ignored the setting. Set it from inside the
Windows process instead — `authoring/t01-diag/run_keep.py` is the working pattern.

## 2026-09-04, later still — the context axis does not currently vary what it claims to

Section 4's discrimination check had only ever been run against **unpadded** sandboxes (~2k), a
configuration the grid never runs. Two more Haiku rows were run at 48k requested fill, one trial
across all eight tasks, agentic so they compare to trials 0-3.

**Both rows passed 8/8.** The count is unchanged: seven of eight saturated on every condition now
tried — unpadded agentic, unpadded one-shot, and both padded rows.

### A padding defect was found and fixed before the second row

The original filler was written as `__pibench_pad_NNNN.{py,md}`, flat at the sandbox root. Either
the name or the position lets a model exclude the whole fill in one glob and be left with the
unpadded sandbox — on t01 especially, where the real material is in `docs/` and `history/`. A grid
with excludable padding yields a curve flatter than reality, **and the flatness looks like a
finding**. The first 48k row is therefore recorded as **inconclusive on the padding axis** and must
not be cited as having closed the fill question.

Fixed in `pibench.py`: filler is named like real material and distributed into the seed's own
directories (cache/build dirs excluded so nothing lands in `__pycache__`), deliverable names are
never shadowed, and padding is identified by a `pad_files` manifest in `padding.json` rather than by
filename. The row was then re-run once.

### The measurement, and why it outranks the Haiku row

Achieved fill is now recorded per task from the model's own reported prompt tokens
(`input + cache_read + cache_creation`, peak across assistant messages), via `measure_fill.py` /
`merge_fill.py`. The `est_tokens_after` char-based estimate was **removed** from the artifacts
rather than kept alongside, because it reads like a measurement and is not one.

**~48,000 tokens of material were written per task; median achieved fill was 22,669 against an
unpadded floor of 18,603. Padding contributed about 4,100 tokens — under 10% of what was written.**
Padding on disk only enters context if the model reads it, and an agentic arm reads what it needs.
t04 is the lone exception (37,555 tokens, 32 tool calls) because its negative question genuinely
requires searching the tree.

**Consequence, and it is bigger than the saturation question.** As specified, a 24k cell and a 64k
cell would both land near ~20-25k of achieved fill for an agentic arm, so the context axis would
produce a near-flat curve for reasons unrelated to the quants under test. Any reading of
"performance holds up at 64k" would be unfounded.

**Banked, not decided — this is a plan-level change and it is the owner's.** Options, with a
recommendation: (a) put the fill in the **prompt** rather than on disk, which guarantees occupancy
and is what I would recommend if the context axis is to mean anything; (b) author tasks that
*require* wide reading, as t04 incidentally does; (c) keep disk padding but **verify achieved fill
per trial** and discard or re-label any trial that missed its target — the cheapest, and it at least
stops the harness reporting fills it never achieved. In every case, trials must record achieved fill
and the grid must be read against that number rather than the cell label.

**Saturation at genuine 48k+ occupancy remains untested and cannot be tested by writing filler to
disk.** The two rows remove an objection to the literal reading of section 4 without settling it.
The choice between the two readings remains open.

## 2026-09-04, local calibration — the context axis is dead on the arm that matters

My earlier fill numbers were taken on a Claude Code subagent arm with an 18,603-token floor. The pi
arm's floor is ~2k per plan section 4, so that table could not be carried across. Section 6 step 3
local calibration was run on the pi/Ollama arm to settle it. **Calibration only — no pass/fail from
these runs is reported or citable, per 4a.** `OLLAMA_KV_CACHE_TYPE=q4_0` was set with a restart
before and reverted to `q8_0` with a restart after; one model resident at a time.

| cell | g01 achieved fill | t04 achieved fill | residency |
| --- | --- | --- | --- |
| Q2_K_L 24k | 4,701 | 10,527 | 11.83 GB, 100% GPU, peak 13,362 MiB, 59.1 tok/s |
| Q2_K_L 64k | 3,836 | 9,382 | 13.35 GB, 100% GPU, peak 14,612 MiB, 59.4 tok/s |
| Q3_K_S 64k | 7,051 | 12,640 | 14.70 GB, 100% GPU, peak 15,769 MiB, 53.3 tok/s |

**Raising the cell 24k → 64k at fixed quant lowered achieved fill slightly (4,701 → 3,836 and
10,527 → 9,382) while the padding written rose 2.67x.** Cell label and achieved fill are
uncorrelated. On the local arm the axis is worse than on the Claude arm, where padding at least
moved the median by ~1,000 tokens.

**Consequence.** A 24k row and a 64k row would measure the same thing, so the grid's context axis
would produce a flat curve as a harness artefact. **Putting the fill in the prompt is now the only
workable option**; verifying achieved fill per trial and discarding misses degenerates, because on
this evidence every trial would be discarded. The variation that does exist tracks the *task* —
t04 draws ~2.5x g01's fill in every cell because its negative question requires searching the tree.

**Still open:** the plan change itself and the choice between the two saturation readings.

**Deviation:** the brief named `q27-Q3_K_S-24k`, which did not exist and was not mine to build, so
the same-quant comparison used Q2_K_L (both cells present). `q27-Q3_K_S-64k` was run as asked.

## Correction — "fifteen grid model tags: done" was false

`schedule.md` and `findings-2026-09-04-grid-harness-gap.md` both recorded the fifteen grid tags as
built. `ollama list` on the Windows daemon showed **three** cell tags, two of which predate this
session — so the `make_grid_models.sh` run produced exactly **one**. The script is correct and its
tag is correct (`num_ctx 24576`, `num_gpu 66`); this was an unfinished run written up as finished.
Both documents are corrected in place with the retraction left visible.

This is the third claim this session whose evidence did not cover it. The hazard was not cosmetic:
`ollama list` also carries five suffix-less base tags, so a later session starting run 1 on the
"done" line would have had twelve of fifteen cells fail outright, or silently fall back to a base
tag baking `num_ctx 32768` with no `num_gpu` — the exact mis-measurement the harness-gap page exists
to prevent. **Confirm tags with `ollama list` immediately before run 1; do not trust the table.**

## 2026-09-04 — the fill fix is built and its acceptance test PASSED

The owner decided the mechanism: fill is delivered **in the prompt**, not on disk. Built as
`pibench.py --fill-tokens N` (target for the whole prompt); `--pad-tokens` is demoted to sandbox
realism and no longer sized to the cell. Rules held constant across every cell and task: the
instruction is byte-identical and taken verbatim from the frozen `prompt.md`, it always leads with
the extra material after it, and that material is never labelled as filler — it is presented as
further project context, because anything reading as "ignore the following" gets ignored.

Acceptance on `q27-Q3_K_S`, quant held constant, achieved fill from reported prompt tokens:

| cell | g01 | t04 |
| --- | --- | --- |
| 24k (target 24,000) | 23,427 (97.6%) | 22,383 (93.3%) |
| 64k (target 64,000) | 57,871 (90.4%) | 57,857 (90.4%) |

Both criteria met: every trial past 90%, and 64k far above 24k for the same task where the old
mechanism went *down*. All trials 100% GPU-resident. Calibration only; no pass/fail is citable, 4a.

**Two harness faults fixed on the way, both worth remembering.** A prompt over 32,767 chars cannot
be passed as an argv on Windows — the first attempt died at spawn with `WinError 206` and wrote
`"runs": []`, which reads like "the fix failed" but means no request reached the model; large
prompts now go to a file via pi's `@file`. And `PAD_CHARS_PER_TOKEN = 5.95` was 28% wrong for this
purpose: measured 4.664, which matters because sizing on 5.95 overflows `num_ctx` and truncates
silently. `FILL_CHARS_PER_TOKEN` is now separate.

**Banked for the owner, not decided.** At the 64k cell the agentic loop collapsed to **one turn**
(against 5-6 at 24k), because ~57.9k of a 65,536 window is prompt and only ~7.6k remains for the
tool loop. The 64k end of the axis therefore measures *less room to work*, not merely more to read.
That is a property of running a 64k cell on a 64k window rather than a defect in the fill fix, but
it changes what a 64k row means and the plan does not currently say which is intended. Options:
run 64k cells on a larger window, accept and report the constraint, or cap fill at a fraction of
the window. Not taken.

**Also banked:** `/api/generate` silently truncates a prompt to exactly half `num_ctx` (observed
12,290 on a 24k cell and 32,770 on a 64k cell). pi's own path does not. Anyone calibrating through
that endpoint will get half the fill they asked for and no warning.

## 2026-09-04 — discrimination at real fill, six tasks sized, t04 fixed and re-gated

### Saturation holds at genuine context fill (seven of eight, unchanged)

The discrimination check was re-run with prompt-side fill, paired with a Sonnet row at identical
fill now that the Sonnet restriction is lifted. Median achieved context rose from 18,603 (unpadded)
to **49,210 for Haiku** and **62,656 for Sonnet**. Both passed **8/8**. The "only saturated because
the context was empty" objection is closed; the count stays seven of eight and the structural
choice stays the owner's.

**Bounded claim, recorded deliberately.** Sonnet runs spontaneously described the filler as
"decoy"/"boilerplate"/"unrelated filler". It is realistic in form but generic in content, so these
rows prove the tasks survive *recognisably* irrelevant context, not plausible-but-wrong material
that must be disambiguated. Filler drawn from the same project as the answer would be a sharper
instrument. Not changed mid-measurement; flagged for the owner.

### Section 6 step 3 local calibration — the six unsized tasks are now sized

`q27-Q3_K_S-24k`, prompt-side fill 20k, one trial each. Calibration only; no pass/fail citable, 4a.

| task | achieved fill | % of 24k | wall | output tokens |
| --- | --- | --- | --- | --- |
| g02 | 23,459 | 97.7% | 32.0 s | 557 |
| g03 | 22,508 | 93.8% | 51.3 s | 1,708 |
| g04 | 22,228 | 92.6% | 43.2 s | 1,361 |
| t01 | 22,390 | 93.3% | 40.5 s | 1,236 |
| t02 | 22,083 | 92.0% | 39.2 s | 1,191 |
| t03 | 21,462 | 89.4% | 24.7 s | 127 |

All 100% GPU-resident, peaks 14,209-14,515 MiB. **Both never-checked questions are answered:
appetite is fine — 127-1,708 output tokens against a 5,000 ceiling — and the wall is fine, 24.7-51.3 s
against a 300 s limit.** With g01 and t04 from the earlier round, all eight tasks are now sized
against a local quant. Section 6 step 3 is complete for the 24k cell.

### t04's latent prompt defect is fixed and t04 is re-gated

"Cite the smallest contiguous line span containing the implementation" had no correct answer when an
implementation is split across non-contiguous regions or files. The prompt now says to cite the
single contiguous span holding the largest part and to name the rest in `EXPLANATION`, so there is
always exactly one span to give. Propagated to all three copies (md5 `4d9cca5a`).

**A changed prompt is a changed task, so t04's earlier gate rows are invalidated**, exactly as with
t01. Re-gated alone: **Sonnet 3/3, GLM 3/3** — rule 1 satisfied.

Note for the record: the Haiku and Sonnet fill rows above used the **pre-fix** t04 prompt, since
their prompts were composed before the edit. That is internally consistent (both rows used identical
prompts) and does not affect the saturation count, but the fill rows and the t04 gate rows are not
from the same prompt revision.

## 2026-09-04 — the 64k KV question is settled on capacity, and the plan's prediction is falsified

`kv-probe-plan-2026-09-03.md` predicted both q8_0 cells would fail to fit at 64k. Both fit, fully
resident, no CPU spill: q27-Q3_K_S-64k at 14.70 GB and q27-IQ3_M-64k at 15.11 GB, 100% GPU under
q8_0 on a 16,303 MiB card.

**And the cache setting made no measurable difference.** Repeating the load under q4_0 gave
*identical* resident sizes (14.70 / 15.11 GB); nvidia-smi differed by 6-42 MiB, noise against a
15.9 GB working set. `OLLAMA_FLASH_ATTENTION=1` is set and the tags bake only `num_ctx`/`num_gpu`,
so the usual explanations do not apply. Either Ollama ignores `OLLAMA_KV_CACHE_TYPE` for gemma-3's
sliding-window attention, or the difference is too small to see; this evidence cannot separate them.

**Operationally identical under both readings:** there is no capacity reason to prefer q4_0 at 64k,
and the schedule's mandatory "q4_0 before every cell, q8_0 after" ritual is **not buying anything
measurable**. Worth knowing before that ritual is cited as a controlled variable — every run this
session that observed it was unaffected by it.

**Banked, not taken:** whether to drop the ritual, keep it as cheap insurance, or first determine
whether the variable does anything at all. Cache quality is untested and, if the setting is inert,
untestable this way. Left at the fleet default q8_0.

## 2026-09-05, Opus manager session — machine verified, suite re-banded, two checker defects found

Opened from `plan-2026-09-05.md` and `handoff-2026-09-05.md`. Skills `org`, `codex-run` and
`agent-runtime` invoked before the first action. Under plan section 10 every decision on this page
is the manager's; each is recorded with its reasoning and none was banked.

### Machine state, verified by a real load rather than a version string

    nvidia-smi         RTX 5080, 1768 MiB / 16303 MiB used, idle
    real load          q27-Q3_K_S-24k, 3213 eval tokens, 52.20 gen tok/s
    ollama ps          14.15 GB resident, pct_gpu 100%, context 24576
    nvidia-smi peak    15583 MiB

52.20 tok/s sits on the Q3_K_S curve in `results/gpu-tune/summary.md` and matches the 52.7 tok/s
measured after the CUDA repair, so the GPU is genuinely serving. The model was unloaded with
`keep_alive: 0` afterwards and the card returned to 1768 MiB. Script: `gpu_verify.py`.

**Grid tags confirmed from the daemon, not the table.** `/api/tags` on the Windows Ollama returns
21 models: the fifteen cell tags (Q2_K_L, Q3_K_S, IQ3_M at 24/32/48/64k; Q3_K_M at 24/32/48k), the
five suffix-less base tags the handoff warns about, and the upstream GGUF repo tag. All fifteen
present.

### THE RE-BANDING RESULT: every task in the suite is far below the smallest band

Plan section 3.2 requires each task's real material size measured and recorded before any GPU
cell, in bands of small 4k-8k, medium 12k-20k and large 30k-45k tokens. Measured with
`authoring/measure_material.py` over every file under each candidate's `seed/`, at the suite's
own measured constant of **4.664 characters per token**. Full table:
`authoring/material-sizes-2026-09-05.json`.

| task | selected candidate | material tokens | band |
| --- | --- | --- | --- |
| g01 | cand-2 | 537 | below small |
| g02 | cand-3 | 1,722 | below small |
| g03 | cand-1 | 283 | below small |
| g04 | cand-1 | 367 | below small |
| t01 | cand-3 | 174 | below small |
| t02 | cand-2 | 301 | below small |
| t03 | cand-3 | 6,235 | **small** |
| t04 | cand-3 | 195 | below small |

Across all 31 candidates the range is **149 to 7,637 tokens**. Exactly three of the thirty-one —
t03's cand-1, cand-2 and cand-3 — reach even the small band. **Nothing in the suite reaches the
medium band and nothing comes within a factor of four of the large band.**

**This corrects the plan.** Section 3.2 states that "t03 already belongs to the medium band by
construction — eight graded facts out of a 12k-token document" and holds it up as the model for
the others. Measured, t03's selected candidate is **6,235 tokens**, about half that, and it is in
the small band. The claim was an estimate that was never measured; it is now measured and it is
wrong by roughly 2x.

**Consequence, and it reshapes the campaign.** Re-banding was scheduled as a cheap bookkeeping
step — measure, record, move on. It is not: the measurement says the medium and large bands are
**empty**, so there is no context axis to run at all until material-heavy tasks exist. Authoring
is therefore the campaign's critical path, not a side quest, and it serves desaturation at the
same time because "more material to hold at once" is the first lever on the plan's own ladder
(section 2.3).

### Decision: two bands with the same eight task families in both, not three bands with different tasks in each

Taken under section 10; the alternative was banked by nobody because it is mine.

The plan's section 3.4 concedes that a band populated by "the tasks that genuinely need it" makes
the grid ragged and the bands non-comparable: a small-band score and a large-band score would be
over **different tasks**, so any difference between them confounds context with task identity.
Given that every existing task is below the small band anyway, that confound is avoidable at no
extra cost:

- **small band** — the eight existing task families at their measured sizes, run at 24k;
- **large band** — a new `cand-5` per family, the *same question over 30k-45k tokens of real
  material*, run at 64k.

The context curve is then measured **within a task family**, which removes the confound entirely,
and two well-populated bands beat three thin ones. The medium band is populated later only if
time allows; it is a refinement of a curve, not a precondition for having one.

Cost, stated honestly: the small band's material (174-6,235 tokens) is below the plan's own 4k-8k
floor, so "small" here means "the task's natural size", and every report of it must give the
measured number rather than the band name.

### Eight authoring runs dispatched, and the contract they run under

`authoring/CONTRACT-2026-09-05.md` written and dispatched with eight parallel Luna runs
(`gpt-5.6-luna`, high effort), one per task family, briefs in `briefs/author-<id>-cand5.txt`.
It amends `CONTRACT.md`: synthetic fill withdrawn (A1), the band table and the exact
character-count measurement method with a `MANIFEST.json` deliverable (A2), the 1.6x
working-margin rule (A3), the difficulty ladder with ambiguity excluded (A4), the standing
"more reading, not more writing" sizing limits (A5), the negative-answer requirement (A6),
and the mandatory near-miss probe (A7).

### TWO CHECKER DEFECTS IN THE LIVE SUITE, found by probing rather than by report

The handoff's standing instruction — probe every strict-format checker with a deliberately shaped
near-miss set before trusting it — was carried out with a new tool, `authoring/probe_checkers.py`.
It builds the reference sandbox, works out which files the reference produced or changed, and
re-runs the checker once per perturbation that the prompt does not forbid: no trailing newline,
one extra trailing newline, CRLF, a leading blank line, trailing spaces.

**Run against the live `gate-suite/` — the eight already-gated tasks — it found six failures on
two tasks:**

    t01  extra_trailing_nl / leading_blank / trailing_spaces on reference_audit.txt -> SCORE 0/8, visibly_failed
    t04  extra_trailing_nl / leading_blank / trailing_spaces on answer.txt          -> SCORE 0/4, visibly_failed

A **completely correct** answer scored zero and was labelled `visibly_failed` because it carried
an invisible trailing space or one blank line. This is the same class as the trailing-newline
defect fixed on 2026-09-04 and it is the same instrument it corrupts: `visibly_failed` and
`confidently_wrong` are the headline rates and they outrank pass rate. The 2026-09-04 fix
addressed only the *missing* newline; the probe confirms that case now passes and that the three
opposite cases did not.

It matters because the bias is model-dependent, exactly as before. Emitting a trailing blank line
is a habit some models have and others do not, so the defect silently penalises one arm.
`verify_candidates.py` cannot catch it: it checks a reference written by the same hand and the
same habits as the checker, which is why a probe that perturbs a *correct* answer is a different
instrument and not a duplicate one.

**Fixed** by `authoring/fix_answer_parsers.py`, which is idempotent and re-runnable. It normalises
only what the prompt does not specify — a UTF-8 BOM, the line-ending convention, and leading and
trailing blank lines — plus, for t04 only, trailing whitespace on each line. t01 deliberately
keeps trailing whitespace significant **inside** a line: its fields are tab-separated and the last
one is a replacement string the prompt requires verbatim, so a space there is real content.

Applied so far to `gate-suite/t01`, `gate-suite/t04`, `round1/suite/t01` and `round1/suite/t04`.
**Not yet applied to the `tasks-v5/t01/cand-*` and `tasks-v5/t04/cand-*` sources**, because eight
Luna authoring runs held that tree at the time; propagating it there is owed and is listed in the
handoff.

### Three probe hits adjudicated as NOT defects, so they are not re-litigated

The probe is deliberately blunt and over-applies. Each survivor was read rather than assumed:

- **g04, trailing spaces on `invoice.py`/`policy.py`.** g04's task *is* to make a supplied style
  tool report clean, and that tool's rule at line 11 is `if line.rstrip(" \t") != line: "trailing
  whitespace"`. Adding trailing spaces legitimately fails a graded subcheck. Correct behaviour.
- **g03, trailing spaces on `badge_core.py`/`event_core.py`.** The failing subcheck is `doctest`,
  and a doctest's expected output is whitespace-sensitive by language design. Correct behaviour.
- **t01, trailing spaces on `reference_audit.txt`.** The perturbation lands in the verbatim
  replacement field. Real content, correctly rejected.

So the perturbation set is right and the adjudication is per task: a source file being graded for
style or by doctest is legitimately whitespace-sensitive; a line-oriented answer file is not.

## 2026-09-05 — desaturation round 1, the variant sweep, and a task that could not be answered

### Round 1: the seven `cand-4` harder variants, Haiku x3

`authoring/round1/` — the seven saturated tasks swapped to their `cand-4` variants, t04 left at
cand-3. Built, prepped and graded by `authoring/round.py`, which does exactly what
`prep_gate_sandboxes.py` did but takes a suite mapping and per-trial suites.

| task | candidate | Haiku passes | verdicts |
| --- | --- | --- | --- |
| g01 | cand-4 | 3/3 | correct x3 |
| g02 | cand-4 | 3/3 | correct x3 |
| g03 | cand-4 | **1/3** | confidently_wrong, confidently_wrong, correct |
| g04 | cand-4 | 3/3 | correct x3 |
| t01 | cand-4 | 2/3 -> **3/3 corrected** | see below |
| t02 | cand-4 | 3/3 | correct x3 |
| t03 | cand-4 | 3/3 | correct x3 |
| t04 | cand-3 | 3/3 | correct x3 |

**21/24 = 87.5% as run; 22/24 = 91.7% once t01's row is corrected.** Against a target of about
80% (19-20 of 24) that is movement but not arrival: the `cand-4` variants were authored to be
harder rather than larger, and only **g03/cand-4 genuinely discriminates**.

t01's single failure was not difficulty. Its prompt asked for lines "ordered by POSIX relative
source-file path"; its checker enforces byte order, in which `README.md` precedes
`docs/links.md`. A trial produced **all seven classifications correctly**, sorted
case-insensitively, and scored `0/14` `visibly_failed`. Unstated convention, banned by section
2.3. The prompt now states the ordering exactly (`fix_t01_sort_ambiguity.py`), the old rows are
invalidated, and t01 re-ran **3/3** under the corrected wording (`authoring/round1-t01fix/`).

### The variant sweep: is a harder variant already on disk?

Before commissioning anything, the sixteen candidates not in any suite were run once each with
Haiku (`authoring/sweep/`). Cheap, parallel, and it maps the difficulty of what already exists.

**13 of 16 passed.** The three failures:

- **t04/cand-2** — `SCORE 3/4`, `confidently_wrong`, failing `cited line span`. A genuine
  wrong-answer-confidently-given, which is the shape the headline instrument exists to measure.
- **t04/cand-1** — `SCORE 3/4`, `confidently_wrong`, failing `explanation`. **Not genuine.** The
  checker required the literal substring `expired` or `expiry`; the trial wrote "when the
  session's `expires_at` has passed", which names the expiry decision exactly as the prompt
  requires. Fixed to stem matching (`fix_unstated_conventions.py`).
- **t03/cand-1** — `SCORE 0/8`, `visibly_failed`. See below; it is the largest finding on this
  page.

So the existing candidate space contains **one** genuinely harder item (g03/cand-4) plus t04's
positive variants. Everything else is saturated. That is the measurement that makes the
large-band `cand-5` authoring the campaign's critical path rather than an option.

### Decision: rotate t02 and t04 across their variants

The handoff banked this as structural. It is the manager's under section 10 and it is taken.

As single items each is one bit: t02/cand-2 always answers "yes", t04/cand-3 always answers
"no". A model that guesses that bit and holds it scores 3/3 for the wrong reason on all three
trials, and the guess is never punished. Round 2 therefore rotates:

    trial 0   t02 <- cand-2 (positive)   t04 <- cand-1 (positive)
    trial 1   t02 <- cand-4 (negative)   t04 <- cand-2 (positive)
    trial 2   t02 <- cand-1 (negative)   t04 <- cand-3 (negative)

**Arity is unchanged** — each task still contributes three trials to the denominator — so
section 7's verdict rule needs no amendment. `round.py` grows per-trial suites (`suite-0/`,
`suite-1/`, `suite-2/`) to support it, and each trial is graded against the variant it was
given. It also keeps a negative correct answer in the comprehension class, which section 2.3's
ladder requires of at least half the variants.

### THE BIGGEST TASK DEFECT OF THE SESSION: t03/cand-1 asserts values its material does not contain

Round 2 put t03 on `cand-1`, the largest-material candidate in the suite (7,637 tokens). It
failed on every arm. The reason is not difficulty.

**Its reference answer gives `incident_date` as "2031-04-17". That string does not appear in its
seed material. Neither does "2031". Neither does any ISO date, in any format, anywhere.** The
prompt says in terms: "Do not infer or calculate facts that are not stated there." So there was
no correct answer to give.

**Five independent trials across two model families all reported this**, which is as strong as
this kind of evidence gets. The Sonnet guard arm was explicit: "No incident date appears anywhere
in the record (verified via exhaustive numeric/date-pattern search), so per the instruction not
to infer facts not stated, incident_date was set to 'not stated in the record' rather than
fabricated." That is section 2.2 working exactly as designed — a task Sonnet fails is under
suspicion of being broken, not hard — and the reading confirms it.

A second field was wrong the same way. The material says "delayed telemetry writes **affecting**
12.4% of eu-west-2 tenants" (seed line 101); the reference demanded "delayed telemetry writes
**for** 12.4% of eu-west-2 tenants", a wording that appears nowhere. The reference paraphrased
its own material — while the prompt, as amended today, requires values copied verbatim.

**And the failure was total rather than partial.** A non-string value trips the checker's shape
gate, so a trial that got six of eight fields right scored `0/8`, not `6/8`, and was labelled
`visibly_failed`. The headline instrument was being fed a fabricated failure.

**Why nothing in the tree could catch it, and the new instrument that does.**
`verify_candidates.py` copies `ref/` into the sandbox and runs the checker, so the reference
passes by construction whatever it asserts — it never asks whether the *material* supports the
assertion. `probe_checkers.py` perturbs a correct answer and inherits the same blind spot.
`selfcheck.py` executes the prompt's examples against `ref/`, not against `seed/`. All three
agree with each other and all three are wrong together.

`authoring/check_derivable.py` is the missing check: for every JSON reference answer, take each
leaf value, normalise whitespace and case, and search the concatenated seed material for it,
with tolerant forms for numbers and dates. It flags t03/cand-1's two values and clears every
other reference answer in the tree, including the new `cand-5`s.

One correction worth recording, because it nearly produced a clean bill of health: the first
version's date fallback also accepted the bare year and the bare day-of-month, which match
almost any prose. It passed the fabricated date. **A tolerant check that tolerates everything is
worse than no check, because it reads as a clean result.** Tightened to whole-date alternates
only.

**Fix taken** (`fix_t03c1_unanswerable.py`): `incident_date` removed from the prompt, the
checker's field list, the accept table and the reference; `impact_scope` corrected to the
material's own wording; `_ora_total` corrected from 8 to 7, which had been hardcoded and was
inflating the denominator. The task keeps its real difficulty — the `detection_channel` trap
("canary" against "synthetic canary") and the customer-minutes decoys that Sonnet had to
separate — and is now answerable. t03's earlier rows are invalidated and were re-run.

### A mistake of mine, and the tool change that prevents it recurring

To fix t03 I re-prepped the whole round-2 arm. **`round.py prep` deletes and recreates every
sandbox it touches**, so that destroyed roughly twenty completed-but-ungraded reference-model
runs — the entire Sonnet trial 0 and trial 1, and most of Haiku trial 2 — for the sake of one
task. The graded `results.json` files survived; the work did not.

`prep` and `grade` now take an optional task list, and a **scoped grade merges** into the
existing `results.json` instead of replacing it, so re-grading one task can no longer turn the
other seven into failures against emptied sandboxes. The lost runs were simply re-run.

### GPU: local calibration on the small band with no fill at all

Plan section 5 step 3, run while the cloud arms worked. `q27-Q3_K_S-24k`, the eight tasks of the
current `gate-suite`, one trial each, **no `--fill-tokens`, no `--pad-tokens`** — the
configuration plan section 3 leaves as the only scored one. Artifact
`results/calib-nofill-24k-q3ks.json`.

| | range across the eight tasks |
| --- | --- |
| wall | 11.9 - 29.3 s against a 300 s limit |
| output tokens | 455 - 1,386 against a 5,000 ceiling |
| turns | 4 - 5 (never single-turn) |
| tool calls | 4 - 7 |
| residency | 13.18 GB, **pct_gpu 100** on every trial |
| nvidia-smi peak | 15,585 - 15,593 MiB |
| gen tok/s | 52.5, on the Q3_K_S curve |

Every never-checked question in step 3 is answered and all of them comfortably: the tasks fit,
the appetite is a fifth of its ceiling, the wall is a tenth of its limit, nothing spilled to
system RAM, and the agentic loop did not collapse.

**The quant passed all eight.** That is recorded as calibration and nothing else, per rev 5.9
section 4a: no task was kept, dropped, reworded or reordered because of it, and no pass/fail from
it is citable as a result. It does, though, retire one specific worry the plan raised in section
2.1 — that Haiku might be an optimistic proxy and a suite tuned to Haiku-80% might floor every
quant. On this suite the quant is at the ceiling, not the floor. **Hardening is the safe
direction, and the plan's own risk clause is the thing that is now measured rather than
feared.** The hardening decision itself was the owner's ruling and predates this measurement, so
nothing here drives it.

## 2026-09-05 — desaturation round 2: the small band settles at Haiku 87.5%, Sonnet 100%

`authoring/round2/`, three per-trial suites so t02 and t04 rotate. Both arms, three trials each,
graded by `round.py`. **The final composition of the small band:**

| task | candidate(s) | Haiku | Sonnet | note |
| --- | --- | --- | --- | --- |
| g01 | cand-4 | 3/3 | 3/3 | saturated |
| g02 | cand-4 | 3/3 | 3/3 | saturated |
| g03 | cand-4 | **1/3** | 3/3 | **the suite's sharpest task**; two `confidently_wrong` |
| g04 | cand-4 | 3/3 | 3/3 | saturated |
| t01 | cand-4 | 3/3 | 3/3 | saturated, sort ambiguity fixed |
| t02 | rotating cand-2 / cand-4 / cand-1 | **2/3** | 3/3 | one `confidently_wrong` on cand-1 |
| t03 | cand-3 | 3/3 | 3/3 | saturated; cand-1 withdrawn as broken |
| t04 | rotating cand-1 / cand-3 / cand-3 | 3/3 | 3/3 | cand-2 withdrawn as broken |

    Haiku   21/24 = 87.5%
    Sonnet  24/24 = 100.0%

**The guard holds with room to spare** — Sonnet 100% against a floor of 90%, and it holds on the
two tasks Haiku fails, which is what makes those failures difficulty rather than ambiguity.

**The target is not met.** The plan asks for about 80%, 19 or 20 of 24. 87.5% is real movement
from the 23/24 (95.8%) the session inherited, and the two failures are genuine and both
`confidently_wrong` — the verdict the campaign most wants to be able to measure. But six of eight
tasks remain saturated, and **the existing candidate space is exhausted**: all 31 pre-existing
candidates have now been run at least once, and only g03/cand-4 and t02/cand-1 discriminate.

**Where the remaining movement has to come from, and it is already built.** The eight `cand-5`
large-band tasks carry 30,000-45,000 tokens of material against a small band whose median is
about 500. Difficulty by material is the plan's own first lever, and it is the one axis the small
band cannot exercise at all. They are authored and mechanically verified; they have no cloud gate
row. **Gating them is the next session's first job** and it is the only remaining lever that has
not been tried.

### Two variants withdrawn on guard evidence, and why that is the rule working

t03/cand-1 and t04/cand-2 were both dropped after a Sonnet failure was read rather than counted.
In both cases the model's answer was better justified by the prompt than the reference was: one
task demanded a date its material never contains, the other demanded a line span that excludes
half the behaviour its own prompt describes. Full evidence:
`findings-2026-09-05-unanswerable-tasks.md`.

Withdrawal rather than repair was chosen in both cases because the repair changes what the task
measures: t03/cand-1 has the same shape of defect on a third field, and making t04/cand-2's
reference agree with its prompt widens the answer to the point of triviality. Both stay on disk.

### The rotation worked, and the evidence is specific

t02 and t04 were rotated across their variants precisely so a model that guesses the yes/no bit
once cannot score three times for it. **t02's only failure is on cand-1, the variant that
occupies a different rotation slot from the one the previous suite used**, which is exactly the
information a single fixed item could not have produced. Arity is unchanged and section 7 needs
no amendment.

## 2026-09-05 — the large band exists: eight `cand-5` tasks, measured and verified

Eight parallel Luna runs against `authoring/CONTRACT-2026-09-05.md`. Material measured
independently with `measure_material.py`, not taken from the workers' `MANIFEST.json` — the two
agree exactly on all eight.

| task | material tokens | seed files | prompt words |
| --- | --- | --- | --- |
| g01 | 30,001 | 109 | 267 |
| g02 | 32,476 | 35 | 291 |
| g03 | 29,840 | 351 | 199 |
| g04 | 42,570 | 28 | 179 |
| t01 | 36,643 | 26 | 337 |
| t02 | 31,102 | 37 | 203 |
| t03 | 30,604 | 37 | 248 |
| t04 | 41,138 | 50 | 267 |

Seven are inside the large band (30,000-45,000); g03 is 160 tokens under the floor and its run was
still writing when this was measured. Every prompt is far inside the 2,000-word limit, so the
size is in the material rather than in the instruction, which is the point.

**Verified independently rather than taken on report:** `verify_candidates.py` over all 39
candidates now reports **REF 39/39 and EMPTY 39/39, no problems**, and `probe_checkers.py` over
the seven-task large-band suite finds **no format-strictness defects at all** — the A7 amendment
did its job at authoring time rather than leaving it to be found later.

**One worker report was false and independent verification caught it.** g04/cand-5's notes stated
"`test.py` against `ref/`: SCORE 10/10, PASS, VERDICT correct, exit 0" and listed all eight A7
probes as passing. Run independently, its reference scored **5/10**: the reference solution was
written to `ref/reconcile.py` while the checker requires `ref/src/reconcile.py`. Its did-nothing
sandbox also returned `confidently_wrong` where the contract requires `visibly_failed`, which
would have inflated the headline instrument for every quant that changed nothing. Both fixed
(`fix_g04c5_empty_verdict.py` hard-codes the pristine digest, as the rest of the suite does) and
both re-verified. A worker's answer is a claim.

**Two scope violations, both harmless and both removed:** an empty `ollama-bench/tasks-v5/t03/...`
tree nested inside `t03/cand-5`, and five empty directories at candidate level in `t01/cand-5`
duplicating names under its `seed/`. No file was lost. `git add -A` was not used at any point
while workers held the tree.

## 2026-09-05 — small-band bend-finding started

`results/bend-small-24k.json`: all four quants that reach 24k (Q2_K_L, Q3_K_S, Q3_K_M, IQ3_M)
against the round-2 small band, one trial per task, no fill, `q8_0` KV. This is plan step 4 for
the small band and it is the run the plan says to protect. Check whether it completed before
re-running it.

---

## 2026-09-05, Opus manager session — round 3, the large band, and the GPU cells

### D-R3-1. The large band is round 3, and it is `cand-5` for all eight families

Every `cand-5` authored under `authoring/CONTRACT-2026-09-05.md` measures in the large band by
`measure_material.py` (30,018 – 42,570 tokens of real material, 26–177 seed files). The pre-existing
`cand-1`…`cand-4` measure **tiny** almost everywhere — 149 to 770 tokens — with the sole exception of
`t03/cand-1..3` at 6.2–7.6k, which is the bottom of *small*. That is the whole re-banding finding in one
line: before this session the suite had no medium band and no large band at all, and what `schedule.md`
called "small" was tiny.

`round3/` is therefore the scored large-band suite:

| task | candidate | seed files | material chars | material tokens |
| --- | --- | ---: | ---: | ---: |
| g01 | g01/cand-5 | — | — | large |
| g02 | g02/cand-5 | — | — | large |
| g03 | g03/cand-5 | 177 | 140,004 | 30,018 |
| g04 | g04/cand-5 | 28 | 198,546 | 42,570 |
| t01 | t01/cand-5 | 26 | 170,904 | 36,643 |
| t02 | t02/cand-5 | 37 | 145,058 | 31,102 |
| t03 | t03/cand-5 | 37 | 142,739 | 30,604 |
| t04 | t04/cand-5 | 50 | 191,868 | 41,138 |

(the full table, with every candidate of every family, is `authoring/bands-2026-09-05.json` and
`authoring/material-sizes-2026-09-05.json`.)

### D-R3-2. The large band runs at 64k, and `Q3_K_M` is excluded from it

Plan section 3.3 asks for `num_ctx >= 1.6 x material`. 64k is the grid ceiling, so:

- **Q3_K_M cannot hold the large band at all.** It stops at 48k (section 4), and 48k is below 1.6x for
  every large task. It is not run there, and its absence is a **capacity** result, not a quality one.
- Six of the eight large tasks clear 1.6x at 64k. **Two do not**: `g04/cand-5` at 42,570 tokens wants
  68,112 (ratio 1.54) and `t04/cand-5` at 41,138 wants 65,821 (ratio 1.59). There is no larger tag,
  so the shortfall is **reported, not resolved**. Both are flagged in the artifact.

Trimming those two tasks' material to fit was rejected: section 4a forbids reshaping a task around what
a quant can hold, and the honest reading is that the 27B/64k configuration is *at* its ceiling on the
large band — which is exactly the measurement the campaign exists to take.

### D-R3-3. Two more format-brittle checkers, found by probing rather than by counting failures

`fix_answer_parsers.py` reported `NO MATCH -- inspect by hand` on four files after propagation into
`tasks-v5/`. Each was read, and the four split two ways:

- `t01/cand-5` and `t04/cand-5` are **legitimately clean**: authored under amendment A7, they already
  normalise. `probe_checkers.py` over a purpose-built suite confirms both: `clean`.
- `t01/cand-1` and `t01/cand-2` carry a **second parser shape** the fixer's pattern did not match:

      lines = raw.splitlines()
      if len(lines) != len(_ORA_EXPECTED) or raw != raw.rstrip("\n") + "\n":
          return None

  The `raw != raw.rstrip("\n") + "\n"` clause makes a single trailing newline **mandatory** and rejects a
  BOM, CRLF, and any leading or trailing blank line. Probed, both failed all four whitespace near-misses
  — `no_trailing_newline`, `extra_trailing_nl`, `leading_blank`, `trailing_spaces` — each scored
  `FAIL 0/8 visibly_failed` on an answer that is *correct*. That is format bias scored as comprehension,
  and it corrupts the section 6 instrument.

Fixed by `authoring/fix_t01_alt_parsers.py`, which applies the same normalisation already carried by
`cand-3`/`cand-4`: strip a BOM, fold CRLF, drop leading and trailing blank lines, keep everything else
strict. Trailing whitespace **inside** a line is deliberately still significant — the fields are
tab-separated and the last is a replacement string the prompt requires verbatim.

Note the shape of the discovery: neither of these two candidates is in the scored rotation, and neither
had ever failed a scored row. They were found because the propagation step *printed something it could
not do* and that line was read, not because a number looked wrong.

### D-R3-4. `g03/cand-5` was accepted on evidence, not on its report

The Luna authoring run returned `A7: 1 pass, 2 pass, 3 pass, 4 pass, 5 pass, 6 fail` with no checker
defects. Its claim was re-taken here rather than believed — this session had already caught one worker
report that was simply false (`g04/cand-5`, claimed 10/10, actually 5/10). Re-run locally:
`probe_checkers.py` over `g03/cand-5` alone reports `ref=pass deliverables=176 clean`, and
`verify_candidates.py` keeps the whole tree at REF 39/39 and EMPTY 39/39. Accepted.

### D-R3-5. `t04/cand-5` scored a correct answer as `confidently_wrong` on an exact span equality — fixed, and every t04 row re-graded

Found by reading a failure rather than counting one. Three round-3 Haiku rows and two Sonnet rows all
cited `PATH: app/request_path.py` with an explanation naming all three required behaviours; the only
difference between a pass and a `FAIL 4/5 confidently_wrong` was `LINES: 6-20` against `LINES: 8-20`.
The checker held:

```python
_ora_check("contiguous implementation span", lambda: _ora_parsed is not None and
            _ora_parsed[1] == (6, 20))
```

Lines 6-20 of `app/request_path.py` are `def process_login(...)` (6), its docstring (7), and the body
(8-20). The prompt asks for the span that "contains the largest part of the implementation itself,
**not a caller, helper declaration, configuration value, documentation, comment, or test**" — wording
that actively invites excluding the `def` line and the docstring. `8-20` is therefore a correct
reading of the same correct finding, and the checker was labelling it with the worst verdict the
instrument has. Under plan section 6, where the confidently-wrong rate outranks pass rate, that is the
most damaging defect this suite can carry: it manufactures the headline number.

Fixed by `authoring/fix_t04c5_span_equality.py`. The span must now lie inside the function and cover
all three required operations — the pre-verification lockout check (9-11), the 60 s record (13-17) and
the clear on success (18) — expressed as `6 <= first <= 9 and 18 <= last <= 20`. A shotgun span such
as `1-100` still fails on the lower bound. Re-probed with the near-miss set: `no format-strictness
defects found`. `verify_candidates.py` re-run: REF 39/39, EMPTY 39/39.

**Every t04 row in round 3 was then re-graded against the corrected checker, for both arms and all
trials, not only the failing ones.** Re-grading is deterministic — the sandboxes are preserved and the
checker is a pure function of the deliverable — and correcting an instrument for one arm only would be
worse than not correcting it. Result: Haiku t04 went 1/3 -> 3/3, Sonnet stayed 2/2, and three
`confidently_wrong` labels were withdrawn as instrument artifacts rather than model failures.

This is **not** a section 4a violation. 4a forbids keeping, dropping, rewording or reordering a task
because of whether a quant passed or failed it. Nothing here was decided by a score: the prompt was
read, the checker was read, the two were found to disagree, and the checker was brought into line with
the prompt it is supposed to be scoring. The fix was applied uniformly and before any GPU cell.

### D-R3-6. `g04/cand-5`'s prompt carries a cosmetic escaping artifact, and it is left alone until the round closes

`tasks-v5/g04/cand-5/prompt.md` contains fourteen literal `\`` sequences — backslash-escaped backticks
that survived the authoring brief — so the prompt renders as ``\`src/reconcile.py\``` rather than
`` `src/reconcile.py` ``. It is legible and it changes no requirement.

It is **not** the cause of Haiku's 0/3 on g04: the failures are `['totals', 'groups', 'report_format']`,
which is the policy memo's per-row rounding rule, and Sonnet reads the identical prompt and passes 2/2.
Fixing it now would desynchronise the source tree from the `round3/suite` copy that produced the scored
rows, so it is recorded as a cosmetic defect for the next round rather than patched mid-round. It is in
the handoff.

### D-R3-7. Two Haiku reference trials, not three, for the large band on Sonnet

Plan section 7 says to treat Sonnet as the expensive arm after the reset and to lean on Haiku. So the
large band gets **three** Haiku trials and **two** Sonnet trials. Sonnet's guard is a floor of 90%; two
clean trials of eight tasks plus round 2's 24/24 is ample to establish it, and a third would buy a
digit of precision on a number that is already at its ceiling.

### D-R3-8. The artifact called `bend-small-24k` is measured **tiny**, and the report must say so

The 24k bend-finding pass ran against `authoring/round2/suite-0`, whose mapping is
`g01..g04/cand-4`, `t01/cand-4`, `t02/cand-2`, `t03/cand-3`, `t04/cand-1`. Measured material for
those eight is 174-770 tokens for seven of them and 6,235 for `t03/cand-3` alone. So the band is
**tiny**, not small, for seven of the eight cells; the tag name is kept because the artifact was
already open and renaming a live run's tag would have split it into two files that resume
independently, but every report of it must carry the correction.

This matters for exactly one reason: a 24k window against 300 tokens of material measures nothing
about context. It is a *baseline* row — what each quant does on the same eight questions when
context is not the constraint — and its value is as the thing the 64k large-band row is compared
against, not as a result on its own.

### D-R3-9. Which 64k cells are fair-weather, corrected against the measurement rather than against the first reading

Plan section 4: above roughly 14.2 GB **resident** a configuration is fair-weather on this desktop,
because idle VRAM drifts 1.0-2.9 GB and reclaims without warning.

The first reading taken was `nvidia-smi` — **15,152 MiB of 16,303 MiB** with the 64k Q2_K_L cell
loaded — and on that number every 64k cell would have been fair-weather. That reading is wrong for
this purpose: it is whole-device usage including the runner's own overhead, not the model's
resident size. `/api/ps` for the same cell reports **13.35 GB resident, 100% GPU**, which is
*below* the threshold.

So, stated per cell rather than per band:

- `q27-Q2_K_L-64k`: **13.35 GB resident — not fair-weather.** The 2-bit line is the one quant that
  holds the large band with headroom.
- `q27-Q3_K_S-64k` and `q27-IQ3_M-64k`: measured 2026-09-04 at **14.70 and 15.11 GB** at full
  `num_ctx` under q8_0 KV. Both are above 14.2 GB and **are** fair-weather; every trial of theirs
  is labelled.

Recording the correction rather than the first number is the point. The two figures differ by
1.8 GB and they answer different questions, and taking the convenient one would have labelled the
entire large band unreliable when a third of it is not.

The consequence for reading the results is unchanged: a 64k cell that fails is ambiguous between a
quality result and a capacity result until the single-turn flag (section 3.3) is checked. A band
whose trials collapsed to one turn is a **capacity** result and must be reported as one.

### D-R3-10. The 64k throughput-curve probe killed the pass it was diagnosing, and it is dropped rather than retried

`q27-Q3_K_S-64k` was about to run its first task when `pibench.tps_curve()` — which walks fills of
0, 4k, 8k, 14k, 20k and 27k tokens — failed to return inside `post()`'s 900-second HTTP timeout at
the top of that ladder. The `TimeoutError` propagated out of `main()` and **ended the entire run**,
with `Q2_K_L`'s eight rows already banked and `IQ3_M` never started.

**A correction to the first reading, because it was mine and it was wrong.** A single live
`/api/ps` taken at the moment of failure reported the model resident at **15.78 GB**, and I wrote
that down as the finding. `pibench`'s own per-run `/api/ps`, recorded on every one of the trials
that followed, reads **14.70 GB** — exactly matching the independent 2026-09-04 capacity
measurement. The 15.78 GB reading was almost certainly transient, with the previous model still
unloading. **14.70 GB is the number to plan against**, the 2026-09-04 measurement stands unamended,
and the "resident sizes have grown by a gigabyte" claim is withdrawn. One sample taken at the
noisiest possible moment is not a measurement.

What survives the correction is the ordering, and it is stark. At 64k, resident size and wall time
move together across the whole grid:

| cell | resident | t03 wall | vs Q2_K_L |
| --- | ---: | ---: | ---: |
| `q27-Q2_K_L-64k` | 13.35 GB | 35.4 s | 1x |
| `q27-IQ3_M-64k` | 15.11 GB | 216.3 s | 6.1x |
| `q27-Q3_K_S-64k` | 14.70 GB | 498.4 s | 14.1x |
| `q27-Q3_K_M-48k` | 14.91 GB | 880.6 s | 24.9x |

So the curve probe did not fail because anything was broken. It failed because a 27,000-token
prefill on a card with a couple of hundred megabytes of headroom is genuinely that slow, and that
is a **capacity** result rather than a fault.

**Decision: the curve probe is dropped for the remaining quants** (`--no-tps`) and the pass
resumed. Plan step 4 calls the bend-finding pass the run to protect if the night runs short.
Losing eight real task rows to a *diagnostic* inverts that priority. The full curve exists for
`Q2_K_L-64k` and for all four 24k cells, which is enough to state the shape.

The generalisable form, and it is why this is written down rather than just worked around: **a
measurement harness that lets a diagnostic abort the experiment has its error handling backwards.**
`post()` raising through `main()` is the actual fault; `--no-tps` is tonight's workaround. A future
session should wrap the `tps()` call so a failed curve records itself as `null` and the run
continues.

### D-R3-11. The 64k pass was stopped short deliberately, and the campaign ends with the GPU idle

After `Q3_K_S-64k` produced g01 at **1,456.9 s** and g02 at **1,779.7 s** — against `Q2_K_L`'s
58.6 s and 361.4 s on the same two tasks — finishing its remaining five tasks and all eight of
`IQ3_M`'s was going to cost something like six hours, and the Windows converge is held until this
card is idle.

Plan section 6 sets the verdict wall at **900 s**. Both of those `Q3_K_S` rows breach it, so both
are **fails on wall time whatever their checkers say** — and their checkers passed, which makes the
point sharper rather than softer: this configuration is not wrong, it is unusable. Spending six
hours to re-establish that on eleven more tasks buys a decimal place on a disqualification that one
resident size and two wall times already carry.

So the pass was stopped and replaced with a **bounded closing burst** that answers the question the
remaining rows would have answered:

- `t03` — the cheapest task in the band, 35.4 s on `Q2_K_L` — on each of the two unfinished 64k
  quants, to show the slowdown is the *configuration* and not the task. It is: 216.3 s and 498.4 s.
- The `Q3_K_M` 48k partial row on the three large tasks whose 1.6x margin fits inside 48k.
- `--timeout 900` throughout, aligning the harness with the verdict wall so a trial that would
  breach it is recorded as the timeout it is instead of running on to 1800 s. `Q2_K_L`'s slowest
  64k row was 493.5 s, so nothing that would have passed the wall was affected.

`nvidia-smi` at the end: **604 MiB, 0%**. The card is idle and the converge is unblocked. What is
left undone is stated in `schedule.md` as queue item 1, with the artifact resuming rather than
repeating.
