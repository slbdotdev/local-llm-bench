# routing stage

*Owner: M. Lindqvist (Data Stewardship). Module: `src/routing_core.py`.*

## What it is for

The routing stage is the delivery boundary of the quayside-shuttle pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside replay.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 64 | the largest number of tokens held before the stage refuses new work |
| `window_s` | 60 | seconds a token may stay `pending` before it is reaped |

Both are read from the `routing` section of the manifest by `build_routing`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with replay and backfill

`replay` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `backfill`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `coalesced` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Acknowledged deliveries

*This stage's record of the deliveries it has acknowledged in the current half-
year, newest first. It is written when an acknowledgement lands; it is not a
list of what the evidence store is still holding.*

| delivery | acknowledged |
| --- | --- |
| DLV-5110 | 2034-12-24 |
| DLV-5111 | 2034-12-13 |
| DLV-5112 | 2034-12-02 |
| DLV-5113 | 2034-11-21 |
| DLV-5114 | 2034-11-10 |
| DLV-5115 | 2034-10-30 |
