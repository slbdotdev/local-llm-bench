"""One-pass key migration for a document with an immutable tail."""

import re

FROZEN = "# FROZEN BELOW"
_PAIR = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_.-]*)(\s*:\s*)(.*)$")

def _mapping(mapping):
    if not hasattr(mapping, "items"):
        raise TypeError("mapping must be a mapping")
    result = {}
    for old, new in mapping.items():
        if not isinstance(old, str) or not isinstance(new, str):
            raise TypeError("keys must be strings")
        if not old or not new:
            raise ValueError("keys must be non-empty")
        result[old] = new
    return result

def _split(text):
    if not isinstance(text, str):
        raise TypeError("document must be a string")
    return text.splitlines(True)

def _frozen_at(lines):
    for index, line in enumerate(lines):
        if line.rstrip("\r\n") == FROZEN:
            return index
    return len(lines)

def _pair(line):
    raw = line.rstrip("\r\n")
    match = _PAIR.match(raw)
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3), match.group(4), line[len(raw):]

def _rewrite_line(line, mapping):
    item = _pair(line)
    if item is None or item[1] not in mapping:
        return line
    before, key, separator, value, ending = item
    return before + mapping[key] + separator + value + ending

def _editable_lines(lines):
    return range(_frozen_at(lines))

def migrate(text, mapping):
    lines, changes = _split(text), _mapping(mapping)
    result = list(lines)
    for index in _editable_lines(lines):
        result[index] = _rewrite_line(lines[index], changes)
    return "".join(result)

def keys(text, include_frozen=True):
    lines = _split(text)
    limit = len(lines) if include_frozen else _frozen_at(lines)
    return [item[1] for item in (_pair(line) for line in lines[:limit]) if item]

def migrate_many(documents, mapping):
    return [migrate(document, mapping) for document in documents]

def migration_count(text, mapping, include_frozen=False):
    changes = _mapping(mapping)
    lines = _split(text)
    limit = len(lines) if include_frozen else _frozen_at(lines)
    return sum(item is not None and item[1] in changes
               for item in (_pair(line) for line in lines[:limit]))

def has_frozen_tail(text):
    lines = _split(text)
    return _frozen_at(lines) < len(lines)

def unchanged_tail(before, after):
    old_lines, new_lines = _split(before), _split(after)
    old_at, new_at = _frozen_at(old_lines), _frozen_at(new_lines)
    return "".join(old_lines[old_at:]) == "".join(new_lines[new_at:])

__all__ = ["FROZEN", "migrate", "keys", "migrate_many", "migration_count", "has_frozen_tail", "unchanged_tail"]
