# cinder-crest

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
| drain | `src/drain_store.py` | `docs/drain.md` | S. Nwachukwu |
| lineage | `src/lineage_flow.py` | `docs/lineage.md` | E. Thorsdottir |
| rollup | `src/rollup_flow.py` | `docs/rollup.md` | A. Villanueva |
| quota | `src/quota_flow.py` | `docs/quota.md` | P. Ravindran |
| compaction | `src/compaction_core.py` | `docs/compaction.md` | K. Sorensen |
| checkpoint | `src/checkpoint_view.py` | `docs/checkpoint.md` | E. Thorsdottir |
| reconcile | `src/reconcile_view.py` | `docs/reconcile.md` | D. Ferreira |
| shard | `src/shard_flow.py` | `docs/shard.md` | M. Lindqvist |
| audit | `src/audit_view.py` | `docs/audit.md` | E. Thorsdottir |
| attestation | `src/attestation_flow.py` | `docs/attestation.md` | T. Abarca |
| watermark | `src/watermark_flow.py` | `docs/watermark.md` | N. Oyelaran |
| backfill | `src/backfill_flow.py` | `docs/backfill.md` | P. Ravindran |
| digest | `src/digest_store.py` | `docs/digest.md` | H. Bergstrom |
| schema | `src/schema_gate.py` | `docs/schema.md` | C. Batbayar |
| replay | `src/replay_store.py` | `docs/replay.md` | R. Okonjo |
| cursor | `src/cursor_core.py` | `docs/cursor.md` | C. Batbayar |
| tenancy | `src/tenancy_core.py` | `docs/tenancy.md` | J. Maldonado |
| throttle | `src/throttle_store.py` | `docs/throttle.md` | L. Achterberg |
| ledger | `src/ledger_core.py` | `docs/ledger.md` | S. Nwachukwu |
| routing | `src/routing_gate.py` | `docs/routing.md` | A. Villanueva |
| ingest | `src/ingest_view.py` | `docs/ingest.md` | K. Sorensen |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
