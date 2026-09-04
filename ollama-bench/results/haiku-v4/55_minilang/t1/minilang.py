class MiniError(Exception):
    def __init__(self, kind, message=""):
        self.kind = kind
        super().__init__(message)

# Lexer
class Token:
    def __init__(self, type, value, pos=0):
        self.type = type
        self.value = value
        self.pos = pos

class Lexer:
    KEYWORDS = {'let', 'letrec', 'and', 'in', 'if', 'then', 'else', 'fun', 'match', 'with', 'end', 'ref', 'true', 'false'}
    OPERATORS = ['->',  ':=', '==', '!=', '<=', '>=', '&&', '||', '++']
    SINGLE_CHAR_OPS = ['+', '-', '*', '/', '%', '<', '>', '=', '(', ')', '{', '}', ',', '.', '|', '!']

    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.tokens = []

    def tokenize(self):
        while self.pos < len(self.source):
            c = self.source[self.pos]

            if c in ' \t\r\n':
                self.pos += 1
            elif c == '"':
                self.read_string()
            elif c.isdigit():
                self.read_number()
            elif c.isalpha() or c == '_':
                self.read_identifier()
            else:
                self.read_operator()

        if not self.tokens and not self.source.strip():
            raise MiniError("parse", "Empty input")
        if not self.tokens:
            raise MiniError("parse", "Empty input")

        return self.tokens

    def read_string(self):
        start = self.pos
        self.pos += 1
        value = ""
        while self.pos < len(self.source):
            c = self.source[self.pos]
            if c == '"':
                self.pos += 1
                self.tokens.append(Token('STRING', value))
                return
            elif c == '\\' or c == '\n':
                raise MiniError("parse", "Invalid character in string")
            else:
                value += c
                self.pos += 1
        raise MiniError("parse", "Unterminated string")

    def read_number(self):
        start = self.pos
        if self.source[self.pos] == '0':
            self.pos += 1
            if self.pos < len(self.source) and self.source[self.pos].isdigit():
                raise MiniError("parse", "Leading zero not allowed")
            self.tokens.append(Token('INT', 0))
        else:
            value = ""
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                value += self.source[self.pos]
                self.pos += 1
            self.tokens.append(Token('INT', int(value)))

    def read_identifier(self):
        value = ""
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            c = self.source[self.pos]
            if ord(c) > 127:
                raise MiniError("parse", "Non-ASCII character in identifier")
            value += c
            self.pos += 1

        if value == '_':
            self.tokens.append(Token('_', '_'))
        elif value in self.KEYWORDS:
            self.tokens.append(Token(value.upper(), value))
        else:
            self.tokens.append(Token('IDENT', value))

    def read_operator(self):
        for op in self.OPERATORS:
            if self.source[self.pos:].startswith(op):
                self.tokens.append(Token(op, op))
                self.pos += len(op)
                return

        if self.source[self.pos] in self.SINGLE_CHAR_OPS:
            op = self.source[self.pos]
            self.tokens.append(Token(op, op))
            self.pos += 1
        else:
            raise MiniError("parse", f"Invalid character: {self.source[self.pos]}")

# AST Nodes
class Expr:
    pass

class IntLit(Expr):
    def __init__(self, value):
        self.value = value

class StrLit(Expr):
    def __init__(self, value):
        self.value = value

class BoolLit(Expr):
    def __init__(self, value):
        self.value = value

class Ident(Expr):
    def __init__(self, name):
        self.name = name

class BinOp(Expr):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOp(Expr):
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

class IfExpr(Expr):
    def __init__(self, cond, then_expr, else_expr):
        self.cond = cond
        self.then_expr = then_expr
        self.else_expr = else_expr

class LetExpr(Expr):
    def __init__(self, name, value, body):
        self.name = name
        self.value = value
        self.body = body

class LetrecExpr(Expr):
    def __init__(self, bindings, body):
        self.bindings = bindings  # list of (name, expr) tuples
        self.body = body

class FunExpr(Expr):
    def __init__(self, param, body):
        self.param = param
        self.body = body

class AppExpr(Expr):
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg

class RecordLit(Expr):
    def __init__(self, fields):
        self.fields = fields  # dict of name -> expr

class FieldAccess(Expr):
    def __init__(self, record, field):
        self.record = record
        self.field = field

class MatchExpr(Expr):
    def __init__(self, expr, arms):
        self.expr = expr
        self.arms = arms  # list of (pattern, body) tuples

