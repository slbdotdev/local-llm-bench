# shard stage

*Owner: H. Bergstrom (Delivery Engineering). Module: `src/shard_view.py`.*

## What it is for

The shard stage is the placement boundary of the orison-thread pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside attestation.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 480 | the largest number of frames held before the stage refuses new work |
| `window_s` | 180 | seconds a frame may stay `pending` before it is reaped |

Both are read from the `shard` section of the manifest by `build_shard`. A key that is
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
- `settled` - durable, visible to the audit trail, immutable
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

### harborleaf dossier

veil06_01
veil06_02
veil06_03
veil06_04
veil06_05
veil06_06
veil06_07
veil06_08

@06 silverfin frostmark cloudrest q0601 moonbay
@06 mossvale frostmark rainport flintroad driftpine
@06 bracken frostmark driftpine q0603 cloudrest
@06 windmere q0602 cloudrest frostmark moonbay
