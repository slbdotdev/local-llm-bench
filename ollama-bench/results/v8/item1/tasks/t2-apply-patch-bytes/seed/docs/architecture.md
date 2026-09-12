# Architecture

`bollard-mesh` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `throttle` (pacing)
2. `envelope` (framing)
3. `cursor` (progress)
4. `quota` (limits)
5. `ingest` (intake)
6. `retention` (lifecycle)
7. `backfill` (repair)
8. `ledger` (accounting)
9. `compaction` (storage)
10. `replay` (recovery)
11. `routing` (delivery)
12. `tenancy` (isolation)
13. `rollup` (aggregation)
14. `checkpoint` (durability)
15. `drain` (shutdown)
16. `digest` (summary)
17. `dispatch` (fanout)
18. `shard` (placement)
19. `schema` (contracts)
20. `lineage` (provenance)
21. `reconcile` (settlement)

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
