# Final implementation checklist

Before comparing a result, walk the input once from left to right. For each
record ask whether its source, after literal ASCII-space edge removal and exact
alias lookup, has already established a bucket. If not, allocate the bucket
and its independent entry position map now. Do this even when the record has no
changes or every action is administrative.

For each change, consult the closed action table. Ignore and void stop there.
Add, remove, adjust, and hold continue. Multiply the signed delta by 1, -1, 1,
or 0. Normalize the key only now: ASCII edge spaces, casefold, one global
alias, one alias for the canonical source. Use that result in the source-local
position map. New identity means a fresh entry and occurrence one; existing
identity means add amount and one occurrence without moving.

Scan labels only on this accepted path. Remove ASCII edge spaces, casefold,
discard empty values, and append unseen canonical values to the output-owned
list in input order. A set may answer unseen, but never supplies output order.

At return, inspect the public tree: bucket fields are source and entries;
entry fields are key, total, occurrences, labels. Empty values stay present.
No raw input object or private state is reused. The original input must compare
equal to its deep copy. These checks are sufficient for every current fixture;
they do not add behavior for malformed input.

The checklist is intentionally procedural because the five operations feed one
another. A solver that gets each rule right but changes their order can still
produce a fluent, plausible ledger with incorrect identity, counts, labels, or
positions. That is the intended serial difficulty of the candidate.
