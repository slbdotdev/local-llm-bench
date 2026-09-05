"""Relay Ledger 3.2 transformation function."""


# Configuration data from the seed directory
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
    """Canonicalize a source name."""
    name = source.strip(" ")
    return SOURCE_ALIASES.get(name, name)


def _canonical_key(source, key):
    """Canonicalize a key for a given source."""
    value = key.strip(" ").casefold()
    value = GLOBAL_KEY_ALIASES.get(value, value)
    per_source = SOURCE_KEY_ALIASES.get(source, {})
    return per_source.get(value, value)


def _canonical_label(label):
    """Canonicalize a label."""
    return label.strip(" ").casefold()


def _contribution(delta, action):
    """Calculate the contribution of a change, or None if rejected."""
    multiplier = ACTION_MULTIPLIERS.get(action)
    if multiplier is None:
        return None
    return delta * multiplier


def _append_new_labels(existing, labels):
    """Append canonical nonempty labels not seen in this entry so far."""
    seen = set(existing)
    for label in labels:
        value = _canonical_label(label)
        if value and value not in seen:
            existing.append(value)
            seen.add(value)


def transform(records):
    """Transform a list of records into buckets with entries.
    
    This implements the Relay Ledger 3.2 adapter, which:
    - Groups changes by canonical source
    - Applies action policy to accept/reject changes
    - Canonicalizes keys and labels
    - Accumulates totals and occurrence counts
    - Preserves order by first appearance
    """
    buckets = []
    bucket_positions = {}
    entry_positions = []
    
    for record in records:
        source = _canonical_source(record["source"])
        
        # Create bucket if it doesn't exist
        bucket_index = bucket_positions.get(source)
        if bucket_index is None:
            bucket_index = len(buckets)
            bucket_positions[source] = bucket_index
            buckets.append({"source": source, "entries": []})
            entry_positions.append({})
        
        bucket = buckets[bucket_index]
        positions = entry_positions[bucket_index]
        
        # Process each change
        for change in record["changes"]:
            amount = _contribution(change["delta"], change["action"])
            if amount is None:
                # Action rejected, skip this change
                continue
            
            key = _canonical_key(source, change["key"])
            entry_index = positions.get(key)
            
            if entry_index is None:
                # First occurrence of this key
                labels = []
                _append_new_labels(labels, change["labels"])
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
                _append_new_labels(entry["labels"], change["labels"])
    
    return buckets
