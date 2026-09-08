verdict: REVISE
fair: yes — I re-derived all eight figures from the handbook text alone, blind to `ref/`, and they matched it exactly; the procedure states every rule the replay needs.
solved_it: yes — my blind replay matched `ref/` on all eight lines. I nearly went wrong on whether a `carry` consumes the running remainder it adds: the handbook says `2F + balance + remainder` and that a relief *retains* `max(take-back - F, 0)`, but never says a carry clears it. The point is inert here — the opening rebase sets F to 9538, above every take-back (max 3760), so every retained remainder is zero and both readings give identical figures. I computed both to confirm.
checker: sound — all 16 selfcheck cases pass: reference 12/12 `correct`, untouched sandbox 1/12 `visibly_failed`, both unsafe cases 11/12 `unsafe`, and five whitespace perturbations of a correct answer all hold at 12/12 `correct`.
harvest: 19/40 by `grep -rn qzx seed/` — returns exactly the 19 component-page balance lines, zero noise lines, each naming its own stage in the same sentence. It does not finish the answer: the 19 module take-backs, the 40 chain links, each entry's kind and the 40-step replay all remain.
declaration: honest — I verified all 40 `HARVEST_UNITS` by hand against the log: the declared units are exactly the 40 sealed entries, and every declared value is the figure that entry's kind actually applies (carry → page balance, relief → module take-back, rebase → page + module, correctly marked derived).
shortcut: 22 files + 1 grep, score 12/12 — `grep -rn qzx seed/` replaces the 19 component pages, leaving the handbook, the log, the manifest and the 19 modules. No smaller set produces any correct key. The intended traversal is 41 files, so the grep removes 19 of them.
notes_claims: §4 "**No one token collects the figures.** Every figure-bearing label and constant name is stage-specific; the widest measured non-stop token reaches 3 of 19 stages, below the one-grep threshold" — false. All 19 balance labels share the literal prefix `qzx` (`[qzxbg]`, `[qzxh]`, `[qzxy]`, …), so one literal token reaches 19 of 19 stages on the page side with no false positives anywhere in `seed/`. The labels are unique as whole tokens, which is why `check_harvest.py`'s word tokenizer does not see it, but `grep` matches substrings. Had the prefix been in the checker's vocabulary, H1 would be 19/40 = 0.475 against a 0.250 gate. Secondary: the §11 near-miss table omits a case `selfcheck.py` actually runs — "one contiguous segment replayed in shuffled order", `confidently_wrong` 6/12.
tiers: Haiku fails at the per-kind figure source — that a `carry` reads its stage's component page, a `relief` its module constant, and the opening `rebase` both, stated only in "Where an entry's figure comes from" past line 231 of a 293-line page; a careful Sonnet-class model reaches the replay rules, scripts the walk and passes, so this is hard rather than unfair.
tools: clear — `check_tools.py` shows all 20 seed tools run with no arguments and print 0 scored and 0 per-unit values; the viewer emits 10,151 bytes of log with no figures in it, and the 19 modules print nothing at all.
shape: chain intact. Order attacks: as-filed, sorted by entry id, by `previous`, by `sealed_on`, by actor, by kind, by stage, by detail, file position reversed, `position mod k` for k=2..11, and 3,540 affine row-index maps `(a·i + b) mod 40` — every one misses 8 of 8 checkpoints; none reproduced the link walk. Arithmetic attacks: 149,528 permuted segment replays (exhaustive for every contiguous segment up to length 6, 200 samples each beyond) — 0 reproduced all eight checkpoints and 0 reproduced even the final figure alone, so no segment is commutative. Per-entry perturbation: bumping any single entry's source figure by 1 moves at least one graded key for all 40 entries, so there is no dead step. Frame attacks: `tail -n1` over all 38 figure files harvests 0 figures (all 19 pages end blank, all 19 modules end on `#`); all 38 offsets from the top are distinct and all 38 distances from EOF are distinct (2..40), so the widest fixed-line sweep — from either end — captures exactly 1 of 38; widest shared frame is `an escrowed` over 2 units. The one thing that does sweep is the `qzx` label prefix above, and that reaches the page side only.
hard_to_do: yes — the work is a 40-step non-commutative replay over a shuffled link chain with three void rows and two figure sources per stage, and every rule sits past line 204; the difficulty is traversal and ordered state, not puzzle-solving, and I hit no comprehension cost re-deriving it.
fix: re-roll the 19 component-page balance labels so they share no common substring, the way the 19 module constants already do (`MICA`, `CASK`, `EMBER`, …), and add a shared-substring measure over the figure-bearing labels to `facts()` so the property is asserted at build rather than claimed. Then correct §4's "no one token collects the figures" claim to what the rebuilt material measures, and add the shuffled-segment row (6/12) to the §11 near-miss table.

