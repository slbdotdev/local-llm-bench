# v7 calibration on the GPU — 2026-09-06

*Written by the Opus manager subagent on FRACTAL, in WSL, executing
`manager-brief-calibration-2026-09-06.md` against `plan-2026-09-06.md` section 7. Every decision
is in `decisions.md` as D7-26 … D7-n; this file is the result, not the reasoning. The host clock
reports `2026-09-05`; documents are dated by the campaign, as v5, v6 and the v7 authoring round
all were.*

**Calibration is not selection.** v5's rule 4a stands in full and was not bent: no task was kept,
dropped, reworded or reordered because a quant passed or failed it. Difficulty is tuned against
the aggregate; an individual task changed only on a fairness or measurement finding read out of a
transcript.

## The configuration this was measured on

| | |
| --- | --- |
| workhorse | **IQ2_M** at its own rung, **64k** (`q27-IQ2_M-64k`), main timeout 900 s |
| neighbours | **UDQ3KXL at 48k** (`q27-UDQ3KXL-48k`), **Q2_K at 64k** (`q27-Q2_K-64k`) |
| cheap band | 24k for all three, on tags baked for this run (D7-27) |
| suite | `authoring/suite/`, 20 tasks, ten failure modes, one main and one cheap slot each |
| harness | `pibench.py` through pi, `--think medium`, `--no-tps`, no fill or pad flags, the pi resilience extension mandatory on every cell |

The suite is authored for 60-75% occupancy of a **48k** window. IQ2_M and Q2_K run it at 64k, so
the *authored* occupancy figure there is **45-56%**, restated rather than corrected, exactly as
D7-1 said it would be. UDQ3KXL at 48k carries the authored figure unchanged. What was
*achieved* is a different number and is the first thing this report reads.

## Before anything was scored

**The GPU was verified by a real load on all six tags, never by a version string** (D7-28). Every
tag: 100% GPU, residency reproducing v6's placement table to the hundredth of a GiB where v6
measured the same rung, generation 56-64 tok/s. Generation is 20-25% *faster* than v6's own
figures for the same quants, because v6 shared the card with a second campaign from 22:44 and
measured ~6% contention (D6-38); nothing else was running here. **v7 walls are therefore not
comparable with v6's**, for the same reason v6's were not comparable with v5's.

**The suite was re-validated on disk**: `validate_all.py` over all twenty candidates, **20 sound,
0 problems** — files, band, seed cleanliness, compilation, selfcheck, and the full probe
(reference passes, untouched sandbox is a clean `visibly_failed`, no whitespace perturbation of a
correct answer changes the verdict).

**Sandboxes are outside every git repository** by construction on this harness (D7-29):
`pibench.run_pi()` uses `tempfile.mkdtemp` and runs under the Windows interpreter, whose temp
directory is `C:\Users\slb\AppData\Local\Temp`. The handoff's open item was about `sanity.py`,
which built the reference arms, and it still stands for any future arm.

<!-- RESULTS SECTIONS ARE APPENDED BELOW AS EACH PHASE LANDS -->
