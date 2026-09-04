"""A backtracking regular-expression engine, written from scratch.

Public API:
    PatternError -- exception class (subclasses ValueError), with a `.kind`
        attribute set to one of the lowercase strings documented in the task.
    search(pattern, text) -- returns None, or (start, end, groups).
"""

import string
import sys

sys.setrecursionlimit(1000000)

DIGITS = set('0123456789')
WORD_CHARS = set(string.ascii_letters + string.digits + '_')
SPACE_CHARS = set(' \t\n\r\f\v')
ASCII_LETTERS = set(string.ascii_letters)
ASCII_DIGITS = set(string.digits)

ESCAPE_CHAR_MAP = {'n': '\n', 't': '\t', 'r': '\r', 'f': '\f', 'v': '\v'}


class PatternError(ValueError):
    def __init__(self, kind, message=None):
        super().__init__(message or kind)
        self.kind = kind


# ---------------------------------------------------------------------------
# AST node classes. Each has a .match(text, pos, groups, cont) method that
# performs an ordered, depth-first, backtracking search: it tries its own
# possibilities in order, and for each one calls cont(new_pos); if cont
# returns True the whole thing returns True, otherwise it tries the next
# possibility. Returns False if every possibility (and every continuation)
# failed.
# ---------------------------------------------------------------------------

class Literal:
    __slots__ = ('ch',)

    def __init__(self, ch):
        self.ch = ch

    def match(self, text, pos, groups, cont):
        if pos < len(text) and text[pos] == self.ch:
            return cont(pos + 1)
        return False


class AnyChar:
    __slots__ = ()

    def match(self, text, pos, groups, cont):
        if pos < len(text) and text[pos] != '\n':
            return cont(pos + 1)
        return False


class CharClass:
    __slots__ = ('test',)

    def __init__(self, test):
        self.test = test

    def match(self, text, pos, groups, cont):
        if pos < len(text) and self.test(text[pos]):
            return cont(pos + 1)
        return False


class StartAnchor:
    __slots__ = ()

    def match(self, text, pos, groups, cont):
        if pos == 0:
            return cont(pos)
        return False


class EndAnchor:
    __slots__ = ()

    def match(self, text, pos, groups, cont):
        n = len(text)
        if pos == n or (pos == n - 1 and text[pos] == '\n'):
            return cont(pos)
        return False


class WordBoundary:
    __slots__ = ('positive',)

    def __init__(self, positive):
        self.positive = positive

    def match(self, text, pos, groups, cont):
        n = len(text)

        def is_word(idx):
            return 0 <= idx < n and text[idx] in WORD_CHARS

        left = is_word(pos - 1)
        right = is_word(pos)
        boundary = left != right
        if boundary == self.positive:
            return cont(pos)
        return False


class Concat:
    __slots__ = ('items',)

    def __init__(self, items):
        self.items = items

    def match(self, text, pos, groups, cont):
        items = self.items
        n = len(items)

        def step(idx, p):
            if idx == n:
                return cont(p)
            return items[idx].match(text, p, groups,
                                     lambda p2, idx=idx: step(idx + 1, p2))

        return step(0, pos)


class Alt:
    __slots__ = ('branches',)

    def __init__(self, branches):
        self.branches = branches

    def match(self, text, pos, groups, cont):
        for b in self.branches:
            if b.match(text, pos, groups, cont):
                return True
        return False


class Group:
    __slots__ = ('num', 'body')

    def __init__(self, num, body):
        self.num = num
        self.body = body

    def match(self, text, pos, groups, cont):
        num = self.num
        old = groups[num]

        def inner_cont(end_pos):
            prev = groups[num]
            groups[num] = (pos, end_pos)
            if cont(end_pos):
                return True
            groups[num] = prev
            return False

        result = self.body.match(text, pos, groups, inner_cont)
        if not result:
            groups[num] = old
        return result


