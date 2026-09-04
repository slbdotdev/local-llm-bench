def transform(records):
    """Transform records into grouped entries with aggregated deltas.
    
    Process records left to right:
    - Groups appear in first-appearance order
    - For each group/key, sum all deltas and count occurrences
    - First occurrence creates the entry, later ones update in place
    - Empty groups and keys are preserved
    """
    groups_dict = {}  # {group: {"order": int, "entries": {key: {"total": int, "occurrences": int, "order": int}}}}
    group_order = []
    
    for record in records:
        group = record["group"]
        
        # Create group if it doesn't exist
        if group not in groups_dict:
            groups_dict[group] = {
                "order": len(group_order),
                "entries": {}
            }
            group_order.append(group)
        
        # Process entries for this group
        for entry in record["entries"]:
            key = entry["key"]
            delta = entry["delta"]
            
            group_entries = groups_dict[group]["entries"]
            
            if key not in group_entries:
                # First occurrence - create entry with insertion order
                group_entries[key] = {
                    "total": delta,
                    "occurrences": 1,
                    "order": len(group_entries)
                }
            else:
                # Later occurrence - update in place
                group_entries[key]["total"] += delta
                group_entries[key]["occurrences"] += 1
    
    # Build output in group order
    result = []
    for group in group_order:
        group_data = groups_dict[group]
        entries_list = []
        
        # Sort entries by insertion order
        entries_items = sorted(
            group_data["entries"].items(),
            key=lambda x: x[1]["order"]
        )
        
        for key, entry_data in entries_items:
            entries_list.append({
                "key": key,
                "total": entry_data["total"],
                "occurrences": entry_data["occurrences"]
            })
        
        result.append({
            "group": group,
            "entries": entries_list
        })
    
    return result
