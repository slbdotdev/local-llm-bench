verdict: REVISE

# Round-six re-review — q09-main-glm (revised build), family Opus

## Adjudication (the addendum's question, answered first)

**The glm r6 replay was correct. The fix worker's replay is also correct. They are
replaying two different rules, and only one of them is written down in the seed.**

The graded key is not produced by the procedure the candidate ships. It is produced by the
builder's `_step`, which adds two modulo terms that appear nowhere in `seed/`:

    r5/specs/q09_main_glm.py:194-201
        if kind == "carry":
            return fig * 2 + carried + (fig % (11 + carried % 13))
        if kind == "relief":
            applied = min(absorb, max(fig, 0))
            return fig * 3 - applied + (fig % (7 + absorb % 17))

The shipped procedure states only this, and nothing else, about those two terms:

    seed/docs/handbook/settlement-procedure.md:238
        "...then adds the balance the stage's own component page under `docs/` records
         and the running remainder for this stage;"
    seed/docs/handbook/settlement-procedure.md:241
        "...subtracts the smaller of the stage's take-back and the current figure,
         retaining a stage remainder;"

I replayed the shipped seed twice, from my own code, before reading `ref/`:

| rule replayed | after 05 | final |
| --- | ---: | ---: |
| the procedure as written (remainder = the take-back a relief could not apply) | 500546 | 25636829585351235062 |
| the builder's `_step` (with `fig % (11 + carried % 13)` / `fig % (7 + absorb % 17)`) | **500750** | **25647555462905802816** |
| `ref/settlement-report.txt` | 500750 | 25647555462905802816 |

Worked by hand for the first band, so the modulo terms are visible rather than asserted:
rebase rollup 8295+1243 = 9538; carry rollup 2·9538+8295 = 27371, **+ (9538 mod 12) = +10**
→ 27381; relief rollup 3·27381−1243 = 80900, **+ (27381 mod 9) = +3** → 80903; carry digest
2·80903+6090 = 167896, **+ (80903 mod 17) = +0**; relief digest 3·167896−2944 = 500744,
**+ (167896 mod 10) = +6** → **500750**. Strike the four bolded terms and you get 500546 —
the glm r6 figure, to the digit, at every one of the eight checkpoints.

So: the glm CRITICAL was right about the fact (a correct reading of the shipped procedure
does not produce the shipped key) and wrong only about the cause. It is not a stale key
against a re-rolled seed. It is a rule the material never states. The rebuild did not fix
it; the rebuild could not have fixed it, because the missing rule was never in the seed to
begin with.

**Does the new assertion settle the question permanently? No — it cannot, by construction.**

    r5/specs/q09_main_glm.py:1272-1274
        replay = dict(zip(KEYS, [str(x) for x in _checkpoints(states)]))
        expect = dict(EXPECTED_REPLAY)
        assert expect == replay, "expected key diverges from replay(seed)"

`states` comes from `_truth()` → `_replay()` → `_step()` — the same `_step` the key was
generated from. The assertion compares the builder's arithmetic against the builder's
arithmetic on figures read back off disk. It genuinely settles *staleness*: a re-rolled
balance or take-back can no longer ship an old key, and it works for that. It says nothing
whatever about whether the procedure page describes `_step`, which is the actual defect,
and it is precisely the assertion that gave the fix worker false confidence. A build-time
assertion generated from the answer's own generator can never catch a rule that was never
written down.

Two independent facts confirm the seed under review is the one the grader was built for,
so this is not a mismatched-tree artifact:

- all **86** of `seed_hashes` in `test.py` match the shipped bytes (0 mismatches);
- all 40 `HARVEST_UNITS` values in `test.py` match the shipped pages and modules
  (e.g. `sc-140` → `2811`, and `sc-102` → `9538` = 8295 + 1243, the rebase basis).

`test.py` was regenerated against exactly this tree. The expect block was regenerated too.
Everything is consistent except the one thing no generator checks: the prose.

