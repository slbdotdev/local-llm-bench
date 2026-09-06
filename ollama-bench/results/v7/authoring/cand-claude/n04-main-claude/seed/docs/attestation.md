# attestation stage

*Owner: H. Bergstrom (Platform Reliability). Module: `src/attestation_core.py`.*

## What it is for

The attestation stage is the signing boundary of the pellworth-array pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside digest.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 64 | the largest number of segments held before the stage refuses new work |
| `window_s` | 90 | seconds a segment may stay `pending` before it is reaped |

Both are read from the `attestation` section of the manifest by `build_attestation`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with digest and watermark

`digest` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `watermark`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `resolved` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Retained depth

This stage writes its sealed segments into evidence vault `EV-11`. The number of
segments the vault keeps available after a seal is the stage's *retained depth*, and
it is the figure the array refresh model is sized against.

The depth this stage was commissioned with is `COMMISSIONED_DEPTH`, in
`src/pellworth/attestation_core.py`, and that constant is the only place the commissioned
figure is written down.

The depth **in force** is the commissioned depth as the change journal under
`ops/journal/` has since amended it. The journal is filed against vaults rather than
against stages, is append-only, and is not a table of current values; this document is
not a copy of one either, because a copy would be stale the next time a change request
was filed, and a stale copy is what made the November array incident as long as it was.
`docs/journal-protocol.md` is where the journal's own rules are written.
