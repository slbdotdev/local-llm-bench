# v5 planning — revision log

What changed in `plan-2026-09-03.md` and `questions.md`, and why. Newest first.
Owner rulings are recorded canonically in `decisions.md`; this file records their effect on the
deliverables.

---

## Revision 4 — 2026-09-03, the remaining rulings, the v4 stop, and the execution-ready plan

Two rounds of owner rulings arrived the same afternoon, and the GPU plan changed underneath them.
**Every v5 question is now answered and `questions.md` is closed.**

| ruling | effect on the plan |
|---|---|
| **Q7 = A** — per-quant maximum resident context (Q2_K_L 96k, Q3_K_S 64k, Q3_K_M 48k) | section 8 item 3 rewritten: the ladder is **context-confounded** and the exact headline sentence is specified rather than paraphrased; the two build steps for suffixed `q27-<QUANT>-<ctx>` variants are written out, including the trap that `make_model.sh` names its output `q27-<QUANT>` with no suffix and **silently overwrites the 32k model the v4 records came from** |
| **Q10 = A** — hard tasks authored and gated, waiver lane as specified | section 5 waiver lane marked adopted; `decimate-under-budget` stays dropped with Blender |
| **Q8 = B** — all pi changes bench-local via `PI_CODING_AGENT_DIR` | section 7d marked answered; the `reserveTokens` floor written as `proposals/reservetokens-floor.diff` plus a ten-point rationale, **PROPOSAL ONLY — not applied, not committed, not converged** |
| **`pi-run --agent-dir` = NO** | sub-question withdrawn from both the plan and the proposal rationale; the env-var route is enough and needs no wrapper change |
| **Decision 0 reversed at 12:03** — the v4 ranking is stopped | section 8 preamble and section 11 item 2 rewritten; new risk **R15**: Q2_K_L at 18 of 30 runs with one pass, never to be cited as a finished ranking; Phase 0 is running on the GPU under **another agent** and this session runs nothing |
| **Live gate results** — `maxTokens: 8192` at medium failed, low thinking failed, direct probe `finish=stop` with ~21k reasoning tokens and zero content | new 7g subsection and new risk **R14**. The cap is **necessary but not sufficient**; reasoning tokens are evidently not charged against `max_tokens` on this path. New fix **F8** establishes where the answer went — raw response, `think` toggled off, and whether reasoning counts against the cap — before any report calls the quant unfit |
| **Gate task moved** | to **`59_uri`**, with `q27-Q3_K_S` as the secondary gate. Verified first-hand in `results/v4-local-medium.json`: of Q2_K_L's 18 runs, `59_uri` trial 1 scored **1.000 over 37 turns** — the file's only unambiguous pass. `52_reengine` was the wrong gate: it is a fingerprint task the quant has never passed, so failing it proves nothing. A caveat travels with the choice — section 3 says `59_uri` must not rank anything (its oracle is a renamed copy of its own reference), which is fine for a liveness gate and is *not* evidence of capability |
| **Q9 = A** | section 8 item 5: pooled headline leading, per-arm breakdown beside it, timeout counts next to every mean |
| **Q5 = A** | `builds-worse` rework confirmed, with the Haiku re-probe of the current fixture as a **precondition** (step 0e), since every saturation record pre-dates the `93b563c0` rebuild |
| **Q2 = A** | `bench-D` after the first two or three tasks and a proven three-editor loop, copied from `bench-C`; the plan now says plainly that ~6 GB of RAM is the binding cost and that **M1 must land first**, because there is still no call site for `free_memory_gb()` |
| **Q11a / Q11b / Q11d = yes** | `skill_invoked` at weight ~0.05 on two or three tasks (carriers named in section 13); a red-team blocklist fixture in the self-test suite, **not scored** (step 0d); the `org` doc line is another agent's edit and was not touched |
| **all questions answered** | new **section 13, the execution-ready authoring plan**: five pre-task steps, the first three tasks named with their editors and gates, when `bench-D` appears, the per-task loop, the batch-boundary instrumentation, and the reporting shape |

