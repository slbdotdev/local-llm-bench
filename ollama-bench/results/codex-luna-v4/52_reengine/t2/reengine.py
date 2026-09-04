"""A small, deliberately self-contained backtracking regular-expression engine."""


class PatternError(ValueError):
    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind)


_DIGITS = set("0123456789")
_WORD = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")
_SPACE = set(" \t\n\r\f\v")


class _Parser:
    def __init__(self, pattern):
        self.s = pattern
        self.i = 0
        self.groups = 0

    def error(self, kind):
        raise PatternError(kind)

    def expression(self, in_group=False):
        branches = [self.branch()]
        while self.i < len(self.s) and self.s[self.i] == '|':
            self.i += 1
            branches.append(self.branch())
        if in_group:
            if self.i >= len(self.s) or self.s[self.i] != ')':
                self.error('unbalanced_paren')
            self.i += 1
        elif self.i < len(self.s) and self.s[self.i] == ')':
            self.error('unbalanced_paren')
        return ('alt', branches)

    def branch(self):
        items = []
        while self.i < len(self.s) and self.s[self.i] not in '|)':
            atom = self.atom()
            if self.i < len(self.s):
                q = self.quantifier_at(self.i)
                if q is not None:
                    if atom[0] == 'anchor':
                        # Bounded-repeat validation precedes this check.
                        if q[4] is not None and q[1] > q[2]:
                            self.error('bad_repeat')
                        self.error('anchor_repeat')
                    if q[4] is not None and q[1] > q[2]:
                        self.error('bad_repeat')
                    self.i = q[0]
                    if self.i < len(self.s) and self.s[self.i] == '?':
                        greedy = False
                        self.i += 1
                    else:
                        greedy = True
                    if self.i < len(self.s) and self.quantifier_at(self.i) is not None:
                        self.error('multiple_repeat')
                    atom = ('repeat', atom, q[1], q[2], greedy)
            items.append(atom)
        return ('seq', items)

    def quantifier_at(self, p):
        if p >= len(self.s):
            return None
        c = self.s[p]
        if c == '*': return (p + 1, 0, None, True, None)
        if c == '+': return (p + 1, 1, None, True, None)
        if c == '?': return (p + 1, 0, 1, False, None)
        if c != '{': return None
        j = p + 1
        a = j
        while j < len(self.s) and self.s[j] in _DIGITS: j += 1
        lo_text = self.s[a:j]
        if j < len(self.s) and self.s[j] == '}' and lo_text:
            return (j + 1, int(lo_text), int(lo_text), True, True)
        if j < len(self.s) and self.s[j] == ',':
            j += 1
            b = j
            while j < len(self.s) and self.s[j] in _DIGITS: j += 1
            hi_text = self.s[b:j]
            if j < len(self.s) and self.s[j] == '}':
                return (j + 1, int(lo_text) if lo_text else 0,
                        int(hi_text) if hi_text else None, True, True)
        return None

    def atom(self):
        if self.i >= len(self.s):
            self.error('unbalanced_paren')
        c = self.s[self.i]
        self.i += 1
        if c == '(':
            capturing = True
            if self.i < len(self.s) and self.s[self.i] == '?':
                self.i += 1
                if self.i >= len(self.s) or self.s[self.i] != ':':
                    self.error('bad_group')
                self.i += 1
                capturing = False
            number = None
            if capturing:
                self.groups += 1
                number = self.groups - 1
            body = self.expression(True)
            return ('group', body, number) if capturing else body
        if c == '[':
            return self.char_class()
        if c == '.': return ('dot',)
        if c in '^$': return ('anchor', c)
        if c == '\\': return self.escape(False)
        if c in '*+?':
            self.error('nothing_to_repeat')
        if c == '{' and self.quantifier_at(self.i - 1) is not None:
            self.error('nothing_to_repeat')
        return ('lit', c)

    def escape(self, inside):
        if self.i >= len(self.s): self.error('trailing_backslash')
        c = self.s[self.i]; self.i += 1
        if c in 'dDwWsS': return ('classesc', c) if not inside else ('memberesc', c)
        if c in 'ntrfv':
            return (('member', {'n':'\n','t':'\t','r':'\r','f':'\f','v':'\v'}[c])
                    if inside else ('lit', {'n':'\n','t':'\t','r':'\r','f':'\f','v':'\v'}[c]))
        if inside and c == 'b': return ('member', '\b')
        if not inside and c in 'bB': return ('anchor', c)
        if c == 'B' and inside: self.error('bad_escape')
        if c.isascii() and (c.isalpha() or c.isdigit()): self.error('bad_escape')
        return ('lit', c) if not inside else ('member', c)

    def char_class(self):
        neg = False
        if self.i < len(self.s) and self.s[self.i] == '^':
            neg = True; self.i += 1
        members = []
        if self.i < len(self.s) and self.s[self.i] == ']':
            members.append(('member', ']')); self.i += 1
        while True:
            if self.i >= len(self.s): self.error('unterminated_class')
            if self.s[self.i] == ']':
                self.i += 1
                return ('class', neg, members)
            if self.s[self.i] == '\\':
                self.i += 1
                m = self.escape(True)
            else:
                m = ('member', self.s[self.i]); self.i += 1
            if self.i < len(self.s) and self.s[self.i] == '-' and self.i + 1 < len(self.s) and self.s[self.i + 1] != ']':
                self.i += 1
                if self.s[self.i] == '\\':
                    self.i += 1
                    n = self.escape(True)
                else:
                    n = ('member', self.s[self.i]); self.i += 1
                if m[0] == 'memberesc' or n[0] == 'memberesc': self.error('bad_range')
                if ord(m[1]) > ord(n[1]): self.error('bad_range')
                members.append(('range', m[1], n[1]))
            else:
                members.append(m)


