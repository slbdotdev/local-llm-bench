# Source lifecycle cases

Outer state is established one record at a time. Canonicalize the record source
and ensure its bucket before looking at the changes list. This is true for an
empty list, a list containing only ignore/void, and a list containing a hold.

Raw sources `core`, ` platform `, and `core` establish one platform bucket at
the position of the first of those records. Raw sources `svc`, `service`, and
` svc ` establish one service bucket at the position of the first. A second
record for an existing canonical source cannot move it or reset its entry
position map.

The outer result order follows first canonical source appearance. It does not
follow raw spelling order, canonical lexical order, first nonempty bucket order,
or first accepted entry order. A source can be first because of a rejected-only
record and still precede a source whose first record has an accepted change.

A record with no changes cannot be represented by omitting it: omission makes a
reported empty source indistinguishable from an absent source. Conversely, a
change with a rejected action cannot be represented by an empty entry because
that would invent a key. These two lifecycle levels must remain separate.

The source string in output is the canonical source. Empty canonical source is
valid and can be a bucket. The bucket dictionary has exactly source and entries,
with entries as a fresh list.
