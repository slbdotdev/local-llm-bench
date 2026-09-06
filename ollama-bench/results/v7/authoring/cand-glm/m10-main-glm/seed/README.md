# solder-brook

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
| quota | `src/quota_core.py` | `docs/quota.md` | N. Oyelaran |
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | J. Maldonado |
| dispatch | `src/dispatch_flow.py` | `docs/dispatch.md` | L. Achterberg |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | N. Oyelaran |
| compaction | `src/compaction_view.py` | `docs/compaction.md` | S. Nwachukwu |
| ledger | `src/ledger_store.py` | `docs/ledger.md` | R. Okonjo |
| cursor | `src/cursor_core.py` | `docs/cursor.md` | P. Ravindran |
| lineage | `src/lineage_flow.py` | `docs/lineage.md` | A. Villanueva |
| retention | `src/retention_flow.py` | `docs/retention.md` | R. Okonjo |
| throttle | `src/throttle_view.py` | `docs/throttle.md` | S. Nwachukwu |
| checkpoint | `src/checkpoint_gate.py` | `docs/checkpoint.md` | S. Nwachukwu |
| reconcile | `src/reconcile_flow.py` | `docs/reconcile.md` | H. Bergstrom |
| shard | `src/shard_flow.py` | `docs/shard.md` | A. Villanueva |
| backfill | `src/backfill_view.py` | `docs/backfill.md` | S. Nwachukwu |
| ingest | `src/ingest_gate.py` | `docs/ingest.md` | L. Achterberg |
| envelope | `src/envelope_store.py` | `docs/envelope.md` | D. Ferreira |
| replay | `src/replay_gate.py` | `docs/replay.md` | H. Bergstrom |
| drain | `src/drain_flow.py` | `docs/drain.md` | K. Sorensen |
| routing | `src/routing_core.py` | `docs/routing.md` | M. Lindqvist |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Escalation contacts

`data/owner-directory.csv` and `data/escalation-secondary.csv` record where each stage's
escalation contact is filed, each under its own rule. See `docs/incidents/` for the current
known issue with these.
