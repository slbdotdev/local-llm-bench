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
    return range(len(lines))

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

def records(text, include_frozen=True):
    """Return parsed key/value records with their original line numbers."""
    lines = _split(text)
    limit = len(lines) if include_frozen else _frozen_at(lines)
    result = []
    for number, line in enumerate(lines[:limit], 1):
        item = _pair(line)
        if item is not None:
            result.append({"key": item[1], "value": item[3], "line": number})
    return result

def editable_records(text):
    return records(text, include_frozen=False)

def frozen_suffix(text):
    """Return the marker and immutable suffix exactly as supplied."""
    lines = _split(text)
    return "".join(lines[_frozen_at(lines):])

def validate_mapping(mapping):
    """Return a copy of a valid migration mapping."""
    return dict(_mapping(mapping))

def migration_plan(text, mapping):
    """Describe editable key changes without changing the document."""
    changes = _mapping(mapping)
    return [(item["line"], item["key"], changes[item["key"]])
            for item in editable_records(text) if item["key"] in changes]

def rename_keys(text, mapping):
    """Alias for migrate retained for callers using the older API name."""
    return migrate(text, mapping)

def migrate_if_needed(text, mapping):
    output = migrate(text, mapping)
    return (output != text, output)

def has_key(text, key, include_frozen=False):
    return any(item["key"] == key for item in records(text, include_frozen))

def is_valid_document(text):
    """Check that every non-comment, non-blank line is a key/value pair."""
    for line in _split(text):
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        if _pair(line) is None:
            return False
    return True

__all__ += ["records", "editable_records", "frozen_suffix",
            "validate_mapping", "migration_plan", "rename_keys",
            "migrate_if_needed", "has_key", "is_valid_document"]


def is_frozen_line(line):
    return isinstance(line, str) and line.rstrip("\r\n") == FROZEN


def split_editable_tail(text):
    """Return (editable prefix, immutable suffix), retaining all newlines."""
    lines = _split(text)
    at = _frozen_at(lines)
    return "".join(lines[:at]), "".join(lines[at:])


def key_counts(text, include_frozen=True):
    counts = {}
    for item in records(text, include_frozen):
        counts[item["key"]] = counts.get(item["key"], 0) + 1
    return counts


def affected_lines(text, mapping):
    return [item["line"] for item in migration_plan(text, mapping)]


def select_keys(text, names, include_frozen=False):
    wanted = set(names)
    return [item for item in records(text, include_frozen) if item["key"] in wanted]


def normalized_mapping(mapping):
    """Return mapping data in insertion order after validation."""
    return list(_mapping(mapping).items())


def migration_summary(text, mapping):
    plan = migration_plan(text, mapping)
    return {"changes": len(plan), "lines": [entry[0] for entry in plan],
            "has_tail": has_frozen_tail(text)}


def same_editable_prefix(before, after):
    old, new = split_editable_tail(before), split_editable_tail(after)
    return old[0] == new[0]


__all__ += ["is_frozen_line", "split_editable_tail", "key_counts",
            "affected_lines", "select_keys", "normalized_mapping",
            "migration_summary", "same_editable_prefix"]
