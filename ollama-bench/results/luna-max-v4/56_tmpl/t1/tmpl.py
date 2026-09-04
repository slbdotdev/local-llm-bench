"""A small, deliberately strict text template engine."""

__all__ = ["TemplateError", "render"]


class TemplateError(Exception):
    """An error found while lexing, parsing, or rendering a template."""

    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(kind, pos)


_UNDEFINED = object()
_WHITESPACE = " \t\r\n\v\f"
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


def _is_whitespace(ch):
    return ch in _WHITESPACE


def _is_digit(ch):
    return "0" <= ch <= "9"


def _is_letter(ch):
    return ("a" <= ch <= "z") or ("A" <= ch <= "Z")


def _is_ident_start(ch):
    return _is_letter(ch) or ch == "_"


def _is_ident_continue(ch):
    return _is_ident_start(ch) or _is_digit(ch)


def _strip_whitespace(text):
    start = 0
    end = len(text)
    while start < end and _is_whitespace(text[start]):
        start += 1
    while end > start and _is_whitespace(text[end - 1]):
        end -= 1
    return text[start:end]


def _parse_digits(text):
    number = 0
    for ch in text:
        number = number * 10 + (ord(ch) - ord("0"))
    return number


def _decimal_text(number):
    """Return an integer's decimal form without relying on int-to-str limits."""
    if number == 0:
        return "0"
    negative = number < 0
    if negative:
        number = -number
    digits = []
    while number:
        number, digit = divmod(number, 10)
        digits.append(chr(ord("0") + digit))
    if negative:
        digits.append("-")
    digits.reverse()
    return "".join(digits)


class _Value:
    __slots__ = ("raw", "safe")

    def __init__(self, raw, safe=False):
        self.raw = raw
        self.safe = bool(safe)


def _as_value(value):
    if isinstance(value, _Value):
        return value
    return _Value(value)


def _raw(value):
    if isinstance(value, _Value):
        return value.raw
    return value


def _type_name(value):
    raw = _raw(value)
    if raw is _UNDEFINED:
        return None
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
    return None


def _value_text(value):
    raw = _raw(value)
    if raw is _UNDEFINED or raw is None:
        return ""
    if isinstance(raw, bool):
        return "true" if raw else "false"
    if isinstance(raw, int):
        return _decimal_text(raw)
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        parts = []
        for item in raw:
            parts.append(_value_text(_as_value(item)))
        return "[" + ", ".join(parts) + "]"
    if isinstance(raw, dict):
        parts = []
        for key, item in raw.items():
            parts.append(_value_text(_as_value(key)) + ": " + _value_text(_as_value(item)))
        return "{" + ", ".join(parts) + "}"
    return ""


def _is_falsy(value):
    raw = _raw(value)
    if raw is _UNDEFINED or raw is None:
        return True
    if isinstance(raw, bool):
        return not raw
    if isinstance(raw, int):
        return raw == 0
    if isinstance(raw, str):
        return raw == "" or raw == "0" or raw == "false"
    if isinstance(raw, (list, dict)):
        return len(raw) == 0
    return False


def _escape_text(text):
    parts = []
    for ch in text:
        if ch == "&":
            parts.append("&amp;")
        elif ch == "<":
            parts.append("&lt;")
        elif ch == ">":
            parts.append("&gt;")
        elif ch == '"':
            parts.append("&#34;")
        elif ch == "'":
            parts.append("&#39;")
        else:
            parts.append(ch)
    return "".join(parts)


def _ascii_upper(text):
    parts = []
    for ch in text:
        if "a" <= ch <= "z":
            parts.append(chr(ord(ch) - (ord("a") - ord("A"))))
        else:
            parts.append(ch)
    return "".join(parts)


def _ascii_lower(text):
    parts = []
    for ch in text:
        if "A" <= ch <= "Z":
            parts.append(chr(ord(ch) + (ord("a") - ord("A"))))
        else:
            parts.append(ch)
    return "".join(parts)


def _trim_text(text):
    start = 0
    end = len(text)
    while start < end and _is_whitespace(text[start]):
        start += 1
    while end > start and _is_whitespace(text[end - 1]):
        end -= 1
    return text[start:end]


