# Architecture

`pellworth-array` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `attestation` (signing)
2. `digest` (summary)
3. `watermark` (ordering)
4. `reconcile` (settlement)
5. `quota` (limits)
6. `lineage` (provenance)
7. `drain` (shutdown)
8. `envelope` (framing)
9. `checkpoint` (durability)
10. `ledger` (accounting)
11. `schema` (contracts)
12. `dispatch` (fanout)
13. `throttle` (pacing)
14. `compaction` (storage)
15. `shard` (placement)

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
