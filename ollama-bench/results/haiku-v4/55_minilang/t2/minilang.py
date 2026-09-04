"""
A minimal expression language interpreter.
"""


class MiniError(Exception):
    """Exception for minilang errors."""
    def __init__(self, kind):
        self.kind = kind
        super().__init__(f"MiniError({kind})")


# Lexer

class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r})"


def lex(source):
    """Tokenize the source code."""
    tokens = []
    i = 0

    while i < len(source):
        # Skip whitespace
        if source[i] in ' \t\r\n':
            i += 1
            continue

        # Integer literal
        if source[i] in '0123456789':
            if source[i] == '0':
                # Check for leading zero
                if i + 1 < len(source) and source[i + 1] in '0123456789':
                    raise MiniError("parse")
                tokens.append(Token("INT", 0))
                i += 1
            else:
                # Digit 1-9
                j = i
                while j < len(source) and source[j] in '0123456789':
                    j += 1
                tokens.append(Token("INT", int(source[i:j])))
                i = j
            continue

        # String literal
        if source[i] == '"':
            i += 1
            j = i
            while j < len(source) and source[j] != '"':
                if source[j] == '\\' or source[j] == '\n':
                    raise MiniError("parse")
                j += 1
            if j >= len(source):
                raise MiniError("parse")
            tokens.append(Token("STRING", source[i:j]))
            i = j + 1
            continue

        # Identifier or keyword
        if source[i].isalpha() or source[i] == '_':
            j = i
            while j < len(source) and (source[j].isalnum() or source[j] == '_'):
                j += 1
            word = source[i:j]

            # Check if all ASCII
            if not all(ord(c) < 128 for c in word):
                raise MiniError("parse")

            # Reserved words
            reserved = {'let', 'letrec', 'and', 'in', 'if', 'then', 'else',
                       'fun', 'match', 'with', 'end', 'ref', 'true', 'false'}

            if word == '_':
                tokens.append(Token("_", None))
            elif word in reserved:
                tokens.append(Token(word, None))
            else:
                tokens.append(Token("IDENT", word))
            i = j
            continue

        # Operators and punctuation
        # Longest match first
        if i + 2 < len(source):
            three = source[i:i+3]
            # No three-char operators

        if i + 1 < len(source):
            two = source[i:i+2]
            if two in ['->', ':=', '==', '!=', '<=', '>=', '&&', '||', '++']:
                tokens.append(Token(two, None))
                i += 2
                continue

        one = source[i]
        if one in '+-*/%<>=(){},.!|':
            tokens.append(Token(one, None))
            i += 1
            continue

        # Invalid character
        raise MiniError("parse")

    return tokens


