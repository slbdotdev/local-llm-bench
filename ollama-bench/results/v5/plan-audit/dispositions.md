# Dispositions — GLM audit of the v5 plan

Audit: `review-glm-v5.md` (GLM 5.3 Flash, effort high, routed by **throughput** under the owner's
one-time exception). Prompt script: `run-glm-v5.sh`. Raw stderr: `review-glm-v5.err` (`rc=0`).

**Routing note.** The throughput exception was implemented by copying `~/.pi/agent` to
`%TEMP%\v5-pi-agent-throughput`, changing **only that copy's** `providers.openrouter.sort` from
`"price"` to `"throughput"`, and pointing pi at it with `PI_CODING_AGENT_DIR`
(`pi-coding-agent/docs/environment-variables.md:81`). The managed `~/.pi/agent` was never touched.
The copy's `"packages"` key was also removed so `pi-mcp-extension` could not load — see F18/R9 for
why that mattered.

**Tally.** 23 numbered items. Three are explicit "verified, no finding" (F5, F17, F22).
Of the 20 actionable findings: **19 accepted in full, 1 accepted in part (F11), 0 rejected in
full.** One factual half of F11 is rejected as wrong, and it is the only place the auditor
asserted something I could disprove.

Every accepted fix is bench-local. None needs a commit or a fleet config change.

---

## Accepted in full

