# kelvin-strait

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
| backfill | `src/backfill_gate.py` | `docs/backfill.md` | C. Batbayar |
| envelope | `src/envelope_gate.py` | `docs/envelope.md` | D. Ferreira |
| compaction | `src/compaction_flow.py` | `docs/compaction.md` | R. Okonjo |
| attestation | `src/attestation_view.py` | `docs/attestation.md` | L. Achterberg |
| audit | `src/audit_gate.py` | `docs/audit.md` | L. Achterberg |
| checkpoint | `src/checkpoint_gate.py` | `docs/checkpoint.md` | H. Bergstrom |
| drain | `src/drain_store.py` | `docs/drain.md` | P. Ravindran |
| replay | `src/replay_gate.py` | `docs/replay.md` | K. Sorensen |
| routing | `src/routing_view.py` | `docs/routing.md` | R. Okonjo |
| ingest | `src/ingest_gate.py` | `docs/ingest.md` | T. Abarca |
| shard | `src/shard_store.py` | `docs/shard.md` | J. Maldonado |
| rollup | `src/rollup_view.py` | `docs/rollup.md` | C. Batbayar |
| retention | `src/retention_view.py` | `docs/retention.md` | S. Nwachukwu |
| quota | `src/quota_gate.py` | `docs/quota.md` | N. Oyelaran |
| tenancy | `src/tenancy_core.py` | `docs/tenancy.md` | K. Sorensen |
| throttle | `src/throttle_view.py` | `docs/throttle.md` | T. Abarca |

## Conventions

- Nothing is imported at module scope across stages; the pipeline is assembled from the
  manifest at run time.
- A `snapshot()` is always sorted. Insertion order is never part of any contract.
- A configuration key that is present but unparseable is a startup error, never a
  silent fallback to the module constant.
- Documentation under `docs/` outranks a history entry; a policy under `docs/policy/`
  outranks everything else.

## Repair allowance

- `docs/policy/guarantees.md` - what a stage guarantees to repair traffic, when a guarantee stops and
  starts applying, and which disagreements between a document and the pipeline are reported.
- A stage's bands and their sizes are commissioned in the stage's module. The changes since
  commissioning are in the stage's own entry under `history/`. Neither is repeated anywhere
  else, and the two are read together.