**A correction I made to my own earlier claim.** I had cited `57_stateful` (0.6154) as the task
Q2_K_L had done best on. Re-reading the records directly, `59_uri` trial 1 is a **1.000 at 37
turns** — a full pass, not partial credit. That is the difference between a gate that isolates the
harness variable and one that does not, and it was worth the re-read.

---

## Revision 3 — 2026-09-03, the isolation audit and the harness-fix ruling

Two inputs: a line-by-line audit of the isolation surfaces (`bench/projects.py`, `bench/runner.py`,
`bench/gateway.py`, `bench/unitymcp.py`, the installed `mcpforunityserver 10.1.2` and FastMCP, and
the live `HKCU:\Software\Unity Technologies\Unity Editor 5.x` registry key), and the owner's ruling
that v5 must **fix** the pi harness bugs v4 exposed rather than only propose them.

| input | effect on the plan |
|---|---|
| `reset_assets` derives its `robocopy /MIR` **target from its argument** with no containment check (`projects.py:186-200`) | 5b1 row 1 downgraded to "HARD for the runner, NOTHING for the module API"; new mechanism **M3**, now the highest-priority fix; new risk **R12** |
| `runner.project_dir_for` (`:750`) formats the path by hand instead of calling `projects.project_dir()`, and `--editors` is never validated against `BENCH_SLOTS` (`:1460`) | same; M3 covers both, and `execute_run` calls `reset_assets(project_dir)` unconditionally at `:1286`, which is what makes it reachable |
| `launch_editor` validates only that the target has an `Assets/` dir; with `reuse=True` it would return the owner's live PID | 5b1 row 2 downgraded the same way; M3 covers it. Latent prefix bug in `_matches_project` recorded (`bench-A` would match `bench-A2`) |
| `manage_tools` `activate`/`deactivate`/`reset` call FastMCP `enable_components`/`disable_components`/`reset_visibility`, documented and implemented as **"this session only"** with a session-prefixed state key | 5b1 row 5 **resolved**; **H10 cleared to proceed**; M2 reduced from a wire probe to a one-line rule |
| `manage_tools` `action: "sync"` routes to `PluginHub._sync_server_tool_visibility` and rewrites `mcp._transforms` on the shared hub | hard constraint added to H10: the gateway must **never** call `sync`, because it changes what every new MCP session on the machine sees |
| `EditorPrefs` is one registry key shared by every Unity project and version; `policy.json` does not mention it and `execute_code` can write it; `policy.json`'s path bans are literal regexes evaded by concatenation | new 5b1 **row 8**; new mechanism **M4**; `policy.json` re-described as a guard against accident, not a boundary |
| Rows 4 and 5 both rest on a pinned third-party version, and `bench/tests/` uses a fake server | new mechanism **M5**: one integration test, run at upgrade time |
| Owner ruling on harness fixes | new **section 7g, Phase 0**: F1-F7 with concrete changes and acceptance tests, a binding smoke gate (`52_reengine` / `q27-Q2_K_L` at 32k must produce a tool call or a non-empty answer **and** record a `stopReason`), an explicit deferral of H3, and a non-comparability record (`harness_version: v5`, the frozen `pi-agent/` dir, no merging with v4). New risk **R13**. Section 11 item 3 rewritten as the Phase 0 gate; section 8 gated on it |
| Owner answers now landed | section 11 item 1 rewritten: Q1, Q3, Q6, Q11c and Q12 answered; Q4, Q7, Q8 and Q10 remain open and none of them blocks authoring |

**What this revision changed about the answer to Q1 itself.** Revision 2 gave an unqualified
guarantee on rows 1 and 2. That was too strong, and it was too strong for an instructive reason:
the guarantee held for every path the *runner* takes, and I had verified the runner. It does not
hold for the module the agents call directly, which is where a typo actually lands. The corrected
statement distinguishes the two, and M3 makes the distinction go away.

---

## Revision 2 — 2026-09-03, after the owner answered the blocking questions

Triggered by owner rulings relayed through the coordinator (see `decisions.md`). Nothing was
executed: no editor driven, no contestant run, no local model run, no commit, no managed file
edited.

### Owner rulings folded in

