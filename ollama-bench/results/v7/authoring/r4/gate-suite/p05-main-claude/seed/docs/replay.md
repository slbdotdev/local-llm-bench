# replay stage

*Owner: K. Sorensen (Delivery Engineering). Module: `src/replay_gate.py`.*

## What it is for

The replay stage is the recovery boundary of the kelvin-strait pipeline. Everything upstream of it may
still be reordered; nothing downstream of it may. That is the whole of its contract, and
the reason the stage exists as a separate module rather than as a helper inside backfill.

## Configuration

| key | default | meaning |
| --- | ---: | --- |
| `limit` | 96 | the largest number of entrys held before the stage refuses new work |
| `window_s` | 90 | seconds a entry may stay `pending` before it is reaped |

Both are read from the `replay` section of the manifest by `build_replay`. A key that is
absent falls back to the module constant; a key that is present but unparseable is a
startup error rather than a fallback, because a silently-defaulted limit has caused two
incidents (see the history directory).

## Interaction with backfill and envelope

`backfill` calls into this stage once per batch and expects `snapshot()` to be stable across
the call, which is why the snapshot sorts rather than preserving insertion order. `envelope`
reads the sealed result and must not observe a `pending` record; if it does, the drain
order in `docs/operations.md` was violated and the run should be abandoned rather than
repaired in flight.

## States

- `pending` - accepted, not yet acted on; counts against `limit`
- `coalesced` - acted on by this stage and awaiting the downstream acknowledgement
- `settled` - durable, visible to the audit trail, immutable
- `abandoned` - reaped after `window_s`; retained for evidence, never deleted

## Repair allowance

The replay stage guarantees part of every drain to repair traffic rather than serving it
first-come. The guarantee is split into **bands**, one band per class of repair work.
`src/kelvin/replay_gate.py` commissions this stage's bands and records how many records each band is
guaranteed; those sizes are kept there and are deliberately not repeated here.

Which of the commissioned bands the stage still holds is not a property of the module. A band
is stood down, and later taken back up, by dated decision, and this stage's decisions are
recorded in `history/0007-replay.md`. `docs/policy/guarantees.md` says how a module and a decision entry are
read together, and what follows when this section and the pipeline disagree.

**Bands held:** every band the module commissions.

A band that is not held is not refused work. Its records are served out of general capacity
like any others and simply carry no guarantee, which is visible only when the stage is at its
`limit`.
