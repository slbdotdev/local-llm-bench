"""A small, hand-written expression-language interpreter."""


_ERROR_KINDS = {
    "parse",
    "dup_field",
    "dup_binding",
    "unbound",
    "uninit",
    "type",
    "div_zero",
    "no_field",
    "no_match",
}


class MiniError(Exception):
    """An error reported by the lexer, parser, or evaluator."""

    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind)


class _Token:
    __slots__ = ("kind", "value", "position")

    def __init__(self, kind, value=None, position=0):
        self.kind = kind
        self.value = value
        self.position = position


class _Lexer:
    _WORDS = {
        "let": "LET",
        "letrec": "LETREC",
        "and": "AND",
        "in": "IN",
        "if": "IF",
        "then": "THEN",
        "else": "ELSE",
        "fun": "FUN",
        "match": "MATCH",
        "with": "WITH",
        "end": "END",
        "ref": "REF",
        "true": "TRUE",
        "false": "FALSE",
    }

    _TWO_CHAR = {
        "->": "ARROW",
        ":=": "ASSIGN",
        "==": "EQ",
        "!=": "NE",
        "<=": "LE",
        ">=": "GE",
        "&&": "ANDAND",
        "||": "OROR",
        "++": "CONCAT",
    }

    _ONE_CHAR = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "STAR",
        "/": "SLASH",
        "%": "PERCENT",
        "<": "LT",
        ">": "GT",
        "=": "EQUAL",
        "(": "LPAREN",
        ")": "RPAREN",
        "{": "LBRACE",
        "}": "RBRACE",
        ",": "COMMA",
        ".": "DOT",
        "|": "BAR",
        "!": "BANG",
    }

    @staticmethod
    def _is_digit(char):
        return "0" <= char <= "9"

    @staticmethod
    def _is_letter(char):
        return ("A" <= char <= "Z") or ("a" <= char <= "z")

    def __init__(self, source):
        self.source = source
        self.length = len(source)
        self.index = 0

    def tokens(self):
        result = []
        while self.index < self.length:
            char = self.source[self.index]
            if char in " \t\r\n":
                self.index += 1
                continue

            position = self.index
            if self._is_digit(char):
                result.append(self._integer(position))
                continue

            if char == '"':
                result.append(self._string(position))
                continue

            if self._is_letter(char) or char == "_":
                result.append(self._identifier(position))
                continue

            pair = self.source[self.index : self.index + 2]
            if pair in self._TWO_CHAR:
                result.append(_Token(self._TWO_CHAR[pair], pair, position))
                self.index += 2
                continue

            kind = self._ONE_CHAR.get(char)
            if kind is not None:
                result.append(_Token(kind, char, position))
                self.index += 1
                continue

            raise MiniError("parse")

        result.append(_Token("EOF", position=self.length))
        return result

    def _integer(self, position):
        start = self.index
        if self.source[self.index] == "0":
            self.index += 1
            if self.index < self.length and self._is_digit(self.source[self.index]):
                while self.index < self.length and self._is_digit(self.source[self.index]):
                    self.index += 1
                raise MiniError("parse")
            return _Token("INT", 0, position)

        value = 0
        while self.index < self.length and self._is_digit(self.source[self.index]):
            value = value * 10 + (ord(self.source[self.index]) - ord("0"))
            self.index += 1
        return _Token("INT", value, position)

    def _string(self, position):
        self.index += 1
        start = self.index
        pieces = []
        while self.index < self.length:
            char = self.source[self.index]
            if char == '"':
                if pieces:
                    pieces.append(self.source[start : self.index])
                    value = "".join(pieces)
                else:
                    value = self.source[start : self.index]
                self.index += 1
                return _Token("STRING", value, position)
            if char == "\\" or char == "\n" or char == "\r":
                raise MiniError("parse")
            self.index += 1

        raise MiniError("parse")

    def _identifier(self, position):
        start = self.index
        self.index += 1
        while self.index < self.length:
            char = self.source[self.index]
            if self._is_letter(char) or self._is_digit(char) or char == "_":
                self.index += 1
            else:
                break
        text = self.source[start : self.index]
        if text == "_":
            return _Token("UNDERSCORE", text, position)
        return _Token(self._WORDS.get(text, "IDENT"), text, position)


