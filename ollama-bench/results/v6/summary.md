# v6 — per-quant summary (plan section 5)

*Built by `summarize.py` from the scored artifacts and `placement.json`. Resident GB is
`/api/ps` size / 2^30. `n` is trials, over the tasks the working-margin rule admits to the
cell (D6-1), which is 8 in the tiny band, 6 in a 64k large band and 3 in a 48k one. Wall
figures are seconds. `cw` is the confidently-wrong rate, which outranks pass rate.*

| quant | max viable ctx | resident | gen tok/s there | gen tok/s @64k |
|---|---:|---:|---:|---:|
| IQ2_M | 48k | 11.68 GB | 51.9 | - |
| IQ3_XS | **none** | - | - | 5.2 |
| IQ3_XXS | 64k | 14.31 GB | 29.0 | 29.0 |
| Q2_K | 64k | 13.07 GB | 45.1 | 45.1 |
| Q2_K_L | 64k | 13.35 GB | 44.9 | 44.9 |

## Scored cells

| cell | band | tasks | n | pass | cw rate | median wall | max wall | mean in tok | mean peak-prompt | mean out tok | turns | tools | timeouts | achieved out tok/s | generate | transform |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|

## Per task (passes/trials)

| task |  |
|---|
