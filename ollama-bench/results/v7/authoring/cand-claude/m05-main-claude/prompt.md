# Window documentation checklist

You are working in a checkout of the hearth-relay repository; your current directory is the root of
that checkout.

Every stage's component document carries an `enforced_window_s` row in its configuration
table. Check it against the value the code actually uses, `ENFORCED_WINDOW_S` in the stage's own
module. **Where the two disagree, the module governs**: the document is what an operator was
told and the module is what the code does, and a corrected row reports the module's number,
never the document's. Read the tree to find which design record currently rules this way and
cite its identifier exactly as that record names itself (a short dashed code, for example
`DR-0091`, case as written); an earlier record ruled the opposite way and was superseded, and
citing it is wrong.

Some stages are exempt from this comparison entirely: they were moved to a new enforced-window
baseline, their document intentionally still shows the number from before the move as a
historical record, and their row is `MATCHES` regardless of what the numbers say. The tree
records why, and which stages, though not in the same place: find the current, complete list,
not a partial or an out-of-date one.

Write the checklist to a new file `doc-checklist.txt` in the root of the workspace: one line for
every stage the manifest names, in the manifest's own order, then exactly these two summary
lines, in this order:

    <stage-name>: MATCHES
    <stage-name>: CORRECTED <the module's enforced-window value>
    ...
    corrected_count: <the number of CORRECTED rows, a plain integer>
    authoritative_source: <the identifier of the design record currently in force>

Exactly one line per stage, in the manifest's own order, then the two summary lines, and
nothing else. No header, no quotes, no explanation. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the checklist.

Work until the checklist is complete, then stop.
