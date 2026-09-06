# Cutover readiness report

You are working in a checkout of the lantern-quay repository; your current directory is
the root of that checkout.

The migration window opens only when every stage's acceptance is in order, and the
project's acceptance procedure, written in this repository, is what decides what "in
order" means: it defines what it means for a stage's acceptance to be on file, what makes
an acceptance record signed, and how a stage accepted as part of a group is recorded.
Find it and apply it.
Every stage the manifest names is in scope, and the report follows the manifest's order.

Write the report to a new file `cutover-report.txt` in the root of the workspace. It must contain
exactly these four lines, in this order:

    missing_acceptance: <the stages with no acceptance on file, comma-separated, manifest order>
    unsigned_acceptance: <the stages with an acceptance on file but not signed, comma-separated, manifest order>
    blocked_count: <the number of stages without a signed acceptance record on file, a plain integer>
    batch_record: <the code that identifies the record covering the stages accepted as one batch>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report; the
checkout must remain exactly as you found it.

Work until the report is complete, then stop.
