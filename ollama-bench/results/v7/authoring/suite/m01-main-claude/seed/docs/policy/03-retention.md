# Policy: retention of reaped records

*What happens to a record the pipeline stops waiting for.*

**This policy outranks `docs/architecture.md`, `docs/operations.md`, every component document
and every history entry.** Where a component document describes behaviour this policy forbids,
the component document is stale and is to be corrected, not followed.

## The rule

A record that has waited longer than its stage's `window_s` is **reaped**. Reaping is a change
of state and not a removal:

1. The record's `state` becomes `abandoned`.
2. The record **stays in the stage** and stays visible to `snapshot()`, for the full retention
   term of its class. It is never removed from the stage by reaping.
3. An `abandoned` record **stops counting against the stage's `limit`**. That is the entire
   operational purpose of reaping: to return capacity without losing evidence.

## Which records count against the limit, stated once and completely

A record counts against its stage's `limit` **from the moment the stage accepts it until it
reaches `settled` or `abandoned`, and at every state in between**. The intermediate state a
stage writes when it acts on a record — the one named after the stage's own operation — is a
record still in flight, still occupying a slot, and still counted.

Only two states do not count: `settled`, because the record is durable and has left the stage's
working set, and `abandoned`, because reaping is what returned the slot. Nothing else is exempt,
and a stage that counts only its `pending` records will report capacity it does not have.

## Why the record is kept

Reaping is how the pipeline recovers from a stall, and a stall is exactly the condition whose
cause somebody will later have to establish. A stage that drops its reaped records returns the
same capacity and destroys the only record that the stall happened. Two reviews have turned on
a reaped record that was still there to read.

## What is out of scope here

The retention term itself is a property of the record's class and is set elsewhere. This policy
governs only what reaping does, and it governs it for every stage in the project.
