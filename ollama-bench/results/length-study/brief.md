# Length-vs-outcome study on tasks-v4 (read-only analysis)

Question from the owner: "In trying to write harder tests, many of these tests are simply longer, and that seems
to be a larger issue for the local LLM." Quantify it.

Inputs (all read-only; do not modify anything outside results/length-study/):
- tasks-v4/<task>/prompt.md (the spec each model saw) and tasks-v4/<task>/test.py (hidden test; count its cases
  and the SCORE denominator n/m).
- Outcomes: results/v4-ref-medium-1800.json (fp8 reference, 3 trials, fields pass/score/wall_s/timed_out/in_tokens/
  out_tokens), results/sonnet-v4/grades.json, results/haiku-v4/grades.json, results/codex-luna-v4/grades.json
  (dicts keyed "<task>/t<n>" with pass, score), results/v4-local-medium.json (Q2_K_L, 18 runs, harness-capped:
  treat as a separate row and say so), results/v5-smoke-q27-Q3_K_S.json (partial, fixed harness).

Deliverable: results/length-study/report.md with
1. A per-task table: prompt bytes, approx tokens (bytes/4), number of numbered/bulleted requirement clauses in
   prompt.md (state your counting rule), hidden-test case count m, and per model: pass rate and mean SCORE.
2. Correlations (Spearman is fine, computed with a small Python script you write under results/length-study/)
   between prompt length / clause count / case count and mean SCORE, per model and pooled; also between
   prompt length and out_tokens for the fp8 reference (reasoning appetite vs spec length).
3. A plain conclusion: is the local model's difficulty driven by length (more clauses) or by depth, and how does
   that differ from Sonnet/fp8/Luna/Haiku? Where do the models' failures fall: many clauses each partly wrong,
   or one deep clause?
4. A proposed authoring rule for v5: a prompt-length ceiling (bytes and clauses) with the number justified
   from the data, and what should carry difficulty instead. Mark clearly what is measured vs inferred.
Keep the report under 120 lines. Python is available as `python`. Do not run any model or benchmark.
