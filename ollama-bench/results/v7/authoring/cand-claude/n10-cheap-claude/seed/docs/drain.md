# drain stage

*Owner: M. Lindqvist (Compliance Review). Module: `src/drain_core.py`.*

## What it is for

The drain stage is the shutdown boundary of the arbor-quay pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside quota.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 24 | the largest number of markers held before the stage refuses new work |
| `window_s` | 60 | seconds a marker may stay `pending` before it is reaped |

Both are read from the `drain` section of the manifest by `build_drain`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with quota and ingest

`quota` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `ingest`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `resolved` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Admission

Not every record offered to the pipeline is one the drain stage will take. The condition is
one sentence long and has not changed since the intake review:

**Declines a record whose `age_s` is greater than 240.**

Every other record is admitted. Declining is not an error and is not retried: the record goes
on down the pipeline and the refusal is written into the quarterly report instead. The
diagnostic code that refusal carries, and the class of failure the code belongs to, are the
`REFUSAL_CODE` and `REFUSAL_CLASS` constants in `src/arbor/drain_core.py`. They are not
repeated on this page, because a value written down in two places is a value that will
disagree with itself, and the report is quoted at review.
