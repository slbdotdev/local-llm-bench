# Cutover readiness report

You are working in a checkout of the lantern-quay repository; your current directory is
the root of that checkout.

The migration window opens only when every stage's acceptance is in order, and the
project's acceptance procedure, written in this repository, is what decides what "in
order" means: it defines what it means for a stage's acceptance to be on file, what makes
an acceptance record signed, and which placements are sanctioned. Find it and apply it.
Every stage the manifest names is in scope, and the report follows the manifest's order.

Write the report to a new file `cutover-report.txt` in the root of the workspace. It must contain
exactly these four lines, in this order:

    missing_acceptance: <the stages with no acceptance on file, comma-separated, manifest order>
    unsigned_acceptance: <the stages whose acceptance is on file but not signed, comma-separated, manifest order>
    blocked_count: <how many stages are without a signed acceptance record on file, a plain integer>
    batch_record: <the identifier of the record that covers the stages accepted at batch level>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report. A
cutover that repairs what it measures has measured nothing.

Work until the report is complete, then stop.
