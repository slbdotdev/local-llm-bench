# thistle-works

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
| lineage | `src/lineage_flow.py` | `docs/lineage.md` | T. Abarca |
| retention | `src/retention_view.py` | `docs/retention.md` | J. Maldonado |
| compaction | `src/compaction_store.py` | `docs/compaction.md` | D. Ferreira |
| watermark | `src/watermark_core.py` | `docs/watermark.md` | K. Sorensen |
| dispatch | `src/dispatch_gate.py` | `docs/dispatch.md` | N. Oyelaran |
| shard | `src/shard_view.py` | `docs/shard.md` | K. Sorensen |
| ingest | `src/ingest_view.py` | `docs/ingest.md` | T. Abarca |
| schema | `src/schema_core.py` | `docs/schema.md` | P. Ravindran |
| digest | `src/digest_flow.py` | `docs/digest.md` | H. Bergstrom |
| backfill | `src/backfill_gate.py` | `docs/backfill.md` | L. Achterberg |
| attestation | `src/attestation_gate.py` | `docs/attestation.md` | M. Lindqvist |
| cursor | `src/cursor_view.py` | `docs/cursor.md` | P. Ravindran |
| rollup | `src/rollup_flow.py` | `docs/rollup.md` | A. Villanueva |
| checkpoint | `src/checkpoint_flow.py` | `docs/checkpoint.md` | T. Abarca |
| routing | `src/routing_gate.py` | `docs/routing.md` | D. Ferreira |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | H. Bergstrom |
| reconcile | `src/reconcile_gate.py` | `docs/reconcile.md` | A. Villanueva |
| throttle | `src/throttle_store.py` | `docs/throttle.md` | A. Villanueva |
| drain | `src/drain_gate.py` | `docs/drain.md` | P. Ravindran |
| envelope | `src/envelope_flow.py` | `docs/envelope.md` | K. Sorensen |
| audit | `src/audit_flow.py` | `docs/audit.md` | R. Okonjo |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
