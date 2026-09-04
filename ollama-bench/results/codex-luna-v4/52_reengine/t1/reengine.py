"""A small backtracking regular-expression engine for the specified syntax."""

_DIGITS = frozenset("0123456789")
_WORD = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")
_SPACE = frozenset(" \t\n\r\f\v")


class PatternError(ValueError):
    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind)


def _error(kind):
    raise PatternError(kind)


class _Parser:
    def __init__(self, pattern):
        self.s = pattern
        self.i = 0
        self.groups = 0

    def parse(self):
        node = self._expression(False)
        if self.i != len(self.s):
            if self.s[self.i] == ')':
                _error("unbalanced_paren")
        return node, self.groups

    def _expression(self, in_group):
        branches = [self._branch(in_group)]
        while self.i < len(self.s) and self.s[self.i] == '|':
            self.i += 1
            branches.append(self._branch(in_group))
        if in_group:
            if self.i >= len(self.s):
                _error("unbalanced_paren")
            if self.s[self.i] != ')':
                _error("unbalanced_paren")
            self.i += 1
        return _Alt(branches) if len(branches) > 1 else branches[0]

    def _branch(self, in_group):
        items = []
        while self.i < len(self.s) and self.s[self.i] not in "|)":
            if self._is_quantifier_start(self.i):
                _error("nothing_to_repeat")
            atom = self._atom()
            if self._is_quantifier_start(self.i):
                lo, hi, end = self._read_quantifier(self.i)
                self.i = end
                nongreedy = False
                if self.i < len(self.s) and self.s[self.i] == '?':
                    nongreedy = True
                    self.i += 1
                if hi is not None and lo > hi:
                    _error("bad_repeat")
                if atom.anchor:
                    _error("anchor_repeat")
                if self._is_quantifier_start(self.i):
                    _error("multiple_repeat")
                atom = _Repeat(atom, lo, hi, nongreedy)
            items.append(atom)
        return _Seq(items)

    def _atom(self):
        if self.i >= len(self.s):
            _error("nothing_to_repeat")
        c = self.s[self.i]
        self.i += 1
        if c == '(':
            capturing = True
            if self.i < len(self.s) and self.s[self.i] == '?':
                self.i += 1
                if self.i >= len(self.s) or self.s[self.i] != ':':
                    _error("bad_group")
                self.i += 1
                capturing = False
            number = None
            if capturing:
                self.groups += 1
                number = self.groups
            body = self._expression(True)
            return _Group(body, number)
        if c == ')':
            _error("unbalanced_paren")
        if c == '[':
            return self._class()
        if c == '.':
            return _Char(lambda x: x != '\n')
        if c == '^':
            return _Anchor(lambda p, t: p == 0)
        if c == '$':
            return _Anchor(lambda p, t: p == len(t) or (p == len(t) - 1 and t.endswith('\n')))
        if c == '\\':
            return self._escape(False)
        return _Char(lambda x, wanted=c: x == wanted)

    def _escape(self, inside_class):
        if self.i >= len(self.s):
            _error("trailing_backslash")
        c = self.s[self.i]
        self.i += 1
        if inside_class and c == 'B':
            _error("bad_escape")
        sets = {'d': _DIGITS, 'w': _WORD, 's': _SPACE,
                'D': None, 'W': None, 'S': None}
        if c in sets:
            base = {'d': _DIGITS, 'w': _WORD, 's': _SPACE,
                    'D': _DIGITS, 'W': _WORD, 'S': _SPACE}[c]
            if c in 'DWS':
                return _Char(lambda x, b=base: x not in b)
            return _Char(lambda x, b=base: x in b)
        if c in 'ntrfv':
            value = {'n': '\n', 't': '\t', 'r': '\r', 'f': '\f', 'v': '\v'}[c]
            return _Char(lambda x, wanted=value: x == wanted)
        if c == 'b' and inside_class:
            return '\x08'
        if c == 'b' or c == 'B':
            want = c == 'b'
            return _Anchor(lambda p, t, w=want: ((_word(t, p - 1) != _word(t, p)) == w))
        if ('A' <= c <= 'Z') or ('a' <= c <= 'z') or c in _DIGITS:
            _error("bad_escape")
        return c

    def _class(self):
        negated = False
        if self.i < len(self.s) and self.s[self.i] == '^':
            negated = True
            self.i += 1
        members = []
        if self.i < len(self.s) and self.s[self.i] == ']':
            members.append(('char', ']'))
            self.i += 1
        while True:
            if self.i >= len(self.s):
                _error("unterminated_class")
            if self.s[self.i] == ']':
                self.i += 1
                break
            if self.s[self.i] == '\\':
                first = self._escape(True)
                first_is_set = isinstance(first, _Char)
            else:
                first = self.s[self.i]
                self.i += 1
                first_is_set = False
            if self.i < len(self.s) and self.s[self.i] == '-' and self.i + 1 < len(self.s) and self.s[self.i + 1] != ']':
                self.i += 1
                if self.i >= len(self.s):
                    _error("unterminated_class")
                if self.s[self.i] == '\\':
                    second = self._escape(True)
                    second_is_set = isinstance(second, _Char)
                else:
                    second = self.s[self.i]
                    self.i += 1
                    second_is_set = False
                if first_is_set or second_is_set or not isinstance(first, str) or not isinstance(second, str) or ord(first) > ord(second):
                    _error("bad_range")
                members.append(('range', first, second))
            else:
                members.append(first if first_is_set else ('char', first))
        def matches(ch):
            for m in members:
                if isinstance(m, _Char):
                    if m.test(ch): return True
                elif m[0] == 'char' and ch == m[1]: return True
                elif m[0] == 'range' and m[1] <= ch <= m[2]: return True
            return False
        return _Char(lambda x: (not matches(x)) if negated else matches(x))

    def _read_quantifier(self, at):
        c = self.s[at]
        if c == '*': return 0, None, at + 1
        if c == '+': return 1, None, at + 1
        if c == '?': return 0, 1, at + 1
        if c != '{': return None
        j = at + 1
        a = j
        while j < len(self.s) and self.s[j] in _DIGITS: j += 1
        lo_text = self.s[a:j]
        if j < len(self.s) and self.s[j] == '}' and lo_text:
            return int(lo_text), int(lo_text), j + 1
        if j < len(self.s) and self.s[j] == ',':
            j += 1; b = j
            while j < len(self.s) and self.s[j] in _DIGITS: j += 1
            if j < len(self.s) and self.s[j] == '}':
                return (int(lo_text) if lo_text else 0), (int(self.s[b:j]) if b < j else None), j + 1
        return None

    def _is_quantifier_start(self, at):
        return at < len(self.s) and (self.s[at] in '*+?' or self._read_quantifier(at) is not None)


