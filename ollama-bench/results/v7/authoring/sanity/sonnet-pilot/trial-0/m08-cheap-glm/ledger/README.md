# Ledger columns

All three monthly files share the same columns:

    date,account,entry,description,amount,status

- `date` - ISO date of the entry.
- `account` - the ledger account (see docs/account-map.md).
- `entry` - a short reference: INV-<n> invoice, CN-<n> credit note,
  TR-<n> transfer, PM-<n> payment run, REV-<n> reversal, OPENING.
- `description` - free text from the invoice folder.
- `amount` - euros with two decimals. Credits to the account are
  positive, debits are negative, exactly as stored.
- `status` - normally empty. `REVERSED` marks an entry that was later
  reversed; `REVERSAL` marks the line that undoes it. How reversals are
  treated is governed by docs/reconciliation-rules.md, rule 3.

Example rows, to show the shape (fictional entries, not in any file):

    date,account,entry,description,amount,status
    2026-01-05,K-7,INV-9999,invoice 9999 example wharf,100.00,
    2026-01-06,K-7,INV-9999,invoice 9999 example wharf,100.00,REVERSED
    2026-01-06,K-7,REV-9999,reversal of invoice 9999,-100.00,REVERSAL
    2026-01-07,K-7,CN-9998,credit note 9998 example wharf,-25.00,

The example account's balance from these rows is 75.00: the pair counts
as nothing and both of its lines are excluded rows; the OPENING row
would come first in a real July file. INV-9999, REV-9999 and CN-9998 do
not exist in this tree's ledgers and never did.

