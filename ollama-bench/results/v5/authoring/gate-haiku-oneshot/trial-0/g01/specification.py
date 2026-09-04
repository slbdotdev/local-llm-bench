"""Specification for the ordered group-delta transformation.

The implementation target is ``transform(records)``.

Input schema
------------
``records`` is a list.  Each record is a dictionary with a string ``group``
and an ``entries`` list.  Each item in ``entries`` is a dictionary with a
string ``key`` and an integer ``delta``.  Empty strings are valid group and
key values.  Inputs supplied to the function follow this schema.

Output schema and algorithm
---------------------------
Return a new list of group dictionaries.  Process records from left to right.

* A group is created at the first record having that group string, even when
  that record's ``entries`` list is empty.  Group dictionaries appear in first
  appearance order.
* For each entry, find its group and key.  The first occurrence of a key in a
  group creates one output entry at that position.  Later occurrences of the
  same key update that entry in place; they do not move it and do not create a
  second entry.
* An output entry has ``key``, ``total``, and ``occurrences`` fields.  ``total``
  is the sum of all deltas for that group/key, and ``occurrences`` is the
  number of entries for that group/key.  A delta of zero still counts.
* No group or key is sorted, discarded, or deduplicated by value.  In
  particular, empty groups, empty keys, repeated deltas, negative deltas, and
  zero deltas are retained according to the rules above.
* The input is not mutated.  The returned dictionaries and lists are fresh.

Worked examples
---------------
"""

EXAMPLES = [
    (
        [],
        [],
    ),
    (
        [{"group": "b", "entries": [{"key": "x", "delta": 4}]}],
        [{"group": "b", "entries": [{"key": "x", "total": 4, "occurrences": 1}]}],
    ),
    (
        [
            {"group": "z", "entries": [{"key": "a", "delta": 2}, {"key": "a", "delta": -2}]},
            {"group": "a", "entries": []},
            {"group": "z", "entries": [{"key": "b", "delta": 0}, {"key": "a", "delta": 5}]},
        ],
        [
            {"group": "z", "entries": [
                {"key": "a", "total": 5, "occurrences": 3},
                {"key": "b", "total": 0, "occurrences": 1},
            ]},
            {"group": "a", "entries": []},
        ],
    ),
    (
        [
            {"group": "", "entries": [{"key": "", "delta": 0}, {"key": "", "delta": 7}]},
            {"group": "", "entries": []},
        ],
        [{"group": "", "entries": [{"key": "", "total": 7, "occurrences": 2}]}],
    ),
]
