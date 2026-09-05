# Caller notes

The batch importer sends records in file order. It can emit several records for
the same source because a source's changes arrive in pages. It does not merge
pages first: doing that in a caller would change first-seen entry order and
would make an empty page indistinguishable from a missing page.

The service exporter uses short source aliases (`svc`, `web`, `ui`) and key
abbreviations (`err`, `warn`, `lat`, `dur`, `cfg`). The build exporter uses
`core`, `jobs`, and `batch`, and sometimes surrounds a field with ordinary
spaces. Neither exporter lowercases source names. The adapter owns the exact
canonicalization so the two callers converge without pre-processing.

An operations replay may contain `ignore` and `void` changes. They are sent to
the same adapter rather than filtered in the caller so the source bucket is
still recorded. An operations hold is a real observation: its zero contribution
must not make it disappear, and its labels are useful to the review screen.

The UI reads entries in returned order to display the first observed key first.
It reads `occurrences`, not whether `total` is nonzero, to show activity. It
also displays labels in returned order and expects canonical lower-case values.
No caller relies on implementation-only fields, and no caller is allowed to
mutate the returned list back into the next input batch.

A common integration mistake is to use a dictionary comprehension keyed by
source or key and then iterate it after sorting. That merges values but loses
the temporal order the UI uses. Another is to build labels with a set; the UI
would then flicker because set order is not the contract even when the set's
contents are right.