| ruling | effect on the deliverables |
|---|---|
| **Q3 = D**, Blender arm dropped, no containment controls built | Tasks **B1-B3 removed** from section 4; the four-control containment programme cancelled; the Blender risk bullet in section 6 replaced with a **record of the reasoning plus a standing rule** (nothing in v5 invokes Blender in any form). Candidate pool **21 -> 18**. Suite target **16-20 -> 14-18**. Coverage table, authoring order, trap-catalogue cross-references, comparability accounting and the verification log all updated. New risk **R10** (thin candidate margin). |
| **Q1**, structural isolation rather than scheduling | New **section 5b1**, the mechanism statement: a seven-row guarantees table (project dir, Unity lock, the 8080 hub, instance routing, `manage_tools`, RAM, console), each marked hard / shared / unverified / nothing, with the failure mode. Two proposed bench-local mechanisms, **M1** (a RAM floor) and **M2** (settle `manage_tools` scope). The old "state right now" bullet was **demoted from a guarantee to a snapshot**, and the old "never run a batch while someone is driving fargo-crispy" rule is now labelled what it always was: a convention, not a mechanism. `questions.md` Q1 rewritten to say plainly that the question I asked was the wrong one, plus a summary table at the end of the file. |
| **v4 ranking finishes unchanged**, no re-run | Section 7a now carries the ruling and a **harness-cap caveat** that every v4 local number must be reported with. Risk **R8** rewritten. Section 8 item 3 split so the v4 ranking's 32k config is explicitly *not* governed by the v5 config decision. |
| **Q12 = A**, Unity gates through the runner only | Section 5 gate mechanics changed from a proposal to a ruling, with `--effort high` in the example invocation. `questions.md` Q12 marked answered, including the two paths that Q12 does **not** cover (harness `ctx.mcp` calls, and my own `_selfcheck` work). |
| **Q6 = no plan-usage cap, instrumentation mandatory** | New **section 5a1** with the four concrete steps: live `claude-usage` at every batch boundary, the figure in every log and report, inbox alerts at 85% and 95%, and a current resume note under `results/v5/`. OpenRouter cap stays **USD 25 staged**, and the fp8 reference row now states the consequence: the cap does not buy three trials, so the reference will be **n=1 for most tasks** and must be labelled as such. |
| **Q11c = effort `high`** | New **section 5a2**: every v5 Claude contestant at `--effort high` passed explicitly, the 27B at medium, records with differing effort never pooled. Closes the section 1 defect where the existing suite pools `high`/`low`/`None` and `xhigh` appears nowhere. |
| **Q4 = A** (default stands) | `questions.md` Q4 marked answered; section 9 unchanged in substance. |
| **Nesting guard** being added to the wrappers in ansible-slb | New **section 7f** and risk **R11**. |

### Findings produced by this revision, not by the rulings

These came out of the work and are new to revision 2:

1. **No RAM guard exists anywhere in the bench.** `projects.free_memory_gb()` is defined and
   exported, and the only call site in the tree is the untracked `scratchpad/preflight.py:24`.
   `runner.py` has no memory check. This is the **only** contention point where a batch can
   actually harm the owner's session, and it is unguarded. Mechanism M1 proposed.
2. **The bench contestant path needs its own nesting guard, and the fleet one will not cover it.**
   `runner.contestant_env` deliberately **strips** nesting markers (`CLAUDECODE`,
   `CLAUDE_CODE_*`) so a contestant behaves like a fresh top-level session — the opposite of what
   an `AGENT_RUN_DEPTH` guard needs. `AGENT_RUN_DEPTH` is in neither `ENV_STRIP` nor `pi_env`, so
   it is inherited if set and absent if not, which makes behaviour depend on the launching shell.
   And **none of the 43 deny-list entries mentions `pi`, `codex`, `claude`, `node`, `npm` or
   `curl`**, so a contestant can spawn a nested agent that bills the OpenRouter account outside all
   cost accounting. Two-line fix proposed in section 7f.
3. **The cached plan-usage figure is unreliable, not merely stale.** `~/.claude.json`
   `cachedUsageUtilization` read `seven_day: 32` while the live figure was **77%** — wrong by more
   than a factor of two. The instrumentation must call `claude-usage` live. The API exposes no
   dollar limits (`limit_dollars` is `null`), which is why the alert thresholds are percentages.
