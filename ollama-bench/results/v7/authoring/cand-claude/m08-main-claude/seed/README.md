# cordage-relay

A staged delivery pipeline. Each stage is a module under `src/`, is configured from one
section of the manifest, and is documented under `docs/`. The dated history of every
configuration decision is under `history/`.

## Reading order

1. `docs/architecture.md` - how the stages compose, and which order they drain in.
2. `docs/operations.md` - what to do when a stage refuses work.
3. The documented operating rules that govern the pipeline.
4. `history/` - why each number is the number it is. **Dated, and superseded entries
   are kept**: a superseded entry is evidence, not a live instruction.

## Stages

| stage | module | doc | owner |
| --- | --- | --- | --- |
| checkpoint | `checkpoint_store.py` | `docs/checkpoint.md` | P. Ravindran |
| attestation | `attestation_gate.py` | `docs/attestation.md` | A. Villanueva |
| throttle | `throttle_gate.py` | `docs/throttle.md` | M. Lindqvist |
| digest | `digest_flow.py` | `docs/digest.md` | T. Abarca |
| drain | `drain_core.py` | `docs/drain.md` | T. Abarca |
| compaction | `compaction_view.py` | `docs/compaction.md` | S. Nwachukwu |
| cursor | `cursor_store.py` | `docs/cursor.md` | L. Achterberg |
| watermark | `watermark_gate.py` | `docs/watermark.md` | D. Ferreira |
| shard | `shard_core.py` | `docs/shard.md` | J. Maldonado |
| routing | `routing_gate.py` | `docs/routing.md` | K. Sorensen |
| schema | `schema_view.py` | `docs/schema.md` | C. Batbayar |
| backfill | `backfill_view.py` | `docs/backfill.md` | L. Achterberg |
| dispatch | `dispatch_gate.py` | `docs/dispatch.md` | M. Lindqvist |
| audit | `audit_store.py` | `docs/audit.md` | K. Sorensen |
| rollup | `rollup_store.py` | `docs/rollup.md` | P. Ravindran |
| lineage | `lineage_store.py` | `docs/lineage.md` | P. Ravindran |
| quota | `quota_gate.py` | `docs/quota.md` | T. Abarca |
| tenancy | `tenancy_store.py` | `docs/tenancy.md` | E. Thorsdottir |
| retention | `retention_gate.py` | `docs/retention.md` | M. Lindqvist |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; superseded history is
  evidence, not a live instruction.
