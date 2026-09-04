_WS = " \t\r\n\v\f"
_KEYWORDS = {"true", "false", "none", "not", "and", "or", "in"}
_FILTER_ARITY = {
    "upper": 0,
    "lower": 0,
    "trim": 0,
    "length": 0,
    "first": 0,
    "safe": 0,
    "escape": 0,
    "default": 1,
    "join": 1,
    "replace": 2,
    "slice": 2,
}
_UNDEFINED = object()

__all__ = ["TemplateError", "render"]


class TemplateError(Exception):
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(kind, pos)


class _Value:
    __slots__ = ("raw", "safe")

    def __init__(self, raw, safe=False):
        self.raw = raw
        self.safe = bool(safe)


class _Tag:
    __slots__ = ("kind", "body", "pos", "left", "right")

    def __init__(self, kind, body, pos, left, right):
        self.kind = kind
        self.body = body
        self.pos = pos
        self.left = left
        self.right = right


class _Text:
    __slots__ = ("text",)

    def __init__(self, text):
        self.text = text


class _ExprParser:
    def __init__(self, text, tag_pos, allow_pipeline):
        self.text = text
        self.tag_pos = tag_pos
        self.allow_pipeline = allow_pipeline
        self.i = 0

    def _syntax(self):
        raise TemplateError("syntax", self.tag_pos)

    def _skip(self):
        text = self.text
        n = len(text)
        i = self.i
        while i < n and text[i] in _WS:
            i += 1
        self.i = i

    def _word_at(self, word):
        self._skip()
        i = self.i
        end = i + len(word)
        if not self.text.startswith(word, i):
            return False
        if end < len(self.text) and _is_ident_continue(self.text[end]):
            return False
        self.i = end
        return True

    def _parse_word(self, word):
        if self._word_at(word):
            return True
        return False

    def parse(self):
        node = self._parse_disjunct()
        filters = []
        if self.allow_pipeline:
            while True:
                self._skip()
                if self.i >= len(self.text) or self.text[self.i] != "|":
                    break
                self.i += 1
                filters.append(self._parse_filter())
        self._skip()
        if self.i != len(self.text):
            self._syntax()
        if filters:
            return ("filter_chain", node, filters)
        return node

    def _parse_disjunct(self):
        node = self._parse_conjunct()
        while self._parse_word("or"):
            node = ("or", node, self._parse_conjunct())
        return node

    def _parse_conjunct(self):
        node = self._parse_negation()
        while self._parse_word("and"):
            node = ("and", node, self._parse_negation())
        return node

    def _parse_negation(self):
        if self._parse_word("not"):
            return ("not", self._parse_negation())
        return self._parse_comparison()

    def _parse_comparison(self):
        left = self._parse_primary()
        self._skip()
        op = None
        for candidate in ("==", "!=", "<=", ">=", "<", ">"):
            if self.text.startswith(candidate, self.i):
                op = candidate
                self.i += len(candidate)
                break
        if op is None and self._parse_word("in"):
            op = "in"
        if op is None:
            return left
        right = self._parse_primary()
        return ("compare", op, left, right)

    def _parse_primary(self):
        node = self._parse_atom()
        while True:
            self._skip()
            if self.i < len(self.text) and self.text[self.i] == ".":
                self.i += 1
                self._skip()
                if self.i >= len(self.text):
                    self._syntax()
                if _is_ident_start(self.text[self.i]):
                    start = self.i
                    self.i += 1
                    while self.i < len(self.text) and _is_ident_continue(self.text[self.i]):
                        self.i += 1
                    key = self.text[start:self.i]
                elif _is_digit(self.text[self.i]):
                    start = self.i
                    while self.i < len(self.text) and _is_digit(self.text[self.i]):
                        self.i += 1
                    key = self.text[start:self.i]
                else:
                    self._syntax()
                node = ("lookup_dot", node, key)
                continue
            if self.i < len(self.text) and self.text[self.i] == "[":
                self.i += 1
                key = self._parse_primary()
                self._skip()
                if self.i >= len(self.text) or self.text[self.i] != "]":
                    self._syntax()
                self.i += 1
                node = ("lookup", node, key)
                continue
            break
        return node

    def _parse_atom(self):
        self._skip()
        if self.i >= len(self.text):
            self._syntax()
        c = self.text[self.i]
        if c == "'" or c == '"':
            return ("literal", self._read_string())
        if _is_digit(c):
            start = self.i
            while self.i < len(self.text) and _is_digit(self.text[self.i]):
                self.i += 1
            return ("literal", _parse_decimal(self.text[start:self.i]))
        if _is_ident_start(c):
            start = self.i
            self.i += 1
            while self.i < len(self.text) and _is_ident_continue(self.text[self.i]):
                self.i += 1
            word = self.text[start:self.i]
            if word == "true":
                return ("literal", True)
            if word == "false":
                return ("literal", False)
            if word == "none":
                return ("literal", None)
            if word in _KEYWORDS:
                self._syntax()
            return ("name", word)
        self._syntax()

    def _read_string(self):
        quote = self.text[self.i]
        self.i += 1
        result = []
        while self.i < len(self.text):
            c = self.text[self.i]
            self.i += 1
            if c == quote:
                return "".join(result)
            if c == "\\":
                if self.i >= len(self.text):
                    self._syntax()
                escaped = self.text[self.i]
                self.i += 1
                if escaped == "n":
                    result.append("\n")
                elif escaped == "t":
                    result.append("\t")
                else:
                    result.append(escaped)
            else:
                result.append(c)
        self._syntax()

    def _parse_filter(self):
        self._skip()
        if self.i >= len(self.text):
            self._syntax()
        if _is_digit(self.text[self.i]):
            self._syntax()
        if not (_is_letter(self.text[self.i]) or self.text[self.i] == "_"):
            self._syntax()
        start = self.i
        self.i += 1
        while self.i < len(self.text) and _is_filter_char(self.text[self.i]):
            self.i += 1
        name = self.text[start:self.i]
        if name not in _FILTER_ARITY:
            raise TemplateError("unknown_filter", self.tag_pos)

        args = []
        self._skip()
        if self.i < len(self.text) and self.text[self.i] == ":":
            self.i += 1
            args = self._parse_filter_args()

        self._skip()
        if len(args) != _FILTER_ARITY[name]:
            raise TemplateError("filter_args", self.tag_pos)
        if self.i < len(self.text) and self.text[self.i] != "|":
            self._syntax()
        return (name, args)

    def _parse_filter_args(self):
        args = []
        while True:
            self._skip()
            if self.i < len(self.text) and (self.text[self.i] == "'" or self.text[self.i] == '"'):
                value = self._read_string()
                self._skip()
                if self.i < len(self.text) and self.text[self.i] not in ",|":
                    self._syntax()
            else:
                start = self.i
                while self.i < len(self.text) and self.text[self.i] not in ",|":
                    self.i += 1
                value = _parse_filter_arg(_strip_ws(self.text[start:self.i]))
            args.append(value)
            self._skip()
            if self.i >= len(self.text) or self.text[self.i] == "|":
                return args
            if self.text[self.i] != ",":
                self._syntax()
            self.i += 1


