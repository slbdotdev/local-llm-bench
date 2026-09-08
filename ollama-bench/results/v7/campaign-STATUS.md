# v7 local validation and acceptance campaign — live status

Started: 2026-09-08 (UTC)

## Plan

Validate the admitted m01-main-glm and m10-main-glm slots on the named workhorse using the
repository v7 harness, with the GPU load check first. GPU spend is recorded in GPU_BUDGET.log.

## Completed

- Six-tag GPU real-load verification completed successfully. Desktop `gpuverify.log` recorded
  100% residency for all six tags and generation throughput on each; Ollama `/api/ps` was empty
  afterward.

## In progress

- Workhorse acceptance: three trials each for `m01-main-glm` and `m10-main-glm` at
  `q27-IQ2_M-64k`, 65536 context, using the Windows Python interpreter and pi resilience
  extension.

## Acceptance result

- `m01-main-glm`: 2/3 `correct`; one `confidently_wrong`.
- `m10-main-glm`: 0/3 `correct`; three `confidently_wrong`.
- Combined: 2/6 `correct`, 4/6 `confidently_wrong`, 0 length stops; `/api/ps` empty at end.

## Final CPU validation

- `coverage_gate.py`: exit 1; 0/6 pass, 6/6 below 50% coverage (coverage is a diagnostic under
  the current owner ruling).
- `tally_trials.py`: exit 1 only because the candidate directory includes unmeasured slots;
  the measured rows are m01 2/3 and m10 0/3, both at the required three-trial minimum.
- `probe_scope_gate_suite.sh`: exit 0; all 20 references `correct` under the Windows
  interpreter.
- `validate_all.py --slot m01-main-glm`: exit 0; 1 candidate sound, 0 problems.
- `validate_all.py --slot m10-main-glm`: exit 0; 1 candidate sound, 0 problems.
- Final idle check: `/api/ps` returned `{"models":[]}`; GPU telemetry 3%, 1641 MiB.

## Campaign closed

- No further GPU work was run. Accounted GPU-holding time is 27m39s (1659s), from the two
  intervals in `GPU_BUDGET.log`; the 12-hour budget remains ample.
- The acceptance cell did not modify the suite or admit either candidate. Both candidates are
  mechanically sound, but every measured trial missed the 50% material-coverage gate.

## Continuation: trials to n=10 (2026-09-08)

- Desktop clone fast-forwarded cleanly to origin before work. The corrected acceptance cell used
  `q27-IQ2_M-64k`, 65536 context, medium thinking, pi resilience, 900s timeout, and the candidate
  directory `authoring/cand-glm`; it resumed `v7r6-accept-IQ2_M-main` and added trials 3 through 9
  for each admitted slot. The initial attempt pointed at `authoring/suite`, found zero named tasks,
  and consumed no GPU time.
- Every continuation trial row is recorded in `results/v7r6-accept-IQ2_M-main.json` and its
  markdown report:

  | slot | trial | verdict | stop | timeout | wall s |
  |---|---:|---|---|---|---:|
  | m01-main-glm | 3 | correct | stop | no | 148.5 |
  | m01-main-glm | 4 | correct | stop | no | 251.4 |
  | m01-main-glm | 5 | visibly_failed | length | no | 274.5 |
  | m01-main-glm | 6 | confidently_wrong | stop | no | 142.7 |
  | m01-main-glm | 7 | visibly_failed | toolUse | yes | 900.1 |
  | m01-main-glm | 8 | confidently_wrong | stop | no | 197.8 |
  | m01-main-glm | 9 | correct | stop | no | 215.2 |
  | m10-main-glm | 3 | correct | stop | no | 504.6 |
  | m10-main-glm | 4 | visibly_failed | toolUse | yes | 900.1 |
  | m10-main-glm | 5 | confidently_wrong | stop | no | 126.5 |
  | m10-main-glm | 6 | correct | stop | no | 196.6 |
  | m10-main-glm | 7 | correct | stop | no | 496.6 |
  | m10-main-glm | 8 | correct | stop | no | 334.8 |
  | m10-main-glm | 9 | correct | stop | no | 166.0 |

