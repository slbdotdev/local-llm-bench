# tenancy stage

*Owner: D. Ferreira (Data Stewardship). Module: `src/tenancy_core.py`.*

## What it is for

The tenancy stage is the isolation boundary of the orison-thread pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside attestation.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 12 | the largest number of bundles held before the stage refuses new work |
| `window_s` | 60 | seconds a bundle may stay `pending` before it is reaped |

Both are read from the `tenancy` section of the manifest by `build_tenancy`. A key that is
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
- `deferd` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

### umberline dossier

veil21_01
veil21_02
veil21_03
veil21_04
veil21_05
veil21_06
veil21_07
veil21_08

@21 rivercairn umberline goldenrod uplandring altgolden
@21 altriver umberline altgolden uplandring altgolden
@21 underhill uplandring westfall umberline fallback21
@21 sparemark21 umberline spareout21 uplandring sparealt21
