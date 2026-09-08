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