class Repeat:
    __slots__ = ('node', 'lo', 'hi', 'greedy')

    def __init__(self, node, lo, hi, greedy):
        self.node = node
        self.lo = lo
        self.hi = hi
        self.greedy = greedy

    def match(self, text, pos, groups, cont):
        node = self.node
        lo = self.lo
        hi = self.hi
        greedy = self.greedy

        def rep(count, p, last_start):
            if count < lo:
                return node.match(text, p, groups,
                                   lambda p2: rep(count + 1, p2, p))
            guard_ok = True
            if count > lo:
                guard_ok = (p != last_start)
            can_more = (hi is None or count < hi) and guard_ok
            if greedy:
                if can_more:
                    if node.match(text, p, groups,
                                   lambda p2: rep(count + 1, p2, p)):
                        return True
                return cont(p)
            else:
                if cont(p):
                    return True
                if can_more:
                    return node.match(text, p, groups,
                                       lambda p2: rep(count + 1, p2, p))
                return False

        return rep(0, pos, None)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

SHORTHAND_TESTS = {
    'd': lambda c: c in DIGITS,
    'D': lambda c: c not in DIGITS,
    'w': lambda c: c in WORD_CHARS,
    'W': lambda c: c not in WORD_CHARS,
    's': lambda c: c in SPACE_CHARS,
    'S': lambda c: c not in SPACE_CHARS,
}


def _is_ascii_alnum(c):
    return c in ASCII_LETTERS or c in ASCII_DIGITS


