"""Dated package renames from the release archive."""
from .schema import load_json, require_list, require_string


def load_history(text):
    rows = require_list(load_json(text, "history"), "history")
    result = []
    for row in rows:
        result.append({
            "old": require_string(row.get("old"), "history old name"),
            "new": require_string(row.get("new"), "history new name"),
            "effective": require_string(row.get("effective"), "history date"),
        })
    return result


def canonical(name, release, rows):
    current = name
    visited = set()
    while current not in visited:
        visited.add(current)
        changed = False
        for row in rows:
            if row["old"] == current and release >= row["effective"]:
                current = row["new"]
                changed = True
                break
        if not changed:
            return current
    raise ValueError("cyclic history")
