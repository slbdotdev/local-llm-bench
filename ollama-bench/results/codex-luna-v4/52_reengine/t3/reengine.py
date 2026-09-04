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

    def err(self, kind):
        raise PatternError(kind)

    def brace(self, i):
        """Return (lo, hi, end) for a real brace quantifier, or None."""
        if i >= len(self.s) or self.s[i] != '{':
            return None
        j = i + 1
        a = j
        while j < len(self.s) and self.s[j] in _DIGITS:
            j += 1
        lo_text = self.s[a:j]
        if j < len(self.s) and self.s[j] == '}' and lo_text:
            return int(lo_text), int(lo_text), j + 1
        if j < len(self.s) and self.s[j] == ',':
            j += 1
            b = j
            while j < len(self.s) and self.s[j] in _DIGITS:
                j += 1
            if j < len(self.s) and self.s[j] == '}':
                return (int(lo_text) if lo_text else 0,
                        int(self.s[b:j]) if b != j else None, j + 1)
        return None

    def starts_quant(self, i):
        if i < len(self.s) and self.s[i] in '*+?':
            return True
        return self.brace(i) is not None

    def parse(self):
        tree = self.branches(False)
        if self.i != len(self.s):
            self.err('unbalanced_paren')
        return tree, self.groups

    def branches(self, in_group):
        out = []
        while True:
            out.append(self.sequence(in_group))
            if self.i < len(self.s) and self.s[self.i] == '|':
                self.i += 1
                continue
            break
        if in_group:
            if self.i >= len(self.s) or self.s[self.i] != ')':
                self.err('unbalanced_paren')
            self.i += 1
        return ('alt', out)

    def sequence(self, in_group):
        items = []
        while self.i < len(self.s) and self.s[self.i] not in '|)':
            if self.s[self.i] in '*+?':
                self.err('nothing_to_repeat')
            if self.s[self.i] == '{' and self.brace(self.i) is not None:
                self.err('nothing_to_repeat')
            atom = self.atom(in_group)
            q = None
            if self.i < len(self.s):
                c = self.s[self.i]
                if c == '*': q = (0, None)
                elif c == '+': q = (1, None)
                elif c == '?': q = (0, 1)
                else: q = self.brace(self.i)
            if q is not None:
                if isinstance(q, tuple) and len(q) == 3:
                    lo, hi, end = q
                else:
                    lo, hi = q; end = self.i + 1
                self.i = end
                if self.i < len(self.s) and self.s[self.i] == '?':
                    greedy = False; self.i += 1
                else:
                    greedy = True
                if hi is not None and lo > hi: self.err('bad_repeat')
                if atom[0] == 'anchor': self.err('anchor_repeat')
                if self.starts_quant(self.i): self.err('multiple_repeat')
                atom = ('rep', atom, lo, hi, greedy)
            items.append(atom)
        return ('seq', items)

    def atom(self, in_group):
        c = self.s[self.i]
        if c == '(':
            self.i += 1
            capture = True
            if self.i < len(self.s) and self.s[self.i] == '?':
                self.i += 1
                if self.i >= len(self.s) or self.s[self.i] != ':': self.err('bad_group')
                self.i += 1; capture = False
            num = None
            if capture:
                self.groups += 1; num = self.groups
            body = self.branches(True)
            return ('group', num, body)
        if c == '[': return self.charclass()
        if c == '.': self.i += 1; return ('char', lambda x: x != '\n')
        if c in '^$': self.i += 1; return ('anchor', c)
        if c == '\\':
            kind, value = self.escape(False)
            if kind == 'class':
                base, inverted = value
                return ('char', lambda x, base=base, inverted=inverted: (x in base) != inverted)
            return ('anchor', value) if kind == 'anchor' else ('char', lambda x, value=value: x == value)
        self.i += 1
        return ('char', lambda x, c=c: x == c)

    def escape(self, inside):
        self.i += 1
        if self.i >= len(self.s): self.err('trailing_backslash')
        c = self.s[self.i]; self.i += 1
        if c in 'dDwWsS':
            base = _DIGITS if c.lower() == 'd' else _WORD if c.lower() == 'w' else _SPACE
            return 'class', (base, c.isupper())
        if c in 'ntrfv': return 'literal', {'n':'\n','t':'\t','r':'\r','f':'\f','v':'\v'}[c]
        if c == 'b': return 'literal' if inside else 'anchor', '\x08' if inside else 'b'
        if c == 'B':
            if inside: self.err('bad_escape')
            return 'anchor', 'B'
        if c.isascii() and c.isalnum(): self.err('bad_escape')
        return 'literal', c

    def charclass(self):
        self.i += 1; neg = False
        if self.i < len(self.s) and self.s[self.i] == '^': neg = True; self.i += 1
        members = []
        if self.i < len(self.s) and self.s[self.i] == ']':
            members.append(('lit', ']')); self.i += 1
        while True:
            if self.i >= len(self.s): self.err('unterminated_class')
            if self.s[self.i] == ']': self.i += 1; break
            if self.s[self.i] == '\\':
                typ, val = self.escape(True)
                m = ('set', val) if typ == 'class' else ('lit', val)
            else:
                m = ('lit', self.s[self.i]); self.i += 1
            if self.i < len(self.s) and self.s[self.i] == '-' and self.i + 1 < len(self.s) and self.s[self.i+1] != ']':
                self.i += 1
                if self.i >= len(self.s): self.err('unterminated_class')
                if self.s[self.i] == '\\': typ, val = self.escape(True); n = ('set', val) if typ == 'class' else ('lit', val)
                else: n = ('lit', self.s[self.i]); self.i += 1
                if m[0] == 'set' or n[0] == 'set' or ord(m[1]) > ord(n[1]): self.err('bad_range')
                members.append(('range', m[1], n[1]))
            else: members.append(m)
        def pred(ch, members=members, neg=neg):
            ok = any((ch == x[1]) if x[0] == 'lit' else (x[1] <= ch <= x[2]) if x[0] == 'range' else ((ch in x[1][0]) != x[1][1]) for x in members)
            return not ok if neg else ok
        return ('char', pred)


