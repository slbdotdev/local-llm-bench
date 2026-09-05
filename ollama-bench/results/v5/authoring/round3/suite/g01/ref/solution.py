"""Reference implementation for Relay Ledger 3.2."""


_SOURCES = {
    "core": "platform", "svc": "service", "web": "frontend",
    "ui": "frontend", "jobs": "worker", "batch": "worker",
}
_GLOBALS = {
    "err": "error", "warn": "warning", "lat": "latency",
    "dur": "duration", "cfg": "config",
}
_LOCAL = {
    "platform": {"compile": "build", "compilation": "build"},
    "service": {"request": "requests", "req": "requests"},
    "frontend": {"paint": "render", "draw": "render"},
    "worker": {"job": "jobs", "task": "jobs"},
}
_MULTIPLIERS = {"add": 1, "remove": -1, "adjust": 1, "hold": 0}


def transform(records):
    buckets = []
    source_positions = {}
    entry_positions = []
    for record in records:
        raw_source = record["source"].strip(" ")
        source = _SOURCES.get(raw_source, raw_source)
        if source not in source_positions:
            source_positions[source] = len(buckets)
            buckets.append({"source": source, "entries": []})
            entry_positions.append({})
        bucket_index = source_positions[source]
        bucket = buckets[bucket_index]
        positions = entry_positions[bucket_index]
        for change in record["changes"]:
            action = change["action"]
            if action not in _MULTIPLIERS:
                continue
            key = change["key"].strip(" ").casefold()
            key = _GLOBALS.get(key, key)
            key = _LOCAL.get(source, {}).get(key, key)
            amount = change["delta"] * _MULTIPLIERS[action]
            if key not in positions:
                positions[key] = len(bucket["entries"])
                labels = []
                seen = set()
                for raw_label in change["labels"]:
                    label = raw_label.strip(" ").casefold()
                    if label and label not in seen:
                        seen.add(label)
                        labels.append(label)
                bucket["entries"].append({
                    "key": key, "total": amount, "occurrences": 1,
                    "labels": labels,
                })
            else:
                entry = bucket["entries"][positions[key]]
                entry["total"] += amount
                entry["occurrences"] += 1
                seen = set(entry["labels"])
                for raw_label in change["labels"]:
                    label = raw_label.strip(" ").casefold()
                    if label and label not in seen:
                        seen.add(label)
                        entry["labels"].append(label)
    return buckets
