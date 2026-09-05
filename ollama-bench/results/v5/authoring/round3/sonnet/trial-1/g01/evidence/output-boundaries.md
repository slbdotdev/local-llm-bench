# Output boundary cases

Every bucket has exactly two fields: source and entries. Every entry has exactly
four: key, total, occurrences, and labels. Empty lists are values, not signals
to remove a field. Dictionary insertion order is not used as a substitute for
the semantic ordering rules, although the reference emits fields in documented
order.

Outer buckets are in first canonical-source order. Inner entries are in first
accepted-canonical-key order. Labels are in first canonical-label order. Later
duplicates update totals, occurrences, and labels without moving any object.

The return tree is fresh. An input record dictionary, changes list, change
dictionary, or labels list cannot be returned as any public object. Repeated
calls with one input produce equal but independent results. Mutating the result
after return cannot alter the input or a result from another call.

Integer totals and occurrence counts remain integers. A total of zero and a
label list of zero length do not change the shape. A source with no entries is
still a bucket. An entry with zero total and zero labels is still an entry if it
has an accepted occurrence.

No implementation state is public. Position maps, raw fields, action names,
multipliers, page numbers, source aliases, and rejected labels must not appear.
The benchmark compares Python structures directly, so serialization is not a
license to change types or ordering.
