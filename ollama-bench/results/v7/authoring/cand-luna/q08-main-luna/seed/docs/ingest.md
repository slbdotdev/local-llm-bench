# ingest stage

*Owner: P. Ravindran (Platform Reliability). Module: `src/ingest_flow.py`.*

## What it is for

The ingest stage is the intake boundary of the orison-thread pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside attestation.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 48 | the largest number of records held before the stage refuses new work |
| `window_s` | 120 | seconds a record may stay `pending` before it is reaped |

Both are read from the `ingest` section of the manifest by `build_ingest`. A key that is
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
- `promoted` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

### ivoryledger dossier

veil07_01
veil07_02
veil07_03
veil07_04
veil07_05
veil07_06
veil07_07
veil07_08

@07 driftpine glenward starling q0701 rivercairn
@07 cloudrest q0702 starling glenward rivercairn
@07 rainport glenward stoneharbor granitebell holloway
@07 moonbay glenward holloway q0703 starling
