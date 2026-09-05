# cinder-vault

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
| dispatch | `src/dispatch_gate.py` | `docs/dispatch.md` | M. Lindqvist |
| cursor | `src/cursor_view.py` | `docs/cursor.md` | L. Achterberg |
| replay | `src/replay_core.py` | `docs/replay.md` | N. Oyelaran |
| quota | `src/quota_core.py` | `docs/quota.md` | S. Nwachukwu |
| drain | `src/drain_gate.py` | `docs/drain.md` | D. Ferreira |
| envelope | `src/envelope_flow.py` | `docs/envelope.md` | P. Ravindran |
| tenancy | `src/tenancy_core.py` | `docs/tenancy.md` | S. Nwachukwu |
| digest | `src/digest_flow.py` | `docs/digest.md` | T. Abarca |
| watermark | `src/watermark_flow.py` | `docs/watermark.md` | J. Maldonado |
| checkpoint | `src/checkpoint_gate.py` | `docs/checkpoint.md` | T. Abarca |
| backfill | `src/backfill_flow.py` | `docs/backfill.md` | N. Oyelaran |
| lineage | `src/lineage_view.py` | `docs/lineage.md` | D. Ferreira |
| shard | `src/shard_gate.py` | `docs/shard.md` | J. Maldonado |
| ingest | `src/ingest_gate.py` | `docs/ingest.md` | L. Achterberg |
| retention | `src/retention_gate.py` | `docs/retention.md` | L. Achterberg |
| rollup | `src/rollup_gate.py` | `docs/rollup.md` | R. Okonjo |
| attestation | `src/attestation_gate.py` | `docs/attestation.md` | E. Thorsdottir |
| ledger | `src/ledger_view.py` | `docs/ledger.md` | J. Maldonado |
| schema | `src/schema_flow.py` | `docs/schema.md` | N. Oyelaran |
| routing | `src/routing_flow.py` | `docs/routing.md` | N. Oyelaran |
| compaction | `src/compaction_view.py` | `docs/compaction.md` | T. Abarca |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
