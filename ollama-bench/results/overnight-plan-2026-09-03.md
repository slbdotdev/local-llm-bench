# Overnight plan, 2026-09-03 (v2, 01:35, after pi audit by GLM 5.3 Flash and qwen3.8-27b; owner option B)

Goal: rank the local Qwen3.8-27B quants by QUALITY against the unquantized fp8 reference, with speed already
measured, and keep the RTX 5080 busy all night without a human in the loop.

Constraints (owner): no commits anywhere; no fleet config changes (Ollama env may be toggled for measurement
only and is restored to OLLAMA_FLASH_ATTENTION=1, OLLAMA_KV_CACHE_TYPE=q8_0 before the quality step; a winner
is reported, not applied); one model on the GPU at a time, asserted via /api/ps (<=1 model) and nvidia-smi
(one GPU process) at every probe/run boundary; process-tree kill on every timeout; a watchdog samples VRAM,
Ollama RSS and free host RAM every 10 s all night (results/gpu-watch.log, alert marker results/gpu-watch.ALERT
when VRAM does not return within 60 s of an unload or free RAM drops below 8 GB); every harness unit checks
the marker at each task boundary and stops the stream if present.

## Quality-run configuration (controlled, identical for every quant)
- num_ctx 32768 for ALL quants: it is baked into each q27-* Modelfile, which is what pi's requests get; the
  harness --num-ctx flag only affects the TPS probe, not task runs (audit finding). No per-quant ctx.
- KV q8_0, flash attention on, the managed defaults, asserted from server.log before the first quality run.
- pi agent dir results/pi-agent (contextWindow 32768, maxTokens 16000 for every local model), medium thinking,
  --timeout 1800, the same hidden tests and SCORE partial credit as the fp8 reference.
- Q3_K_M runs at this config even though it spills (62/66 layers, ~15-22 tok/s): the ranking must not confound
  ctx or KV type with quant. Its slowness costs time, not validity. Q3_K_L is excluded (spills further, 15 tok/s).
- If tuning shows Q3_K_M fully resident at 32k with q4_0 KV, that is run AFTER the controlled pass as a labelled
  "at-best-config" extra, never mixed into the ranking.
- Metric: primary = mean SCORE per quant (continuous, 10 tasks x 3 trials = 30 samples), secondary = pass rate;
  each reported with a bootstrap 90% CI over tasks; the ranking is only stated if CIs separate, otherwise "tied".
- Trials: 3 per quant, mandatory for any quant in the ranking; the pass is all-or-nothing across quants
  (no quant gets a third trial unless all do). Speed figures in the report are the tuning probes at exactly
  this (quant, 32k, q8_0) tuple, labelled as such.
- Serving-stack caveat: the fp8 reference runs on OpenRouter (Parasail, ZDR) through the managed pi config
  with the same thinking level and timeout but a different max_tokens/provider; the quant-vs-fp8 delta is
  reported as an upper bound on quant loss, and the quant-vs-quant comparison (same stack) is the ranking.

## Streams

### GPU stream (sequential, never idle)
1. Tuning legs (running): KV q8_0 vs q4_0, num_ctx 32k/48k/64k on Q2_K_L and Q3_K_S, forced num_gpu 66 on
   near-misses, one or two fine-tune candidates. Output: results/gpu-tune/probe.jsonl + summary md. ETA ~03:00.
2. Filler until v4 is ready: KV q4_0 at 64k on Q3_K_S(forced 66) and Q2_K_L; Q3_K_M ctx ladder 12k-32k with
   q4_0 KV + forced 66; Q3_K_L the same; 4-point prompt-fill curves (0/16k/32k/60k) for the best config per
   quant; fine-tune at its best config if disk allows. When the list is exhausted, LOOP: repeat the KV/ctx
   matrix on the remaining quant/config combinations, then a one-trial v3 pass on Q2_K_L at 32k (extra data,
   not the workhorse), until v4 lands. Each unit is short; the stream yields at any unit boundary.
   Before step 3: restore env to q8_0 KV (restart Ollama at a boundary), verify server.log, log the env.
