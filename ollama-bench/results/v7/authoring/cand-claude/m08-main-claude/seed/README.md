# cordage-relay

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
| checkpoint | `src/checkpoint_store.py` | `docs/checkpoint.md` | P. Ravindran |
| attestation | `src/attestation_gate.py` | `docs/attestation.md` | A. Villanueva |
| throttle | `src/throttle_gate.py` | `docs/throttle.md` | M. Lindqvist |
| digest | `src/digest_flow.py` | `docs/digest.md` | T. Abarca |
| drain | `src/drain_core.py` | `docs/drain.md` | T. Abarca |
| compaction | `src/compaction_view.py` | `docs/compaction.md` | S. Nwachukwu |
| cursor | `src/cursor_store.py` | `docs/cursor.md` | L. Achterberg |
| watermark | `src/watermark_gate.py` | `docs/watermark.md` | D. Ferreira |
| shard | `src/shard_core.py` | `docs/shard.md` | J. Maldonado |
| routing | `src/routing_gate.py` | `docs/routing.md` | K. Sorensen |
| schema | `src/schema_view.py` | `docs/schema.md` | C. Batbayar |
| backfill | `src/backfill_view.py` | `docs/backfill.md` | L. Achterberg |
| dispatch | `src/dispatch_gate.py` | `docs/dispatch.md` | M. Lindqvist |
| audit | `src/audit_store.py` | `docs/audit.md` | K. Sorensen |
| rollup | `src/rollup_store.py` | `docs/rollup.md` | P. Ravindran |
| lineage | `src/lineage_store.py` | `docs/lineage.md` | P. Ravindran |
| quota | `src/quota_gate.py` | `docs/quota.md` | T. Abarca |
| tenancy | `src/tenancy_store.py` | `docs/tenancy.md` | E. Thorsdottir |
| retention | `src/retention_gate.py` | `docs/retention.md` | M. Lindqvist |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
