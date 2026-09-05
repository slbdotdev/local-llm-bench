# Key boundary cases

Key canonicalization has five mechanical steps: remove ASCII spaces at both
edges; case-fold; perform one global alias lookup; perform one lookup in the
table for the canonical source; use the resulting string as entry identity.
The order is observable in source-local aliases and in names containing tabs.

The global table maps err, warn, lat, dur, and cfg. The local tables map
platform compile and compilation, service request and req, frontend paint and
draw, and worker job and task. No table is applied recursively. A canonical
unknown result remains unknown.

For an empty key, the edge-space step yields the empty string, which is a valid
entry identity. A tab-only key is not empty under the release rule. A key with
an interior space keeps that interior space. Case folding handles ordinary
mixed case and the full Python string case-fold operation; no ASCII-only
lowercase substitute is specified.

Entry identity is scoped to the canonical source. The same canonical key in two
different sources creates one entry in each source. The same key across alias
spellings in one source updates one entry. A rejected first occurrence does not
reserve a position, while an accepted hold does.

The result emits the canonical key, never its raw spelling, alias source, action,
or any temporary lookup key. Existing entry position is stable under updates.
