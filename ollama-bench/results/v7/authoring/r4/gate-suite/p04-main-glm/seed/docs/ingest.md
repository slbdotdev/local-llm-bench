# ingest stage

*Owner: T. Abarca (Delivery Engineering). Module: `src/ingest_view.py`.*

## What it is for

The ingest stage is the intake boundary of the latchbridge pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside dispatch.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 480 | the largest number of entrys held before the stage refuses new work |
| `window_s` | 120 | seconds a entry may stay `pending` before it is reaped |

Both are read from the `ingest` section of the manifest by `build_ingest`. A key that is
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
- `reconciled` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Crates inside the storeroom gate

Receiving ends when the dock clock strikes noon; goods
landing past the whistle are turned away, and the docket is what
you see, weighed at the ramp, unopened. Nothing ships until the
stamp:

The storeroom gate closed on 165 crates.

Pallets move out on 2034-10-30.
