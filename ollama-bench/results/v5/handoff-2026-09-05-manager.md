> **SUPERSEDED.** This handoff is kept for its evidence. The current handoff is
> `handoff-2026-09-05-round3.md`, written after round 3 and the large band.

# v5 handoff — the Opus manager session of 2026-09-05

**This is the newest handoff. Read it first.** It supersedes `handoff-2026-09-05.md`, which
supersedes `handoff-2026-09-04.md`. Both older pages remain accurate as *evidence* of what was
true when they were written; where any of them disagrees with this page or with
`plan-2026-09-05.md`, the plan wins first and this page second.

`date +%F` returned `2026-09-04` on this machine while every document in this campaign is dated
`2026-09-05`; the two handoff names that follow the clock were already taken, so this file carries
a suffix rather than clobbering a page that still holds evidence.

## Read these, in this order

1. **`plan-2026-09-05.md`** in full — the plan of record. Then `plan-rev5-focused.md` sections 1a,
   3, 4, **4a** and 7, which it keeps by reference.
2. This page.
3. `schedule.md` — rewritten today against the true state; the queue starts at item 1.
4. `decisions.md` from the heading "2026-09-05, Opus manager session" to the end.
5. The three findings pages written today:
   `findings-2026-09-05-rebanding.md`, `findings-2026-09-05-checker-format-bias.md`,
   `findings-2026-09-05-unanswerable-tasks.md`.

There is **no `CLAUDE.md` and no `AGENTS.md`** in this repository and there never has been. The
contract is `README.md` plus the plan.

## The three owner rulings, unchanged and still governing

1. **There is no freeze and no structural sign-off.** Nothing in this campaign waits on the owner
   except ending it and writing the report.
2. **Sharpen until Haiku sits near 80% while Sonnet holds at or above 90%.**
3. **Synthetic context fill is withdrawn.** Context comes from material a task genuinely requires.
   Every scored row uses **no `--fill-tokens` and no `--pad-tokens`**.

## Machine state, verified today rather than assumed

    nvidia-smi          RTX 5080, 16,303 MiB total, idle at ~1,460-1,770 MiB
    real load           q27-Q3_K_S-24k, 3,213 eval tokens, 52.20 gen tok/s
    ollama ps           14.15 GB resident, pct_gpu 100, context 24576
    nvidia-smi peak     15,583 MiB
    model tags          /api/tags returns 21: the 15 cell tags, 5 suffix-less base tags,
                        and the upstream GGUF repo tag

52.20 tok/s is on the Q3_K_S curve in `results/gpu-tune/summary.md`. **Verify by a real load
reporting a processor split and a throughput together, never by a version string** — every cheap
check was correct throughout the 2026-09-04 CPU-only fault. `gpu_verify.py` beside this file does
it in one command.

The invocation for all GPU-side work, with no ssh and no PowerShell:

    /mnt/c/Users/slb/scoop/apps/python/current/python.exe <script> ...

with cwd under `/mnt/d/...`, which that interpreter sees as `D:\...`. `nvidia-smi` works directly
from WSL. **A WSL-side `ollama serve` holds `127.0.0.1:11434` inside WSL with zero models**, so
WSL Python hitting localhost gets 404s that look like missing models; do not chase them.
`OLLAMA_KV_CACHE_TYPE` stays `q8_0` and the `q4_0` ritual is withdrawn.

## What this session did

### The re-banding measurement, which reshaped the campaign

Every task's real material was counted at the suite's measured 4.664 chars/token. Across all 31
pre-existing candidates the range is **149 to 7,637 tokens**. Only t03's three candidates reached
even the small band; **the medium and large bands were empty**. The plan's own worked example —
"t03 already belongs to the medium band, eight graded facts out of a 12k-token document" —
measures 6,235 tokens and is corrected.

That turned re-banding from bookkeeping into the critical path: there was no context axis to run.
`findings-2026-09-05-rebanding.md`.

### The grid design taken in response

**Two bands over the same eight task families**, rather than three bands over different tasks:

- **small** — the existing families at their natural size (median ~500 tokens), run at **24k**;
- **large** — a new `cand-5` per family, the *same question over 30,000-45,000 tokens*, at **64k**.

Section 3.4 concedes that bands populated by different tasks confound context with task identity.
Holding the family fixed across both bands removes that confound entirely and costs nothing here,
because every existing task needed a larger sibling anyway. The price: "small" means "the task's
natural size" and sits below the plan's 4k-8k floor, so **always report the measured token count,
never the band name alone**.

### Desaturation, two rounds

Round 1 swapped the seven `cand-4` harder variants in: **Haiku 21/24**, but only g03/cand-4
genuinely discriminated. A 16-candidate sweep then ran every unused variant once, which is how the
rest of the difficulty space was mapped cheaply.

