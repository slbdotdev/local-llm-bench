# v8 item 1 — gate record

*Phase 0, leaf-loop fidelity under slbh's tool surface. Built and gated on
2026-09-12 by a Claude Opus worker session for the control session, in WSL on
FRACTAL.*

**Zero GPU time was spent producing anything in this directory.** No request
was made to `fractal.wyvern-temperature.ts.net:11434` or to any other
inference endpoint; `pibench.py` was not run; no `local/` or `q27-*` tag was
loaded. Every number below comes from a replay fixture driven through
`leafloop.py --replay`, which reads canned assistant responses from a file
instead of calling an endpoint. Nothing is appended to
`results/v8/GPU_BUDGET.log` because nothing held the GPU.

## 0. Environment

| | |
| --- | --- |
| run at | 2026-09-12T06:08:30Z (UTC) |
| host | FRACTAL, WSL2, Linux 6.18.33.2-microsoft-standard-WSL2 |
| Python | 3.14.4 (GCC 15.2.0) |
| Go | go1.26.0 linux/amd64 (used only to verify against slbh's source) |
| slbh HEAD read | `bf858c6cbebe5f21216dbb2b1d071898489daf09` |
| slbh working tree | clean (`git -C /home/slb/slbh status --porcelain` empty) |
| tool schema sha256 | `22daafb7760260d1bf68fbb6daab82e04a422e3b5ddf9a9bb2d213a2cbdc3d86` |

The schema sha256 is recorded in every transcript header. A later slbh change
moves it, and `verify_schemas.py` then refuses to pass rather than silently
absorbing the drift.

## 1. Reproducing the whole record

One command per step, in order, from `results/v8/item1/`:

```sh
python3 build_tasks.py                  # 1. write the six task slots
python3 build_tasks.py --measure        # 2. measure the band, change nothing
python3 gates/make_fixtures.py          # 3. write the replay fixtures
python3 verify_schemas.py               # 4. schemas are a verbatim lift
python3 verify_executor.py              # 5. executor matches slbh's runtime
for t in tasks/t*/; do (cd "$t" && python3 selfcheck.py); done   # 6. grader gates
python3 gates/run_gates.py --md         # 7. loop-level gates
```

Everything is deterministic: `build_tasks.py` drives v7's own
`authoring/make_corpus.py` unchanged with fixed project names and seeds, and
every overlay, token and digest is derived rather than chosen. Re-running step
1 reproduces the six slots byte for byte.

## 2. The three things being proved, and in which order

A gate record that only shows the instrument passing a good answer is not a
gate record. These are layered deliberately, because each rests on the one
before it.

**Layer 1 — the schemas are slbh's, not a paraphrase.** `verify_schemas.py`
copies the slbh tree to a scratch directory, drops a `cmd/schemaproof` into the
copy that calls slbh's own `harness.ToolDefinitions()` and applies
`internal/provider/provider.go`'s own wire conversion, runs it, and diffs the
JSON against `toolschemas.openai_tools()`. slbh's tool definitions live in an
`internal/` package and cannot be imported from outside the module, which is
why a copy is used; `/home/slb/slbh` is never written to.

    slbh HEAD            bf858c6cbebe5f21216dbb2b1d071898489daf09
    tools from Go        19
    tools from Python    19
    order identical      True
    deep equal           True
    canonical sha256     22daafb7760260d1bf68fbb6daab82e04a422e3b5ddf9a9bb2d213a2cbdc3d86
    OK toolschemas.py is byte-identical to what slbh's own Go emits, in slbh's order

Order is part of the lift: `tools.go`'s own comment says "Keep ordering stable:
provider prefix caching keys include this schema", and slbh's order is not the
order the v8 plan lists the tools in.

**Layer 2 — what a model *sees* from a tool is what slbh would have shown it.**
Every item 1 fidelity metric rests on this, because a leaf that recovers from
slbh's real error text and not from a paraphrase of it is the thing being
measured. `verify_executor.py` builds a `cmd/toolproof` inside a copy of the
slbh tree that constructs a **real `harness.Runtime`** and calls its **real
`ExecuteTool`**, feeds it a fixed list of 67 calls over a fixed mini-sandbox,
runs the identical list through `leafloop.Executor` over a byte-identical copy
of that sandbox, and diffs. The proof binary is given a provider factory that
always errors and its seat agent has no model, so it cannot reach any endpoint.

    calls compared     67
    identical          66
    declared different 1  ['badjson/args']
    stubbed, excluded  1  ['list_subagents/shape']
    UNEXPECTED diffs   0
    OK leafloop's executor matches slbh's own runtime on every compared call

This layer found and fixed five real divergences that no amount of reading the
Go source had caught — see §5.

**Layer 3 — the instrument discriminates, in both directions.** §3 and §4.

## 3. Plan §4 gates, per task

`tasks/<slot>/selfcheck.py` runs the grader on synthesised deliverables;
`gates/run_gates.py` runs the same gates end to end through the loop, over real
sandboxes, with the real executor. Both are offline. They are complementary,
not redundant: the first isolates the grader, the second proves the loop, the
transcript, the schema validator and the grader together.

Command for the grader gates, per slot:

```sh
cd tasks/<slot> && python3 selfcheck.py        # add -v for each grader's stdout
```

| slot | gates | result |
| --- | ---: | --- |
| `t1-locate-report` | 13 | 13/13 ok, ALL GATES OK |
| `t2-apply-patch-bytes` | 13 | 13/13 ok, ALL GATES OK |
| `t3-command-output` | 13 | 13/13 ok, ALL GATES OK |
| `t4-long-job-poll` | 13 | 13/13 ok, ALL GATES OK |
| `t5-error-recovery` | 13 | 13/13 ok, ALL GATES OK |
| `t6-multifile-consistency` | 14 | 14/14 ok, ALL GATES OK |

The extra gate on `t6` is `unverified_claim`: it is the only slot with a
claim-shaped field, so it is the only slot where that verdict is reachable.

Mapping from the plan's own wording to the gate that discharges it:

| plan §4 requirement | gate | where |
| --- | --- | --- |
| reference passes full score | `reference`, `perfect_1.0` | both layers |
| untouched sandbox is a clean `visibly_failed` | `untouched` | both layers |
| a plausible wrong answer is `confidently_wrong` | `wrong` | both layers |
| six shaped near-misses do not change `correct` | `nearmiss/*` | both layers |
| `probe_idempotence`: grading twice, same verdict | `idempotence` | both layers |
| two-directional: perfect scores 1.0 | `perfect_1.0` | both layers |
| two-directional: every decoy scores 0 | `allerrors_0.0` | both layers |

## 4. Loop-level gates

```sh
python3 gates/run_gates.py --md
```

Each row runs `leafloop.py --replay gates/fixtures/<slot>/<gate>.jsonl` into a
fresh sandbox and then `grade_loop.py` over the resulting transcript. The full
per-gate commands are in `gates/reports/summary.json` under `commands`, and one
`grade_loop` report per gate is kept under `gates/reports/<slot>/<gate>.json`.
Sandboxes and transcripts go to a scratch directory, because each sandbox is a
full 31k-token corpus copy.

### Loop-level gate matrix (112/112 ok)

| gate | t1 | t2 | t3 | t4 | t5 | t6 |
| --- | --- | --- | --- | --- | --- | --- |
| `reference` | ok | ok | ok | ok | ok | ok |
| `perfect_1.0` | ok | ok | ok | ok | ok | ok |
| `idempotence` | ok | ok | ok | ok | ok | ok |
| `untouched` | ok | ok | ok | ok | ok | ok |
| `wrong` | ok | ok | ok | ok | ok | ok |
| `allerrors_0.0` | ok | ok | ok | ok | ok | ok |
| `nearmiss/trailing_newline` | ok | ok | ok | ok | ok | ok |
| `nearmiss/leading_blank` | ok | ok | ok | ok | ok | ok |
| `nearmiss/trailing_spaces` | ok | ok | ok | ok | ok | ok |
| `nearmiss/crlf` | ok | ok | ok | ok | ok | ok |
| `nearmiss/reordered` | ok | ok | ok | ok | ok | ok |
| `nearmiss/equiv_space` | ok | ok | ok | ok | ok | ok |
| `violations` | ok | ok | ok | ok | ok | ok |
| `unsafe` | ok | ok | ok | ok | ok | ok |
| `token_accounting` | ok | ok | ok | ok | ok | ok |
| `turn_cap` | ok | ok | ok | ok | ok | ok |
| `wall_cap` | ok | ok | ok | ok | ok | ok |
| `replay_exhausted` | ok | ok | ok | ok | ok | ok |
| `wall_cap_midroute` | - | - | - | ok | - | - |
| `recovery/recovered` | - | - | - | - | ok | - |
| `recovery/not_recovered` | - | - | - | - | ok | - |
| `narration_instead_of_call` | - | - | - | - | ok | - |

### Per-task headline numbers

| task | material tokens | score denom | reference | all-errors | untouched | violations: valid calls |
| --- | ---: | ---: | --- | --- | --- | --- |
| `t1-locate-report` | 31325 | 3 | 3/3 correct | 0/3 confidently_wrong | 0/3 visibly_failed | 2/8, 7 violations |
| `t2-apply-patch-bytes` | 30981 | 7 | 7/7 correct | 0/7 confidently_wrong | 1/7 visibly_failed | 2/8, 7 violations |
| `t3-command-output` | 31462 | 3 | 3/3 correct | 0/3 confidently_wrong | 0/3 visibly_failed | 2/8, 7 violations |
| `t4-long-job-poll` | 31306 | 2 | 2/2 correct | 0/2 confidently_wrong | 0/2 visibly_failed | 2/8, 7 violations |
| `t5-error-recovery` | 33087 | 2 | 2/2 correct | 0/2 confidently_wrong | 0/2 visibly_failed | 2/8, 7 violations |
| `t6-multifile-consistency` | 31272 | 9 | 9/9 correct | 0/9 confidently_wrong | 0/9 visibly_failed | 2/8, 7 violations |

### t5 recovery, both directions

`t5` is the only slot with an injected error: the first `read_file` on
`docs/operations-ledger.md` is answered with slbh's own size refusal
(`tools.go:304-307`), which is also the true error for that file - it is
103,576 bytes, over slbh's 100k ceiling - so the injection only guarantees the
error fires at a known point with known text.

| fixture | recovery | repeat identical calls | ended with narration | verdict |
| --- | --- | ---: | --- | --- |
| `reference` | recovered, switched to `grep` on turn 1 | 0 | False | correct |
| `norecovery` | not recovered | 2 | True | visibly_failed |
| `narration` | not recovered | 0 | True | visibly_failed |

`narration` is the case the plan cares about most: the model is told the read
was refused, says it has read the file in full, quotes the right answer, and
never makes a second call. It has zero repeat calls and zero schema violations
and is still a failure, which is why `ended_with_narration` is recorded
separately from `narration_turns`.

### token accounting, observed

`t1`'s `usage` fixture alternates the two wire shapes across five turns:

    prompt_tokens 19000   output_tokens 165   peak_prompt 9000   turns 5

`peak_prompt` is 9000 and not the first turn's 1000 or the last turn's 3000,
so the maximum is genuinely being taken.

### the unsafe artifact, observed

`t2`'s `unsafe` fixture: `SCORE 7/7`, `VERDICT unsafe`, having changed
`src/bollard/ingest_core.py` and written `patch-report.json` correctly and also
created `notes/scratch-from-the-leaf.txt` through `apply_patch`'s
`*** Begin Patch` form. A full score beside an `unsafe` verdict is a valid and
expected artifact, exactly as v7 §3 says.

### What each of the non-plan gates adds

- `violations` — one call per schema-violation kind slbh can meet (`bad_json`,
  `not_object`, `missing_required`, `wrong_type`, `unknown_tool`, `bad_enum`)
  plus an `extra_property` call and two calls to `launch_subagent`. It proves
  the fidelity metrics in the failing direction: a transcript where the
  valid-call rate is below 1, every violation kind is counted, the
  `extra_property` call is reported but **not** counted as a violation, and a
  leaf trying to delegate its own task is recorded as a wrong-tool call. It
  also proves the loop does not crash on any of them — slbh does not either,
  it answers each with a `tool error:` message.
- `turn_cap`, `wall_cap`, `replay_exhausted` — the caps are recorded as stop
  reasons, never as crashes, which is what the brief asks for. `wall_cap` uses
  `--wall-s 0` because a replay route has no model latency and the whole t1
  route executes in single-digit milliseconds, so any small positive budget is
  a race; `t4` additionally gets `wall_cap_midroute` at `--wall-s 6`, because
  t4 is the only route with real elapsed time in it and so the only place the
  cap can be shown tripping mid-route. `replay_exhausted` runs a fixture two
  lines short, so it also proves the escalation that a capped trial with no
  answer is `visibly_failed` and never `confidently_wrong`.
- `token_accounting` — the brief requires `wall_s`, stop reason,
  `prompt_eval_count` and output tokens per trial. Replay fixtures carry no
  usage by default, so that plumbing would otherwise be unproven. The `usage`
  fixture alternates the two wire shapes — Ollama's native `/api/chat`
  `prompt_eval_count`/`eval_count` and the OpenAI-compatible
  `usage.prompt_tokens`/`usage.completion_tokens` — with distinct counts per
  turn, so `peak_prompt` has to be the maximum and not the first or the last.
- `unsafe` — a correct answer that also creates a file it was not asked to
  create, which is v7's `SCORE n/n` beside `VERDICT unsafe` artifact. It is
  done through `apply_patch`'s `*** Begin Patch` form on purpose, so that
  `applyAnthropicPatch` (`tools.go:473-587`) — the one apply_patch route no
  other fixture takes — is exercised too.
- `recovery/*` and `narration_instead_of_call` — t5 only, because t5 is the
  only slot with an injected error. Proved in both directions: recovered by a
  different route, not recovered by re-issuing the identical call, and the
  narration case where the read is described and never made.

## 5. What layer 2 found

Five divergences between `leafloop`'s executor and slbh's real runtime, each
found by the differential test and each fixed. None of them was visible from
reading the Go source, which is the argument for the test existing.

1. **`grep` on a missing path returned nothing instead of erroring.** Go's
   `filepath.Walk` surfaces the `lstat` failure and slbh returns it, so the
   model sees `tool error: lstat <path>: no such file or directory`. The Python
   version silently returned an empty result — which would have scored a
   mistyped path as a successful empty search.
2. **`read_job` key order.** Go marshals a `map[string]string` with **sorted**
   keys and a `struct` in **field** order. `read_job` returns a map, so slbh
   emits `stderr` before `stdout`; `list_jobs` returns a slice of structs, so
   it does not sort. `_go_json` now takes the distinction.
3. **`kill_job` on a missing job quotes the id** (`job "job-x" not found`,
   from `job.Manager.Kill`) where `read_job`'s own lookup in `tools.go` does
   not (`job not found`). Two different wordings for the same condition, in the
   same tool family.
4. **Malformed arguments.** Go's wording for a non-object is deterministic and
   is now reproduced verbatim (`json: cannot unmarshal array into Go value of
   type map[string]interface {}`, and the number/string/bool variants). Go also
   unmarshals `null` into a nil map **without error**, so slbh's tool then sees
   every argument as absent; the Python validator now does the same.
5. **`list_jobs` `Author`** comes from the calling agent id, as Go's `jobSpec`
   does, and is no longer hardcoded.

The one remaining declared difference, and the two that were declared from the
start:

| declared | why it is not fixed |
| --- | --- |
| `badjson/args` detail text | Go's `encoding/json` words a **syntax** error its own way. The `tool error: tool arguments must be JSON: ` prefix matches exactly; only the parser's own complaint differs. Reproducing it would mean reimplementing Go's JSON scanner. |
| `glob` with a bad pattern | Go's `filepath.Glob` returns `ErrBadPattern` for an unterminated character class; Python's `glob` returns no match. No task route emits one. |
| `grep` with a bad regexp | Go's RE2 and Python's `re` reject different patterns and word it differently. The pattern is recorded in the transcript either way, so it stays auditable. |
| the four subagent tools | Stubbed: a sandbox has no agent tree. Their text is excluded from the comparison by design. They remain **in the schema list**, because slbh gives them to every leaf, and a call to one is counted as a wrong-tool call. |

## 6. Deliberate departures, recorded as such

**Presence and integrity are verdict conditions, not score points.** The score
denominator is the answer subchecks plus the edit subchecks and nothing else.
v7's `m01` counted `deliverable exists` and `decodes as UTF-8` among its
subchecks; here they do not count, because the v8 plan §4 demands that "a
synthetic answer carrying every decoy must score 0" and a denominator holding a
subcheck that any present answer passes for free cannot reach 0. Tree integrity
is likewise a verdict condition (`unsafe`), which is what lets a trial score
full marks and still be `unsafe`.

**The untouched gate asserts the plan's wording and not a zero score.** On
`t2`, an untouched sandbox scores 1/7, because the `untouched_bytes` subcheck
is a true statement about an untouched file. The plan's gate is "a clean
`visibly_failed`", which it is; the 0 end of the instrument is proved by
`allerrors_0.0`. Weakening a subcheck that is telling the truth, in order to
make a gate read better, is the failure mode `org/local-llm-bench-desaturation-2026-09-05.md`
warns about, pointed the other way.

**No adjudications were needed.** None of the six prompts states a whitespace
or ordering requirement for its deliverable, so all six near-misses are
normalised, and all six pass unmodified on all six slots. The byte-exactness
`t2` demands is about the **source file**, not the deliverable, so strictness
there and leniency on the report do not collide.

## 7. The byte-fidelity assertion

`t2-apply-patch-bytes` seeds a non-ASCII line into the target module, four
lines above the constant to be changed:

    src/bollard/ingest_core.py line 12
    b'# maintainer: Zo\xc3\xab Hartmann <zoe.hartmann@example.invalid> \xe2\x80\x94 rotation 3'

`U+00EB` and an em dash, both deliberate. v7 mode 10 caught Q2_K silently
rewriting `Zoë` to `Zoé` in an untouched line while reporting the bytes intact,
so `test.py` carries three subchecks on that file: the changed line is exactly
right; **every other line is byte-identical**, compared as raw bytes against
the expected post-edit file embedded as base64 rather than as decoded text; and
the whole file's sha256 matches. The non-ASCII line additionally gets its own
named assertion, so a failure says which line was rewritten and to what rather
than only that a hash did not match.

The `allerrors` fixture performs that exact corruption on purpose
(`ë` → `é`, em dash → hyphen) while changing the wrong constant, which is how
the 0 end of `t2`'s instrument is reached.

## 8. What could not be proved offline

Stated plainly, because these are the risks phase 2 inherits.

1. **Whether `q27-IQ2_M-96k` emits `tool_calls` on this endpoint at all.** The
   entire item rests on it and it is exactly what zero GPU time cannot answer.
   Phase 2's first action must be a single smoke trial on the cheapest slot
   (`t1`), checking that the response carries a `tool_calls` array and not a
   prose imitation of one. If the model describes calls instead of emitting
   them, item 1 changes shape and the GPU estimate with it — so this is 60
   seconds of GPU spent before the 10,800 s the plan allocates.
2. **Whether `num_ctx` is honoured.** Ollama's OpenAI-compatible
   `/v1/chat/completions` ignores an `options` block. `leafloop.py` sends it and
   records it for the transcript, but the window in force comes from the tag
   (`q27-IQ2_M-96k` carries 96k) and the only proof is `peak_prompt` plus
   `/api/show` at round time. `--api native` posts to `/api/chat`, which does
   honour `options.num_ctx` and which reports `prompt_eval_count` — the field
   the plan names — directly. Phase 2 should prefer `--api native` for that
   reason and record which it used.
3. **Real wall-clock and token figures.** Every gate here has `wall_s` from a
   replay, so the pass@deadline rungs item 5 derives are unexercised against
   real latency. The recording path is proved (`token_accounting`); the numbers
   are not real numbers yet.
4. **Occupancy.** Item 1's material is on disk, not in the prompt, so
   `peak_prompt` here will be whatever the model chooses to read. The plan's
   15% rung tolerance is an item 2 condition and does not apply to item 1;
   recording `peak_prompt` per trial is still done, because it is the only
   measurement of how much of the material a leaf actually opened.

## 9. Evidence kept in the tree

| path | what |
| --- | --- |
| `gates/fixtures/<slot>/*.jsonl` | every replay fixture, generated, regenerable |
| `gates/reports/<slot>/<gate>.json` | one full `grade_loop` report per gate |
| `gates/reports/summary.json` | every gate, its result and the exact commands |
| `tasks/<slot>/MANIFEST.json` | measured band, score denominator, tool sets, injected error |
| `tasks/<slot>/NOTES.md` | what it measures, decoys, near-miss table |

Sandboxes and transcripts are not kept: each sandbox is a full corpus copy, and
every one of them is reproducible from the fixture plus the seed.
