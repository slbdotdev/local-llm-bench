# arbor-quay

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
| drain | `src/drain_core.py` | `docs/drain.md` | M. Lindqvist |
| quota | `src/quota_view.py` | `docs/quota.md` | L. Achterberg |
| ingest | `src/ingest_view.py` | `docs/ingest.md` | T. Abarca |
| backfill | `src/backfill_flow.py` | `docs/backfill.md` | L. Achterberg |
| attestation | `src/attestation_core.py` | `docs/attestation.md` | P. Ravindran |
| checkpoint | `src/checkpoint_gate.py` | `docs/checkpoint.md` | P. Ravindran |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.
