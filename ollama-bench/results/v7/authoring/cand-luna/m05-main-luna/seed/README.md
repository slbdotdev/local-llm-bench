# CedarSignal

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
| audit | `src/audit_core.py` | `docs/audit.md` | K. Sorensen |
| reconcile | `src/reconcile_view.py` | `docs/reconcile.md` | K. Sorensen |
| attestation | `src/attestation_gate.py` | `docs/attestation.md` | K. Sorensen |
| watermark | `src/watermark_core.py` | `docs/watermark.md` | T. Abarca |
| ingest | `src/ingest_store.py` | `docs/ingest.md` | K. Sorensen |
| ledger | `src/ledger_core.py` | `docs/ledger.md` | C. Batbayar |
| envelope | `src/envelope_view.py` | `docs/envelope.md` | D. Ferreira |
| drain | `src/drain_view.py` | `docs/drain.md` | D. Ferreira |
| tenancy | `src/tenancy_store.py` | `docs/tenancy.md` | K. Sorensen |
| checkpoint | `src/checkpoint_view.py` | `docs/checkpoint.md` | J. Maldonado |
| compaction | `src/compaction_view.py` | `docs/compaction.md` | D. Ferreira |
| dispatch | `src/dispatch_core.py` | `docs/dispatch.md` | R. Okonjo |
| throttle | `src/throttle_flow.py` | `docs/throttle.md` | M. Lindqvist |
| routing | `src/routing_gate.py` | `docs/routing.md` | S. Nwachukwu |
| replay | `src/replay_flow.py` | `docs/replay.md` | J. Maldonado |
| shard | `src/shard_flow.py` | `docs/shard.md` | L. Achterberg |
| digest | `src/digest_flow.py` | `docs/digest.md` | E. Thorsdottir |
| retention | `src/retention_view.py` | `docs/retention.md` | D. Ferreira |
| cursor | `src/cursor_core.py` | `docs/cursor.md` | N. Oyelaran |
| rollup | `src/rollup_core.py` | `docs/rollup.md` | D. Ferreira |
| schema | `src/schema_flow.py` | `docs/schema.md` | A. Villanueva |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
