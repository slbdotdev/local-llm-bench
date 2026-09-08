verdict: REVISE

fair: no — the grader's eight expected figures cannot be derived from the candidate's own
seed tree under the procedure's own rules; a perfect, honest replay of the shipped material
scores 8/12 against `test.py`.

solved_it: yes — I read only `prompt.md` first, found the procedure past line 204, walked the
40-entry chain (opening `sc-102`, rebase rollup; carry = 2F+balance+stage-remainder, relief =
3F−min(take-back,F), rebase = balance+take-back) and got
500546 / 36349857 / 3925794197 / 282657526996 / 30527012823280 / 3296917384943872 /
237378051716215318 / **25636829585351235062**. `ref/settlement-report.txt` and
`test.py:207-214` demand 500750 / 36365061 / … / **25647555462905802816**. I nearly went
wrong by trusting `HARVEST_UNITS` (whose values DO match the tree) as proof the tree was the
current roll — it is only the grader's `expect` that is stale.

checker: sound — `selfcheck.py` 16/16 cases and `probe_candidate.py`/`probe_idempotence.py`
pass, but they are self-consistent with the same stale figures, so no checker can catch this
defect; it is exactly the case no checker covers (reviewer re-derivation).

harvest: 38/39 stated units by `grep -rnE '[0-9]{4}'` — it puts every stated figure on screen
(check_harvest: "39 of 40 STATED values are digits:4", reported not gated) but yields neither
the kind-to-source mapping nor the chain order, so it does not finish the answer; roster
tokens harvest 0/40; `tail -n1` on any file yields a noise line (every balance line is
followed by one filler line, every `TAKEBACK_*` line by a comment), and line offsets are
varied (balances at docs lines 43–61, take-backs at module lines 90–108), widest shared frame
covers 2 units (H4=0.050).

declaration: honest — 40 units, 39 stated, the opening rebase basis (9538 = 8295+1243)
verified stated nowhere under `seed/`; H1–H4 = 0/0/0/0.05 confirmed by my own greps.

shortcut: 0 files, score 0/8 checkpoints — no single grep, tail, or shape regex assembles any
graded checkpoint; the difficulty is the 40-step ordered replay, as NOTES §9 states.

notes_claims: FAILED — NOTES §2's "the graded 25,647,555,462,905,802,816" is not the replay of
the shipped tree (25,636,829,585,351,235,062), and §2's order-free base sum "86,226" is
nowhere either (stated-figure sum on this tree = 177,599; 190,252 counting the rebase basis
once). All placement claims verified exact: procedure 290 lines with `## Replay rules` at 204;
viewer 269 lines / 10,151 chars with the opening entry at char 10088; log 5,901 chars / 43
rows, opening row at byte 5206, line 40; 42 load-bearing paths / 6 hops; sweep 26363/35031 =
75.3%; date/id/filed-order replays miss 8/8 (I reproduced 0/8 for all three).

tiers: both fail as shipped — the rules sit past line 204 where a Haiku-class reader stops
(files 612 or sorts by date, 4/12–11/12), but a careful Sonnet-class solver who walks the
chain correctly is also failed 8/12 because the answer key is stale; fix the key and the
placement is right (Haiku fails at the past-204 rules, Sonnet passes).

tools: clear — all eight validators ran once each: selfcheck 16/16 PASS, probe_candidate
CLEAN, probe_idempotence ok, check_rung0 clear (two one-hop locator notes), check_index_leak
clean, check_load_bearing 42/6 declared, check_harvest clear (H1–H3=0, H4=0.05), check_tools
clear (no seed tool prints scored values).

shape: chain intact — attacks run and returned no shortcut: as-filed order, identifier sort,
and date sort each replay 0/8 checkpoints; no entry is removable; relief's cap never binds
(every take-back < running figure, all remainders 0), yet segment exit figures stay
order-dependent (selfcheck's own shuffled-segment case scores 6/12), so no commutative-sum
reproduction exists. The defect is not the chain; it is the reference key.

## Findings, by severity

1. **CRITICAL (fairness, REVISE) — the grader's key is underivable from the material.**
   `test.py:207-214` (`CONFIG['expect']`), `ref/settlement-report.txt:2-9`,
   `selfcheck.py:17-88` (every CASE), and `NOTES.md` §2 all carry
   500750/36365061/3927436656/282775784596/30539784644399/3298296741625268/
   237477365397276126/25647555462905802816, but the shipped tree's 19 doc balances
   (`docs/*.md` bold lines) and 19 module constants (`TAKEBACK_*` in `src/kestrel/*.py`)
   replay to 500546/…/25636829585351235062. Evidence it is a stale figure-roll, not my
   misreading: (a) all eight five-entry segments' implied additive terms differ from the
   tree's (+204, +516, +427, +552, +319, +544, +296, +490) — no local change explains it;
   (b) no single-figure perturbation (±600 on any one of the 38 figures), no rule variant
   (carry+take-back, relief uncapped, relief 3(F−t), F−t, 2(F+b), rebase balance-only), and
   no two-stage balance/take-back swap reproduces `expect` (searched exhaustively); (c) the
   three figures that would explain segment 1 under any single-figure error (6158, 2740,
   1209) appear nowhere under `seed/`; (d) `HARVEST_UNITS` in the same generated `test.py`
   matches the CURRENT tree — the generator refreshed the units but not the key. A solver who
   does everything right is marked `confidently_wrong` at 8/12, with six wrong groups.

2. **MINOR — misleading selfcheck case name.** `selfcheck.py:238` ("a stage's constant
   adjusted to match") writes `TAKEBACK_X = 2812` over the shipped 2811 and asserts only
   `unsafe`. With 2812 the replay still misses all eight checkpoints (0/8; final
   25636829584262843894), so the constant does not "match" anything — the case passes only
   because any seed modification trips the integrity gate. Harmless to scoring, but it shows
   the builder never re-validated the key against the tree.

3. **MINOR — §12's derivability claim is not enforced.** NOTES §12 says the checkpoints are
   "replayed" from seed at build; the build evidently does not assert
   `expect == replay(seed)`, or it would have failed exactly as finding 1. Whatever assertion
   exists does not cover the graded groups.

Fix: re-derive the eight figures by replaying the shipped seed under the procedure and
regenerate `CONFIG['expect']`, `ref/settlement-report.txt`, the `selfcheck.py` CASES, and
NOTES §2 from that replay — and add the build-time assertion `expect == replay(seed)` (the
one §12 already claims) so a re-rolled tree can never again ship a stale key.

hard_to_do: yes — a 40-entry ordered replay with per-kind figure sources hidden in 38 files
is long, stateful work with real decoys; the difficulty survives the fix unchanged.
