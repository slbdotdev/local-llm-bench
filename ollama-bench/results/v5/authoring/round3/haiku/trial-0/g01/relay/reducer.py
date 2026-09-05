"""The ordered fold used by the public adapter.

This module shows the sequencing boundary: source bucket creation happens
before action policy, while key and label accumulation happen only after policy.
It is kept independent of the API wrapper so batch and streaming callers can
share the same conceptual reducer.
"""

from .actions import contribution
from .keys import canonical_key
from .labels import labels_for, merge_labels
from .models import empty_bucket, empty_entry
from .sources import canonical_source


def _new_state():
    return [], {}


def reduce_records(records):
    buckets, bucket_positions = _new_state()
    entry_positions = []

    for record in records:
        source = canonical_source(record["source"])
        bucket_index = bucket_positions.get(source)
        if bucket_index is None:
            bucket_index = len(buckets)
            bucket_positions[source] = bucket_index
            buckets.append(empty_bucket(source))
            entry_positions.append({})

        bucket = buckets[bucket_index]
        positions = entry_positions[bucket_index]
        for change in record["changes"]:
            amount = contribution(change["delta"], change["action"])
            if amount is None:
                continue
            key = canonical_key(source, change["key"])
            entry_index = positions.get(key)
            if entry_index is None:
                positions[key] = len(bucket["entries"])
                bucket["entries"].append(
                    empty_entry(key, amount, labels_for(change))
                )
            else:
                entry = bucket["entries"][entry_index]
                entry["total"] += amount
                entry["occurrences"] += 1
                merge_labels(entry, change)

    return buckets
