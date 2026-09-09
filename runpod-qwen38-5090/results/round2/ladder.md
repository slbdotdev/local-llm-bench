# Round two ladder

Outcome: row 0 measured on-pod after the public-proxy 403 was bypassed. The result is far below the round-one baseline, so rows 1–8 were not run.

| row | configuration | decode t/s | tau | sanity | exact command |
|---:|---|---:|---:|---|---|
| 0 | pinned cu129, native qwen3_5_mtp n=3, FP8 KV, prefix cache, 131072, seqs 4, batched 4096, MM zero, skip profiling, 100 GB disk | 48.77059339547925 median | ~2.985 | not run | sakamakismile/Qwen3.8-27B-MTP-NVFP4 --served-model-name qwen38 --kv-cache-dtype fp8 --enable-prefix-caching --max-model-len 131072 --skip-mm-profiling --max-num-seqs 4 --max-num-batched-tokens 4096 --limit-mm-per-prompt JSON --speculative-config JSON |

| row | decode t/s | tau | sanity | command/result |
|---:|---:|---:|---|---|
| 0 | — | — | blocked | boot PASS on 100 GB; harness padded request HTTP 403, minimal curl HTTP 200 |

Round-one baseline: 184.32 t/s median; 300 t/s gate: FAIL.

## Final methodology correction and resumed stop

The written early-EOS policy excludes every row that terminates before the requested 256 tokens. The authoritative retrospective medians are baseline 149.04233143870985 (12/12), row 0 135.26698280871545 (9/12), row 1a n=5 130.00625279864605 (8/12), row 1b n=7 120.35735889639692 (9/12), and graph row 141.52601944441466 (9/12). Earlier values in this file used the substituted `completion_tokens >= 16` rule and remain in the audit trail only.

The requested one-live-pod continuation reached no new rung. Two launch attempts failed before model boot (entrypoint/quoting); the replacement pod then read back CUDA 12.8 before spend, below the >=12.9 floor, so the campaign stopped. No same-pod TPS result is claimed.

The n=5 sanity result is corrected separately: normalizing whitespace makes the Fibonacci case pass, so its prior 4/5 result was a formatting artifact. Applying one exclusion rule to both rows retains only `completion_tokens == 256`: row 0 is 135.26698280871545 (9/12) and n=5 is 130.00625279864605 (8/12). The n=5 raw median, 121.45609259931331, includes the completion_tokens=1 / decode_tps=0.0 trial.

Two further one-live-pod reruns for n=5→n=7 were blocked at pre-spend read-back: both pods reported CUDA 12.8. They were deleted without boot or measurement, so no clean n=5/n=7 rerun result is available.

Owner retraction supersedes that one-pod method. The correct shape is one fresh cold pod per configuration, with a disclosed ±10% pod-to-pod term; differences below ~10% are not reportable. Separate n=5 attempts were stopped by CUDA 12.8, argument serialization, and container-creation failures before valid measurement. n=7 was not launched within the remaining budget.
## Resumed TPS campaign results

The corrected cold baseline was 149.04233143870985 decode TPS (12 rows). Row 0 passed its ±10% gate at 134.50816926569888 TPS (11 valid rows after early-EOS exclusion; sanity 5/5). The reached ladder was:

| row | configuration | corrected decode TPS | sanity | result |
|---:|---|---:|---|---|
| baseline | MTP n=3, cold re-derivation | 149.04233143870985 | not assessed | reference |
| 0 | MTP n=3 | 134.50816926569888 | 5/5 pass | gate PASS |
| 1a | MTP n=5 | 121.476713806405 | 4/5 pass | reached; sanity FAIL |
| 1b | MTP n=7 | 115.48142042919815 | 4/5 pass | reached; sanity FAIL |
| 2 | MTP n=3 + FULL_DECODE_ONLY graphs | 140.8465264747512 | 5/5 pass | reached |

Row 2 used one early-EOS exclusion from 12 rows. Post-measurement tau was approximately 2.9101; reported tau values are pod-lifetime counter snapshots, not isolated deltas. The 300 TPS target was not reached.

2026-09-08T09:03:41Z CORRECTION — The preceding “Resumed TPS campaign results” table is retained as historical audit material, but its retired medians and FAIL labels are superseded. Under the one-rule full-length policy, the arm is n=3 baseline pod 149.04233143870985 TPS, n=3 row-0 pod 135.26698280871545 TPS, n=5 130.00625279864605 TPS, and n=7 120.35735889639692 TPS, with tau 2.762 → 3.291 → 3.585. Both n=5 and n=7 checker FAILs reverse to 5/5 under whitespace-normalized code matching; they were formatting artifacts, not correctness failures. Row 2’s stored sanity output likewise evaluates 5/5 under the fixed checker. The row-1 finding is monotone decline as draft length rises: longer drafts cost more per step than acceptance returns, n=3 is best of the arm, and no adjacent step clears the disclosed ±10% pod-to-pod term.
