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
