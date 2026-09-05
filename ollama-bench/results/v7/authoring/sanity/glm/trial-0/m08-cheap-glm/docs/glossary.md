# Glossary - ledger

- **Books of record** - the three monthly CSVs under `ledger/`. Until the
  migration in the README's TODO lands, they are the only authoritative
  figure source.
- **OPENING row** - the first row of an account in the July file: the
  balance carried into the fiscal year. Set once, at the year boundary.
- **Invoice (INV-<n>)** - a charge to a customer, a credit to its
  account.
- **Credit note (CN-<n>)** - a refund or correction issued to a
  customer, a debit on its account.
- **Transfer (TR-<n>)** - a movement between two accounts. Appears twice
  with the same reference, once on each side, amounts opposite.
- **Payment run (PM-<n>)** - money actually moving out the door to a
  supplier.
- **REVERSED / REVERSAL** - an entry raised in error and the line that
  undoes it. Both stay in the file for the audit trail; both count as
  nothing (reconciliation rules, rule 3).
- **Excluded rows** - the REVERSED and REVERSAL lines of an account.
  They are excluded from balances and from counts of counted rows alike.
- **Counted rows** - the account's rows that are not excluded: the
  OPENING row plus every ordinary row.

A figure in a report is either traceable to counted rows by these rules
or it does not go out.
