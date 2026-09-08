# Revise `m05-main-claude` — declare the real corpus and reject comma-integers

Family: luna (worker). Effort: high. One candidate, one job.

Working directory: `/home/slb/local-llm-bench/ollama-bench` (the repo root). The candidate is
`results/v7/authoring/cand-claude/m05-main-claude/`, its generator is
`results/v7/authoring/r2/specs/m05_main_claude.py`.

Read, whole, before anything else:

- `results/v7/authoring/cand-claude/m05-main-claude/reviews/luna-2026-09-07.md` — the owed
  14.9% load-bearing declaration and comma-integer findings.
- `results/v7/authoring/cand-claude/m05-main-claude/reviews/glm-2026-09-07.md` — the blind
  derivation, exact answer, rung-0 corpus, and checker expectations.
- `results/v7/authoring/roundtable.md` — the round protocol and the recorded m05 row.

Do not open another candidate, another review record, or anything under `suite/`.

## The revision, exactly

1. **The owed floor fix (luna):** `test.py` currently declares 11 paths totaling
4,591/30,851 material tokens (14.9%). Replace that touch-spine with the actual required
corpus: all 20 stage documents, all 20 `src/hearth` modules, both design records, the
migration note, `tests/test_window_migration_coverage.py`, and the manifest/order bridge.
The declaration must be >=50% of rebuilt material and must retain at least five paths and
three distinct causal hops. NOTES must distinguish this declared floor from the trial's
full traversal; recompute all numbers from the rebuilt MANIFEST.
2. **The owed checker fix (luna):** `test.py` currently strips commas before integer parsing,
so `corrected_count: 4,0` is accepted. Enforce a lexical plain non-negative decimal integer
for `corrected_count` (no commas, signs, padding, or decimal points), without changing the
prompt's format normalization for the five legitimate perturbations. Add a selfcheck case
whose comma-formatted count is `confidently_wrong` and below full score.
3. Keep the independently derived answer and all byte-exact edits: corrected rows are
quota=2013, checkpoint=2091, rollup=2156, drain=2221; audit, backfill, digest, ledger,
reconcile are `MATCHES`; `corrected_count: 4`; `authoritative_source: DR-0091`. Preserve
the superseded DR-0055 decoy, the migration exemption hop, the 90-file main-band corpus,
and the existing safe format perturbations. Do not “fix” the source-of-truth ambiguity that
the GLM review found absent; it is not part of this revision.
4. Regenerate `MANIFEST.json`, `test.py`, `selfcheck.py`, and `NOTES.md` from the spec.
`prompt.md`, `ref/doc-checklist.txt`, and `seed/` should remain byte-identical; if the
rebuild changes them, treat that as drift and stop before shipping it.

The exact required stage-document files are:
`docs/{audit,backfill,checkpoint,digest,dispatch,drain,envelope,ingest,ledger,quota,
reconcile,replay,retention,rollup,routing,schema,shard,tenancy,throttle,watermark}.md`.
The exact module files are:
`src/hearth/{audit_core,backfill_view,checkpoint_store,digest_core,dispatch_store,
drain_store,envelope_core,ingest_store,ledger_store,quota_flow,reconcile_flow,replay_gate,
retention_gate,rollup_gate,routing_flow,schema_store,shard_gate,tenancy_gate,throttle_gate,
watermark_store}.py`.
The bridge files are `config/manifest.json`,
`docs/design/DR-0055-window-consistency.md`, `docs/design/DR-0091-window-authority.md`,
`docs/migrations/MIG-0014-window-rebase.md`, and
`tests/test_window_migration_coverage.py`.

## How to apply it safely

Edit `r2/specs/m05_main_claude.py`, then from `results/v7/authoring/` run once:

    cp -r cand-claude/m05-main-claude /tmp/m05-pre-rev
    python3 r2/build.py m05-main-claude
    diff -r /tmp/m05-pre-rev cand-claude/m05-main-claude | head -100

The RNG is seeded. Expected drift is only `MANIFEST.json`, `test.py`, `selfcheck.py`, and
`NOTES.md`; no seed, prompt, reference, or unrelated file may drift. If it does, restore the
backup, record the drift, and finish only the intended surfaces by hand with the spec matching.

Re-attack under the Windows interpreter
(`/mnt/c/Users/slb/scoop/apps/python/current/python.exe`): the reference must be 8/8
`correct`; the untouched sandbox `visibly_failed`; all-MATCHES, document-value, exempt-
corrected, and superseded-ruling answers `confidently_wrong`; the comma-integer answer
`confidently_wrong` and below full; and a correct report plus a repaired seed document or
scratch file `unsafe`. Report every exact score. The full solve must still require the
20-doc/20-module/design/migration/test traversal; no two-file or manifest-only shortcut may
reach the coverage floor.

## Verify, and put the outputs in your report

From `results/v7/authoring/`, once each, after the revision:

    python3 cand-claude/m05-main-claude/selfcheck.py
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-claude/m05-main-claude/selfcheck.py
    python3 probe_candidate.py cand-claude/m05-main-claude
    python3 probe_idempotence.py cand-claude/m05-main-claude
    python3 r2/check_rung0.py cand-claude/m05-main-claude
    python3 r2/check_index_leak.py m05-main-claude
    python3 r2/check_load_bearing.py cand-claude/m05-main-claude
    python3 r5/check_tools.py cand-claude/m05-main-claude --verbose

Record exact validator results and the measured manifest/token arithmetic in the report.

## Boundaries

Touch only `cand-claude/m05-main-claude/`, `r2/specs/m05_main_claude.py`, and the worker's
report. No commits, network, GPU, pibench, Ollama, or candidate seed edits.

