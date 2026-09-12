# v8 decisions

Numbered as they are taken, in the v7 style. Plan of record:
`results/v8/plan-2026-09-11.md`.

**D8-1 — v8 is an acceptance instrument, not a ranking one.** One scored
model, `q27-IQ2_M-96k`, the tag live as slbh's default leaf. A ceiling is an
acceptable result for a cell; a cell that cannot say go or no-go for a use is
not. Grounds: v7 scored 19/20 against a ~50% target and did not separate three
quants (`results/v7/decisions-r5-2026-09-06.md`), and the owner's ruling of
2026-09-06 puts the question at integration rather than capability.

**D8-2 — item 3 cells run single-shot, through `item3/render_prompt.py`.**
In agentic mode `peak_prompt` measures what the model *chose to open*, not
what it was handed — the D7-32 trap — so the plan's +/-15% occupancy void rule
is only meaningful single-shot. Single-shot is also the shape the production
use actually has: a transcript handed to a leaf to summarise. The agentic
reading path is item 1's, where it is the thing under test and not an
assumption.

**D8-3 — a tool-call smoke gate runs before any item 1 cell.** Nothing offline
could establish that `q27-IQ2_M-96k` emits `tool_calls` on this endpoint at
all, and the whole of item 1's 10,800 s rests on it. `run_gpu_round.sh` step 1b
runs one short `t1` trial, counts responses carrying `tool_calls`, and on zero
marks item 1 **void as designed** and skips its cells while the rest of the
round continues. The cheapest question that can void an item is asked first.

**D8-4 — the native Ollama API is the path of record, `--api native`.**
`/v1/chat/completions` ignores `options.num_ctx` and reports
`usage.prompt_tokens` rather than `prompt_eval_count`, so on that path both
the context window and the occupancy rung are unverifiable — and occupancy is
the whole of item 2. Every cell records which API it used.

**D8-5 — the desktop clone's pre-existing work was committed before any v8
phase-2 run touches it.** `15f6a33 q09 r5 fix list` (44 files, the r5 fix list
applied: the procedure page 290 -> 293 lines, the deciding offset 10,135 ->
10,088) and `c67199e m08 slot and accept tallies` (106 files) were the owner's
uncommitted work; upstream never touched those paths. 103 untracked files were
hash-identical to `origin/main` and one, `results/v7r6-accept-IQ2_M-main.md`,
was a stale local copy of a file upstream now carries; all 104 went to a stash
rather than a delete, alongside a first stash holding three superseded
partials (the desktop's `v7r6-accept-IQ2_M-main.json` had 70 runs where main
has 108). Nothing was deleted at any point.

**D8-6 — item 1's tool surface is proved, not asserted.** `verify_schemas.py`
builds a Go program inside a scratch copy of slbh and calls slbh's own
`ToolDefinitions()`, diffing against the Python snapshot: deep equal, order
identical, same sha256. `verify_executor.py` differentially tests the Python
executor against slbh's real `harness.Runtime.ExecuteTool`. Snapshot taken at
slbh HEAD `bf858c6cbebe5f21216dbb2b1d071898489daf09`, working tree clean; the
schemas are a snapshot and a later slbh commit invalidates them.

## Banked for the owner, not blocking

1. **When the GPU may be taken.** `run_gpu_round.sh` refuses without
   `--owner-ok`: the workhorse plan's automatic availability signal is a later
   phase and is not built, so there is nothing to read.
2. **Whether to promote long serial state into the committed set.** The
   hardened q09 slot is now committed at `15f6a33` and costs one n=10 cell,
   about 3,100 s. It is the only shape that has separated this model from the
   frontier arms: 1 of 3 with two confidently-wrong against four arms at 12/12.
   Recommended.

**D8-7 — the two-directional instrument proof is verified once, here, and not
re-derived by the round runner.** All three items carry it; the runner's
attempt to confirm it by matching gate *names* failed two items that pass,
because the three workers produced three different `GATES.json` shapes: item 1
has no `gates` key at all, item 2's is a list of plain strings, item 3's a list
of objects. Only `passed`, `failed`, `when` and `platform` are common, and the
preflight now reads only those. The evidence, checked directly:

- **item 1** — `GATES.md` layer 3: `perfect_1.0` and `allerrors_0.0` both `ok`
  across all six tasks; the reference scores 1.0 and the all-errors answer
  scores exactly 0.0.
- **item 2** — `G6 two-directional instrument proof`, perfect **1.0** and
  all-decoy **0.0**, 12 of 12 slots.
- **item 3** — `<slot>: abstention instrument proved in both directions` for
  each of the six slots, with `instrument=1.000` positive and `0.000` negative.

The rule this follows, having now broken it twice: **do not infer a property
from a label.** Grepping prose scored a passing item as failing once; matching
gate names did it again. A property is either checked against the evidence, or
recorded as checked — never guessed from a string.
