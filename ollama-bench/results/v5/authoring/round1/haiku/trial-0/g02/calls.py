"""Token-preserving renaming of exact Python call targets."""

import io
import tokenize


def _tokens(source):
    try:
        return list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (IndentationError, tokenize.TokenError, SyntaxError) as exc:
        raise ValueError("source is not tokenizable") from exc


def _valid_name(value):
    return (isinstance(value, str) and value and
            all(part.isidentifier() for part in value.split(".")))


def _mapping_items(mapping):
    if not hasattr(mapping, "items"):
        raise TypeError("mapping must be a mapping")
    result = []
    for old, new in mapping.items():
        if not _valid_name(old) or not _valid_name(new):
            raise ValueError("mapping names must be dotted identifiers")
        result.append((old, new))
    return sorted(result, key=lambda pair: pair[0])


def _call_targets(tokens):
    """Yield (dotted name, first token index, last token index)."""
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if (token.type != tokenize.NAME or
                (index and tokens[index - 1].string in (".", "def", "class"))):
            index += 1
            continue
        last = index
        pieces = [token.string]
        while (last + 2 < len(tokens) and tokens[last + 1].string == "."
               and tokens[last + 2].type == tokenize.NAME):
            pieces.extend([tokens[last + 1].string, tokens[last + 2].string])
            last += 2
        if last + 1 < len(tokens) and tokens[last + 1].string == "(":
            yield "".join(pieces), index, last
        index = last + 1


def _call_spans(tokens, mapping):
    result = []
    for name, first, last in _call_targets(tokens):
        if name in mapping:
            result.append((first, last, mapping[name]))
    return result


def _offsets(source):
    starts = [0]
    for line in source.splitlines(True):
        starts.append(starts[-1] + len(line))
    return starts


def _absolute(starts, point):
    return starts[point[0] - 1] + point[1]


def _apply(source, tokens, spans):
    starts = _offsets(source)
    result = source
    absolute = [(_absolute(starts, tokens[first].start),
                 _absolute(starts, tokens[last].end), replacement)
                for first, last, replacement in spans]
    for begin, end, replacement in sorted(absolute, reverse=True):
        result = result[:begin] + replacement + result[end:]
    return result


def rewrite_calls(source, mapping):
    if not isinstance(source, str):
        raise TypeError("source must be a string")
    items = _mapping_items(mapping)
    tokens = _tokens(source)
    return _apply(source, tokens, _call_spans(tokens, dict(items)))


def called_names(source):
    return [name for name, _, _ in _call_targets(_tokens(source))]


def call_count(source, name=None):
    names = called_names(source)
    return len(names) if name is None else sum(item == name for item in names)


def rewrite_many(sources, mapping):
    return [rewrite_calls(source, mapping) for source in sources]


def changed(source, mapping):
    return rewrite_calls(source, mapping) != source


__all__ = ["rewrite_calls", "called_names", "call_count", "rewrite_many", "changed"]
