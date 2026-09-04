"""A small backtracking regular-expression engine, written from scratch.

Public API:
    search(pattern, text) -> None | (start, end, [span_or_None, ...])
Raises PatternError (a ValueError) for malformed patterns.
"""

import sys

sys.setrecursionlimit(30000)


class PatternError(ValueError):
    """Raised for a malformed pattern; .kind names the exact problem."""

    def __init__(self, kind, message=None):
        ValueError.__init__(self, message or kind)
        self.kind = kind


_DIGIT = "0123456789"
_WORD = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
_SPACE = set(" \t\n\r\f\v")
_CTRL = {"n": "\n", "t": "\t", "r": "\r", "f": "\f", "v": "\v"}
_ALNUM = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")


def _pred(name, ch):
    if name == "d":
        return ch in _DIGIT
    if name == "D":
        return ch not in _DIGIT
    if name == "w":
        return ch in _WORD
    if name == "W":
        return ch not in _WORD
    if name == "s":
        return ch in _SPACE
    return ch not in _SPACE


# ---------------------------------------------------------------- parser


class _Parser(object):
    def __init__(self, pat):
        self.p = pat
        self.n = len(pat)
        self.i = 0
        self.ngroups = 0

    def err(self, kind, msg=None):
        raise PatternError(kind, msg)

    def parse(self):
        node = self.parse_alt()
        if self.i != self.n:
            # only possible cause: a stray ')'
            self.err("unbalanced_paren")
        return node, self.ngroups

    def parse_alt(self):
        branches = [self.parse_cat()]
        while self.i < self.n and self.p[self.i] == "|":
            self.i += 1
            branches.append(self.parse_cat())
        if len(branches) == 1:
            return branches[0]
        return ("alt", branches)

    def parse_cat(self):
        items = []
        while self.i < self.n and self.p[self.i] not in "|)":
            items.append(self.parse_quantified(items))
        if len(items) == 1:
            return items[0]
        return ("cat", items)

    def parse_quantified(self, items):
        start = self.i
        atom = self.parse_atom()
        quant = self.read_quant()
        if quant is None:
            return atom
        if atom[0] in ("bol", "eol", "wb"):
            self.err("anchor_repeat")
        mn, mx, greedy = quant
        # a second quantifier is never allowed
        if self.read_quant(strict=False) is not None:
            self.err("multiple_repeat")
        del start
        return ("rep", atom, mn, mx, greedy)

    def read_quant(self, strict=True):
        if self.i >= self.n:
            return None
        c = self.p[self.i]
        if c in "*+?":
            self.i += 1
            mn, mx = {"*": (0, None), "+": (1, None), "?": (0, 1)}[c]
            greedy = True
            if self.i < self.n and self.p[self.i] == "?":
                self.i += 1
                greedy = False
            return (mn, mx, greedy)
        if c == "{":
            j = self.i + 1
            lo = ""
            while j < self.n and self.p[j] in _DIGIT:
                lo += self.p[j]
                j += 1
            if j < self.n and self.p[j] == "}":
                if lo == "":
                    return None
                self.i = j + 1
                v = int(lo)
                mn, mx = v, v
            elif j < self.n and self.p[j] == ",":
                j += 1
                hi = ""
                while j < self.n and self.p[j] in _DIGIT:
                    hi += self.p[j]
                    j += 1
                if j >= self.n or self.p[j] != "}":
                    return None
                self.i = j + 1
                mn = int(lo) if lo else 0
                mx = int(hi) if hi else None
            else:
                return None
            if mx is not None and mn > mx and strict:
                self.err("bad_repeat")
            greedy = True
            if self.i < self.n and self.p[self.i] == "?":
                self.i += 1
                greedy = False
            return (mn, mx, greedy)
        return None

    def parse_atom(self):
        c = self.p[self.i]
        if c in "*+?":
            self.err("nothing_to_repeat")
        if c == "{" and self.peek_quant_here():
            self.err("nothing_to_repeat")
        if c == "(":
            self.i += 1
            idx = None
            if self.i < self.n and self.p[self.i] == "?":
                if self.i + 1 < self.n and self.p[self.i + 1] == ":":
                    self.i += 2
                else:
                    self.err("bad_group")
            else:
                self.ngroups += 1
                idx = self.ngroups
            body = self.parse_alt()
            if self.i >= self.n or self.p[self.i] != ")":
                self.err("unbalanced_paren")
            self.i += 1
            return ("grp", idx, body)
        if c == "[":
            return self.parse_class()
        if c == ".":
            self.i += 1
            return ("any",)
        if c == "^":
            self.i += 1
            return ("bol",)
        if c == "$":
            self.i += 1
            return ("eol",)
        if c == "\\":
            self.i += 1
            if self.i >= self.n:
                self.err("trailing_backslash")
            e = self.p[self.i]
            self.i += 1
            if e in "dDwWsS":
                return ("cls", False, [("p", e)])
            if e in _CTRL:
                return ("lit", _CTRL[e])
            if e == "b":
                return ("wb", True)
            if e == "B":
                return ("wb", False)
            if e in _ALNUM:
                self.err("bad_escape", "bad escape")
            return ("lit", e)
        self.i += 1
        return ("lit", c)

    def peek_quant_here(self):
        save = self.i
        try:
            q = self.read_quant(strict=False)
        finally:
            got = self.i
            self.i = save
        del got
        return q is not None

    def class_member(self):
        c = self.p[self.i]
        if c == "\\":
            self.i += 1
            if self.i >= self.n:
                self.err("trailing_backslash")
            e = self.p[self.i]
            self.i += 1
            if e in "dDwWsS":
                return ("p", e)
            if e in _CTRL:
                return ("c", _CTRL[e])
            if e == "b":
                return ("c", "\x08")
            if e in _ALNUM:
                self.err("bad_escape", "bad escape")
            return ("c", e)
        self.i += 1
        return ("c", c)

    def parse_class(self):
        self.i += 1  # skip '['
        neg = False
        if self.i < self.n and self.p[self.i] == "^":
            neg = True
            self.i += 1
        items = []
        first = True
        while True:
            if self.i >= self.n:
                self.err("unterminated_class")
            if self.p[self.i] == "]" and not first:
                self.i += 1
                break
            first = False
            m = self.class_member()
            if (self.i + 1 < self.n and self.p[self.i] == "-"
                    and self.p[self.i + 1] != "]"):
                self.i += 1
                if self.i >= self.n:
                    self.err("unterminated_class")
                m2 = self.class_member()
                if m[0] != "c" or m2[0] != "c":
                    self.err("bad_range")
                if ord(m[1]) > ord(m2[1]):
                    self.err("bad_range")
                items.append(("r", m[1], m2[1]))
            else:
                items.append(m)
        return ("cls", neg, items)


