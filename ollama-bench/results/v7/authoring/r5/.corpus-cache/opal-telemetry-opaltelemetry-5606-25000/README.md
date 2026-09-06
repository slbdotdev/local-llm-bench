# opal-telemetry

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
| shard | `src/shard_core.py` | `docs/shard.md` | K. Sorensen |
| lineage | `src/lineage_store.py` | `docs/lineage.md` | L. Achterberg |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | E. Thorsdottir |
| schema | `src/schema_view.py` | `docs/schema.md` | N. Oyelaran |
| cursor | `src/cursor_core.py` | `docs/cursor.md` | K. Sorensen |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | R. Okonjo |
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | M. Lindqvist |
| digest | `src/digest_core.py` | `docs/digest.md` | L. Achterberg |
| checkpoint | `src/checkpoint_flow.py` | `docs/checkpoint.md` | H. Bergstrom |
| backfill | `src/backfill_view.py` | `docs/backfill.md` | S. Nwachukwu |
| compaction | `src/compaction_view.py` | `docs/compaction.md` | J. Maldonado |
| dispatch | `src/dispatch_core.py` | `docs/dispatch.md` | S. Nwachukwu |
| replay | `src/replay_core.py` | `docs/replay.md` | A. Villanueva |
| rollup | `src/rollup_store.py` | `docs/rollup.md` | C. Batbayar |
| ingest | `src/ingest_flow.py` | `docs/ingest.md` | J. Maldonado |
| retention | `src/retention_flow.py` | `docs/retention.md` | J. Maldonado |
| quota | `src/quota_flow.py` | `docs/quota.md` | L. Achterberg |
| routing | `src/routing_flow.py` | `docs/routing.md` | S. Nwachukwu |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
