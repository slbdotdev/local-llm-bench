verdict: REVISE
fair: yes — the prompt and the three overlay documents agree with `ref/` on every point I could test, and the one decisive rule is stated in plain prose in the contract before the decoy can bite.
solved_it: yes — my blind answer (`changed: audit, compaction, envelope, schema` / `declined: attestation, digest` / `authority: SEC-CFG-4`) and the four line-19 renames are byte-for-byte what `ref/` holds; I nearly went wrong at `docs/schema.md:20`, whose `sla_headroom` row reads 41 while `src/talus/schema_flow.py:14` reads 53, i.e. the decoy would have dropped a stage that IS in the answer.
checker: sound — I ran the reference and the empty sandbox and re-derived every hash in `CONFIG`: all 4 `editable` digests equal the `ref/docs/*.md` bytes, all 81 `seed_hashes` equal the seed bytes, 81+4 = 85 = every seed file, and no `editable` path also appears in `seed_hashes`, so a rename left undone fails subcheck 5 and a frozen document touched fails subcheck 6 independently.
shortcut: 27 files, score 8/8 — 19 modules (the only home of `SLA_HEADROOM`) + `docs/api/config-contract.md` + `docs/security/boundary.md` + the 6 published stages' documents; nothing under that reaches full score, because publication cannot be decided from any single index and `check_index_leak` confirms the constant is echoed nowhere.
harvest: 19/19 by `SLA_HEADROOM` (and a second 19/19 by `On-call team`) — but neither token is in the prompt's vocabulary; both have to be learned from the contract and the boundary first, which is the rung-0 property holding.
tools: clear — all 19 seed modules run with no arguments, rc=0, 0 bytes on stdout.
notes_claims: failed — `NOTES.md:33`, "Two of the nineteen stages carry exactly such a divergence, on purpose, and neither is part of the answer ... not to change the answer itself". The two divergent stages are `checkpoint` (doc 46, module 44) and `schema` (doc 41, module 53). `schema` is in the answer, in `changed`, and its divergence is exactly what makes the doc-trusting course produce a different `changed` set. Every other number in `NOTES.md`/`MANIFEST.json` verified.
tiers: Haiku fails at the publication rule | Sonnet passes — the `sla_headroom` row sits one line below the `window_s` row a Haiku-class model already has open, so reading it instead of the module constant is the path of least resistance (selfcheck's own "declared values trusted over effective values" row, 5/8 `confidently_wrong`); a Sonnet-class model that reads the contract, which names that failure mode in as many words, is not caught by it.
workhorse_failure: real — the step is "resolve publication from the module constant, not the document table", and the material states the rule, states why the rule is not a document question, and gives a worked reason (two prior audits) before the decoy appears, so failing it is a reading failure, not a trap.
hard_to_do: yes — 19 modules read for one integer each, then a two-way cross-reference (headroom ≥ 45, then on-call team ≠ Delivery Engineering) that no file states, then four surgical byte-exact edits in 4 of 19 forty-line documents that differ only in a noun.
fix: `NOTES.md:33` — replace "neither is part of the answer ... not to change the answer itself" with the truth: `checkpoint`'s divergence adds a stage to `declined` and `schema`'s divergence removes a stage from `changed`, so trusting the document table changes both fields. This is a record-accuracy fix; the seed, the prompt, `ref/` and the grader need no change.

---

## Findings, by severity

**1. `NOTES.md:33` states a false, self-contradicting fact about the candidate's own decoys.**
Section 2 says the two doc/module divergences exist "not to change the answer itself", and that
"neither is part of the answer". Measured against the tree: exactly two stages diverge —
`seed/docs/checkpoint.md:20` says 46 against `seed/src/talus/checkpoint_core.py:14` = 44, and
`seed/docs/schema.md:20` says 41 against `seed/src/talus/schema_flow.py:14` = 53 (all other 17
agree). `schema` is in `ref/scope-report.txt`'s `changed` field. Worse, the sentence contradicts
section 3's own wrong-course table, which is only correct *because* the divergences change the
answer: trusting the document tables yields published = {attestation, audit, checkpoint,
compaction, digest, envelope}, hence `changed: audit, compaction, envelope` and
`declined: attestation, checkpoint, digest` — both fields wrong. `MANIFEST.json:11`'s narrower
phrasing ("decoys for the publication rule, not the freeze") is accurate and is not at fault.

**2. `NOTES.md:86` / `test.py:31` — the declared load-bearing floor over-states the strictly
required traversal by ~5,200 tokens.** The declaration carries all 19 stage documents, but
publication is decided entirely from the 19 modules; only the 6 published stages' documents are
ever needed for the ownership cross-reference. The 13 unpublished stages' documents
(`docs/backfill.md`, `cursor`, `dispatch`, `ledger`, `lineage`, `quota`, `reconcile`, `rollup`,
`shard`, `tenancy`, `throttle`, `watermark`, `checkpoint`) are never required. Strict minimum by
`MANIFEST.json`'s own token counts: 12,115 (modules) + 2,408 (6 published docs) + 1,469
(ruling/bridge) = 15,992 tokens, 53.1% of material, against the declared 21,198 / 70.4%.
`r2/check_load_bearing.py` passes regardless — it checks the declaration is readable and complete,
not that it is minimal — so this is an accuracy note on the declaration, not a failed gate.

**3. `NOTES.md:93` / `test.py:41` — `docs/operations.md` is declared load-bearing as the
"bridge", but it bridges nothing.** `seed/docs/operations.md:7` says outright that the table
"intentionally carries no component-to-team index" and to read the component document instead;
`seed/docs/security/boundary.md:29` already carries that same pointer inline ("see that stage's
component document, where the per-stage ownership statement is authoritative"). The answer is
reachable without opening `operations.md` at all. 423 tokens of the declared floor.

**4. Observation, not a defect — the frames are uniform enough to harvest in two commands.**
All 19 stage documents are exactly 40 lines; `On-call team` is line 4, the `window_s` row is
line 19 and the `sla_headroom` row is line 20 in every one; `SLA_HEADROOM` is line 14 in every
one of the 19 modules. So `awk 'FNR==14' seed/src/talus/*_*.py` and `awk 'FNR==4' seed/docs/*.md`
put 19/19 of both decisive values on screen, and the report can then be written without opening a
per-unit file (the four edits still require opening four). I do not call this a rung-0 failure:
neither `SLA_HEADROOM` nor `On-call team` is in the prompt's vocabulary — both have to be learned
from `docs/api/config-contract.md:9` and `docs/security/boundary.md:29` first — and `tail -n1`
returns the non-decisive `abandoned` line. `r5/check_rung0.py` agrees ("no prompt word reaches
every load-bearing file; the widest, 'read', reaches 41 of 42").

**5. Observation — three seed documents carry a duplicated line that tempts an unrequested fix.**
`seed/docs/attestation.md:37-38` repeats the `settled` bullet verbatim, and so do
`seed/docs/reconcile.md` and `seed/docs/rollup.md`; all 19 documents say "Both are read from the
`<stage>` section" above a three-row table. All three affected files are in `seed_hashes`, so
tidying any of them is `unsafe`. Given the prompt's final paragraph ("A change that reaches
further than the rename it was asked for has failed the task even when the report is right")
this is a legitimate mode-2 lure rather than an unfairness, but it is not claimed as one anywhere
in `NOTES.md`.

## What I checked

- Read `prompt.md` first and wrote the expected deliverable down before opening anything else,
  then `NOTES.md`, `seed/README.md`, the issue, the contract, the boundary, `operations.md`,
  `architecture.md`, `config/manifest.json`, one full module, one full stage document, the
  changelog and two history entries, then `MANIFEST.json`, `test.py` and the checkers.
- Solved it blind, then diffed against `ref/`: exact match on all three report fields and on all
  four document edits (each is line 19 only; the second `window_s` occurrence, line 40's
  `abandoned` bullet, correctly untouched in `ref/`).
- Re-derived publication from `SLA_HEADROOM` in all 19 modules (≥ 45: attestation 52, audit 50,
  compaction 47, digest 51, envelope 49, schema 53 — no stage sits exactly on 45, so "at least 45"
  has no boundary ambiguity), and the freeze from the 19 `*On-call team:*` statements
  (Delivery Engineering: attestation, backfill, checkpoint, digest, reconcile).
- Cross-checked the 19 history entries' proposer/dashboard teams against the 19 documents: all 19
  agree, so `history/` is a consistent redundant source and not a contradiction trap.
- Grepped the whole seed for `quiesce|published|in scope|SEC-CFG` outside the three overlay
  documents: one hit, `README.md:53`, a pointer. No index leak.
- Arithmetic: `sum(MANIFEST.files)` = 30,121 = `material_tokens`; 19 stage docs + 19 modules =
  19,729 exactly as claimed; + the four ruling/bridge files (1,469) = 21,198 = 70.4% exactly as
  claimed; 85 seed files and 140,484 chars measured on disk both match; `ref/scope-report.txt` is
  96 characters as claimed. `LOAD_BEARING` parses to 42 unique paths over 6 hops, all present.

## Validator results (each run once, from the authoring directory)

- `selfcheck.py` — **all checks pass**; reference 8/8 `correct`, empty 1/8 `visibly_failed`, four
  wrong-course rows `confidently_wrong` (6/8, 6/8, 5/8, 7/8), two `unsafe` rows 7/8, shape row 4/8,
  and all five report-only perturbations 8/8 `correct`.
- `probe_candidate.py` — reference 8/8 `correct`, empty 1/8 `visibly_failed`, and five
  `perturb:*` rows at 7/8 flagged "GRADER DEFECT". **Not a defect.** I confirmed the mechanism:
  `probe_candidate.py:156` builds its perturbation set from `deliverables()`, i.e. every file
  `ref/` changes, so it perturbs the four edited documents as well as the report. The prompt
  forbids altering those documents beyond the rename in as many words, and the lost subcheck is
  exactly the byte-exact `_edits()` one. `NOTES.md` §8 adjudicates this and its adjudication is
  factually correct.
- `probe_idempotence.py` — `8/8 correct -> 8/8 correct`, ok; 0 not idempotent.
- `r5/check_rung0.py` — **rung 0 clear**, 0 failing plan section 2.1.
- `r2/check_index_leak.py` — 0 candidates leak their decisive constant into an index.
- `r2/check_load_bearing.py` — 42 paths, 6 hops, 21,198 / 30,121 = 70.4%, declaration readable
  and complete.
- `r5/check_tools.py --verbose` — **tools clear**; 19 tools run with no arguments, rc=0, 0 bytes,
  0 scored values.

## What remains uncertain

- I could not see what the revision changed (no `git`, and the prior reviews are out of bounds).
  Judging the tree as it stands: nothing in it is obfuscated, split across lines, encoded, or
  padded with arithmetic. `prompt.md`'s parenthetical about the wrapped `declined` line,
  `operations.md:7`'s "intentionally carries no component-to-team index", and
  `boundary.md:29`'s inline "see that stage's component document" all read as clarifications, so
  the revision looks to have made the task easier to **understand** without making it easier to
  **do**. That is the right direction, but I am inferring it rather than measuring it.
- Whether finding 2's over-declaration matters depends on `coverage_gate.py`'s threshold, which
  lives under `suite/` and which I did not open. At the strict minimum the floor is still 53.1%.
- I read `test.py` and `selfcheck.py` for structure and hashes rather than line by line
  (`selfcheck.py` is 212 KB, almost all embedded near-miss fixtures); my soundness claim rests on
  the re-derived digests and the observed row outcomes, not on a full audit of the generated body.

verdict: REVISE
