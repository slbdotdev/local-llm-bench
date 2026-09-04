def transform(records):
    """Transform records into grouped entries with aggregated deltas."""
    groups = {}
    group_order = []
    
    for record in records:
        group = record["group"]
        
        # Create group if not exists
        if group not in groups:
            groups[group] = {}
            group_order.append(group)
        
        # Process entries
        for entry in record["entries"]:
            key = entry["key"]
            delta = entry["delta"]
            
            # Create or update entry
            if key not in groups[group]:
                groups[group][key] = {"total": delta, "occurrences": 1}
            else:
                groups[group][key]["total"] += delta
                groups[group][key]["occurrences"] += 1
    
    # Build output
    result = []
    for group in group_order:
        entries = []
        for key in groups[group]:
            entries.append({
                "key": key,
                "total": groups[group][key]["total"],
                "occurrences": groups[group][key]["occurrences"]
            })
        result.append({
            "group": group,
            "entries": entries
        })
    
    return result
