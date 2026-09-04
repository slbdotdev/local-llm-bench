"""A hand-written lexer/parser/evaluator for a small expression language.

No eval/exec/compile, and no ast/operator/functools imports are used anywhere
in this module, per spec.
"""

from collections import namedtuple

# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------


class MiniError(Exception):
    def __init__(self, kind):
        super().__init__(kind)
        self.kind = kind


RESERVED = frozenset({
    'let', 'letrec', 'and', 'in', 'if', 'then', 'else', 'fun', 'match',
    'with', 'end', 'ref', 'true', 'false', '_',
})

CMP_OPS = ('==', '!=', '<', '<=', '>', '>=')

# --------------------------------------------------------------------------
# Lexer
# --------------------------------------------------------------------------

Token = namedtuple('Token', ['kind', 'text', 'pos'])

_TWO_CHAR_OPS = ('->', ':=', '==', '!=', '<=', '>=', '&&', '||', '++')
_ONE_CHAR_OPS = '+-*/%<>=(){},.|!'


def tokenize(source):
    tokens = []
    i = 0
    n = len(source)
    while i < n:
        c = source[i]
        if c in ' \t\r\n':
            i += 1
            continue
        if c == '"':
            j = i + 1
            while j < n and source[j] not in '"\\\n':
                j += 1
            if j >= n or source[j] != '"':
                raise MiniError('parse')
            tokens.append(Token('STRING', source[i + 1:j], i))
            i = j + 1
            continue
        if c in '0123456789':
            j = i
            while j < n and source[j] in '0123456789':
                j += 1
            text = source[i:j]
            if len(text) > 1 and text[0] == '0':
                raise MiniError('parse')
            tokens.append(Token('INT', text, i))
            i = j
            continue
        if c == '_' or (c.isalpha() and c.isascii()):
            j = i + 1
            while j < n:
                cj = source[j]
                if cj == '_' or (cj.isalnum() and cj.isascii()):
                    j += 1
                else:
                    break
            tokens.append(Token('IDENT', source[i:j], i))
            i = j
            continue
        two = source[i:i + 2]
        if two in _TWO_CHAR_OPS:
            tokens.append(Token('OP', two, i))
            i += 2
            continue
        if c in _ONE_CHAR_OPS:
            tokens.append(Token('OP', c, i))
            i += 1
            continue
        raise MiniError('parse')
    tokens.append(Token('EOF', '', n))
    return tokens


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def check_no_dup_names(names, kind):
    seen = set()
    for name in names:
        if name in seen:
            raise MiniError(kind)
        seen.add(name)


def collect_pattern_vars(pat, out):
    tag = pat[0]
    if tag == 'pvar':
        out.append(pat[1])
    elif tag == 'precord':
        for _name, sub in pat[1]:
            collect_pattern_vars(sub, out)


def can_start_atom(tok):
    if tok.kind in ('INT', 'STRING'):
        return True
    if tok.kind == 'OP':
        return tok.text in ('(', '{')
    if tok.kind == 'IDENT':
        if tok.text in ('true', 'false'):
            return True
        if tok.text in RESERVED:
            return False
        return True
    return False


