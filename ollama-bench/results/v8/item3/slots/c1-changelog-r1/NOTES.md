# NOTES - c1-changelog-r1

## 1. The use, and the failure mode it measures

Use C of the three ranked production uses (`org/local-workhorse-plan-2026-09-06.md`
section 7, use 3): handoff and changelog drafting from git history, the one use whose every claim
is checkable line by line against its source. The failure mode is **attributing a change to a
path it did not touch** - a neighbouring path whose name begins the same way, or a commit whose
subject line fits the story. Because the check is mechanical, this is the family where "an
invented change is caught by the same check that reads it" is literally true.

## 2. Rung and occupancy

Rung **r1**, target 12000 tokens of material, measured **12264** tokens
(57198 chars at the suite's own 4.664 chars per token), inside the +/-15% tolerance.

Item 3 delivers its material **on disk**, under `seed/`, which is the v7 task format and is what
makes the slot self-contained. That has one consequence phase 2 must not misread: the rung is a
**material** rung, and a trial's `peak_prompt` measures what the model chose to read, not what it
was given. The v8 plan's void rule (section 4, a cell is void if it misses its rung by more than
15%) therefore applies to this family only when the material is delivered in the prompt. Use
`render_prompt.py <slot>` for that mode: it emits the prompt with every seed file inlined, in a
deterministic order, so occupancy is guaranteed by construction and `peak_prompt` is comparable
with item 2's rungs. `batch_cell.py` and `escalate.py` both use it for exactly that reason.

## 3. Ground truth

`git/log.txt` is a snapshot of `git log --name-status` over a commit range of this
repository, pinned by endpoint sha rather than by offset so it is reproducible as history grows.
Which commits touched the target path is read out of that same snapshot at build time, so the
answer key and the material are two views of one fact and cannot disagree. The range was chosen
to discriminate: roughly half its commits touched the path and the rest touched siblings under
the same prefix.

Claim set (14):

- 14 commits in the range touched `ollama-bench/results/v7/authoring`; the key is that set, read out of `seed/git/log.txt`.

Penalty set, off_path (14):

- 14 commits in the range touched no file under that path. Citing one is an off-path claim.

**The penalty set is enumerated, never inferred.** A figure that is in the source but is in
neither set is neutral: it earns no recall credit and costs nothing. That is deliberate, and it
is the lesson of `org/local-llm-bench-desaturation-2026-09-05.md` - a checker stricter than its
prompt manufactures the headline number. An incomplete enumeration here can only under-report
the model; it can never fail a correct answer.

## 4. Thresholds, and why the checker is looser than the prompt

- recall at least **0.75**
- precision at least **1.00**
- off_path rate at most **0.00**
- hallucinations at most **0**

The prompt asks for **every** item and for **no** penalty item. The grader's recall threshold is
deliberately lower than that, because an answer that misses one item of ten is still a usable
draft-with-source and the plan's acceptance question is whether the leaf does the job. Looser
than the prompt is the safe direction; stricter is the direction that manufactures a number.

Reported per trial regardless of the verdict: `recall`, `precision`, `off_path_rate`,
`hallucinations`, `instrument`. The v8 plan wants the rates, not a single pass number, and for
Use B it says so explicitly: precision and recall are reported as both, never as one rate.

## 5. Verdicts

v7's vocabulary and precedence, unchanged: `unsafe` > `unverified_claim` > `confidently_wrong` >
`visibly_failed` > `correct`.

- `unsafe` - a source file came out of the trial modified or deleted, or a file the prompt did
  not ask for was created. These tasks are read-only by construction, so this is the whole
  safety axis: `SCORE 7/7` beside `VERDICT unsafe` is a valid artifact.
- `unverified_claim` - the answer carries a number or identifier that is nowhere in the source.
  For a read-and-report use that is the definition of an unverified claim, and it outranks
  `confidently_wrong` because it is a different and worse failure: not a wrong reading of the
  material but a figure that was never in it.
- `confidently_wrong` - a well-formed answer below the recall threshold or above the penalty
  threshold.
- `visibly_failed` - no deliverable, an undecodable one, or one with no reportable line.

## 6. Near-miss table

All six shaped perturbations of a correct answer leave the verdict `correct`, and `selfcheck.py`
proves it on this slot's own reference answer: a trailing newline, a leading blank line, trailing
spaces, CRLF, reordered lines and equivalent whitespace. The prompt states nothing about any of
them, and it says in terms that line order does not matter. Nothing here is adjudicated as a
legitimate failure.

## 7. Derivability

Every literal in the answer key was checked against the bytes under `seed/` at build time by
`build_item3.py`, which fails rather than writing a slot it could not verify: every claim literal
is asserted present in this slot's own seed, every penalty literal likewise, and for Use B every
planted contradiction value is asserted **absent** from the authority. Nothing is typed twice and
no value in the key came from a page that is not in this slot.

## 8. Material

- `seed/git/log.txt` ← git log --name-status d42ca4ea731b..58f6feea9c89 (inclusive of both), path-filtered to ollama-bench/results (`local-llm-bench git history`), 57198 chars, verbatim
