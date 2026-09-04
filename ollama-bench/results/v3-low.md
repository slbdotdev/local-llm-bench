# pi bench (v3-low)

| model | size | %GPU | gen tok/s (empty ctx / fullest measured) | pass | mean score | tasks solved | wall/run | out tok/run | tool calls/run |
|---|---|---|---|---|---|---|---|---|---|
| qwen/qwen3.8-27b | ? GB | ? | ? | 54/57 | 0.99 (57/57 runs) | 14/17 all-trials | 239s | 14525 | 10.9 |

## Per task (passes/trials)

| task | qwen/qwen3.8-27b |
|---|---|
| 20_csv | 3/3 (score 1.00) |
| 21_json_bugfix | 3/3 (score 1.00) |
| 22_calc | 3/3 (score 1.00) |
| 23_duration | 3/3 (score 1.00) |
| 24_inventory | 3/3 (score 1.00) |
| 25_stackvm | 3/3 (score 1.00) |
| 26_iniconf | 3/3 (score 1.00) |
| 27_semver | 5/6 (score 0.99) |
| 28_cron | 3/3 (score 1.00) |
| 29_mdtable | 3/3 (score 1.00) |
| 30_bitpack | 3/3 (score 1.00) |
| 31_stackvm | 5/6 (score 1.00) |
| 32_wirefmt | 3/3 (score 1.00) |
| 33_spanmap | 3/3 (score 1.00) |
| 34_tmplfix | 2/3 (score 0.88) |
| 35_ledger | 3/3 (score 1.00) |
| 36_minilang | 3/3 (score 1.00) |
