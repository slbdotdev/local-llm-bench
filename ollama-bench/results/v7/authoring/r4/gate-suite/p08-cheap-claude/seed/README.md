# fenwick-conduit

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
| reconcile | `src/reconcile_store.py` | `docs/reconcile.md` | H. Bergstrom |
| backfill | `src/backfill_store.py` | `docs/backfill.md` | C. Batbayar |
| dispatch | `src/dispatch_core.py` | `docs/dispatch.md` | R. Okonjo |
| drain | `src/drain_flow.py` | `docs/drain.md` | N. Oyelaran |
| checkpoint | `src/checkpoint_flow.py` | `docs/checkpoint.md` | M. Lindqvist |
| rollup | `src/rollup_gate.py` | `docs/rollup.md` | K. Sorensen |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

Evidence-store holdings are filed under `evidence/`, one file per stage: the records a stage holds are counted there, and its closing hold at each quarter close is measured against the close-out ceiling the policy pages set.
