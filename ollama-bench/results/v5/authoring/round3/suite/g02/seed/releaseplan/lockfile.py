"""Pinned dependency snapshot parsing."""
from .schema import load_json, require_list, require_string, unique_names


def load_lock(text):
    rows = require_list(load_json(text, "lockfile"), "lockfile")
    unique_names(rows, "lockfile")
    result = {}
    for row in rows:
        name = require_string(row.get("name"), "lock name")
        deps = row.get("deps", [])
        if not isinstance(deps, list) or any(not isinstance(x, str) for x in deps):
            raise ValueError("bad lock dependencies")
        result[name] = {"name": name, "version": require_string(row.get("version"), "lock version"),
                        "deps": list(deps)}
    return result
