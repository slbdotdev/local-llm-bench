# Round-five re-review brief — the two round-two candidates proposed for admission

*One reviewer, one candidate, blind: you did not write it and you do not know who did. Read this
whole, once. Read-only except for the one report file you are told to write.*

## Why this review exists

`m01-main-glm` and `m10-main-glm` are the two most discriminating candidates this campaign has
produced: on the 2-bit workhorse (`q27-IQ2_M-64k`, four trials each) `m10-main-glm` is **0 of 4**
and `m01-main-glm` is **1 of 4**, against a suite that sits at 96 of 100. The round-five manager
proposes to admit them.

They cannot be admitted on that number alone. `plan-2026-09-07.md` section 3.1 requires **two
blind cross-family reviews, both passing**, before any candidate enters the suite, and
`results/v7/authoring-2026-09-06.md` section 8.2 records that these nine round-two candidates got
**one** round of review, by clean-context agents rather than by the other two families. This
review is the shortfall being closed, and your verdict decides whether the candidate is admitted.

`results/v7/authoring-2026-09-06.md` section 8.1 also records that the round-two family labels are
the plan's *slot assignments* and not a claim about which model wrote the prose. Do not treat the
`glm` in the slot name as evidence of anything.

## What you are judging

The candidate is at `cand-glm/<slot>/`. Round two's property was **rung 0 — make the material
necessary**: a main-band answer must require reconciling facts from several files that the
prompt's own vocabulary cannot locate. The two standing tiers are unchanged: a task **Sonnet 5
fails is unfair, not hard**, and a task **Haiku 4.5 passes easily is saturated**.

A candidate the workhorse fails is interesting only if it fails it for the right reason. **Your
central question is whether these two are hard or merely broken.** `m01-main-glm` failed once by
running its context out after 39 file reads, and `m10-main-glm` came back confidently wrong three
times out of four. Either can be a real long-horizon failure, which is what the bench exists to
measure, or an unfair task, an ambiguous prompt, or a defective grader. Say which, with evidence.

## Method, in this order

It is a slow Windows mount: `cat`, `sed -n`, `ls` on named paths; never a recursive `find`, never
`grep -r` over the repository, never `git`. Work from
`/mnt/d/local-llm-bench/ollama-bench/results/v7/authoring`.

1. Read `prompt.md` as the model under test would, **before** anything else, and write down what
   you believe the deliverable must contain. Then read `NOTES.md`, `seed/` as far as the task
   needs, `ref/` and `test.py`. If your reading of the prompt and the reference disagree, that is
   a fairness finding whichever of you is right.
2. **Solve it yourself, honestly, from the prompt.** Then compare with `ref/`. This is the one
   thing no checker does, and it is what has found every fairness defect in this campaign.
3. Run, once each:

       python3 cand-glm/<slot>/selfcheck.py
       python3 probe_candidate.py cand-glm/<slot>
       python3 probe_idempotence.py cand-glm/<slot>
       python3 r5/check_rung0.py cand-glm/<slot>
       python3 r5/check_index_leak.py <slot>
       python3 r5/check_load_bearing.py cand-glm/<slot>
       python3 r5/check_tools.py cand-glm/<slot> --verbose

   `check_tools.py` is new: it runs every executable file in the seed with no arguments and fails
   the candidate if any prints a scored value. It dropped a round-four candidate that no other
   check caught. `check_harvest.py` does not apply — these specs predate `harvest_units()` — so
   do the harvest attack by hand instead, at step 5.
4. **Attack the shortcut.** Produce the deliverable from as few files as you can: an index, a
   manifest, a docs page, a helper that prints the answer. Say how many files your best shortcut
   needed and whether it reached the full score. **Under five files is a rung-0 failure and a
   REVISE.** Four of eight round-four candidates died here.
5. **Attack the harvest by hand.** Using tokens the prompt gives away, the roster's unit names,
   the deliverable's key names and any constant name you can see, run real greps on named paths:

       grep -rn -C2 '<token>' cand-glm/<slot>/seed/ | head -60

   Report the best single grep you found: the token, how many units' decisive values it put on
   screen, and whether the answer could then be finished without opening a per-unit file.
6. Check every number `NOTES.md` claims against the tree.
7. Judge the workhorse's recorded failure. Name the specific step where a small model is expected
   to go wrong, and say whether that step is **real work** or a **defect**: ambiguity, a
   judgement call, a grader stricter than its prompt, arithmetic volume, or a deliverable so long
   that a correct answer cannot fit in the output budget. Say whether a careful Sonnet-class
   model would be caught by the same step.

## Report

Write exactly one file, `r5/reviews/<slot>--<your family>.md`, in this shape and nothing else:

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
