# Architecture

`wardstone-flux` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `lineage` (provenance)
2. `schema` (contracts)
3. `drain` (shutdown)
4. `replay` (recovery)
5. `dispatch` (fanout)
6. `compaction` (storage)
7. `retention` (lifecycle)
8. `routing` (delivery)
9. `attestation` (signing)
10. `digest` (summary)
11. `checkpoint` (durability)
12. `envelope` (framing)
13. `cursor` (progress)
14. `reconcile` (settlement)
15. `throttle` (pacing)
16. `rollup` (aggregation)
17. `backfill` (repair)
18. `shard` (placement)
19. `audit` (evidence)

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
