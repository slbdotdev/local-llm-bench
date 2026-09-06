# attestation stage

*Owner: M. Lindqvist (Delivery Engineering). Module: `src/attestation_store.py`.*

## What it is for

The attestation stage is the signing boundary of the tallow-basin pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside audit.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 960 | the largest number of bundles held before the stage refuses new work |
| `window_s` | 15 | seconds a bundle may stay `pending` before it is reaped |

Both are read from the `attestation` section of the manifest by `build_attestation`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with audit and dispatch

`audit` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `dispatch`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `settled` - durable, visible to the audit trail, immutable
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Reservation adjustments

The reservation this stage runs against is not one number in one place. It is the opening
grant in `src/tallow/attestation_store.py`, as changed by the adjustment entries below.
Every entry the reallocation programme has recorded for this stage is here, including the
ones that were never carried: which of them are applied, and what the standing allowance is,
are settled by the standing ruling under `docs/policy/` and are deliberately not restated
here. Changes are in slots and are signed. A total written into a document goes stale the
day the next entry is ratified, so this table carries entries and never a total, and the
reserved figure quoted in older reviews is not maintained.

Whether this stage is holding more slots than it is allowed to hold is not answered here,
and no page in this tree answers it: it is computed from the entries below, against the
allowance the amendment in force sets. Pages that quote a figure go stale the moment an
entry is ratified; where one disagrees with the computation it is corrected by its owner and
by nobody else, so a reader who finds a disagreement records it and leaves those pages
alone.

| entry | change | state | dated | note |
| --- | ---: | --- | --- | --- |
| RA-041 | -115 | ratified | 2034-01-05 | phase one, re-derived from the intake sampling |
| RA-042 | +190 | proposed | 2034-03-13 | queued until the client migration is scheduled |
| RA-043 | -482 | ratified | 2034-06-02 | closing wave, ratified at the June review |

The `dated` column is the date the entry reached the state it is in. The owner named
at the head of this document is the one who files an entry; a second signature is
recorded in the programme's own papers and not here.
