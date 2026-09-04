# Codex Luna spot probe on tasks-v4 (2026-09-03, 11:10-11:32)

Question: on v4 tasks, does gpt-5.6-luna via the new `codex-run` wrapper land nearer Haiku or Sonnet?

Setup: 4 tasks x 3 trials, same sandboxes and hidden tests as results/haiku-v4 and results/sonnet-v4
(run.py copied from sonnet-v4). Wrapper defaults (gpt-5.6-luna, effort medium), `--timeout 1800`,
`--ephemeral`, `--no-context-files` (deviation from "keep defaults": the AGENTS.md chain was skipped so the
sandbox got no fleet instructions; Codex still saw ~/.agents/skills). 4 takers in parallel. All 12 runs rc 0,
no usage-limit hit, wall 138-429 s (mean ~265 s).

| task | Haiku pass (mean SCORE) | Luna pass (mean SCORE) | Sonnet pass (mean SCORE) |
|---|---|---|---|
| 52_reengine | 0/3 (0.677) | 1/3 (0.688) | 2/3 (0.914) |
| 55_minilang | 0/3 (0.796) | 1/3 (0.946) | 0/3 (0.968) |
| 57_stateful | 0/3 (0.308) | 1/3 (0.808) | 3/3 (1.000) |
| 60_numlit   | 0/3 (0.611) | 1/3 (0.778) | 2/3 (0.978) |
| mean / total | 0.598, 0/12 | 0.805, 4/12 | 0.965, 7/12 |

Verdict: Luna sits between the two, slightly nearer Sonnet on mean SCORE (0.16 below Sonnet, 0.21 above
Haiku) and roughly midway on passes. Haiku is clearly below it on every task.

Finding (important): Codex discovered the fleet-deployed `codex-run` skill in ~/.agents/skills and invoked
itself recursively as a "second-pass reviewer" in 8 of 12 runs (37 nested codex-run calls in total, up to 11
in one run; 60_numlit/t3). Each nested call burns ChatGPT plan quota and makes the score partly a
"Luna consulting Luna" result. pi-run was never nested. Same hazard exists for pi with the pi-run skill.
Suggested fix (ansible-slb, owner decision): the wrapper sets a depth marker in the environment and refuses
nested calls (or SKILL.md says not to invoke it from inside a Codex/pi run). The wrapper's usage-limit grep
also false-matched the word "quota" from SKILL.md text echoed in the transcript; harmless because it only
fires on non-zero exit, but the grep should be narrowed.

Files: runs.json (rc, wall), grades.json (hidden-test grades), <task>/t<n>/ sandboxes with _codex_final.md
and _codex_stderr.log (full transcript).

Addendum from the probe subagent's own report: on its first attempt (wrapper defaults, AGENTS.md chain on)
3 of 4 takers self-delegated within two minutes, reaching ~10 codex processes on the shared plan window; it
killed that batch, reset the sandboxes and relaunched with --no-context-files, which did not stop the
behaviour (skill discovery is independent of AGENTS.md). Its kill sweep also terminated some of its own
shells; no benchmark data was affected and the concurrent v4 local ranking was never touched. Its count was
9 of 12 reruns delegating (1-7 nested calls each); the grep count above (8 of 12, up to 11) used a narrower
pattern. Either way: the scores are Luna-delegating-to-Luna, not single-agent Luna.
