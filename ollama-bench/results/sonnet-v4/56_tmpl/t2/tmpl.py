"""A small hand-written text template engine (pure string processing)."""

WS = ' \t\r\n\x0b\x0c'

KEYWORDS = {'true', 'false', 'none', 'not', 'and', 'or', 'in'}

FILTERS = {
    'upper': 0, 'lower': 0, 'trim': 0, 'length': 0, 'first': 0,
    'safe': 0, 'escape': 0,
    'default': 1, 'join': 1,
    'replace': 2, 'slice': 2,
}

BLOCK_NAMES = {'if', 'elif', 'else', 'endif', 'for', 'empty', 'endfor', 'set'}


class TemplateError(Exception):
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__("%s at %d" % (kind, pos))


def is_alpha(c):
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z')


def is_digit(c):
    return '0' <= c <= '9'


def is_ident_start(c):
    return is_alpha(c) or c == '_'


def is_ident_char(c):
    return is_ident_start(c) or is_digit(c)


def strip_ws(s):
    i = 0
    n = len(s)
    while i < n and s[i] in WS:
        i += 1
    j = n
    while j > i and s[j - 1] in WS:
        j -= 1
    return s[i:j]


def ascii_upper(s):
    out = []
    for c in s:
        if 'a' <= c <= 'z':
            out.append(chr(ord(c) - 32))
        else:
            out.append(c)
    return ''.join(out)


def ascii_lower(s):
    out = []
    for c in s:
        if 'A' <= c <= 'Z':
            out.append(chr(ord(c) + 32))
        else:
            out.append(c)
    return ''.join(out)


def html_escape(s):
    out = []
    for c in s:
        if c == '&':
            out.append('&amp;')
        elif c == '<':
            out.append('&lt;')
        elif c == '>':
            out.append('&gt;')
        elif c == '"':
            out.append('&#34;')
        elif c == "'":
            out.append('&#39;')
        else:
            out.append(c)
    return ''.join(out)


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

OPENERS = {'{{': ('}}', 'interp'), '{%': ('%}', 'block'), '{#': ('#}', 'comment')}


def lex(source):
    n = len(source)
    i = 0
    toks = []
    while i < n:
        if source[i] == '{' and i + 1 < n and source[i + 1] in '{%#':
            opener = source[i:i + 2]
            closer, kind = OPENERS[opener]
            start = i
            j = i + 2
            left = False
            if j < n and source[j] == '-':
                left = True
                j += 1
            content_start = j
            found = -1
            k = content_start
            while k + 2 <= n:
                if source[k:k + 2] == closer:
                    found = k
                    break
                k += 1
            if found == -1:
                raise TemplateError('unclosed_tag', start)
            body_end = found
            right = False
            if body_end > content_start and source[body_end - 1] == '-':
                right = True
                body_end -= 1
            body = source[content_start:body_end]
            tag_end = found + 2
            toks.append({'type': kind, 'body': body, 'left': left,
                          'right': right, 'start': start, 'end': tag_end})
            i = tag_end
        else:
            start = i
            i += 1
            while i < n and not (source[i] == '{' and i + 1 < n and source[i + 1] in '{%#'):
                i += 1
            toks.append({'type': 'text', 'value': source[start:i], 'start': start, 'end': i})
    return toks


def apply_trim(tokens):
    n = len(tokens)
    trimmed = {}
    for idx, tok in enumerate(tokens):
        if tok['type'] != 'text':
            continue
        s = tok['value']
        prev = tokens[idx - 1] if idx - 1 >= 0 else None
        nxt = tokens[idx + 1] if idx + 1 < n else None
        start = 0
        end = len(s)
        if prev is not None and prev['type'] != 'text' and prev.get('right'):
            while start < end and s[start] in WS:
                start += 1
        if nxt is not None and nxt['type'] != 'text' and nxt.get('left'):
            while end > start and s[end - 1] in WS:
                end -= 1
        trimmed[idx] = s[start:end]
    final = []
    for idx, tok in enumerate(tokens):
        if tok['type'] == 'text':
            final.append({'type': 'text', 'value': trimmed[idx], 'start': tok['start'], 'end': tok['end']})
        elif tok['type'] == 'comment':
            continue
        else:
            final.append(tok)
    return final


