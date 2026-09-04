def transform(records):
    groups_by_name = {}
    order = []

    for record in records:
        group = record["group"]
        if group not in groups_by_name:
            g = {"group": group, "entries": [], "_keys": {}}
            groups_by_name[group] = g
            order.append(g)
        g = groups_by_name[group]
        for entry in record.get("entries", []):
            key = entry["key"]
            delta = entry["delta"]
            keys = g["_keys"]
            if key not in keys:
                new_entry = {"key": key, "total": delta, "occurrences": 1}
                keys[key] = new_entry
                g["entries"].append(new_entry)
            else:
                existing = keys[key]
                existing["total"] += delta
                existing["occurrences"] += 1

    result = []
    for g in order:
        result.append({
            "group": g["group"],
            "entries": [dict(e) for e in g["entries"]],
        })
    return result
