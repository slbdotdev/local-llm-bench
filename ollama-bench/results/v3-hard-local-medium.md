# pi bench (v3-hard-local-medium)

| model | size | %GPU | gen tok/s (empty ctx / fullest measured) | pass | mean score | tasks solved | wall/run | out tok/run | tool calls/run |
|---|---|---|---|---|---|---|---|---|---|
| q27-Q2_K_L | ? GB | ? | ? | 2/5 | 0.57 (5/5 runs) | 2/5 all-trials | 541s | 28790 | 12.0 |
| q27-Q3_K_S | ? GB | ? | ? | 2/5 | 0.62 (5/5 runs) | 2/5 all-trials | 609s | 26761 | 14.8 |
| q27-IQ3_M | ? GB | ? | ? | 0/5 | 0.40 (5/5 runs) | 0/5 all-trials | 1542s | 11964 | 4.6 |
| q27-Q3_K_M | ? GB | ? | ? | 3/5 | 0.90 (5/5 runs) | 3/5 all-trials | 1528s | 28750 | 19.8 |

## Per task (passes/trials)

| task | q27-Q2_K_L | q27-Q3_K_S | q27-IQ3_M | q27-Q3_K_M |
|---|---|---|---|---|
| 32_wirefmt | 0/1 (score 0.00) | 0/1 (score 0.55) | 0/1 (score 0.24) | 1/1 (score 1.00) |
| 33_spanmap | 0/1 (score 0.83) | 0/1 (score 0.00) | 0/1 (score 0.00) | 0/1 (score 0.83) |
| 34_tmplfix | 1/1 (score 1.00) | 1/1 (score 1.00) | 0/1 (score 0.81) | 1/1 (score 1.00) |
| 35_ledger | 1/1 (score 1.00) | 1/1 (score 1.00) | 0/1 (score 0.97) | 1/1 (score 1.00) |
| 36_minilang | 0/1 (score 0.00) | 0/1 (score 0.54) | 0/1 (score 0.00) | 0/1 (score 0.67) |
