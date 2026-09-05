# harrow-exchange

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
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | E. Thorsdottir |
| routing | `src/routing_store.py` | `docs/routing.md` | S. Nwachukwu |
| ingest | `src/ingest_view.py` | `docs/ingest.md` | H. Bergstrom |
| envelope | `src/envelope_view.py` | `docs/envelope.md` | R. Okonjo |
| drain | `src/drain_core.py` | `docs/drain.md` | S. Nwachukwu |
| checkpoint | `src/checkpoint_gate.py` | `docs/checkpoint.md` | S. Nwachukwu |
| dispatch | `src/dispatch_gate.py` | `docs/dispatch.md` | S. Nwachukwu |
| reconcile | `src/reconcile_view.py` | `docs/reconcile.md` | D. Ferreira |
| backfill | `src/backfill_core.py` | `docs/backfill.md` | E. Thorsdottir |
| rollup | `src/rollup_gate.py` | `docs/rollup.md` | K. Sorensen |
| lineage | `src/lineage_store.py` | `docs/lineage.md` | M. Lindqvist |
| retention | `src/retention_view.py` | `docs/retention.md` | H. Bergstrom |
| audit | `src/audit_flow.py` | `docs/audit.md` | R. Okonjo |
| replay | `src/replay_flow.py` | `docs/replay.md` | T. Abarca |
| attestation | `src/attestation_gate.py` | `docs/attestation.md` | J. Maldonado |
| shard | `src/shard_view.py` | `docs/shard.md` | M. Lindqvist |
| cursor | `src/cursor_gate.py` | `docs/cursor.md` | J. Maldonado |
| watermark | `src/watermark_store.py` | `docs/watermark.md` | H. Bergstrom |
| schema | `src/schema_gate.py` | `docs/schema.md` | D. Ferreira |
| quota | `src/quota_flow.py` | `docs/quota.md` | M. Lindqvist |
| digest | `src/digest_store.py` | `docs/digest.md` | D. Ferreira |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