3. v4 quality runs, once v4 is "ready" (below): per quant, in order Q2_K_L, Q3_K_S, Q3_K_M:
   PYTHONUTF8=1 python pibench.py --provider ollama --models <q> --think medium --trials 3 --no-tps
     --tasks-dir tasks-v4 --tag v4-local-medium --timeout 1800   # ctx 32768 from the Modelfile, q8_0 KV from env
   Pre-flight: python selftest2.py tasks-v4 clean; every tasks-v4/* subdir has prompt.md and test.py (no scratch
   dirs); /api/ps empty; watchdog alive. Re-forecast after the first 4 tasks from measured wall/run.
   ETA: start ~05:00; 3 trials x 10 tasks: Q2_K_L ~2-4 h, Q3_K_S ~2-4 h, Q3_K_M ~5-8 h (spilled); worst case
   with timeouts runs into the evening. The morning message reports whatever is complete; the ranking is sent
   when all three quants have 3 trials, not before.

### OpenRouter stream (parallel, no GPU)
4. v3 finishes as is (35_ledger, 36_minilang, extra 31_stackvm trials, low thinking). ETA ~02:00.
5. fp8 medium reference on v3 hard tasks 32-36, 2 trials (running; results/v3-hard-ref-medium.json).
6. v4 authoring (running): Opus overseer + 3 Opus authors, 12 candidates designed from observed failure modes
   (results/v4-authoring/brief.md): randomized differential hidden tests vs an oracle, fixed seed, SCORE n/m
   partial credit, selftest2 validation. Keep filter = fp8 medium 3 trials on OR, on mean SCORE not pass bins:
   keep iff mean SCORE in [0.25, 0.85]; also keep mean SCORE in (0, 0.25) flagged "hard, quant-discriminating";
   reject mean SCORE == 0 (unfair or broken) or > 0.85 (saturated). Note PASS implies SCORE 1.0, so a 3/3 task
   is always > 0.85 and always rejected. Up to two extra author rounds if fewer than 8 keepers; stop when 10
   keepers exist. Reference: after the keeper set is final, the keep-filter trials are the reference only if
   every keeper was run under the identical harness params (same agent dir, thinking, timeout); otherwise
   re-run 3 trials on the final set as results/v4-ref-medium.json. OR concurrency: at most 2 pibench processes;
   the v3 reference (step 5) and v3 tail (step 4) count toward that cap.

## Handoffs and failure handling
- v4 "ready": selftest2 clean, layout check clean, >= 8 keepers, results/v4-ref-medium.json final,
  results/v4-authoring/report.md written. If only 5-7 keepers by 05:00, run them (3 trials) and say so; if < 5,
  keep the GPU on the filler loop and report.
- Each GPU harness invocation is one (quant, suite) unit; env changes and model swaps only at unit boundaries.
- Fixed-seed hidden tests make a task's difficulty partly a property of its seed; reported as a caveat.
- Nothing here is a permission to commit, to change ansible-slb, or to change the managed pi/Ollama config.

## Reports (to phone@fractal)
- ~08:00 interim: tuning winners, 64k reachability and cost, v3/v4 authoring outcome, quality trials done so far,
  anything that leaked. First line states whether the ranking is ready or when it will be.
- Final: quality-vs-speed ranking per quant (mean SCORE with CI, pass rate, fp8 reference, gen tok/s at the
  32k/q8_0 config) on the first line.

## Audit dispositions (results/plan-audit/review-glm.md, review-qwen.md)
Accepted: common ctx and KV for all quants (G1,G2,G3,G13,Q1,Q5); mean SCORE primary, 3 mandatory trials,
all-or-nothing (G4,Q3); score-band keep filter, 0<SCORE<0.25 kept and flagged, PASS=>SCORE 1.0 makes the old
"3/3 with SCORE<0.9" branch unreachable (G5,G6,G7,Q2); serving-stack caveat and delta-as-upper-bound (G8,Q6);
speed pinned to the exact tuple (G9,Q14); ETA re-forecast and timeout tail (G10,Q12); filler loop (G11,Q9);
watchdog + boundary assertions (G12,Q7,Q8); reference re-run rule (G14); interim vs final report (G16,Q4);
4-point fill curves (G17); layout pre-flight (Q11); OR concurrency counts existing runs (Q13).
Rejected: Q1's "server default 4-8k" (the Modelfiles bake 32768, verified with ollama show); G15 seed caveat
noted rather than adding per-case distributions tonight; Q6's local fp8 control (no fp8 27B fits 16 GB).
