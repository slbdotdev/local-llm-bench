"""Small, conservative rewriter for sectioned deployment manifests."""

import re

_SECTION = re.compile(r"^\s*\[([^\]]+)\]\s*$")
_ASSIGN = re.compile(r"^(\s*)([^=:#]+?)(\s*=\s*)(.*)$")

def _name(value):
    return value.strip()

def _same_name(left, right):
    return _name(left) == _name(right)

def _section(line):
    match = _SECTION.match(line)
    return match.group(1).strip() if match else None

def _assignment(line):
    match = _ASSIGN.match(line)
    if not match:
        return None
    key = match.group(2).strip()
    return (match.group(1), key, match.group(3), match.group(4)) if key else None

def _split_lines(text):
    return text.splitlines(), text.endswith("\n")

def _join_lines(lines, trailing):
    return "\n".join(lines) + ("\n" if trailing else "")

def _valid_update_key(key):
    return (isinstance(key, tuple) and len(key) == 2 and
            all(isinstance(part, str) for part in key))

def _prepare_updates(updates):
    if updates is None:
        return {}
    if not hasattr(updates, "items"):
        raise TypeError("updates must be a mapping")
    answer = {}
    for pair, value in updates.items():
        if not _valid_update_key(pair):
            raise ValueError("update keys are (section, key) pairs")
        answer[(_name(pair[0]), _name(pair[1]))] = str(value)
    return answer

def _find_update(prepared, section, key):
    for (wanted_section, wanted_key), value in prepared.items():
        if _same_name(section or "", wanted_section) and _same_name(key, wanted_key):
            return value
    return None

def _section_end(lines, start):
    for index in range(start + 1, len(lines)):
        if _section(lines[index]) is not None:
            return index
    return len(lines)

def _existing_sections(lines):
    answer = []
    for index, line in enumerate(lines):
        section = _section(line)
        if section is not None:
            answer.append((index, section))
    return answer

def _insert_missing(lines, prepared, used):
    for pair, value in prepared.items():
        if pair in used:
            continue
        section_name, key = pair
        matching = next(((i, s) for i, s in _existing_sections(lines)
                         if _same_name(s, section_name)), None)
        if matching is None:
            if lines and lines[-1] != "":
                lines.append("")
            lines.extend(["[" + section_name + "]", key + "=" + value])
            used.add(pair)
            continue
        end = _section_end(lines, matching[0])
        insert_at = end
        while insert_at > matching[0] + 1 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
        lines.insert(insert_at, key + "=" + value)
        used.add(pair)

def rewrite(text, updates=None):
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    prepared = _prepare_updates(updates)
    lines, trailing = _split_lines(text)
    output, current, used = [], None, set()
    for line in lines:
        found = _section(line)
        if found is not None:
            current = found
            output.append(line)
            continue
        item = _assignment(line)
        if item is None or line.lstrip().startswith("#"):
            output.append(line)
            continue
        before, key, separator, old_value = item
        value = _find_update(prepared, current, key)
        if value is None:
            output.append(line)
        else:
            output.append(before + key + separator + value)
            used.update(pair for pair in prepared
                        if _same_name(pair[0], current or "") and _same_name(pair[1], key))
    _insert_missing(output, prepared, used)
    return _join_lines(output, trailing)

def sections(text):
    answer, seen = [], set()
    for line in text.splitlines():
        section = _section(line)
        if section is not None and section.casefold() not in seen:
            answer.append(section)
            seen.add(section.casefold())
    return answer

def values(text, section_name):
    answer, current = {}, None
    for line in text.splitlines():
        found = _section(line)
        if found is not None:
            current = found
            continue
        item = _assignment(line)
        if item and _same_name(current or "", section_name):
            answer[item[1]] = item[3]
    return answer

def remove_keys(text, removals):
    targets = {(_name(a).casefold(), _name(b).casefold()) for a, b in removals}
    lines, trailing = _split_lines(text)
    result, current = [], None
    for line in lines:
        found = _section(line)
        if found is not None:
            current = found
            result.append(line)
            continue
        item = _assignment(line)
        if item and ((current or "").casefold(), item[1].casefold()) in targets:
            continue
        result.append(line)
    return _join_lines(result, trailing)

def overlay(texts, updates):
    return [rewrite(text, updates) for text in texts]

__all__ = ["rewrite", "sections", "values", "remove_keys", "overlay"]


def parse_records(text):
    """Return assignment records with their section and source position."""
    result = []
    current = None
    for number, line in enumerate(text.splitlines(), 1):
        found = _section(line)
        if found is not None:
            current = found
            continue
        item = _assignment(line)
        if item is not None and not line.lstrip().startswith("#"):
            result.append({"section": current, "key": item[1],
                           "value": item[3], "line": number})
    return result


def find_records(text, section_name=None, key_name=None):
    """Find records matching optional case-insensitive section and key."""
    answer = []
    for record in parse_records(text):
        if (section_name is not None and
                not _same_name(record["section"] or "", section_name)):
            continue
        if key_name is not None and not _same_name(record["key"], key_name):
            continue
        answer.append(record)
    return answer


def validate(text):
    """Return a list of human-readable structural errors."""
    errors = []
    current = None
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("#") or not line.strip():
            continue
        found = _section(line)
        if found is not None:
            current = found
            if not found:
                errors.append("line %d: empty section" % number)
            continue
        if _assignment(line) is None:
            errors.append("line %d: expected assignment in %s" %
                          (number, current or "root"))
    return errors


def update_keys(text, updates):
    """Named alias for rewrite, useful to callers that prefer verb semantics."""
    return rewrite(text, updates)


def has_section(text, section_name):
    return any(_same_name(name, section_name) for name in sections(text))


def copy_with_update(text, section, key, value):
    """Convenience wrapper for changing one section/key pair."""
    return rewrite(text, {(section, key): value})


__all__ += ["parse_records", "find_records", "validate", "update_keys",
            "has_section", "copy_with_update"]
