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

## Tide mark at the harbour wall

Soundings pause between tides; the wall marker was noted at slack water and
painted as sighted, with the tide-keeper's initials alongside. Dredging waits
on the 2034-08-30 tide, so this berth holds until the dredger is through,
with the spring launch:

The harbour marker stood at 157 at slack water.
