# Round-five manager decisions, with reasons

**Owner's ruling, 2026-09-06 (campaign 2026-09-10): the material lever is exhausted at 96%. Admit
the staged round-two and round-three candidates that discriminate, slot for slot within the family
cap; report pass probability with its spread and the confidently-wrong rate over at least three
trials; run a context-pressure cell as a measurement only; and author a few new tasks on two
shapes, long serial state and large correct output. No further material round, and no single-trial
number is ever reported as a task property.**

*Recorded before any other work of this round. Everything below is downstream of it.*

## The admission pass, and the finding that shrank it

### What the ruling asked for, and what the artifacts actually support

The brief for this round said the nineteen staged candidates from rounds two and three "hold two
cross-family reviews". **They do not.** `results/v7/authoring-2026-09-06.md` section 8.2 records,
in terms, that the nine round-two candidates got **one** round of review, by clean-context agents
rather than by the other two families, and section 8.1 records that their family labels are "the
plan's slot assignments and not a claim about which model wrote the prose" — all nine were drafted
by clean-context Sonnet subagents. `plan-2026-09-07.md` section 3.1 requires two blind
cross-family reviews, both passing, before any candidate enters the suite. So the nine were one
review short and their `glm`/`luna`/`claude` labels, which is what the 40% cap is computed from,
are nominal.

That is a discrepancy between the brief and the record, and the record is what governs. It was
found before any register edit and it is the reason this pass admits three candidates and not
eight.

### The second finding: the two best candidates fail their first real review

`m10-main-glm` (workhorse **0 of 4**) and `m01-main-glm` (**1 of 4**) are the only two candidates
this campaign has produced that the workhorse mostly fails, and they were the obvious admissions.
Both were sent to a blind Luna cross-family review under `r5/REVIEW-BRIEF-r2.md`. **Both came back
REVISE**, before their second review was even run:

* **`m10-main-glm` — REVISE, and the finding is rung 0.** A **two-file** shortcut scores 6/8: diff
  the two CSVs and treat every raw path difference as a correction. Under five files is a rung-0
  failure, which is exactly what dropped four of eight round-four candidates. Its `NOTES.md` also
  claims 17,805 of 29,192 material tokens (61.0%) are traversed where the declared load-bearing
  set checks at 6,696 (22.9%) — a claim the built candidate does not bear out, the campaign's
  most-repeated defect. The reviewer's tier judgement is `both pass`: saturated at Sonnet and
  Haiku. So the workhorse's 0 of 4 is at least partly a defect and not only difficulty.
* **`m01-main-glm` — REVISE, on one narrow defect.** The prompt's required output key `authority`
  is a one-file locator to a load-bearing release note. Everything else is sound: the reviewer
  solved it and matched `ref/`, the checker is sound, the best shortcut needed **18 files at 7/7**
  (far above the floor), `NOTES.md` verified, tools clear, and the reviewer judges the workhorse
  failure **real** — a long all-stage reconciliation after 39 file reads, not ambiguity. Its fix
  is one rename plus the reference and grader expectations.

Both are **parked**, not dropped: one REVISE earns one revision under plan 3.1, and neither has a
free author lane this round. `m01-main-glm` is the cheapest discrimination available to the next
round and it is pickup 1 of the handoff.

### What was admitted, and why each one

Ranking is by workhorse pass probability over the trials each candidate actually has — round
three's four (one gate trial plus three repeats), round two's four for `m01`/`m10` and **one** for
the other seven, and round four's four for `p05`. A candidate replaces the incumbent of **the same
failure mode and band**, read from each candidate's own `MANIFEST.json`: round three's slot
numbers are its ten *ideas*, not the ten failure modes, so `n02`, `n04`, `n06`, `n01` and
`n10` are all mode 1 and compete for **one** slot between them. That single fact is what makes
this a three-row change rather than a ten-row one.

| # | mode / band | out (workhorse) | in (workhorse) | why this candidate |
| ---: | --- | --- | --- | --- |
| 1 | 1, main | `m01-main-claude` 5/5 = 1.000 | **`n02-main-glm`** 2/4 = 0.500 | the most discriminating candidate with two genuine PASSes for that slot, and the only move available that frees a claude slot. `m01-main-glm` (0.25) is better and is parked on its REVISE; `n01` (0.75), `n04` (0.50, claude) and `n06` (1.00) lose to it on the number or on the cap |
| 2 | 5, main | `m05-main-luna` 5/5 = 1.000 | **`p05-main-claude`** 1/4 = 0.250 | two cross-family PASSes with `fix: none` from both since round four, parked then only by the cap, and the strongest measured discrimination in the whole staged set at 0.250. Beats `n03-main-luna` (0.500) for the same slot |
| 3 | 9, main | `m09-main-glm` 5/5 = 1.000 | **`n05-main-luna`** 3/4 = 0.750 | two PASSes, and the only candidate for the slot |

Family share after the pass: **claude 8 (40%), glm 6 (30%), luna 6 (30%)** — claude exactly on the
cap, which `assemble_suite.py` allows, and the two slots of every mode still in different
families. It is the cap that stops the fourth admission: `n10-cheap-claude` (0.750, mode 1 cheap,
against `m01-cheap-luna` at 1.000) would put claude at 9 of 20, and no further claude-freeing move
is available while `m01`/`m10` are parked.

### Measured and deliberately not admitted

* `n06-main-glm` 4/4, `n07-main-claude` 4/4, `n08-cheap-glm` 4/4, `n09-cheap-luna` 4/4 — all at
  pass probability 1.000, the same as the incumbents they would replace. They are sound tasks and
  they buy no discrimination, so admitting them would be churn. `n09-cheap-luna` is the one worth
  naming: it is the single row of nineteen that ever passed the coverage gate (88.5%), so it
  remains the obvious admission the moment coverage is wanted for its own sake rather than as the
  demoted diagnostic it now is.
* `n01-main-claude` 3/4 and `n03-main-luna` 2/4 — lost their slots to a better candidate for the
  same mode and band, not on merit.
* `m02`, `m03`, `m04`, `m05`, `m07`, `m08`, `m09` of round two — one trial each, which the ruling
  forbids reporting as a task property, **and** one cross-family review short. Two things are
  owed before any of them can be admitted, and neither was affordable on this round's worker
  lanes.
* `p04-main-glm` (one PASS, one REVISE) and `p08-cheap-claude` (one PASS, one corrected REVISE)
  remain one review short, exactly as the round-four handoff left them.
