# larkspur-vault

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
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | N. Oyelaran |
| drain | `src/drain_flow.py` | `docs/drain.md` | H. Bergstrom |
| reconcile | `src/reconcile_flow.py` | `docs/reconcile.md` | N. Oyelaran |
| schema | `src/schema_gate.py` | `docs/schema.md` | D. Ferreira |
| quota | `src/quota_store.py` | `docs/quota.md` | D. Ferreira |
| audit | `src/audit_flow.py` | `docs/audit.md` | E. Thorsdottir |
| routing | `src/routing_gate.py` | `docs/routing.md` | P. Ravindran |
| digest | `src/digest_gate.py` | `docs/digest.md` | R. Okonjo |
| rollup | `src/rollup_core.py` | `docs/rollup.md` | N. Oyelaran |
| shard | `src/shard_store.py` | `docs/shard.md` | M. Lindqvist |
| attestation | `src/attestation_store.py` | `docs/attestation.md` | S. Nwachukwu |
| dispatch | `src/dispatch_flow.py` | `docs/dispatch.md` | R. Okonjo |
| compaction | `src/compaction_view.py` | `docs/compaction.md` | N. Oyelaran |
| ingest | `src/ingest_core.py` | `docs/ingest.md` | C. Batbayar |
| envelope | `src/envelope_flow.py` | `docs/envelope.md` | A. Villanueva |
| throttle | `src/throttle_view.py` | `docs/throttle.md` | J. Maldonado |
| lineage | `src/lineage_flow.py` | `docs/lineage.md` | N. Oyelaran |
| replay | `src/replay_core.py` | `docs/replay.md` | R. Okonjo |
| retention | `src/retention_gate.py` | `docs/retention.md` | L. Achterberg |
| checkpoint | `src/checkpoint_store.py` | `docs/checkpoint.md` | D. Ferreira |
| backfill | `src/backfill_core.py` | `docs/backfill.md` | H. Bergstrom |
| settle | `src/settle_gate.py` | `docs/settle.md` | P. Ravindran |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
