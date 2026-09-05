# quota-desk

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
| ingest | `src/ingest_gate.py` | `docs/ingest.md` | J. Maldonado |
| lineage | `src/lineage_store.py` | `docs/lineage.md` | K. Sorensen |
| retention | `src/retention_store.py` | `docs/retention.md` | H. Bergstrom |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Budget accounting

Budget accounting for the metered side of the service lives in `src/quota/budget.py`, with a
test suite that is the contract.

    PYTHONPATH=src python -m pytest tests

## The one invariant

**No account is ever reported as having negative remaining budget.** Overspend happens — a burst
lands between two checks and the meter catches up afterwards — and when it does, the remaining
budget is zero and the overspend is reported separately by `overspend()`. Reporting a negative
remaining figure has, twice, caused a downstream system to treat it as a credit.
