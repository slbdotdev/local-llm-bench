# DeepSeek V4.1 Flash preview — single pass, 2026-09-09

Provenance for `deepseek-v41-preview-2026-09-09.{json,md}`. Read this before
comparing these rows with any campaign cell.

## What ran

| field | value |
| --- | --- |
| model id | `deepseek-v4.1-flash-expires-on-0910` (unlisted preview; the short alias `deepseek-v4.1-flash` returns HTTP 400) |
| provider | DeepSeek first-party API, OpenAI-compatible, `https://api.deepseek.com/v1` |
| suite | `results/v5/authoring/round3/suite` — 8 slots, g01-g04 and t01-t04 |
| trials | 1 per task |
| thinking | medium |
| context | 65536 |
| `pi` version | **0.85.1** — this is what `pibench.py` invokes as a subprocess |
| `pi-slb` version | **0.2.9** — the supervisor layer; `pibench.py` does not call it |
| date | 2026-09-09 |

Both version strings are recorded because the request named "pi 0.2.9" and the
two layers carry different numbers. Neither is corrected here; both are stated.

## Result

8/8 PASS, every score 1.00, every verdict `correct`. Cost $0.13, measured as a
balance delta ($1.62 to $1.49), not estimated from token counts.

A clean sweep is the expected result on this suite and is **not** evidence about
the model. The v5-era suite does not discriminate reliably even between small
local models, which is the reason the v7 campaign exists. The throughput column
is the deliverable here; the pass column is not.

## Three deviations from the campaign's standard cell

**1. The pi resilience extension was not loaded.** `results/v7/calibration-2026-09-06.md`
records it as mandatory on every campaign cell. It lives on a Windows path and
was not carried into this WSL run. Consequence: no retries, no empty-turn nudges,
no tool-output truncation, no supervisor session resume. **These rows are
therefore not methodologically comparable to v5 or v7 campaign cells**, and
`g02`'s 867 s wall is unexplained under that caveat — an unretried stall is a
live possibility and has not been ruled out.

**2. The suite path is `results/v5/authoring/round3/suite`, not `tasks-v5`.**
`tasks-v5/<slot>/` holds only `cand-1`..`cand-5` subdirectories and no
slot-level `prompt.md`, so `load_tasks` (`pibench.py:118`) raises before any
request is made. `round3/suite` is the committed loadable assembly of the same
eight slots; `prompt.md` and `test.py` were diffed byte-identical against
`tasks-v5/<slot>/cand-5`, the 64k cell matching this run's configuration. Same
material, different path — not a change of suite.

**3. `settings.json` carried two WSL edits**: `shellPath` to `/bin/bash`, and
`enabledModels: ["ollama/*"]` omitted, which would otherwise have excluded the
provider. The agent directory lived at `/tmp/pi-agent-deepseek/` (0600) and its
`apiKey` was an environment reference, so no credential reached disk or output.

## Reading `effective_gen_tps`

The new per-run field is `out_tokens / wall_s`. Wall includes tool execution,
grading, and network round-trips, so it is **effective end-to-end throughput and
not decode throughput**. It must never be compared with the ollama `gen_tps`
column, which is pure decode derived from `eval_duration`, nor with vendor
decode figures. The distinct name is deliberate.

`g02` demonstrates the trap: 24.5 eff tok/s against a 197-305 spread, caused by
38 turns and 52 tool calls inside the wall clock, not by slow generation.

## Known gap

The split between cache-hit and cache-miss input tokens was not captured.
DeepSeek returns `prompt_cache_hit_tokens` and `prompt_cache_miss_tokens` on
every response and `pibench.py` records neither, so the pass's cost cannot be
attributed between the two rates. The gap between the flat-rate computation
(~$0.35 over 5.11 M input tokens) and the charged $0.13 implies substantial
cache hits, but that is **inferred from the balance delta, not measured**.
Recording the two fields alongside `in_tokens` would settle it.

## Expiry

The preview id expires 2026-09-10. It did not expire mid-run. After that date
these rows are not reproducible against the same model.
