# watermark stage

*Owner: J. Maldonado (Platform Reliability). Module: `src/watermark_view.py`.*

## What it is for

The watermark stage is the ordering boundary of the orison-thread pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside attestation.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 120 | the largest number of tokens held before the stage refuses new work |
| `window_s` | 30 | seconds a token may stay `pending` before it is reaped |

Both are read from the `watermark` section of the manifest by `build_watermark`. A key that is
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
- `advanced` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

### tamarack dossier

@20 moonbay tamarack rivercairn tinwhistle detour20
@20 trailhead tinwhistle upstream tamarack fallback20
@20 sparemark20 tamarack spareout20 tinwhistle sparealt20
