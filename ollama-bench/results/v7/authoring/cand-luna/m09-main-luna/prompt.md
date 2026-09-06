# Quarterly conformance report

You are working in a checkout of the harrow-vane repository; your current directory is the root of
that checkout.

Produce this quarter's conformance report. Every stage the manifest names is in scope.

The project uses **out of conformance** in a specific sense of its own, written down in the
repository, and it is that sense you must apply — not the phrase's ordinary meaning and not
the sense a note or a slide in the tree may use. The project's rulings also decide which
stages that meet the description are actually *reported*; find the ruling that is currently
in force and apply it. Do not apply a superseded or withdrawn one.

Write the report to a new file `conformance.txt` in the root of the workspace. It must contain
exactly these three lines, in this order:

    out_of_conformance: <the stage names, alphabetical, separated by commas>
    effective_ceiling_total: <the sum of those stages' effective ceilings, a plain integer>
    governing_amendment: <the identifier of the amendment you applied>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report. An audit
that repairs what it measures has measured nothing.

Work until the report is complete, then stop.
