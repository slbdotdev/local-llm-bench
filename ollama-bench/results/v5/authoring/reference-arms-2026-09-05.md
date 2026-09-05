# Reference arms on the v5 suite — Haiku, Sonnet, GLM, Luna

*Assembled 2026-09-05 by the control session from the durable results files, per task,
pass counts over trials. Haiku and Sonnet ran under Claude Code (`round2/`, `round3/`,
`tally_all.py`); GLM 5.3 Flash ran through `pibench.py` under `pi-run`'s harness, baseline
before and sanity after the resilience extension (`results/pirun/`); Luna ran through native
Codex at `high`, eight tasks concurrently (`gate-luna/`). Local quants are not here: the v6
sweep (`results/v6/`) is producing those rows.*

Tiny band (24k). Haiku and Sonnet: three trials over `round2/suite-0..2`, which differ only in
the t02 and t04 candidate; GLM and Luna: one trial each on `suite-0`.

| task | Haiku | Sonnet | GLM baseline | GLM sanity | Luna |
| --- | --- | --- | --- | --- | --- |
| g01 | 3/3 | 3/3 | 1/1 | 1/1 | 1/1 |
| g02 | 3/3 | 3/3 | 1/1 | 1/1 | 1/1 |
| g03 | 1/3 | 3/3 | 0/1 | 0/1 | 1/1 |
| g04 | 3/3 | 3/3 | 0/1 | 0/1 | 1/1 |
| t01 | 3/3 | 3/3 | 1/1 | 1/1 | 1/1 |
| t02 | 2/3 | 3/3 | 1/1 | 0/1 | 1/1 |
| t03 | 3/3 | 3/3 | 1/1 | 1/1 | 1/1 |
| t04 | 3/3 | 3/3 | 0/1 | 1/1 | 1/1 |
| **total** | **21/24** | **24/24** | **5/8** | **5/8** | **8/8** |

Large band (64k), every arm on `round3/suite`.

| task | Haiku | Sonnet | GLM baseline | GLM sanity | Luna |
| --- | --- | --- | --- | --- | --- |
| g01 | 3/3 | 2/2 | 1/1 | 1/1 | 1/1 |
| g02 | 3/3 | 2/2 | 1/1 | 1/1 | 1/1 |
| g03 | 1/3 | 2/2 | 0/1 | 1/1 | 1/1 |
| g04 | 0/3 | 2/2 | 1/1 | 1/1 | 1/1 |
| t01 | 1/3 | 2/2 | 1/1 | 0/1 | 1/1 |
| t02 | 3/3 | 2/2 | 1/1 | 1/1 | 1/1 |
| t03 | 3/3 | 2/2 | 1/1 | 1/1 | 1/1 |
| t04 | 3/3 | 2/2 | 1/1 | 1/1 | 0/1 |
| **total** | **17/24** | **16/16** | **7/8** | **7/8** | **7/8** |

Reading it: Sonnet is the ceiling at 40/40. Luna sits just under it at 15/16, its one miss
t04 large, a lexical-checker miss on a correct-looking answer. Haiku and GLM sit at the same
level (79% and 75%) and fail on different tasks: Haiku's misses are g03, g04 and t01 in the
large band, GLM's are g03 and g04 in the tiny band and one of g03 or t01 in the large. g03 is
the one task every non-Sonnet arm has failed at least once. GLM's context was not restricted
in either band: `--num-ctx` is ignored on the OpenRouter path, and g03 large peaked at 100k
prompt tokens. Wall and token figures per arm are on the source pages named above.
