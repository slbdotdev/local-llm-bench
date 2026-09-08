# DR-0055 - keeping the enforced-window document and the module in step

- Status: **superseded by DR-0091**

## The rule

Every stage's component document carries an `enforced_window_s` row in its configuration table.
A stage's component document is authoritative for its enforced window. Where the
module's `ACTIVE_WINDOW_S` disagrees with the document, the module is what has drifted and is
corrected to match the document at the next release.

## Status

Superseded. Correcting a module to match a document required a deploy for a change
that was, in every incident so far, actually a stale document; the module was never
once found to be the one that was wrong. Kept for its reasoning at the time.
