# Review request: two benchmark tasks, each made harder today

You are reviewing two tasks from a benchmark suite for local language models. Each was edited
today to make it measure what it was designed to measure. Report findings only; **change no
file**.

Working directory: `/mnt/d/local-llm-bench/ollama-bench/results/v7/authoring`

The two tasks:

    cand-glm/m09-main-glm     behaviour: reading past the first screen
    cand-glm/m05-cheap-glm    behaviour: documentation that disagrees with the code

Each directory holds `prompt.md` (the only thing the model under test sees), `seed/` (the
starting working directory), `ref/` (the reference answer), `test.py` (the hidden grader),
`selfcheck.py`, `NOTES.md` and `MANIFEST.json`.

## The governing rule you are judging against

**A task must be hard to DO and never hard to UNDERSTAND.** If two careful readers can disagree
about what the task asks, the task is broken, not hard. Difficulty may come only from the amount
of material that has to be read and reconciled, from a plausible-looking wrong course that the
material itself rules out, and from steps that depend on one another — in that order. It may
never come from ambiguity, from missing information, from an unstated convention, or from a
tighter output format.

## What changed

**m09-main-glm.** The timeline `seed/data/quarantine-timeline.csv` gained one row:
`2034-03-28,CC-1204,replay,requarantined,post-lift check failed`. The amendment dated 2034-04-14
in `seed/docs/replay-policy.md` was rewritten. The expected answer moved from `2034-03-20` to
`2034-04-11` in `ref/lift-audit.txt` and in the grader.

**m05-cheap-glm.** `seed/docs/rate-card.md` rules R4, R5, R6 and R7 were rewritten so that R5
alone states what the fuel surcharge is computed on. The grader gained back a sixth subcheck
scoring the content of `fixlog.txt`, and its total went from 5 to 6.

## Method — do exactly this, in this order

Read each file whole, once. Do not read files in slices. Do not re-read a file you have read.

1. For **m09-main-glm**: read `prompt.md`, then `seed/docs/replay-policy.md`, then `NOTES.md`,
   then `test.py`. Run `python tools/timeline_dump.py` once from inside `seed/` and read its
   output. Work out the answer yourself from the policy and the timeline **before** you look at
   `ref/lift-audit.txt`, then compare.
2. For **m05-cheap-glm**: read `prompt.md`, then `seed/docs/rate-card.md`, then
   `seed/src/kestrel/rates.py`, then `NOTES.md`, then `test.py`. Work out which of the eight
   rules the code implements wrongly, and which rule each wrong result should be attributed to,
   **before** you look at `ref/fixlog.txt`, then compare.
3. Run each task's `selfcheck.py` once, at the end, and nothing else.

## Report exactly these five fields, per task

1. **The answer you derived yourself**, before reading the reference, and whether it matches.
2. **Is the task hard to understand anywhere?** Name any sentence where two careful readers could
   land differently. This is the field that matters most; be specific or say "none".
3. **Is the added difficulty on the ladder** — more material to reconcile, a more plausible wrong
   course, more dependent steps — or is it ambiguity, missing information or format strictness
   wearing difficulty's clothes?
4. **Is the grader's expected answer the one the material actually supports?** Quote the sentence
   that settles it.
5. **One concrete fix**, if any. If none, say none.

Then one final line: for each of the two, `ACCEPT` or `REVISE`.

Be concrete and short. Quote line numbers. Do not restate the code back to me.