def _is_ws(c):
    return c in _WS


def _is_letter(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z")


def _is_digit(c):
    return "0" <= c <= "9"


def _is_ident_start(c):
    return _is_letter(c) or c == "_"


def _is_ident_continue(c):
    return _is_ident_start(c) or _is_digit(c)


def _is_filter_char(c):
    return _is_letter(c) or _is_digit(c) or c == "_"


def _strip_ws(text):
    left = 0
    right = len(text)
    while left < right and _is_ws(text[left]):
        left += 1
    while right > left and _is_ws(text[right - 1]):
        right -= 1
    return text[left:right]


def _parse_decimal(text):
    value = 0
    for c in text:
        value = value * 10 + (ord(c) - 48)
    return value


def _parse_filter_arg(text):
    if text != "":
        all_digits = True
        for c in text:
            if not _is_digit(c):
                all_digits = False
                break
        if all_digits:
            return _parse_decimal(text)
    if text == "true":
        return True
    if text == "false":
        return False
    if text == "none":
        return None
    return text


def _lex(source):
    segments = []
    last = 0
    i = 0
    length = len(source)
    openers = {"{{": ("interp", "}}"), "{%": ("block", "%}"), "{#": ("comment", "#}")}
    while i < length:
        if source[i] != "{" or i + 1 >= length:
            i += 1
            continue
        opener = source[i:i + 2]
        spec = openers.get(opener)
        if spec is None:
            i += 1
            continue
        if i > last:
            segments.append(_Text(source[last:i]))
        kind, closer = spec
        body_start = i + 2
        left = body_start < length and source[body_start] == "-"
        if left:
            body_start += 1
        close_start = source.find(closer, body_start)
        if close_start < 0:
            raise TemplateError("unclosed_tag", i)
        right = close_start > i and source[close_start - 1] == "-"
        body_end = close_start - 1 if right else close_start
        body = source[body_start:body_end]
        segments.append(_Tag(kind, body, i, left, right))
        i = close_start + 2
        last = i
    if last < length:
        segments.append(_Text(source[last:]))

    for index, segment in enumerate(segments):
        if not isinstance(segment, _Text):
            continue
        original = segment.text
        start = 0
        end = len(original)
        if index > 0 and isinstance(segments[index - 1], _Tag) and segments[index - 1].right:
            while start < end and _is_ws(original[start]):
                start += 1
        if index + 1 < len(segments) and isinstance(segments[index + 1], _Tag) and segments[index + 1].left:
            while end > 0 and _is_ws(original[end - 1]):
                end -= 1
        segment.text = original[start:end]
    return segments


def _split_tag_body(body):
    if body == "":
        return "", ""
    i = 0
    while i < len(body) and not _is_ws(body[i]):
        i += 1
    return body[:i], _strip_ws(body[i:])


def _text_is_identifier(text):
    if text == "" or not _is_ident_start(text[0]):
        return False
    for c in text[1:]:
        if not _is_ident_continue(c):
            return False
    return text not in _KEYWORDS


def _word_at_text(text, index, word):
    end = index + len(word)
    if not text.startswith(word, index):
        return False
    return end == len(text) or not _is_ident_continue(text[end])


def _parse_set(rest, pos):
    if rest == "" or not _is_ident_start(rest[0]):
        raise TemplateError("syntax", pos)
    i = 1
    while i < len(rest) and _is_ident_continue(rest[i]):
        i += 1
    name = rest[:i]
    if name in _KEYWORDS:
        raise TemplateError("syntax", pos)
    while i < len(rest) and _is_ws(rest[i]):
        i += 1
    if i >= len(rest) or rest[i] != "=" or (i + 1 < len(rest) and rest[i + 1] == "="):
        raise TemplateError("syntax", pos)
    i += 1
    expression = _strip_ws(rest[i:])
    if expression == "":
        raise TemplateError("syntax", pos)
    return name, _ExprParser(expression, pos, True).parse()


def _parse_for(rest, pos):
    if rest == "" or not _is_ident_start(rest[0]):
        raise TemplateError("syntax", pos)
    i = 1
    while i < len(rest) and _is_ident_continue(rest[i]):
        i += 1
    name = rest[:i]
    if name in _KEYWORDS:
        raise TemplateError("syntax", pos)
    while i < len(rest) and _is_ws(rest[i]):
        i += 1
    if not _word_at_text(rest, i, "in"):
        raise TemplateError("syntax", pos)
    i += 2
    expression = _strip_ws(rest[i:])
    if expression == "":
        raise TemplateError("syntax", pos)
    return name, _ExprParser(expression, pos, True).parse()


def _parse(segments):
    root = []
    current = root
    stack = []
    for segment in segments:
        if isinstance(segment, _Text):
            current.append(("text", segment.text))
            continue
        if segment.kind == "comment":
            continue
        body = _strip_ws(segment.body)
        if segment.kind == "interp":
            if body == "":
                raise TemplateError("syntax", segment.pos)
            expression = _ExprParser(body, segment.pos, True).parse()
            current.append(("interp", expression, segment.pos))
            continue

        name, rest = _split_tag_body(body)
        if name == "":
            raise TemplateError("unknown_tag", segment.pos)
        if name not in {"if", "elif", "else", "endif", "for", "empty", "endfor", "set"}:
            raise TemplateError("unknown_tag", segment.pos)

        if name == "elif":
            if not stack or stack[-1]["kind"] != "if" or stack[-1]["has_else"]:
                raise TemplateError("unexpected_tag", segment.pos)
            if rest == "":
                raise TemplateError("syntax", segment.pos)
            condition = _ExprParser(rest, segment.pos, False).parse()
            body_nodes = []
            stack[-1]["node"][1].append((condition, body_nodes, segment.pos))
            current = body_nodes
            continue

        if name == "else":
            if not stack or stack[-1]["kind"] != "if" or stack[-1]["has_else"]:
                raise TemplateError("unexpected_tag", segment.pos)
            if rest != "":
                raise TemplateError("syntax", segment.pos)
            body_nodes = []
            stack[-1]["node"][2] = body_nodes
            stack[-1]["has_else"] = True
            current = body_nodes
            continue

        if name == "endif":
            if not stack or stack[-1]["kind"] != "if":
                raise TemplateError("unexpected_tag", segment.pos)
            if rest != "":
                raise TemplateError("syntax", segment.pos)
            frame = stack.pop()
            current = frame["parent"]
            continue

        if name == "empty":
            if not stack or stack[-1]["kind"] != "for" or stack[-1]["has_empty"]:
                raise TemplateError("unexpected_tag", segment.pos)
            if rest != "":
                raise TemplateError("syntax", segment.pos)
            body_nodes = []
            stack[-1]["node"][4] = body_nodes
            stack[-1]["has_empty"] = True
            current = body_nodes
            continue

        if name == "endfor":
            if not stack or stack[-1]["kind"] != "for":
                raise TemplateError("unexpected_tag", segment.pos)
            if rest != "":
                raise TemplateError("syntax", segment.pos)
            frame = stack.pop()
            current = frame["parent"]
            continue

        if name == "if":
            if rest == "":
                raise TemplateError("syntax", segment.pos)
            condition = _ExprParser(rest, segment.pos, False).parse()
            node = ["if", [(condition, [], segment.pos)], None, segment.pos]
            current.append(node)
            stack.append({
                "kind": "if",
                "node": node,
                "parent": current,
                "pos": segment.pos,
                "has_else": False,
            })
            current = node[1][0][1]
            continue

        if name == "for":
            if rest == "":
                raise TemplateError("syntax", segment.pos)
            loop_name, expression = _parse_for(rest, segment.pos)
            node = ["for", loop_name, expression, [], None, segment.pos]
            current.append(node)
            stack.append({
                "kind": "for",
                "node": node,
                "parent": current,
                "pos": segment.pos,
                "has_empty": False,
            })
            current = node[3]
            continue

        # The only remaining opening tag is set.
        if rest == "":
            raise TemplateError("syntax", segment.pos)
        set_name, expression = _parse_set(rest, segment.pos)
        current.append(("set", set_name, expression, segment.pos))

    if stack:
        raise TemplateError("unclosed_block", stack[-1]["pos"])
    return root


def _kind(raw):
    if raw is _UNDEFINED:
        return "undefined"
    if raw is None:
        return "none"
    if isinstance(raw, bool):
        return "bool"
    if isinstance(raw, int):
        return "number"
    if isinstance(raw, str):
        return "string"
    if isinstance(raw, list):
        return "list"
    if isinstance(raw, dict):
        return "map"
    return "other"


def _int_text(value):
    if value == 0:
        return "0"
    negative = value < 0
    if negative:
        value = -value
    digits = []
    while value:
        value, digit = divmod(value, 10)
        digits.append(chr(48 + digit))
    digits.reverse()
    result = "".join(digits)
    return "-" + result if negative else result


def _value_text(value):
    raw = value.raw if isinstance(value, _Value) else value
    kind = _kind(raw)
    if kind == "undefined" or kind == "none":
        return ""
    if kind == "bool":
        return "true" if raw else "false"
    if kind == "number":
        return _int_text(raw)
    if kind == "string":
        return raw
    if kind == "list":
        return "[" + ", ".join(_value_text(item) for item in raw) + "]"
    if kind == "map":
        pieces = []
        for key, item in raw.items():
            pieces.append(_value_text(key) + ": " + _value_text(item))
        return "{" + ", ".join(pieces) + "}"
    return ""


def _escape(text):
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&#34;",
        "'": "&#39;",
    }
    pieces = []
    for c in text:
        pieces.append(replacements.get(c, c))
    return "".join(pieces)


