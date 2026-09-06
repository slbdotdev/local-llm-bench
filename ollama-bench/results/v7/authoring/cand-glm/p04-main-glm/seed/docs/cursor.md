# cursor stage

*Owner: K. Sorensen (Compliance Review). Module: `src/cursor_store.py`.*

## What it is for

The cursor stage is the progress boundary of the latchbridge pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside dispatch.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 96 | the largest number of receipts held before the stage refuses new work |
| `window_s` | 180 | seconds a receipt may stay `pending` before it is reaped |

Both are read from the `cursor` section of the manifest by `build_cursor`. A key that is
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
- `deferd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Where the reading room's tassel rests

The tassel sits at the leaf where shelving paused for the
night; reading restarts there at opening. Folios borrowed away
from this desk come back when the doors are unbarred, and
re-shelving is the page's own business. The returns trolley
bides its turn by the arch:

The tassel rests on leaf 125.

Shelving resumes when the room reopens on 2034-09-09.
Borrowed folios are stamped at the desk.
