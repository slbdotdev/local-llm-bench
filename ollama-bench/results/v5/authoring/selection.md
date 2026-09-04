# v5 candidate selection — 2026-09-04

Twenty-four candidates were authored, three per task, by eight parallel Luna runs against
`CONTRACT.md`. This page records which one this session picked per task and why. Nothing has been
moved or deleted: all 24 candidates remain in place, and these are recommendations with reasons
attached, not a decision already made.

## The section 4a audit record, which is the point of this page

For **every one of the eight tasks**, the answer to "which local runs informed this task, and
which property did they settle" is:

> **None. No local run of any kind informed any task in this suite.**

That is not a discipline achievement, it is a hardware fact: FRACTAL's CUDA backend was broken
for the whole session and no quant was reachable at any point
(`findings-2026-09-04-gpu-cuda-broken.md`). Selection against a quant's results was therefore not
merely avoided, it was **impossible**, and the selection can be audited on that basis rather than
trusted.

The flip side is the cost, and it must be carried forward: plan section 6 step 3 sizes each task
against the local model — does a trial finish under 300 s, does the prompt read unambiguously to
a small model, does the material fit the window. **None of those properties is settled for any
task.** They are outstanding for every task below, and they are the reason this suite is not ready
to run even setting the GPU aside.

Properties that WERE settled, mechanically and with no model involved
(`verify_candidates.py`, run under the same Windows interpreter the harness uses):

- the checker passes its own reference solution — `SCORE m/m`, `PASS`, `VERDICT correct`, exit 0;
- a did-nothing sandbox yields `VERDICT visibly_failed` and does not crash the grader;
- `prompt.md` is well inside the 2,000-word guidance (the largest is t01 at ~315 words);
- every prompt's worked examples execute against the reference (`selfcheck.py` per candidate).

## The picks

| task | pick | why this one |
| --- | --- | --- |
| g01 | **cand-2** | Precise mechanical execution: first-seen ordering independent of lexical order, duplicate keys merged in place, duplicate values counted not deduplicated, empty groups meaningful. The near-miss (reach for a convenient sorted aggregation, drop empty groups) scored 16/24 — strong discrimination, and it is the failure a fluent model actually makes. |
| g02 | **cand-3** | Halt at a literal frozen-tail sentinel and preserve the suffix byte-for-byte. The tempting wrong fix truncates the tail: it satisfies the visible assertion while silently losing valid content, which is the exact silent-damage shape the instrument exists to catch. Also the smallest reference of the three (81 lines, ~700 tokens) against the 5k appetite ceiling. |
| g03 | **cand-1** (replaced) | Mechanical rename plus signature change across three modules, with the straggler in a reflective `getattr` lookup. Completeness under tedium with **one** hidden site rather than five — which is why it holds where cand-3 did not. Sonnet 3/3, GLM 3/3. See "The g03 switch" below. |
| g04 | **cand-1** (replaced) | Minimal, precise repair driven by a supplied style tool, where the temptation is to delete or reformat rather than fix and the diff bound plus behaviour tests stop that. Sonnet 3/3, GLM 3/3. See "The g04 switch" below. |
| t01 | **cand-3** | Closest to the incident this task is drawn from: archived quotations and dated move notes are deliberately readable and look like stale links, but they are audit evidence. Updating them is productive-looking damage. |
| t02 | **cand-2** | **The docstring is accurate and the correct answer is "yes".** This is the one item in the suite that punishes a model which has learned to always find a discrepancy, and without it a reflexively negative model scores well on the comprehension class. It is selected for that property specifically. |
| t03 | **cand-3** | The tempting values sit in proposals and objections *before* the final decision log, so a model that stops reading before the last third is exposed. t03 carries the context axis, and this variant is the one whose failure mode is caused by not reading far enough. |
| t04 | **cand-3** | **The negative variant**: the described behaviour is implemented nowhere, and near-misses are planted (a 60-second cooldown setting, a comment about throttling, failure and reset-looking helpers). Plan section 4 calls this the most valuable single item for the headline measurement, and it is. |

