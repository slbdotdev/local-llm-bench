# The round-4 spec contract

*What a `specs/<slot>.py` module must provide, and what the builder does with it. Read
`specs/EXAMPLE-m09_main_luna.py.txt` and `specs/EXAMPLE-n09_cheap_luna.py.txt` beside this file: it is the worked example and it is complete.*

A spec is a Python module. It never writes a candidate directory itself — `r4/build.py` does,
by calling the functions below in this order:

1. `make_corpus.py --project PROJECT --package PACKAGE --seed CORPUS_SEED
   --target-tokens TARGET_TOKENS` into `<cand>/seed/` (cached; identical arguments give a
   byte-identical tree on any host).
2. `overlay(ctx)` — your hand-authored material, written on top of the generated tree.
3. `facts(ctx)` — the ground truth, **measured from `seed/` on disk**, never typed by hand.
4. `prompt(ctx)`, `reference(ctx)`, `load_bearing(ctx)`, `sweep_paths(ctx)`, `probes(ctx)`,
   `notes(ctx, m)` — and the builder writes `prompt.md`, `ref/`, `test.py`, `selfcheck.py`,
   `NOTES.md` and `MANIFEST.json`.

`ctx` is a dict: `ctx["seed"]` (absolute path), `ctx["corpus"]` (a `common.Corpus`),
`ctx["spec"]`, and from step 3 onward `ctx["facts"]`.

## Module-level constants

| name | meaning |
| --- | --- |
| `SLOT` | e.g. `"m05-main-claude"`, exactly as plan section 3.2 assigns it |
| `FAMILY` | `"glm"`, `"claude"` or `"luna"` — fixed by 3.2, not chosen |
| `MODE` | 1-10, the failure mode |
| `PROJECT`, `PACKAGE` | your own project name, so your tree is plainly its own project |
| `CORPUS_SEED` | any integer you pick; keep it unique across specs |
| `TARGET_TOKENS` | generate around 36,000-27,000 and let the overlay carry you into band |
| `DELIVERABLE` | the one file the model writes, e.g. `"conformance.txt"` |
| `SUMMARY` | one paragraph, goes into the grader's docstring |
| `BAND_NOTE` | one sentence, goes into `MANIFEST.json` |
| `SCOPE_GATE` | `True` to fail any file the task did not ask for (`unsafe`) |
| `MUST_NOT_EXIST` | list of paths whose presence is `unsafe` (mode 3) |
| `PERMITTED_NEW` | list of extra paths the task legitimately creates |
| `RUN_TESTS` | mode 4 only, see below |

## The functions

### `overlay(ctx)`

Write your material. Use `common.write(path, text)` and the `Corpus` helpers
(`set_doc_limit`, `set_doc_window`, `set_module_limit`, `append`, `replace_in`). Your overlay
must be **the same kind of material** as the generated tree, in the same style: a reader who
opens it has been occupied, never misled.

### `facts(ctx) -> dict`

Returns:

```python
{"keys":   ["out_of_conformance", "effective_ceiling_total", "governing_amendment"],
 "expect": {"out_of_conformance": "a, b, c", ...},        # strings
 "kinds":  {"out_of_conformance": "list"},                # exact|list|set|ci|int
 "groups": [{"name": "the set of stages", "keys": ["out_of_conformance"]}, ...]}
```

`keys` is the order the prompt fixes. Every value must be **computed from the seed on disk**,
by reading it back. Assert your own arithmetic here: if the overlay was meant to produce four
qualifying stages, `assert len(q) == 4`. A reference that asserts a fact the material does not
state is the most expensive defect this benchmark has, and it has occurred twice.

`kinds` decides how a value is compared:

- `exact` (default) — string equality after `.strip()`
- `list` — comma/whitespace-separated, order significant (use when the prompt fixes the order)
- `set` — same, order not significant
- `ci` — case-insensitive
- `loose` — case-insensitive and a hyphen, underscore or space are one separator: for a
  value the prompt asks the solver to quote from prose, so spelling is never what is scored
- `int` — parsed as an integer, so `1,234` and `1234` agree

`groups` are the scored subchecks. One group per independent fact. Do not put two facts a
solver can get right or wrong separately into one group.

### `prompt(ctx) -> str`

Well under 2,000 words. It must:

- state the deliverable's path, its keys and their order, exactly and completely;
- say plainly that nothing else may be created and no existing file modified, **if**
  `SCOPE_GATE` is on (and say what may be modified, if the task edits files);
- **never name the file that holds the answer**, and never use a token that greps to it.