def _is_falsy(value):
    raw = value.raw if isinstance(value, _Value) else value
    kind = _kind(raw)
    if kind == "undefined" or kind == "none":
        return True
    if kind == "bool":
        return not raw
    if kind == "number":
        return raw == 0
    if kind == "string":
        return raw == "" or raw == "0" or raw == "false"
    if kind == "list" or kind == "map":
        return len(raw) == 0
    return False


def _lookup(base, key):
    raw_base = base.raw
    raw_key = key.raw
    base_kind = _kind(raw_base)
    if base_kind == "undefined" or base_kind == "none":
        return _Value(_UNDEFINED)

    if base_kind == "map":
        if isinstance(raw_key, str) and raw_key in raw_base:
            return _Value(raw_base[raw_key])
    elif base_kind == "list" or base_kind == "string":
        index = None
        if isinstance(raw_key, int) and not isinstance(raw_key, bool):
            if raw_key >= 0:
                index = raw_key
        elif isinstance(raw_key, str) and raw_key != "":
            digits = True
            for c in raw_key:
                if not _is_digit(c):
                    digits = False
                    break
            if digits:
                index = _parse_decimal(raw_key)
        if index is not None:
            if index < len(raw_base):
                return _Value(raw_base[index])
            return _Value(_UNDEFINED)

    if isinstance(raw_key, str):
        if raw_key == "size":
            if base_kind == "string" or base_kind == "list" or base_kind == "map":
                return _Value(len(raw_base))
        elif raw_key == "keys":
            if base_kind == "map":
                return _Value(list(raw_base.keys()))
        elif raw_key == "type":
            if base_kind != "undefined":
                return _Value(base_kind)
    return _Value(_UNDEFINED)


