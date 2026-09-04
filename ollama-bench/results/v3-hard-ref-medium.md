# pi bench (v3-hard-ref-medium)

| model | size | %GPU | gen tok/s (empty ctx / fullest measured) | pass | mean score | tasks solved | wall/run | out tok/run | tool calls/run |
|---|---|---|---|---|---|---|---|---|---|
| qwen/qwen3.8-27b | ? GB | ? | ? | 8/10 | 0.99 (10/10 runs) | 3/5 all-trials | 417s | 27201 | 24.6 |

## Per task (passes/trials)

| task | qwen/qwen3.8-27b |
|---|---|
| 32_wirefmt | 1/2 (score 0.98) |
| 33_spanmap | 2/2 (score 1.00) |
| 34_tmplfix | 2/2 (score 1.00) |
| 35_ledger | 1/2 (score 0.99) |
| 36_minilang | 2/2 (score 1.00) |