# --------------------------------------------------------------------------
# Parser
# --------------------------------------------------------------------------


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect_op(self, s):
        tok = self.peek()
        if tok.kind != 'OP' or tok.text != s:
            raise MiniError('parse')
        self.advance()

    def expect_kw(self, word):
        tok = self.peek()
        if tok.kind != 'IDENT' or tok.text != word:
            raise MiniError('parse')
        self.advance()

    def expect_ident_nonreserved(self):
        tok = self.peek()
        if tok.kind != 'IDENT' or tok.text in RESERVED:
            raise MiniError('parse')
        self.advance()
        return tok.text

    # ---- expr ----

    def parse_expr(self):
        tok = self.peek()
        if tok.kind == 'IDENT':
            if tok.text == 'let':
                return self.parse_let()
            if tok.text == 'letrec':
                return self.parse_letrec()
            if tok.text == 'if':
                return self.parse_if()
            if tok.text == 'fun':
                return self.parse_fun()
            if tok.text == 'match':
                return self.parse_match()
        return self.parse_assign()

    def parse_let(self):
        self.advance()
        name = self.expect_ident_nonreserved()
        self.expect_op('=')
        e1 = self.parse_expr()
        self.expect_kw('in')
        e2 = self.parse_expr()
        return ('let', name, e1, e2)

    def parse_letrec(self):
        self.advance()
        bindings = []
        name = self.expect_ident_nonreserved()
        self.expect_op('=')
        e = self.parse_expr()
        bindings.append((name, e))
        while self.peek().kind == 'IDENT' and self.peek().text == 'and':
            self.advance()
            name = self.expect_ident_nonreserved()
            self.expect_op('=')
            e = self.parse_expr()
            bindings.append((name, e))
        self.expect_kw('in')
        body = self.parse_expr()
        check_no_dup_names([b[0] for b in bindings], 'dup_binding')
        return ('letrec', bindings, body)

    def parse_if(self):
        self.advance()
        c = self.parse_expr()
        self.expect_kw('then')
        a = self.parse_expr()
        self.expect_kw('else')
        b = self.parse_expr()
        return ('if', c, a, b)

    def parse_fun(self):
        self.advance()
        param = self.expect_ident_nonreserved()
        self.expect_op('->')
        body = self.parse_expr()
        return ('fun', param, body)

    def parse_match(self):
        self.advance()
        e = self.parse_expr()
        self.expect_kw('with')
        arms = [self.parse_arm()]
        while self.peek().kind == 'OP' and self.peek().text == '|':
            arms.append(self.parse_arm())
        self.expect_kw('end')
        return ('match', e, arms)

    def parse_arm(self):
        self.expect_op('|')
        pat = self.parse_pattern()
        varsout = []
        collect_pattern_vars(pat, varsout)
        check_no_dup_names(varsout, 'dup_binding')
        self.expect_op('->')
        body = self.parse_expr()
        return (pat, body)

    # ---- precedence chain ----

    def parse_assign(self):
        left = self.parse_or()
        tok = self.peek()
        if tok.kind == 'OP' and tok.text == ':=':
            self.advance()
            right = self.parse_expr()
            return (':=', left, right)
        return left

    def parse_or(self):
        left = self.parse_and()
        while self.peek().kind == 'OP' and self.peek().text == '||':
            self.advance()
            right = self.parse_and()
            left = ('||', left, right)
        return left

    def parse_and(self):
        left = self.parse_cmp()
        while self.peek().kind == 'OP' and self.peek().text == '&&':
            self.advance()
            right = self.parse_cmp()
            left = ('&&', left, right)
        return left

    def parse_cmp(self):
        left = self.parse_cat()
        tok = self.peek()
        if tok.kind == 'OP' and tok.text in CMP_OPS:
            op = tok.text
            self.advance()
            right = self.parse_cat()
            left = (op, left, right)
        return left

    def parse_cat(self):
        left = self.parse_add()
        tok = self.peek()
        if tok.kind == 'OP' and tok.text == '++':
            self.advance()
            right = self.parse_cat()
            left = ('++', left, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek().kind == 'OP' and self.peek().text in ('+', '-'):
            op = self.peek().text
            self.advance()
            right = self.parse_mul()
            left = (op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek().kind == 'OP' and self.peek().text in ('*', '/', '%'):
            op = self.peek().text
            self.advance()
            right = self.parse_unary()
            left = (op, left, right)
        return left

    def parse_unary(self):
        tok = self.peek()
        if tok.kind == 'OP' and tok.text == '-':
            self.advance()
            operand = self.parse_unary()
            return ('neg', operand)
        if tok.kind == 'OP' and tok.text == '!':
            self.advance()
            operand = self.parse_unary()
            return ('deref', operand)
        if tok.kind == 'IDENT' and tok.text == 'ref':
            self.advance()
            operand = self.parse_unary()
            return ('ref', operand)
        return self.parse_app()

    def parse_app(self):
        left = self.parse_postfix()
        while can_start_atom(self.peek()):
            arg = self.parse_postfix()
            left = ('app', left, arg)
        return left

    def parse_postfix(self):
        node = self.parse_atom()
        while self.peek().kind == 'OP' and self.peek().text == '.':
            self.advance()
            name = self.expect_ident_nonreserved()
            node = ('field', node, name)
        return node

    def parse_atom(self):
        tok = self.peek()
        if tok.kind == 'INT':
            self.advance()
            return ('int', int(tok.text))
        if tok.kind == 'STRING':
            self.advance()
            return ('str', tok.text)
        if tok.kind == 'IDENT':
            if tok.text == 'true':
                self.advance()
                return ('bool', True)
            if tok.text == 'false':
                self.advance()
                return ('bool', False)
            if tok.text in RESERVED:
                raise MiniError('parse')
            self.advance()
            return ('var', tok.text)
        if tok.kind == 'OP' and tok.text == '(':
            self.advance()
            e = self.parse_expr()
            self.expect_op(')')
            return e
        if tok.kind == 'OP' and tok.text == '{':
            return self.parse_record()
        raise MiniError('parse')

    def parse_record(self):
        self.expect_op('{')
        fields = []
        if not (self.peek().kind == 'OP' and self.peek().text == '}'):
            name = self.expect_ident_nonreserved()
            self.expect_op('=')
            e = self.parse_expr()
            fields.append((name, e))
            while self.peek().kind == 'OP' and self.peek().text == ',':
                self.advance()
                name = self.expect_ident_nonreserved()
                self.expect_op('=')
                e = self.parse_expr()
                fields.append((name, e))
        self.expect_op('}')
        check_no_dup_names([f[0] for f in fields], 'dup_field')
        return ('record', fields)

    # ---- patterns ----

    def parse_pattern(self):
        tok = self.peek()
        if tok.kind == 'INT':
            self.advance()
            return ('pint', int(tok.text))
        if tok.kind == 'STRING':
            self.advance()
            return ('pstr', tok.text)
        if tok.kind == 'IDENT':
            if tok.text == '_':
                self.advance()
                return ('wildcard',)
            if tok.text == 'true':
                self.advance()
                return ('pbool', True)
            if tok.text == 'false':
                self.advance()
                return ('pbool', False)
            if tok.text in RESERVED:
                raise MiniError('parse')
            self.advance()
            return ('pvar', tok.text)
        if tok.kind == 'OP' and tok.text == '{':
            return self.parse_record_pattern()
        raise MiniError('parse')

    def parse_record_pattern(self):
        self.expect_op('{')
        fields = []
        if not (self.peek().kind == 'OP' and self.peek().text == '}'):
            name = self.expect_ident_nonreserved()
            self.expect_op('=')
            p = self.parse_pattern()
            fields.append((name, p))
            while self.peek().kind == 'OP' and self.peek().text == ',':
                self.advance()
                name = self.expect_ident_nonreserved()
                self.expect_op('=')
                p = self.parse_pattern()
                fields.append((name, p))
        self.expect_op('}')
        check_no_dup_names([f[0] for f in fields], 'dup_field')
        return ('precord', fields)


# --------------------------------------------------------------------------
# Runtime values
# --------------------------------------------------------------------------


class Closure:
    __slots__ = ('param', 'body', 'env')

    def __init__(self, param, body, env):
        self.param = param
        self.body = body
        self.env = env


class Cell:
    __slots__ = ('value',)

    def __init__(self, value):
        self.value = value


UNINIT = object()


class Env:
    __slots__ = ('vars', 'parent')

    def __init__(self, vars, parent):
        self.vars = vars
        self.parent = parent

    def lookup(self, name):
        e = self
        while e is not None:
            if name in e.vars:
                v = e.vars[name]
                if v is UNINIT:
                    raise MiniError('uninit')
                return v
            e = e.parent
        raise MiniError('unbound')


# --------------------------------------------------------------------------
# Evaluator
# --------------------------------------------------------------------------


def trunc_div(a, b):
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return q


def eval_cmp(op, av, bv):
    if op in ('==', '!='):
        ta, tb = type(av), type(bv)
        if ta is bool and tb is bool:
            eq = (av == bv)
        elif ta is int and tb is int:
            eq = (av == bv)
        elif ta is str and tb is str:
            eq = (av == bv)
        elif isinstance(av, Cell) and isinstance(bv, Cell):
            eq = (av is bv)
        else:
            raise MiniError('type')
        return eq if op == '==' else not eq
    else:
        ta, tb = type(av), type(bv)
        if ta is int and tb is int:
            pass
        elif ta is str and tb is str:
            pass
        else:
            raise MiniError('type')
        if op == '<':
            return av < bv
        if op == '<=':
            return av <= bv
        if op == '>':
            return av > bv
        return av >= bv


def match_pattern(pat, value, bindings):
    tag = pat[0]
    if tag == 'wildcard':
        return True
    if tag == 'pvar':
        bindings[pat[1]] = value
        return True
    if tag == 'pint':
        return type(value) is int and value == pat[1]
    if tag == 'pstr':
        return type(value) is str and value == pat[1]
    if tag == 'pbool':
        return type(value) is bool and value == pat[1]
    if tag == 'precord':
        if not isinstance(value, dict):
            return False
        for name, subpat in pat[1]:
            if name not in value:
                return False
            if not match_pattern(subpat, value[name], bindings):
                return False
        return True
    raise MiniError('parse')  # unreachable


def eval_expr(node, env):
    tag = node[0]

    if tag == 'int' or tag == 'str' or tag == 'bool':
        return node[1]

    if tag == 'var':
        return env.lookup(node[1])

    if tag == 'let':
        _, name, e1, e2 = node
        v1 = eval_expr(e1, env)
        new_env = Env({name: v1}, env)
        return eval_expr(e2, new_env)

    if tag == 'letrec':
        _, bindings, body = node
        slots = {name: UNINIT for name, _e in bindings}
        new_env = Env(slots, env)
        for name, e in bindings:
            v = eval_expr(e, new_env)
            new_env.vars[name] = v
        return eval_expr(body, new_env)

    if tag == 'if':
        _, c, a, b = node
        cv = eval_expr(c, env)
        if type(cv) is not bool:
            raise MiniError('type')
        return eval_expr(a, env) if cv else eval_expr(b, env)

    if tag == 'fun':
        _, param, body = node
        return Closure(param, body, env)

    if tag == 'match':
        _, e, arms = node
        v = eval_expr(e, env)
        for pat, body in arms:
            bindings = {}
            if match_pattern(pat, v, bindings):
                new_env = Env(bindings, env)
                return eval_expr(body, new_env)
        raise MiniError('no_match')

    if tag == '&&':
        _, a, b = node
        av = eval_expr(a, env)
        if type(av) is not bool:
            raise MiniError('type')
        if av is False:
            return False
        bv = eval_expr(b, env)
        if type(bv) is not bool:
            raise MiniError('type')
        return bv

    if tag == '||':
        _, a, b = node
        av = eval_expr(a, env)
        if type(av) is not bool:
            raise MiniError('type')
        if av is True:
            return True
        bv = eval_expr(b, env)
        if type(bv) is not bool:
            raise MiniError('type')
        return bv

    if tag == ':=':
        _, a, b = node
        av = eval_expr(a, env)
        bv = eval_expr(b, env)
        if not isinstance(av, Cell):
            raise MiniError('type')
        av.value = bv
        return bv

    if tag in ('==', '!=', '<', '<=', '>', '>='):
        _, a, b = node
        av = eval_expr(a, env)
        bv = eval_expr(b, env)
        return eval_cmp(tag, av, bv)

    if tag == '++':
        _, a, b = node
        av = eval_expr(a, env)
        bv = eval_expr(b, env)
        if type(av) is not str:
            raise MiniError('type')
        tb = type(bv)
        if tb is str:
            s = bv
        elif tb is bool:
            s = 'true' if bv else 'false'
        elif tb is int:
            s = str(bv)
        else:
            raise MiniError('type')
        return av + s

    if tag in ('+', '-'):
        _, a, b = node
        av = eval_expr(a, env)
        bv = eval_expr(b, env)
        if type(av) is not int:
            raise MiniError('type')
        if type(bv) is not int:
            raise MiniError('type')
        return av + bv if tag == '+' else av - bv

    if tag == '*':
        _, a, b = node
        av = eval_expr(a, env)
        bv = eval_expr(b, env)
        if type(av) is int:
            if type(bv) is not int:
                raise MiniError('type')
            return av * bv
        if type(av) is str:
            if type(bv) is not int:
                raise MiniError('type')
            return av * bv if bv > 0 else ''
        raise MiniError('type')

    if tag in ('/', '%'):
        _, a, b = node
        av = eval_expr(a, env)
        bv = eval_expr(b, env)
        if type(av) is not int:
            raise MiniError('type')
        if type(bv) is not int:
            raise MiniError('type')
        if bv == 0:
            raise MiniError('div_zero')
        if tag == '/':
            return trunc_div(av, bv)
        return av % bv

    if tag == 'neg':
        _, a = node
        av = eval_expr(a, env)
        if type(av) is not int:
            raise MiniError('type')
        return -av

    if tag == 'deref':
        _, a = node
        av = eval_expr(a, env)
        if not isinstance(av, Cell):
            raise MiniError('type')
        return av.value

    if tag == 'ref':
        _, a = node
        av = eval_expr(a, env)
        return Cell(av)

    if tag == 'app':
        _, f, a = node
        fv = eval_expr(f, env)
        av = eval_expr(a, env)
        if not isinstance(fv, Closure):
            raise MiniError('type')
        new_env = Env({fv.param: av}, fv.env)
        return eval_expr(fv.body, new_env)

    if tag == 'field':
        _, e, fname = node
        ev = eval_expr(e, env)
        if not isinstance(ev, dict):
            raise MiniError('type')
        if fname not in ev:
            raise MiniError('no_field')
        return ev[fname]

    if tag == 'record':
        _, fields = node
        result = {}
        for name, e in fields:
            result[name] = eval_expr(e, env)
        return result

    raise MiniError('parse')  # unreachable


def to_python(v):
    if type(v) is bool:
        return v
    if type(v) is int:
        return v
    if type(v) is str:
        return v
    if isinstance(v, dict):
        return {k: to_python(val) for k, val in v.items()}
    if isinstance(v, Closure):
        return "<fn>"
    if isinstance(v, Cell):
        return "<ref>"
    raise MiniError('type')  # unreachable


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------


def run(source):
    tokens = tokenize(source)
    parser = Parser(tokens)
    ast = parser.parse_expr()
    if parser.peek().kind != 'EOF':
        raise MiniError('parse')
    env = Env({}, None)
    value = eval_expr(ast, env)
    return to_python(value)
