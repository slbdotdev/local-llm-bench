# brindle-quay

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
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | C. Batbayar |
| rollup | `src/rollup_store.py` | `docs/rollup.md` | J. Maldonado |
| digest | `src/digest_flow.py` | `docs/digest.md` | A. Villanueva |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | J. Maldonado |
| throttle | `src/throttle_flow.py` | `docs/throttle.md` | A. Villanueva |
| lineage | `src/lineage_core.py` | `docs/lineage.md` | J. Maldonado |
| compaction | `src/compaction_flow.py` | `docs/compaction.md` | J. Maldonado |
| cursor | `src/cursor_core.py` | `docs/cursor.md` | J. Maldonado |
| watermark | `src/watermark_core.py` | `docs/watermark.md` | M. Lindqvist |
| ledger | `src/ledger_flow.py` | `docs/ledger.md` | L. Achterberg |
| checkpoint | `src/checkpoint_core.py` | `docs/checkpoint.md` | D. Ferreira |
| drain | `src/drain_gate.py` | `docs/drain.md` | R. Okonjo |
| retention | `src/retention_core.py` | `docs/retention.md` | H. Bergstrom |
| replay | `src/replay_flow.py` | `docs/replay.md` | C. Batbayar |
| backfill | `src/backfill_core.py` | `docs/backfill.md` | S. Nwachukwu |
| schema | `src/schema_flow.py` | `docs/schema.md` | T. Abarca |
| envelope | `src/envelope_flow.py` | `docs/envelope.md` | C. Batbayar |
| routing | `src/routing_core.py` | `docs/routing.md` | A. Villanueva |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Release material

- `docs/release/` - the numbered release records: what a stage has to satisfy to ship, how a
  readiness report is filed, and what a stage's release class means. The filing rules travel
  with whichever record is in force and are not repeated here. A record marked **in
  force** applies; a record marked **superseded** is kept as evidence because later reasoning
  cites it, and is never a live instruction.
- `tools/check_record.py` - checks that one dated record under `history/` is well formed. It
  reads the single record you name and nothing else, and it changes nothing.