# ---------------------------------------------------------------------------
# Expression parsing
# ---------------------------------------------------------------------------

class ExprParser:
    def __init__(self, s, tag_pos):
        self.s = s
        self.n = len(s)
        self.i = 0
        self.tag_pos = tag_pos

    def skip_ws(self):
        while self.i < self.n and self.s[self.i] in WS:
            self.i += 1

    def try_match_keyword(self, kw):
        save = self.i
        self.skip_ws()
        L = len(kw)
        if self.s[self.i:self.i + L] == kw:
            after = self.i + L
            nc = self.s[after] if after < self.n else None
            if nc is None or not is_ident_char(nc):
                self.i = after
                return True
        self.i = save
        return False

    def try_match_str(self, tok):
        save = self.i
        self.skip_ws()
        L = len(tok)
        if self.s[self.i:self.i + L] == tok:
            self.i += L
            return True
        self.i = save
        return False

    def read_ident(self):
        start = self.i
        self.i += 1
        while self.i < self.n and is_ident_char(self.s[self.i]):
            self.i += 1
        return self.s[start:self.i]

    def read_int(self):
        start = self.i
        while self.i < self.n and is_digit(self.s[self.i]):
            self.i += 1
        return int(self.s[start:self.i])

    def read_string(self):
        quote = self.s[self.i]
        self.i += 1
        out = []
        while True:
            if self.i >= self.n:
                raise TemplateError('syntax', self.tag_pos)
            c = self.s[self.i]
            if c == quote:
                self.i += 1
                return ''.join(out)
            if c == '\\':
                self.i += 1
                if self.i >= self.n:
                    raise TemplateError('syntax', self.tag_pos)
                e = self.s[self.i]
                self.i += 1
                if e == 'n':
                    out.append('\n')
                elif e == 't':
                    out.append('\t')
                else:
                    out.append(e)
            else:
                out.append(c)
                self.i += 1

    def read_key(self):
        self.skip_ws()
        if self.i < self.n and is_ident_start(self.s[self.i]):
            return self.read_ident()
        if self.i < self.n and is_digit(self.s[self.i]):
            start = self.i
            while self.i < self.n and is_digit(self.s[self.i]):
                self.i += 1
            return self.s[start:self.i]
        raise TemplateError('syntax', self.tag_pos)

    def parse_atom(self):
        self.skip_ws()
        if self.i >= self.n:
            raise TemplateError('syntax', self.tag_pos)
        c = self.s[self.i]
        if is_digit(c):
            return ('num', self.read_int())
        if c == '"' or c == "'":
            return ('str', self.read_string())
        if is_ident_start(c):
            ident = self.read_ident()
            if ident == 'true':
                return ('true',)
            if ident == 'false':
                return ('false',)
            if ident == 'none':
                return ('none',)
            if ident in KEYWORDS:
                raise TemplateError('syntax', self.tag_pos)
            return ('ident', ident)
        raise TemplateError('syntax', self.tag_pos)

    def parse_primary(self):
        node = self.parse_atom()
        while True:
            save = self.i
            self.skip_ws()
            if self.i < self.n and self.s[self.i] == '.':
                self.i += 1
                key = self.read_key()
                node = ('dot', node, key)
                continue
            if self.i < self.n and self.s[self.i] == '[':
                self.i += 1
                sub = self.parse_primary()
                self.skip_ws()
                if self.i >= self.n or self.s[self.i] != ']':
                    raise TemplateError('syntax', self.tag_pos)
                self.i += 1
                node = ('sub', node, sub)
                continue
            self.i = save
            break
        return node

    def match_cmpop(self):
        if self.try_match_keyword('in'):
            return 'in'
        if self.try_match_str('=='):
            return '=='
        if self.try_match_str('!='):
            return '!='
        if self.try_match_str('<='):
            return '<='
        if self.try_match_str('>='):
            return '>='
        if self.try_match_str('<'):
            return '<'
        if self.try_match_str('>'):
            return '>'
        return None

    def parse_comparison(self):
        left = self.parse_primary()
        save = self.i
        op = self.match_cmpop()
        if op is None:
            self.i = save
            return left
        right = self.parse_primary()
        save2 = self.i
        op2 = self.match_cmpop()
        if op2 is not None:
            raise TemplateError('syntax', self.tag_pos)
        self.i = save2
        return ('cmp', op, left, right)

    def parse_negation(self):
        save = self.i
        if self.try_match_keyword('not'):
            inner = self.parse_negation()
            return ('not', inner)
        self.i = save
        return self.parse_comparison()

    def parse_conjunct(self):
        left = self.parse_negation()
        while True:
            save = self.i
            if self.try_match_keyword('and'):
                right = self.parse_negation()
                left = ('and', left, right)
            else:
                self.i = save
                break
        return left

    def parse_disjunct(self):
        left = self.parse_conjunct()
        while True:
            save = self.i
            if self.try_match_keyword('or'):
                right = self.parse_conjunct()
                left = ('or', left, right)
            else:
                self.i = save
                break
        return left

    def parse_arg_list(self):
        args = []
        while True:
            self.skip_ws()
            c = self.s[self.i] if self.i < self.n else None
            if c == '"' or c == "'":
                val = self.read_string()
                self.skip_ws()
                c2 = self.s[self.i] if self.i < self.n else None
                if c2 not in (None, '|', ','):
                    raise TemplateError('syntax', self.tag_pos)
                args.append(val)
            else:
                start = self.i
                while self.i < self.n and self.s[self.i] not in ',|':
                    self.i += 1
                raw = strip_ws(self.s[start:self.i])
                args.append(interpret_bare_arg(raw))
                c2 = self.s[self.i] if self.i < self.n else None
            if c2 == ',':
                self.i += 1
                continue
            else:
                break
        return args

    def parse_filter(self):
        self.skip_ws()
        if self.i >= self.n or not is_ident_start(self.s[self.i]):
            raise TemplateError('syntax', self.tag_pos)
        fname = self.read_ident()
        if fname not in FILTERS:
            raise TemplateError('unknown_filter', self.tag_pos)
        args = []
        self.skip_ws()
        if self.i < self.n and self.s[self.i] == ':':
            self.i += 1
            args = self.parse_arg_list()
        self.skip_ws()
        if self.i < self.n and self.s[self.i] != '|':
            raise TemplateError('syntax', self.tag_pos)
        arity = FILTERS[fname]
        if len(args) != arity:
            raise TemplateError('filter_args', self.tag_pos)
        return (fname, args)

    def parse_pipeline(self):
        node = self.parse_disjunct()
        filters = []
        while True:
            save = self.i
            self.skip_ws()
            if self.i < self.n and self.s[self.i] == '|':
                self.i += 1
                f = self.parse_filter()
                filters.append(f)
            else:
                self.i = save
                break
        return node, filters


