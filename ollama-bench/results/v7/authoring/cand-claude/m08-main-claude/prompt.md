# Closeout note

You are working in a checkout of the cordage-relay repository; your current directory is the root of
that checkout.

Something in this quarter's on-call record narrowed a live defect to exactly one stage's
module, without ever finishing the diagnosis. Find that record's own conclusion — do not
re-diagnose the defect yourself, and do not fix it. Then determine, from the project's own
written material:

- which stage's module the record narrowed the defect to;
- which stage's existing, dated history record any fix to that module obliges as a follow-up
  migration;
- which stage's existing test must keep passing as the compatibility guarantee for that
  follow-up.

All three are already recorded somewhere in the tree; none of the three is named here.

Write your findings to a new file `closeout.txt` in the root of the workspace. It must contain
exactly these three lines, in this order:

    primary_module: <path to the module the defect narrows to>
    migration_record: <path to the history record the fix obliges>
    compatibility_test: <path to the existing test that must keep passing>

No header, no quotes, no explanation, no other lines. It may end with a newline or not.

Do not modify or delete any existing file, and create no file other than this one. You are not
asked to fix the defect, perform the migration, or change any test — only to report where each
one already lives.

Work until the report is complete, then stop.
