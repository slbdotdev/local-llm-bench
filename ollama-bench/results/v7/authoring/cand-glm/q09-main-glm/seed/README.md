# kestrel-turn

A staged delivery pipeline. Each stage is a module under `src/`, is configured from one
section of the manifest, and is documented under `docs/`. The dated history of every
configuration decision is under `history/`.

## Reading order

1. `docs/architecture.md` - how the stages compose, and which order they drain in.
2. `docs/operations.md` - what to do when a stage refuses work.
3. `docs/handbook/` - the rules that outrank both of the above.
4. `history/` - why each number is the number it is. **Dated, and superseded entries
   are kept**: a superseded entry is evidence, not a live instruction.

## Stages

| stage | module | doc | owner |
| --- | --- | --- | --- |
| schema | `src/schema_gate.py` | `docs/schema.md` | P. Ravindran |
| audit | `src/audit_view.py` | `docs/audit.md` | J. Maldonado |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | H. Bergstrom |
| rollup | `src/rollup_flow.py` | `docs/rollup.md` | A. Villanueva |
| watermark | `src/watermark_store.py` | `docs/watermark.md` | A. Villanueva |
| replay | `src/replay_gate.py` | `docs/replay.md` | P. Ravindran |
| lineage | `src/lineage_core.py` | `docs/lineage.md` | D. Ferreira |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | C. Batbayar |
| digest | `src/digest_gate.py` | `docs/digest.md` | S. Nwachukwu |
| drain | `src/drain_core.py` | `docs/drain.md` | D. Ferreira |
| envelope | `src/envelope_store.py` | `docs/envelope.md` | J. Maldonado |
| compaction | `src/compaction_flow.py` | `docs/compaction.md` | K. Sorensen |
| shard | `src/shard_flow.py` | `docs/shard.md` | D. Ferreira |
| dispatch | `src/dispatch_view.py` | `docs/dispatch.md` | J. Maldonado |
| reconcile | `src/reconcile_flow.py` | `docs/reconcile.md` | J. Maldonado |
| routing | `src/routing_flow.py` | `docs/routing.md` | T. Abarca |
| ingest | `src/ingest_store.py` | `docs/ingest.md` | D. Ferreira |
| checkpoint | `src/checkpoint_view.py` | `docs/checkpoint.md` | E. Thorsdottir |
| backfill | `src/backfill_store.py` | `docs/backfill.md` | T. Abarca |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/handbook/`
  outranks everything else.

## Settlement material

- `docs/handbook/settlement-procedure.md` - the settlement procedure, and the replay
  rules that govern this cycle's settlement.
- `data/settlement-log.csv` - the cycle's settlement log as the clerks filed it.
- `tools/settlement_status.py` - prints the log as filed and resolves the opening entry.
- Each finished cycle's close summary is filed under `docs/` with the quarter in its name.
