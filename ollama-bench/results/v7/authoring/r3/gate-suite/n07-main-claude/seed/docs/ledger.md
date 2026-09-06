# ledger stage

*Owner: L. Achterberg (Delivery Engineering). Module: `src/ledger_store.py`.*

## What it is for

The ledger stage is the accounting boundary of the strand-harbour pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside attestation.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 250 | the largest number of entrys held before the stage refuses new work |
| `window_s` | 90 | seconds a entry may stay `pending` before it is reaped |
| `custody_days` | 365 | days of evidence custody, as decided by this stage's custody pool |

Both are read from the `ledger` section of the manifest by `build_ledger`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with attestation and cursor

`attestation` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `cursor`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `retired` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
