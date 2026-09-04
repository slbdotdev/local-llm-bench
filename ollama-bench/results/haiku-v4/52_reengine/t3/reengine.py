"""Backtracking regular expression engine."""


class PatternError(ValueError):
    """Exception raised for malformed regex patterns."""
    def __init__(self, message, kind):
        super().__init__(message)
        self.kind = kind


class Parser:
    """Parses a regex pattern into an AST."""

    def __init__(self, pattern):
        self.pattern = pattern
        self.pos = 0
        self.group_count = 0
        self.next_group_num = 0  # Assign group numbers in order of opening (

    def peek(self, offset=0):
        """Peek at character without consuming."""
        idx = self.pos + offset
        return self.pattern[idx] if idx < len(self.pattern) else None

    def consume(self):
        """Consume and return current character."""
        ch = self.peek()
        self.pos += 1
        return ch

    def parse_pattern(self, in_group=False):
        """Parse a full pattern (one or more branches separated by |)."""
        branches = []
        branches.append(self.parse_branch(in_group))

        while self.peek() == '|':
            self.consume()  # consume |
            branches.append(self.parse_branch(in_group))

        return ('alternation', branches)

    def parse_branch(self, in_group=False):
        """Parse a branch (concatenation of atoms and quantifiers)."""
        atoms = []

        while self.pos < len(self.pattern):
            ch = self.peek()
            # Break on | (always) or ) (only if inside a group)
            if ch == '|' or (ch == ')' and in_group):
                break

            # If we see ) outside a group, it's an error (will be caught in parse_atom)

            # Check for quantifier at start of branch (nothing_to_repeat)
            if not atoms:
                if ch and ch in '*+?':
                    raise PatternError("nothing to repeat", "nothing_to_repeat")
                elif ch == '{':
                    # Check if it's a valid quantifier
                    saved_pos = self.pos
                    q = self.parse_quantifier()
                    if q is not None:
                        raise PatternError("nothing to repeat", "nothing_to_repeat")
                    # parse_quantifier restores position on failure

            atoms.append(self.parse_quantified_atom())

        return ('concatenation', atoms)

    def parse_quantified_atom(self):
        """Parse an atom followed by an optional quantifier."""
        atom = self.parse_atom()
        quantifier = self.parse_quantifier()

        if quantifier is None:
            return atom

        # Check if quantifier is on anchor (anchor_repeat)
        if atom[0] == 'anchor':
            raise PatternError("anchor repeat", "anchor_repeat")

        # Check for multiple quantifiers (multiple_repeat)
        ch = self.peek()
        if ch and ch in '*+?':
            raise PatternError("multiple repeat", "multiple_repeat")
        elif ch == '{':
            # Check if it's a valid quantifier
            q = self.parse_quantifier()
            if q is not None:
                raise PatternError("multiple repeat", "multiple_repeat")
            # parse_quantifier restores position on failure

        return ('quantified', atom, quantifier)

    def parse_atom(self):
        """Parse a single atom."""
        ch = self.peek()

        if ch == '(':
            return self.parse_group()
        elif ch == '[':
            return self.parse_class()
        elif ch == '.':
            self.consume()
            return ('dot',)
        elif ch == '^':
            self.consume()
            return ('anchor', 'start')
        elif ch == '$':
            self.consume()
            return ('anchor', 'end')
        elif ch == ')':
            # Unmatched closing paren
            raise PatternError("unbalanced paren", "unbalanced_paren")
        elif ch == '\\':
            return self.parse_escape()
        else:
            self.consume()
            return ('literal', ch)

    def parse_group(self):
        """Parse a group: (...) or (?:...)."""
        self.consume()  # consume (

        if self.peek() == '?':
            self.consume()  # consume ?
            if self.peek() != ':':
                raise PatternError("bad group", "bad_group")
            self.consume()  # consume :
            body = self.parse_pattern(in_group=True)
            if self.peek() != ')':
                raise PatternError("unbalanced paren", "unbalanced_paren")
            self.consume()  # consume )
            return ('non_capturing_group', body)
        else:
            # Assign group number now (before parsing body)
            self.next_group_num += 1
            group_num = self.next_group_num
            body = self.parse_pattern(in_group=True)
            if self.peek() != ')':
                raise PatternError("unbalanced paren", "unbalanced_paren")
            self.consume()  # consume )
            return ('capturing_group', group_num, body)

    def parse_escape(self):
        """Parse an escape sequence."""
        self.consume()  # consume \

        if self.pos >= len(self.pattern):
            raise PatternError("trailing backslash", "trailing_backslash")

        ch = self.consume()

        if ch == 'd':
            return ('class', set('0123456789'), False)
        elif ch == 'D':
            return ('class', set('0123456789'), True)
        elif ch == 'w':
            return ('class', set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'), False)
        elif ch == 'W':
            return ('class', set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'), True)
        elif ch == 's':
            return ('class', set(' \t\n\r\f\v'), False)
        elif ch == 'S':
            return ('class', set(' \t\n\r\f\v'), True)
        elif ch == 'b':
            return ('anchor', 'word')
        elif ch == 'B':
            return ('anchor', 'not_word')
        elif ch == 'n':
            return ('literal', '\n')
        elif ch == 't':
            return ('literal', '\t')
        elif ch == 'r':
            return ('literal', '\r')
        elif ch == 'f':
            return ('literal', '\f')
        elif ch == 'v':
            return ('literal', '\v')
        elif ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789':
            raise PatternError("bad escape", "bad_escape")
        else:
            return ('literal', ch)

    def parse_class(self):
        """Parse a character class [...]."""
        self.consume()  # consume [

        negated = False
        if self.peek() == '^':
            self.consume()
            negated = True

        # Check if next char is ] - if so, it's a member (not the closing bracket)
        first_char_is_close = False
        if self.peek() == ']':
            first_char_is_close = True

        members = []

        while self.pos < len(self.pattern):
            ch = self.peek()

            # Check if this is the closing bracket (only if not the first char)
            if ch == ']' and not first_char_is_close:
                self.consume()
                return ('class', members, negated)

            first_char_is_close = False  # Only the first ] after [ or [^ is special

            member = self.parse_class_member()

            # Check for range
            if self.peek() == '-':
                next_ch = self.peek(1)
                if next_ch is not None and next_ch != ']':
                    self.consume()  # consume -
                    member2 = self.parse_class_member()

                    # Validate range
                    # Check if member or member2 is a class escape
                    if member[0] == 'class_escape' or member2[0] == 'class_escape':
                        raise PatternError("bad range", "bad_range")

                    # Check if endpoints are literals and are reversed
                    if member[0] == 'literal' and member2[0] == 'literal':
                        if ord(member[1]) > ord(member2[1]):
                            raise PatternError("bad range", "bad_range")

                    members.append(('range', member, member2))
                else:
                    members.append(member)
            else:
                members.append(member)

        raise PatternError("unterminated class", "unterminated_class")

    def parse_class_member(self):
        """Parse a single member of a character class."""
        if self.peek() == '\\':
            self.consume()  # consume \
            if self.pos >= len(self.pattern):
                raise PatternError("trailing backslash", "trailing_backslash")

            ch = self.consume()

            if ch == 'd':
                return ('class_escape', 'd')
            elif ch == 'D':
                return ('class_escape', 'D')
            elif ch == 'w':
                return ('class_escape', 'w')
            elif ch == 'W':
                return ('class_escape', 'W')
            elif ch == 's':
                return ('class_escape', 's')
            elif ch == 'S':
                return ('class_escape', 'S')
            elif ch == 'b':
                return ('literal', '\x08')  # backspace
            elif ch == 'B':
                raise PatternError("bad escape", "bad_escape")
            elif ch == 'n':
                return ('literal', '\n')
            elif ch == 't':
                return ('literal', '\t')
            elif ch == 'r':
                return ('literal', '\r')
            elif ch == 'f':
                return ('literal', '\f')
            elif ch == 'v':
                return ('literal', '\v')
            else:
                return ('literal', ch)
        else:
            ch = self.consume()
            return ('literal', ch)

    def parse_quantifier(self):
        """Parse a quantifier after an atom."""
        if self.pos >= len(self.pattern):
            return None

        ch = self.peek()

        if ch == '*':
            self.consume()
            greedy = self.peek() != '?'
            if not greedy:
                self.consume()
            return ((0, float('inf')), greedy)
        elif ch == '+':
            self.consume()
            greedy = self.peek() != '?'
            if not greedy:
                self.consume()
            return ((1, float('inf')), greedy)
        elif ch == '?':
            self.consume()
            greedy = self.peek() != '?'
            if not greedy:
                self.consume()
            return ((0, 1), greedy)
        elif ch == '{':
            return self.parse_brace_quantifier()

        return None

    def parse_brace_quantifier(self):
        """Parse a {...} quantifier or return None if not a valid quantifier."""
        start_pos = self.pos
        self.consume()  # consume {

        # Read LO
        lo_str = ''
        while self.pos < len(self.pattern) and self.peek() in '0123456789':
            lo_str += self.consume()

        lo = int(lo_str) if lo_str else 0

        if self.peek() == '}' and lo_str:
            # {n}
            self.consume()
            # Check for bad_repeat before checking for greedy marker
            # Actually, {n} is always valid (lo == hi)
            greedy = self.peek() != '?'
            if not greedy:
                self.consume()
            return ((lo, lo), greedy)
        elif self.peek() == ',':
            self.consume()  # consume ,
            hi_str = ''
            while self.pos < len(self.pattern) and self.peek() in '0123456789':
                hi_str += self.consume()

            hi = int(hi_str) if hi_str else float('inf')

            if self.peek() == '}':
                self.consume()
                # Check for bad_repeat: lo > hi
                if hi != float('inf') and lo > hi:
                    raise PatternError("bad repeat", "bad_repeat")
                greedy = self.peek() != '?'
                if not greedy:
                    self.consume()
                return ((lo, hi), greedy)

        # Not a valid quantifier, backtrack
        self.pos = start_pos
        return None


class Matcher:
    """Matches a pattern against text using backtracking."""

    def __init__(self, pattern_ast, text, max_group_num=0):
        self.ast = pattern_ast
        self.text = text
        self.groups = {}  # group_num -> (start, end) or None
        self.max_group_num = max_group_num  # Highest group number

    def is_word_char(self, ch):
        """Check if character is a word character."""
        return ch and (ch.isalnum() or ch == '_')

    def match_at(self, pos, node):
        """
        Try to match node at position pos.
        Yields (new_pos, None) for each successful match.
        """
        if node[0] == 'alternation':
            # Try each branch left to right
            for branch in node[1]:
                yield from self.match_at(pos, branch)

        elif node[0] == 'concatenation':
            # Match concatenation of atoms
            yield from self.match_concat(pos, node[1], 0)

        elif node[0] == 'capturing_group':
            # Save and restore group spans
            group_num = node[1]
            body = node[2]

            old_value = self.groups.get(group_num)
            self.groups[group_num] = (pos, pos)  # Mark start

            for new_pos, _ in self.match_at(pos, body):
                self.groups[group_num] = (pos, new_pos)  # Update end
                yield (new_pos, None)

            # Restore on backtrack
            if old_value is None:
                self.groups.pop(group_num, None)
            else:
                self.groups[group_num] = old_value

        elif node[0] == 'non_capturing_group':
            # Just match the body
            yield from self.match_at(pos, node[1])

        elif node[0] == 'quantified':
            atom = node[1]
            (lo, hi), greedy = node[2]
            yield from self.match_quantified(pos, atom, lo, hi, greedy)

        elif node[0] == 'literal':
            if pos < len(self.text) and self.text[pos] == node[1]:
                yield (pos + 1, None)

        elif node[0] == 'dot':
            if pos < len(self.text) and self.text[pos] != '\n':
                yield (pos + 1, None)

        elif node[0] == 'anchor':
            if node[1] == 'start':
                if pos == 0:
                    yield (pos, None)
            elif node[1] == 'end':
                if pos == len(self.text) or (pos == len(self.text) - 1 and self.text[pos] == '\n'):
                    yield (pos, None)
            elif node[1] == 'word':
                before_is_word = self.is_word_char(self.text[pos - 1] if pos > 0 else None)
                after_is_word = self.is_word_char(self.text[pos] if pos < len(self.text) else None)
                if before_is_word != after_is_word:
                    yield (pos, None)
            elif node[1] == 'not_word':
                before_is_word = self.is_word_char(self.text[pos - 1] if pos > 0 else None)
                after_is_word = self.is_word_char(self.text[pos] if pos < len(self.text) else None)
                if before_is_word == after_is_word:
                    yield (pos, None)

        elif node[0] == 'class':
            if pos < len(self.text):
                if self.match_class(self.text[pos], node[1], node[2]):
                    yield (pos + 1, None)

    def match_concat(self, pos, atoms, atom_idx):
        """Match concatenation of atoms."""
        if atom_idx >= len(atoms):
            yield (pos, None)
            return

        atom = atoms[atom_idx]
        for new_pos, _ in self.match_at(pos, atom):
            yield from self.match_concat(new_pos, atoms, atom_idx + 1)

    def match_quantified(self, pos, atom, lo, hi, greedy):
        """Match a quantified atom with proper backtracking."""
        # Recursively match iterations
        def iterate(current_pos, current_count, prev_pos_was_same):
            """
            Iterate: match atom or proceed.
            current_pos: current position in text
            current_count: number of iterations so far
            prev_pos_was_same: whether the previous iteration consumed 0 characters
            """
            # Base: we've matched the minimum required
            if current_count >= lo:
                # Yield current position (no more iterations)
                if greedy:
                    # For greedy, try extending first (below), then backtrack to this position
                    pass
                else:
                    # For non-greedy, try this position first
                    yield (current_pos, None)

            # Try to match more iterations
            if current_count < hi:
                can_iterate = (current_count == 0) or (not prev_pos_was_same)

                if can_iterate:
                    for next_pos, _ in self.match_at(current_pos, atom):
                        iteration_consumed = (next_pos > current_pos)
                        if greedy:
                            # Greedy: recursively extend (depth-first), yielding longer matches first
                            yield from iterate(next_pos, current_count + 1, not iteration_consumed)
                        else:
                            # Non-greedy: recursively extend, but non-greedy will choose shorter
                            yield from iterate(next_pos, current_count + 1, not iteration_consumed)

            # After trying to extend (or if we can't), yield current position if we have enough iterations
            if current_count >= lo:
                if greedy:
                    # For greedy, yield after trying extensions
                    yield (current_pos, None)

        yield from iterate(pos, 0, False)

    def match_class(self, ch, members, negated):
        """Check if character matches a class."""
        # Handle both set and list representations
        if isinstance(members, set):
            matches = ch in members
        else:
            matches = False
            for member in members:
                if member[0] == 'literal':
                    if ch == member[1]:
                        matches = True
                        break
                elif member[0] == 'class_escape':
                    escape = member[1]
                    if escape == 'd' and ch in '0123456789':
                        matches = True
                        break
                    elif escape == 'D' and ch not in '0123456789':
                        matches = True
                        break
                    elif escape == 'w' and (ch.isalnum() or ch == '_'):
                        matches = True
                        break
                    elif escape == 'W' and not (ch.isalnum() or ch == '_'):
                        matches = True
                        break
                    elif escape == 's' and ch in ' \t\n\r\f\v':
                        matches = True
                        break
                    elif escape == 'S' and ch not in ' \t\n\r\f\v':
                        matches = True
                        break
                elif member[0] == 'range':
                    m1, m2 = member[1], member[2]
                    if m1[0] == 'class_escape' or m2[0] == 'class_escape':
                        raise PatternError("bad range", "bad_range")
                    c1 = m1[1] if m1[0] == 'literal' else None
                    c2 = m2[1] if m2[0] == 'literal' else None
                    if c1 and c2 and ord(c1) <= ord(ch) <= ord(c2):
                        matches = True
                        break

        return matches != negated


def validate_pattern(pattern):
    """Validate a pattern and build AST."""
    parser = Parser(pattern)

    # Track quantifiers to validate them
    ast = parser.parse_pattern()

    # Additional validation pass
    def validate_quantifiers(node):
        if node[0] == 'alternation':
            for branch in node[1]:
                validate_quantifiers(branch)
        elif node[0] == 'concatenation':
            for i, atom in enumerate(node[1]):
                if atom[0] == 'quantified':
                    inner = atom[1]
                    lo, hi = atom[2][0]

                    # Check if quantifier is on anchor
                    if inner[0] == 'anchor':
                        raise PatternError("anchor repeat", "anchor_repeat")

                    # Check bounds
                    if lo > hi and hi != float('inf'):
                        raise PatternError("bad repeat", "bad_repeat")

                    # Check for multiple quantifiers
                    if i > 0:
                        prev = node[1][i - 1]
                        if prev[0] == 'quantified':
                            raise PatternError("multiple repeat", "multiple_repeat")

                    # Check if quantifier at start
                    if i == 0:
                        raise PatternError("nothing to repeat", "nothing_to_repeat")

                validate_quantifiers(atom)
        elif node[0] == 'capturing_group':
            validate_quantifiers(node[2])
        elif node[0] == 'non_capturing_group':
            validate_quantifiers(node[1])

    # Better approach: validate during parse
    return ast


def search(pattern, text):
    """Search for pattern in text."""
    # Parse pattern (validation happens during parsing)
    parser = Parser(pattern)
    ast = parser.parse_pattern()

    # Try to match at each position
    for start_pos in range(len(text) + 1):
        matcher = Matcher(ast, text, parser.next_group_num)

        for end_pos, _ in matcher.match_at(start_pos, ast):
            # Collect groups in order of group number
            groups = []
            for group_num in range(1, parser.next_group_num + 1):
                if group_num in matcher.groups:
                    span = matcher.groups[group_num]
                    groups.append(span)
                else:
                    groups.append(None)

            return (start_pos, end_pos, groups)

    return None
