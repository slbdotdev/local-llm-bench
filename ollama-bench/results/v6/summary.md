# v6 — per-quant summary (plan section 5)

*Built by `summarize.py` from the scored artifacts and `placement.json`. Resident GB is
`/api/ps` size / 2^30. `n` is trials, over the tasks the working-margin rule admits to the
cell (D6-1), which is 8 in the tiny band, 6 in a 64k large band and 3 in a 48k one. Wall
figures are seconds. `cw` is the confidently-wrong rate, which outranks pass rate.*

| quant | max viable ctx | resident | gen tok/s there | gen tok/s @64k |
|---|---:|---:|---:|---:|
| IQ2_M | 96k | 13.27 GB | 41.9 | 46.6 |
| IQ3_M | **none** | - | - | - |
| IQ3_XS | 48k | 14.34 GB | 26.7 | 10.4 |
| IQ3_XXS | 48k | 13.07 GB | 47.0 | 29.0 |
| Q2_K | 64k | 13.07 GB | 45.1 | 45.1 |
| Q2_K_L | 64k | 13.35 GB | 44.9 | 44.9 |
| Q3_K_S | **none** | - | - | - |
| UDQ3KXL | 48k | 13.45 GB | 44.8 | 12.5 |
| mrIQ3M | 48k | 13.25 GB | 42.7 | 22.0 |

## Scored cells

| cell | band | tasks | n | pass | cw rate | median wall | max wall | mean in tok | mean peak-prompt | mean out tok | turns | tools | timeouts | achieved out tok/s | generate | transform |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| IQ2_M-64k | large | 6 | 6 | 3/6 | 17% | 170 | 600 | 155623 | 19818 | 7343 | 14.2 | 21.0 | 2 | 35.0 | marginal (2/3 solved) | not viable (1/3 solved) |
| IQ2_M-64k | tiny | 8 | 8 | 8/8 | 0% | 30 | 183 | 20505 | 4303 | 3591 | 6.1 | 6.9 | 0 | 55.5 | viable (4/4 solved) | viable (4/4 solved) |
| IQ3_XS-48k | large | 2 | 2 | 1/2 | 50% | 246 | 438 | 235800 | 19682 | 6242 | 16.5 | 19.5 | 0 | 24.6 | not viable (0/1 solved) | viable (1/1 solved) |
| IQ3_XXS-48k | large | 2 | 2 | 1/2 | 50% | 160 | 286 | 210604 | 17426 | 7646 | 18.0 | 21.0 | 0 | 43.6 | not viable (0/1 solved) | viable (1/1 solved) |
| Q2_K-48k | large | 2 | 2 | 2/2 | 0% | 316 | 600 | 408484 | 22175 | 14458 | 26.0 | 30.5 | 1 | 40.8 | not viable (0/1 solved) | viable (1/1 solved) |
| Q2_K-64k | large | 6 | 6 | 4/6 | 0% | 126 | 414 | 145958 | 19330 | 9090 | 13.3 | 14.7 | 0 | 44.3 | not viable (1/3 solved) | viable (3/3 solved) |
| Q2_K_L-48k | large | 2 | 2 | 2/2 | 0% | 239 | 452 | 375284 | 22416 | 11502 | 21.5 | 26.5 | 0 | 41.2 | viable (1/1 solved) | viable (1/1 solved) |
| Q2_K_L-64k | large | 6 | 6 | 4/6 | 17% | 141 | 582 | 228541 | 18382 | 10525 | 18.5 | 19.3 | 0 | 43.9 | marginal (2/3 solved) | marginal (2/3 solved) |
| Q2_K_L-64k | tiny | 8 | 8 | 6/8 | 25% | 28 | 153 | 21729 | 4592 | 3183 | 6.2 | 6.1 | 0 | 50.9 | viable (3/4 solved) | viable (3/4 solved) |
| UDQ3KXL-48k | large | 2 | 2 | 2/2 | 0% | 172 | 295 | 253074 | 19838 | 7851 | 18.5 | 32.0 | 0 | 43.1 | viable (1/1 solved) | viable (1/1 solved) |
| mrIQ3M-48k | large | 2 | 2 | 1/2 | 0% | 213 | 379 | 320704 | 22768 | 9844 | 21.0 | 29.5 | 0 | 41.7 | viable (1/1 solved) | not viable (0/1 solved) |

## Per task (passes/trials)

| task | IQ2_M-64k large | IQ2_M-64k tiny | IQ3_XS-48k large | IQ3_XXS-48k large | Q2_K-48k large | Q2_K-64k large | Q2_K_L-48k large | Q2_K_L-64k large | Q2_K_L-64k tiny | UDQ3KXL-48k large | mrIQ3M-48k large |
|---|---|---|---|---|---|---|---|---|---|---|---|
| g01 | 1/1 | 1/1 | - | - | - | 1/1 | - | 1/1 | 1/1 | - | - |
| g02 | 1/1 | 1/1 | - | - | - | 0/1 | - | 1/1 | 1/1 | - | - |
| g03 | 0/1 | 1/1 | 0/1 | 0/1 | 1/1 | 0/1 | 1/1 | 0/1 | 0/1 | 1/1 | 1/1 |
| g04 | - | 1/1 | - | - | - | - | - | - | 1/1 | - | - |
| t01 | 0/1 | 1/1 | - | - | - | 1/1 | - | 1/1 | 1/1 | - | - |
| t02 | 0/1 | 1/1 | - | - | - | 1/1 | - | 0/1 | 1/1 | - | - |
| t03 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 0/1 |
| t04 | - | 1/1 | - | - | - | - | - | - | 0/1 | - | - |
