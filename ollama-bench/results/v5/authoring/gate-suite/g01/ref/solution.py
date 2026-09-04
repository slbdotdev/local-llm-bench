"""Reference implementation for the candidate transformation."""


def transform(records):
    """Aggregate entries by first-seen group and key, without reordering."""
    groups = []
    group_positions = {}

    for record in records:
        group_name = record["group"]
        group_index = group_positions.get(group_name)
        if group_index is None:
            group_index = len(groups)
            group_positions[group_name] = group_index
            groups.append({"group": group_name, "entries": []})

        output_entries = groups[group_index]["entries"]
        key_positions = {}
        for index, output_entry in enumerate(output_entries):
            key_positions[output_entry["key"]] = index

        for entry in record["entries"]:
            key = entry["key"]
            entry_index = key_positions.get(key)
            if entry_index is None:
                key_positions[key] = len(output_entries)
                output_entries.append({
                    "key": key,
                    "total": entry["delta"],
                    "occurrences": 1,
                })
            else:
                output_entry = output_entries[entry_index]
                output_entry["total"] += entry["delta"]
                output_entry["occurrences"] += 1

    return groups
