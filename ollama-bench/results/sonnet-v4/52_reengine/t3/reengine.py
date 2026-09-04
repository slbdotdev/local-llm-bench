"""A backtracking regular-expression engine, written from scratch.

Public API:
    PatternError -- exception for malformed patterns; has a `.kind` attribute.
    search(pattern, text) -- see docstring below.
"""

import sys

sys.setrecursionlimit(20000)


class PatternError(ValueError):
    def __init__(self, kind, message=None):
        self.kind = kind
        super().__init__(message or kind)


# ---------------------------------------------------------------------------
# Character classification helpers (ASCII only)
# ---------------------------------------------------------------------------

def _is_digit(c):
    return '0' <= c <= '9'


def _is_word(c):
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or ('0' <= c <= '9') or c == '_'


def _is_space(c):
    return c in ' \t\n\r\f\v'


def _is_ascii_alnum(c):
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or ('0' <= c <= '9')


def _shorthand_match(letter, ch):
    if letter == 'd':
        return _is_digit(ch)
    if letter == 'D':
        return not _is_digit(ch)
    if letter == 'w':
        return _is_word(ch)
    if letter == 'W':
        return not _is_word(ch)
    if letter == 's':
        return _is_space(ch)
    if letter == 'S':
        return not _is_space(ch)
    raise AssertionError("bad shorthand")


def _is_boundary(text, pos):
    before = pos > 0 and _is_word(text[pos - 1])
    after = pos < len(text) and _is_word(text[pos])
    return before != after


# ---------------------------------------------------------------------------
# Parser: pattern string -> AST
# ---------------------------------------------------------------------------
#
# AST node shapes:
#   ('lit', ch)
#   ('any',)
#   ('shorthand', letter)          letter in 'dDwWsS'
#   ('class', negate, literal_set, ranges, shorthands)
#   ('start',)
#   ('end',)
#   ('wordb',)
#   ('nwordb',)
#   ('group', num_or_None, alt_node)
#   ('rep', atom_node, lo, hi_or_None, greedy)
#   ('alt', [branch, branch, ...])   branch = list of nodes (a concatenation)

