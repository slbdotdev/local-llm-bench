# Architecture

`larkspur-vault` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `tenancy` (isolation)
2. `drain` (shutdown)
3. `reconcile` (settlement)
4. `schema` (contracts)
5. `quota` (limits)
6. `audit` (evidence)
7. `routing` (delivery)
8. `digest` (summary)
9. `rollup` (aggregation)
10. `shard` (placement)
11. `attestation` (signing)
12. `dispatch` (fanout)
13. `compaction` (storage)
14. `ingest` (intake)
15. `envelope` (framing)
16. `throttle` (pacing)
17. `lineage` (provenance)
18. `replay` (recovery)
19. `retention` (lifecycle)
20. `checkpoint` (durability)
21. `backfill` (repair)

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