| # | rating | finding | disposition |
|---|---|---|---|
| **F1** | LOW | Every `builds-worse` run pre-dates the `93b563c0` fixture rebuild, so "saturated on the control" is proven only against the **old** fixture. | **ACCEPT.** Correct and I missed it. The rework direction survives (two defects found by one measurement is structurally weak) but the claim needed qualifying. Plan now says so and requires one Haiku re-probe of the *current* fixture before the rework is designed. |
| **F2** | MED | The §1 model aggregates do not reproduce from the 45-usable set. | **ACCEPT — and my recomputation disagrees with both the plan and the auditor.** I took the plan's figures from a subagent's `runner report`. Recomputing directly over non-`excluded`, non-`error` records (n=51) I get haiku **0.7052** (n=14), sonnet **0.8834** (n=20), opus/fable **0.9398**, glm-flash **0.9167**; haiku by category `measure` **0.8183** (n=9) vs `build` **0.5016** (n=5). The auditor got 0.727/0.917/0.940/0.940 and build 0.502; `runner report` gave 0.677/0.939/0.947/0.938. Three different answers means **the aggregation rule is the finding.** Plan now publishes my recomputation with the rule stated inline, flags that `runner report` pools differently, and stops treating any pooled model mean as quotable. The categorical claim is softened as the auditor asks — `material-slots` is a `measure` task and is the single strongest separator (0.215 vs 1.000). |
| **F3** | LOW | `_smoke` wall range is 13.6-31.1 s, not "18-51 s". | **ACCEPT.** Corrected. |
| **F4** | HIGH | §2's "all nine finished Q2_K_L runs are one turn, zero tool calls" is stale, and "0/9" is wrong. | **ACCEPT — the most useful correction in the audit.** Verified against the current file (13 rows): `55_minilang t0` = 2 turns, 1 tool call, score **0.1935**; `57_stateful t0` = 5 turns, 1 tool call, score **0.6154**; `57_stateful t1` = 3 turns, score 0.0769. So Q2_K_L's mean SCORE is about **0.068**, not 0, and it demonstrably *can* reach a tool call. The 7a mechanism survives untouched, but "the local arm measures the harness" is now stated as "on the tasks where the quant never escapes turn one", with 57_stateful named as the counterexample. |
| **F6** | HIGH | "A Unity task cannot run locally at 32k **at all**" is contradicted by the plan's own scenario D. | **ACCEPT.** The overreach is mine. Scenario D (Unity `core` group only, 29 tools) leaves ~9.7k of response at 32k, and H10 says that reduction is real. Restated as: **full 48-tool Unity is unrunnable at 32k; core-subset Unity is tight but viable; 64k is recommended for headroom, not a hard prerequisite.** The auditor's extra route is good and adopted: the **gateway is already a pre-model tool-list rewriter** (it hides 7 tools and makes a startup call at `gateway.py:441`), so pre-calling `manage_tools` there delivers scenario D without the model ever seeing the fat schemas. Q7 in `questions.md` is downgraded from "prerequisite" to "strongly recommended". |
| **F7** | MED | The scenario table omits the **18,071-byte bench contestant `CLAUDE.md`** that `build_pi_command` actually appends, and scenario A's components sum to 35,843 not 37,335. | **ACCEPT.** Everything moves in the pessimistic direction, which makes it worse to have stated it as measured. Plan now adds the profile `CLAUDE.md` (~4,518 tokens) and `pi-system-note.md` to the accounting and footnotes the ~1,492-token residue as unexplained. |
| **F7b** | MED | The 86,094/12,465-byte schema counts could not be corroborated — the hub is down and the only artifact is the plan itself. | **ACCEPT.** This matches the caveat I had already written into 7b before the audit; strengthened as the auditor asks: **the H5/H6 wire probe must publish the raw `tools/list` dump beside the numbers**, and until it does the figures are labelled a subagent claim. |
| **F8** | HIGH | §4 violates §3's own rules — only U7 has >= 8 checks; U4, B2, P3 have a 0.35 check against a stated 0.30 cap. | **ACCEPT.** The plan failed its own gate, which is exactly the sort of thing that should not reach a campaign. Resolved by relaxing §3 to an **admission floor of >= 5 checks and <= 0.35 any single check**, while keeping **>= 8 sub-requirements as a hard requirement for `build`-category tasks**, which is where the 2026-09-02 evidence says the discrimination actually lives. |
| **F9** | MED | U6's "the animated property still animates" and U9's "shaders_alive" lean on shader semantics the plan's own trap catalogue says are not measurable in-editor; `_selfcheck.py` will mask them because the golden solve is authored, not measured. | **ACCEPT.** Adopted as a general authoring rule: **`_selfcheck.py` must flip each check individually on a hand-built wrong solve, not just the task as a whole**, and any check that cannot be made to flip is demoted to a report/honesty check. |
| **F10** | MED | P3 pays its largest weights for **inaction** — a no-op collects `no_number_in_docs` .35 plus plausibly `tool_named` .25 ≈ **0.60**, against a stated no-op ceiling of 0.35. U4's `other_untouched` .30 is at the limit. | **ACCEPT, and this is the best calibration catch in the audit.** It would have inverted discrimination exactly at the bottom of the ladder, where the local quants live — a timed-out run would have banked abstention credit. Plan now caps **any weight granted for inaction at 0.10** and makes P3's `no_number_in_docs` conditional on the docs having been correctly updated. |
| **F12** | LOW | B1's required add-on lives at `D:\avatars\apply_modifiers_with_shape_keys` — **inside the blocked path** — and the plan never says the fixture must vendor a copy. | **ACCEPT.** I had noted the bare-gitlink problem but not that the path is blocked, which makes vendoring mandatory rather than merely tidy. |
| **F13** | HIGH | The 64k ladder is not deliverable: `gpu-tune/summary.md:40` says **"Q3_K_M reaches 48k and Q3_K_L only 24k; neither reaches 64k."** | **ACCEPT — the single most consequential correction.** Verified, and it is worse than the auditor says: the same file's table shows `Q3_K_S @ 64k with num_gpu 66` and `Q3_K_M @ 32k with num_gpu 66` both **FAIL (thrash)**. So my "identical config at 64k / q4_0 / num_gpu 66 across all three quants" is impossible on two counts. Plan now prescribes **the largest context each quant can hold at full residency** (Q2_K_L up to 96k, Q3_K_S 64k, Q3_K_M 48k), states plainly that this **breaks the identical-config freeze**, and reports the ladder as context-confounded rather than pretending otherwise. Q7 becomes a per-quant question. |
| **F14** | MED | The Sonnet feasibility gate will bounce U3/U6/U9/B3 — the very tasks §8's "too low" remedy assumes can be admitted — while the Haiku gate can pass a near-saturated task (2/3 at mean 0.94). | **ACCEPT.** Real conflict, and better found now than at gate time. Plan proposes an explicit **waiver lane**: a task with a passing golden selfcheck, a per-check trap flip, and Haiku mean < 0.30 is admissible despite Sonnet 0/3, recorded as "hard, waived". Raised to the owner as a new option under Q10. |
| **F15** | MED | The gate budget leans on a blended per-run mean; the 36 Sonnet Unity gate runs are on new build-shaped tasks, plausibly 1.5-2.5x the blend, so **USD 75-125** rather than ~50. | **ACCEPT.** The blend really does mix `material-slots` at 2.3 min with `toggle-default-on` at 10.5 min and USD 3.33 median. Plan now estimates per task class, and `questions.md` Q6 asks for a **plan-usage cap** alongside the OpenRouter cap. The wall-clock figure is now explicitly conditioned on Q12. |
| **F16** | LOW | "96/96 in 1.2 s" is a subagent report; a static count finds 93 test defs. | **ACCEPT.** Labelled "as reported 2026-09-03 10:50, parametrization not audited". Not load-bearing. |
| **F18** | HIGH | The Blender containment is **a promise, not a control**: `policy.json` has no blender pattern at all; two `blender-mcp` bridges are running; and headless-only protects the live editor but **not the owner's files** — a contestant has Bash, `blender -b --python <script>` matches no deny rule, and a script that opens `D:\avatars\crispy\sources\…` from inside Blender passes every screen written today. | **ACCEPT — the most important safety finding in the audit, and it corrects a real gap in my reasoning.** I had treated "headless" as the containment. It is not: it moves the risk from the owner's live session to the owner's files, and the deny lists match *invocation strings*, not what `bpy` does once running. Plan now requires, before any Blender task is authored: (i) the blender server name and `mcp_blender_*` added to the deny layer for both contestant kinds, (ii) the fixture vendoring its tools and inputs into the sandbox, (iii) a harness-supplied wrapper that pins `-b --factory-startup` and a scripts directory with the raw executable denied, and (iv) a stop-rule tripwire on any `blender-mcp` process spawn during a batch. Q3 in `questions.md` is rewritten around this. |
| **F19** | LOW | The live-Blender premise is stale — pid 19744 is gone. | **ACCEPT.** Already partly corrected before the audit landed (`%TEMP%\quit.blend` timestamps its 11:02:22 exit). The justification is now stated as a principle — *the owner may at any time hold unsaved work, and a contestant cannot tell* — rather than pinned to a process sighting. |
| **F20** | LOW | `93b563c0` touched `CLAUDE.md` (18 lines) as well as `SKILL.md`, so the pre/post-rebuild caveat is broader than stated. | **ACCEPT.** Corrected, and it dovetails with F7: `bench/contestant/CLAUDE.md` (18,071 B) is its own artifact, distinct from `D:\avatars\CLAUDE.md` (39,452 B). |
| **F21** | MED | Figures headed for the owner's report that do not reproduce: the model means (F2); **"55.3 tool calls / 68k output tokens"**, where the cited file now says **34.2 / 53,702** over 6 runs; the schema bytes (F7b); `_smoke` timings (F3). | **ACCEPT.** Verified: `results/v4-ref-medium-1800.md` currently reads 3/6 pass, mean 0.89, 969 s/run, 53,702 out tok, **34.2 tool calls**. I quoted a snapshot that the still-running campaign has since overwritten — which is precisely the "scores rot" failure the skill warns about, committed in a document about not doing that. Corrected, re-cited to the current snapshot, and marked in-flight. |

