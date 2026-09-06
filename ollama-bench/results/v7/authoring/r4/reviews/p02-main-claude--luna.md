verdict: PASS
fair: yes — the prompt states the exact three-line deliverable and the policy gives an explicit roster, rule, cutoff, and live allowance.
checker: unsound — the required `check_index_leak.py p02-main-claude` run aborted while importing unrelated `p03_main_luna.py` at line 167 with `IndentationError`, so it never checked p02.
harvest: 0/18 by `OPENING_GRANT` — this grep puts all 18 opening grants on screen but no decisive current-reservation values; the answer cannot be finished without opening per-unit records.
declaration: honest — all 18 unit values are per-stage current reservations derived from the grant plus effective adjustments, and the checker found them absent from seed.
shortcut: 2 files, score 5/7 — `docs/reservation-standing.md` plus `docs/policy/reservation-programme.md` yields the stale snapshot set and live RP-4 allowance, so it misses the closing-wave answer.
notes_claims: verified
tiers: Haiku fails at replaying all 18 stage tables and filtering by state/date — a careful Sonnet should not be caught because the policy and scope are explicit.
hard_to_do: yes — the derived values are clear to understand, but computing them requires the broad per-stage traversal.
fix: none
