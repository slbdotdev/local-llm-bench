# ember-course

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
| quota | `src/quota_view.py` | `docs/quota.md` | S. Nwachukwu |
| replay | `src/replay_view.py` | `docs/replay.md` | E. Thorsdottir |
| audit | `src/audit_view.py` | `docs/audit.md` | C. Batbayar |
| dispatch | `src/dispatch_core.py` | `docs/dispatch.md` | H. Bergstrom |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | N. Oyelaran |
| throttle | `src/throttle_gate.py` | `docs/throttle.md` | L. Achterberg |
| ledger | `src/ledger_view.py` | `docs/ledger.md` | R. Okonjo |
| schema | `src/schema_flow.py` | `docs/schema.md` | K. Sorensen |
| shard | `src/shard_store.py` | `docs/shard.md` | S. Nwachukwu |
| retention | `src/retention_core.py` | `docs/retention.md` | H. Bergstrom |
| ingest | `src/ingest_store.py` | `docs/ingest.md` | E. Thorsdottir |
| compaction | `src/compaction_gate.py` | `docs/compaction.md` | P. Ravindran |
| digest | `src/digest_store.py` | `docs/digest.md` | T. Abarca |
| rollup | `src/rollup_view.py` | `docs/rollup.md` | C. Batbayar |
| watermark | `src/watermark_core.py` | `docs/watermark.md` | T. Abarca |
| cursor | `src/cursor_store.py` | `docs/cursor.md` | D. Ferreira |
| backfill | `src/backfill_flow.py` | `docs/backfill.md` | E. Thorsdottir |
| checkpoint | `src/checkpoint_view.py` | `docs/checkpoint.md` | T. Abarca |
| drain | `src/drain_core.py` | `docs/drain.md` | R. Okonjo |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Support-tooling bridge

A small subsystem alongside the generated pipeline stages exposes one stage's own recovery
operation under a second, outward name for the support tooling: a bridge module, a lookup
table and a serializer under `src/ember/ext/`, a usage note under `docs/`, and a regression
test under `tests/`. It binds to exactly one stage; see the bridge module's own docstring
for which one and how that is decided.
