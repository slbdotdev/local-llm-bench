# Architecture

`cinder-parcel` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `replay` (recovery)
2. `compaction` (storage)
3. `reconcile` (settlement)
4. `envelope` (framing)
5. `checkpoint` (durability)
6. `rollup` (aggregation)
7. `schema` (contracts)
8. `retention` (lifecycle)
9. `quota` (limits)
10. `audit` (evidence)
11. `backfill` (repair)
12. `watermark` (ordering)
13. `ingest` (intake)
14. `cursor` (progress)
15. `tenancy` (isolation)
16. `drain` (shutdown)
17. `attestation` (signing)
18. `throttle` (pacing)
19. `routing` (delivery)

Sealing out of order is the single most common cause of a `pending` record surviving
into the audit trail, and it is why `seal()` is idempotent: the drain may be retried
safely, but it may not be reordered.

## Why stages do not import each other

An earlier revision wired the stages with direct imports. It worked and it made two
things impossible: running a subset of the pipeline in a test, and replacing one stage
without a coordinated deploy. Both are now routine. The cost is that a reader cannot
follow the pipeline by following imports, and must read the manifest instead.

## The manifest

`config/manifest.json` names each stage and carries its section. A section may set
`limit` and `window_s`; anything else in a section is ignored with a warning, which is
deliberate - it lets a section carry a note for a human reader.
