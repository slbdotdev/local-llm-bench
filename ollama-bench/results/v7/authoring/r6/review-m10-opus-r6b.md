verdict: PASS
fair: yes -- every trap the task punishes (CRLF, the accented owner bytes, the backslash path, the two different rules) is stated in plain words in the prompt or the incident note before it can bite, and nothing decisive is hidden or encoded.
solved_it: yes -- I derived all three keys and both corrected CSVs from the prompt alone and matched `ref/` byte-for-byte; I nearly went wrong on retention, whose module says `ESCALATION_ELIGIBLE = True` but whose history entry says `withdrawn`, so it is a secondary-only fix and not a primary one.
checker: sound -- I ran the full selfcheck case set under both `python3` and `/mnt/c/Users/slb/scoop/apps/python/current/python.exe`; the naming case is `wrong: raw diff of the two files, legitimate divergence included`, which lands 6/8 `confidently_wrong`, and the reference lands 8/8 `correct` under both interpreters.
shortcut: 3 files, score 6/8 -- `docs/incidents/2034-escalation-routing.md` gives `root_cause` and the two data files give `bytes_preserved`, so path/readable/shape plus two of three fact groups pass while `corrected` and the byte-exact edit subcheck both fail; full score needs 39 distinct seed files (19 history entries + 17 modules + 2 CSVs + the incident note), far above the five-file floor.
harvest: 19/19 by `ESCALATION_ELIGIBLE` -- and `grep -rn "ESCALATION_ELIGIBLE\|- Status:" seed/` puts all 38 decisive values (19 statuses + 19 eligibility flags) on screen in one command; both sit at a fixed offset in byte-identical frames (module line 14, history line 4), so `sed -n 14p seed/src/solder/*.py` works too. After that grep the answer can be finished from three hand-opened files. This is a measurement, not a defect: the 38 lines still come from 38 files, and defeating grep by splitting or encoding the datum is itself a REVISE under step 8.
tools: clear -- all 19 seed modules run with no arguments, print 0 bytes, and expose no scored or per-unit value.
notes_claims: verified -- LOAD_BEARING sums to exactly 12360 tokens over 31 paths in 6 hops (42.36% of 29178); the section-3 enumeration sums to exactly 16475 (56.46%); the `files` map has 86 entries matching 86 files on disk and sums to 29175; the three bug categories are disjoint (`both` = 9, `primary_only` = quota/tenancy, `secondary_only` = retention/checkpoint, union 13); the naive cross-file diff yields 8 stages of which only 4 are in the answer, so it is neither subset nor superset as claimed; and the section-10 perturbation adjudication is exact -- CRLF is the only no-op and the other four fail on the editable CSVs.
tiers: Haiku fails at the byte-preserving in-place edit of two CRLF, non-ASCII CSVs combined with the 38-fact per-stage sweep -- a Haiku-class model rewrites the CSVs through a naive writer (losing CRLF or the diacritics), normalises `config\routing.json` to a forward slash, or miscounts `bytes_preserved` by treating `Bérénice` as one non-ASCII character; a careful Sonnet-class model is warned about all three explicitly in the prompt and gets the count by script, so it is not caught by the same step.
workhorse_failure: real -- the failure step is applying two different rules to two files that a diff makes look like one problem, then editing both in place without disturbing a byte; the material genuinely requires reconciling a per-stage history status against a per-stage module constant, and no file or index carries either fact twice (`check_index_leak` confirms `ESCALATION_ELIGIBLE` appears only in each stage's own module, and no document repeats a status).
hard_to_do: yes -- 38 per-unit facts, two distinct rules, four stages of legitimate divergence that must be left alone, and a byte-exact edit, none of which any single file or diff supplies.
fix: none required; optionally tighten the `bytes_preserved` gloss (see finding 1).

## Findings, by severity

1. **low -- residual ambiguity in the `bytes_preserved` gloss.** `prompt.md:32` says "every
   accented or non-Latin character in every owner name in both files, **counted once each**".
   `quota`'s owner, `Zoë Oyelaran`, is the one owner name byte-identical in both files, so a
   solver who reads "counted once each" as deduplicating across files answers 34 instead of 35.
   The leading clause at `prompt.md:30` ("the total number of characters, across the `owner`
   column of both files combined, whose Unicode code point is greater than 127") is precise and
   settles it at 35, which is why I do not treat this as a fairness defect -- but it makes
   `NOTES.md:128` ("two careful readers cannot land on different, equally-defensible numbers")
   an overstatement. Concrete fix if wanted: replace "counted once each" with "counting every
   occurrence, including the same name appearing in both files".

2. **low -- `NOTES.md:79` mis-describes the floor.** It calls 31 "the measured minimum-file
   path to full score". The true minimum is 39 distinct seed paths: `corrected` cannot be
   emitted without the status of all 19 stages and the eligibility flag of the 17 accepted ones,
   plus both CSVs and the incident note. The declaration is conservative in the safe direction
   (it understates, so `check_load_bearing` passing at 31/42.4% is still valid), but the
   sentence claims a measurement it did not make.

3. **informational -- `MANIFEST.json:6` `material_chars` 136087 vs 136127 measured.** The
   40-character delta is exactly the 40 CRLF pairs in the two data files, so the manifest counted
   with newline translation while a `newline=""` read does not. Consistent convention, and
   `material_tokens` (29178), which is the number every gate uses, is unaffected.

4. **informational -- `NOTES.md` section 9 near-miss table omits one selfcheck case.**
   `selfcheck.py` runs 16 cases; the table lists 15 (counting the five perturbations as one row).
   The missing one, `wrong: byte-perturbed correct report`, is adjudicated in section 10 instead.
   Cosmetic.

## What I checked

Read whole, once: `prompt.md`, `NOTES.md`, `MANIFEST.json`, `test.py`, `selfcheck.py`,
`seed/README.md`, `seed/config/routing.json`, `seed/config/manifest.json`,
`seed/docs/incidents/2034-escalation-routing.md`, `seed/docs/operations.md`,
`seed/docs/retention.md`, all 20 files under `seed/history/`, both `seed/data/*.csv`, both
`ref/data/*.csv` and `ref/env-report.txt`. Did not open `reviews/`, `r5/reviews/`, any other
candidate, `authoring/r6/` other than the method and this file, or run `git`.

Validator results, once each, from `results/v7/authoring`:

    python3 cand-glm/m10-main-glm/selfcheck.py            16/16 cases PASS, "all checks pass"
    (same, Windows interpreter)                           16/16 cases PASS, "all checks pass"
    python3 probe_candidate.py cand-glm/m10-main-glm       reference 8/8 correct; empty 1/8
                                                          visibly_failed; perturb:crlf 8/8 correct;
                                                          the other four perturbations 7/8
                                                          confidently_wrong, reported as
                                                          "GRADER DEFECT" -- the documented
                                                          NOTES section 10 exception, since those
                                                          four rewrite bytes in the byte-exact
                                                          editable CSVs
    python3 probe_idempotence.py cand-glm/m10-main-glm     8/8 correct -> 8/8 correct, ok
    python3 r5/check_rung0.py cand-glm/m10-main-glm        "rung 0 clear"; widest prompt word
                                                          'stage' reaches 28 of 31
    python3 r2/check_index_leak.py m10-main-glm            "clean"
    python3 r2/check_load_bearing.py cand-glm/m10-main-glm 31 paths, 6 hops, 12360/29178 = 42.4%
    python3 r5/check_tools.py cand-glm/m10-main-glm -v     "tools clear", 19 tools, 0 bytes each

My independent solution, before opening `ref/`: `corrected: attestation, checkpoint, compaction,
cursor, dispatch, envelope, ingest, quota, reconcile, replay, retention, shard, tenancy`;
`root_cause: config\routing.json`; `bytes_preserved: 35`; primary file moves 11 rows to the
escalation root, secondary file moves 9 rows to the escalation root and 2 (retention, checkpoint)
back to the owners root. Identical to `ref/` in all three keys and both files.

## What remains uncertain

- I could not see the pre-revision tree (no `git`), so my judgement on step 8 rests on
  `NOTES.md` section 3's own account of what changed plus the evidence in front of me: there is
  no obfuscation, no value split across lines, no encoded datum and no added arithmetic, and the
  cross-file diff that section 3 says used to reproduce the answer demonstrably no longer does
  (8 stages, 4 of them right). On that evidence the revision made the task harder to **do**, not
  harder to **understand**.
- Whether the harvest measurement above should count against a main-band candidate is a campaign
  standard question, not a defect I can adjudicate alone. I read the method's step 8 as settling
  it in the candidate's favour and graded accordingly.

verdict: PASS
