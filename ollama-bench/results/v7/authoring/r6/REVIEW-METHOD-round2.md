# Round-six re-review method — the round-two nine, revised builds

*This file is the method. Your cover brief names your family, your candidate slot, and the one
report file you write. One reviewer, one candidate, blind: you did not write it and you do not
know who did. Read this whole, once. Read-only except for that one report file.*

## What you are judging

The round-two nine are staged main-band candidates built on rung 0 — **a main-band answer must
require reconciling facts from several files that the prompt's own vocabulary cannot locate**.
Each has been revised once since the 2026-09-07 cross-family review; the tree in front of you
is the revised build, and it is the only thing under judgment. Attack it fresh: your verdict is
yours, not a check of someone else's fix list.

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

       python3 cand-glm/<slot>/selfcheck.py
       python3 probe_candidate.py cand-glm/<slot>
       python3 probe_idempotence.py cand-glm/<slot>
       python3 r5/check_rung0.py cand-glm/<slot>
       python3 r2/check_index_leak.py <slot>
       python3 r2/check_load_bearing.py cand-glm/<slot>
       python3 r5/check_tools.py cand-glm/<slot> --verbose

   `check_harvest.py` does not apply — these specs predate `harvest_units()` — so do the
   harvest attack by hand, at step 5. Read every checker's output even when it passes.
4. **Attack the shortcut.** Produce the deliverable from as few files as you can: an index, a
   manifest, a docs page, a helper that prints the answer, a diff of two data files. Say how
   many files your best shortcut needed and whether it reached the full score. **Under five
   files for full score is a rung-0 failure and a REVISE.**
5. **Attack the harvest by hand.** With tokens the prompt gives away, the roster's unit names,
   the deliverable's key names and any constant name you can see:

       grep -rn -C2 '<token>' cand-glm/<slot>/seed/ | head -60

   Report the best single grep you found: the token, how many units' decisive values it put on
   screen, and whether the answer could then be finished without opening a per-unit file.
   Also check the frames: are value-bearing lines at a fixed line offset, or last lines, in
   byte-identical frames across most units? (`tail -n1` is a fair attack.)
6. Check every number `NOTES.md` claims against the tree. Two of round three's systemic defects
   were found by checking a number rather than reading an argument.
7. Judge the tiers honestly: name the specific step where a Haiku-class model is expected to go
   wrong, and say whether a careful Sonnet-class model would be caught by the same step.
8. Say whether the revision (the tree changed recently) made the task harder to **do** or
   harder to **understand**. Obfuscation, a value split across lines to defeat a grep, an
   encoded datum, or sheer arithmetic volume are all REVISE: they fail Sonnet too.

## Report

Write exactly one file, `cand-glm/<slot>/reviews/<your family>-2026-09-08.md`, in this shape
and nothing else:

    verdict: PASS | REVISE
    fair: yes | no — one sentence
    solved_it: yes | no — did your own answer match ref/, and where did you nearly go wrong
    checker: sound | unsound — one sentence, naming the case you ran
    shortcut: <n> files, score <a>/<b> — what the shortcut was
    harvest: <n>/<units> by `<the token>` — the best single grep you found
    tools: clear | <the tool that printed something and what>
    notes_claims: verified | <the claim that failed>
    tiers: Haiku fails at <step> | both pass | both fail — one sentence
    workhorse_failure: real | defect — one sentence naming the step, and why
    hard_to_do: yes | no — one sentence
    fix: <one concrete change, or none>

REVISE needs at least one concrete fix. Do not rewrite the task; do not edit the candidate.