def _cls_match(items, neg, ch):
    hit = False
    for it in items:
        if it[0] == "c":
            if ch == it[1]:
                hit = True
                break
        elif it[0] == "r":
            if it[1] <= ch <= it[2]:
                hit = True
                break
        else:
            if _pred(it[1], ch):
                hit = True
                break
    return hit != neg


# ---------------------------------------------------------------- matcher


class _St(object):
    __slots__ = ("text", "ln", "marks", "result")


def _isword(st, i):
    return 0 <= i < st.ln and st.text[i] in _WORD


def _m(node, pos, k, st):
    t = node[0]
    if t == "lit":
        if pos < st.ln and st.text[pos] == node[1]:
            return k(pos + 1)
        return None
    if t == "any":
        if pos < st.ln and st.text[pos] != "\n":
            return k(pos + 1)
        return None
    if t == "cls":
        if pos < st.ln and _cls_match(node[2], node[1], st.text[pos]):
            return k(pos + 1)
        return None
    if t == "bol":
        return k(pos) if pos == 0 else None
    if t == "eol":
        if pos == st.ln or (pos == st.ln - 1 and st.text[pos] == "\n"):
            return k(pos)
        return None
    if t == "wb":
        b = _isword(st, pos - 1) != _isword(st, pos)
        return k(pos) if b == node[1] else None
    if t == "cat":
        items = node[1]
        ln = len(items)

        def run(idx, p):
            if idx == ln:
                return k(p)
            return _m(items[idx], p, lambda q, idx=idx: run(idx + 1, q), st)

        return run(0, pos)
    if t == "alt":
        marks = st.marks
        save = marks[:]
        for br in node[1]:
            r = _m(br, pos, k, st)
            if r is not None:
                return r
            marks[:] = save
        return None
    if t == "grp":
        idx = node[1]
        if idx is None:
            return _m(node[2], pos, k, st)
        marks = st.marks
        a = 2 * (idx - 1)
        b = a + 1
        o0, o1 = marks[a], marks[b]

        def kk(p):
            prev = marks[b]
            marks[b] = p
            r = k(p)
            if r is None:
                marks[b] = prev
            return r

        marks[a] = pos
        r = _m(node[2], pos, kk, st)
        if r is None:
            marks[a] = o0
            marks[b] = o1
        return r
    # repetition
    _, child, mn, mx, greedy = node
    marks = st.marks
    if greedy:
        def rep(p, count, last):
            if count < mn:
                save = marks[:]
                r = _m(child, p, lambda q, p=p, c=count: rep(q, c + 1, p), st)
                if r is None:
                    marks[:] = save
                return r
            if (mx is None or count < mx) and p != last:
                save = marks[:]
                r = _m(child, p, lambda q, p=p, c=count: rep(q, c + 1, p), st)
                if r is not None:
                    return r
                marks[:] = save
            return k(p)
    else:
        def rep(p, count, last):
            if count < mn:
                save = marks[:]
                r = _m(child, p, lambda q, p=p, c=count: rep(q, c + 1, p), st)
                if r is None:
                    marks[:] = save
                return r
            save = marks[:]
            r = k(p)
            if r is not None:
                return r
            marks[:] = save
            if (mx is not None and count >= mx) or p == last:
                return None
            r = _m(child, p, lambda q, p=p, c=count: rep(q, c + 1, p), st)
            if r is None:
                marks[:] = save
            return r

    return rep(pos, 0, -1)


_cache = {}


def _compile(pattern):
    got = _cache.get(pattern)
    if got is None:
        got = _Parser(pattern).parse()
        if len(_cache) > 500:
            _cache.clear()
        _cache[pattern] = got
    return got


def search(pattern, text):
    node, ng = _compile(pattern)
    st = _St()
    st.text = text
    st.ln = len(text)
    out = []

    def top(p):
        out.append(p)
        return p

    for start in range(len(text) + 1):
        st.marks = [None] * (2 * ng)
        del out[:]
        r = _m(node, start, top, st)
        if r is not None:
            groups = []
            for g in range(ng):
                a, b = st.marks[2 * g], st.marks[2 * g + 1]
                groups.append(None if a is None or b is None else (a, b))
            return (start, out[-1], groups)
    return None
