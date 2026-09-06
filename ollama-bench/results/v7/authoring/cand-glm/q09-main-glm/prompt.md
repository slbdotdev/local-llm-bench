# Settlement report

You are working in a checkout of a delivery-pipeline repository; your current directory is
the root of that checkout.

This cycle's carryover settlement has not yet been computed. Compute it. The manifest
names what is in scope.

The repository's own written procedure has the rules of the settlement: what the log's
columns are for, which rows count, where each figure is read from, and what order the
entries go in. That procedure is what you must apply — not the ordinary reading of the
log's field names, and not any summary previously filed in the tree. Find the procedure
and apply it from its opening entry to its final entry.

Write the report to a new file `settlement-report.txt` in the root of the workspace. It must contain
exactly these eight lines, in this order:

    figure_after_05: <the settlement figure after the 5th entry, a plain integer>
    figure_after_10: <the same, after the 10th entry>
    figure_after_15: <the same, after the 15th entry>
    figure_after_20: <the same, after the 20th entry>
    figure_after_25: <the same, after the 25th entry>
    figure_after_30: <the same, after the 30th entry>
    figure_after_35: <the same, after the 35th entry>
    figure_final: <the settlement figure after the chain's final entry, a plain integer>

Entries are counted in the procedure's order, its opening entry being entry one. No
header, no quotes, no explanation, no other lines. The report may end with a newline or
not.

Do not modify or delete any existing file, and create no file other than the report.

Work until the report is filed, then stop.
