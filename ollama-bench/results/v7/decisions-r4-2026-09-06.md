# Round-four manager decisions, with reasons
*Renamed 2026-09-06 from `v7/decisions-r4-2026-09-09.md`: the campaign labelled rounds by planned campaign day, not by the calendar date they were written.*

**p03-main-luna — DROPPED after two revisions.** Second blind review reproduced the reference
with **zero files opened** (three greps, byte-identical, `test.py` 8/8 PASS correct) and showed
the slot no longer exercises mode 3 at all: no text under `seed/` asks the solver to create, move
or run anything, so there is no imported imperative to decline. The plan drops a candidate that
misses twice. `m03-main-glm` stays in the suite.

**p06-cheap-luna — DROPPED after one revision and two reviews.** Second review found a two-file
shortcut at full score: `prompt.md` names both `tests/test_decoder.py` and `src/relay/decoder.py`
by path, and the visible test states the kind label, the exclusive right boundary and the range
relaxation, so the other 42 files are ruling-out volume rather than steps. This is mode 6's known
structural property, not a fixable defect in this candidate: the plan already labels
`m06-main-glm` `short-traversal` because "mode 6's traceback names the file holding the defect and
no rung reaches around that" (D7-34). Its `HARVEST_EXEMPT` sentence was accepted as truthful by
the reviewer, which is the point — the exemption was honest and the mode still cannot clear rung
0. `m06-cheap-claude` stays in the suite.

**p07-cheap-glm and p10-cheap-glm — WITHDRAWN, unauthored.** Scheduling, not merit. The Z.ai plan
allows this manager one concurrent GLM run, each GLM slot measured about 57 minutes, and four
authoring runs plus six reviews on one lane would consume the remaining GPU window that the
reference arms and the calibration need. `m07-cheap-luna` and `m10-cheap-luna` stay in the suite.
An unfilled slot costs the suite nothing: admission only ever replaces an incumbent.

**p01-main-glm and p09-main-luna — in revision.** p01 on H4 = 1.000 (a shared sentence frame over
all 18 dates) found only after the checker's splitter was widened to break on `/`, `.`, `-` and
`_`; p09 on H4 = 0.816 and an inflated load-bearing declaration. p09's is a **second** revision, a
recorded deviation, granted because its first moved measured coverage from 19.4% to 47.3%.

**Family share if every survivor is admitted.** Candidates able to reach admission: p01 (glm),
p02 (claude), p05 (claude), p08 (claude), p09 (luna), and p04 (glm) if it lands. Replacing
m01-main-claude, m02-main-luna, m05-main-luna, m08-cheap-glm, m09-main-glm and m04-main-claude
gives claude 7, luna 6, glm 7 of 20 — every family inside the 40% cap, and the two slots of every
mode still written by different families.

**p01-main-glm — DROPPED after its one revision.** The revision closed the fairness defect it was
sent back for (recomputed by the re-reviewer: every affected stage's run-date falls strictly inside
its own horizon) and took H4 from 1.000 to 0.000, but the harvest failure came back one line
further out. The two named frames were replaced by new fixed frames one line from the value, and
`grep -C2` reaches one line further: `grep -rn -C2 'through:' seed/` returns 36 of the 54 declared
units, and `grep -rn -C2 'Older passes are not shown' seed/` — a frame found by reading one module,
with no giveaway vocabulary at all — returns 36 of 36. The re-reviewer then demonstrated a **two-file
shortcut at full score**: one file for the promise and the record id, one
`grep -rnE -C2 'DLV-|through:' seed/`, driven into a script, reproduced `ref/compatibility-report.txt`
byte for byte and scored 8/8 `correct`. Under five files is a rung-0 failure. The candidate also
re-entered a fairness defect of its own: README and all eighteen pages state the log convention as
"oldest signature last" while the rows run oldest-first, so a reader who trusts the prose lands in
the author's own listed wrong course. Two misses is a drop, as for p03. `m01-main-claude` stays in
the suite.

**Consequence for admission.** With p01 out, the family cap binds. Baseline is claude 7, glm 6,
luna 7 of 20. Every claude candidate admitted moves one slot to claude, and only p04 moves one
away. So if p04 lands: p09 plus **two** of {p02, p05, p08} gives claude 8 (40%, the cap refuses
only *above* 40%); all three gives claude 9 (45%) and `assemble_suite.py` refuses the suite. If p04
does not land: p09 plus **one** claude candidate is the maximum.