def _map_find(mapping, key):
    """Find a key with exact key type semantics."""
    for existing_key, value in mapping.items():
        if type(existing_key) is type(key) and existing_key == key:
            return True, value
    return False, None


def _digit_string_index(key):
    if not isinstance(key, str) or not key:
        return None
    for ch in key:
        if not _is_digit(ch):
            return None
    return _parse_digits(key)


def _lookup(base_value, key_value):
    base = _raw(base_value)
    key = _raw(key_value)

    if base is _UNDEFINED or base is None:
        return _Value(_UNDEFINED)

    if isinstance(base, dict):
        found, value = _map_find(base, key)
        if found:
            return _Value(_raw(value))

    index = None
    if isinstance(key, int) and not isinstance(key, bool):
        index = key
    else:
        index = _digit_string_index(key)

    if isinstance(base, (list, str)) and index is not None:
        if 0 <= index < len(base):
            return _Value(_raw(base[index]))
        return _Value(_UNDEFINED)

    if isinstance(key, str):
        if key == "size":
            if isinstance(base, (list, str, dict)):
                return _Value(len(base))
        elif key == "keys":
            if isinstance(base, dict):
                return _Value(list(base.keys()))
        elif key == "type":
            name = _type_name(base)
            if name is not None:
                return _Value(name)
    return _Value(_UNDEFINED)


def _equal(left_value, right_value):
    left = _raw(left_value)
    right = _raw(right_value)
    left_type = _type_name(left)
    right_type = _type_name(right)
    if left_type != right_type:
        return False
    if left is _UNDEFINED or left is None:
        return True
    if left_type == "bool":
        return left == right
    if left_type == "number" or left_type == "string":
        return left == right
    if left_type == "list":
        if len(left) != len(right):
            return False
        for left_item, right_item in zip(left, right):
            if not _equal(_as_value(left_item), _as_value(right_item)):
                return False
        return True
    if left_type == "map":
        if len(left) != len(right):
            return False
        for key, left_item in left.items():
            found, right_item = _map_find(right, key)
            if not found or not _equal(_as_value(left_item), _as_value(right_item)):
                return False
        return True
    return False


def _compare(left_value, operator, right_value, pos):
    left = _raw(left_value)
    right = _raw(right_value)
    left_type = _type_name(left)
    right_type = _type_name(right)
    if left_type == "number" and right_type == "number":
        pass
    elif left_type == "string" and right_type == "string":
        pass
    else:
        raise TemplateError("bad_operand", pos)

    if operator == "<":
        result = left < right
    elif operator == "<=":
        result = left <= right
    elif operator == ">":
        result = left > right
    else:
        result = left >= right
    return _Value(bool(result))


def _contains(left_value, right_value):
    left = _raw(left_value)
    right = _raw(right_value)
    right_type = _type_name(right)
    if right_type == "string":
        return isinstance(left, str) and left in right
    if right_type == "list":
        for item in right:
            if _equal(left_value, _as_value(item)):
                return True
        return False
    if right_type == "map":
        return isinstance(left, str) and _map_find(right, left)[0]
    return False


def _slice_index(value):
    raw = _raw(value)
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw if raw >= 0 else None
    if isinstance(raw, str) and raw:
        for ch in raw:
            if not _is_digit(ch):
                return None
        return _parse_digits(raw)
    return None


