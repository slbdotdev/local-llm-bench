"""A small regular-expression engine implemented from scratch.

Supported syntax:
  - literal characters
  - `.` matches any single character
  - backslash escapes (`\\.` -> literal `.`, `\\\\` -> literal `\\`, etc.)
  - character classes `[abc]`, ranges `[a-z0-9]`, negated classes `[^abc]`
  - quantifiers `*`, `+`, `?`
  - grouping `( ... )`
  - alternation `|` (lowest precedence)

Only `fullmatch(pattern, text)` is exposed; it anchors at both ends.
"""

# ---------------------------------------------------------------------------
# AST node types.  Each node is a tuple whose first element is a tag string.
#
#   ('lit', ch)                  -- a literal character
#   ('any',)                     -- '.'
#   ('class', set_of_chars, neg) -- a character class (neg = negated?)
#   ('group', alternation)       -- a parenthesised group; alternation is a
#                                    list of concatenations (see below)
#   ('star', node)                -- node*
#   ('plus', node)                -- node+
#   ('opt', node)                  -- node?
#
# A "concatenation" is a list of the above nodes.
# An "alternation" is a list of concatenations (the '|' branches).
# ---------------------------------------------------------------------------


class _Parser:
    def __init__(self, pattern):
        self.p = pattern
        self.i = 0
        self.n = len(pattern)

    def peek(self):
        if self.i < self.n:
            return self.p[self.i]
        return None

    def advance(self):
        ch = self.p[self.i]
        self.i += 1
        return ch

    def parse(self):
        alt = self.parse_alternation()
        if self.i != self.n:
            # Should only happen if there's a stray ')' left unconsumed.
            raise ValueError("Unbalanced parentheses in pattern")
        return alt

    def parse_alternation(self):
        branches = [self.parse_concat()]
        while self.peek() == '|':
            self.advance()
            branches.append(self.parse_concat())
        return branches

    def parse_concat(self):
        nodes = []
        while True:
            ch = self.peek()
            if ch is None or ch == '|' or ch == ')':
                break
            atom = self.parse_atom()
            atom = self.parse_quantifier(atom)
            nodes.append(atom)
        return nodes

    def parse_quantifier(self, atom):
        ch = self.peek()
        if ch in ('*', '+', '?'):
            self.advance()
            if ch == '*':
                return ('star', atom)
            elif ch == '+':
                return ('plus', atom)
            else:
                return ('opt', atom)
        return atom

    def parse_atom(self):
        ch = self.peek()
        if ch is None:
            raise ValueError("Unexpected end of pattern")
        if ch in ('*', '+', '?'):
            raise ValueError("Quantifier '%s' with nothing before it" % ch)
        if ch == '(':
            self.advance()
            alt = self.parse_alternation()
            if self.peek() != ')':
                raise ValueError("Unbalanced parentheses in pattern")
            self.advance()
            return ('group', alt)
        if ch == ')':
            raise ValueError("Unbalanced parentheses in pattern")
        if ch == '[':
            return self.parse_class()
        if ch == '\\':
            self.advance()
            if self.i >= self.n:
                raise ValueError("Trailing backslash in pattern")
            escaped = self.advance()
            return ('lit', escaped)
        if ch == '.':
            self.advance()
            return ('any',)
        self.advance()
        return ('lit', ch)

    def parse_class(self):
        # assumes current char is '['
        self.advance()  # consume '['
        neg = False
        if self.peek() == '^':
            neg = True
            self.advance()

        chars = set()
        first = True
        while True:
            ch = self.peek()
            if ch is None:
                raise ValueError("Unterminated character class")
            if ch == ']' and not first:
                self.advance()
                break
            first = False
            if ch == ']':
                # literal ']' as first character
                self.advance()
                chars.add(']')
                continue
            if ch == '\\':
                self.advance()
                if self.i >= self.n:
                    raise ValueError("Trailing backslash in pattern")
                lit = self.advance()
                chars.add(lit)
                continue
            # potential range a-b
            self.advance()
            if (
                self.peek() == '-'
                and self.i + 1 < self.n
                and self.p[self.i + 1] != ']'
            ):
                # ch '-' end  form a range, unless '-' is trailing
                self.advance()  # consume '-'
                end = self.peek()
                if end is None:
                    raise ValueError("Unterminated character class")
                if end == '\\':
                    self.advance()
                    if self.i >= self.n:
                        raise ValueError("Trailing backslash in pattern")
                    end = self.advance()
                else:
                    self.advance()
                if ord(end) < ord(ch):
                    raise ValueError("Bad character range in class")
                for code in range(ord(ch), ord(end) + 1):
                    chars.add(chr(code))
            else:
                chars.add(ch)
        return ('class', chars, neg)


def _parse(pattern):
    parser = _Parser(pattern)
    return parser.parse()


# ---------------------------------------------------------------------------
# Matching engine: backtracking via generators of possible end positions.
# Each "match" function takes a position in the text and yields all
# possible end positions (indices) after consuming input for that node.
# ---------------------------------------------------------------------------


def _match_node(node, text, pos):
    tag = node[0]
    if tag == 'lit':
        ch = node[1]
        if pos < len(text) and text[pos] == ch:
            yield pos + 1
        return
    if tag == 'any':
        if pos < len(text):
            yield pos + 1
        return
    if tag == 'class':
        _, chars, neg = node
        if pos < len(text):
            in_class = text[pos] in chars
            if in_class != neg:
                yield pos + 1
        return
    if tag == 'group':
        alt = node[1]
        for branch in alt:
            yield from _match_concat(branch, text, pos)
        return
    if tag == 'star':
        yield from _match_repeat(node[1], text, pos, 0, None)
        return
    if tag == 'plus':
        yield from _match_repeat(node[1], text, pos, 1, None)
        return
    if tag == 'opt':
        yield from _match_repeat(node[1], text, pos, 0, 1)
        return
    raise AssertionError("unknown node tag: %r" % (tag,))


def _match_repeat(node, text, pos, min_count, max_count):
    """Yield all end positions reachable by matching `node` between
    min_count and max_count (inclusive, None = unbounded) times,
    exploring all repeat counts (greedy-first) so the caller can
    backtrack into whichever count lets the rest of the pattern match."""

    # positions reachable after exactly k repetitions, tracked to avoid
    # infinite loops on zero-width matches.
    seen_at_count = [{pos}]  # seen_at_count[0] = positions after 0 reps

    def positions_after(k):
        while len(seen_at_count) <= k:
            prev_positions = seen_at_count[-1]
            nxt = set()
            for p in prev_positions:
                for np in _match_node(node, text, p):
                    nxt.add(np)
            seen_at_count.append(nxt)
            if not nxt:
                break
        if k < len(seen_at_count):
            return seen_at_count[k]
        return set()

    counts = []
    k = 0
    while True:
        if max_count is not None and k > max_count:
            break
        ps = positions_after(k)
        if not ps and k > 0:
            break
        counts.append(k)
        if not ps:
            break
        k += 1
        if k > len(text) + 1:
            # safety valve against pathological zero-width loops
            break

    for k in sorted((c for c in counts if c >= min_count), reverse=True):
        for p in positions_after(k):
            yield p


def _match_concat(nodes, text, pos):
    if not nodes:
        yield pos
        return
    head, rest = nodes[0], nodes[1:]
    for p in _match_node(head, text, pos):
        yield from _match_concat(rest, text, p)


def fullmatch(pattern: str, text: str) -> bool:
    alt = _parse(pattern)
    for branch in alt:
        for end in _match_concat(branch, text, 0):
            if end == len(text):
                return True
    return False
