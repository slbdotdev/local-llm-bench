# Architecture

`halyard-mesh` is a linear pipeline of independent stages. A stage never imports another stage;
the manifest names them in order and the assembler wires them together at run time.

## Drain order

Stages are sealed in **reverse manifest order**, so that no stage is sealed while an
upstream stage can still hand it work. The order is:

1. `checkpoint` (durability)
2. `ledger` (accounting)
3. `reconcile` (settlement)
4. `backfill` (repair)
5. `audit` (evidence)
6. `digest` (summary)
7. `compaction` (storage)
8. `schema` (contracts)
9. `attestation` (signing)
10. `quota` (limits)
11. `drain` (shutdown)
12. `ingest` (intake)
13. `watermark` (ordering)
14. `envelope` (framing)
15. `replay` (recovery)
16. `cursor` (progress)
17. `throttle` (pacing)
18. `retention` (lifecycle)
19. `dispatch` (fanout)
20. `shard` (placement)
21. `routing` (delivery)

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

## A note on SUPERSEDED_BY

Reviewers ask why SUPERSEDED_BY is not in the manifest. It is not, by design:
the manifest is the run-time description and a superseded module still runs.
