# Quarterly refusal report

You are working in a checkout of this repository; your current directory is the root of the
checkout.

Assemble this quarter's refusal report. It is over the records in `data/batch-2034q3.txt`
and over no others.

This repository uses **finding** in a particular sense of its own, and that sense is written
down in the repository rather than here. So is the thing this report turns on: the order in
which a report puts its findings. That order has been settled more than once, only one of
those settlements is in force, and every one that is not in force is superseded or withdrawn.
Find the one in force and apply it.

Write the report to a new file `findings.txt` in the root of the workspace. It must contain
exactly these three lines, in this order:

    report_order: <every finding, in report order, separated by commas>
    records_at_fault: <the records that raise one finding or more, in any order>
    governing_revision: <the revision you applied, written the way the repository writes it>

Write a finding as `<record-id>/<diagnostic-code>`, and a record as its record id: a finding
might be written `R-0000/RF-0000` and a record `R-0000`. No header, no quotes, no explanation,
no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report.

Work until the report is complete, then stop.
