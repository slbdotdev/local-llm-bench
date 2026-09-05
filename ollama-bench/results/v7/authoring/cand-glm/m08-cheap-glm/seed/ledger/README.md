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
