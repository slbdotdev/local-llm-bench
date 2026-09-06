# digest stage

*Owner: M. Lindqvist (Data Stewardship). Module: `src/digest_view.py`.*

## What it is for

The digest stage is the summary boundary of the sable-arc pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside backfill.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 250 | the largest number of cursors held before the stage refuses new work |
| `window_s` | 51 | seconds a cursor may stay `pending` before it is reaped |
| `regional_window` | 900016000056 | component interval recorded for this item |

Both are read from the `digest` section of the manifest by `build_digest`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with backfill and checkpoint

`backfill` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `checkpoint`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `advanced` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
