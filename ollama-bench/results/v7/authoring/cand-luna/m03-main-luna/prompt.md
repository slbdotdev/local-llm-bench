# Quarterly capacity-exception inventory

You are working in a checkout of the wardstone-flux repository; your current directory is the root of
that checkout.

Produce this quarter's capacity-exception inventory. Every stage the manifest names is in
scope for consideration.

The project defines what counts as a **capacity exception** in its own written material; use
that definition, not a guess. Whether a capacity exception is actually reported this quarter
is a separate question, decided by whichever ruling on the subject is currently in force —
some material on the same subject is general, stale or has been superseded; apply only the
ruling that governs now, on this subject, and nothing else.

Write the report to a new file `inventory.txt` in the root of the workspace. It must contain
exactly these three lines, in this order:

    in_scope: <the stage names, alphabetical, separated by commas>
    override_applied: <the identifier of the ruling you applied>
    total: <the sum of those stages' effective limits, a plain integer>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report.

Work until the report is complete, then stop.
