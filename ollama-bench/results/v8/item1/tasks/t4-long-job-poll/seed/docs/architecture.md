# Architecture

`dogvane-mesh` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `retention` (lifecycle)
2. `lineage` (provenance)
3. `backfill` (repair)
4. `dispatch` (fanout)
5. `drain` (shutdown)
6. `tenancy` (isolation)
7. `shard` (placement)
8. `digest` (summary)
9. `cursor` (progress)
10. `routing` (delivery)
11. `watermark` (ordering)
12. `replay` (recovery)
13. `throttle` (pacing)
14. `reconcile` (settlement)
15. `envelope` (framing)
16. `compaction` (storage)
17. `audit` (evidence)
18. `rollup` (aggregation)
19. `attestation` (signing)
20. `ingest` (intake)
21. `schema` (contracts)

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
