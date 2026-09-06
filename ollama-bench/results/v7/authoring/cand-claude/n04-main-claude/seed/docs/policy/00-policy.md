# Policy: retention

*How long each record class is kept, and who may shorten it.*

**This policy outranks `docs/architecture.md`, `docs/operations.md`, every component
document and every history entry.** Where a component document describes behaviour this
policy forbids, the component document is stale and is to be corrected, not followed.

## Rules

1. A record that has reached `settled` is immutable. No stage, no operator and no
   repair script may alter it. A correction is a new record that cites the old one.
2. An `abandoned` record is retained for the full retention term of its class, even
   when it is obviously the result of a defect. Deleting it destroys the evidence that
   the defect existed.
3. The retention term is a property of the record's class and never of the stage that
   produced it. Two stages may hold records of the same class for different reasons and
   for the same term.
4. A limit change is a manifest change and takes effect at the next assembly. A limit
   changed by any other route is reverted and the route is reported.
5. The attestation stage carries the longest term of any stage, 64 days, because it is the
   boundary at which ordering becomes durable.

## What this policy does not cover

It does not say what a stage should do when it cannot reach the evidence store. That
is deliberately left to `docs/operations.md`, because the answer depends on which
stage and on how far the drain has progressed, and a policy that tried to enumerate
those cases would be wrong within a quarter.
