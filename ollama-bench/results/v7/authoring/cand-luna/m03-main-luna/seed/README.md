# wardstone-flux

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
| lineage | `src/lineage_view.py` | `docs/lineage.md` | N. Oyelaran |
| schema | `src/schema_gate.py` | `docs/schema.md` | E. Thorsdottir |
| drain | `src/drain_gate.py` | `docs/drain.md` | K. Sorensen |
| replay | `src/replay_core.py` | `docs/replay.md` | C. Batbayar |
| dispatch | `src/dispatch_flow.py` | `docs/dispatch.md` | N. Oyelaran |
| compaction | `src/compaction_flow.py` | `docs/compaction.md` | C. Batbayar |
| retention | `src/retention_flow.py` | `docs/retention.md` | N. Oyelaran |
| routing | `src/routing_core.py` | `docs/routing.md` | N. Oyelaran |
| attestation | `src/attestation_gate.py` | `docs/attestation.md` | J. Maldonado |
| digest | `src/digest_core.py` | `docs/digest.md` | R. Okonjo |
| checkpoint | `src/checkpoint_core.py` | `docs/checkpoint.md` | P. Ravindran |
| envelope | `src/envelope_store.py` | `docs/envelope.md` | A. Villanueva |
| cursor | `src/cursor_gate.py` | `docs/cursor.md` | D. Ferreira |
| reconcile | `src/reconcile_gate.py` | `docs/reconcile.md` | M. Lindqvist |
| throttle | `src/throttle_gate.py` | `docs/throttle.md` | E. Thorsdottir |
| rollup | `src/rollup_core.py` | `docs/rollup.md` | L. Achterberg |
| backfill | `src/backfill_view.py` | `docs/backfill.md` | C. Batbayar |
| shard | `src/shard_flow.py` | `docs/shard.md` | R. Okonjo |
| audit | `src/audit_gate.py` | `docs/audit.md` | T. Abarca |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## This quarter's capacity-exception inventory

Already compiled — see `docs/legacy-capacity-list.md`.
