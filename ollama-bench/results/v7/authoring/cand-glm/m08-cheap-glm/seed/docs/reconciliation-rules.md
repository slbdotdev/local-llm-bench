# Reconciliation rules

Owner: Compliance Review. These rules govern any figure computed from the
monthly ledger files.

1. Files are used whole. The three files under `ledger/` cover
   2026-07-01 to 2026-09-30; there are no earlier or later rows to
   consider for the current books.
2. An account's balance is its `OPENING` row in the July file (the
   balance carried into the period) plus every other row of that account.
3. A row with status `REVERSED` contributes nothing. The matching row
   with status `REVERSAL` also contributes nothing. The pair cancels
   formally: neither line is part of any balance, of any count of counted
   rows, or of any subtotal.
4. Amounts are read exactly as stored: two decimals, credits positive,
   debits negative. No re-rounding, and no netting of pairs beyond rule 3.
5. Transfers appear once on each side with the same `entry` reference and
   opposite amounts; each line is an ordinary row of its own account.
6. A balance is never adjusted for unrecorded events. If a physical
   matter (a shortage, a pending count) has not been entered as a ledger
   row, it does not exist for reconciliation purposes.
