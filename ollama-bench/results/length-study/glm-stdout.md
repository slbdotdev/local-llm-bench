Done. Deliverables (nothing outside `results/length-study/` touched; the directory isn't a git repo, so no commit applies):

- **`results/length-study/length_study.py`** — self-contained analysis (manual Spearman, no deps), verified to run clean.
- **`results/length-study/report.md`** — 82 lines, all four requested sections.

Note: the GLM subagent attempt already sitting in `results/length-study/` (from `run.sh`) produced an empty stdout, so I did the analysis directly instead.

Key findings:

1. **Table** — 7 tasks, 2.5–4.8 k tokens, 33–49 clauses, m = 26–31. fp8 is missing 61_codecs (16/21 runs), luna only ran 4 tasks.
2. **Correlations are weak everywhere at n=6–7** — pooled rho: bytes −0.16, clauses **+0.10**, cases −0.05. The one strong signal: **haiku declines with prompt bytes (−0.82)**. fp8's out_tokens don't scale with spec length (rho ≈ −0.06) — its cost spike is wall-time/timeouts, not reasoning volume.
3. **Conclusion**: the local model's collapse is a **harness-cap artifact**, not spec length — 11/18 Q2_K_L runs ended single-turn with out_tokens pinned at the ~24 k cap and "import failed" (budget exhausted before the first file was written). Where it did complete, it aced the *shortest* spec (59_uri, 27/27). Clause count is uncorrelated with score for every model (59_uri has the 2nd-most clauses and was the local model's best). Failures by model: sonnet narrow (1.7 checks/run, one deep clause), fp8 one-deep-subsystem across differential buckets (4–9 checks, one mechanism), haiku broad (4.6) + timeouts.
4. **v5 rule** (inferred, flagged as such): ceiling ~14 k bytes / ~45 top-level clauses, difficulty carried by one exactly-specified deep mechanism rather than clause enumeration — and fix the local out-token cap first, or local length studies measure the cap, not the spec.
