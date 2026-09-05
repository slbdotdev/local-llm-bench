"""Transform records according to Release 3.2 specification."""

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


def canonical_source(source):
    """Canonicalize source: strip spaces, lookup alias."""
    name = source.strip(" ")
    return SOURCE_ALIASES.get(name, name)


def canonical_key(source, key):
    """Canonicalize key: strip spaces, casefold, apply aliases."""
    value = key.strip(" ").casefold()
    value = GLOBAL_KEY_ALIASES.get(value, value)
    per_source = SOURCE_KEY_ALIASES.get(source, {})
    return per_source.get(value, value)


def canonical_label(label):
    """Canonicalize label: strip spaces, casefold."""
    return label.strip(" ").casefold()


def contribution(delta, action):
    """Get contribution amount (None if rejected)."""
    multiplier = ACTION_MULTIPLIERS.get(action)
    if multiplier is None:
        return None
    return delta * multiplier


def transform(records):
    """Transform records according to Release 3.2 specification."""
    buckets = []
    bucket_positions = {}
    entry_positions = []

    for record in records:
        source = canonical_source(record["source"])

        # Create or find bucket
        bucket_index = bucket_positions.get(source)
        if bucket_index is None:
            bucket_index = len(buckets)
            bucket_positions[source] = bucket_index
            buckets.append({"source": source, "entries": []})
            entry_positions.append({})

        bucket = buckets[bucket_index]
        positions = entry_positions[bucket_index]

        # Process changes
        for change in record["changes"]:
            amount = contribution(change["delta"], change["action"])
            if amount is None:
                continue

            key = canonical_key(source, change["key"])
            entry_index = positions.get(key)

            if entry_index is None:
                # Create new entry
                labels = []
                for label in change["labels"]:
                    canonical = canonical_label(label)
                    if canonical and canonical not in labels:
                        labels.append(canonical)

                positions[key] = len(bucket["entries"])
                bucket["entries"].append({
                    "key": key,
                    "total": amount,
                    "occurrences": 1,
                    "labels": labels,
                })
            else:
                # Update existing entry
                entry = bucket["entries"][entry_index]
                entry["total"] += amount
                entry["occurrences"] += 1

                # Merge labels
                seen = set(entry["labels"])
                for label in change["labels"]:
                    canonical = canonical_label(label)
                    if canonical and canonical not in seen:
                        entry["labels"].append(canonical)
                        seen.add(canonical)

    return buckets
