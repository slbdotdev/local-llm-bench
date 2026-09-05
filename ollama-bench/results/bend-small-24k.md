# pi bench (bend-small-24k)

| model | size | %GPU | gen tok/s (empty ctx / fullest measured) | pass | mean score | tasks solved | wall/run | out tok/run | tool calls/run | correct | visibly_failed | confidently_wrong | confidently_wrong rate | length stops |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| q27-Q2_K_L-24k | 11.83 GB | 100 | 58.5 / 53.6 @19994 | 7/8 | 0.97 (8/8 runs) | 7/8 all-trials | 41s | 2136 | 5.4 | 7 | 0 | 1 | 12.5% | 0 in 0/8 |
| q27-Q3_K_S-24k | 13.18 GB | 100 | 52.2 / 48.5 @19994 | 7/8 | 0.98 (8/8 runs) | 7/8 all-trials | 55s | 2648 | 6.1 | 7 | 0 | 1 | 12.5% | 0 in 0/8 |
| q27-Q3_K_M-24k | 14.0 GB | 100 | 50.7 / 46.7 @19994 | 6/8 | 0.97 (8/8 runs) | 6/8 all-trials | 41s | 1865 | 5.1 | 6 | 0 | 2 | 25.0% | 0 in 0/8 |
| q27-IQ3_M-24k | 13.35 GB | 100 | 52.4 / 48.7 @19994 | 6/8 | 0.93 (8/8 runs) | 6/8 all-trials | 36s | 1719 | 5.6 | 6 | 0 | 2 | 25.0% | 0 in 0/8 |

## Per task (passes/trials)

| task | q27-Q2_K_L-24k | q27-Q3_K_S-24k | q27-Q3_K_M-24k | q27-IQ3_M-24k |
|---|---|---|---|---|
| g01 | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) |
| g02 | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) |
| g03 | 1/1 (score 1.00) | 0/1 (score 0.87) | 0/1 (score 0.87) | 0/1 (score 0.53) |
| g04 | 1/1 (score 1.00) | 1/1 (score 1.00) | 0/1 (score 0.92) | 0/1 (score 0.92) |
| t01 | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) |
| t02 | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) |
| t03 | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) |
| t04 | 0/1 (score 0.75) | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) |