def _equals(left, right):
    left_kind = _kind(left)
    right_kind = _kind(right)
    if left_kind != right_kind:
        return False
    if left_kind == "undefined" or left_kind == "none":
        return True
    if left_kind == "bool" or left_kind == "number" or left_kind == "string":
        return left == right
    if left_kind == "list":
        if len(left) != len(right):
            return False
        for index in range(len(left)):
            if not _equals(left[index], right[index]):
                return False
        return True
    if left_kind == "map":
        if len(left) != len(right):
            return False
        for key, value in left.items():
            if key not in right or not _equals(value, right[key]):
                return False
        return True
    return False


def _compare_values(op, left, right, pos):
    left_kind = _kind(left)
    right_kind = _kind(right)
    if op == "==":
        return _Value(_equals(left, right))
    if op == "!=":
        return _Value(not _equals(left, right))
    if op == "in":
        if right_kind == "string":
            return _Value(left_kind == "string" and left in right)
        if right_kind == "list":
            for item in right:
                if _equals(left, item):
                    return _Value(True)
            return _Value(False)
        if right_kind == "map":
            return _Value(left_kind == "string" and left in right)
        return _Value(False)
    if left_kind == "number" and right_kind == "number":
        pass
    elif left_kind == "string" and right_kind == "string":
        pass
    else:
        raise TemplateError("bad_operand", pos)
    if op == "<":
        result = left < right
    elif op == "<=":
        result = left <= right
    elif op == ">":
        result = left > right
    else:
        result = left >= right
    return _Value(bool(result))


