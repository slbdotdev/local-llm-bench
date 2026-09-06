# ledger stage

*Owner: J. Maldonado (Compliance Review). Module: `src/ledger_gate.py`.*

## What it is for

The ledger stage is the accounting boundary of the sable-arc pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside backfill.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 32 | the largest number of receipts held before the stage refuses new work |
| `window_s` | 30 | seconds a receipt may stay `pending` before it is reaped |
| `regional_window` | 900005000025 | component interval recorded for this item |

Both are read from the `ledger` section of the manifest by `build_ledger`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with backfill and checkpoint

`backfill` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `checkpoint`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `settled` - durable, visible to the audit trail, immutable
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