# Parser

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        if self.pos < len(self.tokens):
            self.pos += 1

    def expect(self, kind):
        token = self.peek()
        if token is None or token.kind != kind:
            raise MiniError("parse")
        self.advance()
        return token

    def parse(self):
        expr = self.parse_expr()
        if self.peek() is not None:
            raise MiniError("parse")
        return expr

    def parse_expr(self):
        token = self.peek()
        if token is None:
            raise MiniError("parse")

        # let x = e1 in e2
        if token.kind == 'let':
            self.advance()
            name = self.expect("IDENT").value
            self.expect("=")
            e1 = self.parse_expr()
            self.expect("in")
            e2 = self.parse_expr()
            return ('let', name, e1, e2)

        # letrec x = e1 and ... and xn = en in body
        if token.kind == 'letrec':
            self.advance()
            bindings = []

            # First binding
            name = self.expect("IDENT").value
            self.expect("=")
            expr = self.parse_expr()
            bindings.append((name, expr))

            # Additional bindings
            while self.peek() and self.peek().kind == 'and':
                self.advance()
                name = self.expect("IDENT").value
                self.expect("=")
                expr = self.parse_expr()
                bindings.append((name, expr))

            # Check for duplicate bindings
            names = [b[0] for b in bindings]
            if len(names) != len(set(names)):
                raise MiniError("dup_binding")

            self.expect("in")
            body = self.parse_expr()
            return ('letrec', bindings, body)

        # if c then a else b
        if token.kind == 'if':
            self.advance()
            cond = self.parse_expr()
            self.expect("then")
            then_expr = self.parse_expr()
            self.expect("else")
            else_expr = self.parse_expr()
            return ('if', cond, then_expr, else_expr)

        # fun x -> e
        if token.kind == 'fun':
            self.advance()
            name = self.expect("IDENT").value
            self.expect("->")
            expr = self.parse_expr()
            return ('fun', name, expr)

        # match e with ... end
        if token.kind == 'match':
            self.advance()
            expr = self.parse_expr()
            self.expect("with")

            arms = []
            while self.peek() and self.peek().kind == '|':
                self.advance()
                pattern = self.parse_pattern()
                self.expect("->")
                arm_expr = self.parse_expr()
                arms.append((pattern, arm_expr))

            self.expect("end")
            return ('match', expr, arms)

        # Otherwise, parse assign
        return self.parse_assign()

    def parse_assign(self):
        lhs = self.parse_orx()

        if self.peek() and self.peek().kind == ':=':
            self.advance()
            rhs = self.parse_expr()
            return (':=', lhs, rhs)

        return lhs

    def parse_orx(self):
        left = self.parse_andx()

        while self.peek() and self.peek().kind == '||':
            self.advance()
            right = self.parse_andx()
            left = ('||', left, right)

        return left

    def parse_andx(self):
        left = self.parse_cmpx()

        while self.peek() and self.peek().kind == '&&':
            self.advance()
            right = self.parse_cmpx()
            left = ('&&', left, right)

        return left

    def parse_cmpx(self):
        left = self.parse_catx()

        if self.peek() and self.peek().kind in ['==', '!=', '<', '<=', '>', '>=']:
            op = self.peek().kind
            self.advance()
            right = self.parse_catx()
            return (op, left, right)

        return left

    def parse_catx(self):
        left = self.parse_addx()

        if self.peek() and self.peek().kind == '++':
            self.advance()
            right = self.parse_catx()
            return ('++', left, right)

        return left

    def parse_addx(self):
        left = self.parse_mulx()

        while self.peek() and self.peek().kind in ['+', '-']:
            op = self.peek().kind
            self.advance()
            right = self.parse_mulx()
            left = (op, left, right)

        return left

    def parse_mulx(self):
        left = self.parse_unary()

        while self.peek() and self.peek().kind in ['*', '/', '%']:
            op = self.peek().kind
            self.advance()
            right = self.parse_unary()
            left = (op, left, right)

        return left

    def parse_unary(self):
        token = self.peek()

        if token and token.kind in ['-', '!', 'ref']:
            op = token.kind
            self.advance()
            expr = self.parse_unary()
            return (op, expr)

        return self.parse_app()

    def parse_app(self):
        expr = self.parse_postfix()

        while True:
            token = self.peek()
            if token is None:
                break

            # Check if this is a postfix expression
            if not self._is_postfix_start(token):
                break

            arg = self.parse_postfix()
            expr = ('app', expr, arg)

        return expr

    def _is_postfix_start(self, token):
        """Check if a token can start a postfix expression (argument)."""
        if token is None:
            return False
        return token.kind in ['INT', 'STRING', 'true', 'false', 'IDENT', '(', '{']

    def parse_postfix(self):
        expr = self.parse_atom()

        while self.peek() and self.peek().kind == '.':
            self.advance()
            field = self.expect("IDENT").value
            expr = ('field', expr, field)

        return expr

    def parse_atom(self):
        token = self.peek()

        if token is None:
            raise MiniError("parse")

        if token.kind == 'INT':
            self.advance()
            return ('int', token.value)

        if token.kind == 'STRING':
            self.advance()
            return ('string', token.value)

        if token.kind == 'true':
            self.advance()
            return ('bool', True)

        if token.kind == 'false':
            self.advance()
            return ('bool', False)

        if token.kind == 'IDENT':
            name = token.value
            self.advance()
            return ('var', name)

        if token.kind == '(':
            self.advance()
            expr = self.parse_expr()
            self.expect(")")
            return expr

        if token.kind == '{':
            return self.parse_record()

        raise MiniError("parse")

    def parse_record(self):
        self.expect("{")
        fields = []

        if self.peek() and self.peek().kind != '}':
            # Parse first field
            name = self.expect("IDENT").value
            self.expect("=")
            expr = self.parse_expr()
            fields.append((name, expr))

            # Parse remaining fields
            while self.peek() and self.peek().kind == ',':
                self.advance()
                name = self.expect("IDENT").value
                self.expect("=")
                expr = self.parse_expr()
                fields.append((name, expr))

        self.expect("}")

        # Check for duplicate field names
        field_names = [f[0] for f in fields]
        if len(field_names) != len(set(field_names)):
            raise MiniError("dup_field")

        return ('record', fields)

    def parse_pattern(self):
        pattern = self._parse_pattern_impl()
        # Check for duplicate variables in the pattern
        vars_in_pattern = self._collect_pattern_vars(pattern)
        if len(vars_in_pattern) != len(set(vars_in_pattern)):
            raise MiniError("dup_binding")
        return pattern

    def _parse_pattern_impl(self):
        token = self.peek()

        if token is None:
            raise MiniError("parse")

        if token.kind == '_':
            self.advance()
            return ('_', None)

        if token.kind == 'INT':
            self.advance()
            return ('int', token.value)

        if token.kind == 'STRING':
            self.advance()
            return ('string', token.value)

        if token.kind == 'true':
            self.advance()
            return ('bool', True)

        if token.kind == 'false':
            self.advance()
            return ('bool', False)

        if token.kind == 'IDENT':
            name = token.value
            self.advance()
            return ('var', name)

        if token.kind == '{':
            return self.parse_record_pattern()

        raise MiniError("parse")

    def _collect_pattern_vars(self, pattern):
        """Collect all variables in a pattern."""
        if pattern[0] == '_':
            return []
        elif pattern[0] in ['int', 'string', 'bool']:
            return []
        elif pattern[0] == 'var':
            return [pattern[1]]
        elif pattern[0] == 'record':
            vars_list = []
            for _, fpat in pattern[1]:
                vars_list.extend(self._collect_pattern_vars(fpat))
            return vars_list
        return []

    def parse_record_pattern(self):
        self.expect("{")
        fields = []

        if self.peek() and self.peek().kind != '}':
            # Parse first field
            name = self.expect("IDENT").value
            self.expect("=")
            pattern = self._parse_pattern_impl()
            fields.append((name, pattern))

            # Parse remaining fields
            while self.peek() and self.peek().kind == ',':
                self.advance()
                name = self.expect("IDENT").value
                self.expect("=")
                pattern = self._parse_pattern_impl()
                fields.append((name, pattern))

        self.expect("}")

        # Check for duplicate field names
        field_names = [f[0] for f in fields]
        if len(field_names) != len(set(field_names)):
            raise MiniError("dup_field")

        return ('record', fields)


