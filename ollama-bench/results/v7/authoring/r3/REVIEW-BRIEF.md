# Round-3 cross-review brief

*One reviewer, one candidate, blind: you did not write it and you do not know who did. Read
this whole, once. Read-only except for the one report file you are told to write.*

## What you are judging

Ten candidates were authored tonight under `r3/BRIEF.md` to break a saturated suite. The owner's
requirement: **most must fail Haiku 4.5 while Sonnet 5 passes them.** A task Sonnet fails is
unfair, not hard. A task Haiku passes easily is saturated. Read `r3/BRIEF.md` sections 1, 5 and
the research idea the candidate implements (`../research-r3-2026-09-08.md`, its slot's subsection
of section 2) before opening the candidate.

## Method, in this order

The candidate is at `cand-<family>/<slot>/`. The tree is a slow mount: `cat`, `sed -n`, `ls`;
never a recursive find, never `git`.

1. Read `prompt.md` as the model under test would, **before** anything else, and write down what
   you believe the deliverable must contain. Then read `NOTES.md`, `seed/` as far as the task
   needs, `ref/` and `test.py`. If your reading of the prompt and the reference disagree, that is
   a fairness finding whichever of you is right.
2. Run, from the authoring directory, once each:

       python3 cand-<family>/<slot>/selfcheck.py
       python3 probe_candidate.py cand-<family>/<slot>
       python3 r3/check_rung0.py cand-<family>/<slot>
       python3 r3/check_index_leak.py cand-<family>/<slot>
       python3 r3/check_load_bearing.py cand-<family>/<slot>

3. Attack the shortcut. Try to produce the deliverable from as few files as you can: an index,
   a manifest, a docs page, a helper tool that prints the answer, a single grep over the prompt's
   own words. Say how many files your best shortcut needed and whether it reached the full
   score. A candidate whose answer is assembled from under five files has failed rung 0.
4. Check every number `NOTES.md` claims against the tree (a line number, a count, a fraction).
   Last round two of three systemic defects were found by a reviewer checking a number rather
   than reading an argument.
5. Judge difficulty honestly against the two tiers: name the specific step where a Haiku-class
   model is expected to go wrong, and say whether a careful Sonnet-class model would be caught
   by the same step. If both tiers pass or both fail, say so.

## Report

Write exactly one file, `r3/reviews/<slot>--<your family>.md`, in this shape and nothing else:

    verdict: PASS | REVISE
    fair: yes | no — one sentence
    checker: sound | unsound — one sentence, naming the case you ran
    shortcut: <n> files, score <a>/<b> — what the shortcut was
    notes_claims: verified | <the claim that failed>
    tiers: Haiku fails at <step> | both pass | both fail — one sentence
    fix: <one concrete change, or none>

REVISE needs at least one concrete fix. Do not rewrite the task; do not edit the candidate.