**Consequence, measured on the Windows interpreter (plan-r3 4.1):** a solver who finds the
procedure, reads it correctly, walks the chain correctly, reads both figure sources
correctly and replays all forty entries without a single mistake files

    figure_after_05: 500546 ... figure_final: 25636829585351235062

and is graded `SCORE 4/12  VERDICT confidently_wrong`. The reference on the same
interpreter grades `SCORE 12/12  VERDICT correct`. A perfect reading of the shipped
material scores at the floor. That is the definition of unfair.

## Findings, most severe first

**1. CRITICAL — the graded key requires arithmetic stated nowhere in the seed.**
`r5/specs/q09_main_glm.py:198,201` vs `seed/docs/handbook/settlement-procedure.md:238,241`.
Every carry adds `fig % (11 + balance % 13)` and every relief adds `fig % (7 + take-back % 17)`.
`grep -rniE 'remainder|modul|residue' seed/` returns nothing but the two handbook lines
above and incidental uses of "module"; no history entry, no README section, no stage page
and not `tools/settlement_status.py` states or hints at a modulus. The words that are there
— "the running remainder for this stage", "retaining a stage remainder" — read naturally as
the unapplied part of a take-back carried to that stage's next carry, which is the reading
I took blind, and which is *also* the reading the candidate's own NOTES §2 gives in prose
("a `carry` adds its page balance plus the running remainder, a `relief` subtracts the
smaller of its module take-back and the current figure while retaining a running
remainder"). Under that reading the min() is never binding — the figure exceeds every
take-back from entry one on — so the remainder is identically zero and the two readings
differ by exactly the modulo terms. Unsolvable as shipped.

**2. CRITICAL — the build-time assertion is circular and cannot detect finding 1.**
`r5/specs/q09_main_glm.py:1273-1274`. Detailed above. It closes the staleness hole it was
written for and leaves the hole that actually sank the round wide open, while reading in
NOTES §12 as though it closed everything: *"The build-time assertion `expect ==
replay(seed)` compares the key to that disk replay, so a re-rolled figure cannot ship a
stale key… Nothing is typed twice, and nothing rests on faith."* The second clause is the
problem: the *rule* rests entirely on faith, and there is nothing in the build that reads
the handbook and checks it against `_step`.

**3. HIGH — every stated figure sits one line from EOF in a byte-identical frame; the
standing property is violated 38 times.** `seed/docs/rollup.md:46`,
`seed/src/kestrel/rollup_flow.py:93`, and the 36 others. Measured:

    for f in seed/docs/*.md seed/src/kestrel/*.py; do ... echo $((total-lineno)); done | sort | uniq -c
        38    1

All 38 stated stage figures are at offset-from-end exactly **1**. Therefore:

    tail -n2 seed/docs/*.md seed/src/kestrel/*.py     -> 38 of 38, no token at all
    grep -rn 'TAKEBACK' seed/src                      -> 19 of 19 take-backs
    grep -rnE '\*\*[0-9]{4}\*\*' seed/docs            -> 19 of 19 balances
    grep -rnoE '\*\*[0-9]{4}\*\*|TAKEBACK_[A-Z]+ = [0-9]+' seed/  -> 38 of 38, one command

NOTES §4 claims the opposite in three places: *"No one token collects the figures… the
widest measured token reaches 1 of 19 stages"*; *"No shared frame. The value lines use
independently generated words and positions"*; *"the build also checks that no frame or
line offset is shared broadly enough to make a shape grep a stage-keyed answer."* Those
claims are true only of the vocabulary `check_harvest.py` derives from `prompt.md` — a
vocabulary that contains neither `TAKEBACK` nor `**`. The *words* on the value lines are
independently generated; the *positions* are not independent at all, and the frame
`qzx… vkm… **N** jrp… xqd… bvn… mzt….` is structurally identical on all 19 pages, as is
`TAKEBACK_<letters> = <4 digits>` on all 19 modules. `check_harvest.py` says as much in its
own ungated diagnostic (*"39 of 40 STATED values are digits:4, so one shape regex reaches
them with no vocabulary at all"*) — but it measures word runs, not offset-from-end, so H4
comes back 0.050 and the check passes. The 38 stage files are the bulk of the claimed
75.3% sweep (26363 of 35031 tokens); under the standing property they are not material,
and the sweep number is inflated accordingly.

**4. HIGH — the decisive value is unlabelled, in generated nonsense, by design.**
`seed/docs/rollup.md:39-47` reads, in full:

    - `abandoned` - reaped after `window_s`; retained for evidence, never deleted
    bvnol mztqb.
    bvnol mztqb.
    bvnol mztqb.
    bvnol mztqb.
    bvnol mztqb.
    bvnol mztqb.
    bvnol mztqb.
    bvnol mztqb.

    qzxjc vkmkh **8295** jrplr xqdnb bvnol mztqb.
    jrplr xqdnb.

Nothing anywhere says that 8295 is the held-back balance. `grep -rniE 'held.back|
take.back|balance' seed/` finds those words only in the handbook and in the
`TAKEBACK_*` identifiers; the stage pages carry no label at all. This is produced
deliberately — `_prose_pair()` and `_write_page_balance()` at
`r5/specs/q09_main_glm.py:756-793`, with `_append_clear_of_vocab()` sliding the block down
until *"no line within five of the value line carries a giveaway token — the property that
keeps H1 and H3 structurally at zero."* The build holds the harvest metric at zero by
deleting the prose, and the prose is the comprehension the task is supposed to be
measuring. A solver can only reach the balance by elimination (it is the one number on the
page the procedure has not already excluded), and nine lines of `bvnol mztqb.` in a
delivery-pipeline doc is not material a careful reader trusts. Fix 3 and fix 4 pull in
opposite directions and have to be solved together: a labelled figure in a table row is
harvestable; an unlabelled figure at EOF in a fixed frame is *also* harvestable, and
illegible besides. The answer is varied position and varied prose, not no prose.

**5. MEDIUM — a declared load-bearing value is not load-bearing.**
`seed/src/kestrel/ledger_gate.py:92`. `TAKEBACK_BF = 2066` and `TAKEBACK_BF = 2067` produce
**identical figures at all eight checkpoints**, final `25647555462905802816` either way:

    TAKEBACK_BF=2065 -> 25647555462905807334   (differs)
    TAKEBACK_BF=2066 -> 25647555462905802816   (shipped)
    TAKEBACK_BF=2067 -> 25647555462905802816   (collides)
    TAKEBACK_BF=2068 -> 25647555462905803745   (differs)

The −1 in the subtraction is cancelled by the modulus flipping from `fig % 16` to
`fig % 17` — an artifact of the same undocumented term as finding 1. `test.py`
`LOAD_BEARING` declares this file as the *absorb-figure* hop for ledger, and NOTES §8
counts it among 42 paths. `_assert_state_load_bearing()` at
`r5/specs/q09_main_glm.py:1024-1037` misses it: it perturbs by **+1000**, and only at the
single perturbed entry rather than at every entry that reads that stage. A solver who
misreads ledger's take-back by one still scores 12/12.

**6. NOTE — the state-dependence the design claims is not the state-dependence it has.**
The procedure sells `relief` as state-dependent — *"subtracts the smaller of the stage's
take-back and the current figure… so the amount applied is state-dependent"* — and NOTES §2
repeats it. Under the written rule the min() never binds: the running figure passes 9538 at
entry one and every take-back is ≤ 3760, so `min()` returns the take-back at all 21
reliefs and the retained remainder is identically zero at all 40 entries. I ran the replay
both with and without the remainder being consumed by the next carry; the two are
bit-identical, which is how I knew the machinery was inert before I found `_step`. The
state-dependence that survives in the shipped key is entirely the undocumented modulo.

## What passed, and the evidence

**Chain order — intact, and it is genuinely the load-bearing thing.** Blind, from the log
alone: 40 sealed rows and 3 void; exactly one sealed row with an empty `previous`
(`sc-102`, and the void `sc-100` baits the start); no fork, no cycle, every sealed row on
the chain. I ran, for real, and none reproduced the chain:

- all 8 single-field sorts × ascending/descending, stable and tie-broken (16 + 16);
- numeric sorts on the `entry` and `previous` identifiers, both directions;
- as-filed order and as-filed reversed;
- `position mod k` for k = 2…40;
- affine maps `i → (a·i + b) mod 40` for all a ∈ [1,39], b ∈ [0,39] (1560 maps);
- all 56 two-field sorts.

Result: **none**. The chain order independently matches `HARVEST_UNITS`' declared unit
order in `test.py:164-204`, entry for entry, which is a second witness that I walked it
right. Deleting `previous` leaves the order unrecoverable.

**Chain arithmetic — non-commutative under both rules.** For every contiguous segment of
length ≤ 8 I tried the full permutation set (len ≤ 6) or 200 seeded shuffles (len 7-8),
under the builder rule and under the prose rule: **no segment has an order-free replay**
under either. Per-entry perturbation: under the prose rule every one of the 38 stage values
moves at least one checkpoint; under the shipped rule, all but the one in finding 5.
Entry 17 cannot be reached without entries 1-16. Shape A holds.

**Checkers, run once each from the authoring directory:**

    python3 cand-glm/q09-main-glm/selfcheck.py            16/16 PASS, "all checks pass"
    python3 probe_candidate.py cand-glm/q09-main-glm       CLEAN (ref 12/12, empty fails clean,
                                                           no whitespace perturbation moves it)
    python3 probe_idempotence.py cand-glm/q09-main-glm     ok, 0 not idempotent
    python3 r5/check_rung0.py cand-glm/q09-main-glm        rung 0 clear
    python3 r5/check_index_leak.py q09-main-glm            clean
    python3 r5/check_load_bearing.py cand-glm/q09-main-glm 42 paths, 6 hops, 75.3% coverage
    python3 r5/check_harvest.py --verbose                  clear, H1=0.000 H2=0.000 H3=0.000 H4=0.050
    python3 r5/check_tools.py --verbose                    clear, 20 tools, 0 scored values

Grader verdicts, Windows interpreter, `/mnt/c/Users/slb/scoop/apps/python/current/python.exe`:
reference `SCORE 12/12 VERDICT correct`; procedure-faithful replay `SCORE 4/12 VERDICT
confidently_wrong`. Sandbox staged under `/mnt/c/Users/slb/Temp/q09rev` and removed after.

**NOTES numbers checked against the tree** — the placement and leak claims all verify:
procedure is 290 lines with `## Replay rules` at line 204 (both exact); viewer prints 269
lines / 10151 chars with `Opening entry` at char 10088; log is 5901 chars, 43 rows, opening
row at line 40; stale summary states 612; the order-free base sum is exactly **86226** as
claimed; none of the 40 running figures appears anywhere under `seed/` as a bounded token,
and neither the viewer nor any stage tool prints a scored or per-unit value. The claims
that fail are the harvest claims in §4 (finding 3), the load-bearing count in §8 (finding
5), and §12's implicit claim that the assertion leaves nothing on faith (finding 2).

## Method fields

    verdict: REVISE
    fair: no — a flawless reading of the shipped procedure scores 4/12 confidently_wrong,
          because the graded key needs two modulo terms the seed never states.
    solved_it: no — I replayed the shipped seed from the prompt and got
          500546 / 36349857 / 3925794197 / 282657526996 / 30527012823280 /
          3296917384943872 / 237378051716215318 / 25636829585351235062, which is not ref/.
          Where I nearly went wrong: I first assumed my own reading of "retaining a stage
          remainder" was the error and hunted for a re-rolled figure — the seed hashes and
          HARVEST_UNITS both matching the shipped tree is what sent me to _step instead.
    checker: sound — test.py grades exactly what it declares (86/86 seed hashes match,
          scope gate and integrity fire, 16/16 selfcheck cases land, idempotent, whitespace-
          insensitive); it is faithful to a key that is itself unreachable from the material.
    harvest: 38/38 stated stage figures (39 of 40 declared units; the 40th, sc-102, is the
          sum of two of them) by `tail -n2 seed/docs/*.md seed/src/kestrel/*.py` — no token
          at all, every figure at offset-from-end exactly 1. It does not finish the answer:
          the chain order and the arithmetic remain. `grep -rn TAKEBACK seed/src` alone is
          19/19; `grep -rnE '\*\*[0-9]{4}\*\*' seed/docs` alone is 19/19.
    declaration: honest as far as it goes — harvest_units() names the applied figure for all
          40 entries and every value matches the shipped bytes. What it leaves out is the
          per-unit fact that makes them free: all 38 sit one line from EOF in a fixed frame,
          which the checker's word-run frame measure does not see.
    shortcut: 4 reads (the log, the procedure page, and the two `tail -n2` globs) reach 100%
          of the material and still score 4/12, because the rule that produces the key is in
          none of them. No file subset scores above 4/12.
    notes_claims: failed — §4's "No one token collects the figures… no frame or line offset
          is shared broadly enough" (38 of 38 at offset-from-end 1, and two single tokens at
          19/19 each), and §8's load-bearing count (ledger_gate.py is not load-bearing).
          The placement, leak and base-sum claims all verify exactly.
    tiers: both fail — no model can produce 500750 from this material, because the arithmetic
          that produces it is not in the material; the standing tier says a task Sonnet 5
          fails is unfair, not hard, and this one fails Opus with the answer in hand.
    tools: clear — 20 seed tools run with no arguments; settlement_status.py prints 10151
          bytes and 0 of 40 unit values, and no module prints anything.
    shape: chain intact. Order attacks run: 16 single-field sorts plus 16 stable variants,
          numeric sorts on `entry` and `previous` both directions, as-filed and reversed,
          `position mod k` for k=2..40, 1560 affine row-index maps, 56 two-field sorts —
          none reproduces the chain, and removing `previous` leaves it unrecoverable.
          Arithmetic attacks run: every contiguous segment of length ≤8, full permutations
          to length 6 and 200 seeded shuffles beyond, under both the builder rule and the
          prose rule — no segment is order-free. Per-entry perturbation moves every
          checkpoint downstream, with the single exception in finding 5. Frame attacks
          returned the harvest above. The chain is real; the arithmetic on it is not stated.
    hard_to_do: no — it is hard to *guess*, not hard to do. The forty-step walk is genuine
          work and the placement past line 204 is real, but the difficulty that decides the
          score is an unstated modulus, which is opacity, not comprehension cost.
    fix: In `r5/specs/q09_main_glm.py:194-201`, delete the two modulo terms from `_step` so
         the arithmetic is exactly what the handbook already states —
         `carry: fig*2 + carried + remainder`, `relief: fig*3 - min(absorb, fig)`, with the
         remainder being the unapplied part of a take-back carried to that stage's next
         carry — then rebuild and regenerate the key. I verified this is safe against every
         shape attack: with the modulo terms removed, no contiguous segment of length ≤8 has
         an order-free replay and every one of the 38 stage values moves a checkpoint (the
         2066/2067 collision of finding 5 disappears with it). If instead the modulus is to
         be kept, it must be written into the replay rules in the same voice as the rest of
         the page and given an institutional reason — but a modulus of `11 + balance % 13`
         has no story a clerk would tell, so removing it is the honest change. Findings 3
         and 4 need their own fix in the same pass: vary the value line's position within
         each file (it is offset-from-end 1 in all 38) and give it a real English label per
         stage, accepting a non-zero H1/H3 rather than buying zero with nonsense.
         Add a build-time check that the handbook's stated rule and `_step` agree — the
         assertion in finding 2 cannot be that check, because it is generated from `_step`.

verdict: REVISE