def interpret_bare_arg(raw):
    if raw != '' and all(is_digit(ch) for ch in raw):
        return int(raw)
    if raw == 'true':
        return True
    if raw == 'false':
        return False
    if raw == 'none':
        return None
    return raw


def parse_condition(rest, tag_pos):
    p = ExprParser(rest, tag_pos)
    node = p.parse_disjunct()
    p.skip_ws()
    if p.i != p.n:
        raise TemplateError('syntax', tag_pos)
    return node


def parse_expr_with_filters(rest, tag_pos):
    p = ExprParser(rest, tag_pos)
    node, filters = p.parse_pipeline()
    p.skip_ws()
    if p.i != p.n:
        raise TemplateError('syntax', tag_pos)
    return node, filters


def parse_for_rest(rest, tag_pos):
    p = ExprParser(rest, tag_pos)
    p.skip_ws()
    if p.i >= p.n or not is_ident_start(p.s[p.i]):
        raise TemplateError('syntax', tag_pos)
    name = p.read_ident()
    if name in KEYWORDS:
        raise TemplateError('syntax', tag_pos)
    if not p.try_match_keyword('in'):
        raise TemplateError('syntax', tag_pos)
    node, filters = p.parse_pipeline()
    p.skip_ws()
    if p.i != p.n:
        raise TemplateError('syntax', tag_pos)
    return name, node, filters


