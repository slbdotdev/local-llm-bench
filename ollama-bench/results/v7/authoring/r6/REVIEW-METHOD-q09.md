# Round-six re-review method — `q09-main-glm`, rebuilt on shape A

*This file is the method. Your cover brief names your family and the one report file you write.
One reviewer, one candidate, blind: you did not write it and you do not know who did. Read this
whole, once. Read-only except for that one report file.*

## What you are judging

`q09-main-glm` (mode 9, main band) is a **shape A, long serial state** candidate: at least
twenty ordered steps, each consuming the previous step's *output*. It was dropped in round five
after blind readers reproduced the whole answer at full score from two files, twice. It has been
re-authored from its own spec with build-time assertions. The tree in front of you is the
rebuilt build, and it is the only thing under judgment. Attack it fresh.

Your job, in one line: **find the step that is not a step.** If step 17 can be computed without
steps 1-16, the task is arithmetic volume wearing a chain's label, and that is REVISE. The
standing property: **a value a single grep can harvest across units is not material, whatever
its token count** — and a value sitting on the last line of every file inside a byte-identical
frame is harvested by `tail -n1` with no token at all. Attack the candidate the way the 2-bit
workhorse does: it does not read the tree, it greps it.

Blind rules: do not open the candidate's `reviews/` directory, anything under
`authoring/r5/reviews/`, anything under `authoring/r6/`, or any other candidate. Do not run
`git`. Never touch anything under `suite/`.

Working directory: `/home/slb/local-llm-bench/ollama-bench/results/v7/authoring`.

The two standing tiers: a task **Sonnet 5 fails is unfair, not hard**, and a task **Haiku 4.5
passes easily is saturated** and adds nothing.

## Method, in this order

1. Read `prompt.md` as the model under test would, **before** anything else, and write down
   what you believe the deliverable must contain. Then `NOTES.md`, `seed/` as far as the task
   needs, `ref/`, `test.py`, `selfcheck.py`. If your reading of the prompt and the reference
   disagree, that is a fairness finding whichever of you is right.
2. **Solve it yourself, honestly, from the prompt.** Then compare with `ref/`. This is the one
   thing no checker does, and it has found every fairness defect in this campaign.
3. Run, once each, from the authoring directory (`python3` for the checkers; grader *verdicts*
   come from the Windows interpreter, `/mnt/c/Users/slb/scoop/apps/python/current/python.exe`,
   per plan-r3 4.1):

       python3 cand-glm/q09-main-glm/selfcheck.py
       python3 probe_candidate.py cand-glm/q09-main-glm
       python3 probe_idempotence.py cand-glm/q09-main-glm
       python3 r5/check_rung0.py cand-glm/q09-main-glm
       python3 r5/check_index_leak.py q09-main-glm
       python3 r5/check_load_bearing.py cand-glm/q09-main-glm
       python3 r5/check_harvest.py cand-glm/q09-main-glm --verbose
       python3 r5/check_tools.py cand-glm/q09-main-glm --verbose

   `check_harvest.py` prints `vacuous` when every declared unit is derived — that is neither
   pass nor fail, and **verifying the declaration by hand is yours**.
4. **Attack the chain's order.** Try, for real: sort the log rows by file position (with and
   without the `previous` column), by identifier, by any single field; try `position mod k`
   and affine maps from row index; delete any column you suspect is doing the ordering. If any
   map reproduces the link walk, that is REVISE.
5. **Attack the chain's arithmetic.** Per-entry perturbation: which entries does each graded
   key actually depend on? For every contiguous segment, can a shuffled replay of that
   segment's contributions reproduce the segment's exit figure (a commutative sum)? Any yes is
   REVISE.
6. **Attack the frames and the harvest.** `tail -n1 docs/*.md src/**/*.py`, shape regexes over
   the tree, and the best single grep you can build from prompt tokens, roster names, key
   names and constant names. Report the token, how many units' decisive values it put on
   screen, and whether it finishes the answer. Check line offsets: are the stated figures at
   varied offsets, never last, with no frame shared across most units?
7. Check every number `NOTES.md` claims against the tree.
8. Judge the tiers honestly: name the specific step where a Haiku-class model is expected to
   go wrong, and say whether a careful Sonnet-class model would be caught by the same step.

## Report

Write exactly one file, `cand-glm/q09-main-glm/reviews/<your family>-2026-09-08.md`, in this
shape and nothing else:

    verdict: PASS | REVISE
    fair: yes | no — one sentence
    solved_it: yes | no — did your own answer match ref/, and where did you nearly go wrong
    checker: sound | unsound — one sentence, naming the case you ran
    harvest: <n>/<units> by `<the token>` — the best single grep you found, and whether it finishes the answer
    declaration: honest | <the per-unit fact harvest_units() left out>
    shortcut: <n> files, score <a>/<b> — what the shortcut was
    notes_claims: verified | <the claim that failed>
    tiers: Haiku fails at <step> | both pass | both fail — one sentence
    tools: clear | <the tool that printed something and what>
    shape: <the step that can be reached without the ones before it, or `chain intact` — say
            which order/arithmetic/frame attacks you ran and what they returned>
    hard_to_do: yes | no — one sentence on difficulty without comprehension cost
    fix: <one concrete change, or none>

REVISE needs at least one concrete fix. Do not rewrite the task; do not edit the candidate.
