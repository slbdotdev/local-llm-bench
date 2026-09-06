# Capacity reconciliation record CR-27

- Status: **in force**
- Applies to: every stage named by the repository's current assembly manifest
- Supersedes: CR-19 (the module was treated as authoritative for all handoffs)

## Purpose

The platform team has found three honest records of a stage's handoff capacity. The
component owner writes a capacity in the stage document, the implementation carries a
capacity in its Python module, and the migration operator records a capacity when the
handoff review is performed. They are often edited at different points in a rollout.
A disagreement is therefore evidence to reconcile, not permission to choose the value
that appears newest or the value that looks most operationally plausible.

The property covered by this record is `handoff_capacity`. The migration row also carries
a resolution class. That class is metadata about how the three records are to be read
and is not itself a fourth capacity. Do not infer a class from the order of the files,
from the date, or from which team owns the artifact.

## What the three records mean

A component document is the owner's stated operating expectation. The Python module
constant is the value the implementation has been configured to use. The migration
ledger is the operator's value recorded during the reconciliation exercise. All three
are retained because each explains a different part of a disagreement.

The ledger is not generally stronger merely because it has a date. A date orders
events; it does not change the precedence that this record sets out below. Likewise,
the module is not generally stronger merely because it controls runtime behaviour.
The report must apply the class attached to each stage's migration row.

## Resolution rules

Rule document-led: for `handoff_capacity`, precedence is component document, then Python
module constant, then migration ledger.

Rule module-led: for `handoff_capacity`, precedence is Python module constant, then
component document, then migration ledger.

Rule ledger-led: for `handoff_capacity`, precedence is migration ledger, then Python
module constant, then component document.

The ledger-led rule is the only exception: the migration ledger outranks the Python
module constant only for the named `handoff_capacity` property. No other property in
the repository receives that treatment. The exception is about the property name, not
about a particular stage, operator, date, or directory.

The words *first*, *then*, and *last* above are precedence, not instructions to edit
anything. Select the first available record in the stated order. In this exercise all
three records are present for every stage, so a later fallback does not replace an
earlier value.

## Reporting convention

A capacity resolution is a reading of the repository at the time of the review. It
does not repair the document or module, and it does not rewrite the migration ledger.
The report names the selected source for each stage so a later operator can explain
why two records were not selected. The total is the sum of the selected effective
capacities, not the sum of all three copies and not the sum of legacy limits.

Stage names in a report are written in alphabetical order. This is a presentation
convention only; the class remains attached to the stage named by its own ledger row.

## Review history

CR-19 treated the implementation as the answer and caused owner documentation to drift.
CR-22 tried to use the latest recorded value, which made a later review overwrite an
earlier decision without explaining the change. Both records remain as history because
they explain why this record calls out precedence explicitly.

The current record was approved after the capacity migration review. Its status is in
force, and its three class rules are the governing interpretation for this report.

## Operator checklist

Read the roster of stages, then locate each stage's three handoff_capacity records.
Read the resolution class on the migration row, apply the matching rule above, and
write the selected value and source. Check the total by adding selected values. Do not
change a source file merely to make the three records agree.

## Terms retained for searchability

A legacy limit is a generated assembly setting and is not a handoff capacity. A
window is a timeout and is not a precedence class. A review date is evidence about
when a row was recorded and is not a fourth source. These terms appear in nearby
material because operators routinely confuse them with the property in this record.
