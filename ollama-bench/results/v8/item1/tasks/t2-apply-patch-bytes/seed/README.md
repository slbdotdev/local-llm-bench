# bollard-mesh

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
| throttle | `src/throttle_flow.py` | `docs/throttle.md` | J. Maldonado |
| envelope | `src/envelope_store.py` | `docs/envelope.md` | L. Achterberg |
| cursor | `src/cursor_store.py` | `docs/cursor.md` | E. Thorsdottir |
| quota | `src/quota_store.py` | `docs/quota.md` | D. Ferreira |
| ingest | `src/ingest_core.py` | `docs/ingest.md` | M. Lindqvist |
| retention | `src/retention_flow.py` | `docs/retention.md` | P. Ravindran |
| backfill | `src/backfill_view.py` | `docs/backfill.md` | M. Lindqvist |
| ledger | `src/ledger_core.py` | `docs/ledger.md` | H. Bergstrom |
| compaction | `src/compaction_gate.py` | `docs/compaction.md` | K. Sorensen |
| replay | `src/replay_flow.py` | `docs/replay.md` | L. Achterberg |
| routing | `src/routing_gate.py` | `docs/routing.md` | R. Okonjo |
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | J. Maldonado |
| rollup | `src/rollup_gate.py` | `docs/rollup.md` | N. Oyelaran |
| checkpoint | `src/checkpoint_core.py` | `docs/checkpoint.md` | H. Bergstrom |
| drain | `src/drain_flow.py` | `docs/drain.md` | R. Okonjo |
| digest | `src/digest_core.py` | `docs/digest.md` | D. Ferreira |
| dispatch | `src/dispatch_gate.py` | `docs/dispatch.md` | L. Achterberg |
| shard | `src/shard_store.py` | `docs/shard.md` | M. Lindqvist |
| schema | `src/schema_flow.py` | `docs/schema.md` | A. Villanueva |
| lineage | `src/lineage_flow.py` | `docs/lineage.md` | S. Nwachukwu |
| reconcile | `src/reconcile_view.py` | `docs/reconcile.md` | C. Batbayar |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
