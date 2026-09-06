# Round-4 cross-review brief

*One reviewer, one candidate, blind: you did not write it and you do not know who did. Read this
whole, once. Read-only except for the one report file you are told to write.*

## What you are judging

Ten candidates were authored under `r4/BRIEF.md`. Read that brief's sections 1 and 4, and the
research idea the candidate implements (`../research-r4-2026-09-09.md`, its slot's subsection of
section 5), before you open the candidate.

The round's one new property: **a value a single grep can harvest across units is not material,
whatever its token count.** Eighteen of nineteen candidates last round were answered correctly
on the 2-bit workhorse while naming 6 to 49% of their material, because the model greps the tree
rather than reading it. Your job is to attack this candidate the way that model does.

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
       python3 r4/check_rung0.py cand-<family>/<slot>
       python3 r4/check_index_leak.py <slot>
       python3 r4/check_load_bearing.py cand-<family>/<slot>
       python3 r4/check_harvest.py cand-<family>/<slot> --verbose

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

Write exactly one file, `r4/reviews/<slot>--<your family>.md`, in this shape and nothing else:

    verdict: PASS | REVISE
    fair: yes | no — one sentence
    checker: sound | unsound — one sentence, naming the case you ran
    harvest: <n>/<units> by `<the token>` — the best single grep you found, and whether it finishes the answer
    declaration: honest | <the per-unit fact harvest_units() left out>
    shortcut: <n> files, score <a>/<b> — what the shortcut was
    notes_claims: verified | <the claim that failed>
    tiers: Haiku fails at <step> | both pass | both fail — one sentence
    hard_to_do: yes | no — one sentence on section 7
    fix: <one concrete change, or none>

REVISE needs at least one concrete fix. Do not rewrite the task; do not edit the candidate.
