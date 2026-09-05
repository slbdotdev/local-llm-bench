# Empty-string review

Empty strings are valid identifiers in the imported schema. A source containing
only edge spaces canonicalizes to the empty source and creates an empty bucket
if it is the first source. A key containing only edge spaces canonicalizes to
the empty key after an accepted action and creates an entry. A label containing
only edge spaces canonicalizes to empty and is discarded.

The three empty cases are intentionally not interchangeable. Empty source is a
bucket identity and remains visible. Empty key is an entry identity and remains
visible. Empty label is metadata and is omitted. A record with source ` ` and a
void empty key still creates the empty-source bucket but no empty-key entry.

An unknown source whose canonical value is empty can coexist only once with
other raw spellings that also canonicalize to empty. It does not alias to a
named source. An empty key in one source is independent of an empty key in
another source. Repeated accepted empty-key changes update the first entry in
place and merge their nonempty labels.

Truthiness tests are especially dangerous here. The source string, key string,
label string, delta, multiplier, and lists all can be empty or zero without
sharing the same policy. The release contract handles each at its own stage.

The output shape never omits `source`, `entries`, `key`, `total`,
`occurrences`, or `labels` merely because their values are empty.