def _node(kind, *parts):
    return (kind,) + parts


class _Parser:
    _COMPARISONS = {"EQ", "NE", "LT", "LE", "GT", "GE"}
    _POSTFIX_START = {"INT", "STRING", "TRUE", "FALSE", "IDENT", "LPAREN", "LBRACE"}

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def current(self):
        return self.tokens[self.index]

    def at(self, kind):
        return self.current().kind == kind

    def accept(self, kind):
        if self.at(kind):
            token = self.current()
            self.index += 1
            return token
        return None

    def expect(self, kind):
        token = self.accept(kind)
        if token is None:
            raise MiniError("parse")
        return token

    def parse(self):
        expression = self.parse_expr()
        self.expect("EOF")
        return expression

    def parse_expr(self):
        if self.accept("LET") is not None:
            return self.parse_let()
        if self.accept("LETREC") is not None:
            return self.parse_letrec()
        if self.accept("IF") is not None:
            return self.parse_if()
        if self.accept("FUN") is not None:
            return self.parse_fun()
        if self.accept("MATCH") is not None:
            return self.parse_match()
        return self.parse_assign()

    def parse_let(self):
        name = self.expect("IDENT").value
        self.expect("EQUAL")
        value = self.parse_expr()
        self.expect("IN")
        body = self.parse_expr()
        return _node("let", name, value, body)

    def parse_letrec(self):
        bindings = []
        names = []
        while True:
            name = self.expect("IDENT").value
            self.expect("EQUAL")
            value = self.parse_expr()
            names.append(name)
            bindings.append((name, value))
            if self.accept("AND") is None:
                break

        self.expect("IN")
        body = self.parse_expr()

        # This check deliberately happens after the body has been parsed.
        if len(names) != len(set(names)):
            raise MiniError("dup_binding")
        return _node("letrec", tuple(bindings), body)

    def parse_if(self):
        condition = self.parse_expr()
        self.expect("THEN")
        yes = self.parse_expr()
        self.expect("ELSE")
        no = self.parse_expr()
        return _node("if", condition, yes, no)

    def parse_fun(self):
        parameter = self.expect("IDENT").value
        self.expect("ARROW")
        body = self.parse_expr()
        return _node("fun", parameter, body)

    def parse_match(self):
        subject = self.parse_expr()
        self.expect("WITH")
        arms = []
        if not self.at("BAR"):
            raise MiniError("parse")
        while self.accept("BAR") is not None:
            pattern, names = self.parse_pattern()
            if len(names) != len(set(names)):
                raise MiniError("dup_binding")
            self.expect("ARROW")
            body = self.parse_expr()
            arms.append((pattern, body))
        self.expect("END")
        return _node("match", subject, tuple(arms))

    def parse_assign(self):
        left = self.parse_or()
        if self.accept("ASSIGN") is not None:
            right = self.parse_expr()
            return _node("assign", left, right)
        return left

    def parse_or(self):
        expression = self.parse_and()
        while self.accept("OROR") is not None:
            expression = _node("binary", "||", expression, self.parse_and())
        return expression

    def parse_and(self):
        expression = self.parse_compare()
        while self.accept("ANDAND") is not None:
            expression = _node("binary", "&&", expression, self.parse_compare())
        return expression

    def parse_compare(self):
        expression = self.parse_concat()
        if self.current().kind in self._COMPARISONS:
            operator = self.current().value
            self.index += 1
            expression = _node("binary", operator, expression, self.parse_concat())
        return expression

    def parse_concat(self):
        left = self.parse_add()
        if self.accept("CONCAT") is not None:
            return _node("binary", "++", left, self.parse_concat())
        return left

    def parse_add(self):
        expression = self.parse_multiply()
        while self.current().kind in {"PLUS", "MINUS"}:
            operator = self.current().value
            self.index += 1
            expression = _node("binary", operator, expression, self.parse_multiply())
        return expression

    def parse_multiply(self):
        expression = self.parse_unary()
        while self.current().kind in {"STAR", "SLASH", "PERCENT"}:
            operator = self.current().value
            self.index += 1
            expression = _node("binary", operator, expression, self.parse_unary())
        return expression

    def parse_unary(self):
        if self.at("MINUS") or self.at("BANG") or self.at("REF"):
            operator = self.current().value if not self.at("REF") else "ref"
            self.index += 1
            return _node("unary", operator, self.parse_unary())
        return self.parse_application()

    def parse_application(self):
        expression = self.parse_postfix()
        while self.current().kind in self._POSTFIX_START:
            expression = _node("apply", expression, self.parse_postfix())
        return expression

    def parse_postfix(self):
        expression = self.parse_atom()
        while self.accept("DOT") is not None:
            field = self.expect("IDENT").value
            expression = _node("field", expression, field)
        return expression

    def parse_atom(self):
        token = self.current()
        if token.kind == "INT":
            self.index += 1
            return _node("int", token.value)
        if token.kind == "STRING":
            self.index += 1
            return _node("str", token.value)
        if token.kind == "TRUE" or token.kind == "FALSE":
            self.index += 1
            return _node("bool", token.kind == "TRUE")
        if token.kind == "IDENT":
            self.index += 1
            return _node("var", token.value)
        if self.accept("LPAREN") is not None:
            expression = self.parse_expr()
            self.expect("RPAREN")
            return expression
        if self.accept("LBRACE") is not None:
            return self.parse_record()
        raise MiniError("parse")

    def parse_record(self):
        fields = []
        names = []
        if not self.at("RBRACE"):
            while True:
                name = self.expect("IDENT").value
                self.expect("EQUAL")
                fields.append((name, self.parse_expr()))
                names.append(name)
                if self.accept("COMMA") is None:
                    break
        self.expect("RBRACE")
        # The closing brace is intentionally consumed before this check.
        if len(names) != len(set(names)):
            raise MiniError("dup_field")
        return _node("record", tuple(fields))

    def parse_pattern(self):
        token = self.current()
        if token.kind == "UNDERSCORE":
            self.index += 1
            return _node("p_wild"), []
        if token.kind == "INT":
            self.index += 1
            return _node("p_int", token.value), []
        if token.kind == "STRING":
            self.index += 1
            return _node("p_str", token.value), []
        if token.kind == "TRUE" or token.kind == "FALSE":
            self.index += 1
            return _node("p_bool", token.kind == "TRUE"), []
        if token.kind == "IDENT":
            self.index += 1
            return _node("p_var", token.value), [token.value]
        if self.accept("LBRACE") is not None:
            return self.parse_record_pattern()
        raise MiniError("parse")

    def parse_record_pattern(self):
        fields = []
        names = []
        if not self.at("RBRACE"):
            while True:
                field = self.expect("IDENT").value
                self.expect("EQUAL")
                pattern, pattern_names = self.parse_pattern()
                fields.append((field, pattern))
                names.extend(pattern_names)
                if self.accept("COMMA") is None:
                    break
        self.expect("RBRACE")
        field_names = [field for field, _ in fields]
        if len(field_names) != len(set(field_names)):
            raise MiniError("dup_field")
        return _node("p_record", tuple(fields)), names


