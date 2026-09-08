# Revise `m09-main-luna` — make the definition hop load-bearing and claims complete

Family: luna (worker). Effort: high. One candidate, one job.

Working directory: `/home/slb/local-llm-bench/ollama-bench/results/v7/authoring`. Candidate:
`cand-luna/m09-main-luna/`. Generator: `r2/specs/m09_main_luna.py`.

## Change list — every round-two review finding

1. **Date-only rung-0 bypass.** Every stage at or after the cutoff is already divergent, so the
   date filter alone yields the reference four-stage set and scores `7/7`; the bypass costs
   `6,179` tokens (or `15,808` scanning all modules), below the 50% claim.
   (`cand-luna/m09-main-luna/reviews/opus-2026-09-07.md:35-80`.) Move the conforming `ingest`
   migration and counter-signature to a post-cutoff date as specified in the finding, keep the
   reference answer at four stages/2228/A-4, and add a build-time assertion plus a near-miss for
   the date-only five-stage answer. The definition comparison must then be necessary.
2. **Inverted grader docstring.** `test.py:5-7` names the decoy `limit`/`DEFAULT_*_LIMIT`
   rule instead of `ceiling`/`ENFORCED_CEILING`, contradicting the glossary and expected result.
   (`cand-luna/m09-main-luna/reviews/opus-2026-09-07.md:90-104`.) Correct the generated docstring and assert the
   exact rule words are the ones materialized.
3. **Missing near-miss cases.** `selfcheck.py` lacks a history-date decoy and the inverted-rule
   empty-set case, though the grader handles both. (`cand-luna/m09-main-luna/reviews/opus-2026-09-07.md:106-113`.)
   Add both cases with their measured scores.
4. **NOTES bridge count.** The `26,775` traversal figure counts `config/manifest.json` plus the
   other bridge artifacts, so “four bridge artifacts” is one short. (`cand-luna/m09-main-luna/reviews/glm-2026-09-07.md:75-79`.)
   Correct the enumeration while recomputing the number from the rebuilt tree.
5. **MANIFEST rounding.** The file map sums to `35,580` versus `material_tokens 35,576`.
   (`cand-luna/m09-main-luna/reviews/glm-2026-09-07.md:80-81`; independently `cand-luna/m09-main-luna/reviews/opus-2026-09-07.md:162-165`.)
   Reconcile the map/aggregate or label their separate rounding bases.
6. **Unsupported checker citation.** NOTES cites `r2/check_index_leak.py` as a mechanical
   measurement, but the review could not verify that tool and used an equivalent grep instead.
   (`cand-luna/m09-main-luna/reviews/glm-2026-09-07.md:82-83`.) State exactly what was run and
   what was inferred; do not claim an unrun validator.
7. **Probe provenance.** NOTES says the near-miss table comes from `probes.json`, which is not
   present; `selfcheck.py` says cases are inline. (`cand-luna/m09-main-luna/reviews/opus-2026-09-07.md:148-161`.)
   Correct the provenance statement.

The GLM review otherwise found the reference, derivation, checker, placements, and coverage
sound, but its three nits above remain findings (`cand-luna/m09-main-luna/reviews/glm-2026-09-07.md:67-91`). The
Opus review supplies the three actionable defects and the date-only blocker. No candidate has
both round-two reviews free of an actionable finding; this slot requires revision.

## Binding revision bars

Keep the answer keys derivable from the material and assert every count, date placement,
qualifying set, output length/offset, and token figure during the build. The added conforming
post-cutoff stage must be an actual material fact, not a typed exception. NOTES must distinguish
measured structural coverage from trial evidence, and MANIFEST numbers must reconcile.

No graded-surface shortcut may expose the result through a single token, prompt label, helper
output, or fixed frame. Vary label fragments, line offsets, surrounding frames, and whether a
decisive value is last; specifically ensure no one grep or `tail -n1` harvest collects the stated
figures across stages. Keep the glossary definition as the only source of the comparison rule,
but do not use that placement to make the task hard to do. Carry the q09/m08 bars: every key must
be material-derivable, every claimed property build-time asserted, and no single-token or
fixed-frame sweep may collect figures across units. Preserve the 29,000–36,000 main band and
the deliberate under-24,000 whole-tool-output truncation treatment, with its measured assertion.

## Rebuild and drift check

Edit only `r2/specs/m09_main_luna.py`, then run exactly:

    cp -r cand-luna/m09-main-luna /tmp/m09-pre-rev
    python3 r2/build.py m09-main-luna
    diff -r /tmp/m09-pre-rev cand-luna/m09-main-luna | head -100

The seeded rebuild must be deterministic. Only explained `seed/`, `ref/`, `test.py`,
`selfcheck.py`, `NOTES.md`, and `MANIFEST.json` surfaces may drift. On unexplained drift, restore
the backup, record it, and finish by hand without shipping unrelated generated changes.

## Exact checker battery

Run once each from this directory. Verdicts must come from the Windows interpreter; `python3`
runs checkers and build artifacts.

    python3 cand-luna/m09-main-luna/selfcheck.py
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-luna/m09-main-luna/selfcheck.py
    python3 probe_candidate.py cand-luna/m09-main-luna
    python3 probe_idempotence.py cand-luna/m09-main-luna
    python3 r5/check_rung0.py cand-luna/m09-main-luna
    python3 r2/check_index_leak.py m09-main-luna
    python3 r2/check_load_bearing.py cand-luna/m09-main-luna
    python3 r5/check_tools.py cand-luna/m09-main-luna --verbose

In scratch, grade reference, untouched, the date-only five-stage answer, history-date answer,
inverted-rule empty-set answer, a byte-perturbed correct report, and a scope breach under
`/mnt/c/Users/slb/scoop/apps/python/current/python.exe`. Report exact scores, the minimum-file
path, and the best single-token/fixed-frame attacks; no shortcut may reach full score.