def _apply_filter(name, value, args):
    raw = value.raw
    safe = value.safe
    if name == "upper":
        text = _value_text(value)
        result = []
        for c in text:
            if "a" <= c <= "z":
                result.append(chr(ord(c) - 32))
            else:
                result.append(c)
        return _Value("".join(result), safe)
    if name == "lower":
        text = _value_text(value)
        result = []
        for c in text:
            if "A" <= c <= "Z":
                result.append(chr(ord(c) + 32))
            else:
                result.append(c)
        return _Value("".join(result), safe)
    if name == "trim":
        text = _value_text(value)
        start = 0
        end = len(text)
        while start < end and _is_ws(text[start]):
            start += 1
        while end > start and _is_ws(text[end - 1]):
            end -= 1
        return _Value(text[start:end], safe)
    if name == "length":
        kind = _kind(raw)
        if kind == "undefined" or kind == "none" or kind == "bool":
            result = 0
        elif kind == "number":
            number_text = _int_text(raw)
            result = len(number_text)
        else:
            result = len(raw)
        return _Value(result, safe)
    if name == "first":
        kind = _kind(raw)
        if kind == "string" or kind == "list":
            result = raw[0] if len(raw) else _UNDEFINED
        elif kind == "map":
            result = next(iter(raw)) if raw else _UNDEFINED
        else:
            result = _UNDEFINED
        return _Value(result, safe)
    if name == "safe":
        return _Value(raw, True)
    if name == "escape":
        return _Value(_escape(_value_text(value)), True)
    if name == "default":
        if _is_falsy(value):
            return _Value(args[0], False)
        return value
    if name == "join":
        separator = _value_text(args[0])
        kind = _kind(raw)
        if kind == "undefined" or kind == "none":
            pieces = []
        elif kind == "list":
            pieces = [_value_text(item) for item in raw]
        elif kind == "string":
            pieces = list(raw)
        elif kind == "map":
            pieces = [_value_text(key) for key in raw.keys()]
        else:
            return _Value(_value_text(value), safe)
        return _Value(separator.join(pieces), safe)
    if name == "replace":
        text = _value_text(value)
        old = _value_text(args[0])
        new = _value_text(args[1])
        if old == "":
            result = text
        else:
            result = text.replace(old, new)
        return _Value(result, safe)
    # slice
    start = args[0]
    length = args[1]
    start = _slice_index(start)
    length = _slice_index(length)
    if start is None or length is None:
        return value
    end = start + length
    if isinstance(raw, list):
        return _Value(raw[start:end], safe)
    if isinstance(raw, str):
        return _Value(raw[start:end], safe)
    text = _value_text(value)
    return _Value(text[start:end], safe)


