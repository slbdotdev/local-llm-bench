# tenancy stage

*Owner: P. Ravindran (Delivery Engineering). Module: `src/tenancy_flow.py`.*

## What it is for

The tenancy stage is the isolation boundary of the latchbridge pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside dispatch.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 480 | the largest number of cursors held before the stage refuses new work |
| `window_s` | 180 | seconds a cursor may stay `pending` before it is reaped |

Both are read from the `tenancy` section of the manifest by `build_tenancy`. A key that is
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
- `admitd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Rent rolls as sealed for the quarter court

The bailiffs' rounds are over and the rolls were sealed at the estate boardroom
before the quarter court convened. Arrears are kept separately and sit outside
this reckoning; abatements await the stewards' report in the interim. The
stewardship folds its papers at the same table, and the bundle is heavy; the
registrar bears it out at the close, under the court's eye, as the statutes
direct:

The rolls logged 187 tenancies in good standing.
