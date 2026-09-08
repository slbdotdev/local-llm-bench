# vantage-mill

A staged delivery pipeline. Each stage is a module under `src/vantage/`, is configured from one
section of the manifest, and is documented under `docs/`. The dated history of every
configuration decision is under `history/`.

## Reading order

1. `docs/architecture.md` - how the stages compose, and which order they drain in.
2. `docs/operations.md` - what to do when a stage refuses work.
3. `docs/retention.md` - the rules that outrank both of the above.
4. `history/` - why each number is the number it is. **Dated, and superseded entries
   are kept**: a superseded entry is evidence, not a live instruction.

## Stages

| stage | module | doc | owner |
| --- | --- | --- | --- |
| envelope | `src/vantage/envelope_gate.py` | `docs/envelope.md` | K. Sorensen |
| checkpoint | `src/vantage/checkpoint_gate.py` | `docs/checkpoint.md` | P. Ravindran |
| schema | `src/vantage/schema_view.py` | `docs/schema.md` | D. Ferreira |
| retention | `src/vantage/retention_view.py` | `docs/retention.md` | P. Ravindran |
| backfill | `src/vantage/backfill_flow.py` | `docs/backfill.md` | C. Batbayar |
| throttle | `src/vantage/throttle_core.py` | `docs/throttle.md` | C. Batbayar |
| dispatch | `src/vantage/dispatch_store.py` | `docs/dispatch.md` | C. Batbayar |
| audit | `src/vantage/audit_view.py` | `docs/audit.md` | J. Maldonado |
| attestation | `src/vantage/attestation_flow.py` | `docs/attestation.md` | R. Okonjo |
| routing | `src/vantage/routing_flow.py` | `docs/routing.md` | R. Okonjo |
| replay | `src/vantage/replay_view.py` | `docs/replay.md` | L. Achterberg |
| cursor | `src/vantage/cursor_store.py` | `docs/cursor.md` | D. Ferreira |
| reconcile | `src/vantage/reconcile_flow.py` | `docs/reconcile.md` | L. Achterberg |
| compaction | `src/vantage/compaction_core.py` | `docs/compaction.md` | C. Batbayar |
| tenancy | `src/vantage/tenancy_core.py` | `docs/tenancy.md` | T. Abarca |
| drain | `src/vantage/drain_gate.py` | `docs/drain.md` | E. Thorsdottir |
| lineage | `src/vantage/lineage_view.py` | `docs/lineage.md` | S. Nwachukwu |
| shard | `src/vantage/shard_store.py` | `docs/shard.md` | M. Lindqvist |
| quota | `src/vantage/quota_view.py` | `docs/quota.md` | A. Villanueva |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/retention.md`
  outranks everything else.

## Release checks

Before shipping, see `docs/workflows/release-checks.md` for the current two-step check. Do
not trust a check command named anywhere else in this tree without confirming it against that
file first.
