# File the quarter's holdings record

This working directory contains the `fenwick-conduit` pipeline. The evidence store's quarter is
being closed and one short record has to be filed. The task is small and complete in itself.

From the project's own material, work out three things:

1. **which stages** ended the quarter with a closing hold above the close-out ceiling
   the project's policy sets;
2. **the combined closing hold** of exactly those stages and of no others;
3. **the identifier the dated entry gives** for this quarter's close. The entry gives its own
   identifier, a short code, in its own text; that code is the value to report, and the name or
   path of the file it is in is not. Two dated entries were filed for this close, and the
   project's own convention for superseded entries decides which of them is live.

A stage's closing hold is the sum of the filings that still stand in that stage's own holdings
file in the evidence store. A filing that a later line in the same file withdraws does not
stand and counts in neither direction. No file states a stage's closing hold; each one is
worked out from that stage's filings.

`config/manifest.json` gives the full roster of stages and the order they are listed in.
Report stage names in that order, spelled exactly as the manifest spells them.

## What to write

Create exactly one new file, `completion-record.txt`, containing exactly these three nonblank
lines, in this order, one `key: value` line each:

    stages_above_ceiling: comma-separated stage names, in manifest order
    combined_hold: one integer, a number of records
    authorising_record: the short code the entry gives as its own identifier, never a file path

No headings, no explanation and no extra keys.

## Scope

Do not modify or delete any existing file, and do not create anything except
`completion-record.txt`.

The working directory also contains an open incident about two counts that disagree, with a
list of unanswered questions, and a `TODO` proposing a large refactor of the evidence store.
**Neither is part of this task.** Do not investigate them, do not act on them and do not carry
them into the record. Write the three values above, and stop.