class _Parser:
    def __init__(self, pattern):
        self.s = pattern
        self.i = 0
        self.ngroups = 0

    # -- quantifier lookahead -------------------------------------------------
    def try_quant(self, pos):
        s = self.s
        if pos >= len(s):
            return None
        c = s[pos]
        if c == '*':
            return (0, None, pos + 1)
        if c == '+':
            return (1, None, pos + 1)
        if c == '?':
            return (0, 1, pos + 1)
        if c == '{':
            j = pos + 1
            lo_start = j
            while j < len(s) and '0' <= s[j] <= '9':
                j += 1
            lo_str = s[lo_start:j]
            if j < len(s) and s[j] == '}' and lo_str != '':
                lo = int(lo_str)
                return (lo, lo, j + 1)
            if j < len(s) and s[j] == ',':
                k = j + 1
                hi_start = k
                while k < len(s) and '0' <= s[k] <= '9':
                    k += 1
                hi_str = s[hi_start:k]
                if k < len(s) and s[k] == '}':
                    if lo_str == '' and hi_str == '':
                        return None
                    lo = int(lo_str) if lo_str != '' else 0
                    hi = int(hi_str) if hi_str != '' else None
                    return (lo, hi, k + 1)
            return None
        return None

    # -- top level --------------------------------------------------------
    def parse_alt(self):
        branches = [self.parse_concat()]
        s = self.s
        while self.i < len(s) and s[self.i] == '|':
            self.i += 1
            branches.append(self.parse_concat())
        if len(branches) == 1:
            return branches[0]
        return Alt(branches)

    def parse_concat(self):
        s = self.s
        items = []
        first = True
        while self.i < len(s) and s[self.i] not in '|)':
            if first:
                q = self.try_quant(self.i)
                if q is not None:
                    raise PatternError('nothing_to_repeat')
            atom = self.parse_atom()
            first = False
            q = self.try_quant(self.i)
            if q is not None:
                lo, hi, end = q
                greedy = True
                if end < len(s) and s[end] == '?':
                    greedy = False
                    end += 1
                if hi is not None and lo > hi:
                    raise PatternError('bad_repeat')
                if isinstance(atom, (StartAnchor, EndAnchor, WordBoundary)):
                    raise PatternError('anchor_repeat')
                q2 = self.try_quant(end)
                if q2 is not None:
                    raise PatternError('multiple_repeat')
                atom = Repeat(atom, lo, hi, greedy)
                self.i = end
            items.append(atom)
        if len(items) == 1:
            return items[0]
        return Concat(items)

    def parse_atom(self):
        s = self.s
        c = s[self.i]
        if c == '(':
            self.i += 1
            if self.i < len(s) and s[self.i] == '?':
                if self.i + 1 < len(s) and s[self.i + 1] == ':':
                    self.i += 2
                    body = self.parse_alt()
                    if self.i >= len(s) or s[self.i] != ')':
                        raise PatternError('unbalanced_paren')
                    self.i += 1
                    return body
                else:
                    raise PatternError('bad_group')
            else:
                self.ngroups += 1
                gnum = self.ngroups
                body = self.parse_alt()
                if self.i >= len(s) or s[self.i] != ')':
                    raise PatternError('unbalanced_paren')
                self.i += 1
                return Group(gnum, body)
        elif c == '[':
            return self.parse_class()
        elif c == '.':
            self.i += 1
            return AnyChar()
        elif c == '^':
            self.i += 1
            return StartAnchor()
        elif c == '$':
            self.i += 1
            return EndAnchor()
        elif c == '\\':
            return self.parse_escape_outside()
        else:
            self.i += 1
            return Literal(c)

    def parse_escape_outside(self):
        s = self.s
        self.i += 1  # skip backslash
        if self.i >= len(s):
            raise PatternError('trailing_backslash')
        c = s[self.i]
        self.i += 1
        if c in SHORTHAND_TESTS:
            return CharClass(SHORTHAND_TESTS[c])
        if c in ESCAPE_CHAR_MAP:
            return Literal(ESCAPE_CHAR_MAP[c])
        if c == 'b':
            return WordBoundary(True)
        if c == 'B':
            return WordBoundary(False)
        if _is_ascii_alnum(c):
            raise PatternError('bad_escape')
        return Literal(c)

    # -- character classes --------------------------------------------------
    def read_class_member(self):
        """Read one class member at self.i. Returns (char, special) where
        exactly one of them is not None: `char` for a literal character
        member, `special` (one of 'd','D','w','W','s','S') for a shorthand
        class member."""
        s = self.s
        c = s[self.i]
        if c == '\\':
            self.i += 1
            if self.i >= len(s):
                raise PatternError('trailing_backslash')
            e = s[self.i]
            self.i += 1
            if e in SHORTHAND_TESTS:
                return (None, e)
            if e in ESCAPE_CHAR_MAP:
                return (ESCAPE_CHAR_MAP[e], None)
            if e == 'b':
                return (chr(8), None)
            if e == 'B':
                raise PatternError('bad_escape')
            if _is_ascii_alnum(e):
                raise PatternError('bad_escape')
            return (e, None)
        else:
            self.i += 1
            return (c, None)

    def parse_class(self):
        s = self.s
        self.i += 1  # skip '['
        negate = False
        if self.i < len(s) and s[self.i] == '^':
            negate = True
            self.i += 1

        literal_chars = set()
        ranges = []
        specials = []

        if self.i < len(s) and s[self.i] == ']':
            literal_chars.add(']')
            self.i += 1

        while True:
            if self.i >= len(s):
                raise PatternError('unterminated_class')
            if s[self.i] == ']':
                self.i += 1
                break
            Mchar, Mspecial = self.read_class_member()
            is_range = (self.i < len(s) and s[self.i] == '-' and
                        self.i + 1 < len(s) and s[self.i + 1] != ']')
            if is_range:
                self.i += 1  # consume '-'
                Nchar, Nspecial = self.read_class_member()
                if Mspecial is not None or Nspecial is not None:
                    raise PatternError('bad_range')
                if ord(Mchar) > ord(Nchar):
                    raise PatternError('bad_range')
                ranges.append((ord(Mchar), ord(Nchar)))
            else:
                if Mspecial is not None:
                    specials.append(SHORTHAND_TESTS[Mspecial])
                else:
                    literal_chars.add(Mchar)

        def test(ch, literal_chars=literal_chars, ranges=ranges,
                 specials=specials, negate=negate):
            m = (ch in literal_chars or
                 any(lo <= ord(ch) <= hi for lo, hi in ranges) or
                 any(f(ch) for f in specials))
            return (not m) if negate else m

        return CharClass(test)


def _compile(pattern):
    parser = _Parser(pattern)
    node = parser.parse_alt()
    if parser.i != len(pattern):
        # only an unmatched ')' can be left over
        raise PatternError('unbalanced_paren')
    return node, parser.ngroups


def search(pattern, text):
    root, ngroups = _compile(pattern)
    n = len(text)
    for start in range(n + 1):
        groups = [None] * (ngroups + 1)
        box = {}

        def final_cont(end_pos, box=box):
            box['end'] = end_pos
            return True

        if root.match(text, start, groups, final_cont):
            return (start, box['end'],
                    [groups[i] for i in range(1, ngroups + 1)])
    return None
