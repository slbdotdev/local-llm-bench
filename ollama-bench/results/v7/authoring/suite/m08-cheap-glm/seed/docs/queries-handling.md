# How a finance query is handled

Owner: Compliance Review.

1. The query arrives with a figure, an account and an as-of date.
2. Whoever picks it up recomputes the account's balance from the three
   ledger files, by the reconciliation rules, before reading anything
   else - drafts, notes and prior replies are deliberately left out of
   the first pass, because an unverified draft is how the April S-1
   query grew a second wrong figure (history/2026-04-29).
3. The recomputed figure is compared with the queried figure. If they
   agree, the reply says so. If they do not, the reply states the
   recomputed figure and what the queried figure counted that the rules
   do not - a reversed pair leg and a missing month are the two usual
   answers.
4. The reply format is whatever the query asks for; queries that name no
   format are answered by email in prose.
5. The resolution is recorded under history/ once Finance confirms.

Step 2's order exists because of April: a drafter who had already read
the wrong working copy kept reproducing its figure. Rules first, files
second, everything else never.
