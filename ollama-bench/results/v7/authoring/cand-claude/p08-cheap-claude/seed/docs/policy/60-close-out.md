# Policy: close-out

*What a stage may still be holding at a quarter close, and what closes it.*

**This policy outranks `docs/architecture.md`, `docs/operations.md`, every component
document and every history entry.** Where a component document describes behaviour this
policy forbids, the component document is stale and is to be corrected, not followed.

## Rules

1. Each stage's holdings are filed in the evidence store, one file per stage under
   `evidence/`. Those files are the record. A dashboard, digest or summary that reports a
   hold is a derived view: where a derived view and the store disagree, the derived view is
   corrected from the store, and never the other way round.
2. A stage's closing hold for a quarter is the sum of the filings that stand in that stage's
   holdings file at the close. A filing that a later line in the same file withdraws does not
   stand and is not counted, in either direction.
3. The close-out ceiling is **150 records**. A stage whose closing hold is greater
   than the ceiling is carried into the next quarter's review; a stage at or below the
   ceiling is not. The ceiling is set between two holds rather than on one, so no stage's
   closing hold is ever exactly equal to it.
4. A quarter close is recorded by a dated entry under `history/`, in the ordinary form every
   other entry there uses. Where more than one dated entry covers the same close, only the
   accepted one is live: a superseded entry is kept as evidence and is never cited.
5. A close-out record names the stages carried forward, what they are holding between them,
   and the entry it is filed against. It does not repeat the per-stage figures, because the
   store already has them and two copies of a number are one copy too many.
6. Nothing in this policy asks anyone to reconcile a derived view with the store. That is
   ordinary follow-up work, it is tracked where such work is tracked, and a close is not held
   open for it.

## Working out a closing hold

Take the stage's holdings file and read the register in the order it is written. Add each
filing that stands, with its sign: a placement adds, a release subtracts. Leave out any
filing the file's own withdrawal line names. A stage whose register read `+40`, `-10` and a
withdrawn `+5` has a closing hold of 30, not 35, and the withdrawn row stays in the register
where it is.

## What this policy does not cover

It does not say how a stage should be brought back under the ceiling. That is a capacity
question, it is answered per stage by the owning team, and a policy that tried to answer it
centrally would be wrong within a quarter. It also does not govern the retention term of any
record class; the retention policy does that, and a record released under it leaves the hold
on the day it leaves the store.
