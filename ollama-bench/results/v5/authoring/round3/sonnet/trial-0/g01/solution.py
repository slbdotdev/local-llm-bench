"""Relay Ledger 3.2 record-to-ledger adapter.

Self-contained reimplementation of the release 3.2 fold described by the
seed material under this sandbox (docs/current-contract.md, the relay/
package, config/*.json, and the fixture/regression records). Not a runtime
dependency on that seed package.
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


def _canonical_source(raw):
    # Only the ordinary ASCII space is presentation whitespace for sources.
    # A tab is real data and must never be stripped.
    name = raw.strip(" ")
    return SOURCE_ALIASES.get(name, name)


def _canonical_key(source, raw):
    value = raw.strip(" ").casefold()
    value = GLOBAL_KEY_ALIASES.get(value, value)
    return SOURCE_KEY_ALIASES.get(source, {}).get(value, value)


def _canonical_label(raw):
    return raw.strip(" ").casefold()


def _append_new_labels(existing, seen, raw_labels):
    for raw in raw_labels:
        value = _canonical_label(raw)
        if value and value not in seen:
            existing.append(value)
            seen.add(value)


def transform(records):
    """Return the fresh ordered ledger for a batch of valid records."""
    buckets = []
    bucket_positions = {}
    # Per bucket: {canonical_key: index into that bucket's entries list}
    key_positions = []
    # Per bucket: {canonical_key: set of canonical labels already present}
    label_seen = []

    for record in records:
        source = _canonical_source(record["source"])
        bucket_index = bucket_positions.get(source)
        if bucket_index is None:
            bucket_index = len(buckets)
            bucket_positions[source] = bucket_index
            buckets.append({"source": source, "entries": []})
            key_positions.append({})
            label_seen.append({})

        entries = buckets[bucket_index]["entries"]
        positions = key_positions[bucket_index]
        seen_labels = label_seen[bucket_index]

        for change in record["changes"]:
            action = change["action"]
            multiplier = ACTION_MULTIPLIERS.get(action)
            if multiplier is None:
                # ignore / void: no occurrence, amount, key, or labels, but
                # the bucket created above is never undone.
                continue

            amount = change["delta"] * multiplier
            key = _canonical_key(source, change["key"])
            entry_index = positions.get(key)

            if entry_index is None:
                entry_index = len(entries)
                positions[key] = entry_index
                fresh_labels = []
                seen = set()
                _append_new_labels(fresh_labels, seen, change["labels"])
                seen_labels[key] = seen
                entries.append(
                    {
                        "key": key,
                        "total": amount,
                        "occurrences": 1,
                        "labels": fresh_labels,
                    }
                )
            else:
                entry = entries[entry_index]
                entry["total"] += amount
                entry["occurrences"] += 1
                _append_new_labels(
                    entry["labels"], seen_labels[key], change["labels"]
                )

    return buckets