Round 2 is the current small band. Composition and rates:

| task | candidate(s) | Haiku | Sonnet |
| --- | --- | --- | --- |
| g01 | cand-4 | 3/3 | 3/3 |
| g02 | cand-4 | 3/3 | 3/3 |
| g03 | cand-4 | **1/3** | 3/3 |
| g04 | cand-4 | 3/3 | 3/3 |
| t01 | cand-4 | 3/3 | 3/3 |
| t02 | rotating cand-2 / cand-4 / cand-1 | **2/3** | 3/3 |
| t03 | cand-3 | 3/3 | 3/3 |
| t04 | rotating cand-1 / cand-3 / cand-3 | 3/3 | 3/3 |

    Haiku   21/24 = 87.5%      target: about 80% (19-20/24)
    Sonnet  24/24 = 100.0%     guard:  at or above 90%

**The guard holds with room to spare, and it holds on the two tasks Haiku fails**, which is what
makes those failures difficulty rather than ambiguity. Both Haiku failures are
`confidently_wrong`, the verdict the campaign most wants to measure.

**The target is not met and the small band cannot meet it.** All 31 pre-existing candidates have
now been run at least once; only two discriminate. The remaining lever is the large band.

### t02 and t04 now rotate their variants

The handoff's banked structural question, taken under section 10. As single items each was one
bit — t02/cand-2 always answers "yes", t04/cand-3 always answers "no" — so a model that guessed
the bit once scored 3/3 for the wrong reason. Each trial now runs a different variant, graded
against the variant it was given. **Arity is unchanged**, so section 7 needs no amendment.
`round.py` supports this with per-trial suites (`suite-0/`, `suite-1/`, `suite-2/`).

### The large band exists but is NOT gated

Eight `cand-5` tasks authored by Luna against `authoring/CONTRACT-2026-09-05.md`. Material
measured independently, agreeing exactly with every worker `MANIFEST.json`:

    g01 30,001   g02 32,476   g03 29,840   g04 42,570
    t01 36,643   t02 31,102   t03 30,604   t04 41,138

`verify_candidates.py` over all 39 candidates: **REF 39/39, EMPTY 39/39, no problems.**
`probe_checkers.py` over the seven-task large-band suite (`authoring/round3/`): **no
format-strictness defects.**

**No cloud gate row exists for any of them.** That is queue item 1 and it is the phase to protect.

### Four task defects, found by probing rather than by report

All the same family: a checker or a reference depending on something the prompt never stated.

- **t01 and t04 answer parsers** scored a *completely correct* answer `SCORE 0/N`,
  `visibly_failed`, for a leading blank line, one extra trailing newline, or a trailing space.
  Model-dependent bias in the headline instrument. Fixed; `fix_answer_parsers.py` is idempotent.
- **t01's sort order** — "ordered by POSIX relative source-file path", enforced as byte order. A
  trial got all seven classifications right, sorted case-insensitively, and scored 0/14. The
  prompt now states the ordering exactly.
- **t03/cand-1** demanded an incident date that appears **nowhere** in its material, and a phrase
  its material does not contain. Five trials across two model families all reported it. Withdrawn.
- **t04/cand-2's** reference cites a line span that excludes half the behaviour its own prompt
  describes. Withdrawn.

`findings-2026-09-05-checker-format-bias.md` and `findings-2026-09-05-unanswerable-tasks.md` carry
the evidence and the tools.

### Local calibration on the small band, no fill (plan step 3): complete

`q27-Q3_K_S-24k`, eight tasks, one trial each, `results/calib-nofill-24k-q3ks.json`:

    wall            11.9 - 29.3 s   against 300 s
    output tokens   455 - 1,386     against 5,000
    turns           4 - 5           never single-turn
    residency       13.18 GB, pct_gpu 100 on every trial
    nvidia-smi      peaks 15,585 - 15,593 MiB
    gen tok/s       52.5, on the Q3_K_S curve

Every never-checked question in step 3 is answered and all of them comfortably.

**The quant passed all eight.** Recorded as calibration only, per 4a: no task was kept, dropped,
reworded or reordered because of it. It does retire the specific worry in plan section 2.1 — that
a suite tuned to Haiku-80% might floor every quant. On this suite the quant is at the **ceiling**,
not the floor, so hardening is the safe direction.

## The five tools this session added, and what each is for

All in `results/v5/authoring/`. Each exists because the tools already there could not see the
defect it finds.

