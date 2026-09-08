# ingest stage

*Owner: C. Batbayar (Data Stewardship). Module: `src/ingest_store.py`.*

## What it is for

The ingest stage is the intake boundary of the hearth-relay pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside retention.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 32 | the largest number of batchs held before the stage refuses new work |
| `window_s` | 90 | seconds a batch may stay `pending` before it is reaped |
| `window_note_00` | retained | contextual release annotation |
| `window_note_01` | retained | contextual release annotation |
| `window_note_02` | retained | contextual release annotation |
| `window_note_03` | retained | contextual release annotation |
| `window_note_04` | retained | contextual release annotation |
| `enforced_window_s` | 2031 | the seconds this stage actually enforces, tracked outside the legacy window_s field |

Both are read from the `ingest` section of the manifest by `build_ingest`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with retention and quota

`retention` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `quota`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `settled` - durable, visible to the audit trail, immutable
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted
