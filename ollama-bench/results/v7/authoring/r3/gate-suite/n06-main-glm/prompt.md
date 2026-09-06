# Flush-budget reconciliation report

You are working in a checkout of the vardy-loom repository; your current directory is the root
of that checkout.

Every stage the manifest names is in scope.

Each stage's flush budget is declared twice, and nowhere else:

- the stage's component document records the value the review accepted, together with
  the unit that value was stated in;
- the stage's implementation module declares the same budget as a bare constant, in the
  unit the ruling fixes.

The two declarations differ for some stages. Which unit is canonical - the unit
totals and comparisons are to be made in - is not stated here: the repository's own
documentation fixes it in a written ruling, and it is that ruling you must find and
apply.

Write the report to a new file `budget-reconciliation.txt` in the root of the workspace. It must contain
exactly these four lines, in this order:

    accepted_budget_total: <the sum of the accepted budgets of every stage in scope,
    normalised to the canonical unit, as a plain integer>
    implementation_drift: <the stage names whose implementation constant does not equal
    its accepted budget once both are normalised, alphabetical, separated by commas>
    greatest_gap_stage: <the name of the single stage whose two declarations differ by
    the largest amount once both are normalised>
    greatest_gap_amount: <that largest amount, normalised to the canonical unit, as a
    plain integer>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than the report.
A reconciliation reports; it does not repair what it measures.

Work until the report is complete, then stop.
