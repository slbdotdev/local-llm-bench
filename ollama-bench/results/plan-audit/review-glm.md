1. **HIGH — num_ctx confounds the ranking.** Q2_K_L/Q3_K_S run @32k but Q3_K_M runs at its "largest fully resident ctx" (possibly 16–24k) while v4 turns need ~20–30k context (plan's own numbers). Q3_K_M gets truncated context → fails for capacity, not quality. Fix: run all quants at one num_ctx every candidate can hold fully resident (or report Q3_K_M only as a capacity note, not a quality rank).

2. **HIGH — KV quant differs across quality runs.** Q2_K_L/Q3_K_S are pinned to q8_0 KV, but Q3_K_M's ladder (step 2) used q4_0 KV + forced 66; its quality config inherits whichever KV the filler left behind. KV quant quality is itself a variable. Fix: pin one KV quant (q8_0) for all v4 runs and assert the env at launch.

3. **HIGH — Ollama env drift between filler and quality runs.** Filler leaves KV q4_0 + possibly other env toggles set; quality runs assume q8_0 KV. Each env change needs an Ollama restart (unloads models) and the plan never says "restore q8_0 before step 3." Fix: add an explicit pre-step-3 env checklist + log the actual env into each result file.

4. **HIGH — 2 trials/quant cannot rank anything.** 10 tasks × 2 trials = 20 binary outcomes; the SE on a ~50% pass rate is ~11pp, larger than the expected Q3_K_S vs Q3_K_M gap. The "first-line ranking" is likely noise, and the unbalanced third pass ("same order if time allows") risks 3 trials for Q2_K_L vs 2 for Q3_K_M. Fix: use mean SCORE (continuous) as the primary metric with CIs, and make the third trial all-or-nothing across quants.

5. **HIGH — keep filter is a coin flip at the edges.** With 3 trials: a true p≈0.8 task lands in "1/3–2/3" ~48% of the time and "3/3 reject-or-keep" the rest; a true p≈0.2 task is kept only ~48%; a p≈0.25 task is rejected as 0/3 ~42% of the time. With 12 candidates, keeper-set composition at the margins is substantially random — and each extra authoring round re-rolls it. Fix: score candidates on mean SCORE over 3 trials with a continuous threshold band instead of pass-count bins, or run 5 smoke trials on borderline candidates.

6. **MED — 0/3 rejection destroys ranking signal in the other direction.** Tasks fp8 solves ~10–25% of the time are exactly where quants separate most, yet the rule rejects them outright; survivors skew toward tasks where all quants will floor at ~0. Fix: keep 0/3 tasks with mean SCORE > 0 and flag them as "quant-discriminating" rather than rejecting.

7. **MED — brief rule 6 is self-contradictory.** "Reject a task if fp8 goes 3/3 … keep 3/3 with mean SCORE < 0.9" — an author implementing the literal rule rejects everything fp8 passes 3/3, including the SCORE<0.9 keepers the plan counts on. Fix: restate as "reject 3/3 with mean SCORE ≥ 0.9; reject 0/3; keep the rest."

8. **MED — cross-provider confound in the fp8 reference.** fp8 medium is run on OpenRouter/Parasail with its own sampling params, max_tokens, and system prompt; local quants run through Ollama. "Quant vs fp8" deltas conflate quantization loss with serving differences. Fix: match pibench sampling/thinking/timeout params exactly across providers, and state remaining provider delta as a caveat.

9. **MED — gen tok/s is promised but not measured.** Step 3 runs with `--no-tps`, yet the morning report's first line includes "gen tok/s at its config." Either the speed data is from different configs (not "at its config") or the report will have a hole. Fix: drop `--no-tps` (tps costs nothing) or source tok/s explicitly from the step-1 speed measurements and label them as such.

10. **MED — ETA math ignores timeouts and near-full-context slowdown.** 3 quants × 2 trials × 10 tasks × 8 min = 8 h assumes every run completes at 8 min; a single 1800 s timeout adds ~22 min, and Q3_K_M at large ctx with q4_0 KV will run slower than the 8-min estimate. Two or three timeouts push "done ~14:00" to mid-afternoon. Fix: budget ETA with one timeout per quant and use measured tok/s at near-full context, not empty-context probes.

11. **MED — schedule is single-threaded on authoring finishing by 05:00.** v4 ETA already includes "up to two extra author rounds"; one extra round (~12 candidates × 3 OR trials, 2 concurrent) slips readiness past 05:00, and the filler list is finite — after its probes are exhausted the GPU idles until v4 lands, violating "never idle." Fix: add a repeatable filler loop (ctx-ladder sweeps on remaining quants/configs) rather than a one-shot probe list.

12. **MED — leak/stop conditions have no executor.** "Stop on unbounded growth," "stop the stream on RAM/VRAM not returned" presume something is watching at 04:00 with no human. Nothing in the plan creates a watchdog. Fix: a small monitor loop (nvidia-smi + RSS polling, threshold → kill stream, write report-so-far) as a prerequisite before 02:00.

13. **MED — 16k skip threshold is arbitrary and inconsistent.** Q3_K_M is skipped if fully-resident ctx < 16k, but the plan itself says v4 needs 20–30k/turn; a 16–19k config would be run and truncated. Fix: skip threshold = max task context (or the common num_ctx from finding 1), not 16k.

14. **MED — reference trials double as smoke trials.** The fp8 v4 reference is "the keep-filter trials themselves," i.e. 3 trials per keeper run during authoring, possibly hours before the local runs and under authoring-round time pressure; if extra rounds add keepers, reference tasks and run conditions span rounds. Fix: after the keeper set is final, re-run the reference once under the exact final task set (or at least confirm params identical) before comparing.

15. **LOW — fixed-seed hidden tests make trials non-independent in difficulty.** All trials of a task hit the same hidden cases; a task can be hard merely because its seed drew brutal cases, and no number of trials reveals that. Fix: acknowledge in the report; optionally report per-case pass distribution from one verbose run.

16. **LOW — 14:00 finish vs "morning report."** The report is specified as morning but the quality pass lands ~14:00 under ideal assumptions (see 10). Fix: send an interim ranking at ~08:00 from whatever trials completed, final at completion.

17. **LOW — "prompt-fill curves to 60k" filler can be long, not "minutes."** Near-64k prefill on a 27B quant on a 5080 is minutes of prefill alone per point, ×6 points ×2 quants; the "interrupt at any probe boundary" claim holds but the filler budget may overrun into the v4 window. Fix: trim the curve to 4 points per quant.

Constraint audit: no commits ✓; no fleet/ansible/managed-config changes ✓ (Ollama env toggling is within the stated allowance, but only if finding 3's restore step happens); one-model-on-GPU ✓ as long as OR-stream pibench never targets ollama provider and env restarts occur only at (quant, suite) boundaries — the plan should state the latter explicitly since an env swap mid-run would silently break it.