# Evaluator

class Evaluator:
    def __init__(self):
        self.env = {}
        self.refs = {}
        self.next_ref_id = 0

    def eval(self, expr, env=None):
        if env is None:
            env = {}

        if isinstance(expr, tuple):
            if expr[0] == 'int':
                return expr[1]

            elif expr[0] == 'string':
                return expr[1]

            elif expr[0] == 'bool':
                return expr[1]

            elif expr[0] == 'var':
                name = expr[1]
                if name not in env:
                    raise MiniError("unbound")
                value = env[name]
                if value is _UNINIT:
                    raise MiniError("uninit")
                return value

            elif expr[0] == 'record':
                fields = expr[1]
                result = {}
                for fname, fexpr in fields:
                    result[fname] = self.eval(fexpr, env)
                return result

            elif expr[0] == 'field':
                obj_expr = expr[1]
                field_name = expr[2]
                obj = self.eval(obj_expr, env)
                if not isinstance(obj, dict):
                    raise MiniError("type")
                if field_name not in obj:
                    raise MiniError("no_field")
                return obj[field_name]

            elif expr[0] == 'fun':
                param = expr[1]
                body = expr[2]
                return ('closure', param, body, env)

            elif expr[0] == 'let':
                name = expr[1]
                e1 = expr[2]
                e2 = expr[3]
                val = self.eval(e1, env)
                new_env = env.copy()
                new_env[name] = val
                return self.eval(e2, new_env)

            elif expr[0] == 'letrec':
                bindings = expr[1]
                body = expr[2]

                # Create a new environment with all names bound to UNINIT
                new_env = env.copy()
                for name, _ in bindings:
                    new_env[name] = _UNINIT

                # Evaluate each binding and store the result
                for name, val_expr in bindings:
                    val = self.eval(val_expr, new_env)
                    new_env[name] = val

                return self.eval(body, new_env)

            elif expr[0] == 'if':
                cond = expr[1]
                then_expr = expr[2]
                else_expr = expr[3]

                cond_val = self.eval(cond, env)
                if not isinstance(cond_val, bool):
                    raise MiniError("type")

                if cond_val:
                    return self.eval(then_expr, env)
                else:
                    return self.eval(else_expr, env)

            elif expr[0] == 'match':
                value_expr = expr[1]
                arms = expr[2]

                value = self.eval(value_expr, env)

                for pattern, arm_expr in arms:
                    bindings = self._match_pattern(pattern, value)
                    if bindings is not None:
                        new_env = env.copy()
                        new_env.update(bindings)
                        return self.eval(arm_expr, new_env)

                raise MiniError("no_match")

            elif expr[0] == 'app':
                func_expr = expr[1]
                arg_expr = expr[2]

                func = self.eval(func_expr, env)
                arg = self.eval(arg_expr, env)

                if not isinstance(func, tuple) or func[0] != 'closure':
                    raise MiniError("type")

                _, param, body, closure_env = func
                call_env = closure_env.copy()
                call_env[param] = arg
                return self.eval(body, call_env)

            elif expr[0] == '+':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)
                if isinstance(left, bool) or isinstance(right, bool) or not isinstance(left, int) or not isinstance(right, int):
                    raise MiniError("type")
                return left + right

            elif expr[0] == '-':
                # Could be unary or binary
                if len(expr) == 2:
                    # Unary minus
                    val = self.eval(expr[1], env)
                    if isinstance(val, bool) or not isinstance(val, int):
                        raise MiniError("type")
                    return -val
                else:
                    # Binary minus
                    left = self.eval(expr[1], env)
                    right = self.eval(expr[2], env)
                    if isinstance(left, bool) or isinstance(right, bool) or not isinstance(left, int) or not isinstance(right, int):
                        raise MiniError("type")
                    return left - right

            elif expr[0] == '*':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)

                if isinstance(left, str):
                    if isinstance(right, bool) or not isinstance(right, int):
                        raise MiniError("type")
                    if right <= 0:
                        return ""
                    return left * right
                elif isinstance(left, int) and not isinstance(left, bool):
                    if isinstance(right, bool) or not isinstance(right, int):
                        raise MiniError("type")
                    return left * right
                else:
                    raise MiniError("type")

            elif expr[0] == '/':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)
                if isinstance(left, bool) or isinstance(right, bool) or not isinstance(left, int) or not isinstance(right, int):
                    raise MiniError("type")
                if right == 0:
                    raise MiniError("div_zero")
                # Truncate toward zero
                return int(left / right)

            elif expr[0] == '%':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)
                if isinstance(left, bool) or isinstance(right, bool) or not isinstance(left, int) or not isinstance(right, int):
                    raise MiniError("type")
                if right == 0:
                    raise MiniError("div_zero")
                # Floored remainder
                return left - (left // right) * right

            elif expr[0] == '++':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)

                if not isinstance(left, str):
                    raise MiniError("type")

                if isinstance(right, str):
                    return left + right
                elif isinstance(right, int):
                    return left + str(right)
                elif isinstance(right, bool):
                    return left + ("true" if right else "false")
                else:
                    raise MiniError("type")

            elif expr[0] == '==':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)

                # Can compare: int (not bool), str, bool, ref
                if isinstance(left, bool) and isinstance(right, bool):
                    return left == right
                elif isinstance(left, int) and not isinstance(left, bool) and isinstance(right, int) and not isinstance(right, bool):
                    return left == right
                elif isinstance(left, str) and isinstance(right, str):
                    return left == right
                elif isinstance(left, tuple) and left[0] == 'ref' and isinstance(right, tuple) and right[0] == 'ref':
                    return left[1] == right[1]
                else:
                    raise MiniError("type")

            elif expr[0] == '!=':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)

                if isinstance(left, bool) and isinstance(right, bool):
                    return left != right
                elif isinstance(left, int) and not isinstance(left, bool) and isinstance(right, int) and not isinstance(right, bool):
                    return left != right
                elif isinstance(left, str) and isinstance(right, str):
                    return left != right
                elif isinstance(left, tuple) and left[0] == 'ref' and isinstance(right, tuple) and right[0] == 'ref':
                    return left[1] != right[1]
                else:
                    raise MiniError("type")

            elif expr[0] == '<':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)

                if isinstance(left, int) and not isinstance(left, bool) and isinstance(right, int) and not isinstance(right, bool):
                    return left < right
                elif isinstance(left, str) and isinstance(right, str):
                    return left < right
                else:
                    raise MiniError("type")

            elif expr[0] == '<=':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)

                if isinstance(left, int) and not isinstance(left, bool) and isinstance(right, int) and not isinstance(right, bool):
                    return left <= right
                elif isinstance(left, str) and isinstance(right, str):
                    return left <= right
                else:
                    raise MiniError("type")

            elif expr[0] == '>':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)

                if isinstance(left, int) and not isinstance(left, bool) and isinstance(right, int) and not isinstance(right, bool):
                    return left > right
                elif isinstance(left, str) and isinstance(right, str):
                    return left > right
                else:
                    raise MiniError("type")

            elif expr[0] == '>=':
                left = self.eval(expr[1], env)
                right = self.eval(expr[2], env)

                if isinstance(left, int) and not isinstance(left, bool) and isinstance(right, int) and not isinstance(right, bool):
                    return left >= right
                elif isinstance(left, str) and isinstance(right, str):
                    return left >= right
                else:
                    raise MiniError("type")

            elif expr[0] == '&&':
                left = self.eval(expr[1], env)
                if not isinstance(left, bool):
                    raise MiniError("type")
                if not left:
                    return False
                right = self.eval(expr[2], env)
                if not isinstance(right, bool):
                    raise MiniError("type")
                return right

            elif expr[0] == '||':
                left = self.eval(expr[1], env)
                if not isinstance(left, bool):
                    raise MiniError("type")
                if left:
                    return True
                right = self.eval(expr[2], env)
                if not isinstance(right, bool):
                    raise MiniError("type")
                return right

            elif expr[0] == '!':
                # Dereference
                val = self.eval(expr[1], env)
                if not isinstance(val, tuple) or val[0] != 'ref':
                    raise MiniError("type")
                ref_id = val[1]
                return self.refs[ref_id]

            elif expr[0] == 'ref':
                # Allocate a ref
                val = self.eval(expr[1], env)
                ref_id = self.next_ref_id
                self.next_ref_id += 1
                self.refs[ref_id] = val
                return ('ref', ref_id)

            elif expr[0] == ':=':
                # Assignment
                lhs = self.eval(expr[1], env)
                rhs = self.eval(expr[2], env)

                if not isinstance(lhs, tuple) or lhs[0] != 'ref':
                    raise MiniError("type")

                ref_id = lhs[1]
                self.refs[ref_id] = rhs
                return rhs

        raise MiniError("parse")

    def _match_pattern(self, pattern, value):
        """Try to match a pattern against a value. Returns a dict of bindings if successful, None if not."""
        if pattern[0] == '_':
            return {}

        elif pattern[0] == 'int':
            if isinstance(value, int) and value == pattern[1]:
                return {}
            return None

        elif pattern[0] == 'string':
            if isinstance(value, str) and value == pattern[1]:
                return {}
            return None

        elif pattern[0] == 'bool':
            if isinstance(value, bool) and value == pattern[1]:
                return {}
            return None

        elif pattern[0] == 'var':
            return {pattern[1]: value}

        elif pattern[0] == 'record':
            if not isinstance(value, dict):
                return None

            bindings = {}
            for fname, fpat in pattern[1]:
                if fname not in value:
                    return None

                sub_bindings = self._match_pattern(fpat, value[fname])
                if sub_bindings is None:
                    return None

                # Check for duplicate bindings
                for key in sub_bindings:
                    if key in bindings:
                        raise MiniError("dup_binding")

                bindings.update(sub_bindings)

            return bindings

        return None


# Sentinel for uninitialized values
class _Uninit:
    pass

_UNINIT = _Uninit()


def _convert_result(value):
    """Convert a value to Python types for the result."""
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        return value
    elif isinstance(value, bool):
        return value
    elif isinstance(value, dict):
        return {k: _convert_result(v) for k, v in value.items()}
    elif isinstance(value, tuple):
        if value[0] == 'closure':
            return "<fn>"
        elif value[0] == 'ref':
            return "<ref>"

    return value


def run(source):
    """Parse and evaluate a minilang expression."""
    # Check for empty or whitespace-only source
    if not source or source.isspace():
        raise MiniError("parse")

    # Lex
    tokens = lex(source)

    if not tokens:
        raise MiniError("parse")

    # Parse
    parser = Parser(tokens)
    ast = parser.parse()

    # Evaluate
    evaluator = Evaluator()
    result = evaluator.eval(ast)

    # Convert and return
    return _convert_result(result)
