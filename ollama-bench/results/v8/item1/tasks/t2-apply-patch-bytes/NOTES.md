# NOTES - t2-apply-patch-bytes

v8 campaign, item 1 (leaf-loop fidelity under slbh's tool surface), standard band.
Built by `results/v8/item1/build_tasks.py`; the bulk material is v7's own
`authoring/make_corpus.py`, unchanged, and the overlay is hand-authored.

## 1. What it measures

A byte-exact apply_patch edit. One line may change; every other line must compare byte-identical as raw bytes, including a deliberately seeded non-ASCII line.

Item 1 is a tool-loop instrument, not a reasoning instrument: every answer here is shallow to
reason about and real to fetch. v7 already measured reasoning depth and saturated at 19/20, so
repeating that axis would buy nothing. What is unmeasured is whether the deployed leaf calls the
right slbh tool with arguments that satisfy slbh's own schema and then reads what came back.

## 2. Tools

Expected: `read_file`, `apply_patch`, `write_file`
Acceptable: `glob`, `grep`, `read_lines`, `read_bytes`, `quick_bash`, `quick_py`

Any other tool call is counted as a wrong-tool call by `grade_loop.py`, including a call to one
of slbh's four subagent tools. Those four are in every leaf's schema list
(`internal/harness/agent.go:285` applies no depth filter) and have no runtime in the sandbox, so
a leaf that tries to delegate its own task is recorded doing it.

## 3. Decoys, and the wrong courses the material rules out

the manifest's own `limit` for the stage, which is a plausible wrong `new`; and the neighbouring DEFAULT_*_WINDOW_S constant.

## 4. Deliverable and scoring

`patch-report.json`, a single JSON object. Score denominator 7: 4 answer subcheck(s) plus
3 edit subcheck(s). Presence, decodability and tree integrity are verdict conditions
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

## 5b. A platform trap this slot found, which the next phase must settle

**On Windows, slbh's unified-diff `apply_patch` route rewrites the whole file
to CRLF, and the model has done nothing wrong.**

slbh's `apply_patch` sends a unified diff to `git apply --unsafe-paths
--whitespace=nowarn` (`tools.go:462`). Git for Windows ships
`core.autocrlf=true` in its **system** config, so that conversion happens even
outside a repository. Running this slot's gates under the Windows interpreter
caught it, with the byte-fidelity assertion naming the line exactly as it was
built to:

    SCORE 5/7
    NOTE non-ascii line 12 was rewritten:
      b'# maintainer: Zo\xc3\xab Hartmann <...> \xe2\x80\x94 rotation 3'
      -> b'# maintainer: Zo\xc3\xab Hartmann <...> \xe2\x80\x94 rotation 3\r'

Every line gained a `\r`. The instrument worked; the route changed the bytes.

The `*** Begin Patch` form goes through slbh's own `applyAnthropicPatch`
(`tools.go:473-587`) with no git involved, and is byte-exact on both platforms.
The reference fixture therefore uses that form.

**This is a validity condition on the slot, not a detail.** If phase 2 runs
`leafloop.py` under the Windows interpreter, a leaf that emits a unified diff -
the commoner shape by far - fails this slot through the platform rather than
through its own byte discipline, and the slot then measures patch-format choice
instead of byte fidelity. Three ways out, for the control session to choose:

1. Run `leafloop.py` under Linux. The deployed slbh leaf runs in WSL anyway, so
   this is also the faithful option; only the grader needs the Windows
   interpreter, and `refprobe.py` covers that.
2. Set `core.autocrlf=false` for the sandbox before the round. This diverges
   from the deployed slbh's own environment, so it should be recorded.
3. Score this slot only on the `*** Begin Patch` route and say so in the prompt,
   which narrows what it measures.

Not chosen here: making `leafloop.py` pass `-c core.autocrlf=false` to
`git apply`. That would make the harness better behaved than slbh and hide a
real slbh property on Windows, which is the opposite of what a fidelity
instrument is for.

## 6. Gates

`python3 selfcheck.py` runs the grader-only gates; `../../gates/run_gates.py` runs the
loop-level gates through `leafloop.py --replay`. Both are offline. Results are recorded in
`results/v8/item1/GATES.md` with the command that produced each.

## 7. Band

Measured, never estimated, at the suite's constant of 4.664 chars/token. See MANIFEST.json:
`material_tokens` against `band_range_tokens`.
