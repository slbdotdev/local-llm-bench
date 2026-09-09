# pi bench (deepseek-v41-preview-2026-09-09)

| model | size | %GPU | gen tok/s (empty ctx / fullest measured) | pass | mean score | tasks solved | wall/run | out tok/run | eff tok/s (wall) | tool calls/run | correct | visibly_failed | confidently_wrong | confidently_wrong rate | length stops |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek-v4.1-flash-expires-on-0910 | ? GB | ? | ? | 8/8 | 1.00 (8/8 runs) | 8/8 all-trials | 141s | 10135 | 209.8 | 28.9 | 8 | 0 | 0 | 0.0% | 1 in 1/8 |

## Per task (passes/trials)

| task | deepseek-v4.1-flash-expires-on-0910 |
|---|---|
| g01 | 1/1 (score 1.00) |
| g02 | 1/1 (score 1.00) |
| g03 | 1/1 (score 1.00) |
| g04 | 1/1 (score 1.00) |
| t01 | 1/1 (score 1.00) |
| t02 | 1/1 (score 1.00) |
| t03 | 1/1 (score 1.00) |
| t04 | 1/1 (score 1.00) |

## Per task eff tok/s (wall)

out_tokens / wall_s per run, meaned per task. Wall includes tool execution, grading and
network round-trips, so this is NOT decode throughput and must not be read as ollama gen_tps.

| task | deepseek-v4.1-flash-expires-on-0910 |
|---|---|
| g01 | 258.9 |
| g02 | 24.5 |
| g03 | 211.3 |
| g04 | 229.8 |
| t01 | 305.1 |
| t02 | 208.5 |
| t03 | 197.4 |
| t04 | 242.7 |
