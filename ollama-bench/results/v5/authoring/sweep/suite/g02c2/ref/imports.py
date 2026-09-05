"""Token-preserving import-prefix rewriter used by a tiny build migrator."""

import io
import tokenize

def _offsets(source):
    starts = [0]
    for line in source.splitlines(True):
        starts.append(starts[-1] + len(line))
    return starts

def _absolute(starts, point):
    return starts[point[0] - 1] + point[1]

def _tokens(source):
    try:
        return list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (IndentationError, tokenize.TokenError, SyntaxError) as exc:
        raise ValueError("source is not tokenizable") from exc

def _mapping_items(mapping):
    if not hasattr(mapping, "items"):
        raise TypeError("mapping must be a mapping")
    answer = []
    for old, new in mapping.items():
        if not isinstance(old, str) or not isinstance(new, str):
            raise TypeError("module names must be strings")
        if not old or not new or old.startswith(".") or new.startswith("."):
            raise ValueError("module names must be absolute and non-empty")
        answer.append((old, new))
    return sorted(answer, key=lambda item: (-len(item[0]), item[0]))

def _map_name(name, items):
    for old, new in items:
        if name == old or name.startswith(old + "."):
            return new + name[len(old):]
    return None

def _module_tokens(tokens, index):
    if index >= len(tokens) or tokens[index].type != tokenize.NAME:
        return None
    first = last = index
    pieces = [tokens[index].string]
    index += 1
    while index + 1 < len(tokens):
        dot, name = tokens[index], tokens[index + 1]
        if dot.string != "." or name.type != tokenize.NAME:
            break
        pieces.extend([dot.string, name.string])
        last, index = index + 1, index + 2
    return "".join(pieces), first, last

def _next_code(tokens, index):
    while index < len(tokens) and tokens[index].type in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.COMMENT):
        index += 1
    return index

def _statement_end(tokens, index):
    depth = 0
    while index < len(tokens):
        token = tokens[index]
        if token.string in "([{":
            depth += 1
        elif token.string in ")]}":
            depth = max(0, depth - 1)
        elif depth == 0 and token.type == tokenize.NEWLINE:
            return index
        index += 1
    return index

def _plain_import_spans(tokens, items):
    spans, index = [], 0
    while index < len(tokens):
        if tokens[index].type != tokenize.NAME or tokens[index].string != "import":
            index += 1
            continue
        end, cursor = _statement_end(tokens, index + 1), _next_code(tokens, index + 1)
        while cursor < end:
            parsed = _module_tokens(tokens, cursor)
            if parsed is None:
                cursor += 1
                continue
            name, first, last = parsed
            replacement = _map_name(name, items)
            if replacement is not None:
                spans.append((tokens[first].start, tokens[last].end, replacement))
            cursor = last + 1
            while cursor < end and tokens[cursor].string != ",":
                cursor += 1
            cursor = _next_code(tokens, cursor + 1) if cursor < end else end
        index = max(index + 1, end + 1)
    return spans

def _from_import_spans(tokens, items):
    spans, index = [], 0
    while index < len(tokens):
        if tokens[index].type != tokenize.NAME or tokens[index].string != "from":
            index += 1
            continue
        end = _statement_end(tokens, index + 1)
        cursor = _next_code(tokens, index + 1)
        if cursor < end and tokens[cursor].string == ".":
            index = end + 1
            continue
        parsed = _module_tokens(tokens, cursor)
        cursor = parsed[2] + 1 if parsed else cursor
        if parsed is None or cursor >= end or tokens[cursor].string != "import":
            index = max(index + 1, end + 1)
            continue
        replacement = _map_name(parsed[0], items)
        if replacement is not None:
            spans.append((tokens[parsed[1]].start, tokens[parsed[2]].end, replacement))
        index = max(index + 1, end + 1)
    return spans

def _apply(source, spans):
    starts, result = _offsets(source), source
    absolute = [(_absolute(starts, a), _absolute(starts, b), text) for a, b, text in spans]
    for begin, end, text in sorted(absolute, reverse=True):
        result = result[:begin] + text + result[end:]
    return result

def rewrite_source(source, mapping):
    if not isinstance(source, str):
        raise TypeError("source must be a string")
    items = _mapping_items(mapping)
    tokens = _tokens(source)
    spans = _plain_import_spans(tokens, items) + _from_import_spans(tokens, items)
    return _apply(source, spans)

def imported_modules(source):
    tokens, answer = _tokens(source), []
    for index, token in enumerate(tokens):
        if token.type != tokenize.NAME or token.string != "import":
            continue
        end, cursor = _statement_end(tokens, index + 1), _next_code(tokens, index + 1)
        while cursor < end:
            parsed = _module_tokens(tokens, cursor)
            if parsed is None:
                cursor += 1
                continue
            answer.append(parsed[0])
            cursor = parsed[2] + 1
            while cursor < end and tokens[cursor].string != ",":
                cursor += 1
            cursor = _next_code(tokens, cursor + 1) if cursor < end else end
    return answer

def changed(source, mapping):
    return rewrite_source(source, mapping) != source

def rewrite_many(sources, mapping):
    return [rewrite_source(source, mapping) for source in sources]

__all__ = ["rewrite_source", "imported_modules", "changed", "rewrite_many"]


def import_spans(source):
    """Return source coordinates for plain import module names."""
    tokens = _tokens(source)
    spans = []
    for start, end, name in _plain_import_spans(tokens, []):
        spans.append((start, end, name))
    return spans


def from_modules(source):
    """List absolute modules in from-import statements."""
    tokens = _tokens(source)
    answer = []
    index = 0
    while index < len(tokens):
        if tokens[index].type == tokenize.NAME and tokens[index].string == "from":
            end = _statement_end(tokens, index + 1)
            cursor = _next_code(tokens, index + 1)
            parsed = _module_tokens(tokens, cursor)
            cursor = parsed[2] + 1 if parsed else cursor
            if parsed and cursor < end and tokens[cursor].string == "import":
                answer.append(parsed[0])
            index = max(index + 1, end + 1)
        else:
            index += 1
    return answer


def validate_mapping(mapping):
    """Validate and return mapping pairs in deterministic matching order."""
    return _mapping_items(mapping)


def rewrite_if_changed(source, mapping):
    """Return (changed, rewritten-source), avoiding a second caller comparison."""
    output = rewrite_source(source, mapping)
    return output != source, output


def source_lines(source):
    """Return source lines without changing newline characters."""
    if not isinstance(source, str):
        raise TypeError("source must be a string")
    return source.splitlines(True)


def has_import(source, module):
    """Whether a plain import statement names module exactly."""
    return module in imported_modules(source)


def rewrite_with_prefix(source, old, new):
    """Convenience wrapper for one module-prefix mapping."""
    return rewrite_source(source, {old: new})


__all__ += ["import_spans", "from_modules", "validate_mapping",
            "rewrite_if_changed", "source_lines", "has_import",
            "rewrite_with_prefix"]
