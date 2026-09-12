# futtock-mesh

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
| ingest | `src/ingest_view.py` | `docs/ingest.md` | A. Villanueva |
| ledger | `src/ledger_core.py` | `docs/ledger.md` | R. Okonjo |
| envelope | `src/envelope_core.py` | `docs/envelope.md` | A. Villanueva |
| dispatch | `src/dispatch_core.py` | `docs/dispatch.md` | N. Oyelaran |
| retention | `src/retention_core.py` | `docs/retention.md` | H. Bergstrom |
| schema | `src/schema_flow.py` | `docs/schema.md` | T. Abarca |
| reconcile | `src/reconcile_flow.py` | `docs/reconcile.md` | T. Abarca |
| rollup | `src/rollup_view.py` | `docs/rollup.md` | P. Ravindran |
| attestation | `src/attestation_core.py` | `docs/attestation.md` | M. Lindqvist |
| routing | `src/routing_view.py` | `docs/routing.md` | M. Lindqvist |
| shard | `src/shard_store.py` | `docs/shard.md` | K. Sorensen |
| quota | `src/quota_view.py` | `docs/quota.md` | M. Lindqvist |
| compaction | `src/compaction_flow.py` | `docs/compaction.md` | L. Achterberg |
| backfill | `src/backfill_view.py` | `docs/backfill.md` | L. Achterberg |
| checkpoint | `src/checkpoint_view.py` | `docs/checkpoint.md` | C. Batbayar |
| drain | `src/drain_store.py` | `docs/drain.md` | H. Bergstrom |
| throttle | `src/throttle_view.py` | `docs/throttle.md` | C. Batbayar |
| cursor | `src/cursor_flow.py` | `docs/cursor.md` | J. Maldonado |
| replay | `src/replay_view.py` | `docs/replay.md` | M. Lindqvist |
| lineage | `src/lineage_gate.py` | `docs/lineage.md` | D. Ferreira |
| tenancy | `src/tenancy_view.py` | `docs/tenancy.md` | T. Abarca |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
