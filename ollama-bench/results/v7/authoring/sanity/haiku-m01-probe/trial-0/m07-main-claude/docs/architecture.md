# Architecture

`kestrel-yard` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `envelope` (framing)
2. `schema` (contracts)
3. `rollup` (aggregation)
4. `compaction` (storage)
5. `settlement` (signing)
6. `ledger` (accounting)
7. `watermark` (ordering)
8. `throttle` (pacing)
9. `dispatch` (fanout)
10. `quota` (limits)
11. `audit` (evidence)
12. `lineage` (provenance)
13. `checkpoint` (durability)
14. `replay` (recovery)
15. `tenancy` (isolation)
16. `shard` (placement)
17. `backfill` (repair)
18. `digest` (summary)
19. `cursor` (progress)
20. `ingest` (intake)
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
