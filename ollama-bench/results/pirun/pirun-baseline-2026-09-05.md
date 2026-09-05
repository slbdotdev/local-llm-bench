# pi-run baseline — GLM 5.3 Flash through pi, v5 suite, 2026-09-05

## tiny band (`pirun-baseline-tiny`)

| task | pass | wall s | usage_in | usage_in_peak | usage_out | turns | tools | stop reason | auto_retry | compaction | error |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| g01 | PASS | 32.1 | 22248 | 5882 | 2460 | 6 | 5 | stop | 0 | 0 |  |
| g02 | PASS | 8.9 | 17158 | 3593 | 930 | 6 | 5 | stop | 0 | 0 |  |
| g03 | FAIL | 23.4 | 26749 | 4756 | 2621 | 8 | 11 | stop | 0 | 0 |  |
| g04 | FAIL | 46.1 | 26498 | 4663 | 2772 | 8 | 8 | stop | 0 | 0 |  |
| t01 | PASS | 21.6 | 23580 | 4167 | 1926 | 8 | 8 | stop | 0 | 0 |  |
| t02 | PASS | 7.8 | 9925 | 2356 | 540 | 5 | 4 | stop | 0 | 0 |  |
| t03 | PASS | 4.0 | 18106 | 7477 | 397 | 4 | 3 | stop | 0 | 0 |  |
| t04 | FAIL | 5.3 | 8955 | 2026 | 310 | 5 | 6 | stop | 0 | 0 |  |
| **total (8 tasks)** | **5/8** | **149.2** | **153219** | | **11956** | **50** | **50** | | | | |

## large band (`pirun-baseline-large`)

| task | pass | wall s | usage_in | usage_in_peak | usage_out | turns | tools | stop reason | auto_retry | compaction | error |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| g01 | PASS | 40.9 | 84932 | 13840 | 4499 | 10 | 11 | stop | 0 | 0 |  |
| g02 | PASS | 37.4 | 84265 | 8673 | 2214 | 14 | 14 | stop | 0 | 0 |  |
| g03 | FAIL | 614.6 | 2282699 | 100241 | 55662 | 47 | 46 | stop | 0 | 0 |  |
| g04 | PASS | 29.6 | 73161 | 13523 | 1945 | 9 | 12 | stop | 0 | 0 |  |
| t01 | PASS | 156.7 | 470586 | 31175 | 15590 | 30 | 30 | stop | 0 | 0 |  |
| t02 | PASS | 18.5 | 54886 | 8623 | 1178 | 10 | 11 | stop | 0 | 0 |  |
| t03 | PASS | 35.6 | 76693 | 18077 | 940 | 8 | 7 | stop | 0 | 0 |  |
| t04 | PASS | 19.1 | 43400 | 6541 | 975 | 10 | 10 | stop | 0 | 0 |  |
| **total (8 tasks)** | **7/8** | **952.4** | **3170622** | | **83003** | **138** | **141** | | | | |

## Both bands

| | value |
|---|---|
| tasks | 16 |
| passed | 12/16 |
| summed task wall | 1101.6 s |
| usage_in (summed) | 3323841 |
| usage_out (summed) | 94959 |

## Run

| | value |
|---|---|
| date | 2026-09-05 (host `date` reports 2026-09-04) |
| started | 2026-09-04T18:55:52-06:00 |
| finished | 2026-09-04T19:11:46-06:00 |
| wall clock, whole run (both bands in parallel) | 954 s (15 m 54 s) |
| tiny band process | 18:55:52 -> 18:58:21, exit 0 |
| large band process | 18:55:52 -> 19:11:45, exit 0 |
| OpenRouter key usage before | USD 36.890078 |
| OpenRouter key usage after | USD 37.087310 |
| key spend delta | **USD 0.197232** |
| pi version | 0.85.0 |
| node | v24.20.0 |
| model | `z-ai/glm-5.3-flash` via `--provider openrouter` |
| agent dir | managed `C:\Users\slb\.pi\agent` (no `--agent-dir`) |
| bench code commit (scratch clone) | `07de475` ("large band and the headroom bend"), clean |
| campaign clone at commit time | `a9ab63e` ("v6 plan revised"); it advanced by two commits from another session while this ran |
| scratch clone | `C:\Users\slb\bench-pirun` (clone of `D:\local-llm-bench`) |
| GPU before / after | 711 MiB, 0% / 721 MiB, 0% (idle; openrouter provider, no Ollama) |

## Exact commands

Run from WSL as `bash run-baseline.sh` in the scratch clone's `ollama-bench/`;
the bench is Windows-only and is driven through the Windows interpreter over
interop, no ssh and no pwsh. `PY=/mnt/c/Users/slb/scoop/apps/python/current/python.exe`.

```
PYTHONUTF8=1 "$PY" pibench.py --provider openrouter --models z-ai/glm-5.3-flash \
    --think medium --trials 1 --no-tps --timeout 900 \
    --tasks-dir results/v5/authoring/round2/suite-0 --num-ctx 24576 \
    --tag pirun-baseline-tiny > results/pirun-baseline-tiny.log 2>&1

PYTHONUTF8=1 "$PY" pibench.py --provider openrouter --models z-ai/glm-5.3-flash \
    --think medium --trials 1 --no-tps --timeout 900 \
    --tasks-dir results/v5/authoring/round3/suite --num-ctx 65536 \
    --tag pirun-baseline-large > results/pirun-baseline-large.log 2>&1
```

Both were launched together and `wait`ed on. Key spend was read before and
after with the `usage()` one-liner from `results/glm-v4.sh`.

## Notes

Twelve of sixteen tasks passed: 5/8 tiny, 7/8 large. No timeouts, no memory-guard
kills, no non-zero `rc`, no `errors` entries, and every trial's last stop reason was
`stop`; `auto_retry_end` and `compaction_end` were zero on all sixteen. Every failure
was graded `confidently_wrong`, none `visibly_failed`. One row dominates the numbers:
large-band `g03` ran 614.6 s over 47 turns and 46 tool calls for 55,662 output tokens
and 2.28 M cumulative input tokens, and still failed; its single-turn input peak,
100,241 tokens, is the only figure in the run above the band's nominal 64k label, which
is expected because `--num-ctx` is an Ollama-side setting and is ignored on the
openrouter provider. Excluding `g03`, the large band's whole cost is 337.8 s and
888 k cumulative input tokens. The three tiny-band families that fail are `g03`, `g04` and `t04`,
overlapping the discriminating set the campaign's reference arms found (`g04`, `t01`,
`g03`), so nothing here looks like a harness fault.
