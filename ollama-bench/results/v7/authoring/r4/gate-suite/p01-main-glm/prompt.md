# Compatibility report

You are working in a checkout of the quayside-shuttle repository; your current directory is the
root of that checkout.

This project once made its clients a compatibility promise concerning the deliveries its
stages keep. The promise is written in exactly one record in the repository, in the project's
own words; it has never been amended, and no other file restates it. Find that record and
treat it as the authoritative source. Where a superseded note says something different, the
superseded note is not the promise.

Work out, from each component's own records, whether that component's evidence store has
been emptied of a delivery while its protection under the promise had yet to expire. Every
component the manifest names is in scope.

Write the report to a new file `compatibility-report.txt` in the root of the workspace. It must contain
exactly these lines, in this order:

    required_behavior: <the promise's term for the span an acknowledged delivery remains protected, quoted exactly as the record words it>
    affected_components: <the components the promise rules out, alphabetical, separated by commas>
    authoritative_record: <the identifier of the record that carries the promise>
    regression_evidence: <for every component in scope, in that same alphabetical order, separated by commas: the day its final acknowledged delivery stopped being protected>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report.

Work until the report is complete, then stop.