class Parser:
    def __init__(self, pattern):
        self.p = pattern
        self.i = 0
        self.n = len(pattern)
        self.group_count = 0

    # -- top level --------------------------------------------------------

    def parse_alt(self):
        branches = [self.parse_concat()]
        while self.i < self.n and self.p[self.i] == '|':
            self.i += 1
            branches.append(self.parse_concat())
        return ('alt', branches)

    def parse_concat(self):
        nodes = []
        while self.i < self.n and self.p[self.i] not in '|)':
            if not nodes and self.peek_quantifier(self.i) is not None:
                raise PatternError('nothing_to_repeat')
            atom = self.parse_one_atom()
            q = self.peek_quantifier(self.i)
            if q is not None:
                lo, hi, next_i = q
                greedy = True
                final_end = next_i
                if next_i < self.n and self.p[next_i] == '?':
                    greedy = False
                    final_end = next_i + 1
                if hi is not None and lo > hi:
                    raise PatternError('bad_repeat')
                if atom[0] in ('start', 'end', 'wordb', 'nwordb'):
                    raise PatternError('anchor_repeat')
                if self.peek_quantifier(final_end) is not None:
                    raise PatternError('multiple_repeat')
                self.i = final_end
                atom = ('rep', atom, lo, hi, greedy)
            nodes.append(atom)
        return nodes

    def peek_quantifier(self, i):
        """Return (lo, hi_or_None, next_i) if a well-formed quantifier core
        starts at i, else None. Does not consume state."""
        if i >= self.n:
            return None
        c = self.p[i]
        if c == '*':
            return (0, None, i + 1)
        if c == '+':
            return (1, None, i + 1)
        if c == '?':
            return (0, 1, i + 1)
        if c == '{':
            j = i + 1
            lo_start = j
            while j < self.n and self.p[j].isdigit():
                j += 1
            lo_str = self.p[lo_start:j]
            if j < self.n and self.p[j] == '}' and lo_str != '':
                return (int(lo_str), int(lo_str), j + 1)
            elif j < self.n and self.p[j] == ',':
                j2 = j + 1
                hi_start = j2
                while j2 < self.n and self.p[j2].isdigit():
                    j2 += 1
                hi_str = self.p[hi_start:j2]
                if j2 < self.n and self.p[j2] == '}':
                    lo = int(lo_str) if lo_str != '' else 0
                    hi = int(hi_str) if hi_str != '' else None
                    return (lo, hi, j2 + 1)
                return None
            else:
                return None
        return None

    # -- atoms --------------------------------------------------------

    def parse_one_atom(self):
        c = self.p[self.i]
        if c == '(':
            return self.parse_group()
        if c == '[':
            return self.parse_class()
        if c == '.':
            self.i += 1
            return ('any',)
        if c == '^':
            self.i += 1
            return ('start',)
        if c == '$':
            self.i += 1
            return ('end',)
        if c == '\\':
            return self.parse_escape_outside()
        self.i += 1
        return ('lit', c)

    def parse_group(self):
        self.i += 1  # consume '('
        capturing = True
        if self.i < self.n and self.p[self.i] == '?':
            if self.i + 1 < self.n and self.p[self.i + 1] == ':':
                capturing = False
                self.i += 2
            else:
                raise PatternError('bad_group')
        group_num = None
        if capturing:
            self.group_count += 1
            group_num = self.group_count
        body = self.parse_alt()
        if self.i >= self.n or self.p[self.i] != ')':
            raise PatternError('unbalanced_paren')
        self.i += 1  # consume ')'
        return ('group', group_num, body)

    def parse_escape_outside(self):
        i = self.i
        if i + 1 >= self.n:
            raise PatternError('trailing_backslash')
        X = self.p[i + 1]
        self.i = i + 2
        if X in 'dDwWsS':
            return ('shorthand', X)
        if X == 'n':
            return ('lit', '\n')
        if X == 't':
            return ('lit', '\t')
        if X == 'r':
            return ('lit', '\r')
        if X == 'f':
            return ('lit', '\f')
        if X == 'v':
            return ('lit', '\v')
        if X == 'b':
            return ('wordb',)
        if X == 'B':
            return ('nwordb',)
        if _is_ascii_alnum(X):
            raise PatternError('bad_escape')
        return ('lit', X)

    # -- character classes --------------------------------------------

    def parse_class(self):
        self.i += 1  # consume '['
        negate = False
        if self.i < self.n and self.p[self.i] == '^':
            negate = True
            self.i += 1

        members_literal = set()
        ranges = []
        shorthands = []
        first_pos = True

        while True:
            if self.i >= self.n:
                raise PatternError('unterminated_class')
            if self.p[self.i] == ']' and not first_pos:
                self.i += 1
                break
            m = self._read_class_member()
            first_pos = False
            if (self.i < self.n and self.p[self.i] == '-'
                    and self.i + 1 < self.n and self.p[self.i + 1] != ']'):
                self.i += 1  # consume '-'
                n_member = self._read_class_member()
                if m[0] != 'lit' or n_member[0] != 'lit':
                    raise PatternError('bad_range')
                lo_ch, hi_ch = m[1], n_member[1]
                if ord(lo_ch) > ord(hi_ch):
                    raise PatternError('bad_range')
                ranges.append((ord(lo_ch), ord(hi_ch)))
            else:
                if m[0] == 'lit':
                    members_literal.add(m[1])
                else:
                    shorthands.append(m[1])

        return ('class', negate, members_literal, ranges, shorthands)

    def _read_class_member(self):
        if self.i >= self.n:
            raise PatternError('unterminated_class')
        c = self.p[self.i]
        if c == '\\':
            if self.i + 1 >= self.n:
                raise PatternError('trailing_backslash')
            X = self.p[self.i + 1]
            self.i += 2
            if X in 'dDwWsS':
                return ('short', X)
            if X == 'n':
                return ('lit', '\n')
            if X == 't':
                return ('lit', '\t')
            if X == 'r':
                return ('lit', '\r')
            if X == 'f':
                return ('lit', '\f')
            if X == 'v':
                return ('lit', '\v')
            if X == 'b':
                return ('lit', '\x08')
            if X == 'B':
                raise PatternError('bad_escape')
            if _is_ascii_alnum(X):
                raise PatternError('bad_escape')
            return ('lit', X)
        else:
            self.i += 1
            return ('lit', c)


# ---------------------------------------------------------------------------
# Compiler: AST -> matcher closures
#
# A matcher is a callable m(text, pos, groups, cont) -> bool where `cont` is
# itself a callable p -> bool representing "the rest of the match". Invariant
# maintained by every matcher: if it returns False, `groups` is restored to
# exactly the state it had when the matcher was invoked.
# ---------------------------------------------------------------------------

