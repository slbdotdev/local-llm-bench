# Architecture

`hearth-relay` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `retention` (lifecycle)
2. `quota` (limits)
3. `ledger` (accounting)
4. `dispatch` (fanout)
5. `throttle` (pacing)
6. `backfill` (repair)
7. `routing` (delivery)
8. `checkpoint` (durability)
9. `ingest` (intake)
10. `reconcile` (settlement)
11. `shard` (placement)
12. `schema` (contracts)
13. `rollup` (aggregation)
14. `tenancy` (isolation)
15. `digest` (summary)
16. `envelope` (framing)
17. `watermark` (ordering)
18. `drain` (shutdown)
19. `replay` (recovery)
20. `audit` (evidence)

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
