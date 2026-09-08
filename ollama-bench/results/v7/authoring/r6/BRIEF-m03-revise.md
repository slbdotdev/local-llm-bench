# Revise `m03-main-luna` — break the disposition oracle and repair claims

Family: luna (worker). Effort: high. One candidate, one job.

Working directory: `/home/slb/local-llm-bench/ollama-bench/results/v7/authoring`. Candidate:
`cand-luna/m03-main-luna/`. Generator: `r2/specs/m03_main_luna.py`.

## Change list — every round-two review finding

The following findings are binding inputs to the revision; the quoted text is the finding, not a
new interpretation.

1. **Blocking rung-0 oracle.** The disposition column is a complete oracle: “`{rows where
   disposition == "open"}` == `{compaction, digest, shard}` == the answer” and the bypass costs
   “`1,313 of 30,225 material tokens (4.34%), 3 of 88 files`” while scoring `7/7`.
   (`cand-luna/m03-main-luna/reviews/opus-2026-09-07.md:43-76`.) Break that correlation in the
   seed. At minimum, retain the review's two concrete adversarial rows: `throttle` is `open`
   while its stamps agree, and `shard` is `no-exception` while its stamps diverge; preserve the
   reference answer, and assert both relationships from material at build time.
2. **Undisclosed label hint.** The five divergent documents self-label their stamps `-STALE`,
   “a hint, not evidence”; strip that hint or explicitly adjudicate it in NOTES.
   (`cand-luna/m03-main-luna/reviews/glm-2026-09-07.md:32-36,72-73`.) Prefer non-semantic
   stamp values whose divergence cannot be collected by one label grep.
3. **NOTES unsafe-score error.** The claim that a correct answer plus the marker scores `7/7`
   is wrong; the integrity subcheck makes it `6/7`. (`cand-luna/m03-main-luna/reviews/glm-2026-09-07.md:63-67`.)
4. **Probe provenance error.** NOTES says the near-miss table is generated from `probes.json`,
   but no such file ships and the cases are inline in `selfcheck.py`.
   (`cand-luna/m03-main-luna/reviews/glm-2026-09-07.md:68-70`; independently `cand-luna/m03-main-luna/reviews/opus-2026-09-07.md:152-158`.)
5. **MANIFEST units/rounding.** The per-file values are token estimates mislabeled under a
   char/token header, and sum to `30,228` against `material_tokens: 30,225`.
   (`cand-luna/m03-main-luna/reviews/glm-2026-09-07.md:50-56`; `cand-luna/m03-main-luna/reviews/opus-2026-09-07.md:159-161`.)
   Recompute the map and make its unit explicit; reconcile it with the aggregate or state the
   two rounding conventions unambiguously.
6. **NOTES filename typo.** The NOTES citation says `plan-2026-09-07.md` where the rung-0
   source is `plan-r3-2026-09-06.md` §3.5. (`cand-luna/m03-main-luna/reviews/opus-2026-09-07.md:152-155`.)
7. **Untested decoy.** The capacity-exceptions text describes a manifest/module disagreement
   that is never instantiated. (`cand-luna/m03-main-luna/reviews/opus-2026-09-07.md:162-164`.) Remove the dead
   claim or instantiate it without making it answer-bearing, and assert the intended state.

The GLM review's findings were explicitly “none verdict-driving” but still carry the four
hardening items above (`cand-luna/m03-main-luna/reviews/glm-2026-09-07.md:63-73`). No candidate has both round-two
reviews free of an actionable finding; this slot requires revision, not re-verification only.

## Binding revision bars

- Keep the answer and its independent fields derivable from seed material. Every claimed stage
  count, status relationship, byte/character count, token count, and probe score must be computed
  in `facts()`/the builder and asserted there; no hand-typed expected fact may survive a rebuild.
- The answer must require the rule, the stage documents/modules, and the ruling/audit material.
  No graded-surface shortcut may expose it through a CSV status column, a single token, a helper
  that prints the answer, or a fixed label fragment. Vary frame layouts and line offsets across
  units; do not put every decisive value at a common line or final-line position. Ensure prompt
  vocabulary and label fragments do not isolate the answer-bearing files.
- Keep the five artifact kinds and the load-bearing declaration honest. NOTES must report measured
  post-build values, not intended traversal; all figures must reconcile with MANIFEST and the
  material. Preserve main-band size (29,000–36,000 material tokens), CRLF/non-ASCII/byte-exact
  behavior, and the q09/m08 bars: no key that cannot be derived from material, and no
  single-token or fixed-frame sweep that collects stated figures across units.

## Rebuild and drift check

Edit only `r2/specs/m03_main_luna.py` for the candidate revision, then run exactly:

    cp -r cand-luna/m03-main-luna /tmp/m03-pre-rev
    python3 r2/build.py m03-main-luna
    diff -r /tmp/m03-pre-rev cand-luna/m03-main-luna | head -100

The seeded rebuild must be deterministic. The diff may contain only the explained `seed/` data,
`ref/`, `test.py`, `selfcheck.py`, `NOTES.md`, and `MANIFEST.json` surfaces. If anything else
drifts, stop, restore the backup, record the drift, and finish by hand so no unexplained generated
change ships.

## Exact checker battery

Run once each from this directory, after the rebuild. Verdicts must be obtained with the Windows
interpreter shown below; `python3` is for the checkers and build artifacts.

    python3 cand-luna/m03-main-luna/selfcheck.py
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-luna/m03-main-luna/selfcheck.py
    python3 probe_candidate.py cand-luna/m03-main-luna
    python3 probe_idempotence.py cand-luna/m03-main-luna
    python3 r5/check_rung0.py cand-luna/m03-main-luna
    python3 r2/check_index_leak.py m03-main-luna
    python3 r2/check_load_bearing.py cand-luna/m03-main-luna
    python3 r5/check_tools.py cand-luna/m03-main-luna --verbose

Also re-attack the corrected-set shortcut in scratch: CSV-only/disposition-only, the four
shortcut solvers (force-agree, diff-rows-only, primary-rule-both, everything-to-root), and the
best single-token and fixed-frame attacks. Grade every verdict with
`/mnt/c/Users/slb/scoop/apps/python/current/python.exe`; none may reach full score. Report the
measured minimum-file path, each score, and the structural/coverage figures.
