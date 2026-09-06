# hearth-relay

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
| retention | `src/retention_gate.py` | `docs/retention.md` | R. Okonjo |
| quota | `src/quota_flow.py` | `docs/quota.md` | L. Achterberg |
| ledger | `src/ledger_store.py` | `docs/ledger.md` | R. Okonjo |
| dispatch | `src/dispatch_store.py` | `docs/dispatch.md` | E. Thorsdottir |
| throttle | `src/throttle_gate.py` | `docs/throttle.md` | E. Thorsdottir |
| backfill | `src/backfill_view.py` | `docs/backfill.md` | P. Ravindran |
| routing | `src/routing_flow.py` | `docs/routing.md` | K. Sorensen |
| checkpoint | `src/checkpoint_store.py` | `docs/checkpoint.md` | K. Sorensen |
| ingest | `src/ingest_store.py` | `docs/ingest.md` | C. Batbayar |
| reconcile | `src/reconcile_flow.py` | `docs/reconcile.md` | D. Ferreira |
| shard | `src/shard_gate.py` | `docs/shard.md` | K. Sorensen |
| schema | `src/schema_store.py` | `docs/schema.md` | S. Nwachukwu |
| rollup | `src/rollup_gate.py` | `docs/rollup.md` | T. Abarca |
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | L. Achterberg |
| digest | `src/digest_core.py` | `docs/digest.md` | M. Lindqvist |
| envelope | `src/envelope_core.py` | `docs/envelope.md` | T. Abarca |
| watermark | `src/watermark_store.py` | `docs/watermark.md` | N. Oyelaran |
| drain | `src/drain_store.py` | `docs/drain.md` | C. Batbayar |
| replay | `src/replay_gate.py` | `docs/replay.md` | N. Oyelaran |
| audit | `src/audit_core.py` | `docs/audit.md` | D. Ferreira |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Window documentation

Every stage's documented enforced window is kept in step with its module by hand at release
time, so the two never disagree in a released tree.