class AssignExpr(Expr):
    def __init__(self, target, value):
        self.target = target
        self.value = value

# Patterns
class Pattern:
    pass

class WildcardPattern(Pattern):
    pass

class IntPattern(Pattern):
    def __init__(self, value):
        self.value = value

class StrPattern(Pattern):
    def __init__(self, value):
        self.value = value

class BoolPattern(Pattern):
    def __init__(self, value):
        self.value = value

class IdentPattern(Pattern):
    def __init__(self, name):
        self.name = name

class RecordPattern(Pattern):
    def __init__(self, fields):
        self.fields = fields  # dict of name -> pattern

# Parser
class Parser:
    KEYWORDS = {'let', 'letrec', 'and', 'in', 'if', 'then', 'else', 'fun', 'match', 'with', 'end', 'ref', 'true', 'false'}

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        expr = self.parse_expr()
        if self.pos < len(self.tokens):
            raise MiniError("parse", "Unexpected tokens after expression")
        return expr

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def peek(self, offset=1):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return None

    def consume(self, expected=None):
        token = self.current()
        if expected and (token is None or token.type != expected):
            raise MiniError("parse", f"Expected {expected}, got {token.type if token else 'EOF'}")
        self.pos += 1
        return token

    def match(self, *types):
        token = self.current()
        return token and token.type in types

    def parse_expr(self):
        return self.parse_let_or_if_or_fun_or_match_or_assign()

    def parse_expr_limited(self):
        # Parse an expr but don't consume 'and' or 'in' at the top level
        # This is used for letrec RHS and is effectively the same as parse_expr
        return self.parse_let_or_if_or_fun_or_match_or_assign()

    def parse_let_or_if_or_fun_or_match_or_assign(self):
        if self.match('LET'):
            return self.parse_let()
        elif self.match('LETREC'):
            return self.parse_letrec()
        elif self.match('IF'):
            return self.parse_if()
        elif self.match('FUN'):
            return self.parse_fun()
        elif self.match('MATCH'):
            return self.parse_match()
        else:
            return self.parse_assign()

    def parse_let(self):
        self.consume('LET')
        name_token = self.consume('IDENT')
        if name_token.value in self.KEYWORDS:
            raise MiniError("parse", "Keyword used as variable name")
        self.consume('=')
        value = self.parse_expr()
        self.consume('IN')
        body = self.parse_expr()
        return LetExpr(name_token.value, value, body)

    def parse_letrec(self):
        self.consume('LETREC')
        bindings = []

        while True:
            name_token = self.consume('IDENT')
            if name_token.value in self.KEYWORDS:
                raise MiniError("parse", "Keyword used as variable name")
            self.consume('=')
            value = self.parse_expr_limited()  # parse the RHS, stopping at and/in
            bindings.append((name_token.value, value))

            if not self.match('AND'):
                break
            self.consume('AND')

        # Check for duplicate names
        names = set()
        for name, _ in bindings:
            if name in names:
                raise MiniError("dup_binding", "Duplicate binding in letrec")
            names.add(name)

        self.consume('IN')
        body = self.parse_expr()
        return LetrecExpr(bindings, body)

    def parse_if(self):
        self.consume('IF')
        cond = self.parse_expr()
        self.consume('THEN')
        then_expr = self.parse_expr()
        self.consume('ELSE')
        else_expr = self.parse_expr()
        return IfExpr(cond, then_expr, else_expr)

    def parse_fun(self):
        self.consume('FUN')
        name_token = self.consume('IDENT')
        if name_token.value in self.KEYWORDS:
            raise MiniError("parse", "Keyword used as variable name")
        self.consume('->')
        body = self.parse_expr()
        return FunExpr(name_token.value, body)

    def parse_match(self):
        self.consume('MATCH')
        expr = self.parse_expr()
        self.consume('WITH')

        arms = []
        while self.match('|'):
            self.consume('|')
            pattern = self.parse_pattern()
            # Check for duplicate variables in the pattern
            vars_seen = set()
            self.collect_pattern_vars(pattern, vars_seen)
            self.consume('->')
            body = self.parse_expr()
            arms.append((pattern, body))

        self.consume('END')
        return MatchExpr(expr, arms)

    def parse_assign(self):
        left = self.parse_or()
        if self.match(':='):
            self.consume(':=')
            right = self.parse_expr()
            return AssignExpr(left, right)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.match('||'):
            self.consume('||')
            right = self.parse_and()
            left = BinOp('||', left, right)
        return left

    def parse_and(self):
        left = self.parse_cmp()
        while self.match('&&'):
            self.consume('&&')
            right = self.parse_cmp()
            left = BinOp('&&', left, right)
        return left

    def parse_cmp(self):
        left = self.parse_concat()
        if self.match('==', '!=', '<', '<=', '>', '>='):
            op = self.consume().type
            right = self.parse_concat()
            return BinOp(op, left, right)
        return left

    def parse_concat(self):
        left = self.parse_add()
        if self.match('++'):
            self.consume('++')
            right = self.parse_concat()  # right-associative
            return BinOp('++', left, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.match('+', '-'):
            op = self.consume().type
            right = self.parse_mul()
            left = BinOp(op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.match('*', '/', '%'):
            op = self.consume().type
            right = self.parse_unary()
            left = BinOp(op, left, right)
        return left

    def parse_unary(self):
        if self.match('-', '!', 'REF'):
            op = self.consume().type
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        return self.parse_app()

    def parse_app(self):
        func = self.parse_postfix()
        while self.match('INT', 'STRING', 'TRUE', 'FALSE', 'IDENT', '(', '{') and not self._is_terminator():
            arg = self.parse_postfix()
            func = AppExpr(func, arg)
        return func

    def _is_terminator(self):
        token = self.current()
        if token is None:
            return True
        return token.type in ['IN', 'THEN', 'ELSE', 'WITH', 'END', '|', ')', '}', ',', 'AND']

    def parse_postfix(self):
        expr = self.parse_atom()
        while self.match('.'):
            self.consume('.')
            field = self.consume('IDENT')
            expr = FieldAccess(expr, field.value)
        return expr

    def parse_atom(self):
        token = self.current()

        if self.match('INT'):
            token = self.consume('INT')
            return IntLit(token.value)
        elif self.match('STRING'):
            token = self.consume('STRING')
            return StrLit(token.value)
        elif self.match('TRUE'):
            self.consume('TRUE')
            return BoolLit(True)
        elif self.match('FALSE'):
            self.consume('FALSE')
            return BoolLit(False)
        elif self.match('_'):
            raise MiniError("parse", "Underscore _ cannot be used as an expression")
        elif self.match('IDENT'):
            token = self.consume('IDENT')
            return Ident(token.value)
        elif self.match('('):
            self.consume('(')
            expr = self.parse_expr()
            self.consume(')')
            return expr
        elif self.match('{'):
            return self.parse_record()
        else:
            raise MiniError("parse", f"Unexpected token: {token.type if token else 'EOF'}")

    def parse_record(self):
        self.consume('{')
        fields = {}

        if not self.match('}'):
            while True:
                field_name = self.consume('IDENT')
                if field_name.value in self.KEYWORDS:
                    raise MiniError("parse", "Keyword used as field name")
                if field_name.value in fields:
                    raise MiniError("dup_field", "Duplicate field in record")

                self.consume('=')
                expr = self.parse_expr()
                fields[field_name.value] = expr

                if not self.match(','):
                    break
                self.consume(',')

        self.consume('}')
        return RecordLit(fields)

    def parse_pattern(self):
        if self.match('_'):
            self.consume('_')
            return WildcardPattern()
        elif self.match('INT'):
            token = self.consume('INT')
            return IntPattern(token.value)
        elif self.match('STRING'):
            token = self.consume('STRING')
            return StrPattern(token.value)
        elif self.match('TRUE'):
            self.consume('TRUE')
            return BoolPattern(True)
        elif self.match('FALSE'):
            self.consume('FALSE')
            return BoolPattern(False)
        elif self.match('IDENT'):
            token = self.consume('IDENT')
            if token.value in self.KEYWORDS:
                raise MiniError("parse", "Keyword used as pattern variable")
            return IdentPattern(token.value)
        elif self.match('{'):
            return self.parse_record_pattern()
        else:
            raise MiniError("parse", f"Unexpected token in pattern: {self.current().type if self.current() else 'EOF'}")

    def parse_record_pattern(self):
        self.consume('{')
        fields = {}

        if not self.match('}'):
            while True:
                field_name = self.consume('IDENT')
                if field_name.value in self.KEYWORDS:
                    raise MiniError("parse", "Keyword used as field name")
                if field_name.value in fields:
                    raise MiniError("dup_field", "Duplicate field in record pattern")

                self.consume('=')
                pattern = self.parse_pattern()
                fields[field_name.value] = pattern

                if not self.match(','):
                    break
                self.consume(',')

        self.consume('}')
        # Check for duplicate variables in the pattern
        vars_seen = set()
        for field_pattern in fields.values():
            self.collect_pattern_vars(field_pattern, vars_seen)
        return RecordPattern(fields)

    def collect_pattern_vars(self, pattern, vars_seen):
        if isinstance(pattern, IdentPattern):
            if pattern.name in vars_seen:
                raise MiniError("dup_binding", "Duplicate variable in pattern")
            vars_seen.add(pattern.name)
        elif isinstance(pattern, RecordPattern):
            for field_pattern in pattern.fields.values():
                self.collect_pattern_vars(field_pattern, vars_seen)

# Value classes
class Value:
    pass

class IntVal(Value):
    def __init__(self, value):
        self.value = value

class StrVal(Value):
    def __init__(self, value):
        self.value = value

class BoolVal(Value):
    def __init__(self, value):
        self.value = value

class RecordVal(Value):
    def __init__(self, fields):
        self.fields = fields  # dict

class ClosureVal(Value):
    def __init__(self, param, body, env):
        self.param = param
        self.body = body
        self.env = env

class RefVal(Value):
    def __init__(self, value):
        self.value = value

# Evaluator
class Evaluator:
    def __init__(self):
        self.global_env = {}

    def eval(self, expr, env):
        if isinstance(expr, IntLit):
            return IntVal(expr.value)
        elif isinstance(expr, StrLit):
            return StrVal(expr.value)
        elif isinstance(expr, BoolLit):
            return BoolVal(expr.value)
        elif isinstance(expr, Ident):
            if expr.name not in env:
                raise MiniError("unbound", f"Unbound variable: {expr.name}")
            val = env[expr.name]
            if val is None:
                raise MiniError("uninit", f"Uninitialized variable: {expr.name}")
            return val
        elif isinstance(expr, BinOp):
            return self.eval_binop(expr, env)
        elif isinstance(expr, UnaryOp):
            return self.eval_unary(expr, env)
        elif isinstance(expr, IfExpr):
            return self.eval_if(expr, env)
        elif isinstance(expr, LetExpr):
            return self.eval_let(expr, env)
        elif isinstance(expr, LetrecExpr):
            return self.eval_letrec(expr, env)
        elif isinstance(expr, FunExpr):
            return ClosureVal(expr.param, expr.body, env)
        elif isinstance(expr, AppExpr):
            return self.eval_app(expr, env)
        elif isinstance(expr, RecordLit):
            return self.eval_record(expr, env)
        elif isinstance(expr, FieldAccess):
            return self.eval_field_access(expr, env)
        elif isinstance(expr, MatchExpr):
            return self.eval_match(expr, env)
        elif isinstance(expr, AssignExpr):
            return self.eval_assign(expr, env)
        else:
            raise MiniError("parse", f"Unknown expression type: {type(expr)}")

    def eval_binop(self, expr, env):
        op = expr.op

        # Short-circuit evaluation for && and ||
        if op == '&&':
            left = self.eval(expr.left, env)
            if not isinstance(left, BoolVal):
                raise MiniError("type", "Left operand of && must be bool")
            if not left.value:
                return BoolVal(False)
            right = self.eval(expr.right, env)
            if not isinstance(right, BoolVal):
                raise MiniError("type", "Right operand of && must be bool")
            return right
        elif op == '||':
            left = self.eval(expr.left, env)
            if not isinstance(left, BoolVal):
                raise MiniError("type", "Left operand of || must be bool")
            if left.value:
                return BoolVal(True)
            right = self.eval(expr.right, env)
            if not isinstance(right, BoolVal):
                raise MiniError("type", "Right operand of || must be bool")
            return right

        # Evaluate both operands for other operators
        left = self.eval(expr.left, env)
        right = self.eval(expr.right, env)

        if op == '+':
            if not isinstance(left, IntVal) or not isinstance(right, IntVal):
                raise MiniError("type", "Both operands of + must be int")
            return IntVal(left.value + right.value)
        elif op == '-':
            if not isinstance(left, IntVal) or not isinstance(right, IntVal):
                raise MiniError("type", "Both operands of - must be int")
            return IntVal(left.value - right.value)
        elif op == '*':
            if isinstance(left, IntVal) and isinstance(right, IntVal):
                return IntVal(left.value * right.value)
            elif isinstance(left, StrVal) and isinstance(right, IntVal):
                count = right.value
                if count <= 0:
                    return StrVal("")
                return StrVal(left.value * count)
            else:
                raise MiniError("type", "Invalid operands for *")
        elif op == '/':
            if not isinstance(left, IntVal) or not isinstance(right, IntVal):
                raise MiniError("type", "Both operands of / must be int")
            if right.value == 0:
                raise MiniError("div_zero", "Division by zero")
            # Integer division truncating toward zero
            result = int(left.value / right.value)
            return IntVal(result)
        elif op == '%':
            if not isinstance(left, IntVal) or not isinstance(right, IntVal):
                raise MiniError("type", "Both operands of % must be int")
            if right.value == 0:
                raise MiniError("div_zero", "Division by zero")
            # Floored remainder
            result = left.value % right.value
            return IntVal(result)
        elif op == '++':
            if not isinstance(left, StrVal):
                raise MiniError("type", "Left operand of ++ must be str")
            if isinstance(right, StrVal):
                return StrVal(left.value + right.value)
            elif isinstance(right, IntVal):
                return StrVal(left.value + str(right.value))
            elif isinstance(right, BoolVal):
                return StrVal(left.value + ("true" if right.value else "false"))
            else:
                raise MiniError("type", "Invalid right operand for ++")
        elif op == '==':
            if isinstance(left, IntVal) and isinstance(right, IntVal):
                return BoolVal(left.value == right.value)
            elif isinstance(left, StrVal) and isinstance(right, StrVal):
                return BoolVal(left.value == right.value)
            elif isinstance(left, BoolVal) and isinstance(right, BoolVal):
                return BoolVal(left.value == right.value)
            elif isinstance(left, RefVal) and isinstance(right, RefVal):
                return BoolVal(left is right)
            else:
                raise MiniError("type", "Cannot compare these types with ==")
        elif op == '!=':
            if isinstance(left, IntVal) and isinstance(right, IntVal):
                return BoolVal(left.value != right.value)
            elif isinstance(left, StrVal) and isinstance(right, StrVal):
                return BoolVal(left.value != right.value)
            elif isinstance(left, BoolVal) and isinstance(right, BoolVal):
                return BoolVal(left.value != right.value)
            elif isinstance(left, RefVal) and isinstance(right, RefVal):
                return BoolVal(left is not right)
            else:
                raise MiniError("type", "Cannot compare these types with !=")
        elif op == '<':
            if isinstance(left, IntVal) and isinstance(right, IntVal):
                return BoolVal(left.value < right.value)
            elif isinstance(left, StrVal) and isinstance(right, StrVal):
                return BoolVal(left.value < right.value)
            else:
                raise MiniError("type", "Cannot compare these types with <")
        elif op == '<=':
            if isinstance(left, IntVal) and isinstance(right, IntVal):
                return BoolVal(left.value <= right.value)
            elif isinstance(left, StrVal) and isinstance(right, StrVal):
                return BoolVal(left.value <= right.value)
            else:
                raise MiniError("type", "Cannot compare these types with <=")
        elif op == '>':
            if isinstance(left, IntVal) and isinstance(right, IntVal):
                return BoolVal(left.value > right.value)
            elif isinstance(left, StrVal) and isinstance(right, StrVal):
                return BoolVal(left.value > right.value)
            else:
                raise MiniError("type", "Cannot compare these types with >")
        elif op == '>=':
            if isinstance(left, IntVal) and isinstance(right, IntVal):
                return BoolVal(left.value >= right.value)
            elif isinstance(left, StrVal) and isinstance(right, StrVal):
                return BoolVal(left.value >= right.value)
            else:
                raise MiniError("type", "Cannot compare these types with >=")
        else:
            raise MiniError("parse", f"Unknown operator: {op}")

    def eval_unary(self, expr, env):
        if expr.op == '-':
            operand = self.eval(expr.operand, env)
            if not isinstance(operand, IntVal):
                raise MiniError("type", "Operand of unary - must be int")
            return IntVal(-operand.value)
        elif expr.op == '!':
            operand = self.eval(expr.operand, env)
            if not isinstance(operand, RefVal):
                raise MiniError("type", "Operand of ! must be ref")
            return operand.value
        elif expr.op == 'REF':
            operand = self.eval(expr.operand, env)
            return RefVal(operand)
        else:
            raise MiniError("parse", f"Unknown unary operator: {expr.op}")

    def eval_if(self, expr, env):
        cond = self.eval(expr.cond, env)
        if not isinstance(cond, BoolVal):
            raise MiniError("type", "Condition of if must be bool")
        if cond.value:
            return self.eval(expr.then_expr, env)
        else:
            return self.eval(expr.else_expr, env)

    def eval_let(self, expr, env):
        value = self.eval(expr.value, env)
        new_env = env.copy()
        new_env[expr.name] = value
        return self.eval(expr.body, new_env)

    def eval_letrec(self, expr, env):
        # Check for duplicate names
        names = set()
        for name, _ in expr.bindings:
            if name in names:
                raise MiniError("dup_binding", "Duplicate binding in letrec")
            names.add(name)

        # Create new environment with slots for all bindings
        new_env = env.copy()
        slots = {}
        for name, _ in expr.bindings:
            slots[name] = None
        new_env.update(slots)

        # Evaluate all bindings
        for name, value_expr in expr.bindings:
            try:
                value = self.eval(value_expr, new_env)
                new_env[name] = value
            except MiniError as e:
                if e.kind == "uninit":
                    raise
                raise

        return self.eval(expr.body, new_env)

    def eval_app(self, expr, env):
        func = self.eval(expr.func, env)
        arg = self.eval(expr.arg, env)

        if not isinstance(func, ClosureVal):
            raise MiniError("type", "Left side of application must be a function")

        # Create new environment with parameter bound
        fn_env = func.env.copy()
        fn_env[func.param] = arg
        return self.eval(func.body, fn_env)

    def eval_record(self, expr, env):
        fields = {}
        for name, field_expr in expr.fields.items():
            fields[name] = self.eval(field_expr, env)
        return RecordVal(fields)

    def eval_field_access(self, expr, env):
        record = self.eval(expr.record, env)
        if not isinstance(record, RecordVal):
            raise MiniError("type", "Left side of . must be a record")
        if expr.field not in record.fields:
            raise MiniError("no_field", f"Record has no field: {expr.field}")
        return record.fields[expr.field]

    def eval_match(self, expr, env):
        value = self.eval(expr.expr, env)

        for pattern, body in expr.arms:
            match_env = self.match_pattern(pattern, value, env)
            if match_env is not None:
                return self.eval(body, match_env)

        raise MiniError("no_match", "No pattern matched")

    def match_pattern(self, pattern, value, env):
        if isinstance(pattern, WildcardPattern):
            return env
        elif isinstance(pattern, IntPattern):
            if isinstance(value, IntVal) and value.value == pattern.value:
                return env
            return None
        elif isinstance(pattern, StrPattern):
            if isinstance(value, StrVal) and value.value == pattern.value:
                return env
            return None
        elif isinstance(pattern, BoolPattern):
            if isinstance(value, BoolVal) and value.value == pattern.value:
                return env
            return None
        elif isinstance(pattern, IdentPattern):
            new_env = env.copy()
            new_env[pattern.name] = value
            return new_env
        elif isinstance(pattern, RecordPattern):
            if not isinstance(value, RecordVal):
                return None

            # Check that all pattern fields exist in the value
            for field_name in pattern.fields:
                if field_name not in value.fields:
                    return None

            # Match all pattern fields
            new_env = env.copy()
            for field_name, field_pattern in pattern.fields.items():
                field_value = value.fields[field_name]
                field_match_env = self.match_pattern(field_pattern, field_value, new_env)
                if field_match_env is None:
                    return None
                new_env = field_match_env

            return new_env
        else:
            return None

    def eval_assign(self, expr, env):
        target = self.eval(expr.target, env)
        value = self.eval(expr.value, env)

        if not isinstance(target, RefVal):
            raise MiniError("type", "Left side of := must be a ref")

        target.value = value
        return value

def convert_value(val):
    if isinstance(val, IntVal):
        return val.value
    elif isinstance(val, StrVal):
        return val.value
    elif isinstance(val, BoolVal):
        return val.value
    elif isinstance(val, RecordVal):
        return {k: convert_value(v) for k, v in val.fields.items()}
    elif isinstance(val, ClosureVal):
        return "<fn>"
    elif isinstance(val, RefVal):
        return "<ref>"
    else:
        raise MiniError("type", f"Unknown value type: {type(val)}")

def run(source):
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        evaluator = Evaluator()
        result = evaluator.eval(ast, {})

        return convert_value(result)
    except MiniError:
        raise
