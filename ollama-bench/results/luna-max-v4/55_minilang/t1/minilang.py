"""A small hand-written interpreter for the language in TASK.md."""


_ERROR_KINDS = frozenset(
    (
        "parse",
        "dup_field",
        "dup_binding",
        "unbound",
        "uninit",
        "type",
        "div_zero",
        "no_field",
        "no_match",
    )
)


class MiniError(Exception):
    """The only exception exposed by the interpreter."""

    def __init__(self, kind):
        if type(kind) is not str or kind not in _ERROR_KINDS:
            kind = "parse"
        self.kind = kind
        Exception.__init__(self, kind)


class _Token:
    __slots__ = ("kind", "value", "position")

    def __init__(self, kind, value, position):
        self.kind = kind
        self.value = value
        self.position = position


class _Lexer:
    _reserved = frozenset(
        (
            "let",
            "letrec",
            "and",
            "in",
            "if",
            "then",
            "else",
            "fun",
            "match",
            "with",
            "end",
            "ref",
            "true",
            "false",
        )
    )
    _symbols = (
        "->",
        ":=",
        "==",
        "!=",
        "<=",
        ">=",
        "&&",
        "||",
        "++",
        "+",
        "-",
        "*",
        "/",
        "%",
        "<",
        ">",
        "=",
        "(",
        ")",
        "{",
        "}",
        ",",
        ".",
        "|",
        "!",
    )

    def __init__(self, source):
        self.source = source

    @staticmethod
    def _ascii_letter(character):
        return ("A" <= character <= "Z") or ("a" <= character <= "z")

    @staticmethod
    def _ascii_digit(character):
        return "0" <= character <= "9"

    def tokens(self):
        source = self.source
        length = len(source)
        position = 0
        result = []

        while position < length:
            character = source[position]

            if character in " \t\r\n":
                position += 1
                continue

            if self._ascii_digit(character):
                start = position
                if character == "0":
                    position += 1
                    if position < length and self._ascii_digit(source[position]):
                        raise MiniError("parse")
                else:
                    position += 1
                    while position < length and self._ascii_digit(source[position]):
                        position += 1
                result.append(_Token("INT", source[start:position], start))
                continue

            if character == '"':
                start = position + 1
                position += 1
                while position < length:
                    character = source[position]
                    if character == '"':
                        break
                    if character == "\\" or character == "\n" or character == "\r":
                        raise MiniError("parse")
                    position += 1
                if position >= length or source[position] != '"':
                    raise MiniError("parse")
                result.append(_Token("STRING", source[start:position], start - 1))
                position += 1
                continue

            if character == "_" or self._ascii_letter(character):
                start = position
                position += 1
                while position < length:
                    next_character = source[position]
                    if not (
                        self._ascii_letter(next_character)
                        or self._ascii_digit(next_character)
                        or next_character == "_"
                    ):
                        break
                    position += 1
                word = source[start:position]
                if word == "_":
                    kind = "UNDERSCORE"
                elif word in self._reserved:
                    kind = word
                else:
                    kind = "IDENT"
                result.append(_Token(kind, word, start))
                continue

            matched = False
            for symbol in self._symbols:
                if source.startswith(symbol, position):
                    result.append(_Token(symbol, symbol, position))
                    position += len(symbol)
                    matched = True
                    break
            if matched:
                continue

            raise MiniError("parse")

        result.append(_Token("EOF", "", length))
        return result


def _decimal_value(text):
    value = 0
    for character in text:
        value = value * 10 + (ord(character) - ord("0"))
    return value


def _decimal_text(value):
    if value == 0:
        return "0"
    negative = value < 0
    if negative:
        value = -value
    digits = []
    while value:
        value, remainder = divmod(value, 10)
        digits.append(chr(ord("0") + remainder))
    digits.reverse()
    text = "".join(digits)
    if negative:
        return "-" + text
    return text


