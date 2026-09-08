verdict: PASS

fair: yes — I re-derived all eight figures from the handbook text alone, blind to ref/, and they match ref/ and the grader key exactly.

solved_it: yes — chain from the log (start sc-102 rebase rollup, the only sealed empty-previous row; sc-100 is void bait; 40 sealed entries = 43 rows − 3 voids), figures from each stage's page balance and module take-back, replay by `2F+balance`, `3F−min(tb,F)`, rebase sets basis; I nearly went wrong twice: mis-parsed the CSV as previous,entry on the first walk, and hand-arithmetic drifted after entry 10 — coding the documented-rule replay settled it (final 25636829585351235062, all eight checkpoints matching).

checker: sound — selfcheck.py runs 16 cases (reference 12/12, five wrong courses confidently_wrong at 4/12, 11/12, 3/12, 6/12, two unsafe, five whitespace perturbations all correct), and my own wrong-course replays reproduce the case finals: date order 35017725787245410, swapped sources 16185894609636907366 (carry←module, relief←page).

harvest: 19/38 stated figure lines by a last-non-blank-line sweep (see findings) — but no grep finishes the answer: no sweep or label yields the kinds, the chain order, the 19 take-backs in context, or the derived rebase basis 9538; best top-anchored fixed-line sweep = 1 of 38; raw `tail -n1` = 0 (blank padding); best single word-level label = 3 of 38 figure lines (checker's own worst giveaway token 'turn' = 5–6/40 units, two-token union 8/40, P2=0.200, all under threshold).

declaration: honest — HARVEST_UNITS is 40 units over 40 entries, 39 stated + 1 derived (sc-102's 9538 occurs nowhere under seed/, verified by bounded scan); check_harvest reports exactly that (39 distinct values, 1 derived, 0 indistinct).

shortcut: 2 files (log + handbook) for the rules and order, but zero files shortcut the figures — running figures occur nowhere under seed/ (verified), and no non-handbook file carries two stage figures (verified), so 19 page/module pairs must still be read and reconciled.

notes_claims: verified — 293-line procedure with `## Replay rules` at line 204 and all three formula phrases below it (239/242/293); viewer 269 lines/10,151 chars with the opening entry at char 10088; log 5,901 chars/43 rows, opening row line 40/char 5206; order-free base sum 86,226 = (Σcarry balances 128,701 − Σrelief take-backs 52,013) + rebase basis 9,538; 42 load-bearing paths over 6 hops; sweep 25,402/34,073 = 74.6%; the three rewritten measurement claims (widest non-stop token 3 of 19 stages, widest shared frame ≤2 of 38, all 38 top offsets and 38 EOF distances distinct) all reproduce.

tiers: Haiku fails at the chain start — entry one is a rebase whose basis is page balance + module take-back across two files, reachable only after excluding the void sc-100 bait and refusing the date/id sorts; every trap is a rule stated past line 204, so a careful Sonnet-class reader is caught by the same steps only if careless — not unfair, not saturated.

tools: clear — check_tools: no seed tool prints scored or per-unit values; the viewer prints the log as filed and resolves only the opening entry, no figures.

shape: chain intact — 0 hits from 14 single-field sorts ×2 directions, position-mod-k regrouping k=2..12, and all 1,521 affine row-index maps (a·i+b mod 40); 0 nontrivial hits from 780 contiguous-segment shuffled replays (segments ≤7 fully permuted, longer 5,000 random shuffles each); per-entry perturbation of any of entries 1–3 moves every checkpoint; the carry/relief pairs per shuffled stage admit no arithmetic continuation.

hard_to_do: yes — even with every figure harvested, a solver must still exclude voids, walk 40 previous-links, map kind→source per stage, carry state through 40 non-commuting transforms, and derive the one unstated basis; the difficulty is the ordered replay, not lookup.

fix: none required; two cosmetic notes below.

## Findings, by severity

1. MINOR (frame pattern survives in padded form). All 19 docs-side balance lines are the last non-blank line of their files (e.g. `seed/docs/rollup.md:45`, `seed/docs/schema.md:39`, `seed/docs/audit.md:41`); the "varied EOF distances" (2–20 raw lines, all distinct) are blank-line padding only. Raw `tail -n1` harvests nothing (it returns blanks), so NOTES.md:88-95's literal claims hold and the r6c fix's letter is met — but a workhorse that strips blanks harvests 19 of 38 stated figure lines, half the stated values, with stage labels attached. It does not finish the answer: no take-backs (those have 22–40 real trailing comment lines in src), no kind→source mapping, no chain order, no rebase basis. Concrete change if ever touched again: one short real content line after each balance line, as the src side already has.

2. COSMETIC (mislabeled selfcheck case). `selfcheck.py:48` "wrong: void rows applied with the sealed ones" (final 210106354686471446) is actually the date-order-with-voids compound; chain-order-with-voids lands elsewhere (153793143279119597558, or 10575 if the void rebase is applied last). Either is confidently_wrong 4/12, and NOTES §5 quotes no figure for this course, so nothing drifts — the label is just narrower than the number.

3. COSMETIC (token measure granularity). NOTES.md:90's "widest non-stop token reaches 3 of 19 stages" is word-level and reproduces (share/credits/escrowed/tallies/parcels/quota each on 3 figure lines); at substring level `share` reaches 5 of 38 (plural `shares` on ledger/routing). Still a handful, still order-blind; no action needed.

## What I checked

Blind re-derivation of chain and figures from handbook text alone (prompt → NOTES → seed → handbook → log, ref/ read only after my answer was fixed); reproduction of every wrong-course final in selfcheck from the on-disk log; order attacks (field sorts, mod-k, affine, identity-excluded segment shuffles); arithmetic attacks (per-entry perturbation propagation, remainder semantics — every relief has F > take-back, all remainders 0, as claimed); frame/harvest battery (tail sweeps, fixed-line sweeps top and bottom, word- and substring-level label sweeps, shape regexes); every checkable numeric claim in NOTES.md; all eight validators from the method run once each (selfcheck, probe_candidate, probe_idempotence, check_rung0, check_index_leak, check_load_bearing, check_harvest --verbose, check_tools --verbose) — all pass, H1=0.125 H2=0.000 H3=0.150 H4=0.050 against thresholds 0.250/0.400/0.333. No git, no reviews/ or r5/reviews or r6 content read besides writing my report, nothing outside the candidate touched, nothing committed.

## What remains uncertain

The build-time assertions NOTES attributes to `facts()`/`_assert_documented_rule()` live in the generator, not the tree; I verified every underlying fact by hand instead, and my documented-rule replay reproducing the key is the substantive derivability check. The sweep denominator 34,073 material tokens is the checker's own measure (check_load_bearing prints 74.6%, agreeing with NOTES); I did not recount it independently.

Report file for the record: `ollama-bench/results/v7/authoring/r6/review-q09-glm-r6d.md`.