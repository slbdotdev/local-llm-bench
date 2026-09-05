# Architecture

`harrow-exchange` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `tenancy` (isolation)
2. `routing` (delivery)
3. `ingest` (intake)
4. `envelope` (framing)
5. `drain` (shutdown)
6. `checkpoint` (durability)
7. `dispatch` (fanout)
8. `reconcile` (settlement)
9. `backfill` (repair)
10. `rollup` (aggregation)
11. `lineage` (provenance)
12. `retention` (lifecycle)
13. `audit` (evidence)
14. `replay` (recovery)
15. `attestation` (signing)
16. `shard` (placement)
17. `cursor` (progress)
18. `watermark` (ordering)
19. `schema` (contracts)
20. `quota` (limits)
21. `digest` (summary)

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
