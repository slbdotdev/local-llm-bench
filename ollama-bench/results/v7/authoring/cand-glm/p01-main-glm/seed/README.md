# quayside-shuttle

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
| routing | `src/routing_core.py` | `docs/routing.md` | M. Lindqvist |
| replay | `src/replay_core.py` | `docs/replay.md` | T. Abarca |
| backfill | `src/backfill_store.py` | `docs/backfill.md` | M. Lindqvist |
| envelope | `src/envelope_gate.py` | `docs/envelope.md` | H. Bergstrom |
| ingest | `src/ingest_flow.py` | `docs/ingest.md` | T. Abarca |
| digest | `src/digest_view.py` | `docs/digest.md` | N. Oyelaran |
| attestation | `src/attestation_flow.py` | `docs/attestation.md` | J. Maldonado |
| tenancy | `src/tenancy_gate.py` | `docs/tenancy.md` | S. Nwachukwu |
| watermark | `src/watermark_view.py` | `docs/watermark.md` | S. Nwachukwu |
| retention | `src/retention_view.py` | `docs/retention.md` | C. Batbayar |
| reconcile | `src/reconcile_store.py` | `docs/reconcile.md` | N. Oyelaran |
| rollup | `src/rollup_core.py` | `docs/rollup.md` | S. Nwachukwu |
| dispatch | `src/dispatch_view.py` | `docs/dispatch.md` | H. Bergstrom |
| checkpoint | `src/checkpoint_view.py` | `docs/checkpoint.md` | E. Thorsdottir |
| quota | `src/quota_store.py` | `docs/quota.md` | E. Thorsdottir |
| drain | `src/drain_core.py` | `docs/drain.md` | L. Achterberg |
| shard | `src/shard_gate.py` | `docs/shard.md` | D. Ferreira |
| schema | `src/schema_gate.py` | `docs/schema.md` | K. Sorensen |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Compatibility records

- `docs/releases/` - the release notes and rationales. A promise a release made is stated
  in its own rationale and nowhere else; a note a later release superseded is evidence,
  never a live promise.
- Every component page under `docs/` tables the deliveries its stage has acknowledged,
  newest first, under *Acknowledged deliveries*. The table is the stage's record of what
  it has acknowledged; it is not a list of what its evidence store is still holding.
- Every module under `src/` keeps its sweep state beside its engine class: the nightly
  sweep empties the stage's evidence store of every delivery acknowledged on or before
  the waterline the module records, and nothing newer.
