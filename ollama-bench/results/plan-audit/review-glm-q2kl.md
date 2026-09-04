I've read the evidence file plus the plan, the analyser, the wrapper, `pibench.py` and the live JSON. Answers below.

**Verdict (one line):** Q2_K_L is not a broken quant — at this exact config (32k slot, medium thinking, maxTokens 32768) it deterministically burns its first turn thinking to the context ceiling and returns nothing; record those as legitimate measured 0s, let the 13 remaining runs finish, keep 3 trials, and settle the mechanism with labelled side probes after the controlled pass.

## 1. Broken quant or legitimate 0?

**Record the 0s as legitimate measured results at this config, with a footnote on the failure mode — do not call the quant "broken".**

Evidence:
- The runs are gradable and clean, not harness faults: `rc=0`, empty `errors`, the grader actually ran (`import failed: ModuleNotFoundError ... / not run` in `grader`), so SCORE 0.0 is the truthful grade of "agent produced no code". `v4-analyse.py` counts exactly this (missing score → 0.0).
- The ranking measures the *product* of quant + pi agent + controlled config, per plan §5 ("same ctx/KV/FA/thinking/timeout for all quants"). At this product, Q2_K_L delivers nothing on 8/9 runs. That is a real, reportable result.
- But "broken quant" is refuted by the evidence already in hand: 55_minilang trial 0 made a tool call and scored 0.19; on v3 hard tasks Q2_K_L PASSed 34_tmplfix and 35_ledger with 17-18 turns (under the older 16k output cap). The quant can code and can stop a turn. The failure is the interaction *medium thinking + 24k of thinking tokens + 32k slot*, i.e. it thinks past the slot before emitting anything — exactly what the server log shows (n_tokens ≈ 29.5k of 32768, no error, output all thinking).
- Say so in the report: "Q2_K_L disqualified at the controlled config (runaway first-turn thinking exhausts the 32k slot); not evidence of global quant damage." The plan's language commitments (§6b) already require "replication at task level, not trial level" — add this failure-mode footnote to the same bucket.

## 2. Early exit vs finishing the 13 runs

**Finish them. Expected cost ≈ 1.6 h (13 × ≤560 s: generation is capped by the ~29.5k context stop at 54 tok/s, so no 1800 s timeouts are expected); that is ~10-15% of the total schedule, and early exit breaks all three pillars of the protocol.**

What early exit costs:
- **All-or-nothing three trials:** stopping now leaves 56 at 1/3 trials and 57/59/60/61 at 0/3. The plan's rule "ranking only when all three quants have three trials" fails for Q2_K_L while holding for Q3_K_S/M — an asymmetric design that is hard to defend in the report.
- **Bootstrap over tasks:** `v4-analyse.py` bootstraps over the tasks present per model. Q2_K_L would be averaged over 3-4 tasks vs 7 for the others; a 3-task bootstrap CI is nearly vacuous, and any task where Q2_K_L would have escaped the runaway (55 t0 shows escapes happen) is silently excluded — biasing Q2_K_L's mean *downward* in the very comparison where it looks worst.
- **Paired comparison:** the paired bootstrap restricts to common tasks; with 3-4 common tasks it needs `len(common) >= 2` and produces a diff CI over 3-4 points. The Q2_K_L vs Q3_K_S pair — arguably the most decision-relevant boundary (cheapest quant vs next size up) — would be the least trustworthy pair in the table.
- **Reporting cadence:** the plan fires the interim analysis at quant boundaries; a killed Q2_K_L block means no clean interim and a backfill session later. pibench's lossless resume makes backfill *possible*, but the GPU-time saved (~1.6 h on a 10+ h schedule) is small and the risk that backfill slips ("keep the GPU busy" always wins) is real.

What finishing costs: ~1.6 h of GPU time whose information value is low (8/8 comparable runs are deterministic 0s) — but not zero, since the remaining 4 tasks test whether *any* v4 task escapes the runaway, which feeds the paired diff.

