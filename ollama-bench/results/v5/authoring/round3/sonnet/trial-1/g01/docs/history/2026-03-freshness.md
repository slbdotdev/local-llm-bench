# 2026-03 ownership review

The adapter's return value is intentionally a plain JSON-like tree. It cannot
share the caller's record dictionaries, change dictionaries, or label lists.
The source and key strings may be immutable values reused by Python, but every
outer list, bucket dictionary, entries list, entry dictionary, and emitted label
list is constructed for the result.

The ownership check uses a deep copy before calling the adapter and then mutates
the returned tree in a separate test. The original records remain equal to the
copy. This is especially important for duplicate keys: updating an output entry
must not update the input change's `delta` or `labels` fields.

No private position map, action, raw key, alias spelling, or policy multiplier
is public output. The field sets are exact even when an entry has an empty label
list or a bucket has no entries.
