# digest stage

*Owner: N. Oyelaran (Delivery Engineering). Module: `src/digest_view.py`.*

## What it is for

The digest stage is the summary boundary of the quayside-shuttle pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside routing.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 480 | the largest number of cursors held before the stage refuses new work |
| `window_s` | 45 | seconds a cursor may stay `pending` before it is reaped |

Both are read from the `digest` section of the manifest by `build_digest`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with routing and replay

`routing` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `replay`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `settled` - durable, visible to the audit trail, immutable
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Acknowledged deliveries

*This stage's record of the deliveries it has acknowledged in the current half-
year, newest first. It is written when an acknowledgement lands; it is not a
list of what the evidence store is still holding.*

| delivery | acknowledged |
| --- | --- |
| DLV-5160 | 2034-12-19 |
| DLV-5161 | 2034-12-08 |
| DLV-5162 | 2034-11-27 |
| DLV-5163 | 2034-11-16 |
| DLV-5164 | 2034-11-05 |
| DLV-5165 | 2034-10-25 |