def parse_set_rest(rest, tag_pos):
    p = ExprParser(rest, tag_pos)
    p.skip_ws()
    if p.i >= p.n or not is_ident_start(p.s[p.i]):
        raise TemplateError('syntax', tag_pos)
    name = p.read_ident()
    if name in KEYWORDS:
        raise TemplateError('syntax', tag_pos)
    p.skip_ws()
    if p.i >= p.n or p.s[p.i] != '=':
        raise TemplateError('syntax', tag_pos)
    if p.i + 1 < p.n and p.s[p.i + 1] == '=':
        raise TemplateError('syntax', tag_pos)
    p.i += 1
    node, filters = p.parse_pipeline()
    p.skip_ws()
    if p.i != p.n:
        raise TemplateError('syntax', tag_pos)
    return name, node, filters


# ---------------------------------------------------------------------------
# Parser (block structure)
# ---------------------------------------------------------------------------

def parse(tokens):
    root = []
    stack = []

    def current_target():
        if not stack:
            return root
        top = stack[-1]
        if top['kind'] == 'if':
            if top['seen_else']:
                return top['else_body']
            return top['clauses'][-1][2]
        else:
            if top['seen_empty']:
                return top['empty_body']
            return top['body']

    for tok in tokens:
        if tok['type'] == 'text':
            current_target().append(('text', tok['value']))
            continue
        if tok['type'] == 'interp':
            body = strip_ws(tok['body'])
            if body == '':
                raise TemplateError('syntax', tok['start'])
            node, filters = parse_expr_with_filters(body, tok['start'])
            current_target().append(('interp', node, filters, tok['start']))
            continue

        # block tag
        raw = tok['body']
        body = strip_ws(raw)
        pos = tok['start']
        if body == '':
            raise TemplateError('unknown_tag', pos)
        i = 0
        blen = len(body)
        while i < blen and body[i] not in WS:
            i += 1
        name = body[:i]
        rest = strip_ws(body[i:])

        if name not in BLOCK_NAMES:
            raise TemplateError('unknown_tag', pos)

        if name == 'if':
            if rest == '':
                raise TemplateError('syntax', pos)
            cond = parse_condition(rest, pos)
            target = current_target()
            target.append(None)
            frame = {'kind': 'if', 'pos': pos, 'parent': target, 'idx': len(target) - 1,
                     'clauses': [[cond, pos, []]], 'else_body': None, 'seen_else': False}
            stack.append(frame)

        elif name == 'elif':
            if not stack or stack[-1]['kind'] != 'if' or stack[-1]['seen_else']:
                raise TemplateError('unexpected_tag', pos)
            if rest == '':
                raise TemplateError('syntax', pos)
            cond = parse_condition(rest, pos)
            stack[-1]['clauses'].append([cond, pos, []])

        elif name == 'else':
            if not stack or stack[-1]['kind'] != 'if' or stack[-1]['seen_else']:
                raise TemplateError('unexpected_tag', pos)
            if rest != '':
                raise TemplateError('syntax', pos)
            stack[-1]['seen_else'] = True
            stack[-1]['else_body'] = []

        elif name == 'endif':
            if not stack or stack[-1]['kind'] != 'if':
                raise TemplateError('unexpected_tag', pos)
            if rest != '':
                raise TemplateError('syntax', pos)
            frame = stack.pop()
            clauses_final = [(c[0], c[1], c[2]) for c in frame['clauses']]
            node = ('if', clauses_final, frame['else_body'])
            frame['parent'][frame['idx']] = node

        elif name == 'for':
            var_name, expr_node, filters = parse_for_rest(rest, pos)
            target = current_target()
            target.append(None)
            frame = {'kind': 'for', 'pos': pos, 'parent': target, 'idx': len(target) - 1,
                     'name': var_name, 'expr': expr_node, 'filters': filters,
                     'body': [], 'empty_body': None, 'seen_empty': False}
            stack.append(frame)

        elif name == 'empty':
            if not stack or stack[-1]['kind'] != 'for' or stack[-1]['seen_empty']:
                raise TemplateError('unexpected_tag', pos)
            if rest != '':
                raise TemplateError('syntax', pos)
            stack[-1]['seen_empty'] = True
            stack[-1]['empty_body'] = []

        elif name == 'endfor':
            if not stack or stack[-1]['kind'] != 'for':
                raise TemplateError('unexpected_tag', pos)
            if rest != '':
                raise TemplateError('syntax', pos)
            frame = stack.pop()
            node = ('for', frame['name'], frame['expr'], frame['filters'], frame['pos'],
                    frame['body'], frame['empty_body'])
            frame['parent'][frame['idx']] = node

        elif name == 'set':
            var_name, expr_node, filters = parse_set_rest(rest, pos)
            current_target().append(('set', var_name, expr_node, filters, pos))

    if stack:
        raise TemplateError('unclosed_block', stack[-1]['pos'])

    return root


