def transform(records):
    """Transform relay ledger records to the current release format (3.2)."""

    # Configuration data
    source_aliases_map = {
        "core": "platform",
        "svc": "service",
        "web": "frontend",
        "ui": "frontend",
        "jobs": "worker",
        "batch": "worker"
    }

    global_key_aliases = {
        "err": "error",
        "warn": "warning",
        "lat": "latency",
        "dur": "duration",
        "cfg": "config"
    }

    source_key_aliases = {
        "platform": {
            "compile": "build",
            "compilation": "build"
        },
        "service": {
            "request": "requests",
            "req": "requests"
        },
        "frontend": {
            "paint": "render",
            "draw": "render"
        },
        "worker": {
            "job": "jobs",
            "task": "jobs"
        }
    }

    action_policy = {
        "add": 1,
        "remove": -1,
        "adjust": 1,
        "hold": 0
    }

    # Helper functions
    def canonicalize_source(source):
        """Canonicalize source by removing ASCII spaces and applying aliases."""
        # Remove ASCII spaces at both ends (not tabs)
        stripped = source.strip(" ")
        # Look up in aliases; unknown names are retained
        return source_aliases_map.get(stripped, stripped)

    def canonicalize_key(key, canonical_source):
        """Canonicalize key using global then source-specific aliases."""
        # Remove ASCII spaces at both ends
        stripped = key.strip(" ")
        # Case-fold
        casefolded = stripped.casefold()
        # Apply global alias once
        after_global = global_key_aliases.get(casefolded, casefolded)
        # Apply source-specific alias once
        if canonical_source in source_key_aliases:
            after_source = source_key_aliases[canonical_source].get(after_global, after_global)
        else:
            after_source = after_global
        return after_source

    def canonicalize_label(label):
        """Canonicalize label; return None if empty after processing."""
        # Remove ASCII spaces at both ends
        stripped = label.strip(" ")
        # Case-fold
        casefolded = stripped.casefold()
        # Discard if empty
        return casefolded if casefolded else None

    # Process records into buckets
    source_buckets = {}  # canonical_source -> {"entries": {}, "entry_order": []}
    source_order = []  # Order of first appearance of each canonical source

    for record in records:
        canonical_source = canonicalize_source(record["source"])

        # Create source bucket before iterating changes
        if canonical_source not in source_buckets:
            source_buckets[canonical_source] = {
                "entries": {},
                "entry_order": []
            }
            source_order.append(canonical_source)

        bucket = source_buckets[canonical_source]

        # Process changes for this record
        for change in record["changes"]:
            action = change["action"]

            # Reject ignored and void actions before key/label work
            if action not in action_policy:
                continue

            # Canonicalize key using source as local alias-table selector
            canonical_key = canonicalize_key(change["key"], canonical_source)

            # Calculate contribution using signed integer multiplication
            delta = change["delta"]
            multiplier = action_policy[action]
            contribution = delta * multiplier

            # Get or create entry, preserving first-seen position
            if canonical_key not in bucket["entries"]:
                bucket["entries"][canonical_key] = {
                    "key": canonical_key,
                    "total": 0,
                    "occurrences": 0,
                    "labels": []
                }
                bucket["entry_order"].append(canonical_key)

            entry = bucket["entries"][canonical_key]

            # Update entry with contribution and count this accepted change
            entry["total"] += contribution
            entry["occurrences"] += 1

            # Process labels: normalize before deduplication, only after acceptance
            seen_labels = set(entry["labels"])
            for label in change["labels"]:
                canonical_label = canonicalize_label(label)
                # Keep first occurrence of each canonical label
                if canonical_label and canonical_label not in seen_labels:
                    entry["labels"].append(canonical_label)
                    seen_labels.add(canonical_label)

    # Build output with fresh containers and exact fields only
    output = []
    for canonical_source in source_order:
        bucket = source_buckets[canonical_source]
        entries = []

        # Preserve entry order (first accepted change position)
        for canonical_key in bucket["entry_order"]:
            entry = bucket["entries"][canonical_key]
            # Create fresh entry with exact fields in order
            entries.append({
                "key": entry["key"],
                "total": entry["total"],
                "occurrences": entry["occurrences"],
                "labels": list(entry["labels"])  # Fresh list
            })

        # Create fresh bucket with exact fields
        output.append({
            "source": canonical_source,
            "entries": entries
        })

    return output
