"""Minilang interpreter - lexer, parser, and evaluator."""

class MiniError(Exception):
    """Exception for minilang errors."""
    def __init__(self, kind):
        self.kind = kind
        super().__init__(f"MiniError: {kind}")


# ============================================================================
# LEXER
# ============================================================================

class Token:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r})"


def lex(source):
    """Tokenize source into a list of tokens."""
    tokens = []
    i = 0
    n = len(source)

    keywords = {
        'let', 'letrec', 'and', 'in', 'if', 'then', 'else', 'fun', 'match',
        'with', 'end', 'ref', 'true', 'false'
    }

    while i < n:
        # Skip whitespace
        if source[i] in ' \t\r\n':
            i += 1
            continue

        # Integer literal
        if source[i].isdigit():
            if source[i] == '0':
                if i + 1 < n and source[i + 1].isdigit():
                    raise MiniError("parse")  # Leading zero
                tokens.append(Token('INT', 0))
                i += 1
            else:
                start = i
                while i < n and source[i].isdigit():
                    if not source[i].isascii() or not source[i].isdigit():
                        raise MiniError("parse")
                    i += 1
                value = int(source[start:i])
                tokens.append(Token('INT', value))
            continue

        # String literal
        if source[i] == '"':
            i += 1
            start = i
            while i < n and source[i] != '"':
                if source[i] == '\\' or source[i] == '\n':
                    raise MiniError("parse")
                i += 1
            if i >= n:
                raise MiniError("parse")  # Unterminated string
            value = source[start:i]
            tokens.append(Token('STRING', value))
            i += 1
            continue

        # Identifier or keyword
        if source[i].isalpha() or source[i] == '_':
            if not source[i].isascii():
                raise MiniError("parse")
            start = i
            while i < n and (source[i].isalnum() or source[i] == '_'):
                if not source[i].isascii():
                    raise MiniError("parse")
                i += 1
            word = source[start:i]
            if word == '_':
                tokens.append(Token('WILDCARD', '_'))
            elif word in keywords:
                tokens.append(Token(word.upper(), word))
            else:
                tokens.append(Token('IDENT', word))
            continue

        # Operators and punctuation (longest-first matching)
        if i + 2 < n:
            three = source[i:i + 3]
            if three == '->':
                raise MiniError("parse")  # '->' is 2 chars, not 3

        if i + 1 < n:
            two = source[i:i + 2]
            if two in ['->', ':=', '==', '!=', '<=', '>=', '&&', '||', '++']:
                tokens.append(Token(two, two))
                i += 2
                continue

        # Single character operators
        char = source[i]
        if char in '+-*/%<>=(){},.| !':
            tokens.append(Token(char, char))
            i += 1
            continue

        # Any other character is an error
        raise MiniError("parse")

    if not tokens:
        raise MiniError("parse")  # Empty source

    return tokens


