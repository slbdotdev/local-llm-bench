"""Solution for the ordered group-delta transformation."""


def transform(records):
    """Transform records by accumulating deltas per group/key while preserving order.

    Args:
        records: List of dictionaries with 'group' and 'entries' keys.
                 Each entry has 'key' and 'delta'.

    Returns:
        List of group dictionaries with accumulated deltas and occurrence counts.
    """
    # Track groups in order of first appearance
    group_order = []

    # Track entries within each group: group_name -> {key -> {"total", "occurrences", "position"}}
    group_entries = {}

    # Track next position for new entries in each group
    next_position = {}

    for record in records:
        group = record["group"]

        # Create group if not seen before
        if group not in group_entries:
            group_order.append(group)
            group_entries[group] = {}
            next_position[group] = 0

        # Process entries in this record
        for entry in record["entries"]:
            key = entry["key"]
            delta = entry["delta"]

            if key not in group_entries[group]:
                # First occurrence of this key in this group
                group_entries[group][key] = {
                    "total": delta,
                    "occurrences": 1,
                    "position": next_position[group]
                }
                next_position[group] += 1
            else:
                # Later occurrence - update in place
                group_entries[group][key]["total"] += delta
                group_entries[group][key]["occurrences"] += 1

    # Build output preserving order
    result = []
    for group in group_order:
        entries = []
        # Sort by position to maintain order of first appearance
        sorted_entries = sorted(
            group_entries[group].items(),
            key=lambda x: x[1]["position"]
        )
        for key, entry_data in sorted_entries:
            entries.append({
                "key": key,
                "total": entry_data["total"],
                "occurrences": entry_data["occurrences"]
            })
        result.append({
            "group": group,
            "entries": entries
        })

    return result
