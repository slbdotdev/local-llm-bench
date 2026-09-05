# Output contract

`reconcile()` returns ordinary Python values: `Decimal` for the total and grouped
amounts, `str` for IDs and keys, and `int` for the count.  It must not return JSON text.

`format_report(report)` returns exactly five lines in this order: `TOTAL <decimal>`,
`ACCOUNTS <key=decimal,...>`, `TAX <key=decimal,...>`, `COUNT <integer>`, and
`IDS <id,id,...>`.  The comma-separated entries in the two grouped lines use the sorted
keys already required by the current policy.  A zero-valued group is still printed if
the group has an accepted row; there are no synthetic groups.