## Accepted in part

| # | rating | finding | disposition |
|---|---|---|---|
| **F11** | MED | (a) U1 is graded against a single "precomputed optimum", zero-scoring equally valid configurations. (b) The fixture needs "the Masc avatar" and the auditor could not confirm a base Masc avatar prefab exists in `golden/Assets`. | **(a) ACCEPTED** — a single-solution key is exactly the grader-bug shape that has bitten this suite twice. U1 is now graded outcome-based (rank reached, causes addressed), with the cached optimum used as a hint and a feasibility bound, never as an answer key. **(b) REJECTED — factually wrong.** `D:\VRCA-Bench\golden\Assets\Crispy_Bunny\Bunny_09-00_PC_Masc.prefab` exists; so do `_Fem`, `PLANTI`, `08-09_QUEST` and `08-09_FALLBACK`. It is also the exact prefab three existing task fixtures already build from. No change. |

## Verified, no finding

| # | what the auditor confirmed |
|---|---|
| **F5** | The whole 7a root-cause chain, re-derived independently: the clamp source verbatim, `estimateContextTokens` counting tool schemas at 4 chars/token, `maxTokens == contextWindow` for all six 32k quants so the `Math.min` never binds, the `openai-completions.js` comment, `_checkCompaction`'s early return, and `pibench.py:246` recording an error only on `stopReason == "error"`. Arithmetic reproduced to delta 0 / +34 / -20. **One useful addition adopted:** `simple-options.js` also exports `MIN_ANSWER_TOKENS = 1024` and `clampThinkingBudgetToAnswerRoom` — upstream already contains the shape of the H3 fix, which strengthens H3's plausibility. Added to the plan. |
| **F17** | The `D:\avatars` containment model is real rather than asserted: `policy.json` patterns, the deny list across all three path spellings, `guard.ts` deriving from that same file and failing closed, `paths.py` refusing a runtime inside the repo, and `guard_active: true` on every post-`937a10be` record. |
| **F22** | The §10 comparability discipline is earned, not claimed; the "same task, different harness" bridge label is the right honesty device. No unearned comparability beyond F2/F21. |

---

## What the audit did not catch

Recorded so the next reviewer knows the coverage boundary:

- It accepted §5b's editor and concurrency mechanics without independent re-derivation beyond the
  two line numbers it quotes.
- It did not question the 21 candidate tasks' *choice* — only their gradeability and weights — so
  "are these the right tasks to model the owner's work?" remains unaudited by anyone but me.
- It did not evaluate the trap catalogue (4a) at all, which is the part most likely to contain a
  documented-but-no-longer-true behaviour.
- It could not verify anything requiring a live Unity hub, which is the same gap H5/H6 exist to
  close.

## Verdict, and my read of it

The auditor's verdict — *"should not start as written… what is wrong with it is wording and gating,
not the underlying measurements or the task design"* — is fair and I agree with it. The two
foundations held (the §1 keep/drop/rework calls and the §7a root cause), and the failures were
concentrated in exactly the places a plan gets sloppy: an overreaching headline (F6), a stale quote
(F21), a design rule the document broke itself (F8), a config freeze that the hardware cannot honour
(F13), and a containment story that was a promise rather than a control (F18).

All nineteen accepted fixes are applied to `plan-2026-09-03.md`. None required a commit, a fleet
change, or an edit to any managed file.