# ---------------------------------------------------------------------------
# Values
# ---------------------------------------------------------------------------

class V:
    __slots__ = ('t', 'v', 'safe')

    def __init__(self, t, v, safe=False):
        self.t = t
        self.v = v
        self.safe = safe


def undef():
    return V('undefined', None, False)


def from_py(x):
    if x is None:
        return V('none', None)
    if isinstance(x, bool):
        return V('bool', x)
    if isinstance(x, int):
        return V('number', x)
    if isinstance(x, str):
        return V('string', x)
    if isinstance(x, list):
        return V('list', [from_py(e) for e in x])
    if isinstance(x, dict):
        d = {}
        for k, val in x.items():
            d[k] = from_py(val)
        return V('map', d)
    return V('string', str(x))


def py_const_to_v(x):
    if x is None:
        return V('none', None, False)
    if isinstance(x, bool):
        return V('bool', x, False)
    if isinstance(x, int):
        return V('number', x, False)
    return V('string', x, False)


def text_of(v):
    if v.t == 'undefined' or v.t == 'none':
        return ''
    if v.t == 'bool':
        return 'true' if v.v else 'false'
    if v.t == 'number':
        return str(v.v)
    if v.t == 'string':
        return v.v
    if v.t == 'list':
        return '[' + ', '.join(text_of(e) for e in v.v) + ']'
    if v.t == 'map':
        parts = []
        for k, val in v.v.items():
            parts.append(k + ': ' + text_of(val))
        return '{' + ', '.join(parts) + '}'
    return ''


def truthy(v):
    if v.t in ('undefined', 'none'):
        return False
    if v.t == 'bool':
        return v.v is True
    if v.t == 'number':
        return v.v != 0
    if v.t == 'string':
        return v.v not in ('', '0', 'false')
    if v.t == 'list':
        return len(v.v) != 0
    if v.t == 'map':
        return len(v.v) != 0
    return True


def veq(a, b):
    if a.t != b.t:
        return False
    if a.t in ('undefined', 'none'):
        return True
    if a.t in ('number', 'string', 'bool'):
        return a.v == b.v
    if a.t == 'list':
        if len(a.v) != len(b.v):
            return False
        return all(veq(x, y) for x, y in zip(a.v, b.v))
    if a.t == 'map':
        if len(a.v) != len(b.v):
            return False
        for k, val in a.v.items():
            if k not in b.v:
                return False
            if not veq(val, b.v[k]):
                return False
        return True
    return False


def in_op(x, y):
    if y.t == 'string':
        return x.t == 'string' and (x.v in y.v)
    if y.t == 'list':
        return any(veq(x, item) for item in y.v)
    if y.t == 'map':
        return x.t == 'string' and (x.v in y.v)
    return False


def lookup(base, key):
    if base.t in ('undefined', 'none'):
        return undef()
    if base.t == 'map' and key.t == 'string' and key.v in base.v:
        return base.v[key.v]
    if base.t in ('list', 'string'):
        idx = None
        if key.t == 'number':
            idx = key.v
        elif key.t == 'string' and key.v != '' and all(is_digit(c) for c in key.v):
            idx = int(key.v)
        if idx is not None:
            length = len(base.v)
            if 0 <= idx < length:
                if base.t == 'list':
                    return base.v[idx]
                else:
                    return V('string', base.v[idx])
            else:
                return undef()
    if key.t == 'string':
        if key.v == 'size':
            if base.t in ('string', 'list', 'map'):
                return V('number', len(base.v))
            return undef()
        if key.v == 'keys':
            if base.t == 'map':
                return V('list', [V('string', k) for k in base.v.keys()])
            return undef()
        if key.v == 'type':
            return V('string', base.t)
    return undef()


