# 2025 alias migration (3.0)

Release 3.0 introduced canonical source aliases to make names from the batch
importer and the service exporter converge. The migration initially normalized
aliases with `casefold()` and performed repeated alias lookup until a fixed
point. That looked helpful but made configuration errors silently redirect
unknown names. The 3.2 release uses exact, case-sensitive alias keys after
removing only ASCII spaces and performs one lookup.

The migration also introduced global key abbreviations. In the first draft,
source-specific aliases ran before global aliases. The resulting behavior was
hard to explain when an alias target itself had an abbreviation. The current
release order is explicit: edge spaces, casefold, one global lookup, then one
source-specific lookup. The source-specific table is indexed by the already
canonical source.

A tab in an imported name was a real character from the beginning of the
migration. A review changed a broad `.strip()` to `.strip(" ")` for source,
key, and label fields. Preserve that distinction even if test data usually uses
ordinary spaces.

The compatibility fixtures mention `core`, `svc`, `web`, `ui`, `jobs`, and
`batch`. They are inputs, not extra output categories. The canonical target is
the emitted source spelling, and aliases that point at the same target share
one first-seen bucket. A record with an alias still creates its target bucket
before its changes are inspected.

The 3.0 migration notes are a map of traps, not an alternative algorithm. In
particular, do not sort after canonicalization to make the result look stable:
first appearance is the stability rule chosen by 3.2.