# ============================================================================
# PARSER
# ============================================================================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self, offset=1):
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def advance(self):
        self.pos += 1

    def expect(self, kind):
        token = self.current()
        if not token or token.kind != kind:
            raise MiniError("parse")
        self.advance()
        return token

    def match(self, *kinds):
        token = self.current()
        if token and token.kind in kinds:
            self.advance()
            return token
        return None

    def at_end(self):
        return self.current() is None

    def parse(self):
        expr = self.parse_expr()
        if not self.at_end():
            raise MiniError("parse")
        return expr

    def parse_expr(self):
        """Parse a top-level expression."""
        # Handle let, letrec, if, fun, match
        token = self.current()

        if token and token.kind == 'LET':
            return self.parse_let()

        if token and token.kind == 'LETREC':
            return self.parse_letrec()

        if token and token.kind == 'IF':
            return self.parse_if()

        if token and token.kind == 'FUN':
            return self.parse_fun()

        if token and token.kind == 'MATCH':
            return self.parse_match()

        return self.parse_assign()

    def parse_let(self):
        """Parse: let IDENT = expr in expr"""
        self.expect('LET')
        name_token = self.expect('IDENT')
        name = name_token.value
        self.expect('=')
        value = self.parse_expr()
        self.expect('IN')
        body = self.parse_expr()
        return ('let', name, value, body)

    def parse_letrec(self):
        """Parse: letrec IDENT = expr { and IDENT = expr } in expr"""
        self.expect('LETREC')
        bindings = []

        # Parse first binding
        name_token = self.expect('IDENT')
        name = name_token.value
        self.expect('=')
        value = self.parse_expr()
        bindings.append((name, value))

        # Parse additional bindings
        while self.match('AND'):
            name_token = self.expect('IDENT')
            name = name_token.value
            self.expect('=')
            value = self.parse_expr()
            bindings.append((name, value))

        self.expect('IN')
        body = self.parse_expr()

        # Check for duplicate names
        names = [name for name, _ in bindings]
        if len(names) != len(set(names)):
            raise MiniError("dup_binding")

        return ('letrec', bindings, body)

    def parse_if(self):
        """Parse: if expr then expr else expr"""
        self.expect('IF')
        cond = self.parse_expr()
        self.expect('THEN')
        then_e = self.parse_expr()
        self.expect('ELSE')
        else_e = self.parse_expr()
        return ('if', cond, then_e, else_e)

    def parse_fun(self):
        """Parse: fun IDENT -> expr"""
        self.expect('FUN')
        name_token = self.expect('IDENT')
        name = name_token.value
        self.expect('->')
        body = self.parse_expr()
        return ('fun', name, body)

    def parse_match(self):
        """Parse: match expr with arm { arm } end"""
        self.expect('MATCH')
        expr = self.parse_expr()
        self.expect('WITH')

        arms = []
        while self.current() and self.current().kind == '|':
            self.expect('|')
            pattern = self.parse_pattern()
            self.expect('->')
            body = self.parse_expr()
            arms.append((pattern, body))

        if not arms:
            raise MiniError("parse")

        self.expect('END')
        return ('match', expr, arms)

    def parse_assign(self):
        """Parse: orx [ := expr ]"""
        left = self.parse_orx()
        if self.match(':='):
            right = self.parse_expr()
            return (':=', left, right)
        return left

    def parse_orx(self):
        """Parse: andx { || andx }"""
        left = self.parse_andx()
        while self.match('||'):
            right = self.parse_andx()
            left = ('||', left, right)
        return left

    def parse_andx(self):
        """Parse: cmpx { && cmpx }"""
        left = self.parse_cmpx()
        while self.match('&&'):
            right = self.parse_cmpx()
            left = ('&&', left, right)
        return left

    def parse_cmpx(self):
        """Parse: catx [ ("=="|"!="|"<"|"<="|">"|">=") catx ]"""
        left = self.parse_catx()
        token = self.current()
        if token and token.kind in ['==', '!=', '<', '<=', '>', '>=']:
            op = token.value
            self.advance()
            right = self.parse_catx()
            return (op, left, right)
        return left

    def parse_catx(self):
        """Parse: addx [ ++ catx ]"""
        left = self.parse_addx()
        if self.match('++'):
            right = self.parse_catx()  # Right-associative
            return ('++', left, right)
        return left

    def parse_addx(self):
        """Parse: mulx { (+ | -) mulx }"""
        left = self.parse_mulx()
        while self.current() and self.current().kind in ['+', '-']:
            op = self.current().value
            self.advance()
            right = self.parse_mulx()
            left = (op, left, right)
        return left

    def parse_mulx(self):
        """Parse: unary { (* | / | %) unary }"""
        left = self.parse_unary()
        while self.current() and self.current().kind in ['*', '/', '%']:
            op = self.current().value
            self.advance()
            right = self.parse_unary()
            left = (op, left, right)
        return left

    def parse_unary(self):
        """Parse: (- | ! | ref) unary | app"""
        if self.match('-'):
            expr = self.parse_unary()
            return ('-unary', expr)
        if self.match('!'):
            expr = self.parse_unary()
            return ('!', expr)
        if self.match('REF'):
            expr = self.parse_unary()
            return ('ref', expr)
        return self.parse_app()

    def can_start_postfix(self):
        """Check if current token can start a postfix expression."""
        token = self.current()
        if not token:
            return False
        return token.kind in ['INT', 'STRING', 'TRUE', 'FALSE', 'IDENT', '(', '{']

    def parse_app(self):
        """Parse: postfix { postfix }"""
        func = self.parse_postfix()
        while self.can_start_postfix():
            arg = self.parse_postfix()
            func = ('app', func, arg)
        return func

    def parse_postfix(self):
        """Parse: atom { . IDENT }"""
        atom = self.parse_atom()
        while self.match('.'):
            field = self.expect('IDENT').value
            atom = ('.', atom, field)
        return atom

    def parse_atom(self):
        """Parse: INT | STRING | true | false | IDENT | ( expr ) | record"""
        token = self.current()

        if token and token.kind == 'INT':
            self.advance()
            return ('int', token.value)

        if token and token.kind == 'STRING':
            self.advance()
            return ('string', token.value)

        if token and token.kind == 'TRUE':
            self.advance()
            return ('bool', True)

        if token and token.kind == 'FALSE':
            self.advance()
            return ('bool', False)

        if token and token.kind == 'IDENT':
            self.advance()
            return ('var', token.value)

        if self.match('('):
            expr = self.parse_expr()
            self.expect(')')
            return expr

        if self.match('{'):
            return self.parse_record()

        raise MiniError("parse")

    def parse_record(self):
        """Parse: { [ IDENT = expr { , IDENT = expr } ] }"""
        fields = []
        field_names = set()

        if self.current() and self.current().kind != '}':
            while True:
                name = self.expect('IDENT').value
                if name in field_names:
                    raise MiniError("dup_field")
                field_names.add(name)
                self.expect('=')
                value = self.parse_expr()
                fields.append((name, value))

                if not self.match(','):
                    break

        self.expect('}')
        return ('record', fields)

    def parse_pattern(self):
        """Parse a pattern."""
        token = self.current()

        if token and token.kind == 'WILDCARD':
            self.advance()
            return ('wildcard',)

        if token and token.kind == 'INT':
            self.advance()
            return ('int', token.value)

        if token and token.kind == 'STRING':
            self.advance()
            return ('string', token.value)

        if token and token.kind == 'TRUE':
            self.advance()
            return ('bool', True)

        if token and token.kind == 'FALSE':
            self.advance()
            return ('bool', False)

        if token and token.kind == 'IDENT':
            self.advance()
            return ('bind', token.value)

        if self.match('{'):
            return self.parse_record_pattern()

        raise MiniError("parse")

    def parse_record_pattern(self):
        """Parse: { [ IDENT = pattern { , IDENT = pattern } ] }"""
        fields = []
        field_names = set()

        if self.current() and self.current().kind != '}':
            while True:
                name = self.expect('IDENT').value
                if name in field_names:
                    raise MiniError("dup_field")
                field_names.add(name)
                self.expect('=')
                pattern = self.parse_pattern()
                fields.append((name, pattern))

                if not self.match(','):
                    break

        self.expect('}')
        return ('record', fields)