def compare_rel(op, a, b, tag_pos):
    if (a.t == 'number' and b.t == 'number') or (a.t == 'string' and b.t == 'string'):
        x, y = a.v, b.v
    else:
        raise TemplateError('bad_operand', tag_pos)
    if op == '<':
        return x < y
    if op == '<=':
        return x <= y
    if op == '>':
        return x > y
    if op == '>=':
        return x >= y


def apply_filter(v, name, args):
    if name == 'safe':
        return V(v.t, v.v, True)
    if name == 'escape':
        return V('string', html_escape(text_of(v)), True)
    if name == 'upper':
        return V('string', ascii_upper(text_of(v)), v.safe)
    if name == 'lower':
        return V('string', ascii_lower(text_of(v)), v.safe)
    if name == 'trim':
        return V('string', strip_ws(text_of(v)), v.safe)
    if name == 'length':
        if v.t in ('undefined', 'none', 'bool'):
            n = 0
        elif v.t == 'number':
            n = len(str(abs(v.v)))
        elif v.t == 'string':
            n = len(v.v)
        elif v.t == 'list':
            n = len(v.v)
        elif v.t == 'map':
            n = len(v.v)
        else:
            n = 0
        return V('number', n, v.safe)
    if name == 'first':
        if v.t == 'string':
            if v.v:
                return V('string', v.v[0], v.safe)
            return V('undefined', None, v.safe)
        if v.t == 'list':
            if v.v:
                item = v.v[0]
                return V(item.t, item.v, v.safe)
            return V('undefined', None, v.safe)
        if v.t == 'map':
            if v.v:
                k = next(iter(v.v))
                return V('string', k, v.safe)
            return V('undefined', None, v.safe)
        return V('undefined', None, v.safe)
    if name == 'default':
        x = args[0]
        if not truthy(v):
            return py_const_to_v(x)
        return V(v.t, v.v, v.safe)
    if name == 'join':
        sv = py_const_to_v(args[0])
        sep = text_of(sv)
        if v.t == 'list':
            joined = sep.join(text_of(item) for item in v.v)
        elif v.t == 'string':
            joined = sep.join(list(v.v))
        elif v.t == 'map':
            joined = sep.join(v.v.keys())
        elif v.t in ('undefined', 'none'):
            joined = ''
        elif v.t in ('number', 'bool'):
            joined = text_of(v)
        else:
            joined = ''
        return V('string', joined, v.safe)
    if name == 'replace':
        a_txt = text_of(py_const_to_v(args[0]))
        b_txt = text_of(py_const_to_v(args[1]))
        t = text_of(v)
        if a_txt == '':
            res = t
        else:
            res = t.replace(a_txt, b_txt)
        return V('string', res, v.safe)
    if name == 'slice':
        ok1, start_val = interp_slice_num(args[0])
        ok2, len_val = interp_slice_num(args[1])
        if not (ok1 and ok2):
            return V(v.t, v.v, v.safe)
        if v.t == 'list':
            return V('list', v.v[start_val:start_val + len_val], v.safe)
        if v.t == 'string':
            s = v.v
        else:
            s = text_of(v)
        return V('string', s[start_val:start_val + len_val], v.safe)
    raise AssertionError('unreachable filter %r' % (name,))


def interp_slice_num(x):
    if isinstance(x, bool):
        return (False, 0)
    if isinstance(x, int):
        return (x >= 0, x)
    if isinstance(x, str):
        if x != '' and all(is_digit(c) for c in x):
            return (True, int(x))
        return (False, 0)
    return (False, 0)


# ---------------------------------------------------------------------------
# Evaluation / rendering
# ---------------------------------------------------------------------------

