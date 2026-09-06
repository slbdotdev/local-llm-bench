# cordage-mesh

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
| lineage | `src/lineage_store.py` | `docs/lineage.md` | R. Okonjo |
| rollup | `src/rollup_view.py` | `docs/rollup.md` | S. Nwachukwu |
| replay | `src/replay_gate.py` | `docs/replay.md` | C. Batbayar |
| backfill | `src/backfill_gate.py` | `docs/backfill.md` | S. Nwachukwu |
| digest | `src/digest_store.py` | `docs/digest.md` | J. Maldonado |
| throttle | `src/throttle_core.py` | `docs/throttle.md` | K. Sorensen |
| quota | `src/quota_view.py` | `docs/quota.md` | T. Abarca |
| shard | `src/shard_flow.py` | `docs/shard.md` | A. Villanueva |
| ingest | `src/ingest_gate.py` | `docs/ingest.md` | R. Okonjo |
| audit | `src/audit_flow.py` | `docs/audit.md` | M. Lindqvist |
| tenancy | `src/tenancy_core.py` | `docs/tenancy.md` | J. Maldonado |
| compaction | `src/compaction_store.py` | `docs/compaction.md` | R. Okonjo |
| cursor | `src/cursor_view.py` | `docs/cursor.md` | S. Nwachukwu |
| checkpoint | `src/checkpoint_gate.py` | `docs/checkpoint.md` | D. Ferreira |
| retention | `src/retention_flow.py` | `docs/retention.md` | S. Nwachukwu |
| dispatch | `src/dispatch_store.py` | `docs/dispatch.md` | T. Abarca |
| ledger | `src/ledger_flow.py` | `docs/ledger.md` | K. Sorensen |
| drain | `src/drain_core.py` | `docs/drain.md` | T. Abarca |
| envelope | `src/envelope_view.py` | `docs/envelope.md` | C. Batbayar |
| schema | `src/schema_store.py` | `docs/schema.md` | E. Thorsdottir |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Dwell audits

Every stage's dwell divergence from its module default is reported in the quarterly audit,
without exception.
