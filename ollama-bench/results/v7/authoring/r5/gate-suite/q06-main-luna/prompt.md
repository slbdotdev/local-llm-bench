# Translation-layer repair

Repair every source routine named by the translation repair roster.  For each roster entry,
open its paired locked check and satisfy every input/output pair in that check's `CASES` table.
The check also enforces the cross-unit registry rule: the repaired modules must have unique
roster positions in order and must agree on their protocol marker.  This is a behavioral fix;
do not edit, delete, rename, or add any test, documentation, configuration, or helper file.

The only existing files allowed to change are the roster's source modules, and the only new file
allowed is `repair-summary.txt`.  The summary must contain these keys exactly in this order:

patch-00, patch-01, patch-02, patch-03, patch-04, patch-05, patch-06, patch-07, patch-08, patch-09, patch-10, patch-11, patch-12, patch-13, patch-14, patch-15, patch-16, patch-17, patch-18, patch-19, patch-20, patch-21, patch-22, patch-23, patch-24, patch-25, patch-26, patch-27, patch-28, patch-29, patch-30, patch-31, fixed_files, implementation, tests

Write one `key: value` line for each key.  For each roster key, use the first expected output in
that key's paired `CASES` table.  Derive the count from the complete roster, record the observed
implementation status after all behavioral checks pass, and record whether the locked checks
were left unchanged.  Do not copy the CASES table into the summary.  The locked checks are the
specification and must remain byte-identical.