def evaluate(node, scopes, tag_pos):
    kind = node[0]
    if kind == 'num':
        return V('number', node[1])
    if kind == 'str':
        return V('string', node[1])
    if kind == 'true':
        return V('bool', True)
    if kind == 'false':
        return V('bool', False)
    if kind == 'none':
        return V('none', None)
    if kind == 'ident':
        name = node[1]
        for scope in reversed(scopes):
            if name in scope:
                return scope[name]
        return undef()
    if kind == 'dot':
        base = evaluate(node[1], scopes, tag_pos)
        key = V('string', node[2])
        return lookup(base, key)
    if kind == 'sub':
        base = evaluate(node[1], scopes, tag_pos)
        keyv = evaluate(node[2], scopes, tag_pos)
        return lookup(base, keyv)
    if kind == 'not':
        inner = evaluate(node[1], scopes, tag_pos)
        return V('bool', not truthy(inner))
    if kind == 'and':
        left = evaluate(node[1], scopes, tag_pos)
        if not truthy(left):
            return V('bool', False)
        right = evaluate(node[2], scopes, tag_pos)
        return V('bool', truthy(right))
    if kind == 'or':
        left = evaluate(node[1], scopes, tag_pos)
        if truthy(left):
            return V('bool', True)
        right = evaluate(node[2], scopes, tag_pos)
        return V('bool', truthy(right))
    if kind == 'cmp':
        op = node[1]
        left = evaluate(node[2], scopes, tag_pos)
        right = evaluate(node[3], scopes, tag_pos)
        if op == '==':
            return V('bool', veq(left, right))
        if op == '!=':
            return V('bool', not veq(left, right))
        if op == 'in':
            return V('bool', in_op(left, right))
        return V('bool', compare_rel(op, left, right, tag_pos))
    raise AssertionError('unreachable node %r' % (node,))


def evaluate_pipeline(node, filters, scopes, tag_pos):
    v = evaluate(node, scopes, tag_pos)
    for fname, fargs in filters:
        v = apply_filter(v, fname, fargs)
    return v


def render_nodes(nodes, scopes, out):
    for node in nodes:
        render_node(node, scopes, out)


def render_node(node, scopes, out):
    kind = node[0]
    if kind == 'text':
        out.append(node[1])
        return
    if kind == 'interp':
        _, expr, filters, pos = node
        v = evaluate_pipeline(expr, filters, scopes, pos)
        t = text_of(v)
        if not v.safe:
            t = html_escape(t)
        out.append(t)
        return
    if kind == 'if':
        _, clauses, else_body = node
        for cond, cpos, body in clauses:
            v = evaluate(cond, scopes, cpos)
            if truthy(v):
                render_nodes(body, scopes, out)
                return
        if else_body is not None:
            render_nodes(else_body, scopes, out)
        return
    if kind == 'for':
        _, name, expr, filters, pos, body, empty_body = node
        seqv = evaluate_pipeline(expr, filters, scopes, pos)
        if seqv.t in ('number', 'bool'):
            raise TemplateError('not_iterable', pos)
        if seqv.t == 'list':
            items = seqv.v
        elif seqv.t == 'string':
            items = [V('string', c) for c in seqv.v]
        elif seqv.t == 'map':
            items = [V('string', k) for k in seqv.v.keys()]
        else:
            items = []
        if not items:
            if empty_body is not None:
                render_nodes(empty_body, scopes, out)
            return
        new_scope = {}
        scopes.append(new_scope)
        n = len(items)
        for idx, item in enumerate(items):
            new_scope[name] = item
            loopmap = {
                'index': V('number', idx + 1),
                'index0': V('number', idx),
                'first': V('bool', idx == 0),
                'last': V('bool', idx == n - 1),
                'length': V('number', n),
            }
            new_scope['loop'] = V('map', loopmap)
            render_nodes(body, scopes, out)
        scopes.pop()
        return
    if kind == 'set':
        _, name, expr, filters, pos = node
        v = evaluate_pipeline(expr, filters, scopes, pos)
        scopes[-1][name] = v
        return
    raise AssertionError('unreachable node %r' % (node,))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render(source, context):
    tokens = lex(source)
    tokens = apply_trim(tokens)
    nodes = parse(tokens)
    root_scope = {}
    for k, val in context.items():
        root_scope[k] = from_py(val)
    scopes = [root_scope]
    out = []
    render_nodes(nodes, scopes, out)
    return ''.join(out)
