# HarborAtlas

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
| compaction | `src/compaction_gate.py` | `docs/compaction.md` | P. Ravindran |
| lineage | `src/lineage_core.py` | `docs/lineage.md` | M. Lindqvist |
| backfill | `src/backfill_flow.py` | `docs/backfill.md` | R. Okonjo |
| drain | `src/drain_store.py` | `docs/drain.md` | E. Thorsdottir |
| rollup | `src/rollup_store.py` | `docs/rollup.md` | C. Batbayar |
| routing | `src/routing_store.py` | `docs/routing.md` | A. Villanueva |
| envelope | `src/envelope_store.py` | `docs/envelope.md` | N. Oyelaran |
| retention | `src/retention_core.py` | `docs/retention.md` | K. Sorensen |
| dispatch | `src/dispatch_flow.py` | `docs/dispatch.md` | T. Abarca |
| throttle | `src/throttle_core.py` | `docs/throttle.md` | J. Maldonado |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | J. Maldonado |
| schema | `src/schema_view.py` | `docs/schema.md` | N. Oyelaran |
| cursor | `src/cursor_core.py` | `docs/cursor.md` | L. Achterberg |
| quota | `src/quota_flow.py` | `docs/quota.md` | T. Abarca |
| digest | `src/digest_view.py` | `docs/digest.md` | R. Okonjo |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | N. Oyelaran |
| shard | `src/shard_flow.py` | `docs/shard.md` | M. Lindqvist |
| checkpoint | `src/checkpoint_view.py` | `docs/checkpoint.md` | S. Nwachukwu |
| ingest | `src/ingest_core.py` | `docs/ingest.md` | M. Lindqvist |
| audit | `src/audit_core.py` | `docs/audit.md` | P. Ravindran |
| tenancy | `src/tenancy_view.py` | `docs/tenancy.md` | L. Achterberg |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
