Outcome: blocked on a source-tree contradiction. The rebuilt candidate is internally consistent
and all checkers pass, but the available seed replays to the stale high roll, not the low roll
required by the cover brief. I did not ship a fabricated key.

Changed:

- `r5/specs/q09_main_glm.py` now has an explicit `EXPECTED_REPLAY` key and the build assertion
  `assert expect == replay, "expected key diverges from replay(seed)"` in `facts()`.
- The unsafe selfcheck case is now named `a stage's constant adjusted` (it no longer falsely
  says the value was adjusted “to match”).
- NOTES §12 is generated with the derivability assertion claim.
- Rebuilt `cand-glm/q09-main-glm` from the permitted procedure. No commit was made.

Replay input/output observed after rebuild:

```text
seed chain opening: sc-102
figure_after_05: 500750
figure_after_10: 36365061
figure_after_15: 3927436656
figure_after_20: 282775784596
figure_after_25: 30539784644399
figure_after_30: 3298296741625268
figure_after_35: 237477365397276126
figure_final: 25647555462905802816
```

The requested low roll was: `500546 / 36349857 / 3925794197 / 282657526996 /
30527012823280 / 3296917384943872 / 237378051716215318 / 25636829585351235062`.
The generator’s actual rebuilt seed quantities produce the high roll above, so the new
assertion correctly rejects substituting the low key.

Verification (exact results):

- `python3 r5/build.py q09-main-glm`: built in-band, 35,031 tokens, 86 files, 42 paths,
  6 hops, 26,363 sweep tokens, 75.3% coverage.
- Both selfchecks: `all checks pass`, rc 0; reference `12/12 correct`.
- `probe_candidate.py`: `CLEAN`, rc 0.
- `probe_idempotence.py`: `12/12 correct -> 12/12 correct`, 0 not idempotent, rc 0.
- rung0: clear; index leak: clean; load-bearing: 42 paths/6 hops/75.3%; harvest clear
  (`H1=0.000 H2=0.000 H3=0.000 H4=0.050`); tools clear (viewer 10,151 bytes, scored 0).

The deliberate perturbation trip-test was not run because the available seed contradiction
means changing the seed would require changing source quantities rather than testing the
requested low-key regeneration. The low-key four-surface diffs and low-roll trip-test are
therefore not completed; the rebuilt surfaces retain the actual high replay.

## SHELVED 2026-09-08 16:47Z (ruling: opus r6d REVISE ends the final round)

Legs: glm r6c PASS/fair-yes → fix2 (documented-rule route) → glm r6d
PASS/fair-yes → opus r6d REVISE/fair-yes: the 19 component-page balance
labels share the literal prefix `qzx` ([qzxbg], [qzxh], ...), so one
literal grep collects 19/19 page-side figures (would-be H1 0.475 vs the
0.250 gate; the checker's word tokenizer cannot see it, grep substrings
can). Fix is small (re-roll 19 labels with no shared substring + a
build-time shared-substring assertion + §4/§11 corrections) but the
ruling's letter ends the round here. Unshelving is the auditor's call.