## Why not simply take the sharpest trap everywhere, and the risk in these picks

Each task's three candidates were commissioned to differ in what they make hard: careful
reading, precise mechanical execution, knowing when to stop. Picking the "knowing when to stop"
variant every time would maximise the confidently-wrong signal and produce a **one-dimensional
suite** — eight tasks all measuring the same disposition, reported as if they measured two
classes.

So the picks are deliberately split by class. **Transformation (g01-g04) leans mechanical**,
because that is what section 4 defines the class as — g01 and g04 are precision and semantic
repair rather than restraint. **Comprehension (t01-t04) is where judgement and stopping live**,
which is where section 4 puts the traps. Three of the four comprehension picks have a negative or
partly-negative correct answer, and t02/cand-2 is positive on purpose so that blanket refusal
cannot score.

The residual risk, stated so it can be checked rather than discovered: **this balance is a
judgement made by one session with no local evidence at all.** If the selected suite later looks
one-dimensional, the alternates are all still on disk with their notes.

## Banked, not decided: should t02 and t04 be run as rotating variants?

Section 4's table says t02 has a "trap in half the variants" and t04 has a "trap variant where it
is absent", which reads as though these tasks are meant to be **sets of variants rotated across
trials**, not single fixed items. As single items they are one bit each: t02/cand-2 always
answers yes, t04/cand-3 always answers no. A model that guesses that one bit and holds it scores
full marks on that task for the wrong reason, and across three trials the guess is never
punished.

Rotating the variants would fix it, and all three variants of each exist and verify clean. But
changing a task from one item into a rotating set changes what the task measures and how its
arity works under section 7, so it is **structural, and banked rather than taken**. Both
alternates are retained on disk for whoever decides.

## One defect worth carrying, found by verification rather than reported

g04's partial credit is nearly saturated at "do nothing": an untouched sandbox already scores 8/9
on cand-2, because most subchecks are behaviour tests the pristine file passes. `PASS` still
requires the style tool to report clean, so the **binary** verdict is sound and the task is
usable — but g04's `SCORE` carries almost no information and should not be quoted as partial
credit. Either the checker should weight the style-clean condition much more heavily, or g04's
score should be reported as binary only. Not fixed here: it changes how a task is scored, which
is structural.


## The g04 switch, 2026-09-04 — made on gate evidence, which rule 1 prescribes

g04/cand-2 was the original pick. **Sonnet failed it on both trials**, each time on the same
subcheck, `default_isolation`, and each time for the same stated reason: it deliberately
*preserved* the shared routing dictionary.

The first failure looked like a prompt contradiction ("public behavior must remain intact" against
a checker requiring the behaviour to change) and the prompt was reworded to say that correctly
fixing a genuine defect is expected to change the defective behaviour. **Sonnet failed it again
anyway**, still preserving the sharing. At that point the diagnosis changed, and the deeper
problem is in the task rather than the wording:

    def _ora_default_isolation(mod):
        first  = mod.remember("/promo", "/sale")
        second = mod.resolve("/promo")
        return first == "/sale" and second == "/404"

The checker requires that a function named **`remember`**, called without an explicit table,
must **not** persist anything. A reader who takes the module's own vocabulary seriously will
conclude that persistence is the point of `remember` and preserve it. That is not a trap the
benchmark wants — it does not measure whether a model can spot a silent defect, it measures
whether a model guesses which of two coherent readings the author had in mind. Sonnet chose the
one the identifier names.

g04/cand-1 was gated instead and **passed Sonnet 8/8, `VERDICT correct`, exit 0** on its first
trial. It is now the pick.

**Why this is not a section 4a violation.** 4a forbids keeping, dropping, rewording or reordering
a task because a **quant** passed or failed it. This decision used no quant evidence — none
existed, the GPU was unusable for the whole authoring window — and plan rule 1 says in terms that
a task Sonnet fails "is fixed or replaced, and that is a *task* defect, never evidence about a
quant". Fixing was tried first and did not take; replacing is the prescribed remedy.

