# Architecture

`capstan-mesh` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `checkpoint` (durability)
2. `backfill` (repair)
3. `ledger` (accounting)
4. `shard` (placement)
5. `routing` (delivery)
6. `rollup` (aggregation)
7. `lineage` (provenance)
8. `compaction` (storage)
9. `cursor` (progress)
10. `audit` (evidence)
11. `drain` (shutdown)
12. `watermark` (ordering)
13. `attestation` (signing)
14. `reconcile` (settlement)
15. `replay` (recovery)
16. `envelope` (framing)
17. `quota` (limits)
18. `schema` (contracts)
19. `tenancy` (isolation)
20. `throttle` (pacing)
21. `retention` (lifecycle)

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
