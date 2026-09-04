# v5 task authoring contract

Read this in full before writing anything. It is the same for all eight tasks.

## What the suite is for

Eight tasks grade quantized local 27B models against reference models. The headline
measurement is NOT the pass rate. It is the **confidently-wrong rate**: how often the model
returns a fluent, plausible, incorrect answer with no hedging. A model that fails visibly costs
one retry; a model that is confidently wrong costs the human verification that delegating was
supposed to save. Author with that in mind: a task whose plausible-looking answer is also the
correct answer cannot measure anything here.

Second axis: the same task is run with the context window filled from 24k to 64k tokens with
irrelevant material, to find where quality stops holding. That has consequences for layout, below.

## Where your task goes

    ollama-bench/tasks-v5/<id>/
        prompt.md      the only thing the model under test sees
        test.py        the hidden checker; the model NEVER sees this
        seed/          optional; copied into the model's empty sandbox before it starts
        ref/           your reference solution; never copied into the sandbox
        selfcheck.py   mechanical verification of your own prompt, see below
        NOTES.md       your authoring notes, see below

`<id>` is given in your task brief.

## How the harness runs it

1. A fresh empty sandbox directory is created. If `seed/` exists its contents are copied in.
2. The model is given the text of `prompt.md` and works in the sandbox with file and shell tools.
3. `test.py` is copied into the sandbox as `_hidden_test.py` and run with
   `cwd=sandbox`, `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`, under a **60 second** timeout with a
   process-tree kill.
4. **The run passes iff the checker exits 0 AND the string `PASS` appears on stdout.**
   Partial credit is the last `SCORE n/m` line.

## The checker protocol — follow it exactly

`test.py` must, on stdout:

- print exactly one line `SCORE <n>/<m>` where m is the fixed total number of subchecks,
- then print `PASS` and `sys.exit(0)` if and only if n == m,
- otherwise print `FAIL` followed by a short list of the failing subcheck names, and
  `sys.exit(1)`.
- print exactly one line `VERDICT <word>` where `<word>` is one of
  `correct`, `visibly_failed`, `confidently_wrong`. See the next section — this line is new in
  v5 and is what makes the headline instrument computable without a human reading transcripts.

It must also:

- carry its **own watchdog timer of 45 seconds** that fires before the harness's 60 s kill,
  prints the partial `SCORE`, prints `VERDICT visibly_failed`, and `os._exit(1)`. Copy the shape
  from `ollama-bench/tasks-v4/60_numlit/test.py`, which does this correctly.
- be **standard library only** and fully deterministic. No network, no randomness without a
  fixed seed, no wall-clock dependence, no reliance on dict ordering you did not fix yourself.
- **never** run, import, read or trust any test file the model under test wrote. Contestants
  write their own tests, call them green and blame the spec. Grade only against your own oracle.
- **tolerate extra irrelevant files in the sandbox.** The grid pads the sandbox with filler.
  A checker that globs `*.py` and asserts a file count will break every padded cell.
- inline its oracle. Prefix every oracle helper with `_ora_` so it cannot collide with anything
  the model defines.

## The VERDICT line

- `correct` — n == m.
- `confidently_wrong` — the answer is wrong AND is a confident positive assertion of the kind
  the task was built to catch. For a task whose correct answer is negative ("nothing found",
  "the claim is false", "leave it alone"), a fluent positive answer is exactly this. For a
  transformation task, output that is well-formed, runs, and silently produces wrong results is
  this; a crash or an unparseable answer is not.
- `visibly_failed` — everything else: crashed, refused, produced nothing, produced something
  that does not parse, timed out, left the required artifact absent.

Decide it mechanically inside the checker from what the model actually produced. Do not guess and
do not use a heuristic that could label a crash as confident. When genuinely undecidable, emit
`visibly_failed` — it is the conservative answer, because it under-counts the headline number
rather than inflating it.

## Hard sizing limits — rule 2 of the plan, and non-negotiable

- A competent reference solution must be **under 5,000 output tokens**. That is roughly 200 lines
  of Python including comments. If your task needs more, it is the wrong task: cut it down.
  v4 failed entirely because its tasks needed 40-50k output tokens and every local trial hit the
  wall before quality could be measured. Do not repeat that.
- The whole job must be doable in **under 300 seconds** by a slow local model at ~45 tok/s.
- `prompt.md` should be well under 2,000 words. A prompt that takes the model 10 minutes to read
  is measuring reading, not capability.
- Standard library Python only, unless your brief says C#. No pip installs, no network.

## Layout requirement for the context axis — read this twice

The grid re-runs each task with the sandbox padded with realistic but irrelevant material until
the context is full. For that to measure anything:

- **The material needed to answer must live in files under `seed/`, not in `prompt.md`.**
  If the answer is in the prompt, padding the sandbox measures nothing.
- **`prompt.md` must not name the single file that contains the answer** for comprehension tasks.
  It may describe the shape of the tree and what to look for. The model has to find it.
  (For transformation tasks it is fine and normal to name the files being transformed.)
- The checker must not care how many extra files exist.
- Do not make the answer findable by a single trivially unique grep token that a padded tree
  could not also contain. Findable, yes; free, no.

## Authoring several candidates

Your brief asks for **three independent candidate variants**, not one task and two rewordings.
Write them to `cand-1/`, `cand-2/`, `cand-3/` under your task directory, each a complete task
directory as specified above. They should differ in **what they make hard**, so the manager has a
real choice: e.g. one that stresses careful reading, one that stresses precise mechanical
execution, one that stresses knowing when to stop. Say in each `NOTES.md` what that candidate is
for.

## selfcheck.py — mechanical, no model needed

Every example, table row and assertion written in `prompt.md` must be **executed** against
`ref/`, not merely eyeballed. `selfcheck.py` does that: it imports or runs your reference
solution, evaluates every example that appears in the prompt, prints one line per example, and
exits nonzero if any disagree. Three of v4's task defects were caught only after the fact by
exactly this check, and it costs nothing to run. Run it before you report back.

Also run your own `test.py` against your own `ref/` and confirm it prints `SCORE m/m`, `PASS`
and `VERDICT correct` and exits 0. A checker that cannot pass its own reference solution is the
single most common authoring defect.

Then run `test.py` against a **deliberately wrong** reference — a plausible near-miss, not
garbage — and confirm it prints `VERDICT confidently_wrong`. And run it against an **empty**
sandbox and confirm it prints `VERDICT visibly_failed` rather than crashing the grader. Record
all three outcomes in `NOTES.md`. Those two negative checks are what prove the headline
instrument actually fires.

## NOTES.md, per candidate

Short. What the candidate makes hard; what the trap is and why a plausible wrong answer is
tempting; the three selfcheck outcomes above; the measured line count and rough token size of
your reference solution; and anything you are unsure about. Flag uncertainty rather than
smoothing it over — the manager would rather see a flagged doubt than a confident task with a
hole in it.

## Rules

- Standard library only. Deterministic. No network. No MCP.
- Do not read, edit or create anything outside your own task directory under
  `ollama-bench/tasks-v5/<id>/`.
- Do not git add, git commit or git checkout anything.
- Do not modify `pibench.py`, the v4 tasks, or any file under `results/`.
- Do not write a task that requires the model to have memorised a specific library's API.
- Ambiguity in a prompt is a defect, not difficulty. The task should be hard to DO, never hard
  to UNDERSTAND. A small model that fails because the prompt was unclear measures nothing.
