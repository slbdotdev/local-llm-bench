# drain stage

*Owner: K. Sorensen (Platform Reliability). Module: `src/drain_gate.py`.*

## What it is for

The drain stage is the shutdown boundary of the wardstone-flux pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside lineage.

## Configuration

Configuration context is cross-checked against the stage history.
Operational notes below are descriptive and do not override defaults.

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 120 | the largest number of handles held before the stage refuses new work |
| `review_stamp` | "93aa1c87c6b7" | the capacity-review tag this stage's document currently promises |
| `window_s` | 45 | seconds a handle may stay `pending` before it is reaped |
Both are read from the `drain` section of the manifest by `build_drain`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with lineage and schema

`lineage` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `schema`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `retired` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
