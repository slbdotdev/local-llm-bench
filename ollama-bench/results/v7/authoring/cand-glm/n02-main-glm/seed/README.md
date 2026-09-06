# linnet-slack

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
| shard | `src/shard_flow.py` | `docs/shard.md` | A. Villanueva |
| tenancy | `src/tenancy_store.py` | `docs/tenancy.md` | J. Maldonado |
| routing | `src/routing_core.py` | `docs/routing.md` | K. Sorensen |
| lineage | `src/lineage_core.py` | `docs/lineage.md` | T. Abarca |
| audit | `src/audit_gate.py` | `docs/audit.md` | A. Villanueva |
| watermark | `src/watermark_flow.py` | `docs/watermark.md` | A. Villanueva |
| retention | `src/retention_view.py` | `docs/retention.md` | N. Oyelaran |
| schema | `src/schema_store.py` | `docs/schema.md` | L. Achterberg |
| backfill | `src/backfill_gate.py` | `docs/backfill.md` | E. Thorsdottir |
| replay | `src/replay_flow.py` | `docs/replay.md` | M. Lindqvist |
| ledger | `src/ledger_core.py` | `docs/ledger.md` | H. Bergstrom |
| cursor | `src/cursor_gate.py` | `docs/cursor.md` | A. Villanueva |
| digest | `src/digest_gate.py` | `docs/digest.md` | P. Ravindran |
| dispatch | `src/dispatch_gate.py` | `docs/dispatch.md` | L. Achterberg |
| reconcile | `src/reconcile_store.py` | `docs/reconcile.md` | K. Sorensen |
| ingest | `src/ingest_view.py` | `docs/ingest.md` | P. Ravindran |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | D. Ferreira |
| quota | `src/quota_gate.py` | `docs/quota.md` | R. Okonjo |
| checkpoint | `src/checkpoint_flow.py` | `docs/checkpoint.md` | J. Maldonado |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Recheck bulletins

- `docs/bulletins/` - the recheck bulletin series, serial-numbered as mailed.
- `docs/precedents.md` - how the series is read: which bulletin governs a stage when several
  name one, what a stage's effective interval is, and the report's own vocabulary.
- `docs/recheck-handover.md` - a shift handover's notes about the series. Not reconciled
  with the record and kept only because the incoming shift asked for it in writing.
