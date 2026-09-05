"""Catalog loading and package metadata normalization."""
from .schema import load_json, require_list, require_string, unique_names


def load_catalog(text):
    rows = require_list(load_json(text, "catalog"), "catalog")
    unique_names(rows, "catalog")
    result = {}
    for row in rows:
        name = require_string(row.get("name"), "package name")
        deps = row.get("deps", [])
        platforms = row.get("platforms", ["*"])
        if not isinstance(deps, list) or any(not isinstance(x, str) or not x for x in deps):
            raise ValueError("bad dependencies")
        if not isinstance(platforms, list) or any(not isinstance(x, str) for x in platforms):
            raise ValueError("bad platforms")
        result[name] = {
            "name": name,
            "version": require_string(row.get("version"), "package version"),
            "deps": list(deps),
            "platforms": list(platforms),
            "priority": int(row.get("priority", 100)),
        }
    return result


def available(record, platform):
    platforms = record["platforms"]
    return "*" in platforms or platform in platforms
