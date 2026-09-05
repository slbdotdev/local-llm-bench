# Normalization matrix with field-specific behavior

The three string fields are reviewed side by side because a generic helper is
an attractive source of bugs. For source, remove only ASCII spaces and perform
exact one-step alias lookup without casefold. For key, remove only ASCII
spaces, casefold, then apply one global and one canonical-source-local alias.
For label, remove only ASCII spaces and casefold, then discard an empty result;
there is no alias lookup.

The raw value ` ERR ` becomes source `ERR` if used as a source, key `error` if
used as a key, and label `err` if used as a label. The raw value `\tERR` remains
tab-prefixed in all three field-specific paths because tab is not an edge
space; the key and label still casefold their non-tab characters. The raw value
` ` becomes source empty, key empty, and an omitted label.

Aliases are not applied to labels. A label `err` remains `err`, not `error`.
Aliases are not applied before source canonicalization selects a local key
table. Alias targets are not looked up again. Unknown normalized values remain
valid identities.

The matrix is especially relevant to a source record whose source is ` core `
and whose accepted key is ` compile `. The outer name becomes platform, and
the inner name becomes build only after the policy gate. A rejected compile
must not reserve build or contribute its labels.

The emitted strings are canonical values. Raw source, key, and label spellings
are never copied to output except when normalization leaves them unchanged.
