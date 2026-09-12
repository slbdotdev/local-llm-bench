# capstan-mesh

A staged delivery pipeline. Each stage is a module under `src/`, is configured from one
section of the manifest, and is documented under `docs/`. The dated history of every
configuration decision is under `history/`.

## Reading order

1. `docs/architecture.md` - how the stages compose, and which order they drain in.
2. `docs/operations.md` - what to do when a stage refuses work.
3. `docs/policy/` - the rules that outrank both of the above.
4. `history/` - why each number is the number it is. **Dated, and superseded entries
   are kept**: a superseded entry is evidence, not a live instruction.

## Stages

| stage | module | doc | owner |
| --- | --- | --- | --- |
| checkpoint | `src/checkpoint_core.py` | `docs/checkpoint.md` | L. Achterberg |
| backfill | `src/backfill_view.py` | `docs/backfill.md` | N. Oyelaran |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | A. Villanueva |
| shard | `src/shard_flow.py` | `docs/shard.md` | M. Lindqvist |
| routing | `src/routing_flow.py` | `docs/routing.md` | A. Villanueva |
| rollup | `src/rollup_core.py` | `docs/rollup.md` | L. Achterberg |
| lineage | `src/lineage_core.py` | `docs/lineage.md` | J. Maldonado |
| compaction | `src/compaction_core.py` | `docs/compaction.md` | H. Bergstrom |
| cursor | `src/cursor_flow.py` | `docs/cursor.md` | M. Lindqvist |
| audit | `src/audit_flow.py` | `docs/audit.md` | T. Abarca |
| drain | `src/drain_store.py` | `docs/drain.md` | T. Abarca |
| watermark | `src/watermark_gate.py` | `docs/watermark.md` | N. Oyelaran |
| attestation | `src/attestation_flow.py` | `docs/attestation.md` | K. Sorensen |
| reconcile | `src/reconcile_gate.py` | `docs/reconcile.md` | S. Nwachukwu |
| replay | `src/replay_view.py` | `docs/replay.md` | R. Okonjo |
| envelope | `src/envelope_store.py` | `docs/envelope.md` | N. Oyelaran |
| quota | `src/quota_store.py` | `docs/quota.md` | C. Batbayar |
| schema | `src/schema_core.py` | `docs/schema.md` | L. Achterberg |
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | R. Okonjo |
| throttle | `src/throttle_flow.py` | `docs/throttle.md` | P. Ravindran |
| retention | `src/retention_store.py` | `docs/retention.md` | P. Ravindran |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
