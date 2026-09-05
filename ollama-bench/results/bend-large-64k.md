# pi bench (bend-large-64k)

| model | size | %GPU | gen tok/s (empty ctx / fullest measured) | pass | mean score | tasks solved | wall/run | out tok/run | tool calls/run | correct | visibly_failed | confidently_wrong | confidently_wrong rate | length stops |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| q27-Q2_K_L-64k | 13.35 GB | 100 | 58.1 / 51.2 @26979 | 7/8 | 0.98 (8/8 runs) | 7/8 all-trials | 169s | 8349 | 17.0 | 7 | 0 | 1 | 12.5% | 2 in 2/8 |
| q27-Q3_K_S-64k | ? GB | ? | ? | 3/3 | 1.00 (3/3 runs) | 3/3 all-trials | 1245s | 9898 | 16.7 | 3 | 0 | 0 | 0.0% | 0 in 0/3 |
| q27-IQ3_M-64k | ? GB | ? | ? | 1/1 | 1.00 (1/1 runs) | 1/1 all-trials | 216s | 1685 | 12.0 | 1 | 0 | 0 | 0.0% | 0 in 0/1 |

## Per task (passes/trials)

| task | q27-Q2_K_L-64k | q27-Q3_K_S-64k | q27-IQ3_M-64k |
|---|---|---|---|
| t03 | 1/1 (score 1.00) | 1/1 (score 1.00) | 1/1 (score 1.00) |
