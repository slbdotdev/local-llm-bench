# dispatch stage

*Owner: N. Oyelaran (Capacity Planning). Module: `src/dispatch_view.py`.*

## What it is for

The dispatch stage is the fanout boundary of the latchbridge pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside compaction.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 250 | the largest number of receipts held before the stage refuses new work |
| `window_s` | 180 | seconds a receipt may stay `pending` before it is reaped |

Both are read from the `dispatch` section of the manifest by `build_dispatch`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with compaction and retention

`compaction` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `retention`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `narrowd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## What the yard scale settled on

Set apart from the configuration figures above because the yardmaster reads it
once per settling and not at assembly, and because nothing since the small hours has
moved it. A later settling supersedes what stands here, so until then the
yardmaster quotes it unrounded, unadjusted, and without re-weighing, however the
dawn wagon rocks the beam:

The yard scale came to rest on 101.

A re-weigh is pencilled for 2034-08-14.
Weights live in the yardmaster's safe.