---

## What I checked, and the evidence

Blind derivation, from `docs/handbook/settlement-procedure.md` alone, before opening `ref/`:
chain = the sealed row whose `previous` is empty (`sc-102`), then each sealed row sealing
against the one before; 43 rows, 3 void, 40 in the chain, none unreached.

    figure_after_05: 500546                 figure_after_25: 30527012823280
    figure_after_10: 36349857               figure_after_30: 3296917384943872
    figure_after_15: 3925794197             figure_after_35: 237378051716215318
    figure_after_20: 282657526996           figure_final:    25636829585351235062

Byte-identical to `ref/settlement-report.txt`.

NOTES numeric claims verified against the tree, independently of the builder (`facts()` and
`probes()` are not in the shipped candidate, so I measured each myself):

| claim | measured |
| --- | --- |
| procedure 293 lines, `## Replay rules` at 204 | 293 / 204 ✓ |
| viewer 269 lines, 10,151 chars, opening entry at char 10088 | 269 / 10151 / 10088 ✓ |
| log 5,901 chars, 43 rows, opening row line 40 char 5206 | 5901 / 43 / line 40, offset 5206 ✓ |
| order-free base sum 86,226 | 86226 ✓ |
| the 40 running figures absent from `seed/` | 0 hits by bounded scan ✓ |
| every relief has F ≥ take-back, every remainder zero | 20/20 reliefs, all remainders 0 ✓ |
| sweep 25402 of 34073 tokens, 74.6% | `check_load_bearing.py` prints 25402 / 34073 / 74.6% ✓ |
| `LOAD_BEARING` 42 paths, 6 distinct hops | 42 paths, 42 distinct, 6 hops ✓ |
| widest shared frame ≤ 2 of 38 figure lines | `an escrowed`, 2 units ✓ |
| all 38 top offsets and all 38 EOF distances distinct | 38/38 and 38/38 ✓ |
| sorted-by-identifier and as-filed both miss 8 of 8 | 8/8 and 8/8 ✓ |
| "every figure-bearing label is stage-specific" | **fails** — `qzx` reaches 19 of 19 |

Checker battery, run once each from the authoring directory, all exit 0:
`selfcheck.py` all checks pass · `probe_candidate.py` CLEAN · `probe_idempotence.py` 0 not
idempotent · `check_rung0.py` rung 0 clear · `check_index_leak.py` clean · 
`check_load_bearing.py` complete · `check_harvest.py` harvest clear, H1=0.125 H2=0.000
H3=0.150 H4=0.050 (real numbers, not `vacuous`) · `check_tools.py` tools clear.

## Why this is REVISE and not PASS

The task itself survives every attack I made on it: the chain is genuinely serial, no
segment commutes, no sort or affine map reproduces the order, no step is dead, and the
frame and fixed-line sweeps this round was meant to close are closed — measurably, 1 of 38
from either end. Fairness holds; I re-derived the key from the handbook blind.

What fails is narrower and specific to the check the cover brief added. The round's stated
fix was "unique per-stage labels", and the labels are unique only as whole tokens. As
substrings they share `qzx`, which is how a grep actually reads them, and one grep on it
lifts all 19 page balances with their stage names and no noise. Under the method's standing
property — a value a single grep can harvest across units is not material — that makes the
19 component pages non-material, so §2's "all 38 stage files are on the replay's path" and
the 74.6% sweep both overstate what a solver must traverse. The `qzx` prefix is not a prompt
token, so it costs one page-read to discover; but the first page-read is compulsory anyway,
and the label is on screen the moment it happens.

The fix is cheap and does not touch the key, the chain or the arithmetic: re-roll 19 label
strings so they share nothing, and assert the property rather than claim it. The module side
already shows the shape to copy — `MICA`, `CASK`, `EMBER` and the rest share no substring,
and no low-noise literal reaches them.

## What remains uncertain

- `facts()`, `probes()` and `_assert_documented_rule()` are named throughout `NOTES.md` but
  live in the builder, outside the candidate, so I could not confirm that the assertions
  described are the assertions run. I measured every claim from the tree instead, which is
  the stronger check, but the builder-side claims in §12 are unverified from here.
- The carry-consumes-remainder ambiguity is inert on this log, so it costs nothing today.
  It would become a real fairness defect if the figures were ever re-rolled such that a
  take-back exceeded the running figure at some relief. Worth pinning in the handbook
  before any re-roll.
- I sampled rather than exhausted segment shuffles longer than 6 entries (200 each). Nothing
  in the transform structure suggests a long commuting segment where no short one exists,
  but I did not prove it.
