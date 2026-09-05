# v6 phase 0 — placement

*Rendered from `placement.json`. Resident GB is `/api/ps` `size` / 2^30 (D6-2), the same
field v5 measured, against the ~14.2 GB fair-weather line. `nvidia-smi` peak is recorded
and never used for the verdict (it reads ~1.5 GB high). Speed gate (plan section 4): gen
tok/s at a ~90% fill >= 35 passes, < 20 is spill, between is marginal.*

| quant | ctx | resident GB | %GPU | smi peak MiB | load s | gen tok/s empty | gen tok/s @fill | prompt tok/s @fill | TTFT s | fill tok | verdict | why |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Q2_K_L | 64k | 13.35 | 100% | 15118 | 6.3 | 57.8 | 44.9 | 1337 | 44 | 58421 | **pass** |  |
| IQ3_XXS _(superseded)_ | 64k | 14.72 | 87% | 15332 | 20.9 | 15.1 | 10.3 | 1202 | 49 | 58421 | **spill** | gen 10.3 tok/s |
| IQ3_XS _(superseded)_ | 64k | 15.38 | 82% | 15205 | 16.4 | 10.3 | 5.2 | 1035 | 56 | 58421 | **spill** | gen 5.2 tok/s |
| IQ2_M _(superseded)_ | 48k | 11.68 | 100% | 14134 | 30.9 | 63.9 | 51.9 | 1558 | 28 | 43661 | **pass** |  |
| IQ3_XXS | 64k | 14.31 | 93% | 14968 | 12.2 | 33.7 | 29.0 | 1507 | 39 | 58421 | **marginal** | gen 29.0 tok/s; resident 14.31 GB over the line |
| IQ3_XXS | 48k | 13.07 | 100% | 14676 | 6.8 | 56.7 | 47.0 | 1788 | 24 | 43661 | **pass** |  |
| Q2_K | 48k | 12.46 | 100% | 14042 | 10.5 | 59.1 | 49.2 | 1440 | 30 | 43661 | **pass** |  |
| Q2_K | 64k | 13.07 | 100% | 14672 | 6.4 | 59.2 | 45.1 | 1361 | 43 | 58421 | **pass** |  |
| Q2_K | 96k | 15.04 | 89% | 14976 | 8.0 | 22.0 | 9.0 | 986 | 89 | 87761 | **spill** | gen 9.0 tok/s |
| Q2_K_L | 96k | 16.20 | 83% | 15229 | 13.5 | 19.1 | 8.2 | 946 | 93 | 87761 | **spill** | gen 8.2 tok/s |
| Q3_K_S | 48k | 14.09 | 100% | 15879 | 11.3 | 47.1 | 41.3 | 76 | 571 | 43661 | **spill** | prefill 76 tok/s (TTFT 571s) |
| IQ2_M | 48k | 11.44 | 100% | 13551 | 10.3 | 62.1 | 49.2 | 1511 | 29 | 43661 | **pass** |  |
| IQ2_M | 64k | 12.05 | 100% | 13840 | 6.4 | 61.7 | 46.6 | 1440 | 41 | 58421 | **pass** |  |
| IQ2_M | 96k | 13.27 | 100% | 15068 | 6.4 | 61.0 | 41.9 | 1286 | 68 | 87761 | **pass** |  |
| IQ2_M | 128k | 15.47 | 86% | 15282 | 8.7 | 17.9 | 7.1 | 921 | 128 | 117403 | **spill** | gen 7.1 tok/s |
| IQ3_XS | 64k | 15.12 | 89% | 15276 | 13.7 | 17.2 | 10.4 | 1266 | 46 | 58421 | **spill** | gen 10.4 tok/s |
| IQ3_XS | 48k | 14.34 | 93% | 15193 | 7.7 | 29.6 | 26.7 | 1580 | 28 | 43661 | **marginal** | gen 26.7 tok/s; resident 14.34 GB over the line |
| IQ3_M | 48k | 14.98 | 89% | 15117 | 14.0 | 18.1 | 12.0 | 1327 | 33 | 43661 | **spill** | gen 12.0 tok/s |
| UDQ3KXL | 64k | 14.80 | 91% | 15196 | 33.2 | 24.6 | 12.5 | 1354 | 43 | 58421 | **spill** | gen 12.5 tok/s |
| UDQ3KXL | 48k | 13.45 | 100% | 15376 | 6.5 | 55.6 | 44.8 | 1745 | 25 | 43661 | **pass** |  |
| mrIQ3M | 64k | 14.49 | 92% | 15216 | 10.2 | 25.0 | 22.0 | 1318 | 44 | 58421 | **marginal** | gen 22.0 tok/s; resident 14.49 GB over the line |
| mrIQ3M | 48k | 13.25 | 100% | 15079 | 6.8 | 51.1 | 42.7 | 1621 | 27 | 43661 | **pass** |  |

## Max viable context per quant

*A **passing** rung outranks a marginal one however much context the marginal rung
holds (D6-33): the owner's ruling defines viable as running with no performance
degradation, and marginal is degradation. A marginal rung is reported here only when
the quant has no passing rung at all, and is labelled.*

| quant | max viable ctx | resident there | gen tok/s there | next rung up, and why it is not viable |
|---|---:|---:|---:|---|
| Q2_K_L | 64k | 13.35 | 44.9 | 96k — spill: gen 8.2 tok/s |
| IQ3_XXS | 48k | 13.07 | 47.0 | 64k — marginal: gen 29.0 tok/s; resident 14.31 GB over the line |
| IQ3_XS | 48k _(marginal)_ | 14.34 | 26.7 | 64k — spill: gen 10.4 tok/s |
| IQ2_M | 96k | 13.27 | 41.9 | 128k — spill: gen 7.1 tok/s |
| Q2_K | 64k | 13.07 | 45.1 | 96k — spill: gen 9.0 tok/s |
| Q3_K_S | **none** | - | - | 48k — spill: prefill 76 tok/s (TTFT 571s) |
| IQ3_M | **none** | - | - | 48k — spill: gen 12.0 tok/s |
| UDQ3KXL | 48k | 13.45 | 44.8 | 64k — spill: gen 12.5 tok/s |
| mrIQ3M | 48k | 13.25 | 42.7 | 64k — marginal: gen 22.0 tok/s; resident 14.49 GB over the line |
