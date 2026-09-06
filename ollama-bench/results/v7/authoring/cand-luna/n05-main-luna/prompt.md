# Allocation review report

You are working at the root of the `cinder-parcel` checkout.  The stages in
`config/manifest.json` are the complete scope of this review.

Prepare a report of the allocation review.  For every stage, use its human-readable label as
the name you report.  The repository's allocation-key policy explains how to compute the
four-digit key: first obtain that stage's deployment ordinal and region offset, multiply them,
and then search for the allocation record whose filename contains the resulting key.  Read the
record's `Disposition` line.  Do this for every stage; do not match records by directory order,
module order, or opening order.

Report the labels of the stages whose disposition is exactly `reroute`, the number of those
stages, and the canonical join formula stated by the policy; copy the formula verbatim from
the policy, field names and all.  Put the labels in one comma-
separated value; their order is not significant.

Write a new file `allocation-report.txt` in the checkout root with exactly these three keys,
in this order:

    reroute_stages: <comma-separated human stage labels>
    reroute_count: <plain integer>
    join_formula: <the canonical formula>

No header, quotes, explanation, or other lines.  Whitespace around values is not significant.

Do not modify or delete any existing file, and create no file other than the report.
