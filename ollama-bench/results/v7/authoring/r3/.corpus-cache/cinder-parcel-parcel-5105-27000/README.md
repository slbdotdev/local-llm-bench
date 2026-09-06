# cinder-parcel

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
| replay | `src/replay_view.py` | `docs/replay.md` | H. Bergstrom |
| compaction | `src/compaction_view.py` | `docs/compaction.md` | T. Abarca |
| reconcile | `src/reconcile_core.py` | `docs/reconcile.md` | J. Maldonado |
| envelope | `src/envelope_flow.py` | `docs/envelope.md` | N. Oyelaran |
| checkpoint | `src/checkpoint_gate.py` | `docs/checkpoint.md` | S. Nwachukwu |
| rollup | `src/rollup_core.py` | `docs/rollup.md` | E. Thorsdottir |
| schema | `src/schema_flow.py` | `docs/schema.md` | N. Oyelaran |
| retention | `src/retention_flow.py` | `docs/retention.md` | P. Ravindran |
| quota | `src/quota_core.py` | `docs/quota.md` | C. Batbayar |
| audit | `src/audit_gate.py` | `docs/audit.md` | S. Nwachukwu |
| backfill | `src/backfill_flow.py` | `docs/backfill.md` | P. Ravindran |
| watermark | `src/watermark_gate.py` | `docs/watermark.md` | D. Ferreira |
| ingest | `src/ingest_core.py` | `docs/ingest.md` | P. Ravindran |
| cursor | `src/cursor_core.py` | `docs/cursor.md` | D. Ferreira |
| tenancy | `src/tenancy_core.py` | `docs/tenancy.md` | E. Thorsdottir |
| drain | `src/drain_gate.py` | `docs/drain.md` | T. Abarca |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | S. Nwachukwu |
| throttle | `src/throttle_core.py` | `docs/throttle.md` | S. Nwachukwu |
| routing | `src/routing_store.py` | `docs/routing.md` | K. Sorensen |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