**What is inherited with cand-1, and it is the same wart:** its did-nothing sandbox still scores
7/8, so g04's partial credit remains nearly saturated whichever candidate is used. The binary
`PASS` is sound because it requires the style tool to report clean; the `SCORE` is not
informative and should not be quoted as partial credit. That is a property of the task shape —
mostly behaviour subchecks that a pristine file passes — and it is unresolved.


## The g03 switch, 2026-09-04 — a task with more hidden sites than its prompt could specify

g03/cand-3 was the original pick. Its history across three Sonnet trials was **FAIL, PASS, FAIL**
— 1/3, well short of rule 1's 3/3 — and the two failures were on **different** subchecks:
`reflection propagation` the first time, `bundle urgent propagation` the third. The prompt was
amended between them to state that every forwarding function, including the reflective
dispatcher, must pass the new options through; that fixed the first site and the second one then
failed.

That pattern is the diagnosis. The task threads a new keyword-only option through so many
forwarding sites — a default sender, a comprehension, a reflective `getattr` lookup, an executed
doctest, a bundling wrapper — that a prompt short enough to satisfy the 2,000-word limit cannot
enumerate them, and a model that finds four of five is scored `confidently_wrong` for what is
really an underspecification. Enumerating them all would turn the task into a checklist and stop
measuring anything. Both ways out are bad, which is what makes it the wrong task rather than a
hard one.

g03/cand-1 was gated instead: **Sonnet 3/3** (12/12, `VERDICT correct`, on three independent
trials) and **GLM 3/3**. It tests the same property — completeness of a mechanical rename plus
signature change under tedium, with the straggler in a reflective lookup — with one hidden site
rather than five.

Same section 4a note as for g04: this used no quant evidence, none existed, and rule 1 explicitly
provides for replacing a task the gate model fails.

## 2026-09-04 — harder variants authored as `cand-4`, and DELIBERATELY NOT SELECTED

Section 4's own remedy for a saturated task is a harder variant. Seven exist now, one for each
saturated task (g01, g02, g03, g04, t01, t02, t03); t04 is not saturated and got none. They were
authored by Luna (`gpt-5.6-luna` at high effort, one run per task, in parallel) against the current
`CONTRACT.md`.

**They are candidates on disk and nothing more.** Writing them does not take the structural
decision — whether the suite is re-authored, or the saturation is accepted and reported as a stated
limitation of the ranking, remains **the owner's**. Having the candidates ready makes either answer
cheap, which is the whole point of writing them now. **Nothing in `gate-suite/` was changed**, no
existing candidate was edited, and no selection was made.

Verified independently rather than taken on the workers' word: `verify_candidates.py` now covers
**31 candidates and reports REF 31/31 and EMPTY 31/31, no problems** — every `cand-4` produces
`SCORE m/m` / `PASS` / `VERDICT correct` from its reference solution, and `VERDICT visibly_failed`
with no grader traceback from an untouched sandbox.

What each makes harder, from the authors' own notes: g01 a lexical state machine where quote state
toggles; g02 precise token-boundary reasoning, requiring the maximal dotted expression; t01 harder
semantic classification with exact reporting. (g03, g04, t02 and t03 carry notes in their own
`NOTES.md`.)

**Two scope violations by the workers, found and corrected.** One run created a stray
`ollama-bench/g04/` tree entirely outside `tasks-v5/`, and another left a stray
`tasks-v5/g02/ref/calls.py` at task level rather than under `cand-4/`. Both are removed. **My own
error compounded the first**: I ran `git add -A` in commit `9cc4ea8` while those workers were still
writing to the tree, so the stray was committed before I noticed it. The deletion is in the
following commit. The lesson is the obvious one — do not `git add -A` while background workers hold
the tree — and it is the same class of mistake as the worker collision earlier in this session.
