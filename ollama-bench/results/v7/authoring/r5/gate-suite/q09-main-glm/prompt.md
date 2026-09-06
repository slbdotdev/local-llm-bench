# Quarterly settlement report

You are working in a checkout of a delivery-pipeline repository; your current directory is
the root of that checkout.

This cycle's carryover settlement has not yet been computed. Produce it. Every component
the manifest names is in scope.

The repository's own written procedure governs the settlement: what the log's columns
mean, which rows take effect, where each applied figure comes from, and the order the
entries are applied in. That procedure is what you must apply — not the ordinary reading
of the log's column names, and not any summary previously filed in the tree. Find the
procedure and apply it from its first entry to its last.

Write the report to a new file `settlement-report.txt` in the root of the workspace. It must contain
exactly these eight lines, in this order:

    figure_after_05: <the settlement figure after the fifth entry, a plain integer>
    figure_after_10: <the same, after the tenth entry>
    figure_after_15: <the same, after the fifteenth entry>
    figure_after_20: <the same, after the twentieth entry>
    figure_after_25: <the same, after the twenty-fifth entry>
    figure_after_30: <the same, after the thirtieth entry>
    figure_after_35: <the same, after the thirty-fifth entry>
    figure_final: <the settlement figure after the chain's last entry, a plain integer>

Entries are counted in the order the procedure prescribes, the chain's first entry
counting as entry one. No header, no quotes, no explanation, no other lines. The report
may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report.

Work until the report is complete, then stop.