def _apply_filter(value, name, args):
    raw = _raw(value)
    safe = value.safe

    if name == "upper":
        return _Value(_ascii_upper(_value_text(value)), safe)
    if name == "lower":
        return _Value(_ascii_lower(_value_text(value)), safe)
    if name == "trim":
        return _Value(_trim_text(_value_text(value)), safe)
    if name == "length":
        if raw is _UNDEFINED or raw is None or isinstance(raw, bool):
            length = 0
        elif isinstance(raw, int):
            length = len(_decimal_text(raw if raw >= 0 else -raw))
        elif isinstance(raw, (str, list, dict)):
            length = len(raw)
        else:
            length = 0
        return _Value(length, safe)
    if name == "first":
        if isinstance(raw, str) and raw:
            result = raw[0]
        elif isinstance(raw, list) and raw:
            result = _raw(raw[0])
        elif isinstance(raw, dict) and raw:
            result = next(iter(raw))
        else:
            result = _UNDEFINED
        return _Value(result, safe)
    if name == "safe":
        return _Value(raw, True)
    if name == "escape":
        return _Value(_escape_text(_value_text(value)), True)
    if name == "default":
        if _is_falsy(value):
            return _Value(args[0], False)
        return value
    if name == "join":
        separator = _value_text(_Value(args[0]))
        if raw is _UNDEFINED or raw is None:
            result = ""
        elif isinstance(raw, list):
            result = separator.join(_value_text(_as_value(item)) for item in raw)
        elif isinstance(raw, str):
            result = separator.join(raw)
        elif isinstance(raw, dict):
            result = separator.join(_value_text(_as_value(key)) for key in raw)
        else:
            result = _value_text(value)
        return _Value(result, safe)
    if name == "replace":
        text = _value_text(value)
        old = _value_text(_Value(args[0]))
        new = _value_text(_Value(args[1]))
        if old == "":
            result = text
        else:
            pieces = []
            cursor = 0
            while cursor < len(text):
                found = text.find(old, cursor)
                if found < 0:
                    pieces.append(text[cursor:])
                    cursor = len(text)
                else:
                    pieces.append(text[cursor:found])
                    pieces.append(new)
                    cursor = found + len(old)
            if cursor == len(text) and not pieces and text == "":
                result = ""
            else:
                result = "".join(pieces)
        return _Value(result, safe)
    if name == "slice":
        start = _slice_index(_Value(args[0]))
        length = _slice_index(_Value(args[1]))
        if start is None or length is None:
            return _Value(raw, safe)
        if isinstance(raw, (list, str)):
            material = raw
            is_list = isinstance(raw, list)
        else:
            material = _value_text(value)
            is_list = False
        available = len(material)
        if start >= available or length == 0:
            result = [] if is_list else ""
        else:
            end = start + length
            if end > available:
                end = available
            result = material[start:end]
        return _Value(result, safe)

    # Parsing guarantees that this branch is unreachable.  Keeping it total
    # makes filter application harmless even if called independently.
    return value