class _Parser:
    _comparisons = frozenset(("==", "!=", "<", "<=", ">", ">="))
    _atom_starters = frozenset(("INT", "STRING", "true", "false", "IDENT", "(", "{"))

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def _current(self):
        return self.tokens[self.index]

    def _at(self, kind):
        return self._current().kind == kind

    def _accept(self, kind):
        if self._at(kind):
            token = self._current()
            self.index += 1
            return token
        return None

    def _expect(self, kind):
        token = self._accept(kind)
        if token is None:
            raise MiniError("parse")
        return token

    def _expect_identifier(self):
        token = self._accept("IDENT")
        if token is None:
            raise MiniError("parse")
        return token.value

    def parse(self):
        tree = self._expression()
        if not self._at("EOF"):
            raise MiniError("parse")
        return tree

    def _expression(self):
        if self._accept("let") is not None:
            name = self._expect_identifier()
            self._expect("=")
            right = self._expression()
            self._expect("in")
            body = self._expression()
            return ("let", name, right, body)

        if self._accept("letrec") is not None:
            return self._letrec_expression()

        if self._accept("if") is not None:
            condition = self._expression()
            self._expect("then")
            when_true = self._expression()
            self._expect("else")
            when_false = self._expression()
            return ("if", condition, when_true, when_false)

        if self._accept("fun") is not None:
            parameter = self._expect_identifier()
            self._expect("->")
            body = self._expression()
            return ("fun", parameter, body)

        if self._accept("match") is not None:
            return self._match_expression()

        return self._assignment()

    def _letrec_expression(self):
        names = []
        right_sides = []

        while True:
            names.append(self._expect_identifier())
            self._expect("=")
            right_sides.append(self._expression())
            if self._accept("and") is None:
                break

        self._expect("in")
        body = self._expression()

        seen = set()
        for name in names:
            if name in seen:
                raise MiniError("dup_binding")
            seen.add(name)

        return ("letrec", list(zip(names, right_sides)), body)

    def _match_expression(self):
        subject = self._expression()
        self._expect("with")
        arms = []
        if not self._at("|"):
            raise MiniError("parse")

        while self._accept("|") is not None:
            pattern, variables = self._pattern()
            seen = set()
            for variable in variables:
                if variable in seen:
                    raise MiniError("dup_binding")
                seen.add(variable)
            self._expect("->")
            arm_body = self._expression()
            arms.append((pattern, arm_body))

        self._expect("end")
        return ("match", subject, arms)

    def _assignment(self):
        left = self._or_expression()
        if self._accept(":=") is not None:
            right = self._expression()
            return ("assign", left, right)
        return left

    def _or_expression(self):
        tree = self._and_expression()
        while self._accept("||") is not None:
            tree = ("binary", "||", tree, self._and_expression())
        return tree

    def _and_expression(self):
        tree = self._comparison_expression()
        while self._accept("&&") is not None:
            tree = ("binary", "&&", tree, self._comparison_expression())
        return tree

    def _comparison_expression(self):
        tree = self._concatenation_expression()
        if self._current().kind in self._comparisons:
            op = self._current().kind
            self.index += 1
            right = self._concatenation_expression()
            if self._current().kind in self._comparisons:
                raise MiniError("parse")
            tree = ("binary", op, tree, right)
        return tree

    def _concatenation_expression(self):
        left = self._addition_expression()
        if self._accept("++") is not None:
            return ("binary", "++", left, self._concatenation_expression())
        return left

    def _addition_expression(self):
        tree = self._multiplication_expression()
        while self._current().kind in ("+", "-"):
            op = self._current().kind
            self.index += 1
            tree = ("binary", op, tree, self._multiplication_expression())
        return tree

    def _multiplication_expression(self):
        tree = self._unary_expression()
        while self._current().kind in ("*", "/", "%"):
            op = self._current().kind
            self.index += 1
            tree = ("binary", op, tree, self._unary_expression())
        return tree

    def _unary_expression(self):
        if self._current().kind in ("-", "!", "ref"):
            op = self._current().kind
            self.index += 1
            return ("unary", op, self._unary_expression())
        return self._application_expression()

    def _application_expression(self):
        tree = self._postfix_expression()
        while self._current().kind in self._atom_starters:
            tree = ("application", tree, self._postfix_expression())
        return tree

    def _postfix_expression(self):
        tree = self._atom()
        while self._accept(".") is not None:
            field = self._expect_identifier()
            tree = ("field", tree, field)
        return tree

    def _atom(self):
        token = self._current()
        if token.kind == "INT":
            self.index += 1
            return ("int", _decimal_value(token.value))
        if token.kind == "STRING":
            self.index += 1
            return ("str", token.value)
        if token.kind == "true":
            self.index += 1
            return ("bool", True)
        if token.kind == "false":
            self.index += 1
            return ("bool", False)
        if token.kind == "IDENT":
            self.index += 1
            return ("variable", token.value)
        if token.kind == "(":
            self.index += 1
            tree = self._expression()
            self._expect(")")
            return tree
        if token.kind == "{":
            return self._record()
        raise MiniError("parse")

    def _record(self):
        self._expect("{")
        fields = []
        if self._accept("}") is None:
            while True:
                name = self._expect_identifier()
                self._expect("=")
                value = self._expression()
                fields.append((name, value))
                if self._accept(",") is None:
                    break
            self._expect("}")

            seen = set()
            for name, unused in fields:
                if name in seen:
                    raise MiniError("dup_field")
                seen.add(name)
        return ("record", fields)

    def _pattern(self):
        token = self._current()
        if token.kind == "UNDERSCORE":
            self.index += 1
            return ("wildcard",), []
        if token.kind == "INT":
            self.index += 1
            return ("pint", _decimal_value(token.value)), []
        if token.kind == "STRING":
            self.index += 1
            return ("pstr", token.value), []
        if token.kind == "true":
            self.index += 1
            return ("pbool", True), []
        if token.kind == "false":
            self.index += 1
            return ("pbool", False), []
        if token.kind == "IDENT":
            self.index += 1
            return ("pvariable", token.value), [token.value]
        if token.kind == "{":
            return self._record_pattern()
        raise MiniError("parse")

    def _record_pattern(self):
        self._expect("{")
        fields = []
        variables = []
        if self._accept("}") is None:
            while True:
                name = self._expect_identifier()
                self._expect("=")
                pattern, nested_variables = self._pattern()
                fields.append((name, pattern))
                variables.extend(nested_variables)
                if self._accept(",") is None:
                    break
            self._expect("}")

            seen = set()
            for name, unused in fields:
                if name in seen:
                    raise MiniError("dup_field")
                seen.add(name)
        return ("precord", fields), variables


