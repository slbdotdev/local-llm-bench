# Streaming caller design note

The production adapter also has a streaming caller, but the benchmark exposes
the batch function so the result can be compared as a value. Streaming batches
are concatenated in arrival order before the same fold. A page boundary is not
a semantic boundary: a repeated key on the next page updates the existing
entry, and an empty page still creates its source if that source has not been
seen before.

The streaming note matters for two details that otherwise look like internal
implementation choices. First, source identity is established after source
canonicalization, so an alias page and a long-name page share state. Second,
entry identity is established only after action acceptance and key
canonicalization. An administrative page may therefore add a bucket without
adding an entry.

The batch result must be independent of whether the caller happened to split
the same sequence into pages. It must also be safe for the caller to retain the
input pages: the adapter cannot append labels to a change's label list or reuse
the change dictionary as an output entry.
