# compaction stage

*Owner: P. Ravindran. Module: `src/compaction_gate.py`.*
*On-call team: **Client Integrations**.*

This component document is the authoritative ownership record.

## What it is for

The compaction stage is the storage boundary of the talus-gate pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside attestation.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 250 | the largest number of bundles held before the stage refuses new work |
| `window_s` | 15 | seconds a bundle may stay `pending` before it is reaped |
| `sla_headroom` | 47 | extra records this stage is designed to accept above its `limit` before an operational incident is opened |

Both are read from the `compaction` section of the manifest by `build_compaction`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with attestation and audit

`attestation` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `audit`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `coalesced` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