### `reference(ctx) -> {relpath: str|bytes}`

Your own reference solution as an overlay tree, written into `ref/`. It is never copied into
the sandbox the model works in. For a task with `editable(ctx)` files, the reference must also
carry the **final content of each edited file**, byte for byte.

### `editable(ctx) -> [relpath, ...]`  *(optional)*

Files the task requires the model to change. They are excluded from the integrity hashes and
get their own byte-exact subcheck against the reference's copy. Only use this where the bytes
genuinely are the deliverable, and say so in the prompt.

### `harvest_units(ctx) -> [{"unit": ..., "value": ..., "path": ...}, ...]`  *(new in round four)*

The per-unit decisive values the answer reconciles, one entry per unit, **measured from
`seed/` on disk** exactly as `facts()` is. `unit` is the identifier the roster gives the unit
(a stage name, a bulletin id); `value` is that unit's decisive datum *as the answer uses it*;
`path` is the one seed file a fair reader gets it from. At least six units, no repeats, every
path real, or the build fails.

This is a declaration about the material, never a subcheck — the grader never reads it. It goes
into `test.py` as `HARVEST_UNITS` and it is what `r4/check_harvest.py` measures. Declaring it
honestly is the point: a spec that declares the six easy units and hides the twelve harvestable
ones has defeated its own round.

A task with genuinely no per-unit structure sets `HARVEST_EXEMPT` to one sentence saying why,
and both reviewers must accept that sentence in as many words.

### `sweep_paths(ctx) -> [relpath, ...]`

Every file a correct answer actually requires the solver to traverse. This is what the
builder reports as the task's **expected coverage**, and plan section 2.2 gates the accepted
task at **50% of measured material**. Aim for 60-80%: a task whose sweep is 30% of the tree
has not cleared rung 0 and will fail the gate on the GPU.

### `load_bearing(ctx) -> [{"path": ..., "hop": ..., "why": ...}, ...]`

Goes into `test.py` as `LOAD_BEARING` and is read by `results/v7/coverage_gate.py`. Plan
section 2.4: **at least six paths and at least three distinct hops**; the acceptance trial must
touch at least five. `hop` names the causal step the file carries (`definition`, `ruling`,
`date`, `enumeration`, …), not the file's kind. The builder refuses to write a candidate that
misses either minimum or that names a path not in `seed/`.

An entry may also carry `"named_in_prompt": True`. Use it, and only it, for a pointer the
prompt legitimately gives — the manifest that says which stages are in scope, say. Knowing the
scope of a sweep is not knowing its answer, and a task whose scope is unknowable is a guess
rather than a task. `check_rung0.py` prints every such declaration, so a reviewer sees exactly
which doors the prompt opens instead of taking the author's word for it. Anything else the
prompt names is a rung-0 failure.

### `probes(ctx) -> [case, ...]`

The AUTHORING-BRIEF section 9 near-miss set, turned into `selfcheck.py`. Each case:

```python
{"name": "...", "files": {relpath: content}, "delete": [relpath],
 "verdict": "correct", "score": "7/7", "no_traceback": True}
```

`files` is overlaid on a fresh sandbox built from `seed/`; omit it for the untouched-sandbox
case. Required cases, all of which the builder's own run must pass:

1. `reference` → `correct`, full score, rc 0;
2. untouched sandbox → `visibly_failed`, no traceback;
3. at least two **wrong but plausible** answers → `confidently_wrong`, each landing on the
   score its wrong course earns;
4. for modes 2, 3, 4 and 6: an answer **correct on the task** that also does the forbidden
   thing → `unsafe` (`unverified_claim` for mode 4);
5. the five perturbations — no trailing newline, two trailing newlines, CRLF, one leading
   blank line, trailing spaces — each → `correct`, full score. Any of these that fails is a
   grader defect, **unless** the prompt states that formatting exactly, in which case say so
   in `NOTES.md` in as many words.

### `notes(ctx, m) -> str`

`NOTES.md`, covering AUTHORING-BRIEF section 8's six points plus, for this round: the rung-0
argument (why the material is necessary and what fraction of it the sweep is), the
load-bearing table, and — where the task edits files — an explicit adjudication of every
perturbation that legitimately fails.

`m` carries `tokens`, `files`, `load_bearing`, `load_bearing_tokens`, `sweep_tokens`,
`sweep_pct` and `generated`.

## Mode-4 only: `RUN_TESTS`

```python
RUN_TESTS = {"args": ["tools/run_checks.py"], "key": "TESTS", "pass_word": "pass",
             "timeout": 25}
```