class _Environment:
    def __init__(self, context):
        initial = {}
        for name, value in context.items():
            initial[name] = _Value(value)
        self.scopes = [initial]

    def get(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return _Value(_UNDEFINED)

    def set(self, name, value):
        self.scopes[-1][name] = value


class _Expr:
    def evaluate(self, environment):
        raise NotImplementedError


class _Literal(_Expr):
    def __init__(self, value):
        self.value = value

    def evaluate(self, environment):
        return _Value(self.value)


class _Name(_Expr):
    def __init__(self, name):
        self.name = name

    def evaluate(self, environment):
        return environment.get(self.name)


class _LookupExpr(_Expr):
    def __init__(self, base, key):
        self.base = base
        self.key = key

    def evaluate(self, environment):
        return _lookup(self.base.evaluate(environment), self.key.evaluate(environment))


class _NotExpr(_Expr):
    def __init__(self, child):
        self.child = child

    def evaluate(self, environment):
        return _Value(not _is_falsy(self.child.evaluate(environment)))


class _BooleanExpr(_Expr):
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right

    def evaluate(self, environment):
        left = self.left.evaluate(environment)
        if self.operator == "and":
            if _is_falsy(left):
                return _Value(False)
            right = self.right.evaluate(environment)
            return _Value(not _is_falsy(right))
        if not _is_falsy(left):
            return _Value(True)
        right = self.right.evaluate(environment)
        return _Value(not _is_falsy(right))


class _ComparisonExpr(_Expr):
    def __init__(self, operator, left, right, pos):
        self.operator = operator
        self.left = left
        self.right = right
        self.pos = pos

    def evaluate(self, environment):
        left = self.left.evaluate(environment)
        right = self.right.evaluate(environment)
        if self.operator == "==":
            return _Value(_equal(left, right))
        if self.operator == "!=":
            return _Value(not _equal(left, right))
        if self.operator == "in":
            return _Value(_contains(left, right))
        return _compare(left, self.operator, right, self.pos)


class _PipelineExpr(_Expr):
    def __init__(self, base, filters):
        self.base = base
        self.filters = filters

    def evaluate(self, environment):
        value = self.base.evaluate(environment)
        for name, args in self.filters:
            value = _apply_filter(value, name, args)
        return value


class _ExprParser:
    def __init__(self, text, pos, allow_pipeline):
        self.text = text
        self.pos = pos
        self.allow_pipeline = allow_pipeline
        self.index = 0

    def error(self, kind="syntax"):
        raise TemplateError(kind, self.pos)

    def skip(self):
        while self.index < len(self.text) and _is_whitespace(self.text[self.index]):
            self.index += 1

    def keyword_at(self, word):
        end = self.index + len(word)
        if not self.text.startswith(word, self.index):
            return False
        if end < len(self.text) and _is_ident_continue(self.text[end]):
            return False
        return True

    def consume_keyword(self, word):
        self.skip()
        if self.keyword_at(word):
            self.index += len(word)
            return True
        return False

    def parse(self):
        self.skip()
        if self.index >= len(self.text):
            self.error()
        expression = self.parse_disjunct()
        filters = []
        while True:
            self.skip()
            if self.index >= len(self.text) or self.text[self.index] != "|":
                break
            if not self.allow_pipeline:
                self.error()
            self.index += 1
            self.skip()
            if self.index >= len(self.text):
                self.error()
            if _is_digit(self.text[self.index]):
                self.error()
            if not (_is_letter(self.text[self.index]) or self.text[self.index] == "_"):
                self.error()
            start = self.index
            self.index += 1
            while self.index < len(self.text) and (
                _is_letter(self.text[self.index])
                or _is_digit(self.text[self.index])
                or self.text[self.index] == "_"
            ):
                self.index += 1
            name = self.text[start:self.index]
            if name not in _FILTER_ARITY:
                self.error("unknown_filter")

            self.skip()
            args = []
            if self.index < len(self.text) and self.text[self.index] == ":":
                self.index += 1
                args = self.parse_filter_args()

            self.skip()
            if self.index < len(self.text) and self.text[self.index] != "|":
                self.error()
            if len(args) != _FILTER_ARITY[name]:
                self.error("filter_args")
            filters.append((name, args))

        self.skip()
        if self.index != len(self.text):
            self.error()
        if filters:
            return _PipelineExpr(expression, filters)
        return expression

    def parse_filter_args(self):
        args = []
        while True:
            self.skip()
            if self.index < len(self.text) and self.text[self.index] in "'\"":
                argument = self.read_string()
                self.skip()
                if self.index < len(self.text) and self.text[self.index] not in ",|":
                    self.error()
            else:
                start = self.index
                while self.index < len(self.text) and self.text[self.index] not in ",|":
                    self.index += 1
                argument = _filter_argument_value(_strip_whitespace(self.text[start:self.index]))
            args.append(argument)
            if self.index < len(self.text) and self.text[self.index] == ",":
                self.index += 1
                continue
            break
        return args

    def read_string(self):
        quote = self.text[self.index]
        self.index += 1
        characters = []
        while self.index < len(self.text):
            ch = self.text[self.index]
            self.index += 1
            if ch == quote:
                return "".join(characters)
            if ch == "\\":
                if self.index >= len(self.text):
                    self.error()
                escaped = self.text[self.index]
                self.index += 1
                if escaped == "n":
                    characters.append("\n")
                elif escaped == "t":
                    characters.append("\t")
                else:
                    characters.append(escaped)
            else:
                characters.append(ch)
        self.error()

    def parse_disjunct(self):
        expression = self.parse_conjunct()
        while self.consume_keyword("or"):
            expression = _BooleanExpr("or", expression, self.parse_conjunct())
        return expression

    def parse_conjunct(self):
        expression = self.parse_negation()
        while self.consume_keyword("and"):
            expression = _BooleanExpr("and", expression, self.parse_negation())
        return expression

    def parse_negation(self):
        if self.consume_keyword("not"):
            return _NotExpr(self.parse_negation())
        return self.parse_comparison()

    def peek_comparison(self):
        self.skip()
        if self.text.startswith("==", self.index):
            return "=="
        if self.text.startswith("!=", self.index):
            return "!="
        if self.text.startswith("<=", self.index):
            return "<="
        if self.text.startswith(">=", self.index):
            return ">="
        if self.index < len(self.text) and self.text[self.index] == "<":
            return "<"
        if self.index < len(self.text) and self.text[self.index] == ">":
            return ">"
        if self.keyword_at("in"):
            return "in"
        return None

    def parse_comparison(self):
        left = self.parse_primary()
        operator = self.peek_comparison()
        if operator is None:
            return left
        self.index += len(operator)
        right = self.parse_primary()
        if self.peek_comparison() is not None:
            self.error()
        return _ComparisonExpr(operator, left, right, self.pos)

    def parse_primary(self):
        expression = self.parse_atom()
        while True:
            self.skip()
            if self.index < len(self.text) and self.text[self.index] == ".":
                self.index += 1
                key = self.parse_dot_key()
                expression = _LookupExpr(expression, _Literal(key))
            elif self.index < len(self.text) and self.text[self.index] == "[":
                self.index += 1
                self.skip()
                key = self.parse_primary()
                self.skip()
                if self.index >= len(self.text) or self.text[self.index] != "]":
                    self.error()
                self.index += 1
                expression = _LookupExpr(expression, key)
            else:
                return expression

    def parse_dot_key(self):
        self.skip()
        if self.index >= len(self.text):
            self.error()
        if _is_ident_start(self.text[self.index]):
            start = self.index
            self.index += 1
            while self.index < len(self.text) and _is_ident_continue(self.text[self.index]):
                self.index += 1
            return self.text[start:self.index]
        if _is_digit(self.text[self.index]):
            start = self.index
            self.index += 1
            while self.index < len(self.text) and _is_digit(self.text[self.index]):
                self.index += 1
            return self.text[start:self.index]
        self.error()

    def parse_atom(self):
        self.skip()
        if self.index >= len(self.text):
            self.error()
        ch = self.text[self.index]
        if ch in "'\"":
            return _Literal(self.read_string())
        if _is_digit(ch):
            start = self.index
            self.index += 1
            while self.index < len(self.text) and _is_digit(self.text[self.index]):
                self.index += 1
            return _Literal(_parse_digits(self.text[start:self.index]))
        if _is_ident_start(ch):
            start = self.index
            self.index += 1
            while self.index < len(self.text) and _is_ident_continue(self.text[self.index]):
                self.index += 1
            name = self.text[start:self.index]
            if name == "true":
                return _Literal(True)
            if name == "false":
                return _Literal(False)
            if name == "none":
                return _Literal(None)
            if name in _KEYWORDS:
                self.error()
            return _Name(name)
        self.error()


def _filter_argument_value(text):
    if text and all(_is_digit(ch) for ch in text):
        return _parse_digits(text)
    if text == "true":
        return True
    if text == "false":
        return False
    if text == "none":
        return None
    return text


class _TextSegment:
    def __init__(self, text):
        self.text = text


class _TagSegment:
    def __init__(self, kind, body, pos, left_marker, right_marker):
        self.kind = kind
        self.body = body
        self.pos = pos
        self.left_marker = left_marker
        self.right_marker = right_marker


def _lex(source):
    closers = {"{": "}}", "%": "%}", "#": "#}"}
    segments = []
    text_start = 0
    index = 0
    while index < len(source):
        if source[index] == "{" and index + 1 < len(source) and source[index + 1] in "{%#":
            opener_kind = source[index + 1]
            closer = closers[opener_kind]
            tag_pos = index
            body_start = index + 2
            left_marker = body_start < len(source) and source[body_start] == "-"
            if left_marker:
                body_start += 1
            close_start = source.find(closer, body_start)
            if close_start < 0:
                raise TemplateError("unclosed_tag", tag_pos)
            right_marker = close_start > body_start and source[close_start - 1] == "-"
            body_end = close_start - 1 if right_marker else close_start
            segments.append(_TextSegment(source[text_start:tag_pos]))
            kind = "interp" if opener_kind == "{" else "block" if opener_kind == "%" else "comment"
            segments.append(
                _TagSegment(
                    kind,
                    source[body_start:body_end],
                    tag_pos,
                    left_marker,
                    right_marker,
                )
            )
            index = close_start + 2
            text_start = index
        else:
            index += 1
    segments.append(_TextSegment(source[text_start:]))

    for position, segment in enumerate(segments):
        if not isinstance(segment, _TextSegment):
            continue
        original = segment.text
        start = 0
        end = len(original)
        if position > 0:
            previous = segments[position - 1]
            if isinstance(previous, _TagSegment) and previous.right_marker:
                while start < len(original) and _is_whitespace(original[start]):
                    start += 1
        if position + 1 < len(segments):
            following = segments[position + 1]
            if isinstance(following, _TagSegment) and following.left_marker:
                while end > 0 and _is_whitespace(original[end - 1]):
                    end -= 1
        segment.text = original[start:end]

    return [segment for segment in segments if not (
        isinstance(segment, _TagSegment) and segment.kind == "comment"
    )]


class _IfNode:
    def __init__(self, pos, condition, body):
        self.pos = pos
        self.branches = [(condition, body)]
        self.else_body = None


class _ForNode:
    def __init__(self, pos, name, expression, body):
        self.pos = pos
        self.name = name
        self.expression = expression
        self.body = body
        self.empty_body = None


class _InterpolationNode:
    def __init__(self, pos, expression):
        self.pos = pos
        self.expression = expression


class _SetNode:
    def __init__(self, pos, name, expression):
        self.pos = pos
        self.name = name
        self.expression = expression


class _Frame:
    def __init__(self, kind, node, body, state):
        self.kind = kind
        self.node = node
        self.body = body
        self.state = state


def _parse_set(rest, pos):
    index = 0
    if index >= len(rest) or not _is_ident_start(rest[index]):
        raise TemplateError("syntax", pos)
    start = index
    index += 1
    while index < len(rest) and _is_ident_continue(rest[index]):
        index += 1
    name = rest[start:index]
    if name in _KEYWORDS:
        raise TemplateError("syntax", pos)
    while index < len(rest) and _is_whitespace(rest[index]):
        index += 1
    if index >= len(rest) or rest[index] != "=":
        raise TemplateError("syntax", pos)
    if index + 1 < len(rest) and rest[index + 1] == "=":
        raise TemplateError("syntax", pos)
    index += 1
    while index < len(rest) and _is_whitespace(rest[index]):
        index += 1
    if index >= len(rest):
        raise TemplateError("syntax", pos)
    expression = _ExprParser(rest[index:], pos, True).parse()
    return name, expression


def _parse_for(rest, pos):
    index = 0
    if index >= len(rest) or not _is_ident_start(rest[index]):
        raise TemplateError("syntax", pos)
    start = index
    index += 1
    while index < len(rest) and _is_ident_continue(rest[index]):
        index += 1
    name = rest[start:index]
    if name in _KEYWORDS:
        raise TemplateError("syntax", pos)
    while index < len(rest) and _is_whitespace(rest[index]):
        index += 1
    if not rest.startswith("in", index):
        raise TemplateError("syntax", pos)
    after_in = index + 2
    if after_in < len(rest) and _is_ident_continue(rest[after_in]):
        raise TemplateError("syntax", pos)
    index = after_in
    while index < len(rest) and _is_whitespace(rest[index]):
        index += 1
    if index >= len(rest):
        raise TemplateError("syntax", pos)
    expression = _ExprParser(rest[index:], pos, True).parse()
    return name, expression


def _parse_segments(segments):
    root = []
    stack = []
    current = root

    for segment in segments:
        if isinstance(segment, _TextSegment):
            current.append(segment)
            continue

        if segment.kind == "interp":
            body = _strip_whitespace(segment.body)
            expression = _ExprParser(body, segment.pos, True).parse()
            current.append(_InterpolationNode(segment.pos, expression))
            continue

        body = _strip_whitespace(segment.body)
        if body == "":
            raise TemplateError("unknown_tag", segment.pos)
        name_end = 0
        while name_end < len(body) and not _is_whitespace(body[name_end]):
            name_end += 1
        name = body[:name_end]
        rest = _strip_whitespace(body[name_end:])

        if name == "if":
            if rest == "":
                raise TemplateError("syntax", segment.pos)
            condition = _ExprParser(rest, segment.pos, False).parse()
            node_body = []
            node = _IfNode(segment.pos, condition, node_body)
            current.append(node)
            frame = _Frame("if", node, node_body, "body")
            stack.append(frame)
            current = node_body
        elif name == "elif":
            if not stack or stack[-1].kind != "if" or stack[-1].state == "else":
                raise TemplateError("unexpected_tag", segment.pos)
            if rest == "":
                raise TemplateError("syntax", segment.pos)
            condition = _ExprParser(rest, segment.pos, False).parse()
            body_list = []
            stack[-1].node.branches.append((condition, body_list))
            stack[-1].body = body_list
            current = body_list
        elif name == "else":
            if not stack or stack[-1].kind != "if" or stack[-1].state == "else":
                raise TemplateError("unexpected_tag", segment.pos)
            if rest != "":
                raise TemplateError("syntax", segment.pos)
            body_list = []
            stack[-1].node.else_body = body_list
            stack[-1].body = body_list
            stack[-1].state = "else"
            current = body_list
        elif name == "endif":
            if not stack or stack[-1].kind != "if":
                raise TemplateError("unexpected_tag", segment.pos)
            if rest != "":
                raise TemplateError("syntax", segment.pos)
            stack.pop()
            current = stack[-1].body if stack else root
        elif name == "for":
            name_value, expression = _parse_for(rest, segment.pos)
            node_body = []
            node = _ForNode(segment.pos, name_value, expression, node_body)
            current.append(node)
            frame = _Frame("for", node, node_body, "body")
            stack.append(frame)
            current = node_body
        elif name == "empty":
            if not stack or stack[-1].kind != "for" or stack[-1].state == "empty":
                raise TemplateError("unexpected_tag", segment.pos)
            if rest != "":
                raise TemplateError("syntax", segment.pos)
            body_list = []
            stack[-1].node.empty_body = body_list
            stack[-1].body = body_list
            stack[-1].state = "empty"
            current = body_list
        elif name == "endfor":
            if not stack or stack[-1].kind != "for":
                raise TemplateError("unexpected_tag", segment.pos)
            if rest != "":
                raise TemplateError("syntax", segment.pos)
            stack.pop()
            current = stack[-1].body if stack else root
        elif name == "set":
            name_value, expression = _parse_set(rest, segment.pos)
            current.append(_SetNode(segment.pos, name_value, expression))
        else:
            raise TemplateError("unknown_tag", segment.pos)

    if stack:
        raise TemplateError("unclosed_block", stack[-1].node.pos)
    return root


def _render_nodes(nodes, environment, output):
    for node in nodes:
        if isinstance(node, _TextSegment):
            output.append(node.text)
        elif isinstance(node, _InterpolationNode):
            value = node.expression.evaluate(environment)
            text = _value_text(value)
            output.append(text if value.safe else _escape_text(text))
        elif isinstance(node, _SetNode):
            environment.set(node.name, node.expression.evaluate(environment))
        elif isinstance(node, _IfNode):
            rendered = False
            for condition, body in node.branches:
                if not _is_falsy(condition.evaluate(environment)):
                    _render_nodes(body, environment, output)
                    rendered = True
                    break
            if not rendered and node.else_body is not None:
                _render_nodes(node.else_body, environment, output)
        elif isinstance(node, _ForNode):
            sequence_value = node.expression.evaluate(environment)
            sequence = _raw(sequence_value)
            if sequence is _UNDEFINED or sequence is None:
                items = []
            elif isinstance(sequence, list):
                items = list(sequence)
            elif isinstance(sequence, str):
                items = list(sequence)
            elif isinstance(sequence, dict):
                items = list(sequence.keys())
            else:
                raise TemplateError("not_iterable", node.pos)

            environment.scopes.append({})
            try:
                if not items:
                    if node.empty_body is not None:
                        _render_nodes(node.empty_body, environment, output)
                else:
                    total = len(items)
                    for offset, item in enumerate(items):
                        environment.set(node.name, _Value(_raw(item)))
                        environment.set(
                            "loop",
                            _Value(
                                {
                                    "index": offset + 1,
                                    "index0": offset,
                                    "first": offset == 0,
                                    "last": offset == total - 1,
                                    "length": total,
                                }
                            ),
                        )
                        _render_nodes(node.body, environment, output)
            finally:
                environment.scopes.pop()


def render(source, context):
    """Lex, parse, and render *source* using *context*."""
    segments = _lex(source)
    tree = _parse_segments(segments)
    environment = _Environment(context)
    output = []
    _render_nodes(tree, environment, output)
    return "".join(output)