class _Slot:
    __slots__ = ("initialized", "value")

    def __init__(self):
        self.initialized = False
        self.value = None


class _Environment:
    __slots__ = ("parent", "bindings")

    def __init__(self, parent=None, bindings=None):
        self.parent = parent
        self.bindings = {} if bindings is None else bindings

    def lookup(self, name):
        environment = self
        while environment is not None:
            if name in environment.bindings:
                value = environment.bindings[name]
                if isinstance(value, _Slot):
                    if not value.initialized:
                        raise MiniError("uninit")
                    return value.value
                return value
            environment = environment.parent
        raise MiniError("unbound")


class _Closure:
    __slots__ = ("parameter", "body", "environment")

    def __init__(self, parameter, body, environment):
        self.parameter = parameter
        self.body = body
        self.environment = environment


class _Cell:
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value


def _is_int(value):
    return type(value) is int


def _is_bool(value):
    return type(value) is bool


def _is_string(value):
    return type(value) is str


def _is_record(value):
    return type(value) is dict


class _Evaluator:
    def evaluate(self, expression, environment):
        kind = expression[0]

        if kind == "int" or kind == "str" or kind == "bool":
            return expression[1]
        if kind == "var":
            return environment.lookup(expression[1])
        if kind == "record":
            result = {}
            for name, value_expression in expression[1]:
                result[name] = self.evaluate(value_expression, environment)
            return result
        if kind == "field":
            record = self.evaluate(expression[1], environment)
            if not _is_record(record):
                raise MiniError("type")
            name = expression[2]
            if name not in record:
                raise MiniError("no_field")
            return record[name]
        if kind == "fun":
            return _Closure(expression[1], expression[2], environment)
        if kind == "apply":
            function = self.evaluate(expression[1], environment)
            argument = self.evaluate(expression[2], environment)
            if not isinstance(function, _Closure):
                raise MiniError("type")
            function_environment = _Environment(
                function.environment, {function.parameter: argument}
            )
            return self.evaluate(function.body, function_environment)
        if kind == "let":
            value = self.evaluate(expression[2], environment)
            body_environment = _Environment(environment, {expression[1]: value})
            return self.evaluate(expression[3], body_environment)
        if kind == "letrec":
            return self._evaluate_letrec(expression, environment)
        if kind == "if":
            condition = self.evaluate(expression[1], environment)
            if not _is_bool(condition):
                raise MiniError("type")
            branch = expression[2] if condition else expression[3]
            return self.evaluate(branch, environment)
        if kind == "match":
            return self._evaluate_match(expression, environment)
        if kind == "assign":
            target = self.evaluate(expression[1], environment)
            value = self.evaluate(expression[2], environment)
            if not isinstance(target, _Cell):
                raise MiniError("type")
            target.value = value
            return value
        if kind == "unary":
            return self._evaluate_unary(expression, environment)
        if kind == "binary":
            return self._evaluate_binary(expression, environment)

        raise MiniError("type")

    def _evaluate_letrec(self, expression, environment):
        bindings = expression[1]
        slots = {name: _Slot() for name, _ in bindings}
        recursive_environment = _Environment(environment, slots)
        for name, value_expression in bindings:
            value = self.evaluate(value_expression, recursive_environment)
            slot = slots[name]
            slot.value = value
            slot.initialized = True
        return self.evaluate(expression[2], recursive_environment)

    def _evaluate_match(self, expression, environment):
        value = self.evaluate(expression[1], environment)
        for pattern, body in expression[2]:
            matched, bindings = self._match_pattern(pattern, value)
            if matched:
                arm_environment = _Environment(environment, bindings)
                return self.evaluate(body, arm_environment)
        raise MiniError("no_match")

    def _match_pattern(self, pattern, value):
        kind = pattern[0]
        if kind == "p_wild":
            return True, {}
        if kind == "p_var":
            return True, {pattern[1]: value}
        if kind == "p_int":
            return _is_int(value) and value == pattern[1], {}
        if kind == "p_str":
            return _is_string(value) and value == pattern[1], {}
        if kind == "p_bool":
            return _is_bool(value) and value == pattern[1], {}
        if kind == "p_record":
            if not _is_record(value):
                return False, {}
            bindings = {}
            for name, subpattern in pattern[1]:
                if name not in value:
                    return False, {}
                matched, subbindings = self._match_pattern(subpattern, value[name])
                if not matched:
                    return False, {}
                bindings.update(subbindings)
            return True, bindings
        return False, {}

    def _evaluate_unary(self, expression, environment):
        operator = expression[1]
        value = self.evaluate(expression[2], environment)
        if operator == "-":
            if not _is_int(value):
                raise MiniError("type")
            return -value
        if operator == "!":
            if not isinstance(value, _Cell):
                raise MiniError("type")
            return value.value
        if operator == "ref":
            return _Cell(value)
        raise MiniError("type")

    def _evaluate_binary(self, expression, environment):
        operator = expression[1]
        left = self.evaluate(expression[2], environment)

        if operator == "&&":
            if not _is_bool(left):
                raise MiniError("type")
            if not left:
                return False
            right = self.evaluate(expression[3], environment)
            if not _is_bool(right):
                raise MiniError("type")
            return right

        if operator == "||":
            if not _is_bool(left):
                raise MiniError("type")
            if left:
                return True
            right = self.evaluate(expression[3], environment)
            if not _is_bool(right):
                raise MiniError("type")
            return right

        # All other binary operators evaluate both operands before checking types.
        right = self.evaluate(expression[3], environment)

        if operator in {"+", "-"}:
            if not _is_int(left) or not _is_int(right):
                raise MiniError("type")
            return left + right if operator == "+" else left - right

        if operator == "*":
            if _is_int(left) and _is_int(right):
                return left * right
            if _is_string(left) and _is_int(right):
                return "" if right <= 0 else left * right
            raise MiniError("type")

        if operator == "/" or operator == "%":
            if not _is_int(left) or not _is_int(right):
                raise MiniError("type")
            if right == 0:
                raise MiniError("div_zero")
            if operator == "/":
                quotient = abs(left) // abs(right)
                if (left < 0) != (right < 0):
                    quotient = -quotient
                return quotient
            return left % right

        if operator == "++":
            if not _is_string(left):
                raise MiniError("type")
            if _is_string(right):
                suffix = right
            elif _is_int(right):
                suffix = _integer_text(right)
            elif _is_bool(right):
                suffix = "true" if right else "false"
            else:
                raise MiniError("type")
            return left + suffix

        if operator in {"<", "<=", ">", ">="}:
            same_ints = _is_int(left) and _is_int(right)
            same_strings = _is_string(left) and _is_string(right)
            if not same_ints and not same_strings:
                raise MiniError("type")
            if operator == "<":
                return left < right
            if operator == "<=":
                return left <= right
            if operator == ">":
                return left > right
            return left >= right

        if operator == "==" or operator == "!=":
            if _is_int(left) and _is_int(right):
                equal = left == right
            elif _is_string(left) and _is_string(right):
                equal = left == right
            elif _is_bool(left) and _is_bool(right):
                equal = left == right
            elif isinstance(left, _Cell) and isinstance(right, _Cell):
                equal = left is right
            else:
                raise MiniError("type")
            return equal if operator == "==" else not equal

        raise MiniError("type")


def _integer_text(value):
    if value == 0:
        return "0"
    negative = value < 0
    number = -value if negative else value
    digits = []
    while number:
        number, digit = divmod(number, 10)
        digits.append(chr(ord("0") + digit))
    if negative:
        digits.append("-")
    digits.reverse()
    return "".join(digits)


def _convert(value):
    if _is_int(value) or _is_bool(value) or _is_string(value):
        return value
    if _is_record(value):
        return {name: _convert(field_value) for name, field_value in value.items()}
    if isinstance(value, _Closure):
        return "<fn>"
    if isinstance(value, _Cell):
        return "<ref>"
    raise MiniError("type")


def run(source):
    """Parse and evaluate exactly one expression from *source*."""
    if not isinstance(source, str):
        raise MiniError("parse")
    try:
        tokens = _Lexer(source).tokens()
        expression = _Parser(tokens).parse()
        value = _Evaluator().evaluate(expression, _Environment())
        return _convert(value)
    except MiniError:
        raise
    except Exception:
        # No implementation detail should escape as an interpreter error.
        raise MiniError("parse")


__all__ = ["MiniError", "run"]
