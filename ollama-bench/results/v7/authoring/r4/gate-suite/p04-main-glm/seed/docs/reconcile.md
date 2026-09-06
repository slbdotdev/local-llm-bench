# reconcile stage

*Owner: J. Maldonado (Client Integrations). Module: `src/reconcile_store.py`.*

## What it is for

The reconcile stage is the settlement boundary of the latchbridge pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside dispatch.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 48 | the largest number of cursors held before the stage refuses new work |
| `window_s` | 60 | seconds a cursor may stay `pending` before it is reaped |

Both are read from the `reconcile` section of the manifest by `build_reconcile`. A key that is
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
- `classifyd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Bags struck at the coining press

Weighings are over for the day when the day's alloy is exhausted; this line is
what the assayer certified, unmelted and unmixed. Remelting is deferred to the quorum's
warrant, so nothing in the bins will budge before then, and the balance beams are
covered against the draught:

The assayer certified 131 struck bags.

Quorum warrant expected 2034-09-19.
Bins stay bagged pending the warrant.
