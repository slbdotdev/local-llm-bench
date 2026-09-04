# Length-vs-outcome study on tasks-v4 (read-only analysis)

Script: `length_study.py` (this dir). Spearman, ties = average rank. No model was run.
Caveats up front: fp8 ref has only 16/21 runs (61_codecs never ran); luna only 4 tasks;
local Q2_K_L is **harness-capped** (see §3) — its row measures the cap, not the spec;
local Q3_K_S (v5-smoke, fixed harness) covers 3 tasks, all 3 runs hit the 1200 s wall.

Clause-count rule: a clause = a **top-level** markdown list item (line matching `^- `, `^-* `,
or `^N. `, no leading indent) in prompt.md, outside fenced code blocks; table rows and
indented sub-items are not counted. `m` = `TOTAL` in test.py = the SCORE denominator.

## 1. Per-task table (pass% / mean SCORE, n trials in parens)

| task | bytes | ~tok | clauses | m | fp8 ref | sonnet | haiku | luna | local Q2* | local Q3* |
|---|---|---|---|---|---|---|---|---|---|---|
| 52_reengine | 12725 | 3181 | 33 | 31 | 33%/.78 | 67%/.91 | 0%/.68 | 33%/.69 | 0%/.00 | 0%/.00 |
| 55_minilang | 14126 | 3531 | 46 | 31 | 67%/.99 | 0%/.97 | 0%/.80 | 33%/.95 | 0%/.06 | 0%/.00 |
| 56_tmpl | 19199 | 4799 | 49 | 29 | 0%/.82 | 0%/.92 | 0%/.46 | – | 0%/.00 | – |
| 57_stateful | 14265 | 3566 | 36 | 26 | 67%/.88 | 100%/1.00 | 0%/.31 | 33%/.81 | 0%/.23 | 0%/.19 |
| 59_uri | 10214 | 2553 | 41 | 27 | 33%/.33 | 100%/1.00 | 33%/.89 | – | 33%/.50 | – |
| 60_numlit | 12431 | 3107 | 41 | 30 | 100%/1.00 | 67%/.98 | 0%/.61 | 33%/.78 | 0%/.00 | – |
| 61_codecs | 10624 | 2656 | 37 | 30 | – | 100%/1.00 | 0%/.87 | – | – | – |

*local Q2 = Q2_K_L, 18 runs, harness-capped (§3). local Q3 = Q3_K_S partial smoke, fixed harness.

## 2. Correlations (Spearman rho vs mean SCORE)

| metric | fp8 (n=6) | sonnet (7) | haiku (7) | luna (4) | local Q2 (6) | pooled (33) |
|---|---|---|---|---|---|---|
| bytes | +0.20 | −0.48 | **−0.82** | +0.60 | −0.27 | −0.16 |
| clauses | +0.23 | −0.15 | +0.04 | +0.80 | −0.09 | +0.10 |
| cases m | +0.23 | −0.64 | +0.29 | −0.11 | −0.59 | −0.05 |

- With n=4–7 tasks, **no rho here is individually significant**; treat all as weak evidence.
- The one strong signal: **haiku declines with prompt bytes (−0.82)** — the smallest model
  is the only one measurably hurt by raw spec length.
- Clause count is *uncorrelated* everywhere (pooled +0.10): more enumerated clauses per se
  do not lower any model's score, including the local model's.
- fp8 appetite: bytes vs out_tokens rho = **−0.06**, clauses +0.22, m +0.33 (n=16 runs).
  The reference model does **not** reason longer on longer specs; its cost spike is wall
  time/timeouts (52, 59 both hit the 1800 s cap), not output volume.

## 3. Conclusion: length, depth, or harness?

- **Measured:** the local model's visible collapse is a **harness cap artifact, not spec
  length**. 11/18 Q2_K_L runs ended single-turn with out_tokens pinned at ~22.5–24.8 k and
  "import failed" (the budget was exhausted before the first file was written) → SCORE 0.
  Q3_K_S (fixed harness) then timed out on all 3 tasks it ran.
- **Measured:** where the local model *did* complete, it did best on the **shortest** spec
  (59_uri, 10.2 k bytes: 27/27 in its uncapped 37-turn run) and second-best on 57_stateful
  (0.62). Its worst completed spec is the longest (56_tmpl, 19.2 k, 0/29 capped).
  Directionally "longer hurts", but n is tiny and confounded by the cap — **inferred, not
  proven**.
- **Measured:** clause count does not predict difficulty for *any* model (59_uri has the
  2nd-most clauses, 41, and the local model aced it). Difficulty tracks **depth**: the two
  tasks where fp8 itself loses the most (52 at .78, 59 at .33) are the single-deep-mechanism
  specs (backtracking+capture semantics; URI edge cases), not the longest ones.
- **Where failures fall:** sonnet fails **narrowly** (1.7 distinct failed checks per failed
  run, max 3) — one deep clause. fp8 fails as **one deep subsystem partly wrong across its
  differential buckets** (56 filters, 57 state machine, 60 format_number: 4–9 checks but all
  one mechanism). haiku fails **broadly** (4.6 checks/run) plus grader timeouts. luna sits
  between (2.5). The local model shows no clause-level pattern at all — it fails before or
  while producing code, i.e. breadth never even gets tested.

## 4. Authoring rule for v5

- **Ceiling (inferred, mostly from haiku + cap behavior): keep prompts ≤ ~14 k bytes
  (~3.5 k tokens) and ≤ ~45 top-level clauses.** Justification: every API model holds
  mean SCORE ≥ .78 on all specs ≤ 14.3 k bytes except the deliberately deep 52; the only
  prompt beyond 15 k bytes (56, 19.2 k) is where haiku craters to .46. Not measured on any
  model that completed 56 uncapped except sonnet (.92), so the ceiling is a conservative
  guard, not a cliff.
- **Do not chase clause count.** Measured: it is uncorrelated with score everywhere. A spec
  with 40 precise clauses is not harder than one with 30.
- **What should carry difficulty instead (inferred from where models actually lose points):
  one deep, exactly-specified mechanism** (ordering/semantics that must be *implemented*,
  not enumerated — 52's backtracking, 56's filter stickiness). That is what separates
  sonnet/fp8 from haiku/luna today.
- **Fix the harness first (measured):** a local run that can't finish reading the spec plus
  writing its first file inside the out-token cap produces SCORE 0 regardless of prompt.
  Either raise the cap for local rows or prepend no spec restatement duty; otherwise length
  studies on local models measure the cap.
