# audit stage

*Owner: C. Batbayar (Compliance Review). Module: `src/audit_core.py`.*

## What it is for

The audit stage is the evidence boundary of the orison-thread pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside attestation.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 960 | the largest number of manifests held before the stage refuses new work |
| `window_s` | 30 | seconds a manifest may stay `pending` before it is reaped |

Both are read from the `audit` section of the manifest by `build_audit`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with attestation and backfill

`attestation` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `backfill`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `deferd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

### birchline dossier

@02 brindle birchline bluefen brookstone detour02
@02 briarcode brookstone blackthorn birchline fallback02
@02 sparemark02 birchline spareout02 brookstone sparealt02
