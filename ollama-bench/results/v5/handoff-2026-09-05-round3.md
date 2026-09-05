# Handoff — v5 campaign, round 3 and the large band

*Written 2026-09-05 by the Opus manager session that ran rounds 2 and 3. `date +%F` on this host
still reports `2026-09-04`; every campaign document is dated 2026-09-05 and both plain names were
already taken, hence the suffix. **This file supersedes `handoff-2026-09-05-manager.md`**, which in
turn superseded `handoff-2026-09-05.md`.*

**Read in this order:** `plan-2026-09-05.md` (plan of record) -> this file -> `schedule.md` ->
`decisions.md` from "2026-09-05, Opus manager session — round 3" to the end -> the findings pages
listed below. There is no `CLAUDE.md` in this repo; `README.md` plus the plan is the contract.

## Start here: nothing is blocked

Every precondition ever owed has been met or withdrawn. The suite is never gated on a structural
sign-off. The only things that wait on the owner are ending the campaign and writing the report.
Every plan section 10 decision belongs to the manager: take it, record the reasoning in
`decisions.md`, move on.

## What the suite is now

Two bands over **the same eight task families**, which is what makes the comparison mean anything:

| band | suite | candidates | material | window |
| --- | --- | --- | --- | --- |
| tiny | `authoring/round2/suite-0` | `g01..g04/cand-4`, `t01/cand-4`, `t02/cand-2`, `t03/cand-3`, `t04/cand-1` | 174-770 tokens; t03 alone 6,235 | 24k |
| large | `authoring/round3/suite` | `cand-5`, all eight families | 30,018-42,570 tokens | 64k |

`authoring/bands-2026-09-05.json` and `authoring/material-sizes-2026-09-05.json` hold every
candidate's measured size. Chars per token is **4.664**, measured, not assumed.

**Synthetic fill is withdrawn from every scored row.** No `--fill-tokens`, no `--pad-tokens`.
`fill_calibrate.py` and the fill machinery in `pibench.py` are kept for diagnostics only.

## The reference result, and the target is met

Haiku three trials, Sonnet two, over all eight large-band tasks (`authoring/tally_all.py`):

| band | Haiku | Sonnet | Haiku confidently-wrong |
| --- | --- | --- | --- |
| tiny, 24k | 21/24 = 87.5% | 24/24 = 100% | 12.5% |
| large, 64k | 17/24 = 70.8% | 16/16 = 100% | 29.2% |
| **both** | **38/48 = 79.2%** | **40/40 = 100%** | **20.8%** |

