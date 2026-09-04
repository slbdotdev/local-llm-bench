"""
A backtracking regular-expression engine written from scratch.

Public API:
    PatternError -- exception raised for malformed patterns; has a `.kind`
                    attribute (see the table below).
    search(pattern, text) -- leftmost-first backtracking search.
"""

import sys
import threading

sys.setrecursionlimit(1000000)


class PatternError(ValueError):
    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind)


# ---------------------------------------------------------------------------
# AST node types
# ---------------------------------------------------------------------------

class Literal:
    __slots__ = ('c',)

    def __init__(self, c):
        self.c = c


class AnyChar:
    __slots__ = ()


class Anchor:
    __slots__ = ('kind',)

    def __init__(self, kind):
        self.kind = kind  # 'start' 'end' 'wordb' 'nwordb'


class CharClass:
    __slots__ = ('members', 'negated')

    def __init__(self, members, negated):
        self.members = members
        self.negated = negated


class Group:
    __slots__ = ('capturing', 'num', 'body')

    def __init__(self, capturing, num, body):
        self.capturing = capturing
        self.num = num
        self.body = body


class Concat:
    __slots__ = ('items',)

    def __init__(self, items):
        self.items = items


class Alternation:
    __slots__ = ('branches',)

    def __init__(self, branches):
        self.branches = branches


class Repeat:
    __slots__ = ('body', 'lo', 'hi', 'greedy')

    def __init__(self, body, lo, hi, greedy):
        self.body = body
        self.lo = lo
        self.hi = hi
        self.greedy = greedy


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

_DIGITS = '0123456789'


def _parse_brace(s, i):
    """If s[i] == '{' starts a well-formed brace quantifier, return
    (lo, hi, end_index) with hi possibly None (unbounded); else None.
    Does not mutate anything; pure lookahead."""
    n = len(s)
    j = i + 1
    lo_start = j
    while j < n and s[j] in _DIGITS:
        j += 1
    lo_str = s[lo_start:j]
    if j < n and s[j] == '}' and lo_str != '':
        v = int(lo_str)
        return (v, v, j + 1)
    if j < n and s[j] == ',':
        j2 = j + 1
        hi_start = j2
        while j2 < n and s[j2] in _DIGITS:
            j2 += 1
        hi_str = s[hi_start:j2]
        if j2 < n and s[j2] == '}':
            lo = int(lo_str) if lo_str != '' else 0
            hi = int(hi_str) if hi_str != '' else None
            return (lo, hi, j2 + 1)
    return None


def _is_ascii_alnum(x):
    return ('A' <= x <= 'Z') or ('a' <= x <= 'z') or ('0' <= x <= '9')