4. **The campaign may not fit before the Saturday reset.** USD 115-195 of plan-usage equivalent
   against an allowance already at 77% with extra usage disabled and a hard stop. I cannot convert
   the remaining 23% into dollars, so I cannot say whether it fits — flagged plainly rather than
   estimated away, and it is the reason the resume note is mandatory.
5. **Dropping the Blender arm raised the cost estimate**, from ~USD 100-170 to ~USD 115-195. The
   three Blender candidates were the cheap ones (headless, no editor, no contestant profile), so
   removing them made the remaining mix more Unity-heavy. Counter-intuitive, so it is stated
   explicitly rather than left for someone to rediscover.
6. **`set_active_instance` is provably session-scoped**, keyed by `mcp-session-id`, and the
   gateway's own module docstring records a live verification of it. This is what makes the
   instance-routing guarantee hard rather than conventional, and it is the single most load-bearing
   fact in the isolation table.

### Recomputed for 18 candidates

Gate campaign **102 runs** (13 items x 2 gates x 3 trials, plus a revision cycle on a third), of
which ~84 Unity. Plan usage **USD 115-195**. Wall clock **11-16 h serial** — deliberately **not**
divided by editor count in any headline figure. Timeline **4-6 working days at 3 editors**.
fp8 reference **USD 30-70 for three trials against a USD 25 cap**, hence n=1 for most tasks.

---

## Revision 1 — 2026-09-03, after the GLM audit

`plan-audit/review-glm-v5.md`, dispositioned in `plan-audit/dispositions.md`. 23 numbered items;
3 were "verified, no finding"; of the 20 actionable findings **19 accepted in full, 1 in part, 0
rejected in full**. The headline corrections: the "Unity cannot run at 32k **at all**" overreach
(the core subset is viable); a stale `55.3 tool calls / 68k tokens` citation that the still-running
fp8 campaign had already overwritten with `34.2 / 53,702`; section 4 breaking section 3's own
check-count and weight rules on ten of fifteen tasks; a `P3` weighting that paid a **no-op** about
0.60 when the stated no-op ceiling was 0.35; an "identical 64k config" the hardware cannot deliver;
and the model-mean aggregates, which reproduce three different ways depending on the pooling rule
and are therefore no longer quoted as fact.

One factual half of one finding was **rejected**: the auditor could not confirm a base Masc avatar
prefab in `golden/`, but `Bunny_09-00_PC_Masc.prefab` is present and is what three existing
fixtures already build from.

---

## Revision 0 — 2026-09-03, initial plan

Written from three research subagents plus direct verification, against the v4 material, the
VRCA-Bench code and runs, and `D:\avatars` history. Its central original finding — that the
Q2_K_L "runaway thinking" zeros are pi handing the model the entire residual context window as one
response allowance, reproducing the observed output token counts to delta 0 / +34 / -20 / -14 —
survives every subsequent revision unchanged.

## Rev 5.9 — 2026-09-04

Scope unchanged; the plan is cleared to run. Three records, no new work:

- The worker-runtime precondition is **met**. Its acceptance test ran with a real `codex-run` and
  a real `pi-run` and found three defects, all fixed and verified — the largest being that live
  messaging to a Codex worker had never worked at all. Evidence:
  `ansible-slb/org/worker-runtime-acceptance-2026-09-04.md`. The KV-probe harness faults are the
  remaining precondition and are the manager's first job.
- The manager now **starts from a handoff in a fresh session** rather than being spawned as a
  subagent by the session that wrote the plan. An overnight run should not inherit a spent
  context, and a handoff survives a restart where a spawn does not.
- Section 1a records the owner's own restatement of the mission, with three clarifications: KV is
  pinned rather than optimized, the context axis measures where quality stops **holding** rather
  than whether it grows, and — the one that matters — **tests are never developed in response to
  what the local model turns out to be able to do.** That last is section 4a, and a manager
  working from the restatement alone would breach it.

Standing rule added: this plan removes items from `org/pending.md` as they are finished and never
adds one. Findings go to dated pages.
