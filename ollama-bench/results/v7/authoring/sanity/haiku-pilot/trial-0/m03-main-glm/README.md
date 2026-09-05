# northgate-relay

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
| reconcile | `src/reconcile_gate.py` | `docs/reconcile.md` | S. Nwachukwu |
| throttle | `src/throttle_flow.py` | `docs/throttle.md` | N. Oyelaran |
| backfill | `src/backfill_gate.py` | `docs/backfill.md` | C. Batbayar |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | M. Lindqvist |
| checkpoint | `src/checkpoint_store.py` | `docs/checkpoint.md` | N. Oyelaran |
| compaction | `src/compaction_store.py` | `docs/compaction.md` | R. Okonjo |
| watermark | `src/watermark_core.py` | `docs/watermark.md` | S. Nwachukwu |
| ledger | `src/ledger_flow.py` | `docs/ledger.md` | T. Abarca |
| dispatch | `src/dispatch_view.py` | `docs/dispatch.md` | D. Ferreira |
| replay | `src/replay_store.py` | `docs/replay.md` | P. Ravindran |
| envelope | `src/envelope_store.py` | `docs/envelope.md` | R. Okonjo |
| audit | `src/audit_view.py` | `docs/audit.md` | S. Nwachukwu |
| routing | `src/routing_gate.py` | `docs/routing.md` | N. Oyelaran |
| retention | `src/retention_core.py` | `docs/retention.md` | L. Achterberg |
| digest | `src/digest_gate.py` | `docs/digest.md` | D. Ferreira |
| schema | `src/schema_flow.py` | `docs/schema.md` | M. Lindqvist |
| rollup | `src/rollup_gate.py` | `docs/rollup.md` | H. Bergstrom |
| quota | `src/quota_store.py` | `docs/quota.md` | S. Nwachukwu |
| lineage | `src/lineage_flow.py` | `docs/lineage.md` | M. Lindqvist |
| shard | `src/shard_gate.py` | `docs/shard.md` | D. Ferreira |
| cursor | `src/cursor_gate.py` | `docs/cursor.md` | P. Ravindran |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
