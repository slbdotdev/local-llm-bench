# Regional retention report

You are working at the root of the `sable-arc` repository. Every region named by the repository
manifest is in scope. Read the project's glossary, the active dated decision, each region's
component record for context, its own history entry, the module-facing interval notes, and the
resolved retention event history. The old spot-check page is only a lead. Apply the project's
definition of **regional retention**, then apply the amendment that is currently in force. A
verification is complete only under the repository's stated event-history rule.

Write a new file `retention-report.txt` in the repository root with exactly these four lines, in
this order:

    effective_window: <the sum of the effective windows for excluded regions, as a plain integer>
    governing_amendment: <the identifier of the active amendment>
    excluded_region: <excluded region names in alphabetical order, separated by commas>
    verification_path: <the path stated by the active decision record>

The file may or may not end with a newline. Do not add a header, explanation, quotes, or other
lines. Do not modify or delete any existing file, and create no file other than the report.
