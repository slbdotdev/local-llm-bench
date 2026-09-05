# Ledger close repair

This is a small reconciliation service at the end of a long-running payment migration.
The Python package in `src/` is the code under repair.  The transaction feeds in `data/`,
the policy memos, and the archived close notes are all part of the service's operating
record.  Some archived notes describe rules that were later superseded.

The repaired program must expose `reconcile()` and `format_report()` from
`src/reconcile.py`.  `reconcile()` reads every Python feed in `data/region_*.py`, applies
the current close policy, and returns a dictionary.  `format_report()` renders that
dictionary as one deterministic line per section.  Keep the public signatures and return
types intact.  The feed modules are inputs, not files to rewrite.

The close being repaired is the 2025-12-31 close.  The current memo states the exact
eligibility, dispute, fee, currency, account, and ordering rules.  The history directory
is included because the migration retained several tempting but obsolete rules.

There are intentionally many records.  A row is not filler: every accepted or rejected
row is part of the close population, and the totals and counts depend on the complete
population.
