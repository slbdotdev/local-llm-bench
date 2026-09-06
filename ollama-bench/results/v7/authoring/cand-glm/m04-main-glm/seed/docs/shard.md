# shard stage

*Owner: M. Lindqvist (Client Integrations). Module: `src/shard_store.py`.*

## What it is for

The shard stage is the placement boundary of the vantage-mill pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside envelope.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 960 | the largest number of slots held before the stage refuses new work |
| `window_s` | 120 | seconds a slot may stay `pending` before it is reaped |
| `declared_verified_on` | 2033-02-09 | the date this document itself was last confirmed current; see the stage's own module for the effective date |

Both are read from the `shard` section of the manifest by `build_shard`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with envelope and checkpoint

`envelope` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `checkpoint`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `materialised` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
