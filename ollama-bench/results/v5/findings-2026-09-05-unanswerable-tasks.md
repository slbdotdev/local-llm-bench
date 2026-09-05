# Two tasks whose reference answers their own material does not support

Found 2026-09-05 by the Opus manager session. Both look exactly like difficulty and neither is.
Both were caught by running the tasks and reading *why* a strong model failed, rather than by
counting failures.

`plan-2026-09-05.md` section 2.3 puts this class outside the difficulty ladder in terms:

> **Not on the ladder, ever:** ambiguity, missing information, unstated conventions, trick
> wording, or anything the prompt does not say plainly. If two careful readers can disagree about
> what the task asks, the task is broken.

Section 2.2 is the instrument that catches it: **a task Sonnet fails is under suspicion of being
broken, not hard, until a reading proves otherwise.** Both of these were surfaced by a Sonnet
failure and both readings confirmed the suspicion.

## 1. t03/cand-1 — the reference asserts a date that is nowhere in the record

t03 is an extraction task: read a long technical record, report eight fields as JSON. Its
reference answer gives `incident_date` as `"2031-04-17"`.

    grep -c "2031"                          seed/*.txt  ->  0
    grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}"   seed/*.txt  ->  (nothing)

The string is absent. The year is absent. **No date in any format appears anywhere in the
material.** And the prompt says, in terms: "Do not infer or calculate facts that are not stated
there." There was no correct answer to give.

**Five independent trials across two model families all reported this**, which is as strong as
this kind of evidence gets:

- three Haiku trials answered `null` or empty and explained that the record does not state one;
- a Sonnet trial: *"No incident date appears anywhere in the record (verified via exhaustive
  numeric/date-pattern search), so per the instruction not to infer facts not stated,
  incident_date was set to 'not stated in the record' rather than fabricated."*

Every one of them was scored a failure. Worse, the failure was **total rather than partial**: a
non-string value trips the checker's shape gate, so a trial with six of eight fields correct
scored `SCORE 0/8` and `VERDICT visibly_failed`.

A second field was wrong the same way, and in the opposite direction. The material says "delayed
telemetry writes **affecting** 12.4% of eu-west-2 tenants" (seed line 101); the reference demanded
"delayed telemetry writes **for** 12.4% of eu-west-2 tenants", a wording that appears nowhere.
**The reference paraphrased its own material** — while the prompt, as amended the same day,
requires string values copied verbatim.

### The fix, then the withdrawal

`fix_t03c1_unanswerable.py` removed `incident_date` from the prompt, the checker's field list, the
accept table and the reference; corrected `impact_scope` to the material's own words; and
corrected `_ora_total`, which was hardcoded at 8 while only seven subchecks ran.

**It was then withdrawn from the suite anyway**, because re-running it exposed a third field with
the same shape. `detection_channel` must be `"synthetic canary"`; that phrase occurs **once** in
the whole record, in a passage describing the tooling, and the only sentence about detection says
the review "cites the canary as detection evidence". Sonnet answered "canary notification",
Haiku answered "canary" and "operations channel". Three defensible readings, one accepted string.

Two of eight fields were repairable one at a time; the third made the pattern clear. The task's
material never states an authoritative field-and-value table, so several free-text fields have
more than one defensible answer. **t03 was reverted to `cand-3`**, its previously gated candidate
(Sonnet 3/3, GLM 3/3), which is smaller but sound. `cand-1` stays on disk with this page beside it.

## 2. t04/cand-2 — the reference contradicts the prompt's own rule

t04/cand-2 asks where this behaviour is implemented:

> When the service begins shutting down, it refuses newly submitted jobs but continues running the
> jobs already waiting, in their original first-in-first-out order, until none remain.

and instructs: *"Cite the **smallest contiguous line span that contains the implementation of the
behavior itself**."*

The implementation is in two methods of one class. `submit` (lines 7-11) performs the refusal;
`begin_shutdown` (lines 13-17) sets the flag and drains FIFO. **The checker accepts only
`(14, 17)`** — `begin_shutdown` alone, which does not contain the refusal at all.

Sonnet answered `7-16` and explained both halves. Haiku failed it too. By the prompt's own words
the smallest contiguous span containing the implementation is the one spanning both methods, so
**the reference is further from the prompt than the answer it rejected**.

This is the same latent defect that was found and fixed in t04/cand-3 on 2026-09-04 — "smallest
contiguous line span" has no answer when an implementation is split. The fix was applied to
cand-3 and never to cand-2, which had no gate row at the time.

**Withdrawn from the rotation**, not repaired: making the reference match the prompt makes the
task trivially wide, and making the prompt match the reference ("cite the method that drains")
removes what made it interesting. t04's rotation is now cand-1, cand-3, cand-3.

## The instrument that would have caught the first one, and now does

`results/v5/authoring/check_derivable.py`. For every JSON reference answer it takes each leaf
value, normalises whitespace and case, and searches the concatenated seed material for it, with
tolerant alternates for numbers and whole dates. It flags t03/cand-1's two values and clears every
other reference answer in the tree, including all eight `cand-5`.

**Nothing already in the tree could have found this, and the reason generalises.**

- `verify_candidates.py` copies `ref/` into the sandbox and runs the checker, so the reference
  passes by construction *whatever it asserts*. It never asks whether the material supports it.
- `probe_checkers.py` perturbs a **correct** answer, so it inherits the same blind spot.
- `selfcheck.py` executes the prompt's examples against `ref/`, not against `seed/`.

All three agree with each other and all three are wrong together, because all three take the
reference as the definition of correct. The new check is the only one that treats the *material*
as the authority.

One correction worth recording, because it nearly produced a clean bill of health. The first
version's date fallback also accepted the bare year and the bare day-of-month, both of which match
almost any prose — and it passed the fabricated date. **A tolerant check that tolerates everything
is worse than no check, because it reads as a clean result.** It now accepts only whole-date
alternates.

## What to carry forward

- Run `check_derivable.py` before gating any extraction task. It is cheap and needs no model.
- **A free-text field with one accepted string is a trap for the author, not for the model.**
  Either the material must state the value in exactly one place and one form, or the accept list
  must cover every defensible reading. t03/cand-1 did neither on three fields.
- The Sonnet guard earns its cost. Both defects here were surfaced by a Sonnet failure, and in
  both cases the model's answer was better justified than the reference. Section 2.2's rule —
  suspect the task, not the model — was correct both times.
- **A worker's report is a claim.** g04/cand-5's notes stated "`test.py` against `ref/`: SCORE
  10/10, PASS, VERDICT correct, exit 0" and listed all eight A7 probes as passing. Independent
  verification scored the reference **5/10**: the reference had been written to `ref/reconcile.py`
  when the checker requires `ref/src/reconcile.py`. Its did-nothing sandbox also returned
  `confidently_wrong` where the contract requires `visibly_failed`. Both fixed and re-verified;
  the suite is now REF 39/39, EMPTY 39/39.
