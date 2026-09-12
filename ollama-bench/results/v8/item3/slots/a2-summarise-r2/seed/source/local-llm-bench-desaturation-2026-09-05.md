# The v5 desaturation campaign: what it settled, and the checker lesson

2026-09-05. Rounds 2 and 3 of the local-llm-bench v5 campaign, run by an Opus
manager on the desktop GPU; the campaign's own record is
`ollama-bench/results/v5/` in `local-llm-bench` (plan of record
`plan-2026-09-05.md`, then `handoff-2026-09-05-round3.md`, `schedule.md`,
`decisions.md` from "round 3", and the four `findings-2026-09-05-*.md` pages).
This page holds only what the fleet needs to keep.

## A checker stricter than the prompt it scores manufactures the headline number

`t04/cand-5` scored a correct answer `confidently_wrong`, the worst verdict the
instrument has, on an exact span equality: the checker required lines `6-20`
while its own prompt, asking for "the implementation itself, not a helper
declaration, documentation, comment", invites `8-20`. Three Haiku rows and two
Sonnet rows differed from a pass only there. Fixed to a bounded span, then
every t04 row re-graded for both arms; Haiku t04 went 1/3 to 3/3, and three
confidently-wrong labels were withdrawn as instrument artifacts
(`decisions.md` D-R3-5).

Two live checkers, t01 and t04, also failed a correct answer on an extra
trailing newline, a leading blank line, or trailing spaces, none of which the
prompt forbade; found by `authoring/probe_checkers.py`, which rewrites a
correct deliverable five ways the prompt does not forbid and re-runs the
checker (`findings-2026-09-05-checker-format-bias.md`). The reference-passes,
empty-fails check cannot find this class, because reference and checker share
one author's whitespace habits.

Five faults were found in the round. Four came from reading a tool's report
of what it could not do, or one failing row, and none from looking at a rate.
One worker report was simply false, a candidate claimed 10/10 that was 5/10;
every worker claim after it was re-taken locally before acceptance.

Rule: probe a strict-format checker with a shaped near-miss set before
trusting it; when a fixer or a propagation step prints what it could not do,
read that line.

## Resident size, not `nvidia-smi`, is the fair-weather number

The desktop's fair-weather threshold, about 14.2 GB above which idle VRAM
drift can reclaim a model's memory, is on the resident size `/api/ps`
reports. Whole-device `nvidia-smi` runs about 1.8 GB higher: `q27-Q2_K_L-64k`
is 13.35 GB resident while `nvidia-smi` read 15,152 of 16,303 MiB. Read off
`nvidia-smi`, every 64k cell would have been labelled unreliable; on resident
size the 2-bit line holds the large band with headroom and the two 3-bit lines
(14.70 and 15.11 GB) do not (`decisions.md` D-R3-9).

## The bend is a headroom bend

Same task, t03 at 30,604 tokens, all trials 100% GPU with 66 of 66 layers
offloaded: 35.4 s at 13.35 GB resident, 216.3 s at 15.11, 498.4 s at 14.70,
880.6 s at 14.91. Q3_K_S answered two tasks correctly at 1,456.9 s and
1,779.7 s, correct and unusable, which a pass rate alone would have hidden.
Q2_K_L, the 2-bit quant, wins the large band outright, and the ordering by
pass rate and wall time is the reverse of the ordering by bits at both 24k
and 64k. In thirty-two 24k trials there was no `visibly_failed`: every
failure was confidently wrong.

## What the suite is now, and where it stops

Scored rows use the material a task genuinely requires; synthetic prompt-side
fill is withdrawn. Two bands over the same eight task families: tiny at 24k,
174-770 tokens; large at 64k, 30,018-42,570 tokens. The desaturation target
is met, Haiku 38/48 (79.2%) with Sonnet 40/40. The large band has one
complete quant row (Q2_K_L 7/8); Q3_K_S ran 3 of 8 and IQ3_M 1 of 8 before
the pass was stopped short with the GPU idle (D-R3-11), so the 64k quality
comparison between quants is unmade and is queue item 1 in `schedule.md`; the
artifact resumes under the same `--tag` with `--no-tps --timeout 900`.
