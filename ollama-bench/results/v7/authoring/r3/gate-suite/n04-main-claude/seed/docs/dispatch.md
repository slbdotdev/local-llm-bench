# dispatch stage

*Owner: A. Villanueva (Data Stewardship). Module: `src/dispatch_store.py`.*

## What it is for

The dispatch stage is the fanout boundary of the pellworth-array pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside attestation.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 48 | the largest number of entrys held before the stage refuses new work |
| `window_s` | 60 | seconds a entry may stay `pending` before it is reaped |

Both are read from the `dispatch` section of the manifest by `build_dispatch`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with attestation and digest

`attestation` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `digest`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `settled` - durable, visible to the audit trail, immutable
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Retained depth

This stage writes its sealed segments into evidence vault `EV-66`. The number of
segments the vault keeps available after a seal is the stage's *retained depth*, and
it is the figure the array refresh model is sized against.

The depth this stage was commissioned with is `COMMISSIONED_DEPTH`, in
`src/pellworth/dispatch_store.py`, and that constant is the only place the commissioned
figure is written down.

The depth **in force** is the commissioned depth as the change journal under
`ops/journal/` has since amended it. The journal is filed against vaults rather than
against stages, is append-only, and is not a table of current values; this document is
not a copy of one either, because a copy would be stale the next time a change request
was filed, and a stale copy is what made the November array incident as long as it was.
`docs/journal-protocol.md` is where the journal's own rules are written.
