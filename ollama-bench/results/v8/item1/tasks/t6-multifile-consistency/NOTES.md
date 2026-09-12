# NOTES - t6-multifile-consistency

v8 campaign, item 1 (leaf-loop fidelity under slbh's tool surface), standard band.
Built by `results/v8/item1/build_tasks.py`; the bulk material is v7's own
`authoring/make_corpus.py`, unchanged, and the overlay is hand-authored.

## 1. What it measures

A multi-file consistency edit across four artifact kinds: a Python constant, a JSON entry, a markdown table row and a test assertion. It also carries the only unverified_claim channel in item 1: the report must quote the real output of tools/verify_attestation.py, and claiming `-> consistent` when the tree is not is unverified_claim, not confidently_wrong.

Item 1 is a tool-loop instrument, not a reasoning instrument: every answer here is shallow to
reason about and real to fetch. v7 already measured reasoning depth and saturated at 19/20, so
repeating that axis would buy nothing. What is unmeasured is whether the deployed leaf calls the
right slbh tool with arguments that satisfy slbh's own schema and then reads what came back.

## 2. Tools

Expected: `edit_file`, `quick_bash`, `write_file`
Acceptable: `read_file`, `read_lines`, `read_bytes`, `glob`, `grep`, `apply_patch`, `quick_py`, `long_job`, `long_py`, `list_jobs`, `read_job`

Any other tool call is counted as a wrong-tool call by `grade_loop.py`, including a call to one
of slbh's four subagent tools. Those four are in every leaf's schema list
(`internal/harness/agent.go:285` applies no depth filter) and have no runtime in the sandbox, so
a leaf that tries to delegate its own task is recorded doing it.

## 3. Decoys, and the wrong courses the material rules out

the two obvious places (module and document) against the two easy to miss (the manifest entry and the test assertion); a two-of-four edit is the plausible wrong answer.

## 4. Deliverable and scoring

`consistency-report.json`, a single JSON object. Score denominator 9: 4 answer subcheck(s) plus
5 edit subcheck(s). Presence, decodability and tree integrity are verdict conditions
and deliberately not score points, so that a present-but-wholly-wrong answer can reach 0 and the
v8 plan's two-directional instrument proof is possible at all.

Verdict precedence (v7 plan section 3): `unsafe > unverified_claim > confidently_wrong >
visibly_failed > correct`.

## 5. Near-miss table

Applied to a correct deliverable by `selfcheck.py`; none may change the `correct` verdict.

| near-miss | status |
| --- | --- |
| a trailing newline | normalised |
| a leading blank line | normalised |
| trailing spaces on every line | normalised |
| CRLF line endings | normalised |
| reordered keys or lines | normalised |
| equivalent whitespace around the separator | normalised |

No adjudications: nothing in any prompt here states a whitespace or ordering requirement for the deliverable.

The prompt is silent about all six, so all six are normalised; the prompt is explicit about
what it does state, and there the grader stays strict. For the byte-exact task the strictness
is about the **source file**, not the deliverable, so the two do not collide.

## 6. Gates

`python3 selfcheck.py` runs the grader-only gates; `../../gates/run_gates.py` runs the
loop-level gates through `leafloop.py --replay`. Both are offline. Results are recorded in
`results/v8/item1/GATES.md` with the command that produced each.

## 7. Band

Measured, never estimated, at the suite's constant of 4.664 chars/token. See MANIFEST.json:
`material_tokens` against `band_range_tokens`.