**p09-main-luna — DROPPED after two revisions.** Its blind re-reviewer reproduced
`ref/retention-report.txt` **byte for byte with no file opened**: `python3 tools/retention_audit.py`
— which `README.md` itself tells the solver to run — prints `-> verified_on = <date> (countersigned)`
and `-> windows: declared=… effective=…` for all nineteen regions, and two greps supply the rule and
the decision record. That is `r4/BRIEF.md` section 6's "no tool in the seed may print the answer",
and a zero-file shortcut is a rung-0 failure. The same review found the anti-harvest mechanism to be
the forbidden kind — a synthetic twelve-digit `Window base` split from its remainder across two
lines "for the sole purpose of defeating a grep" — the `Declared remainder`/`Runtime remainder` pair
undeclared in `harvest_units()` and harvestable 19/19 by one frame, and two `NOTES.md` claims false
of the built tree, including the inflated `history/CHANGELOG.md` load-bearing path its previous
revision was supposed to have closed. Two misses is a drop. `m09-main-glm` stays in the suite.

**The cap after four drops.** With p01, p03, p06 and p09 gone, the survivors are p02, p05 and p08
— all three authored by claude — and p04, in revision. Baseline is claude 7, glm 6, luna 7 of 20.
Every claude candidate admitted moves one more slot to claude and only p04 moves one away, and the
cap refuses a share **above** 40%, i.e. above 8 of 20. So: **p04 admitted ⇒ at most two of
{p02, p05, p08}; p04 not admitted ⇒ exactly one.** This is why p04's revision was put first on the
GLM lane ahead of both batched reviews when the Z.ai window refilled, and why p08's GLM review was
dropped from the lane: two claude candidates already hold a first-round cross-family PASS, and a
third review buys a candidate that cannot be admitted.

**p04-main-glm — PARKED after its one revision: one PASS, one REVISE.** The revision closed both
findings it was sent back for — `tools/run_checks.py` now validates a solver-supplied line and a
reviewer confirmed that importing it yields nothing, and the identical seven-line preamble above
every declaration is gone (H4 = 0.067, no content word shared by the fifteen closing sections). Its
luna re-reviewer returned PASS with `fix: none`. Its claude re-reviewer returned REVISE on a
finding that did not exist before: the six failing stages, and only those, carry post-close journal
rows dated `2034-07`, so `grep -rl '2034-07' data/intake/` returns exactly the `failed_stages`
line, and two `NOTES.md` claims are false of the built tree. Rung 0 is cleared — sixteen files,
above the five-file floor — so this is not a drop; it is a candidate that did not earn two PASSes
inside its one revision. `m04-main-claude` stays in the suite.

**p05-main-claude — PARKED by the 40% family cap, not on merit.** Two cross-family PASSes (luna,
glm), `fix: none` from both, `hard_to_do: yes` from both. With p04 unable to move a slot away from
claude, admitting both p02 and p05 would put claude at 9 of 20 (45%) and `assemble_suite.py` would
refuse the suite. It is admissible with no further work the moment a non-claude candidate takes a
claude slot.

**p02-main-claude — ADMITTED, replacing m02-main-luna.** Two cross-family PASSes, `fix: none` from
both. Chosen over p05 on a build-time property of the material and not on any verdict (owner's rule
4a): **floor coverage 74.8%**, thirty-eight load-bearing paths over four hops, the largest
causally-necessary set any candidate in this campaign has declared, against p05's 40.0% over
twenty-three paths; and its glm reviewer re-verified by hand that an exhaustive digit-run search
over the whole tree finds none of the eighteen decisive values, so its H1 = H2 = H3 = H4 = 0.000 is
a measurement rather than the vacuous zero a fully derived declaration can produce.

**Owner's ruling, 2026-09-06, on the coverage question.** Course 2: coverage is demoted to a
diagnostic reported beside every row, and admission rests on the reference arms and the two
cross-family reviews alone. Plan section 2.2 carries the amendment. Nothing becomes a gate again
until it has been shown to correlate with difficulty in the right direction. p05 and p08 remain
parked by the 40% family cap, not by coverage, and p04 by its split review.
