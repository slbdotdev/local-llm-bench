# kestrel-yard

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
| envelope | `src/envelope_view.py` | `docs/envelope.md` | P. Ravindran |
| schema | `src/schema_flow.py` | `docs/schema.md` | J. Maldonado |
| rollup | `src/rollup_core.py` | `docs/rollup.md` | L. Achterberg |
| compaction | `src/compaction_core.py` | `docs/compaction.md` | D. Ferreira |
| settlement | `src/settlement_view.py` | `docs/settlement.md` | K. Sorensen |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | E. Thorsdottir |
| watermark | `src/watermark_flow.py` | `docs/watermark.md` | E. Thorsdottir |
| throttle | `src/throttle_gate.py` | `docs/throttle.md` | S. Nwachukwu |
| dispatch | `src/dispatch_view.py` | `docs/dispatch.md` | E. Thorsdottir |
| quota | `src/quota_store.py` | `docs/quota.md` | L. Achterberg |
| audit | `src/audit_core.py` | `docs/audit.md` | T. Abarca |
| lineage | `src/lineage_flow.py` | `docs/lineage.md` | M. Lindqvist |
| checkpoint | `src/checkpoint_flow.py` | `docs/checkpoint.md` | E. Thorsdottir |
| replay | `src/replay_flow.py` | `docs/replay.md` | P. Ravindran |
| tenancy | `src/tenancy_core.py` | `docs/tenancy.md` | H. Bergstrom |
| shard | `src/shard_core.py` | `docs/shard.md` | H. Bergstrom |
| backfill | `src/backfill_store.py` | `docs/backfill.md` | A. Villanueva |
| digest | `src/digest_flow.py` | `docs/digest.md` | E. Thorsdottir |
| cursor | `src/cursor_flow.py` | `docs/cursor.md` | H. Bergstrom |
| ingest | `src/ingest_gate.py` | `docs/ingest.md` | L. Achterberg |
| reconcile | `src/reconcile_view.py` | `docs/reconcile.md` | E. Thorsdottir |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
