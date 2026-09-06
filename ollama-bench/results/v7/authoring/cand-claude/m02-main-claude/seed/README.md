# talus-gate

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
| attestation | `src/attestation_store.py` | `docs/attestation.md` | M. Lindqvist |
| audit | `src/audit_flow.py` | `docs/audit.md` | M. Lindqvist |
| dispatch | `src/dispatch_gate.py` | `docs/dispatch.md` | R. Okonjo |
| compaction | `src/compaction_gate.py` | `docs/compaction.md` | P. Ravindran |
| backfill | `src/backfill_store.py` | `docs/backfill.md` | S. Nwachukwu |
| reconcile | `src/reconcile_core.py` | `docs/reconcile.md` | H. Bergstrom |
| shard | `src/shard_flow.py` | `docs/shard.md` | S. Nwachukwu |
| tenancy | `src/tenancy_view.py` | `docs/tenancy.md` | A. Villanueva |
| cursor | `src/cursor_gate.py` | `docs/cursor.md` | R. Okonjo |
| throttle | `src/throttle_view.py` | `docs/throttle.md` | L. Achterberg |
| quota | `src/quota_flow.py` | `docs/quota.md` | R. Okonjo |
| digest | `src/digest_flow.py` | `docs/digest.md` | J. Maldonado |
| rollup | `src/rollup_flow.py` | `docs/rollup.md` | J. Maldonado |
| watermark | `src/watermark_view.py` | `docs/watermark.md` | D. Ferreira |
| schema | `src/schema_flow.py` | `docs/schema.md` | L. Achterberg |
| ledger | `src/ledger_flow.py` | `docs/ledger.md` | N. Oyelaran |
| envelope | `src/envelope_gate.py` | `docs/envelope.md` | M. Lindqvist |
| lineage | `src/lineage_gate.py` | `docs/lineage.md` | P. Ravindran |
| checkpoint | `src/checkpoint_core.py` | `docs/checkpoint.md` | H. Bergstrom |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Contract and security material

- `docs/issues/` - numbered requests for a change, one file per issue.
- `docs/api/config-contract.md` - which stages' configuration surface is currently
  published, and by what rule.
- `docs/security/boundary.md` - clauses that freeze a team's stages against a class of
  change. Dated by clause number; superseded and withdrawn clauses are kept as evidence.
- `docs/operations.md` - the on-call table a freeze clause cites.
