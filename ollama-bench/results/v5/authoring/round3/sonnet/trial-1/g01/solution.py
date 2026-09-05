"""Relay Ledger 3.2 record-to-ledger adapter.

Reconciled from the current release contract (docs/current-contract.md,
docs/README.md), the release configuration (config/*.json), and the
explanatory reducer (relay/reducer.py and friends). See those sources for
rationale; this module only implements the current (3.2) behavior.
"""

SOURCE_ALIASES = {
    "core": "platform",
    "svc": "service",
    "web": "frontend",
    "ui": "frontend",
    "jobs": "worker",
    "batch": "worker",
}

GLOBAL_KEY_ALIASES = {
    "err": "error",
    "warn": "warning",
    "lat": "latency",
    "dur": "duration",
    "cfg": "config",
}

SOURCE_KEY_ALIASES = {
    "platform": {"compile": "build", "compilation": "build"},
    "service": {"request": "requests", "req": "requests"},
    "frontend": {"paint": "render", "draw": "render"},
    "worker": {"job": "jobs", "task": "jobs"},
}

ACTION_MULTIPLIERS = {
    "add": 1,
    "remove": -1,
    "adjust": 1,
    "hold": 0,
}


def _canonical_source(source):
    # Only the ASCII space (chr(32)) is edge presentation noise; a tab is
    # data, so str.strip() (which also strips tabs) must not be used here.
    name = source.strip(" ")
    return SOURCE_ALIASES.get(name, name)


def _canonical_key(source, key):
    value = key.strip(" ").casefold()
    value = GLOBAL_KEY_ALIASES.get(value, value)
    per_source = SOURCE_KEY_ALIASES.get(source, {})
    return per_source.get(value, value)


def _canonical_label(label):
    return label.strip(" ").casefold()


def _contribution(delta, action):
    multiplier = ACTION_MULTIPLIERS.get(action)
    if multiplier is None:
        return None
    return delta * multiplier


def _append_new_labels(existing, seen, labels):
    for raw in labels:
        value = _canonical_label(raw)
        if value and value not in seen:
            existing.append(value)
            seen.add(value)


def transform(records):
    buckets = []
    bucket_index_by_source = {}
    # Per-bucket: canonical key -> entry index, and canonical key -> set of
    # labels already present (for O(1) membership without depending on
    # iteration order of a set for the result itself).
    entry_index_by_source = {}
    label_seen_by_entry = {}

    for record in records:
        source = _canonical_source(record["source"])
        bucket_idx = bucket_index_by_source.get(source)
        if bucket_idx is None:
            bucket_idx = len(buckets)
            bucket_index_by_source[source] = bucket_idx
            buckets.append({"source": source, "entries": []})
            entry_index_by_source[source] = {}

        bucket = buckets[bucket_idx]
        positions = entry_index_by_source[source]

        for change in record["changes"]:
            amount = _contribution(change["delta"], change["action"])
            if amount is None:
                continue

            key = _canonical_key(source, change["key"])
            entry_idx = positions.get(key)
            if entry_idx is None:
                labels = []
                seen = set()
                _append_new_labels(labels, seen, change["labels"])
                entry = {
                    "key": key,
                    "total": amount,
                    "occurrences": 1,
                    "labels": labels,
                }
                positions[key] = len(bucket["entries"])
                label_seen_by_entry[(source, key)] = seen
                bucket["entries"].append(entry)
            else:
                entry = bucket["entries"][entry_idx]
                entry["total"] += amount
                entry["occurrences"] += 1
                seen = label_seen_by_entry[(source, key)]
                _append_new_labels(entry["labels"], seen, change["labels"])

    return buckets
