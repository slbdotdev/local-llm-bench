def transform(records):
    groups_order = []  # maintain group insertion order
    groups_entries = {}  # group_name -> list of entries
    key_positions = {}  # (group_name, key) -> index in entries list
    
    for record in records:
        group_name = record['group']
        
        # If this is the first time we see this group, create it
        if group_name not in groups_entries:
            groups_order.append(group_name)
            groups_entries[group_name] = []
        
        # Process each entry in this record
        for entry in record['entries']:
            key = entry['key']
            delta = entry['delta']
            
            key_lookup = (group_name, key)
            
            if key_lookup not in key_positions:
                # First occurrence of this key in this group
                new_entry = {'key': key, 'total': delta, 'occurrences': 1}
                key_positions[key_lookup] = len(groups_entries[group_name])
                groups_entries[group_name].append(new_entry)
            else:
                # Update existing entry
                idx = key_positions[key_lookup]
                groups_entries[group_name][idx]['total'] += delta
                groups_entries[group_name][idx]['occurrences'] += 1
    
    # Build result
    result = []
    for group_name in groups_order:
        result.append({'group': group_name, 'entries': groups_entries[group_name]})
    
    return result
