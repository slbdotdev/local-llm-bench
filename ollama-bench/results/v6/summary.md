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
| UDIQ3S | 64k | 13.03 GB | 46.5 | 46.5 |
| UDQ3KXL | 48k | 13.45 GB | 44.8 | 12.5 |
| mrIQ3M | 48k | 13.25 GB | 42.7 | 22.0 |

## Scored cells

| cell | band | tasks | n | pass | cw rate | median wall | max wall | mean in tok | mean peak-prompt | mean out tok | turns | tools | timeouts | achieved out tok/s | generate | transform |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| IQ2_M-64k | large | 6 | 18 | 12/18 | 11% | 131 | 600 | 175221 | 18244 | 9138 | 15.3 | 18.6 | 3 | 43.3 | marginal (2/3 solved) | marginal (2/3 solved) |
| IQ2_M-64k | tiny | 8 | 24 | 20/24 | 4% | 31 | 300 | 23329 | 4544 | 3672 | 6.5 | 7.3 | 2 | 52.6 | viable (3/4 solved) | viable (4/4 solved) |
| IQ2_M-96k | large | 8 | 8 | 6/8 | 0% | 126 | 578 | 302495 | 22262 | 12801 | 21.0 | 30.4 | 0 | 48.8 | viable (3/4 solved) | viable (3/4 solved) |
| IQ3_XS-48k | large | 3 | 3 | 2/3 | 33% | 181 | 438 | 203443 | 18386 | 5678 | 16.7 | 19.0 | 0 | 24.8 | marginal (1/2 solved) | viable (1/1 solved) |
| IQ3_XS-48k | tiny | 8 | 8 | 6/8 | 25% | 62 | 168 | 21104 | 4412 | 2185 | 6.2 | 6.4 | 0 | 26.6 | viable (3/4 solved) | viable (3/4 solved) |
| IQ3_XXS-48k | large | 3 | 3 | 2/3 | 33% | 154 | 286 | 205433 | 17870 | 7412 | 17.7 | 21.0 | 0 | 44.1 | marginal (1/2 solved) | viable (1/1 solved) |
| IQ3_XXS-48k | tiny | 8 | 8 | 5/8 | 38% | 38 | 300 | 35389 | 5129 | 3858 | 7.8 | 8.5 | 1 | 49.1 | not viable (1/4 solved) | viable (3/4 solved) |
| Q2_K-48k | large | 2 | 2 | 2/2 | 0% | 316 | 600 | 408484 | 22175 | 14458 | 26.0 | 30.5 | 1 | 40.8 | not viable (0/1 solved) | viable (1/1 solved) |
| Q2_K-64k | large | 6 | 6 | 4/6 | 0% | 126 | 414 | 145958 | 19330 | 9090 | 13.3 | 14.7 | 0 | 44.3 | not viable (1/3 solved) | viable (3/3 solved) |
| Q2_K-64k | tiny | 8 | 8 | 6/8 | 25% | 35 | 166 | 17115 | 4069 | 3375 | 5.4 | 6.1 | 0 | 52.3 | viable (3/4 solved) | viable (3/4 solved) |
| Q2_K_L-48k | large | 2 | 2 | 2/2 | 0% | 239 | 452 | 375284 | 22416 | 11502 | 21.5 | 26.5 | 0 | 41.2 | viable (1/1 solved) | viable (1/1 solved) |
| Q2_K_L-64k | large | 6 | 6 | 4/6 | 17% | 141 | 582 | 228541 | 18382 | 10525 | 18.5 | 19.3 | 0 | 43.9 | marginal (2/3 solved) | marginal (2/3 solved) |
| Q2_K_L-64k | tiny | 8 | 8 | 6/8 | 25% | 28 | 153 | 21729 | 4592 | 3183 | 6.2 | 6.1 | 0 | 50.9 | viable (3/4 solved) | viable (3/4 solved) |
| UDQ3KXL-48k | large | 3 | 9 | 8/9 | 11% | 72 | 306 | 177928 | 18911 | 6361 | 13.8 | 20.3 | 0 | 42.9 | viable (2/2 solved) | viable (1/1 solved) |
| UDQ3KXL-48k | tiny | 8 | 24 | 18/24 | 25% | 27 | 300 | 19620 | 4125 | 2492 | 5.9 | 6.0 | 1 | 49.2 | viable (3/4 solved) | viable (3/4 solved) |
| mrIQ3M-48k | large | 3 | 3 | 2/3 | 0% | 71 | 379 | 241462 | 19667 | 7493 | 17.3 | 23.3 | 0 | 40.8 | viable (2/2 solved) | not viable (0/1 solved) |
| mrIQ3M-48k | tiny | 8 | 8 | 6/8 | 25% | 34 | 213 | 19416 | 4206 | 3163 | 6.0 | 6.4 | 0 | 49.7 | marginal (2/4 solved) | viable (4/4 solved) |

## Per task (passes/trials)

| task | IQ2_M-64k large | IQ2_M-64k tiny | IQ2_M-96k large | IQ3_XS-48k large | IQ3_XS-48k tiny | IQ3_XXS-48k large | IQ3_XXS-48k tiny | Q2_K-48k large | Q2_K-64k large | Q2_K-64k tiny | Q2_K_L-48k large | Q2_K_L-64k large | Q2_K_L-64k tiny | UDQ3KXL-48k large | UDQ3KXL-48k tiny | mrIQ3M-48k large | mrIQ3M-48k tiny |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| g01 | 3/3 | 2/3 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | - | 1/1 | 1/1 | - | 1/1 | 1/1 | 3/3 | 3/3 | 1/1 | 1/1 |
| g02 | 3/3 | 3/3 | 1/1 | - | 1/1 | - | 1/1 | - | 0/1 | 1/1 | - | 1/1 | 1/1 | - | 3/3 | - | 1/1 |
| g03 | 0/3 | 1/3 | 1/1 | 0/1 | 0/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | 1/1 | 0/1 | 0/1 | 2/3 | 0/3 | 1/1 | 0/1 |
| g04 | - | 3/3 | 0/1 | - | 1/1 | - | 0/1 | - | - | 1/1 | - | - | 1/1 | - | 2/3 | - | 0/1 |
| t01 | 1/3 | 3/3 | 0/1 | - | 1/1 | - | 1/1 | - | 1/1 | 1/1 | - | 1/1 | 1/1 | - | 3/3 | - | 1/1 |
| t02 | 2/3 | 3/3 | 1/1 | - | 1/1 | - | 1/1 | - | 1/1 | 1/1 | - | 0/1 | 1/1 | - | 3/3 | - | 1/1 |
| t03 | 3/3 | 3/3 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 1/1 | 3/3 | 3/3 | 0/1 | 1/1 |
| t04 | - | 2/3 | 1/1 | - | 0/1 | - | 0/1 | - | - | 0/1 | - | - | 0/1 | - | 1/3 | - | 1/1 |