class Parser:
    def __init__(self, pattern):
        self.s = pattern
        self.i = 0
        self.n = len(pattern)
        self.group_count = 0

    # -- top level ---------------------------------------------------

    def parse_alternation(self):
        branches = [self.parse_concat()]
        while self.i < self.n and self.s[self.i] == '|':
            self.i += 1
            branches.append(self.parse_concat())
        return Alternation(branches)

    def parse_concat(self):
        items = []
        while self.i < self.n and self.s[self.i] not in '|)':
            ch = self.s[self.i]
            if ch in '*+?':
                raise PatternError('nothing_to_repeat')
            if ch == '{':
                if _parse_brace(self.s, self.i) is not None:
                    raise PatternError('nothing_to_repeat')
                # else: falls through, parsed as literal '{' atom below
            atom = self.parse_atom()
            atom = self.maybe_parse_quantifier(atom)
            items.append(atom)
        return Concat(items)

    # -- atoms ---------------------------------------------------------

    def parse_atom(self):
        ch = self.s[self.i]
        if ch == '(':
            return self.parse_group()
        if ch == '[':
            return self.parse_class()
        if ch == '.':
            self.i += 1
            return AnyChar()
        if ch == '^':
            self.i += 1
            return Anchor('start')
        if ch == '$':
            self.i += 1
            return Anchor('end')
        if ch == '\\':
            return self.parse_escape_outside()
        self.i += 1
        return Literal(ch)

    def parse_group(self):
        # self.s[self.i] == '('
        self.i += 1
        is_capturing = True
        if self.i < self.n and self.s[self.i] == '?':
            if self.i + 1 < self.n and self.s[self.i + 1] == ':':
                is_capturing = False
                self.i += 2
            else:
                raise PatternError('bad_group')
        group_num = None
        if is_capturing:
            self.group_count += 1
            group_num = self.group_count
        body = self.parse_alternation()
        if self.i >= self.n:
            raise PatternError('unbalanced_paren')
        # self.s[self.i] == ')'
        self.i += 1
        return Group(is_capturing, group_num, body)

    def parse_escape_outside(self):
        # self.s[self.i] == '\\'
        if self.i + 1 >= self.n:
            raise PatternError('trailing_backslash')
        x = self.s[self.i + 1]
        self.i += 2
        if x in 'dwsDWS':
            return CharClass([('set', x)], False)
        if x == 'n':
            return Literal('\n')
        if x == 't':
            return Literal('\t')
        if x == 'r':
            return Literal('\r')
        if x == 'f':
            return Literal('\f')
        if x == 'v':
            return Literal('\v')
        if x == 'b':
            return Anchor('wordb')
        if x == 'B':
            return Anchor('nwordb')
        if _is_ascii_alnum(x):
            raise PatternError('bad_escape')
        return Literal(x)

    # -- character classes ---------------------------------------------

    def parse_class(self):
        # self.s[self.i] == '['
        self.i += 1
        negated = False
        if self.i < self.n and self.s[self.i] == '^':
            negated = True
            self.i += 1
        members = []
        if self.i < self.n and self.s[self.i] == ']':
            members.append(('char', ']'))
            self.i += 1
        while True:
            if self.i >= self.n:
                raise PatternError('unterminated_class')
            ch = self.s[self.i]
            if ch == ']':
                self.i += 1
                break
            m = self.read_class_member()
            if (self.i < self.n and self.s[self.i] == '-'
                    and self.i + 1 < self.n and self.s[self.i + 1] != ']'):
                self.i += 1  # consume '-'
                m2 = self.read_class_member()
                if m[0] == 'set' or m2[0] == 'set':
                    raise PatternError('bad_range')
                lo_c, hi_c = m[1], m2[1]
                if ord(lo_c) > ord(hi_c):
                    raise PatternError('bad_range')
                members.append(('range', lo_c, hi_c))
            else:
                members.append(m)
        return CharClass(members, negated)

    def read_class_member(self):
        ch = self.s[self.i]
        if ch == '\\':
            if self.i + 1 >= self.n:
                raise PatternError('trailing_backslash')
            x = self.s[self.i + 1]
            self.i += 2
            if x in 'dwsDWS':
                return ('set', x)
            if x == 'n':
                return ('char', '\n')
            if x == 't':
                return ('char', '\t')
            if x == 'r':
                return ('char', '\r')
            if x == 'f':
                return ('char', '\f')
            if x == 'v':
                return ('char', '\v')
            if x == 'b':
                return ('char', '\x08')
            if x == 'B':
                raise PatternError('bad_escape')
            if _is_ascii_alnum(x):
                raise PatternError('bad_escape')
            return ('char', x)
        else:
            self.i += 1
            return ('char', ch)

    # -- quantifiers -----------------------------------------------------

    def maybe_parse_quantifier(self, atom):
        if self.i >= self.n:
            return atom
        ch = self.s[self.i]
        if ch == '*':
            lo, hi = 0, None
            self.i += 1
        elif ch == '+':
            lo, hi = 1, None
            self.i += 1
        elif ch == '?':
            lo, hi = 0, 1
            self.i += 1
        elif ch == '{':
            r = _parse_brace(self.s, self.i)
            if r is None:
                return atom
            lo, hi, end = r
            self.i = end
        else:
            return atom

        greedy = True
        if self.i < self.n and self.s[self.i] == '?':
            greedy = False
            self.i += 1

        # order: bad_repeat, then anchor_repeat, then multiple_repeat
        if hi is not None and lo > hi:
            raise PatternError('bad_repeat')
        if isinstance(atom, Anchor):
            raise PatternError('anchor_repeat')
        if self.i < self.n:
            nxt = self.s[self.i]
            if nxt in '*+?':
                raise PatternError('multiple_repeat')
            if nxt == '{' and _parse_brace(self.s, self.i) is not None:
                raise PatternError('multiple_repeat')
        return Repeat(atom, lo, hi, greedy)


def parse(pattern):
    p = Parser(pattern)
    root = p.parse_alternation()
    if p.i < p.n:
        # only way to stop before the end is an unmatched ')'
        raise PatternError('unbalanced_paren')
    return root, p.group_count


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

_WORD_START = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
_WORD_LOWER = 'abcdefghijklmnopqrstuvwxyz'
_WS = ' \t\n\r\f\v'


def _is_word(c):
    return ('A' <= c <= 'Z') or ('a' <= c <= 'z') or ('0' <= c <= '9') or c == '_'