def _in_class(ch, members):
    for m in members:
        if m[0] == 'member' and ch == m[1]: return True
        if m[0] == 'range' and m[1] <= ch <= m[2]: return True
        if m[0] == 'memberesc':
            if m[1] in 'dD': ok = ch in _DIGITS
            elif m[1] in 'wW': ok = ch in _WORD
            else: ok = ch in _SPACE
            if m[1].isupper(): ok = not ok
            if ok: return True
    return False


def _matches(node, text, pos, caps):
    kind = node[0]
    if kind == 'lit':
        if pos < len(text) and text[pos] == node[1]: yield pos + 1, caps
    elif kind == 'dot':
        if pos < len(text) and text[pos] != '\n': yield pos + 1, caps
    elif kind == 'class':
        if pos < len(text) and (_in_class(text[pos], node[2]) != node[1]): yield pos + 1, caps
    elif kind == 'anchor':
        ok = (pos == 0) if node[1] == '^' else (pos == len(text) or (pos == len(text)-1 and text.endswith('\n')))
        if node[1] in 'bB':
            left = pos > 0 and text[pos-1] in _WORD
            right = pos < len(text) and text[pos] in _WORD
            ok = (left != right) if node[1] == 'b' else (left == right)
        if ok: yield pos, caps
    elif kind == 'classesc':
        if pos < len(text):
            ch = text[pos]
            base = _DIGITS if node[1].lower() == 'd' else _WORD if node[1].lower() == 'w' else _SPACE
            if (ch in base) == node[1].islower(): yield pos + 1, caps
    elif kind == 'seq':
        yield from _sequence(node[1], 0, text, pos, caps)
    elif kind == 'alt':
        for branch in node[1]: yield from _matches(branch, text, pos, caps)
    elif kind == 'group':
        start = pos
        for end, nc in _matches(node[1], text, pos, caps[:]):
            nc = nc[:]; nc[node[2]] = (start, end)
            yield end, nc
    elif kind == 'repeat':
        yield from _repeat(node[1], node[2], node[3], node[4], text, pos, caps)


def _sequence(items, i, text, pos, caps):
    if i == len(items):
        yield pos, caps; return
    for end, nc in _matches(items[i], text, pos, caps):
        yield from _sequence(items, i + 1, text, end, nc)


def _repeat(body, lo, hi, greedy, text, pos, caps):
    def rec(count, cur, state, previous_start):
        mandatory = count < lo
        can_more = hi is None or count < hi
        allowed = mandatory or (can_more and (count == 0 or cur != previous_start))
        if mandatory:
            for end, ns in _matches(body, text, cur, state[:]):
                yield from rec(count + 1, end, ns, cur)
            return
        if greedy and allowed:
            for end, ns in _matches(body, text, cur, state[:]):
                yield from rec(count + 1, end, ns, cur)
        if count >= lo:
            yield cur, state
        if not greedy and allowed:
            for end, ns in _matches(body, text, cur, state[:]):
                yield from rec(count + 1, end, ns, cur)
    yield from rec(0, pos, caps, pos)


def search(pattern, text):
    parser = _Parser(pattern)
    tree = parser.expression(False)
    for start in range(len(text) + 1):
        initial = [None] * parser.groups
        for end, caps in _matches(tree, text, start, initial):
            return (start, end, caps)
    return None