| tool | what it answers |
| --- | --- |
| `measure_material.py` | how many tokens of real material each candidate carries, and which band that is |
| `round.py` | build / prep / grade a desaturation round, with per-trial suites for rotation and a `tally` verb |
| `probe_checkers.py` | does the checker reject a **correct** answer over whitespace the prompt never mentioned |
| `check_derivable.py` | is every value the reference asserts actually **present in the material** |
| `fix_*.py` (four) | each defect's fix, idempotent and re-runnable, with the diagnosis in its docstring |

`verify_candidates.py` checks that the checker passes its own reference and fails an empty
sandbox. **It cannot find either of the two new defect classes**, because the reference is written
by the same hand and habits as the checker; `probe_checkers.py` and `check_derivable.py` are the
instruments that treat the *answer* and the *material* as the authority instead.

## Traps, each with its workaround as an instruction

Everything in `plan-2026-09-05.md` section 8 still stands. Added today:

- **`round.py prep` is destructive.** It deletes and recreates each sandbox it touches. Pass a
  task list (`python3 round.py prep <round> <arm> <trial> t03`) when fixing one task. Re-prepping
  a whole arm to fix one of its tasks destroyed about **twenty finished but ungraded**
  reference-model runs today. A scoped `grade` now merges into the existing `results.json` rather
  than replacing it, so re-grading one task cannot turn the other seven into failures against
  emptied sandboxes.
- **Never re-prep a sandbox while an agent still holds it.** Two Sonnet rows came back
  `visibly_failed` with an untouched or half-written sandbox, purely because a prep raced a
  running agent. Both were re-run. `agent-run status` and the completion notifications tell you
  who is still holding what.
- **Escaping is evaluated once per layer.** A fixer script generated by another script had its
  `\r\n` collapsed into real newlines, producing an unterminated string literal in a checker.
  Write the file, then run the file; and when a string must survive two levels, use `str.format`
  with named fields rather than nested backslash escapes. `python3 -c "import ast; ast.parse(...)"`
  on every patched checker catches it in one second.
- **A worker's report is a claim.** g04/cand-5's notes claimed `SCORE 10/10, PASS, VERDICT
  correct` and eight passing A7 probes; independent verification scored its reference **5/10**.
- **Do not `git add -A` while a worker holds the tree.** Stage paths explicitly. Two empty-directory
  scope violations were left by authoring runs today and were removed by hand.

## State left behind

- **Working tree:** committed. Nothing is left dirty deliberately.
- **GPU:** small-band bend-finding was running when this page was written,
  `results/bend-small-24k.json` — all four 24k quants, one trial per task, no fill. **Check
  whether it completed before re-running it**; `pibench.py` skips `(task, trial)` pairs already in
  the artifact, so re-running it resumes rather than duplicates.
- **Models:** nothing is pinned loaded. `keep_alive: 0` was used after each measurement and the
  card returned to idle.
- **`OLLAMA_KV_CACHE_TYPE`:** untouched at `q8_0`, which is correct and is the setting scored rows
  use.
- **Luna run for g03/cand-5** was still finishing its A7 probes at the end of the session and may
  have left `_probe_a7.py` and `a7-*` scratch directories in `tasks-v5/g03/cand-5/`. Remove them
  if present; `verify_candidates.py` already reports g03/cand-5 REF ok and EMPTY ok.
- **No suite is frozen.** There is no freeze in this campaign and there will not be one.

## What is genuinely the owner's, and it is still only three things

1. Ending the campaign and writing the report.
2. Real-dollar spend beyond the GLM line in plan section 7.
3. Any fleet change under `ansible-slb` that is not a doc.

Everything else is the manager's. Take it, record the reasoning in `decisions.md`, and move on.
**Never stop to ask** — a manager idling behind a question it could have decided is the expensive
failure this fleet has already paid for once (`ansible-slb/org/subagents-2026-09-04.md`).

## Org edits this session was barred from making, and still owes

This session was barred from `/home/slb/ansible-slb` and from every `org/` directory. Three edits
are owed there and are listed for whoever holds that repo:

1. **`org/pending.md`: remove the KV-probe item.** It has been satisfied in substance since
   2026-09-04 — the lifecycle faults are fixed and proven with `drain_branch_proven: true` — and
   this session did not touch it either.
2. **`findings-2026-09-04-gpu-cuda-broken.md` belongs in `ansible-slb/org/` as a dated page**,
   linked from `org/README.md` and validated with `scripts/validate-org-docs.py`. It is a
   fleet-level finding living in the bench repo only because of that bar. It must **not** become
   an `org/pending.md` item.
3. **New, from today:** `org/README.md`'s "Local LLM runtime" section says quant benchmarking
   lives in `local-llm-bench` and stops there. It is worth one line that the campaign's scored
   rows now use **no synthetic context fill**, since the fill mechanism is still in `pibench.py`
   and a future reader will otherwise assume it is in use.
