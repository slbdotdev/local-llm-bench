1. Biggest flaws

- The verdict threshold is effectively all-or-nothing. With Sonnet at 100%, “within 10 points” requires 4/4 Unity and 6/6 general tasks: one miss is 25 or 16.7 points. Conditional “median wall to pass” also hides failures. Fix: report raw per-task pass rates and uncertainty; use a predeclared task-level rule or substantially more tasks before class-level claims.

- The adaptive schedule is selection-biased. B1 only tests tasks where Q3_K_M already passed or scored ≥0.5; a quant that fails Q3_K_M may be better on a hard task, and zero-score tasks disappear. The B0 “stop” rule is based on one trial and three selected tasks, so “not viable” is not earned. Fix: reserve a balanced sentinel set—including zero/near-zero B0 tasks—for every quant and class; otherwise label the result “untested,” not “not viable.”

- The GLM gate is confounded by serving infrastructure. The plan still specifies price routing, while the audit found ~24 tok/s and endpoint idle stalls there; it also omits provider capture and provider-specific timeout sizing. A v5 GLM 2/3 gate could fail because of Relace, invalidating task admission. Fix: use throughput routing, record provider/provider cost and prompt overhead, size timeouts from measured throughput, and separate endpoint failures from model failures.

2. Task risks

- Highest Sonnet-gate risks: `g06` (20 strict sequential calls; one malformed call can fail the whole trial), `g04` (linter/tool/environment dependence), and `u03` (Unity serialization plus asset-reference migration across files).
- `g05` can fail exact-match grading and cannot fit the stated 16k context sweep with a 20k-token document. It is a context/needle task, not a coding discriminator.
- Weak or likely saturated: `g01` (simple function), `g03` (mechanical rename), `u01` (routine null fix), `u02` (named API lookup), and `u04` (test boilerplate). Strong models and many local models may all pass these. `g04` and `g06` are also weak coding discriminators even when they fail, since they mostly measure tooling/protocol reliability. Keep them diagnostic, not headline evidence.

3. Missing measurement

Measure peak VRAM and actual GPU residency per trial—especially KV-cache allocation, offloaded layers, and CPU spill. Without this, “maximum resident context” and concurrency results may silently include CPU offload and misstate usable local performance.
