# pi bench (local-medium)

| model | size | %GPU | gen tok/s (empty ctx / fullest measured) | pass | mean score | tasks solved | wall/run | out tok/run | tool calls/run |
|---|---|---|---|---|---|---|---|---|---|
| q27-Q3_K_M | 14.95 GB | 90 | 22.0 / 15.3 @26979 | 21/22 | - | 10/11 all-trials | 80s | 1666 | 4.3 |
| q27-Q3_K_L | 15.58 GB | 87 | 14.6 / 12.2 @26979 | 21/22 | - | 10/11 all-trials | 107s | 1526 | 5.4 |
| q27-Q3_K_S | 13.48 GB | 100 | 51.2 / 46.4 @26979 | 22/22 | - | 11/11 all-trials | 47s | 2085 | 5.8 |
| q27-Q2_K_L | 12.14 GB | 100 | 57.2 / 48.6 @26979 | 22/22 | - | 11/11 all-trials | 77s | 4018 | 8.4 |

## Per task (passes/trials)

| task | q27-Q3_K_M | q27-Q3_K_L | q27-Q3_K_S | q27-Q2_K_L |
|---|---|---|---|---|
| 01_rle | 2/2 | 2/2 | 2/2 | 2/2 |
| 02_lru | 2/2 | 2/2 | 2/2 | 2/2 |
| 03_calc | 2/2 | 2/2 | 2/2 | 2/2 |
| 04_csv | 2/2 | 1/2 | 2/2 | 2/2 |
| 05_bugfix | 2/2 | 2/2 | 2/2 | 2/2 |
| 06_refactor | 2/2 | 2/2 | 2/2 | 2/2 |
| 07_dijkstra | 2/2 | 2/2 | 2/2 | 2/2 |
| 08_topo | 2/2 | 2/2 | 2/2 | 2/2 |
| 09_wc | 1/2 | 2/2 | 2/2 | 2/2 |
| 10_intervals | 2/2 | 2/2 | 2/2 | 2/2 |
| 11_roman | 2/2 | 2/2 | 2/2 | 2/2 |
