# attestation stage

*Owner: C. Batbayar (Platform Reliability). Module: `src/attestation_view.py`.*

## What it is for

The attestation stage is the signing boundary of the kestrel-turn pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside schema.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 120 | the largest number of records held before the stage refuses new work |
| `window_s` | 30 | seconds a record may stay `pending` before it is reaped |
| `carried` | 192 | the units this stage carries into the close, fixed at the review |

Both are read from the `attestation` section of the manifest by `build_attestation`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with schema and audit

`schema` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `audit`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `promoted` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