def _compile_node(node):
    kind = node[0]

    if kind == 'lit':
        ch = node[1]

        def m(text, pos, groups, cont, ch=ch):
            if pos < len(text) and text[pos] == ch:
                return cont(pos + 1)
            return False
        return m

    if kind == 'any':
        def m(text, pos, groups, cont):
            if pos < len(text) and text[pos] != '\n':
                return cont(pos + 1)
            return False
        return m

    if kind == 'shorthand':
        letter = node[1]

        def m(text, pos, groups, cont, letter=letter):
            if pos < len(text) and _shorthand_match(letter, text[pos]):
                return cont(pos + 1)
            return False
        return m

    if kind == 'class':
        _, negate, members, ranges, shorts = node
        return _make_class_matcher(negate, members, ranges, shorts)

    if kind == 'start':
        def m(text, pos, groups, cont):
            if pos == 0:
                return cont(pos)
            return False
        return m

    if kind == 'end':
        def m(text, pos, groups, cont):
            if pos == len(text) or (len(text) > 0 and pos == len(text) - 1 and text[pos] == '\n'):
                return cont(pos)
            return False
        return m

    if kind == 'wordb':
        def m(text, pos, groups, cont):
            if _is_boundary(text, pos):
                return cont(pos)
            return False
        return m

    if kind == 'nwordb':
        def m(text, pos, groups, cont):
            if not _is_boundary(text, pos):
                return cont(pos)
            return False
        return m

    if kind == 'group':
        _, num, body = node
        body_m = _compile_alt(body)
        if num is not None:
            idx = num - 1

            def m(text, pos, groups, cont, body_m=body_m, idx=idx):
                start = pos

                def k(p2, start=start, idx=idx, cont=cont):
                    old = groups[idx]
                    groups[idx] = (start, p2)
                    if cont(p2):
                        return True
                    groups[idx] = old
                    return False
                return body_m(text, pos, groups, k)
            return m
        else:
            def m(text, pos, groups, cont, body_m=body_m):
                return body_m(text, pos, groups, cont)
            return m

    if kind == 'rep':
        _, sub, lo, hi, greedy = node
        body_m = _compile_node(sub)

        def m(text, pos, groups, cont, body_m=body_m, lo=lo, hi=hi, greedy=greedy):
            return _rep_match(body_m, lo, hi, greedy, text, pos, groups, cont, 0, None)
        return m

    if kind == 'alt':
        return _compile_alt(node)

    raise AssertionError("unknown node kind: %r" % (kind,))


def _make_class_matcher(negate, members_literal, ranges, shorthands):
    def test(ch):
        if ch in members_literal:
            return True
        o = ord(ch)
        for lo, hi in ranges:
            if lo <= o <= hi:
                return True
        for sh in shorthands:
            if _shorthand_match(sh, ch):
                return True
        return False

    def m(text, pos, groups, cont):
        if pos >= len(text):
            return False
        ch = text[pos]
        matched = test(ch)
        if negate:
            matched = not matched
        if matched:
            return cont(pos + 1)
        return False
    return m


def _compile_seq(nodes):
    matchers = [_compile_node(n) for n in nodes]

    def make(idx):
        if idx == len(matchers):
            def base(text, pos, groups, cont):
                return cont(pos)
            return base
        else:
            nxt = make(idx + 1)
            cur = matchers[idx]

            def step(text, pos, groups, cont, cur=cur, nxt=nxt):
                return cur(text, pos, groups, lambda p, nxt=nxt, groups=groups, cont=cont: nxt(text, p, groups, cont))
            return step
    return make(0)


def _compile_alt(node):
    _, branches = node
    branch_matchers = [_compile_seq(b) for b in branches]

    def m(text, pos, groups, cont, branch_matchers=branch_matchers):
        for bm in branch_matchers:
            snap = list(groups)
            if bm(text, pos, groups, cont):
                return True
            groups[:] = snap
        return False
    return m


def _rep_match(body_m, lo, hi, greedy, text, pos, groups, cont, count, last_consumed):
    if count < lo:
        start = pos
        snap = list(groups)

        def k(p2, start=start, count=count):
            consumed = (p2 != start)
            return _rep_match(body_m, lo, hi, greedy, text, p2, groups, cont, count + 1, consumed)
        if body_m(text, pos, groups, k):
            return True
        groups[:] = snap
        return False

    can_iter = (hi is None or count < hi) and (last_consumed is not False)

    def try_more():
        start = pos
        snap = list(groups)

        def k(p2, start=start, count=count):
            consumed = (p2 != start)
            return _rep_match(body_m, lo, hi, greedy, text, p2, groups, cont, count + 1, consumed)
        if body_m(text, pos, groups, k):
            return True
        groups[:] = snap
        return False

    def try_stop():
        return cont(pos)

    if greedy:
        if can_iter and try_more():
            return True
        return try_stop()
    else:
        if try_stop():
            return True
        if can_iter:
            return try_more()
        return False


def _compile_pattern(pattern):
    parser = Parser(pattern)
    ast = parser.parse_alt()
    if parser.i != parser.n:
        # Only way to have leftover input at top level is a stray ')'
        raise PatternError('unbalanced_paren')
    matcher = _compile_alt(ast)
    return matcher, parser.group_count


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search(pattern, text):
    """Search `text` for the first (leftmost, then first-found-by-backtracking)
    match of `pattern`.

    Returns None if there is no match, else a tuple (start, end, groups)."""
    matcher, ngroups = _compile_pattern(pattern)
    n = len(text)
    for start in range(n + 1):
        groups = [None] * ngroups
        holder = {}

        def cont(p, holder=holder):
            holder['end'] = p
            return True

        if matcher(text, start, groups, cont):
            return (start, holder['end'], groups)
    return None