def _is_word_boundary(pos, text):
    before = pos > 0 and _is_word(text[pos - 1])
    after = pos < len(text) and _is_word(text[pos])
    return before != after


def _class_member_matches(member, c):
    t = member[0]
    if t == 'char':
        return c == member[1]
    if t == 'range':
        return member[1] <= c <= member[2]
    # 'set'
    name = member[1]
    if name == 'd':
        return '0' <= c <= '9'
    if name == 'D':
        return not ('0' <= c <= '9')
    if name == 'w':
        return _is_word(c)
    if name == 'W':
        return not _is_word(c)
    if name == 's':
        return c in _WS
    if name == 'S':
        return c not in _WS
    raise AssertionError('bad set name')


def _class_matches(node, c):
    matched = False
    for m in node.members:
        if _class_member_matches(m, c):
            matched = True
            break
    return matched != node.negated


def _match_node(node, pos, text, groups):
    t = type(node)

    if t is Literal:
        if pos < len(text) and text[pos] == node.c:
            yield pos + 1
        return

    if t is AnyChar:
        if pos < len(text) and text[pos] != '\n':
            yield pos + 1
        return

    if t is CharClass:
        if pos < len(text) and _class_matches(node, text[pos]):
            yield pos + 1
        return

    if t is Anchor:
        k = node.kind
        if k == 'start':
            if pos == 0:
                yield pos
        elif k == 'end':
            if pos == len(text) or (pos == len(text) - 1 and text[pos] == '\n'):
                yield pos
        elif k == 'wordb':
            if _is_word_boundary(pos, text):
                yield pos
        elif k == 'nwordb':
            if not _is_word_boundary(pos, text):
                yield pos
        return

    if t is Concat:
        items = node.items

        def gen(idx, p):
            if idx == len(items):
                yield p
                return
            for p2 in _match_node(items[idx], p, text, groups):
                yield from gen(idx + 1, p2)

        yield from gen(0, pos)
        return

    if t is Alternation:
        for br in node.branches:
            yield from _match_node(br, pos, text, groups)
        return

    if t is Group:
        if node.capturing:
            idx = node.num - 1
            saved = groups[idx]
            for end in _match_node(node.body, pos, text, groups):
                groups[idx] = (pos, end)
                yield end
            groups[idx] = saved
        else:
            yield from _match_node(node.body, pos, text, groups)
        return

    if t is Repeat:
        yield from _repeat_match(node, pos, text, groups)
        return

    raise AssertionError('unknown node type')


def _repeat_match(node, pos, text, groups):
    body = node.body
    lo = node.lo
    hi = node.hi
    greedy = node.greedy

    def rec(p, count, prev_consumed):
        if count < lo:
            for p2 in _match_node(body, p, text, groups):
                yield from rec(p2, count + 1, p2 != p)
            return
        can_more = (hi is None or count < hi)
        allow_attempt = can_more and (count == lo or prev_consumed)
        if greedy:
            if allow_attempt:
                for p2 in _match_node(body, p, text, groups):
                    yield from rec(p2, count + 1, p2 != p)
            yield p
        else:
            yield p
            if allow_attempt:
                for p2 in _match_node(body, p, text, groups):
                    yield from rec(p2, count + 1, p2 != p)

    yield from rec(pos, 0, False)


def _search_impl(pattern, text):
    root, group_count = parse(pattern)
    n = len(text)
    for start in range(n + 1):
        groups = [None] * group_count
        for end in _match_node(root, start, text, groups):
            return (start, end, list(groups))
    return None


def search(pattern, text):
    """search(pattern, text) -> (start, end, groups) or None.

    Runs the actual work on a worker thread with a large stack, since the
    backtracking search recurses proportionally to the length of the match.
    """
    box = {}

    def run():
        try:
            box['value'] = _search_impl(pattern, text)
        except PatternError as e:
            box['error'] = e
        except BaseException as e:  # pragma: no cover - safety net
            box['unexpected'] = e

    old_stack_size = None
    try:
        old_stack_size = threading.stack_size()
        threading.stack_size(64 * 1024 * 1024)
    except (ValueError, RuntimeError):
        pass

    th = threading.Thread(target=run)
    th.start()
    th.join()

    if old_stack_size is not None:
        try:
            threading.stack_size(old_stack_size)
        except (ValueError, RuntimeError):
            pass

    if 'error' in box:
        raise box['error']
    if 'unexpected' in box:
        raise box['unexpected']
    return box['value']
