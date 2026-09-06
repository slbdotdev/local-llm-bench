# ledger stage

*Owner: K. Sorensen (Data Stewardship). Module: `src/ledger_flow.py`.*

## What it is for

The ledger stage is the accounting boundary of the cordage-mesh pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside lineage.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 120 | the largest number of windows held before the stage refuses new work |
| `window_s` | 45 | seconds a window may stay `pending` before it is reaped |
| `dwell_s` | 1176 | the seconds this stage currently honours as its dwell, tracked by the branch workflow |

Both are read from the `ledger` section of the manifest by `build_ledger`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with lineage and rollup

`lineage` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `rollup`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `admitd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
