# Round-5 cross-review brief

*One reviewer, one candidate, blind: you did not write it and you do not know who did. Read this
whole, once. Read-only except for the one report file you are told to write.*

## What you are judging

Four candidates were authored under `r5/BRIEF.md`, on two shapes. Read that brief's sections 1,
3 and **the section for your candidate's shape (4 or 5)** before you open the candidate. There is
no research round this time: the shapes are the whole design.

* **Shape A, long serial state** — at least twenty ordered steps, each consuming the previous
  step's *output*. Your job is to find the step that is not a step: a computation a solver can
  reach without having done the ones before it. If step 17 can be computed without steps 1-16,
  the task is arithmetic volume wearing a chain's label, and that is REVISE.
* **Shape B, large correct output** — a deliverable of thirty or more rows or files that must be
  internally consistent, graded exactly. Your job is to find the padding: rows that say the same
  thing about near-identical inputs buy length without work. And to check that a **truncated**
  deliverable really does fail; a grader that passes the correct answer cut off two thirds of the
  way through measures nothing, and that is the failure the whole shape exists to catch.

The round's standing property is unchanged: **a value a single grep can harvest across units is
not material, whatever its token count.** The 2-bit workhorse does not read the tree, it greps
it. Attack this candidate the way that model does.

The two standing tiers are unchanged: a task **Sonnet 5 fails is unfair, not hard**, and a task
**Haiku 4.5 passes easily is saturated** and adds nothing.

## Method, in this order

The candidate is at `cand-<family>/<slot>/`. It is a slow Windows mount: `cat`, `sed -n`, `ls`
on named paths; never a recursive `find`, never `grep -r` over the repository, never `git`.

1. Read `prompt.md` as the model under test would, **before** anything else, and write down what
   you believe the deliverable must contain. Then read `NOTES.md`, `seed/` as far as the task
   needs, `ref/` and `test.py`. If your reading of the prompt and the reference disagree, that is
   a fairness finding whichever of you is right.
2. Run, from the authoring directory, once each:

       python3 cand-<family>/<slot>/selfcheck.py
       python3 probe_candidate.py cand-<family>/<slot>
       python3 r5/check_rung0.py cand-<family>/<slot>
       python3 r5/check_index_leak.py <slot>
       python3 r5/check_load_bearing.py cand-<family>/<slot>
       python3 r5/check_harvest.py cand-<family>/<slot> --verbose
       python3 r5/check_tools.py cand-<family>/<slot> --verbose

   `check_tools.py` is new: it runs every executable file in the seed with no arguments and fails
   the candidate if any of them prints a scored value or the decisive datum of more than a
   quarter of the declared units. It is the mechanical form of "no tool in the seed may print the
   answer", which was found by hand twice last round and dropped two candidates. Read its output
   even when it passes: a tool that prints nine tenths of the material and stops short of the
   answer is still a finding, and the check reports the count.

   `check_harvest.py` now prints **`vacuous`** instead of `0.000` when every declared unit is
   derived. Vacuous is neither a pass nor a failure: it means the measure had nothing to bite on,
   and **verifying the claim by hand is yours**. Do it, and say in `harvest:` what you tried.

3. **Attack the harvest, by hand, and do not trust the checker.** The checker measures what the
   author *declared* in `harvest_units()`. Your first question is whether that declaration is
   honest and complete: does the answer depend on per-unit facts the spec did not declare? Then
   run the attack yourself on the built candidate, with real commands on named paths:

       grep -rn '<token>' cand-<family>/<slot>/seed/ | head
       grep -rn -C2 '<token>' cand-<family>/<slot>/seed/ | head -60

   using tokens the prompt gives away, the roster's unit names, the deliverable's key names, and
   any constant name you can see. Report the **best single grep you found**: the token, how many
   units' decisive values it put on screen, and whether the answer could then be finished without
   opening a per-unit file.
4. **Attack the shortcut**, as in every round: produce the deliverable from as few files as you
   can — an index, a manifest, a docs page, a helper tool that prints the answer. Say how many
   files your best shortcut needed and whether it reached the full score. A candidate whose
   answer is assembled from under five files has failed rung 0.
5. Check every number `NOTES.md` claims against the tree (a line number, a count, a fraction).
   Two of last round's three systemic defects were found by a reviewer checking a number rather
   than reading an argument.
6. Judge difficulty honestly against the two tiers: name the specific step where a Haiku-class
   model is expected to go wrong, and say whether a careful Sonnet-class model would be caught by
   the same step. If both tiers pass or both fail, say so.
7. Say whether the anti-harvest mechanism makes the task harder to **do** or harder to
   **understand**. Obfuscation, a value split across lines to defeat a grep, an encoded datum, a
   fact whose location is a puzzle, or sheer arithmetic volume are all REVISE: they fail Sonnet
   too, and this benchmark never buys difficulty with comprehension.

## Report

Write exactly one file, `r5/reviews/<slot>--<your family>.md`, in this shape and nothing else:

    verdict: PASS | REVISE
    fair: yes | no — one sentence
    checker: sound | unsound — one sentence, naming the case you ran
    harvest: <n>/<units> by `<the token>` — the best single grep you found, and whether it finishes the answer
    declaration: honest | <the per-unit fact harvest_units() left out>
    shortcut: <n> files, score <a>/<b> — what the shortcut was
    notes_claims: verified | <the claim that failed>
    tiers: Haiku fails at <step> | both pass | both fail — one sentence
    tools: clear | <the tool that printed something and what>
    shape: <for A: the step that can be reached without the ones before it, or `chain intact`;
            for B: whether a truncated deliverable fails, and what you found that is padding>
    hard_to_do: yes | no — one sentence on section 7
    fix: <one concrete change, or none>

REVISE needs at least one concrete fix. Do not rewrite the task; do not edit the candidate.
