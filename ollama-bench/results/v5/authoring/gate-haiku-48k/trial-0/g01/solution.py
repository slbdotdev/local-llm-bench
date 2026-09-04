def transform(records):
    """Transform records into grouped entries with accumulated deltas and occurrence counts.

    Process records left to right. Groups are created in first-appearance order.
    For each entry, the first occurrence of a key in a group creates an output entry.
    Later occurrences update that entry in place (accumulating total delta and
    incrementing occurrence count).

    Returns a new list of group dictionaries without mutating the input.
    """
    groups = {}  # group_name -> {"group": group_name, "entries": [...], "_key_to_index": {...}}
    group_order = []  # track order of first appearance

    for record in records:
        group_name = record["group"]

        # Create group if it doesn't exist (even if entries is empty)
        if group_name not in groups:
            groups[group_name] = {
                "group": group_name,
                "entries": [],
                "_key_to_index": {}
            }
            group_order.append(group_name)

        # Process each entry in the record
        for entry in record["entries"]:
            key = entry["key"]
            delta = entry["delta"]

            group_data = groups[group_name]

            if key not in group_data["_key_to_index"]:
                # First occurrence of this key in this group - create new entry
                new_entry = {
                    "key": key,
                    "total": delta,
                    "occurrences": 1
                }
                group_data["entries"].append(new_entry)
                group_data["_key_to_index"][key] = len(group_data["entries"]) - 1
            else:
                # Subsequent occurrence - update existing entry in place
                idx = group_data["_key_to_index"][key]
                group_data["entries"][idx]["total"] += delta
                group_data["entries"][idx]["occurrences"] += 1

    # Build output, removing the _key_to_index helper
    result = []
    for group_name in group_order:
        group_data = groups[group_name]
        result.append({
            "group": group_data["group"],
            "entries": group_data["entries"]
        })

    return result
