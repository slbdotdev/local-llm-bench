# cinder-arch

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
| cursor | `src/cursor_core.py` | `docs/cursor.md` | M. Lindqvist |
| lineage | `src/lineage_core.py` | `docs/lineage.md` | C. Batbayar |
| digest | `src/digest_flow.py` | `docs/digest.md` | H. Bergstrom |
| retention | `src/retention_gate.py` | `docs/retention.md` | S. Nwachukwu |
| ingest | `src/ingest_store.py` | `docs/ingest.md` | K. Sorensen |
| dispatch | `src/dispatch_store.py` | `docs/dispatch.md` | L. Achterberg |
| replay | `src/replay_store.py` | `docs/replay.md` | R. Okonjo |
| ledger | `src/ledger_core.py` | `docs/ledger.md` | J. Maldonado |
| attestation | `src/attestation_gate.py` | `docs/attestation.md` | P. Ravindran |
| tenancy | `src/tenancy_view.py` | `docs/tenancy.md` | H. Bergstrom |
| schema | `src/schema_flow.py` | `docs/schema.md` | T. Abarca |
| backfill | `src/backfill_store.py` | `docs/backfill.md` | P. Ravindran |
| watermark | `src/watermark_view.py` | `docs/watermark.md` | T. Abarca |
| shard | `src/shard_store.py` | `docs/shard.md` | T. Abarca |
| drain | `src/drain_gate.py` | `docs/drain.md` | L. Achterberg |
| quota | `src/quota_flow.py` | `docs/quota.md` | H. Bergstrom |
| routing | `src/routing_gate.py` | `docs/routing.md` | H. Bergstrom |
| envelope | `src/envelope_gate.py` | `docs/envelope.md` | P. Ravindran |
| checkpoint | `src/checkpoint_view.py` | `docs/checkpoint.md` | D. Ferreira |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Capacity reconciliation

The engineering record for capacity reconciliation explains how a component document, Python
module, and migration ledger may disagree. The current migration ledger retains one
`handoff_capacity` row for each stage and records its resolution class. The record's prose is
the authority for selecting among those three sources.