def _match_tree(node, text, pos, state):
    kind = node[0]
    if kind == 'char':
        if pos < len(text) and node[1](text[pos]): yield pos + 1, state
    elif kind == 'anchor':
        c = node[1]
        if c == '^' and pos == 0: yield pos, state
        elif c == '$' and (pos == len(text) or (pos == len(text)-1 and text.endswith('\n'))): yield pos, state
        elif c in ('b','B'):
            a = pos > 0 and text[pos-1] in _WORD; b = pos < len(text) and text[pos] in _WORD
            if (a != b) == (c == 'b'): yield pos, state
    elif kind == 'alt':
        for branch in node[1]: yield from _match_tree(branch, text, pos, state[:])
    elif kind == 'seq':
        def go(k, p, st):
            if k == len(node[1]): yield p, st; return
            for np, ns in _match_tree(node[1][k], text, p, st): yield from go(k+1, np, ns)
        yield from go(0, pos, state)
    elif kind == 'group':
        start = pos
        for np, ns in _match_tree(node[2], text, pos, state[:]):
            if node[1] is not None: ns[node[1]-1] = (start, np)
            yield np, ns
    elif kind == 'rep':
        body, lo, hi, greedy = node[1:]
        def rec(count, p, st, prev_start=None):
            can = hi is None or count < hi
            allowed = can and (count < lo or prev_start is None or p != prev_start)
            if greedy and allowed:
                for np, ns in _match_tree(body, text, p, st[:]):
                    yield from rec(count+1, np, ns, p)
            if count >= lo: yield p, st
            if (not greedy) and allowed:
                for np, ns in _match_tree(body, text, p, st[:]):
                    yield from rec(count+1, np, ns, p)
        yield from rec(0, pos, state)


def search(pattern, text):
    tree, count = _Parser(pattern).parse()
    for start in range(len(text) + 1):
        for end, state in _match_tree(tree, text, start, [None] * count):
            return (start, end, state)
    return None