- `tally_trials.py --tasks-dir results/v7/authoring/cand-glm --only-tags
  v7r6-accept-IQ2_M-main --json results/v7/r6-accept-tally-final.json`: exit 1 because the
  candidate directory contains 14 unmeasured slots; the two measured rows are complete:
  `m01-main-glm` 5/10 = 0.500, Wilson 95% [0.237, 0.763], 3 confidently_wrong, 2 visibly_failed;
  `m10-main-glm` 5/10 = 0.500, Wilson 95% [0.237, 0.763], 4 confidently_wrong, 1 visibly_failed.
  Combined measured rows: 10/20 correct, 7 confidently_wrong, 3 visibly_failed, 0 unsafe.
- Final `/api/ps` was `{"models":[]}`. The corrected extension interval was 4901s and campaign
  accounted GPU time is 6560s (1h49m20s), including the predecessor's 1659s; no early budget stop.

## Continuation: m05-main-claude to n=10 (2026-09-08)

- The synchronized desktop clone ran the admitted `m05-main-claude` candidate at
  `q27-IQ2_M-64k`, 65536 context, medium thinking, pi resilience, 900s timeout, and tag
  `v7r6-accept-IQ2_M-main`.
- Every trial row was recorded in `results/v7r6-accept-IQ2_M-main.json` and the generated
  markdown report:

  | slot | trial | verdict | stop | timeout | wall s |
  |---|---:|---|---|---|---:|
  | m05-main-claude | 0 | correct | stop | no | 85.9 |
  | m05-main-claude | 1 | correct | stop | no | 50.1 |
  | m05-main-claude | 2 | correct | stop | no | 109.7 |
  | m05-main-claude | 3 | correct | stop | no | 59.8 |
  | m05-main-claude | 4 | correct | stop | no | 93.8 |
  | m05-main-claude | 5 | correct | stop | no | 131.7 |
  | m05-main-claude | 6 | correct | stop | no | 102.2 |
  | m05-main-claude | 7 | correct | stop | no | 59.4 |
  | m05-main-claude | 8 | confidently_wrong | stop | no | 66.7 |
  | m05-main-claude | 9 | correct | stop | no | 99.9 |

- `tally_trials.py --tasks-dir results/v7/authoring/cand-claude --only-tags
  v7r6-accept-IQ2_M-main --json results/v7/r6-accept-tally-m05.json`: exit 1 because other
  candidate slots are unmeasured. The m05 row is 9/10 = 0.900, Wilson 95% [0.596, 0.982],
  1 confidently_wrong, 0 visibly_failed, 0 unsafe. The pre-existing m02 row is 8/10 = 0.800,
  Wilson 95% [0.490, 0.943], 2 confidently_wrong.
- The m05 GPU interval was 896s (start 12:47:39Z, end 13:02:35Z), bringing campaign
  accounting to 7456s (2h04m16s). Final Ollama `/api/ps` was `{"models":[]}`.

## Continuation: m09-main-luna to n=10 (2026-09-08)

- Started the admitted m09-main-luna cell with q27-IQ2_M-64k, 65536 context, medium thinking,
  pi resilience, 900s timeout, and tag v7r6-accept-IQ2_M-main. The desktop clone could not
  fast-forward because prior result files are dirty; the current local synchronized candidate
  was used without overwriting the desktop worktree.
- The ten m09 trials completed: all ten were `correct`, `stop`, and non-timeout. GPU interval was
  1055s (18:13:19Z–18:30:54Z).
- Per-trial wall seconds were 82.1, 48.6, 92.7, 86.8, 61.3, 82.9, 136.1, 99.6, 181.4, and
  121.6. `tally_trials.py --tasks-dir results/v7/authoring/cand-luna --only-tags
  v7r6-accept-IQ2_M-main --json results/v7/r6-accept-tally-m09.json` exited 1 because 16 other
  Luna slots were unmeasured; m09-main-luna is 10/10 = 1.000, Wilson 95% [0.722, 1.000], with
  0 confidently_wrong, 0 visibly_failed, and 0 unsafe. Final Ollama `/api/ps` was `{"models":[]}`.

## Continuation: m03-main-luna to n=10 (2026-09-08)

- Ran the admitted m03-main-luna candidate locally synchronized with the desktop worktree at
  `q27-IQ2_M-64k`, 65536 context, medium thinking, pi resilience, 900s timeout, and tag
  `v7r6-accept-IQ2_M-main`. The desktop clone remained dirty and behind, so it was not
  fast-forwarded or overwritten.