def _word(text, pos):
    return 0 <= pos < len(text) and text[pos] in _WORD


class _Node:
    anchor = False
    def match(self, p, caps, text):
        raise NotImplementedError


class _Seq(_Node):
    def __init__(self, items): self.items = items
    def match(self, p, caps, text):
        def go(k, q, c):
            if k == len(self.items):
                yield q, c; return
            for q2, c2 in self.items[k].match(q, c, text):
                yield from go(k + 1, q2, c2)
        yield from go(0, p, caps)


class _Alt(_Node):
    def __init__(self, branches): self.branches = branches
    def match(self, p, caps, text):
        for branch in self.branches:
            yield from branch.match(p, caps[:], text)


class _Char(_Node):
    def __init__(self, test): self.test = test
    def match(self, p, caps, text):
        if p < len(text) and self.test(text[p]): yield p + 1, caps[:]


class _Anchor(_Node):
    anchor = True
    def __init__(self, test): self.test = test
    def match(self, p, caps, text):
        if self.test(p, text): yield p, caps[:]


class _Group(_Node):
    def __init__(self, body, number): self.body, self.number = body, number
    def match(self, p, caps, text):
        for q, c in self.body.match(p, caps[:], text):
            if self.number is not None:
                c[self.number - 1] = (p, q)
            yield q, c


class _Repeat(_Node):
    def __init__(self, body, lo, hi, nongreedy): self.body, self.lo, self.hi, self.nongreedy = body, lo, hi, nongreedy
    def match(self, p, caps, text):
        def go(count, q, c, previous_consumed):
            can_more = self.hi is None or count < self.hi
            can_try = can_more and (count == 0 or previous_consumed)
            def more():
                if can_try:
                    for q2, c2 in self.body.match(q, c[:], text):
                        yield from go(count + 1, q2, c2, q2 != q)
            if self.nongreedy:
                if count >= self.lo: yield q, c[:]
                yield from more()
            else:
                yield from more()
                if count >= self.lo: yield q, c[:]
        yield from go(0, p, caps[:], None)


def search(pattern, text):
    root, count = _Parser(pattern).parse()
    for start in range(len(text) + 1):
        initial = [None] * count
        for end, caps in root.match(start, initial, text):
            return (start, end, caps)
    return None
