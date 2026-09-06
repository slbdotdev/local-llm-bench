# Round-5 authoring brief — four tasks on two shapes, 2026-09-10

*Written by the round-five manager. One author per slot, blind: you do not know who wrote the
others and you will not review your own. Read this whole, once.*

## 1. What this round is for

The material lever is exhausted. Four rounds of authoring have taken the twenty-task suite to
**96 of 100 on the 2-bit workhorse at five trials, with zero confidently-wrong answers**
(`results/v7/handoff-2026-09-09.md`). Rung 0 (make the material necessary), the coverage gate and
the grep-harvest check each moved the number by a little and none of them separated the three
quants. The owner's ruling of 2026-09-06 closes that line and opens two others.

**This round does not ask for more material. It asks for two shapes the workhorse is already
known to fail on, and the evidence for each is in this campaign's own transcripts.**

> **Shape A — long serial state.** The workhorse's real failures were losing the thread in a long
> reconciliation. `m10-main-glm` is 0 of 4 on the workhorse; `n02`, `n03` and `n04` are 1 of 3
> each; `m01-main-glm` ran its context out after 39 file reads. Read the transcripts and the
> misses are not on the first read, they are on the twentieth dependent step. A task on this
> shape requires **twenty or more ordered edits or computations, each depending on the verified
> result of the previous one**, so that an early slip propagates and is visible in the final
> deliverable. It is **not** one formula applied to many values — that is arithmetic volume and
> the model does it well. It is a chain.

> **Shape B — large correct output.** Every `stop=length` failure this campaign has recorded came
> from **output**, not input: `m10-main-glm` at 36,909 output tokens, `m01-main-glm` at 17,867,
> both `visibly_failed` with `STOP=length` while their inputs sat well inside the window. A task
> on this shape has a **large deliverable that must be internally consistent** — thirty or more
> files, or one long exact-format report — **graded exactly on the whole deliverable**, so that a
> model which stops early, drifts in format, or loses consistency across the deliverable is
> caught.

Difficulty still comes from real work: material that must be read and reconciled, a plausible
wrong course the material itself rules out, and steps that depend on the previous one. It never
comes from ambiguity, trick wording, format for its own sake, or a judgement call.
**A task must be hard to DO and never hard to UNDERSTAND.** A task Sonnet 5 fails is unfair, not
hard, and is re-reviewed before it is believed.

## 2. Read, whole, once, in this order

1. `AUTHORING-BRIEF.md` — the contract every task obeys (sections 2, 8 and 9 especially), and the
   table of the ten failure modes.
2. `r5/SPEC.md` — the spec-module contract, including `harvest_units()`, and **the round-five
   addendum at the end**, which is the only part that is new.
3. `r5/specs/EXAMPLE-p02_main_claude.py.txt` — a complete worked main-band spec that cleared
   every check of round four and was admitted to the suite.
   `r5/specs/EXAMPLE-n09_cheap_luna.py.txt` — a complete worked cheap24 spec.
4. `roundtable.md`'s three "What review actually caught" sections, and
   `results/v7/decisions-r4-2026-09-09.md`. Every defect listed there is one your candidate must
   not have. **Four of eight candidates were dropped last round**, all four because a blind
   reviewer reproduced the reference from two files or fewer, twice from zero.

Do not read another author's spec, and do not read the reviews directory.

## 3. The assignment

Family, band and mode are **fixed**. Nobody chose their own: the family is forced by the
campaign's provenance rule (the two slots of a mode are always written by different families) and
by the 40% family cap on the finished suite.

| slot | family | band | mode | shape | replaces |
| --- | --- | --- | ---: | --- | --- |
| `q06-main-luna` | luna | main | 6 | **B — large correct output** | `m06-main-glm` (workhorse 5/5) |
| `q08-main-luna` | luna | main | 8 | **A — long serial state** | `m08-main-claude` |
| `q09-main-glm` | glm | main | 9 | **A — long serial state** | `m09-main-glm` (workhorse 5/5) |
| `q08-cheap-glm` | glm | cheap24 | 8 | **B — large correct output** | `m08-cheap-glm` (workhorse 5/5) |

The failure mode your slot carries is not decoration; it is what the task must exercise:

* **mode 6 — fixing the code rather than the test.** Your large deliverable is the *fix*: the
  seed's tests are hashed and must not be edited, and a correct answer changes many source files
  so that the existing tests pass. This is also the answer to mode 6's known weakness (D7-34,
  `short-traversal`): the traceback names one file, so make the *deliverable* large rather than
  the search.
