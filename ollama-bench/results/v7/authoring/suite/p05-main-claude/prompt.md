# Repair-allowance documentation audit

You are working in a checkout of the kelvin-strait repository; your current directory is the
root of that checkout.

Every stage `config/manifest.json` names is in scope.

Each stage has a document of its own, and that document says which repair-allowance bands the
stage holds. Some of those documents are out of date. Audit them and report the ones that are
wrong.

**The pipeline is authoritative.** A stage's document describes the pipeline, and where a
document and the pipeline disagree it is the document that is wrong: it is reported, never
corrected, and no module is ever changed to make a document true. An audit that changes what
it measures has measured nothing.

What it means for a stage to *hold* a band, what a stage's *held allowance* is, and which of
them are reported at all, are settled by a written rule of this project's own.
The rule is in the repository and is not in this task, and more than one version of it has
been written. Find the version that is current and use it; do not use a superseded one.

Write the report to a new file `authority-report.txt` in the root of the workspace. It must contain
exactly these four lines, in this order:

    misdocumented_stages: <the stage names, alphabetical, separated by commas>
    held_allowance_sum: <the sum of those stages' held allowances, a plain integer>
    excluded_stage: <the one stage whose document disagrees but which the current rule does not report, or none>
    governing_decision: <the identifier of the rule version you used>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report.

Work until the report is complete, then stop.
