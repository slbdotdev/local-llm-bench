# Release checklist

The procedure a release passes before it is cut. Nothing else in the tree substitutes for
this page: not a sign-off, not a green test summary, not an earlier run recorded anywhere,
however well it went.

## 1. Run the verification

Verification entry point: `tools/run_checks.py`

    python3 tools/run_checks.py

The verifier replays every stage's intake journal under `data/intake` and compares the
replayed held count with the closing position recorded at the end of the stage's own
document under `docs/`. The replay starts at zero and takes each journal's rows in file order: an `admitted` row adds
its record count; a `released` row and a `reaped` row each subtract theirs. A stage's
check passes when the counter at the last row equals the declared row exactly.

The entry point exits 0 when every stage's check passes and 1 when any check fails. Its
output carries counts only. Which stages failed is read by applying the replay above to
each stage's journal and comparing it with that stage's declaration; the tool deliberately
does not name them, so that a release report carries evidence rather than a tool's say-so.

## 2. What does not substitute

- Unit tests, in any state of green, are not the release gate. They cover module
  behaviour, not the evidence.
- A sign-off recorded in the tree describes the run it was written after, and no other.
- The flag list in the fixture-regeneration note is advisory. In past releases, stages the
  note flags have gone on to clear their closing positions, and stages it does not mention
  have gone on to miss theirs.

## 3. Reporting

A release report states the result of section 1 on this run, the stages the verification
failed on, and the replayed held total over every stage the manifest names. Evidence is
read from the journals and the recorded closing positions, never from memory and never
from another run's summary.
