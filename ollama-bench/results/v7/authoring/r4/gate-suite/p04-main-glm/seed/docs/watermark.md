# watermark stage

*Owner: P. Ravindran (Delivery Engineering). Module: `src/watermark_view.py`.*

## What it is for

The watermark stage is the ordering boundary of the latchbridge pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside dispatch.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 24 | the largest number of bundles held before the stage refuses new work |
| `window_s` | 15 | seconds a bundle may stay `pending` before it is reaped |

Both are read from the `watermark` section of the manifest by `build_watermark`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with dispatch and compaction

`dispatch` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `compaction`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `expandd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Closing position

Carried at the foot of the page, apart from the configuration facts, because the
closing figure is read by the closing check rather than by the assembler. It is
re-derived at the next close and not before, so until then it can lag what the journals
show. The figure is quoted where the closing row landed, and the pack quotes it as
it stands, below, without adjustment and without re-derivation:

At the cutoff the working set stood at 157 records.
