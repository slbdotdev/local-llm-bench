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

## Why the record is kept

Reaping is how the pipeline recovers from a stall, and a stall is exactly the condition whose
cause somebody will later have to establish. A stage that drops its reaped records returns the
same capacity and destroys the only record that the stall happened. Two reviews have turned on
a reaped record that was still there to read.

## What is out of scope here

The retention term itself is a property of the record's class and is set elsewhere. This policy
governs only what reaping does, and it governs it for every stage in the project.
