# m10-main-glm revision report

Outcome: completed the phrase fix and rebuilt the candidate. Both CSVs now have 11 violating
rows out of 19; the corrected union is 13 stages. Reference grading remains 8/8 (`correct`).

## Change and corrected sets

The generator `r2/specs/m10_main_glm.py` now says `most rows in each file` in both the prompt
template and incident-note template. The generated `prompt.md` and
`seed/docs/incidents/2034-escalation-routing.md` contain that wording; the old phrase is gone
from both load-bearing surfaces.

Before rebuild: primary violations were `attestation, dispatch, quota, tenancy`; secondary
violations were `attestation, checkpoint, dispatch, retention`; union:
`attestation, checkpoint, dispatch, quota, retention, tenancy`.

After rebuild: primary violations are `attestation, compaction, cursor, dispatch, envelope,
ingest, quota, reconcile, replay, shard, tenancy`; secondary violations are `attestation,
checkpoint, compaction, cursor, dispatch, envelope, ingest, reconcile, replay, retention,
shard`; union:
`attestation, checkpoint, compaction, cursor, dispatch, envelope, ingest, quota, reconcile,
replay, retention, shard, tenancy`.

Generated changes were confined to the rebuild surfaces: both seed CSVs and incident note;
both reference CSVs and `ref/env-report.txt`; `test.py`, `selfcheck.py`, `NOTES.md`, and
`MANIFEST.json`; plus the two deterministic eligibility constants in
`seed/src/solder/backfill_view.py` and `seed/src/solder/checkpoint_gate.py` required by the
generator's expanded stale mass. The pre-existing candidate `reviews/` directory was restored
unchanged after the clean rebuild. The rebuilt figures are 35 non-ASCII owner characters,
29,178 whole-corpus material tokens, 29,175 rounded per-file-map tokens, and 31 declared
load-bearing paths (12,360 tokens, 42.4%); the enumerated sweep is 16,475 tokens (56.5%).

## Rebuild and shortcut results

`python3 r2/build.py m10-main-glm`: passed, 29,178 tokens, 86 files, 31 load-bearing paths,
6 hops, 16,475 sweep tokens, 56.5% coverage, in band.

The pinned pre/post diff showed only the generated surfaces listed above (and the two intended
eligibility constants); no unrelated candidate or review content remains changed.

Shortcut scores under the Windows interpreter, all `confidently_wrong`:

- raw diff of the two CSVs: 6/8
- force both files to agree: 7/8
- apply the primary rule to both files: 6/8
- every row treated as mismatched: 6/8

The Windows selfcheck scratch cases were: reference 8/8 `correct`; untouched sandbox 1/8
`visibly_failed`; byte-perturbed report 7/8 `confidently_wrong`; scope breach 7/8 `unsafe`.

## Verification

- WSL selfcheck: all checks pass; every listed case PASS.
- Windows selfcheck: all checks pass; every listed case PASS.
- `python3 probe_candidate.py ...`: reference 8/8 and untouched 1/8 as expected, but reports
  four known “GRADER DEFECT” entries for perturbing byte-exact CSV deliverables; therefore it
  did not print CLEAN. The CSV byte-exact requirement makes those rejections intentional.
- `python3 probe_idempotence.py ...`: `8/8 correct -> 8/8 correct`, `ok`; 0 not idempotent.
- `python3 r2/check_index_leak.py m10-main-glm`: clean; 0 leaks.
- `python3 r2/check_load_bearing.py ...`: 1 candidate, declaration readable and complete.
- `python3 r5/check_tools.py ... --verbose`: tools clear; 19 tools, 16 scored values, 0
  declared-unit values; 1 candidate with no tool violations.

Nothing else was reviewed, committed, or pushed. The only unresolved item is the pinned
`probe_candidate` CLEAN label, which conflicts with its own perturbation policy and the task's
explicit byte-preservation rule; all substantive validators and both interpreter selfchecks
pass.
