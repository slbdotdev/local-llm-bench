# towpath-stores ledger

The bookkeeping CSVs for Towpath Stores, a chandlery and wholesale
counter on the canal. Three monthly ledger files, the reconciliation
rules, and the paper trail around them. No code: the ledger is maintained
by hand from the till and the invoice folder.

## Layout

    ledger/                  monthly CSVs, oldest first
        2026-07.csv          includes each account's OPENING row
        2026-08.csv
        2026-09.csv
        README.md            column reference
    docs/                    rules, procedures, glossary, account map
    incident/                the open August shortage file and correspondence
    notes/                   working notes (drafts, partial counts)
    ops/                     count rota and depot checklists
    history/                 decision records

## TODO(before Q4): migrate this CSV ledger to the new stock system
schema. Estimate: two sprints of mapping work plus a parallel-run month.
Not started; owner wanted. Until it happens, the CSVs remain the books of
record.

## Status

The books are current to 2026-09-30. Finance raised one query on the K-7
figure in early October; the query is handled by whoever picks it up.
The August shortage remains open and paused on IT (see incident/); it
has no ledger side, by rule 6.
