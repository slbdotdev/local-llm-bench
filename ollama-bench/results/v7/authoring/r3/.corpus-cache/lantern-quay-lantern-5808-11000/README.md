# lantern-quay

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
| attestation | `src/attestation_view.py` | `docs/attestation.md` | T. Abarca |
| audit | `src/audit_core.py` | `docs/audit.md` | C. Batbayar |
| backfill | `src/backfill_gate.py` | `docs/backfill.md` | A. Villanueva |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | N. Oyelaran |
| cursor | `src/cursor_core.py` | `docs/cursor.md` | C. Batbayar |
| shard | `src/shard_view.py` | `docs/shard.md` | H. Bergstrom |
| ingest | `src/ingest_flow.py` | `docs/ingest.md` | P. Ravindran |
| compaction | `src/compaction_view.py` | `docs/compaction.md` | J. Maldonado |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
