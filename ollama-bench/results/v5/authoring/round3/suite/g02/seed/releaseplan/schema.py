"""Small, strict JSON boundary used by the planner."""
import json


def load_json(text, label):
    if not isinstance(text, str):
        raise TypeError(label + " must be text")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid " + label) from exc


def require_list(value, label):
    if not isinstance(value, list):
        raise ValueError(label + " must be a list")
    return value


def require_string(value, label):
    if not isinstance(value, str) or not value:
        raise ValueError(label + " must be a non-empty string")
    return value


def unique_names(rows, label):
    seen = set()
    for row in rows:
        name = require_string(row.get("name"), label + " name")
        if name in seen:
            raise ValueError("duplicate " + label + " name")
        seen.add(name)
    return seen
