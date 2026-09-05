# Release 3.2 review checklist

The final review compared four independent views of the adapter: the reducer's
order of operations, the release configuration, the importer callers, and the
regression ledger. The following review questions are recorded because they
catch errors that ordinary examples do not:

Does a canonical alias create its bucket before a rejected change? Does a hold
survive a zero multiplier? Does a signed remove multiply rather than take an
absolute value? Are labels from a rejected change absent even when the same key
later appears? Are source-specific key aliases looked up with the canonical
source? Does the first accepted key stay ahead of a later key after a duplicate
update? Are tabs preserved while ordinary edge spaces disappear? Are all
objects fresh?

The answer to each is yes. The implementation is intentionally a five-stage
sequence: create or find the canonical source bucket; decide action; canonicalize
the surviving key; calculate contribution and occurrence; merge labels and
preserve positions. Changing the order changes observable results.

The review also rejected two attractive “cleanup” proposals. Sorting the result
would make snapshots visually stable but would violate the UI's first-observed
semantics. Filtering empty buckets would reduce output size but would erase the
distinction between a reported empty page and no page. Neither optimization is
part of release 3.2.