* **mode 8 — finishing.** Both mode-8 slots are this round's. The main-band one is the chain that
  must be carried to its twentieth step; the cheap24 one is the report that must be carried to
  its last row. Stopping early is exactly the failure both are for.
* **mode 9 — reading past the first screen.** The chain's later steps depend on facts that sit
  deep in long files and in long command output, never on the first screen of anything.

Bands, measured by `measure_material.py` on the built candidate:

| band | material | runs at | `BAND` | `TARGET_TOKENS` |
| --- | ---: | --- | --- | --- |
| `main` | 29,000-36,000 tokens | 64k | `"main"` | 26,000-27,000 |
| `cheap24` | 12,000-16,000 tokens | 24k | `"cheap24"` | 10,000-11,000 |

The overlay carries you the rest of the way into band.

## 4. Shape A — long serial state, in detail

`q08-main-luna` and `q09-main-glm`.

**The requirement.** The answer is produced by a chain of **at least twenty ordered steps**. Step
*k* cannot be started until step *k−1*'s result is known, and step *k−1*'s result is not stated
anywhere: it is produced by the work. An error at step 3 changes the answer at step 20.

**What makes it a chain and not a sum.** Each step must consume the previous step's *output* as
part of its own input — as the key that selects the next record, as the balance the next entry
adjusts, as the position the next instruction moves from, as the state the next event transitions.
If a solver can compute step 17 without having done steps 1 to 16, you have written arithmetic
volume and not a chain, and a reviewer will say so.

**What is forbidden.** No step may be a puzzle, an encoding, an ambiguity or a judgement call.
Every step must be a plainly stated operation on plainly stated material — the difficulty is that
there are twenty of them in a fixed order over material that has to be found. Twenty easy steps
that must all be right is the point.

**Grading.** The deliverable states the running state **after every fifth step** as well as the
final answer, each as its own scored key and its own group, so the grader records *where* the
chain broke rather than only that it did. Those keys are dependent by construction; say so in
`NOTES.md` in as many words, because the spec contract otherwise asks for independent groups.
The prompt must state the keys, their order and their format exactly and completely.

**Fairness.** The prompt states the rule of every step and the order, once, plainly. The
*material* is what has to be found; the *procedure* is never a guess. A reader who has understood
the prompt knows exactly what to do at every step and still has twenty steps of real work.

## 5. Shape B — large correct output, in detail

`q06-main-luna` (mode 6) and `q08-cheap-glm` (mode 8).

**The requirement.** The deliverable is large and must be internally consistent across the whole
of it. Two forms are allowed and both are graded exactly:

* **one long exact-format report** — at least thirty scored rows, each its own key and its own
  group, in an order the prompt fixes, whose values must agree with each other and with the
  material. This is the right form for `q08-cheap-glm`, where the context window is 24k and the
  deliverable is what fills it.
* **thirty or more files** — for `q06-main-luna`, the many source files a correct fix touches,
  declared through `editable(ctx)` and compared byte for byte against the reference, plus a small
  summary deliverable naming what was changed. Use `editable` **only where the bytes genuinely
  are the deliverable** (`r5/SPEC.md`), and state the exact required content in the prompt or make
  it fully determined by the seed's own tests. A grader strict about a rule its prompt never
  states is a defect and cost round four a candidate.

**What makes it large-correct and not just long.** Consistency across the deliverable must be
*checkable and required*: a total that must equal the sum of the rows above it, a cross-reference
that must name a row that exists, a running identifier that must not repeat, a fix in one module
that must match the constant another module imports. A deliverable of thirty independent rows is
thirty small tasks; a deliverable of thirty rows that must agree is one large one.

**What is forbidden.** Padding. Thirty rows of the same shape over thirty near-identical inputs
buys length without work, and the harvest check will fail it anyway. Length must come from the
material having thirty genuinely different things to say.

**Grading.** Exact on the whole deliverable, one group per row or per file, so a run that stops
at row 19 of 34 scores 19 and is `confidently_wrong` or `visibly_failed` rather than passing.
Check in `probes()` that a **truncated** deliverable — the correct answer cut off two thirds of
the way through — grades as a miss and not as a pass, and that a deliverable with one row's value
wrong grades as a miss. Those two cases are this round's addition to the required probe set.

## 6. Method

Work only in `/mnt/d/local-llm-bench/ollama-bench/results/v7/authoring`. It is a slow Windows
mount: read files with `cat` or `sed -n` on a named path, never a recursive `find`, never
`grep -r` over the repository, and **never run `git` at all**.

