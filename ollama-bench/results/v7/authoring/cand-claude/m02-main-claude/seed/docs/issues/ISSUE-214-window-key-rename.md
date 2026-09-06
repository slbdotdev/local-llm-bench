# ISSUE-214 - rename the `window_s` configuration key

- Filed by: Client Integrations
- Status: **open**

## What is wanted

External consumers of the published configuration surface keep confusing the
`window_s` key with the batch-windowing concept the pipeline uses internally,
which is an unrelated idea and lives nowhere in a stage's configuration table.
The fix is a rename: every stage's component document, in the configuration
table only, spells the row's key `quiesce_s` instead of `window_s`. The value
and the description column are untouched; only the key changes.

## Which stages this reaches

Not every stage. This reaches a stage only when that stage's configuration
surface is currently **published** in the sense the API contract defines, and
even a published stage is out of reach if the security boundary freezes it
against this class of change. Both documents are authoritative over this one;
this issue requests the change, it does not decide who is in scope for it.

## Why a document rename and not a module rename

The module constants (`DEFAULT_<STAGE>_LIMIT`, `DEFAULT_<STAGE>_WINDOW_S`) and
the manifest key `window_s` are unaffected. Only the prose table a human reads
changes; the assembler never parses a document.
