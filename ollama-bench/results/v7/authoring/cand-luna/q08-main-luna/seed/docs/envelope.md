# envelope stage

*Owner: D. Ferreira (Delivery Engineering). Module: `src/envelope_gate.py`.*

## What it is for

The envelope stage is the framing boundary of the orison-thread pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside attestation.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 48 | the largest number of segments held before the stage refuses new work |
| `window_s` | 30 | seconds a segment may stay `pending` before it is reaped |

Both are read from the `envelope` section of the manifest by `build_envelope`. A key that is
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
- `narrowd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

### latticecard dossier

veil10_01
veil10_02
veil10_03
veil10_04
veil10_05
veil10_06
veil10_07
veil10_08

@10 foxglove juniperway silverfin jasperline cloudrest
@10 windmere juniperway moonbay q1001 cairnfall
@10 wainscot juniperway cloudrest q1003 moonbay
@10 bracken q1002 moonbay juniperway cairnfall
