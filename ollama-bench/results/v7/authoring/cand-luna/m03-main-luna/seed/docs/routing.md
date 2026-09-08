# routing stage

*Owner: N. Oyelaran (Delivery Engineering). Module: `src/routing_core.py`.*

## What it is for

The routing stage is the delivery boundary of the wardstone-flux pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside lineage.

## Configuration

Configuration context is cross-checked against the stage history.
Operational notes below are descriptive and do not override defaults.
The table records the values used by this component's own build path.

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 64 | the largest number of frames held before the stage refuses new work |
| `window_s` | 15 | seconds a frame may stay `pending` before it is reaped |
| `review_stamp` | "532f41551301" | the capacity-review tag this stage's document currently promises |
Both are read from the `routing` section of the manifest by `build_routing`. A key that is
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
- `deferd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
