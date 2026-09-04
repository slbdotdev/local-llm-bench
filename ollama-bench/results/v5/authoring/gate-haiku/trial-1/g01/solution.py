def transform(records):
    groups = {}  # {group_name: {"key_data": {}, "key_order": []}}
    group_order = []  # list to maintain group order

    for record in records:
        group_name = record["group"]

        # Create group if it doesn't exist
        if group_name not in groups:
            groups[group_name] = {"key_data": {}, "key_order": []}
            group_order.append(group_name)

        group_info = groups[group_name]

        # Process entries
        for entry in record["entries"]:
            key = entry["key"]
            delta = entry["delta"]

            if key not in group_info["key_data"]:
                # First occurrence: create entry
                group_info["key_data"][key] = {
                    "key": key,
                    "total": delta,
                    "occurrences": 1
                }
                group_info["key_order"].append(key)
            else:
                # Later occurrence: update in place
                group_info["key_data"][key]["total"] += delta
                group_info["key_data"][key]["occurrences"] += 1

    # Build result in group order
    result = []
    for group_name in group_order:
        group_info = groups[group_name]
        entries = [group_info["key_data"][key] for key in group_info["key_order"]]
        result.append({
            "group": group_name,
            "entries": entries
        })

    return result
