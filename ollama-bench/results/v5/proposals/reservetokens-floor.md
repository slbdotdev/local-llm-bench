# reserveTokens sanity floor — rationale (PROPOSAL ONLY)

1. **PROPOSAL ONLY.** Nothing was applied, committed or converged; no host was touched. The diff is
   `reservetokens-floor.diff` in this directory, for the owner to read first.
2. **What pi actually does.** `reserveTokens` is a subtraction, not a threshold: `shouldCompact` is
   `contextTokens > contextWindow - reserveTokens`.
3. **Why the fleet value is fine today.** 1048576 - 548576 = 500000, matching Claude Code's
   `autoCompactWindow` here. Correct — *while* the default model has a ~1M window.
4. **Why it is a trap tomorrow.** Point any managed pi at a model with a window below 548576 and the
   budget goes zero or negative, so it compacts on **every turn**. That presents as a hung or
   looping agent, not as a config error, and it costs a debugging session to find.
5. **This is not hypothetical.** v5 hit the same shape from the other side: the bench agent dir sets
   `compaction.enabled: false` at a 32k window, which disabled pi's truncation recovery and was half
   the mechanism behind v4's Q2_K_L zeros. Small-window pi is where these settings bite.
6. **The repo already knows.** `group_vars/all/vars.yml` says a smaller default window "must revisit
   this number". The proposal turns that sentence into an assertion, so it fails at converge rather
   than at the first turn of someone's run.
7. **Why a floor at half the window.** At exactly half, every turn compacts once the transcript
   passes the midpoint — already pathological. The check is meant to catch an order-of-magnitude
   mismatch, so it is deliberately loose and will not fire on any sane tuning.
8. **Cost.** One `assert` task and one restated variable. No new file, no template, no behaviour
   change on any host where the current values are correct.
9. **The one judgement call.** It adds `agent_config_pi_default_context_window`, duplicating the
   `contextWindow` in `agent_config_pi_models`, because reading it out of the nested
   `modelOverrides[defaultModel]` dict inside an assertion is unreadable. The comment ties the two
   together. If the owner prefers no duplicate var, the assertion can index the dict instead —
   uglier, and it breaks if `defaultModel` ever lacks an override.
10. **Explicitly not proposed:** changing 548576 itself, touching `branchSummary.reserveTokens`
    (separate key, 16384, correct), or any of the bench-local v5 values. Per Q8 = B every pi change
    for v5 is bench-local via `PI_CODING_AGENT_DIR`; this is the single fleet-side item, and it is a
    guardrail rather than a setting.

**Ruled the same day, and recorded here so the question is not reopened:** `pi-run` exposes only
`--model --effort --cwd --timeout --no-context-files` and **will not grow an `--agent-dir` flag**.
It does not strip `PI_CODING_AGENT_DIR` from the environment, so exporting it before the call is
sufficient — which is exactly what this plan's own GLM audit did. No wrapper change, no
ansible-managed file touched.
