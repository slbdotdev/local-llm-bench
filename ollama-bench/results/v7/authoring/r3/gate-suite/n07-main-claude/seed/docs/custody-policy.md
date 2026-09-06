# Evidence custody

*How long each stage keeps the evidence it produces, and where that number comes
from. Written after the 2035 pool merge, which is when most of this stopped being
obvious.*

## A stage does not have a custody period of its own

It belongs to a **custody pool**, and the pool decides how long every stage in it
holds evidence. Pools exist because evidence is read across stages: a lineage
question that reaches back through four stages is unanswerable if the fourth threw
its evidence away first, so the stages that answer a question together keep evidence
for the same length of time.

## How to find the pool a stage is in

Every stage module names the stage it inherits its pool from, in `CUSTODY_POOL`. A
module whose `CUSTODY_POOL` is `-none-` **roots** a pool of its own, and declares
that pool's period in `CUSTODY_DAYS`. So: open the stage's module, read
`CUSTODY_POOL`, and if it names another stage, open that stage's module and read its
`CUSTODY_POOL`, until you reach one that roots a pool. That stage is the pool, and
its `CUSTODY_DAYS` is the period every stage in the chain holds for.

Chains are short and never loop; the merge tooling refuses a change that would make
one. A stage's pool is written in that stage's module and nowhere else, deliberately:
the pool merge moved stages between pools twice in one quarter, and a second copy of
the membership would have been wrong within a week. There is no table of pool
membership in this repository and there is not supposed to be one.

## `REQUESTED_CUSTODY_DAYS` is not a custody period

Every module also carries `REQUESTED_CUSTODY_DAYS`: the period the stage's owner
asked for when the stage was onboarded. It is a record of a request and it is read by
nothing. A stage holds evidence for its pool's period whatever its owner asked for,
and the two agree for some stages and not for others for no reason more interesting
than the order the pools were formed in. Do not compare a component document against
it. Two reviews have, and both filed findings that were withdrawn.

## Where a component document states it

In the `custody_days` row of the stage's own configuration table, under
`## Configuration`. That row is the operator-facing record: it is what somebody
reads before deciding whether an incident's evidence still exists. It is also the
thing that goes stale, because a stage moving between pools changes the number
without touching the document.

## The schedule, as copied at revision R-12

| pool root | days | formed |
| --- | ---: | --- |
| attestation | 45 | 2033-01 |
| checkpoint | 90 | 2034-04 |
| envelope | 180 | 2033-07 |
| watermark | 120 | 2034-10 |
| rollup | 730 | 2033-01 |

**This table is a copy.** The platform resolves the schedule from the stage modules
every time it assembles, and the state report under `tools/` prints what is in
force. Where this copy and that output disagree, the output is right and this table
is behind: a copy is only ever as current as the day somebody last retyped it, and
the revision above says which day that was.

## Why the copy is kept at all

Because an operator reading this page at three in the morning should not have to run
anything to get an approximate answer, and an approximate answer is usually enough
to decide whether to keep looking. It is not enough to file a finding on, and a
finding filed off this table rather than off the platform is withdrawn.

## What a period is not

- Not `window_s`. That is a per-record timeout in seconds, it is a property of a
  stage rather than of a pool, and it has nothing to do with how long evidence is
  kept afterwards.
- Not `limit`. A limit is how much a stage holds at once.
- Not the retention of an `abandoned` record, which is separate and is governed by
  the policy records.
