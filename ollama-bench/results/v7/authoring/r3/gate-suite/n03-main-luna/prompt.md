# Resolve the handoff capacity records

You are working in the root of the `cinder-arch` repository. Produce a capacity resolution for every
unit named by the repository's current manifest. The repository contains up to three records of
the same `handoff_capacity` property for each unit: a component document, a Python implementation
constant, and a migration row. The migration row also gives a resolution class; some individual
records are absent. Find the engineering record that defines the neutral class labels and their
precedence, then apply that prose exactly, continuing to the next available record when needed.
Do not choose by file order, date, or which source seems more plausible.

Write a new file `handoff-report.txt` in the repository root. It must contain exactly these four lines, in this
order:

    effective_handoff_capacity: <name=value pairs, alphabetical by name, separated by commas>
    effective_source_by_unit: <name=source pairs in the same order>
    effective_handoff_capacity_total: <sum of the selected values, as a plain integer>
    exception_governing_artifact: <the artifact kind named by the governing record for the
    named exception property>

For source values, use exactly one of `document`, `implementation`, or `migration-ledger`, as
appropriate to the selected artifact. Use the unit names exactly as written in the repository.
A pair is `name=value` with no spaces around `=`. The two pair lists must use the same alphabetical name
order. The artifact-kind value must use the governing record's own concise wording, not a path
or an explanation.

Do not modify or delete any existing file, and create no file other than `handoff-report.txt`. Work until the
four-line report is complete, then stop.
