# dispatch stage

*Owner: R. Okonjo (Compliance Review). Module: `src/dispatch_core.py`.*

## What it is for

The dispatch stage is the fanout boundary of the fenwick-conduit pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside reconcile.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 250 | the largest number of tokens held before the stage refuses new work |
| `window_s` | 45 | seconds a token may stay `pending` before it is reaped |

Both are read from the `dispatch` section of the manifest by `build_dispatch`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with reconcile and backfill

`reconcile` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `backfill`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `promoted` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

Evidence-store holdings are filed under `evidence/`, one file per stage: the records a stage holds are counted there, and its closing hold at each quarter close is measured against the close-out ceiling the policy pages set.
