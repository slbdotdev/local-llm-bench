# dogvane-mesh

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
| retention | `src/retention_gate.py` | `docs/retention.md` | A. Villanueva |
| lineage | `src/lineage_store.py` | `docs/lineage.md` | J. Maldonado |
| backfill | `src/backfill_flow.py` | `docs/backfill.md` | T. Abarca |
| dispatch | `src/dispatch_store.py` | `docs/dispatch.md` | T. Abarca |
| drain | `src/drain_store.py` | `docs/drain.md` | E. Thorsdottir |
| tenancy | `src/tenancy_core.py` | `docs/tenancy.md` | C. Batbayar |
| shard | `src/shard_view.py` | `docs/shard.md` | A. Villanueva |
| digest | `src/digest_gate.py` | `docs/digest.md` | T. Abarca |
| cursor | `src/cursor_gate.py` | `docs/cursor.md` | L. Achterberg |
| routing | `src/routing_flow.py` | `docs/routing.md` | E. Thorsdottir |
| watermark | `src/watermark_flow.py` | `docs/watermark.md` | K. Sorensen |
| replay | `src/replay_core.py` | `docs/replay.md` | P. Ravindran |
| throttle | `src/throttle_gate.py` | `docs/throttle.md` | S. Nwachukwu |
| reconcile | `src/reconcile_store.py` | `docs/reconcile.md` | A. Villanueva |
| envelope | `src/envelope_core.py` | `docs/envelope.md` | J. Maldonado |
| compaction | `src/compaction_flow.py` | `docs/compaction.md` | P. Ravindran |
| audit | `src/audit_core.py` | `docs/audit.md` | M. Lindqvist |
| rollup | `src/rollup_gate.py` | `docs/rollup.md` | E. Thorsdottir |
| attestation | `src/attestation_core.py` | `docs/attestation.md` | R. Okonjo |
| ingest | `src/ingest_core.py` | `docs/ingest.md` | R. Okonjo |
| schema | `src/schema_gate.py` | `docs/schema.md` | C. Batbayar |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