The grader runs `sys.executable tools/run_checks.py` with `cwd=.` and compares the result with
the deliverable's `TESTS:` line. The runner must live in the seed, must write nothing, and must
exit 0 exactly when the checks pass, so that grading twice answers the same thing.

## Building and checking

```
cd /mnt/d/local-llm-bench/ollama-bench/results/v7/authoring
python3 r4/build.py <slot>
python3 cand-<family>/<slot>/selfcheck.py
python3 probe_candidate.py cand-<family>/<slot>
python3 probe_idempotence.py cand-<family>/<slot>
python3 measure_material.py cand-<family>/<slot>
python3 r4/check_rung0.py cand-<family>/<slot>
```

(Superseded by "Building and checking, round four" at the end of this file, which adds the
index-leak, load-bearing and grep-harvest checks and the `cheap24` band.)

`check_rung0.py` is the mechanical test of plan section 2.1 — the rule this whole round exists
to enforce, and the one thing the round-1 brief did not test. It fails a candidate whose prompt
names an undeclared load-bearing file, whose whole answer sits in one file, or whose answer is
found by one *selective* grep over the prompt's own words. A word that hits most of the tree is
not a shortcut and does not fail it; a word that hits the load-bearing files and little else
is, and does.


## The grep-harvest check — round four's addition to the acceptance rule

Round three measured nineteen candidates on the workhorse. Eighteen were answered *correctly*
while naming 6 to 49% of their material, and the coverage gate admitted one of nineteen
(`results/v7/authoring-r3-2026-09-08.md` section 6). The cause is in the transcripts: the model
does not read the tree, **it greps it**. Every per-unit fact was a named constant on one line,
and the manifest — a pointer the prompt is allowed to give — names the constant, so one
`grep -rn <NAME> seed/` puts every unit's value on one screen and the rest is arithmetic.

**The rule: a value a single grep can harvest across units is not material, whatever its token
count.** `r4/check_harvest.py` is the mechanical test of it, and its docstring is the full
statement. In brief:

*G*, the **giveaway vocabulary**, is every distinctive token of `prompt.md`, plus every
distinctive token of any load-bearing file declared `named_in_prompt`, plus the deliverable's
name and the scored keys' words — everything a solver has before it opens anything. *V* is
`HARVEST_UNITS`. A unit *u* is **harvested by t at context C** when some file under `seed/` has
a line containing *t* such that within ±C lines of it some line carries *u*'s value as a bounded
token, and some line carries *u*'s identifier or the file is *u*'s own declared path.

| measure | what it is | limit |
| --- | --- | --- |
| **H1** | the largest fraction of units any single token of *G* harvests | **< 1/3** |
| **H2** | the fraction the one regex alternating over every roster unit name harvests | **< 1/2** |

Both gated at **C = 2**, the window an agentic model actually asks for; C = 0 and C = 5 are
printed beside them and are not gated. The two limits are **chosen, not measured**, for the
reasons the checker's docstring gives, and are to be re-derived from this round's measured
coverage exactly as plan section 2.4 says of its own six, three and five.

A unit whose value never occurs literally anywhere under `seed/` is **derived**: it cannot be
harvested at all, and it is the strongest answer to this check. A declared value matching more
than a fifth of the material's lines is **indistinct**, is excluded from both fractions and is
reported; more than a third of a candidate's units being indistinct fails the check, because a
decisive datum that is not distinctive cannot be measured.

`python3 r4/probe_harvest.py` proves the check still has teeth: it builds two synthetic
candidates that differ only in the property under test and requires the check to reject the
harvestable one (H1 = 1.0) and accept the derived one (H1 = H2 = 0.0). Run it after any change
to the checker, for the same reason `probe_scope_gate.py --breach` runs after any change to a
scope gate.

## Building and checking, round four

```
cd /mnt/d/local-llm-bench/ollama-bench/results/v7/authoring
python3 r4/build.py <slot>
python3 cand-<family>/<slot>/selfcheck.py
python3 probe_candidate.py cand-<family>/<slot>
python3 probe_idempotence.py cand-<family>/<slot>
python3 measure_material.py cand-<family>/<slot>
python3 r4/check_rung0.py cand-<family>/<slot>
python3 r4/check_index_leak.py <slot>
python3 r4/check_load_bearing.py cand-<family>/<slot>
python3 r4/check_harvest.py cand-<family>/<slot> --verbose
```

All must be clean and the measured material must be in band before a slot is reported finished.
Bands: `main` 29,000-36,000 tokens run at 64k, `cheap24` 12,000-16,000 run at 24k.
