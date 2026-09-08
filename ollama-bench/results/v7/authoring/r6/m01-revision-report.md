# m01-main-glm revision report

## Outcome

The r5 REVISE finding and Opus fixes F1, F2, and F4 were applied. The generator was updated,
rebuilt, and its generated contract surfaces were copied back after restoring the pre-existing
review directory removed by the rebuild. Seed content and hashes were left unchanged.

## What changed

- `r2/specs/m01_main_glm.py`: renamed the deliverable key from `authority` to `scope_note` in
  the facts, prompt, reference, probes, load-bearing rationale, and generated notes; corrected
  the first-branch selfcheck expectation to `checkpoint, envelope` / `0`; removed the false F1
  sentence; and changed F2 to label both the strict floor and thorough traversal.
- `cand-glm/m01-main-glm/prompt.md`: deliverable key is now `scope_note`.
- `cand-glm/m01-main-glm/ref/dwell-audit.txt`: reference uses `scope_note: RN-0212`.
- `cand-glm/m01-main-glm/test.py`: expectation, keys, group label, and rationale use
  `scope_note`.
- `cand-glm/m01-main-glm/selfcheck.py`: all cases use the new key; the first-branch case now
  expects `checkpoint, envelope` and `0`.
- `cand-glm/m01-main-glm/NOTES.md`: F1 sentence removed, F2 now records the strict required
  floor as 8,221 / 32,213 (25.5%) and the thorough traversal as 23,134 / 32,213 (71.8%), and
  contract prose uses `scope_note`.

## Diff and integrity

`python3 r2/build.py m01-main-glm` reported `32213` tokens, `107` files, `18` load-bearing
paths, `7` hops, `23134` sweep tokens, `71.8%`, and `0 out of band`.

The rebuild initially removed the existing `reviews/` directory, so the backup was restored and
the five intended generated surfaces were applied back: `NOTES.md`, `prompt.md`, `ref/`,
`selfcheck.py`, and `test.py`. No other candidate file differs. `MANIFEST.json` comparison:
identical (exit 0). `seed/` comparison: identical (exit 0).

The strict-floor total was recomputed from the shipped MANIFEST: README, config manifest,
branches README, release note, decision note, 15 branch-record files, six stage documents, and
four stale-stage modules sum to 8,221 tokens; 8,221 / 32,213 = 25.5%.

The requested `grep -rn authority cand-glm/m01-main-glm` is not empty: the only remaining hits
are the immutable seed release-note prose and the historical Opus review record. Removing the
seed hit would violate the explicit no-seed-change and unchanged-MANIFEST boundary; the
contract surfaces themselves contain no old key.

## Verification

- `python3 cand-glm/m01-main-glm/selfcheck.py`: all checks pass; every case PASS, including
  reference 7/7 `correct`, corrected first-branch 5/7 `confidently_wrong`, and untouched 1/7
  `visibly_failed`.
- `/mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-glm/m01-main-glm/selfcheck.py`:
  all checks pass; same case results.
- `python3 probe_candidate.py cand-glm/m01-main-glm`: `CLEAN`; reference 7/7, empty 1/7, and
  all whitespace perturbations 7/7.
- `python3 probe_idempotence.py cand-glm/m01-main-glm`: `1 candidate(s), 0 not idempotent`;
  7/7 `correct` to 7/7 `correct`.
- `python3 r2/check_index_leak.py m01-main-glm`: `clean`; `0 candidate(s) leak their decisive
  constant into an index`.
- `python3 r2/check_load_bearing.py cand-glm/m01-main-glm`: `1 candidate(s), every
  LOAD_BEARING declaration readable and complete`; 18 paths, 7 hops, 6,284 load-bearing tokens,
  19.5%.
- `python3 r5/check_tools.py cand-glm/m01-main-glm --verbose`: `tools clear`; 20 tools with no
  arguments, 7 scored values, 0 declared units; `1 candidate(s), 0 whose seed tools print
  scored or per-unit values`.

Windows-interpreter scratch grading:

- Correct report with `scope_note`: exit 0, `SCORE 7/7`, `VERDICT correct`.
- Same report with old `authority` key: exit 1, `SCORE 3/7`, `VERDICT confidently_wrong`.
- Untouched sandbox: exit 1, `SCORE 1/7`, `VERDICT visibly_failed`.

Nothing else was changed or verified; no GPU, Ollama, pibench, network, or git operation was
used.
