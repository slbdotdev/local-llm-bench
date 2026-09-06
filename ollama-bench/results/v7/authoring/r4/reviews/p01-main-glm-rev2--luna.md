verdict: REVISE
fair: yes — the in-force promise, supersession, record locations, and per-stage sweep semantics are explicit, so a careful solver can derive the report without ambiguity.
checker: sound — selfcheck.py and probe_candidate.py pass the reference, near-miss, unsafe, and whitespace cases, and check_harvest.py reports the declared entries accurately.
harvest: 18/54 by `ran:` — one grep exposes all 18 components' sweep run dates, but it does not finish the report without opening or otherwise processing the per-component records.
declaration: the per-component sweep run date is omitted from harvest_units()
shortcut: 38 files, score 8/8 — the manifest, rationale, and all 18 component pages plus all 18 modules assemble the full report; no smaller seed-only shortcut reached full score.
notes_claims: the claimed traversal of 23202/30369 (76.4%) fails; the current load-bearing check measures 23399/30369 (77.0%)
tiers: Haiku fails at locating the in-force rationale and reconciling each log with its shelf run date | both pass — a careful Sonnet follows the release chain and performs the per-component date comparisons.
hard_to_do: yes — the anti-harvest design makes the task require broad record replay and reconciliation rather than making the facts hard to understand.
fix: add one harvest unit for each component's sweep run date and vary the run-date line's wording so a single `ran:` grep cannot harvest all of them.