If the owner insists on early exit: the only defensible variant is kill-now-and-guaranteed-backfill (fill the 13 runs after the other quants, before the final ranking, same tag). Never report a partial-task Q2_K_L mean.

## 3. Should local quants run 1 trial?

**No — keep 3 trials. "Deterministic" is currently an inference from 5 runaway comparisons; the one run that did real work (55 t0) diverged from its reruns, so the evidence contradicts strict determinism, and you need ≥2 trials to ever establish determinism.**

Evidence:
- 52 t0/t1/t2 and 55 t1/t2 are byte-identical — but those are all runaway outputs hitting the same attractor. 55 t0 diverged (2 turns, 1 write, 22,763 out vs 23,780 and 1 turn for t1/t2) — genuine cross-trial path divergence at the same config. A 1-trial policy would have recorded 55 as 0.19 (or, on another task, missed an equally lucky/unlucky divergence); with the task-level bootstrap, one such flip on a 7-task suite moves a mean visibly.
- Changing to 1 trial *now*, and only for local quants, is a mid-stream protocol change applied to the failing quant — exactly the kind of thing the plan's language commitments exist to preempt. If a 1-trial policy is ever adopted, it must be pre-registered for all quants before the ranking, with a determinism check (outputs identical across ≥2 trials) as its justification.
- The fp8 comparison is unaffected either way, and already carries the honest label ("upper bound on quant loss under unequal serving configs", plan §6b). fp8 is non-deterministic (different stack, server batching) and keeps 3 trials; a local-3/fp8-3 design is symmetric and clean. Local-1/fp8-3 would be defensible but buys little.
- If the owner wants the time savings anyway, the right sink is the labelled at-best-config spot-check (plan §6 item 4) on the winning quant — that is where a saved 2-4 h changes a decision.

## 4. Cheap diagnostics to separate "too damaged to stop thinking" from "prompt + medium thinking overflows 32k for any 27B"

**Yes — two cheap, labelled probes after the controlled pass, run through pibench with a separate `--tag` so they can never contaminate the ranking JSON:**

1. **Low-thinking probe (primary, ~8-15 min):** one Q2_K_L task with the shortest prompt (56_tmpl or 60_numlit) at `--think low`, 1 trial, same 32k config, `--tag v4-q2kl-low-probe`. If it now emits tool calls and finishes with a normal turn count (pass or partial score), the runaway is thinking-budget-driven and the quant is fine at a sane config; if it still runs to the ceiling with zero tool calls, the quant itself cannot terminate — that is the discriminating outcome. Note the v3 16k-cap passes are already weak evidence for the first branch, but those runs predate the maxTokens change, so a clean same-config probe is worth the 10 minutes.
2. **Cross-quant control (free-ish, folded into the existing schedule):** watch whether Q3_K_S's first-turn runs also show 1-turn/22k-thinking/empty-text signatures. If Q3_K_S behaves normally at the identical config, the mechanism is quant-specific runaway; if Q3_K_S also runs away on first turns, the honest finding is "medium thinking at 32k is over budget for this model family on these tasks" and that must go in the report beside the ranking, because it reinterprets *every* quant's single-turn failures, not just Q2_K_L's.
3. Optional third: a 64k-ctx side probe (separate Modelfile tag, labelled, never into the ranking) — the tuning notes say 64k is reachable at this quant family; it directly tests "would Q2_K_L finish if given room". Run it only if probes 1-2 are ambiguous.

All three leave the controlled ranking untouched; per plan §6 item 4's precedent, label every probe "side probe, not part of the ranking" in the final report.

**Bottom line for the control session:** let 56 t2 and the remaining 13 Q2_K_L runs finish (≈1.6 h), report the Q2_K_L block as a legitimate 0-at-this-config with the runaway-thinking footnote, keep the 3-trial protocol for Q3_K_S/Q3_K_M, and queue the low-thinking side probe (plus the Q3_K_S cross-check, which is free) for after ALLDONE.