def _slice_index(value):
    if isinstance(value, int) and not isinstance(value, bool):
        return value if value >= 0 else None
    if isinstance(value, str) and value != "":
        for c in value:
            if not _is_digit(c):
                return None
        return _parse_decimal(value)
    return None


def _eval(node, scopes, tag_pos):
    kind = node[0]
    if kind == "literal":
        return _Value(node[1])
    if kind == "name":
        for scope in reversed(scopes):
            if node[1] in scope:
                return scope[node[1]]
        return _Value(_UNDEFINED)
    if kind == "lookup_dot":
        return _lookup(_eval(node[1], scopes, tag_pos), _Value(node[2]))
    if kind == "lookup":
        return _lookup(_eval(node[1], scopes, tag_pos), _eval(node[2], scopes, tag_pos))
    if kind == "not":
        return _Value(_is_falsy(_eval(node[1], scopes, tag_pos)))
    if kind == "and":
        left = _eval(node[1], scopes, tag_pos)
        if _is_falsy(left):
            return _Value(False)
        return _Value(not _is_falsy(_eval(node[2], scopes, tag_pos)))
    if kind == "or":
        left = _eval(node[1], scopes, tag_pos)
        if not _is_falsy(left):
            return _Value(True)
        return _Value(not _is_falsy(_eval(node[2], scopes, tag_pos)))
    if kind == "compare":
        left = _eval(node[2], scopes, tag_pos).raw
        right = _eval(node[3], scopes, tag_pos).raw
        return _compare_values(node[1], left, right, tag_pos)
    if kind == "filter_chain":
        value = _eval(node[1], scopes, tag_pos)
        for name, args in node[2]:
            value = _apply_filter(name, value, args)
        return value
    return _Value(_UNDEFINED)


def _render_nodes_with_positions(nodes, scopes, output):
    for node in nodes:
        kind = node[0]
        if kind == "text":
            output.append(node[1])
        elif kind == "interp":
            value = _eval(node[1], scopes, node[2])
            text = _value_text(value)
            output.append(text if value.safe else _escape(text))
        elif kind == "set":
            scopes[-1][node[1]] = _eval(node[2], scopes, node[3])
        elif kind == "if":
            selected = None
            for condition, body, condition_pos in node[1]:
                if not _is_falsy(_eval(condition, scopes, condition_pos)):
                    selected = body
                    break
            if selected is None:
                selected = node[2]
            if selected is not None:
                _render_nodes_with_positions(selected, scopes, output)
        else:
            raw_sequence = _eval(node[2], scopes, node[5]).raw
            sequence_kind = _kind(raw_sequence)
            if sequence_kind == "undefined" or sequence_kind == "none":
                sequence = []
            elif sequence_kind == "list":
                sequence = list(raw_sequence)
            elif sequence_kind == "string":
                sequence = list(raw_sequence)
            elif sequence_kind == "map":
                sequence = list(raw_sequence.keys())
            else:
                raise TemplateError("not_iterable", node[5])
            loop_scope = {}
            scopes.append(loop_scope)
            try:
                if not sequence:
                    if node[4] is not None:
                        _render_nodes_with_positions(node[4], scopes, output)
                else:
                    total = len(sequence)
                    for index, item in enumerate(sequence):
                        loop_scope[node[1]] = _Value(item)
                        loop_scope["loop"] = _Value({
                            "index": index + 1,
                            "index0": index,
                            "first": index == 0,
                            "last": index == total - 1,
                            "length": total,
                        })
                        _render_nodes_with_positions(node[3], scopes, output)
            finally:
                scopes.pop()


def render(source, context):
    segments = _lex(source)
    tree = _parse(segments)
    scopes = [{key: _Value(value) for key, value in context.items()}]
    output = []
    _render_nodes_with_positions(tree, scopes, output)
    return "".join(output)
