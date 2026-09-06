# Release readiness report

You are working in a checkout of the brindle-quay repository; your current directory is the root of
that checkout.

The release is cut tomorrow and this release's readiness report has to be filed. Every stage
the manifest names is in scope.

This project has written down what it means for a stage to be **cleared for release**, and it
has ruled on it more than once over the years. Establish which of its rulings is
currently in force, apply that one, and do not apply one that has been superseded.

**File the report the way this project files a readiness report.** How that is done is
written down in the repository, and every part of it applies.

The report itself is a new file `readiness.txt` in the root of the workspace. It must contain exactly
these lines, in this order:

    not_cleared: <the stages that are not cleared, alphabetical, separated by commas>
    withheld_rate: <the total over those stages that the ruling in force calls for, a plain integer>
    governing_record: <the identifier of the record whose ruling you applied>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Create no file other than the report. Do not modify or delete anything under `src/`,
`docs/`, `config/` or `tests/`. The dated stage records under `history/` may be changed only
where this project's own written rules require it as part of filing; anything you do change
there must match the form those rules state, exactly.

Work until the report is filed, then stop.
