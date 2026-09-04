"""Ordered group-delta transformation.

See specification.py for the full spec and worked examples.
"""


def transform(records):
    groups = {}
    order = []

    for record in records:
        group = record["group"]
        if group not in groups:
            entries_map = {}
            entry_order = []
            groups[group] = (entries_map, entry_order)
            order.append(group)
        entries_map, entry_order = groups[group]

        for item in record["entries"]:
            key = item["key"]
            delta = item["delta"]
            if key not in entries_map:
                entries_map[key] = {"key": key, "total": delta, "occurrences": 1}
                entry_order.append(key)
            else:
                entry = entries_map[key]
                entry["total"] += delta
                entry["occurrences"] += 1

    result = []
    for group in order:
        entries_map, entry_order = groups[group]
        entries = [dict(entries_map[key]) for key in entry_order]
        result.append({"group": group, "entries": entries})

    return result