class _Cell:
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value


class _Slot:
    __slots__ = ("initialized", "value")

    def __init__(self):
        self.initialized = False
        self.value = None


class _Closure:
    __slots__ = ("parameter", "body", "environment")

    def __init__(self, parameter, body, environment):
        self.parameter = parameter
        self.body = body
        self.environment = environment


class _Environment:
    __slots__ = ("bindings", "parent")

    def __init__(self, bindings=None, parent=None):
        self.bindings = {} if bindings is None else bindings
        self.parent = parent


def _is_int(value):
    return type(value) is int


def _is_bool(value):
    return type(value) is bool


def _is_str(value):
    return type(value) is str


def _is_record(value):
    return type(value) is dict


def _truncating_quotient(left, right):
    quotient = divmod(abs(left), abs(right))[0]
    if (left < 0) != (right < 0):
        return -quotient
    return quotient


class _Interpreter:
    def visit(self, tree, environment):
        tag = tree[0]

        if tag == "int" or tag == "str" or tag == "bool":
            return tree[1]

        if tag == "variable":
            return self._lookup(tree[1], environment)

        if tag == "record":
            result = {}
            for name, expression in tree[1]:
                result[name] = self.visit(expression, environment)
            return result

        if tag == "field":
            record = self.visit(tree[1], environment)
            if not _is_record(record):
                raise MiniError("type")
            field = tree[2]
            if field not in record:
                raise MiniError("no_field")
            return record[field]

        if tag == "unary":
            op = tree[1]
            operand = self.visit(tree[2], environment)
            if op == "-":
                if not _is_int(operand):
                    raise MiniError("type")
                return -operand
            if op == "!":
                if not isinstance(operand, _Cell):
                    raise MiniError("type")
                return operand.value
            if op == "ref":
                return _Cell(operand)
            raise MiniError("type")

        if tag == "binary":
            op = tree[1]
            if op == "&&":
                left = self.visit(tree[2], environment)
                if not _is_bool(left):
                    raise MiniError("type")
                if not left:
                    return False
                right = self.visit(tree[3], environment)
                if not _is_bool(right):
                    raise MiniError("type")
                return right
            if op == "||":
                left = self.visit(tree[2], environment)
                if not _is_bool(left):
                    raise MiniError("type")
                if left:
                    return True
                right = self.visit(tree[3], environment)
                if not _is_bool(right):
                    raise MiniError("type")
                return right

            left = self.visit(tree[2], environment)
            right = self.visit(tree[3], environment)
            return self._binary(op, left, right)

        if tag == "assign":
            cell = self.visit(tree[1], environment)
            value = self.visit(tree[2], environment)
            if not isinstance(cell, _Cell):
                raise MiniError("type")
            cell.value = value
            return value

        if tag == "application":
            function = self.visit(tree[1], environment)
            argument = self.visit(tree[2], environment)
            if not isinstance(function, _Closure):
                raise MiniError("type")
            call_environment = _Environment({function.parameter: argument}, function.environment)
            return self.visit(function.body, call_environment)

        if tag == "let":
            value = self.visit(tree[2], environment)
            body_environment = _Environment({tree[1]: value}, environment)
            return self.visit(tree[3], body_environment)

        if tag == "letrec":
            frame = _Environment({}, environment)
            slots = {}
            for name, unused in tree[1]:
                slot = _Slot()
                frame.bindings[name] = slot
                slots[name] = slot
            for name, expression in tree[1]:
                value = self.visit(expression, frame)
                slot = slots[name]
                slot.value = value
                slot.initialized = True
            return self.visit(tree[2], frame)

        if tag == "if":
            condition = self.visit(tree[1], environment)
            if not _is_bool(condition):
                raise MiniError("type")
            if condition:
                return self.visit(tree[2], environment)
            return self.visit(tree[3], environment)

        if tag == "fun":
            return _Closure(tree[1], tree[2], environment)

        if tag == "match":
            subject = self.visit(tree[1], environment)
            for pattern, body in tree[2]:
                bindings = {}
                if self._matches(pattern, subject, bindings):
                    return self.visit(body, _Environment(bindings, environment))
            raise MiniError("no_match")

        raise MiniError("type")

    @staticmethod
    def _lookup(name, environment):
        current = environment
        while current is not None:
            if name in current.bindings:
                value = current.bindings[name]
                if isinstance(value, _Slot):
                    if not value.initialized:
                        raise MiniError("uninit")
                    return value.value
                return value
            current = current.parent
        raise MiniError("unbound")

    def _binary(self, op, left, right):
        if op == "+" or op == "-":
            if not _is_int(left) or not _is_int(right):
                raise MiniError("type")
            if op == "+":
                return left + right
            return left - right

        if op == "*":
            if _is_int(left):
                if not _is_int(right):
                    raise MiniError("type")
                return left * right
            if _is_str(left):
                if not _is_int(right):
                    raise MiniError("type")
                if right <= 0:
                    return ""
                return left * right
            raise MiniError("type")

        if op == "/" or op == "%":
            if not _is_int(left) or not _is_int(right):
                raise MiniError("type")
            if right == 0:
                raise MiniError("div_zero")
            if op == "/":
                return _truncating_quotient(left, right)
            return left % right

        if op == "++":
            if not _is_str(left):
                raise MiniError("type")
            if _is_str(right):
                rendered = right
            elif _is_int(right):
                rendered = _decimal_text(right)
            elif _is_bool(right):
                rendered = "true" if right else "false"
            else:
                raise MiniError("type")
            return left + rendered

        if op in ("<", "<=", ">", ">="):
            same_ints = _is_int(left) and _is_int(right)
            same_strings = _is_str(left) and _is_str(right)
            if not (same_ints or same_strings):
                raise MiniError("type")
            if op == "<":
                return left < right
            if op == "<=":
                return left <= right
            if op == ">":
                return left > right
            return left >= right

        if op == "==" or op == "!=":
            valid_primitives = (
                (_is_int(left) and _is_int(right))
                or (_is_str(left) and _is_str(right))
                or (_is_bool(left) and _is_bool(right))
            )
            valid_refs = isinstance(left, _Cell) and isinstance(right, _Cell)
            if not valid_primitives and not valid_refs:
                raise MiniError("type")
            if valid_refs:
                equal = left is right
            else:
                equal = left == right
            return equal if op == "==" else not equal

        raise MiniError("type")

    def _matches(self, pattern, value, bindings):
        tag = pattern[0]
        if tag == "wildcard":
            return True
        if tag == "pint":
            return _is_int(value) and value == pattern[1]
        if tag == "pstr":
            return _is_str(value) and value == pattern[1]
        if tag == "pbool":
            return _is_bool(value) and value == pattern[1]
        if tag == "pvariable":
            bindings[pattern[1]] = value
            return True
        if tag == "precord":
            if not _is_record(value):
                return False
            for name, nested in pattern[1]:
                if name not in value:
                    return False
                if not self._matches(nested, value[name], bindings):
                    return False
            return True
        return False


def _python_value(value):
    if _is_int(value) or _is_bool(value) or _is_str(value):
        return value
    if _is_record(value):
        result = {}
        for name, field_value in value.items():
            result[name] = _python_value(field_value)
        return result
    if isinstance(value, _Closure):
        return "<fn>"
    if isinstance(value, _Cell):
        return "<ref>"
    raise MiniError("type")


def run(source):
    if not isinstance(source, str):
        raise MiniError("parse")

    try:
        tokens = _Lexer(source).tokens()
        tree = _Parser(tokens).parse()
    except MiniError:
        raise
    except Exception:
        raise MiniError("parse")

    try:
        value = _Interpreter().visit(tree, _Environment())
        return _python_value(value)
    except MiniError:
        raise
    except Exception:
        raise MiniError("type")
