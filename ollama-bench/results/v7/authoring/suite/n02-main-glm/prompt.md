# Quarterly recheck report

You are working in a checkout of the linnet-slack repository; your current directory is the
root of that checkout.

Produce the operations team's quarterly recheck report. Every stage the manifest names is in
scope.

Each stage runs at a recheck interval of its own, and the project runs a bulletin series that
amends those intervals stage by stage. When more than one bulletin names a stage, the
project's written rulings fix which of them governs; find that rule and apply it. The rulings
also fix what a stage's *effective* interval is, and they use *out of sequence* in a sense of
their own. Apply their senses, not the phrases' ordinary ones.

Write the report to a new file `recheck-report.txt` in the root of the workspace. It must contain
exactly these three lines, in this order:

    out_of_sequence: <the stage names, alphabetical, separated by commas>
    stale_docs: <the stage names, alphabetical, separated by commas>
    recheck_total: <the sum of every stage's effective interval, a plain integer>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

For `stale_docs`: a stage is stale when the recheck interval stated by the stage's own
component document is not the stage's effective interval.

Do not modify or delete any existing file, and create no file other than the report. A report
that repairs what it reports on has measured nothing.

Work until the report is complete, then stop.
