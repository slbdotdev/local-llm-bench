# vardy-loom

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
| lineage | `src/lineage_gate.py` | `docs/lineage.md` | D. Ferreira |
| ingest | `src/ingest_gate.py` | `docs/ingest.md` | A. Villanueva |
| routing | `src/routing_view.py` | `docs/routing.md` | M. Lindqvist |
| digest | `src/digest_view.py` | `docs/digest.md` | E. Thorsdottir |
| drain | `src/drain_flow.py` | `docs/drain.md` | D. Ferreira |
| envelope | `src/envelope_gate.py` | `docs/envelope.md` | E. Thorsdottir |
| dispatch | `src/dispatch_store.py` | `docs/dispatch.md` | L. Achterberg |
| checkpoint | `src/checkpoint_view.py` | `docs/checkpoint.md` | S. Nwachukwu |
| reconcile | `src/reconcile_view.py` | `docs/reconcile.md` | A. Villanueva |
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | P. Ravindran |
| compaction | `src/compaction_view.py` | `docs/compaction.md` | M. Lindqvist |
| ledger | `src/ledger_gate.py` | `docs/ledger.md` | M. Lindqvist |
| quota | `src/quota_view.py` | `docs/quota.md` | T. Abarca |
| backfill | `src/backfill_view.py` | `docs/backfill.md` | D. Ferreira |
| shard | `src/shard_gate.py` | `docs/shard.md` | A. Villanueva |
| watermark | `src/watermark_core.py` | `docs/watermark.md` | N. Oyelaran |
| throttle | `src/throttle_flow.py` | `docs/throttle.md` | A. Villanueva |
| attestation | `src/attestation_core.py` | `docs/attestation.md` | H. Bergstrom |
| retention | `src/retention_core.py` | `docs/retention.md` | L. Achterberg |
| replay | `src/replay_gate.py` | `docs/replay.md` | J. Maldonado |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Flush budgets

Every stage carries a flush budget, declared twice: the component document records the
value the review accepted, in the unit its review stated, and the implementation module
declares the same budget as a constant whose name carries its unit. Totals and
comparisons are made only after both declarations are normalised to the repository's
canonical unit; where the two disagree, the engineering documentation on budget units
governs every other record, and a reconciliation reports the disagreement rather than
repairing either record.
