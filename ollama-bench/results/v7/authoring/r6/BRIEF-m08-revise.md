# Revise `m08-main-claude` — lift the load-bearing floor and prove rung 0

Family: luna (worker). Effort: high. One candidate, one job.

Working directory: `/home/slb/local-llm-bench/ollama-bench` (the repo root). The candidate is
`results/v7/authoring/cand-claude/m08-main-claude/`, its generator is
`results/v7/authoring/r2/specs/m08_main_claude.py`.

Read, whole, before anything else:

- `results/v7/authoring/cand-claude/m08-main-claude/reviews/luna-2026-09-07.md` — the owed
  7.37% declaration and rung-0 finding.
- `results/v7/authoring/cand-claude/m08-main-claude/reviews/glm-2026-09-07.md` — the blind
  derivation, exact answer, required docs/source sweep, and checker limits.
- `results/v7/authoring/roundtable.md` — the round protocol and the recorded m08 row.

Do not open another candidate, another review record, or anything under `suite/`.

## The revision, exactly

1. **The owed floor fix (luna):** `test.py` currently declares seven paths totaling
2,209/29,984 material tokens (7.37%). Replace that declaration with the actual required
corpus: all 19 stage documents and all 19 `src/cordage` modules, plus the incident,
`docs/pending-migrations.md`, `docs/compatibility-guards.md`, `history/0003-digest.md`,
and `tests/test_quota.py`. The declared set must clear 50% of rebuilt material, retain at
least six paths and three causal hops, and state the measured token total and percentage in
NOTES. The docs/source sweep is about 21,556/29,984 tokens before the tracking pair, so
recompute rather than copy that review figure; if the per-file map rounds to 29,987 while
the whole-corpus value is 29,984, label the two units honestly and do not invent a
reconciliation.
2. **Make rung 0 explicit and testable:** retain the structural separation that the GLM
review verified — the incident gives the disagreement criterion but not `watermark`, the
effective `CA-07` is only in `src/cordage/watermark_gate.py`, and the two keyed tracking
documents separately supply `history/0003-digest.md` and `tests/test_quota.py`. Add generator
assertions/NOTES text that no incident or single tracking file names the complete answer and
that docs-only harvesting cannot produce the exact primary-module path. Run the rung-0 and
index-leak checkers; do not weaken the docs-vs-tree path trap or remove the answer-neutral
`docs/policy/` dangling reference unless the checker forces it.
3. Regenerate `MANIFEST.json`, `test.py`, `selfcheck.py`, and `NOTES.md`. Keep `prompt.md`,
`seed/`, and `ref/closeout.txt` byte-identical unless a build-time assertion proves a
necessary deterministic change. Preserve the exact answer:
`primary_module: src/cordage/watermark_gate.py`,
`migration_record: history/0003-digest.md`,
`compatibility_test: tests/test_quota.py`.

The exact stage-document files are:
`docs/{attestation,audit,backfill,checkpoint,compaction,cursor,digest,dispatch,drain,
lineage,quota,retention,rollup,routing,schema,shard,tenancy,throttle,watermark}.md`.
The exact source sweep is:
`src/cordage/{attestation_gate,audit_store,backfill_view,checkpoint_store,compaction_view,
cursor_store,digest_flow,dispatch_gate,drain_core,lineage_store,quota_gate,retention_gate,
rollup_store,routing_gate,schema_view,shard_core,tenancy_store,throttle_store,
watermark_gate}.py`.
The additional exact bridge files are `docs/incidents/2035-04-shed-count-drift.md`,
`docs/pending-migrations.md`, `docs/compatibility-guards.md`,
`history/0003-digest.md`, and `tests/test_quota.py`.

## How to apply it safely

Edit `r2/specs/m08_main_claude.py`, then from `results/v7/authoring/` run once:

    cp -r cand-claude/m08-main-claude /tmp/m08-pre-rev
    python3 r2/build.py m08-main-claude
    diff -r /tmp/m08-pre-rev cand-claude/m08-main-claude | head -100

The RNG is seeded. Expected drift is limited to `MANIFEST.json`, `test.py`, `selfcheck.py`,
and `NOTES.md`; no seed, prompt, reference, or unrelated file may drift. If anything else
changes, restore the backup, record the drift, and finish the intended surfaces by hand with
the spec consistent.

Re-attack under the Windows interpreter
(`/mnt/c/Users/slb/scoop/apps/python/current/python.exe`): reference (7/7, `correct`),
untouched sandbox (`visibly_failed`), decoy-primary, decoy-tracking-row, swapped-values,
and wrong-order deliverables (`confidently_wrong`), plus a correct report with a scratch
file (`unsafe`). Also run a docs-only/targeted shortcut and record its score and rung-0
coverage failure; it must not reach full acceptance.

## Verify, and put the outputs in your report

From `results/v7/authoring/`, once each, after the revision:

    python3 cand-claude/m08-main-claude/selfcheck.py
    /mnt/c/Users/slb/scoop/apps/python/current/python.exe cand-claude/m08-main-claude/selfcheck.py
    python3 probe_candidate.py cand-claude/m08-main-claude
    python3 probe_idempotence.py cand-claude/m08-main-claude
    python3 r2/check_rung0.py cand-claude/m08-main-claude
    python3 r2/check_index_leak.py m08-main-claude
    python3 r2/check_load_bearing.py cand-claude/m08-main-claude
    python3 r5/check_tools.py cand-claude/m08-main-claude --verbose

Record exact results, including the rebuilt MANIFEST arithmetic, load-bearing percentage,
and every shortcut score. No candidate edits outside the generated surfaces, no commits,
network, GPU, pibench, or Ollama.

## Boundaries

Touch only `cand-claude/m08-main-claude/`, `r2/specs/m08_main_claude.py`, and the worker's
report. The review-noted module-path divergence and dangling `docs/policy/` reference are
answer-neutral and must be left alone unless a validator demonstrates otherwise.

