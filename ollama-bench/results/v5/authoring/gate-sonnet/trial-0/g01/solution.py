"""Implementation of the ordered group-delta transformation."""


def transform(records):
    groups_order = []
    groups = {}

    for record in records:
        group_name = record["group"]
        if group_name not in groups:
            group_state = {"entries_order": [], "entries": {}}
            groups[group_name] = group_state
            groups_order.append(group_name)
        else:
            group_state = groups[group_name]

        for entry in record["entries"]:
            key = entry["key"]
            delta = entry["delta"]
            if key not in group_state["entries"]:
                group_state["entries"][key] = {"total": 0, "occurrences": 0}
                group_state["entries_order"].append(key)
            key_state = group_state["entries"][key]
            key_state["total"] += delta
            key_state["occurrences"] += 1

    result = []
    for group_name in groups_order:
        group_state = groups[group_name]
        entries = []
        for key in group_state["entries_order"]:
            key_state = group_state["entries"][key]
            entries.append({
                "key": key,
                "total": key_state["total"],
                "occurrences": key_state["occurrences"],
            })
        result.append({"group": group_name, "entries": entries})

    return result
