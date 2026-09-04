def transform(records):
    """Transform records into ordered group-delta summary.

    Process records left-to-right, tracking first appearance of groups and keys.
    For each group/key combination, sum deltas and count occurrences.
    """
    # Track groups in order of first appearance
    groups_order = []
    groups_seen = set()

    # For each group, track entries: key -> {"total": int, "occurrences": int}
    group_entries = {}

    # For each group, track key order (for maintaining entry order)
    group_key_order = {}

    for record in records:
        group = record["group"]

        # Create group if first appearance
        if group not in groups_seen:
            groups_seen.add(group)
            groups_order.append(group)
            group_entries[group] = {}
            group_key_order[group] = []

        # Process each entry in the record
        for entry in record["entries"]:
            key = entry["key"]
            delta = entry["delta"]

            if key not in group_entries[group]:
                # First occurrence of this key in this group
                group_entries[group][key] = {
                    "total": delta,
                    "occurrences": 1
                }
                group_key_order[group].append(key)
            else:
                # Update existing entry in place
                group_entries[group][key]["total"] += delta
                group_entries[group][key]["occurrences"] += 1

    # Build output in order
    result = []
    for group in groups_order:
        entries_list = []
        for key in group_key_order[group]:
            entry_info = group_entries[group][key]
            entries_list.append({
                "key": key,
                "total": entry_info["total"],
                "occurrences": entry_info["occurrences"]
            })
        result.append({
            "group": group,
            "entries": entries_list
        })

    return result
