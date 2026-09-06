# sable-arc

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
| backfill | `src/backfill_store.py` | `docs/backfill.md` | C. Batbayar |
| checkpoint | `src/checkpoint_flow.py` | `docs/checkpoint.md` | M. Lindqvist |
| shard | `src/shard_flow.py` | `docs/shard.md` | A. Villanueva |
| replay | `src/replay_store.py` | `docs/replay.md` | S. Nwachukwu |
| drain | `src/drain_store.py` | `docs/drain.md` | R. Okonjo |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | J. Maldonado |
| compaction | `src/compaction_store.py` | `docs/compaction.md` | S. Nwachukwu |
| reconcile | `src/reconcile_view.py` | `docs/reconcile.md` | T. Abarca |
| tenancy | `src/tenancy_core.py` | `docs/tenancy.md` | N. Oyelaran |
| ingest | `src/ingest_core.py` | `docs/ingest.md` | S. Nwachukwu |
| quota | `src/quota_view.py` | `docs/quota.md` | M. Lindqvist |
| attestation | `src/attestation_gate.py` | `docs/attestation.md` | R. Okonjo |
| routing | `src/routing_store.py` | `docs/routing.md` | T. Abarca |
| watermark | `src/watermark_flow.py` | `docs/watermark.md` | J. Maldonado |
| dispatch | `src/dispatch_flow.py` | `docs/dispatch.md` | A. Villanueva |
| retention | `src/retention_view.py` | `docs/retention.md` | L. Achterberg |
| digest | `src/digest_view.py` | `docs/digest.md` | M. Lindqvist |
| throttle | `src/throttle_core.py` | `docs/throttle.md` | C. Batbayar |
| audit | `src/audit_core.py` | `docs/audit.md` | R. Okonjo |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Retention review material

- `docs/retention-glossary.md` — definitions, including the project's reporting term.
- `docs/decisions/` — dated policy records; the latest active record controls the reporting date.
- `data/retention-events.csv` — append-only review history. Resolve it with `python tools/retention_audit.py`.
- `history/00NN-<region>.md` — each region's operator-facing interval note.
- `history/CHANGELOG.md` — the module-facing interval note for each region.
- `docs/retention-spot-check.md` — a non-authoritative old window comparison.
