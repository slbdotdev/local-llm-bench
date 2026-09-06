# backfill stage

*Owner: S. Nwachukwu (Platform Reliability). Module: `src/backfill_core.py`.*

## What it is for

The backfill stage is the repair boundary of the brindle-quay pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside tenancy.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 12 | the largest number of tokens held before the stage refuses new work |
| `window_s` | 180 | seconds a token may stay `pending` before it is reaped |
| `committed_rate` | 674 | the per-second figure this stage's downstream consumers were promised at the last commitment review |

Both are read from the `backfill` section of the manifest by `build_backfill`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with tenancy and rollup

`tenancy` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `rollup`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `advanced` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