Section 2.1 asked for Haiku near 80% with Sonnet at or above 90%. **79.2% and 100%.** The three
tasks doing the discriminating are **g04** (0/3 — the policy memo's per-row rounding rule),
**t01** (1/3 — one misclassification in 55 records) and **g03** (1/3 — a 177-file rename).
Every failure was read individually and every one is a genuine comprehension miss; details in
`findings-2026-09-05-large-band.md`.

## The GPU result, and where it stops

`results/bend-small-24k.json` (+ `.md`), `results/bend-large-64k.json`,
`results/bend-large-48k-q3km.json`. No fill, q8_0 KV, 100% GPU on every trial, one trial per cell.

| cell | resident | tasks run | pass | wall range |
| --- | ---: | ---: | ---: | ---: |
| q27-Q2_K_L-24k | 11.83 GB | 8/8 | 7/8 | tiny band |
| q27-Q3_K_S-24k | 13.18 GB | 8/8 | 7/8 | tiny band |
| q27-Q3_K_M-24k | 14.00 GB | 8/8 | 6/8 | tiny band |
| q27-IQ3_M-24k | 13.35 GB | 8/8 | 6/8 | tiny band |
| q27-Q2_K_L-64k | 13.35 GB | **8/8** | 7/8 | 35.4 - 493.5 s |
| q27-Q3_K_S-64k | 14.70 GB | 3/8 | 3/3 checker, 1/3 on the 900 s wall | 498.4 - 1779.7 s |
| q27-IQ3_M-64k | 15.11 GB | 1/8 | 1/1 | 216.3 s |
| q27-Q3_K_M-48k | 14.91 GB | 3/3 that fit | 1/3 | 475.3 - 900.1 s |

**The bend is a headroom bend, not a quality or offload bend.** Same task, t03, 30,604 tokens:
35.4 s at 13.35 GB resident, 216.3 s at 15.11, 498.4 s at 14.70, 880.6 s at 14.91 — every one of
them 100% GPU with all 66 layers offloaded. `Q2_K_L` wins the large band outright, and the ordering
by pass rate and by wall time is the **reverse** of the ordering by bits.

**In thirty-two 24k trials there was not one `visibly_failed`.** Every failure was
`confidently_wrong`, so on that band the confidently-wrong rate and the failure rate are the same
number. The campaign's only `visibly_failed` came from `Q3_K_M-48k` on t02.

**What is not measured.** `Q3_K_S` ran three of eight large tasks and `IQ3_M` one of eight, so the
large band has **one complete quant row, not three**, and the 64k *quality* comparison between the
three quants has not been made — only the wall-clock one. That is queue item 1 in `schedule.md`;
`decisions.md` D-R3-11 has the reasoning for stopping. **The artifact resumes rather than repeats**:
re-run with the same `--tag`, and pass `--no-tps` (the throughput-curve probe is what killed the
first attempt, `decisions.md` D-R3-10) and `--timeout 900`.

**The GPU was idle when this session ended** — `nvidia-smi` 604 MiB, 0% — with no run of this
session's live or queued.

## Faults found this session, and how each was proven

Five, and **four of the five were found by reading a tool's report of what it could not do, or by
reading one failing row — not one by looking at a rate.**

1. **t01 and t04 answer parsers rejected correct answers** on a missing or extra trailing newline,
   a BOM, or CRLF. Proven with a shaped near-miss set over a *correct* answer.
   `findings-2026-09-05-checker-format-bias.md`.
2. **A second t01 parser shape** in `cand-1` and `cand-2` did the same thing through
   `raw != raw.rstrip("\n") + "\n"`. Found because the propagation script printed
   `NO MATCH -- inspect by hand` and that line was read. Same page, addendum.
3. **`t01` sort order was ambiguous** — fixed by naming the byte-value ordering in the prompt.
4. **`t03/cand-1` was unanswerable and `t04/cand-2`'s reference contradicted its prompt.** Both
   withdrawn. `findings-2026-09-05-unanswerable-tasks.md`.
5. **`t04/cand-5` scored a correct answer `confidently_wrong` on an exact span equality**,
   `_ora_parsed[1] == (6, 20)`, when its own prompt invites `8-20`. Proven by diffing rows that
   agreed on everything else. Fixed, re-probed, and **every t04 row re-graded for both arms**.
   `decisions.md` D-R3-5.

A sixth, from earlier in the session and worth keeping: a **worker report was simply false** —
`g04/cand-5` was claimed 10/10 and was actually 5/10. Every worker claim since has been re-taken
locally before acceptance. A worker's answer is a claim, not a result.

## Known and deliberately not fixed

- **`tasks-v5/g04/cand-5/prompt.md` carries 14 literal `\`` sequences**, an escaping artifact from
  the authoring brief. Cosmetic; it changes no requirement and is not the cause of Haiku's 0/3
  (Sonnet reads the same prompt and passes 2/2). Left alone so the source tree does not
  desynchronise from the `round3/suite` copy that produced the scored rows. **Fix it before the
  next round, in both places, then re-run `verify_candidates.py`.**
- **`t01`'s `trailing_spaces` rejection is intentional** and consistent across `cand-1..4`: the
  records are tab-separated and the final field is a replacement string required verbatim, so a
  trailing space is content. `cand-5` uses a different answer format and does normalise it. Do not
  "fix" this.

- **326 tracked `__pibench_pad_*.py` files** sit under `authoring/gate-haiku-48k/`, 2.7 MB of
  synthetic filler from the prompt-side fill approach the owner withdrew on 2026-09-05. They are
  deliberately truncated, so a repo-wide `ast.parse` sweep reports 353 syntax errors and 326 of them
  are these. They were committed before this session and are left alone: they are the evidence
  behind a completed 48k gate measurement, and deleting another session's evidence is not this
  session's call. Flagging them so the next sweep does not chase them, and so the owner can decide.

## Rules that cost this session real time

- **`round.py prep` is destructive.** Pass a task list when fixing one task; re-prepping a whole
  arm destroyed about twenty finished ungraded runs. `prep`/`grade` take a **comma-separated**
  task list as a single argument, not separate argv words.
- **A scoped `grade` merges** into the existing `results.json`; an unscoped one replaces it.
- **`ollama list` from WSL is a lie.** A WSL-side `ollama serve` with zero models holds
  127.0.0.1:11434 inside WSL. Confirm tags against the *Windows* daemon:
  `/mnt/c/Users/slb/scoop/apps/python/current/python.exe -c "...urlopen('http://localhost:11434/api/tags')..."`.
  It returns 21 models: the 15 grid tags, 5 suffix-less base tags that bake `num_ctx 32768` and no
  `num_gpu`, and the upstream repo tag.
- **Never poll with `pgrep -f`** — the pattern matches the waiter's own command line. Poll the
  outcome. `run_bend_large.sh` in `ollama-bench/` is the worked example: it waits on the previous
  pass's own artifact reaching four completed tags.
- GPU-side Python is **Windows** Python run from WSL, cwd under `/mnt/d/...`, no ssh and no
  PowerShell. `nvidia-smi` works directly from WSL.
- Verify the GPU with a **real load** reporting a processor split and a throughput on the known
  curve, never a version string.

## Org edits owed

**None of these were made.** `/home/slb/ansible-slb` and every `org/` directory were out of bounds
for this session, so they are listed here and in the session report rather than applied. No
ansible, no converge was run.

1. **`org/README.md`, "Local LLM runtime"** — add one line: scored v5 rows now use the material a
   task genuinely requires and **no synthetic prompt-side fill**; the suite runs two bands over the
   same eight families, tiny at 24k and large at 64k with 30-42k tokens of real material.
2. **`org/README.md`, same section** — add the resident-vs-`nvidia-smi` correction: the
   fair-weather threshold (~14.2 GB) is on **resident** size from `/api/ps`, and whole-device
   `nvidia-smi` usage runs about 1.8 GB higher, so reading the fair-weather rule off `nvidia-smi`
   labels cells unreliable that are not. Measured 2026-09-05: `Q2_K_L-64k` is 13.35 GB resident
   while `nvidia-smi` reads 15,152 MiB of 16,303 MiB.
3. **A new dated page, `org/local-llm-bench-desaturation-2026-09-05.md`**, linked from
   `org/README.md` under `## Deeper docs` and validated with `scripts/validate-org-docs.py`. It
   carries the one genuinely fleet-level lesson from this session, which is not about benchmarks:
   **a checker that is stricter than the prompt it scores manufactures the headline number.**
   `t04/cand-5` labelled a correct answer `confidently_wrong` purely on a line-boundary choice its
   own prompt invited. The general rule: probe any strict-format checker with a deliberately shaped
   near-miss set *before* trusting it, and when a fixer or a propagation step reports something it
   could not do, read that line — four of the five faults found in this session came from exactly
   that, and none from looking at a rate. **This must not be filed as a pending item**: it is a
   finished measurement with a lesson, not an open cleanup.
4. **`org/pending.md`, the 64k KV rerun item** — no edit owed. Its capacity half is already
   recorded as answered with the prediction falsified, and the quality half is genuinely still
   open. It is queue item 5 in `schedule.md`.
5. **`ollama-cuda-repair-2026-09-04.md`** — no edit owed. It already exists in `org/` and is
   already linked from the "Local LLM runtime" section.

## What a cold start should do next

`schedule.md`'s queue, in order. Item 1 was running when this session ended
(`results/bend-large-64k.json`, chained by `ollama-bench/run_bend_large.sh`); it **resumes rather
than duplicates** if re-run with the same `--tag`, so check the artifact before starting it again.
