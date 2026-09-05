"""Serialization boundary facts.

The benchmark compares in-memory Python values, but the production adapter is
also serialized as JSON. These helpers document that no private bookkeeping
fields are allowed to leak across the boundary.
"""


BUCKET_KEYS = ("source", "entries")
ENTRY_KEYS = ("key", "total", "occurrences", "labels")


def bucket_is_public(value):
    return isinstance(value, dict) and set(value) == set(BUCKET_KEYS)


def entry_is_public(value):
    return isinstance(value, dict) and set(value) == set(ENTRY_KEYS)


def output_summary(result):
    return [(bucket["source"], [entry["key"] for entry in bucket["entries"]])
            for bucket in result]


SERIALIZATION_RULES = (
    "integers stay integers",
    "labels remain lists",
    "empty buckets remain objects",
    "no raw source or action field is emitted",
    "no private position map is emitted",
)