- Every trial row was recorded in `results/v7r6-accept-IQ2_M-main.json` and the generated
  markdown report:

  | slot | trial | verdict | stop | timeout | wall s |
  |---|---:|---|---|---|---:|
  | m03-main-luna | 0 | confidently_wrong | stop | no | 171.7 |
  | m03-main-luna | 1 | correct | stop | no | 98.7 |
  | m03-main-luna | 2 | confidently_wrong | stop | no | 142.7 |
  | m03-main-luna | 3 | correct | stop | no | 138.0 |
  | m03-main-luna | 4 | correct | stop | no | 109.2 |
  | m03-main-luna | 5 | correct | stop | no | 149.5 |
  | m03-main-luna | 6 | visibly_failed | toolUse | yes | 900.1 |
  | m03-main-luna | 7 | correct | stop | no | 231.8 |
  | m03-main-luna | 8 | correct | stop | no | 189.1 |
  | m03-main-luna | 9 | correct | stop | no | 134.9 |

- `tally_trials.py --tasks-dir results/v7/authoring/cand-luna --only-tags
  v7r6-accept-IQ2_M-main --json results/v7/r6-accept-tally-m03.json` exited 1 because 15 other
  Luna slots were unmeasured. The m03 row is 7/10 = 0.700, Wilson 95% [0.397, 0.892], with
  2 confidently_wrong, 1 visibly_failed, and 0 unsafe. The measured m03+m09 rows total 17/20
  correct, 2 confidently_wrong, and 1 visibly_failed. GPU interval was 2317s
  (19:10:23Z–19:49:00Z), bringing campaign accounting to 16255s (4h30m55s), with 26945s
  (7h29m05s) remaining. Final Ollama `/api/ps` was `{"models":[]}`.

## Provenance incident 20:10Z (auditor-found), correction in progress

The accept rows file forked on 0a5778f: the m07/q09/m04 trial commits
copied the /mnt/d result into `results/v7/v7r6-accept-IQ2_M-main.json`
(one directory too deep) while the tracked canonical path is
`results/v7r6-accept-IQ2_M-main.json`. The 20:05Z copy overwrote the
worktree file that held the m09 and m03 rows (20 rows: final_text,
grader, read_paths, per-trial nvidia peaks, token counts). The rows file
at HEAD holds seven slots (m01 m02 m04 m05 m07 m10 q09 = 70 rows); the
duplicate is deleted in this commit. m09 and m03 stand on their committed
tallies (r6-accept-tally-m09/-m03.json) plus run ids
wr-wsl-20260908T180737Z-87574fbb38e6 and wr-wsl-20260908T190543Z-b41d76b6b07c,
whose harness logs carry the full per-trial console tables — pending
re-run for true rows (in flight; this note is amended when they land).

## Provenance correction complete: true m09 and m03 rows (2026-09-08)

- Both slots were rerun on the RTX 5080 with the committed cell: `q27-IQ2_M-64k`,
  65536 context, medium thinking, pi resilience, 900s timeout, tag
  `v7r6-accept-IQ2_M-main`, and `authoring/cand-luna`. Pibench wrote true rows
  to the tracked canonical `results/v7r6-accept-IQ2_M-main.json`; no log synthesis was used.
- Canonical row count was 70 before and 90 after: m09 added 10 rows and m03 added
  10 rows. The seven pre-existing slots remain m01, m02, m04, m05, m07, m10, and
  q09, each with 10 rows.
- `m09-main-luna`: 10/10 correct, 0 confidently_wrong, 0 visibly_failed, 0 unsafe;
  trials 0–8 stopped normally and trial 9 passed with `stop=length` (362.1s, no
  process timeout). Wilson 95% [0.722, 1.000].
- `m03-main-luna`: 7/10 correct, 2 confidently_wrong, 1 visibly_failed, 0 unsafe;
  trial 7 was `stop=toolUse` at the configured 900s timeout. Wilson 95% [0.397, 0.892].
- `r6-accept-tally-m09.json` and `r6-accept-tally-m03.json` were regenerated from
  the canonical-tagged rows. The tally command exits 1 because 15 other Luna slots
  remain below the three-trial reporting minimum.
- The rerun intervals added 1280s (m09) and 2315s (m03); accounted GPU time is now
  20588s (5h43m08s), with 22612s (6h16m52s) remaining in the 12-hour budget. Final
  `/api/ps` was empty; no early budget stop occurred.
