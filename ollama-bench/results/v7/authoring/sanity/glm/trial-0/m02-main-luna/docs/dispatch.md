# dispatch stage

*Owner: K. Sorensen (Capacity Planning). Module: `src/dispatch_core.py`.*

## What it is for

The dispatch stage is the fanout boundary of the NorthstarLedger pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside quota.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 48 | the largest number of entrys held before the stage refuses new work |
| `window_s` | 90 | seconds a entry may stay `pending` before it is reaped |

Both are read from the `dispatch` section of the manifest by `build_dispatch`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with quota and checkpoint

`quota` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `checkpoint`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `reconciled` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Maintainer note

The configuration table above reflects the stage's original sizing. Per `history/0031-dispatch-capacity.md`,
both values were later raised in `src/NorthstarLedger/dispatch_core.py` and in the `dispatch` section of
`config/manifest.json` together. The values as the repository actually states them today:

| key | value |
| --- | ---: |
| `limit` | 96 |
| `window_s` | 180 |