1. Write `r5/specs/<slot with underscores>.py`, e.g. `r5/specs/q08_main_luna.py`, following
   `r5/SPEC.md` exactly. Module constants first, then the functions in the order the contract
   lists them. `facts()` and `harvest_units()` both compute their values by **reading `seed/`
   back from disk** and assert their own arithmetic. *A reference that asserts a fact the
   material does not state is this benchmark's most expensive defect and it has happened twice.*
   For a chain, `facts()` walks the chain itself and asserts the length of it.
2. Build and check, from the authoring directory, running each of these **once** when you believe
   the spec is finished, and again only after a fix:

       python3 r5/build.py <slot>
       python3 cand-<family>/<slot>/selfcheck.py
       python3 probe_candidate.py cand-<family>/<slot>
       python3 probe_idempotence.py cand-<family>/<slot>
       python3 measure_material.py cand-<family>/<slot>
       python3 r5/check_rung0.py cand-<family>/<slot>
       python3 r5/check_index_leak.py <slot>
       python3 r5/check_load_bearing.py cand-<family>/<slot>
       python3 r5/check_harvest.py cand-<family>/<slot> --verbose
       python3 r5/check_tools.py cand-<family>/<slot> --verbose

   All must be clean and the measured material must be in band before you report.
3. Write nothing outside `r5/specs/<your slot>.py`; the builder writes `cand-<family>/<slot>/`
   for you. Never touch another slot, `suite/`, `r2/`, `r3/`, `r4/`, or any file under
   `results/` other than through the builder.

## 7. The traps, as instructions

Every one of these is a defect that has already killed a candidate in this campaign.

- **No tool in the seed may print the answer, or the material the answer reconciles.**
  `r5/check_tools.py` is new this round and it runs every executable file in your seed with no
  arguments and fails you if any of them prints a scored value, or the decisive datum of more
  than a quarter of your declared units. `p09-main-luna` was dropped for exactly this: its
  `README.md` told the solver to run `tools/retention_audit.py`, which printed all nineteen
  regions' verified dates and windows, and a reviewer reproduced the whole reference **with no
  file opened**. A helper validates an input the solver supplies; it never computes the result.
  Run the check before you report, not after a reviewer finds it.
- **Under five files is a rung-0 failure.** Produce your own deliverable from as few files as you
  can before you report it, and say in `NOTES.md` how few you managed and why it is not fewer.
- **The prompt never names the file that holds the answer**, and no single word of `prompt.md`
  may grep to exactly one load-bearing file. The only `named_in_prompt` load-bearing entry is a
  roster of units, if the task needs one.
- **The index leak.** The generated tree writes each stage's `limit` and `window_s` into five
  agreeing artifacts, two of which list every stage in one small file. Your decisive per-unit
  datum is one the generator does not replicate.
- **The vacuous declaration.** `harvest_units()` is your own word about which per-unit datum is
  decisive. A declared value that cannot occur under `seed/` by construction makes H1-H4
  structurally zero, and `check_harvest.py` now prints **`vacuous`** rather than `0.000` when
  every declared unit is derived. Vacuous is not passed: a reviewer will verify the claim by
  hand, and three candidates last round declared composites that re-measured at H1 = 1.000.
  Declare the decisive datum **alone**, one entry per datum.
- **Every claim in `NOTES.md` is a build-time measurement**, never an estimate. Four pages across
  rounds three and four stated a line number or a count the built candidate did not bear out.
- **A correction must never state the delta** in units a solver can apply arithmetically to a
  stale total.
- **`sweep_paths()` should cover 60-80% of the material**; a sweep of 30% has not cleared rung 0.
  `load_bearing()` needs at least six paths and three distinct hops, and
  `check_load_bearing.py`'s **floor coverage should be about 25% or more**.
- **The five perturbations of `probes()` case 5 all pass** — no trailing newline, two trailing
  newlines, CRLF, one leading blank line, trailing spaces — or the grader is defective, unless
  the prompt states the formatting exactly and `NOTES.md` says so in as many words.
- Difficulty is never format, never ambiguity, never a judgement call.
- **`python` is not on the sandbox's path. Write `python3`.**

## 8. Report

When the checks are clean, reply with: the slot; the row `build.py` printed (tokens, files,
load-bearing count, hops, sweep tokens, coverage %); the measured band; the H1/H2/H3/H4 that
`check_harvest.py` printed, or `vacuous` and why; the line `check_tools.py` printed; the floor
coverage from `check_load_bearing.py`; **for shape A, the number of steps in the chain and how
step *k* consumes step *k−1*'s output**; **for shape B, the size of the deliverable and the
consistency constraint that ties it together**; the fewest files your own best shortcut needed
and what it scored; where you departed from this brief and why; and anything you are unsure of.
Nothing else.
