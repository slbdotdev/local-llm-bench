# winter-relay

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
| shard | `src/shard_store.py` | `docs/shard.md` | S. Nwachukwu |
| schema | `src/schema_core.py` | `docs/schema.md` | H. Bergstrom |
| ingest | `src/ingest_core.py` | `docs/ingest.md` | E. Thorsdottir |
| watermark | `src/watermark_view.py` | `docs/watermark.md` | K. Sorensen |
| replay | `src/replay_view.py` | `docs/replay.md` | H. Bergstrom |
| routing | `src/routing_flow.py` | `docs/routing.md` | J. Maldonado |
| envelope | `src/envelope_flow.py` | `docs/envelope.md` | A. Villanueva |
| audit | `src/audit_core.py` | `docs/audit.md` | K. Sorensen |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