# ============================================================================
# EVALUATOR
# ============================================================================

class Ref:
    """Mutable reference cell."""
    def __init__(self, value):
        self.value = value


class Closure:
    """Function closure."""
    def __init__(self, param, body, env):
        self.param = param
        self.body = body
        self.env = env


def eval_expr(expr, env):
    """Evaluate an expression in the given environment."""
    if expr[0] == 'int':
        return expr[1]

    if expr[0] == 'string':
        return expr[1]

    if expr[0] == 'bool':
        return expr[1]

    if expr[0] == 'var':
        name = expr[1]
        if name not in env:
            raise MiniError("unbound")
        value = env[name]
        if isinstance(value, tuple) and value[0] == 'uninit':
            raise MiniError("uninit")
        return value

    if expr[0] == 'record':
        fields = expr[1]
        result = {}
        for name, value_expr in fields:
            result[name] = eval_expr(value_expr, env)
        return result

    if expr[0] == '.':
        record = eval_expr(expr[1], env)
        field = expr[2]
        if not isinstance(record, dict):
            raise MiniError("type")
        if field not in record:
            raise MiniError("no_field")
        return record[field]

    if expr[0] == 'let':
        name, value_expr, body_expr = expr[1], expr[2], expr[3]
        value = eval_expr(value_expr, env)
        new_env = env.copy()
        new_env[name] = value
        return eval_expr(body_expr, new_env)

    if expr[0] == 'letrec':
        bindings, body = expr[1], expr[2]
        new_env = env.copy()

        # Initialize all slots as uninitialised
        for name, _ in bindings:
            new_env[name] = ('uninit',)

        # Evaluate right-hand sides and assign
        for name, value_expr in bindings:
            value = eval_expr(value_expr, new_env)
            new_env[name] = value

        return eval_expr(body, new_env)

    if expr[0] == 'if':
        cond, then_e, else_e = expr[1], expr[2], expr[3]
        cond_val = eval_expr(cond, env)
        if not isinstance(cond_val, bool):
            raise MiniError("type")
        if cond_val:
            return eval_expr(then_e, env)
        else:
            return eval_expr(else_e, env)

    if expr[0] == 'fun':
        param, body = expr[1], expr[2]
        return Closure(param, body, env)

    if expr[0] == 'match':
        value_expr, arms = expr[1], expr[2]
        value = eval_expr(value_expr, env)

        for pattern, body in arms:
            match_env = env.copy()
            if pattern_matches(pattern, value, match_env):
                return eval_expr(body, match_env)

        raise MiniError("no_match")

    if expr[0] == 'app':
        func_expr, arg_expr = expr[1], expr[2]
        func = eval_expr(func_expr, env)
        arg = eval_expr(arg_expr, env)
        if not isinstance(func, Closure):
            raise MiniError("type")
        new_env = func.env.copy()
        new_env[func.param] = arg
        return eval_expr(func.body, new_env)

    if expr[0] == '-unary':
        arg = eval_expr(expr[1], env)
        if not isinstance(arg, int) or isinstance(arg, bool):
            raise MiniError("type")
        return -arg

    if expr[0] == '!':
        arg = eval_expr(expr[1], env)
        if not isinstance(arg, Ref):
            raise MiniError("type")
        return arg.value

    if expr[0] == 'ref':
        arg = eval_expr(expr[1], env)
        return Ref(arg)

    if expr[0] == ':=':
        left, right = expr[1], expr[2]
        ref_val = eval_expr(left, env)
        new_val = eval_expr(right, env)
        if not isinstance(ref_val, Ref):
            raise MiniError("type")
        ref_val.value = new_val
        return new_val

    if expr[0] == '||':
        left, right = expr[1], expr[2]
        left_val = eval_expr(left, env)
        if not isinstance(left_val, bool):
            raise MiniError("type")
        if left_val:
            return True
        right_val = eval_expr(right, env)
        if not isinstance(right_val, bool):
            raise MiniError("type")
        return right_val

    if expr[0] == '&&':
        left, right = expr[1], expr[2]
        left_val = eval_expr(left, env)
        if not isinstance(left_val, bool):
            raise MiniError("type")
        if not left_val:
            return False
        right_val = eval_expr(right, env)
        if not isinstance(right_val, bool):
            raise MiniError("type")
        return right_val

    # Binary operators - evaluate both operands first
    if expr[0] in ['+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>=', '++']:
        left_val = eval_expr(expr[1], env)
        right_val = eval_expr(expr[2], env)

        op = expr[0]

        if op == '+':
            if not (isinstance(left_val, int) and not isinstance(left_val, bool)):
                raise MiniError("type")
            if not (isinstance(right_val, int) and not isinstance(right_val, bool)):
                raise MiniError("type")
            return left_val + right_val

        if op == '-':
            if not (isinstance(left_val, int) and not isinstance(left_val, bool)):
                raise MiniError("type")
            if not (isinstance(right_val, int) and not isinstance(right_val, bool)):
                raise MiniError("type")
            return left_val - right_val

        if op == '*':
            if isinstance(left_val, str):
                if not (isinstance(right_val, int) and not isinstance(right_val, bool)):
                    raise MiniError("type")
                count = right_val
                if count <= 0:
                    return ""
                return left_val * count
            else:
                if not (isinstance(left_val, int) and not isinstance(left_val, bool)):
                    raise MiniError("type")
                if not (isinstance(right_val, int) and not isinstance(right_val, bool)):
                    raise MiniError("type")
                return left_val * right_val

        if op == '/':
            if not (isinstance(left_val, int) and not isinstance(left_val, bool)):
                raise MiniError("type")
            if not (isinstance(right_val, int) and not isinstance(right_val, bool)):
                raise MiniError("type")
            if right_val == 0:
                raise MiniError("div_zero")
            # Truncate toward zero
            if (left_val >= 0 and right_val > 0) or (left_val < 0 and right_val < 0):
                return left_val // right_val
            else:
                return -(-left_val // right_val) if left_val < 0 else -(left_val // -right_val)

        if op == '%':
            if not (isinstance(left_val, int) and not isinstance(left_val, bool)):
                raise MiniError("type")
            if not (isinstance(right_val, int) and not isinstance(right_val, bool)):
                raise MiniError("type")
            if right_val == 0:
                raise MiniError("div_zero")
            # Floored remainder
            return left_val % right_val

        if op == '==':
            # Both must be same type
            if type(left_val) != type(right_val):
                raise MiniError("type")
            if isinstance(left_val, (dict, Closure)):
                raise MiniError("type")
            if isinstance(left_val, Ref):
                return left_val is right_val
            return left_val == right_val

        if op == '!=':
            # Both must be same type
            if type(left_val) != type(right_val):
                raise MiniError("type")
            if isinstance(left_val, (dict, Closure)):
                raise MiniError("type")
            if isinstance(left_val, Ref):
                return left_val is not right_val
            return left_val != right_val

        if op in ['<', '<=', '>', '>=']:
            if isinstance(left_val, int) and not isinstance(left_val, bool):
                if not (isinstance(right_val, int) and not isinstance(right_val, bool)):
                    raise MiniError("type")
            elif isinstance(left_val, str):
                if not isinstance(right_val, str):
                    raise MiniError("type")
            else:
                raise MiniError("type")

            if op == '<':
                return left_val < right_val
            if op == '<=':
                return left_val <= right_val
            if op == '>':
                return left_val > right_val
            if op == '>=':
                return left_val >= right_val

        if op == '++':
            if not isinstance(left_val, str):
                raise MiniError("type")
            if isinstance(right_val, str):
                return left_val + right_val
            elif isinstance(right_val, int) and not isinstance(right_val, bool):
                return left_val + str(right_val)
            elif isinstance(right_val, bool):
                return left_val + ('true' if right_val else 'false')
            else:
                raise MiniError("type")

    raise MiniError("parse")


def pattern_matches(pattern, value, env):
    """Try to match a pattern against a value. Update env with bindings if successful."""
    if pattern[0] == 'wildcard':
        return True

    if pattern[0] == 'int':
        return isinstance(value, int) and not isinstance(value, bool) and pattern[1] == value

    if pattern[0] == 'string':
        return isinstance(value, str) and pattern[1] == value

    if pattern[0] == 'bool':
        return isinstance(value, bool) and pattern[1] == value

    if pattern[0] == 'bind':
        name = pattern[1]
        if name in env and env[name] != ('uninit',):
            # Already bound in this pattern - shouldn't happen for patterns
            pass
        env[name] = value
        return True

    if pattern[0] == 'record':
        if not isinstance(value, dict):
            return False
        fields = pattern[1]
        bound_names = set()
        for name, subpattern in fields:
            if name not in value:
                return False
            if not pattern_matches(subpattern, value[name], env):
                # Rollback bindings? No, pattern matching doesn't backtrack
                return False
            # Check for duplicate bindings in this pattern
            if subpattern[0] == 'bind':
                var_name = subpattern[1]
                if var_name in bound_names:
                    raise MiniError("dup_binding")
                bound_names.add(var_name)
        return True

    return False


def result_to_python(value):
    """Convert an internal value to a Python value."""
    if isinstance(value, dict):
        return {k: result_to_python(v) for k, v in value.items()}
    if isinstance(value, Closure):
        return "<fn>"
    if isinstance(value, Ref):
        return "<ref>"
    return value


def run(source):
    """Parse and evaluate the source, returning the Python result."""
    tokens = lex(source)
    parser = Parser(tokens)
    expr = parser.parse()
    result = eval_expr(expr, {})
    return result_to_python(result)
