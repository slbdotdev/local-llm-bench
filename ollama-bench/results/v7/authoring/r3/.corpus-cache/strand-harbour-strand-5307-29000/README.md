# strand-harbour

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
| attestation | `src/attestation_core.py` | `docs/attestation.md` | D. Ferreira |
| cursor | `src/cursor_store.py` | `docs/cursor.md` | P. Ravindran |
| digest | `src/digest_store.py` | `docs/digest.md` | E. Thorsdottir |
| quota | `src/quota_gate.py` | `docs/quota.md` | M. Lindqvist |
| checkpoint | `src/checkpoint_store.py` | `docs/checkpoint.md` | D. Ferreira |
| throttle | `src/throttle_flow.py` | `docs/throttle.md` | P. Ravindran |
| reconcile | `src/reconcile_view.py` | `docs/reconcile.md` | M. Lindqvist |
| audit | `src/audit_view.py` | `docs/audit.md` | H. Bergstrom |
| envelope | `src/envelope_core.py` | `docs/envelope.md` | K. Sorensen |
| backfill | `src/backfill_gate.py` | `docs/backfill.md` | L. Achterberg |
| compaction | `src/compaction_store.py` | `docs/compaction.md` | S. Nwachukwu |
| dispatch | `src/dispatch_flow.py` | `docs/dispatch.md` | P. Ravindran |
| watermark | `src/watermark_store.py` | `docs/watermark.md` | M. Lindqvist |
| tenancy | `src/tenancy_store.py` | `docs/tenancy.md` | N. Oyelaran |
| ledger | `src/ledger_store.py` | `docs/ledger.md` | L. Achterberg |
| replay | `src/replay_store.py` | `docs/replay.md` | J. Maldonado |
| rollup | `src/rollup_core.py` | `docs/rollup.md` | N. Oyelaran |
| drain | `src/drain_gate.py` | `docs/drain.md` | K. Sorensen |
| retention | `src/retention_core.py` | `docs/retention.md` | K. Sorensen |
| ingest | `src/ingest_store.py` | `docs/ingest.md` | J. Maldonado |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
