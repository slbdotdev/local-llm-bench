# emberledger

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
| digest | `src/digest_store.py` | `docs/digest.md` | D. Ferreira |
| routing | `src/routing_store.py` | `docs/routing.md` | M. Lindqvist |
| envelope | `src/envelope_view.py` | `docs/envelope.md` | N. Oyelaran |
| shard | `src/shard_gate.py` | `docs/shard.md` | S. Nwachukwu |
| backfill | `src/backfill_core.py` | `docs/backfill.md` | S. Nwachukwu |
| checkpoint | `src/checkpoint_store.py` | `docs/checkpoint.md` | E. Thorsdottir |
| ledger | `src/ledger_view.py` | `docs/ledger.md` | K. Sorensen |
| ingest | `src/ingest_core.py` | `docs/ingest.md` | L. Achterberg |
| dispatch | `src/dispatch_store.py` | `docs/dispatch.md` | C. Batbayar |
| replay | `src/replay_view.py` | `docs/replay.md` | E. Thorsdottir |
| cursor | `src/cursor_view.py` | `docs/cursor.md` | E. Thorsdottir |
| compaction | `src/compaction_flow.py` | `docs/compaction.md` | H. Bergstrom |
| attestation | `src/attestation_flow.py` | `docs/attestation.md` | L. Achterberg |
| audit | `src/audit_core.py` | `docs/audit.md` | H. Bergstrom |
| drain | `src/drain_gate.py` | `docs/drain.md` | E. Thorsdottir |
| reconcile | `src/reconcile_view.py` | `docs/reconcile.md` | J. Maldonado |
| lineage | `src/lineage_core.py` | `docs/lineage.md` | E. Thorsdottir |
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | M. Lindqvist |
| retention | `src/retention_store.py` | `docs/retention.md` | P. Ravindran |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
