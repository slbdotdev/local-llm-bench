"""A backtracking regular-expression engine written from scratch."""

class PatternError(ValueError):
    """Exception raised for malformed regex patterns."""
    def __init__(self, message, kind):
        super().__init__(message)
        self.kind = kind


# AST node types
class Literal:
    def __init__(self, char):
        self.char = char


class CharClass:
    def __init__(self, negated, members):
        self.negated = negated
        self.members = members  # list of (type, value) tuples


class Dot:
    pass


class Anchor:
    def __init__(self, anchor_type):  # 'start', 'end', 'word', 'non_word'
        self.anchor_type = anchor_type


class Group:
    def __init__(self, capturing, body, group_num=None):
        self.capturing = capturing
        self.body = body
        self.group_num = group_num


class Alternation:
    def __init__(self, branches):
        self.branches = branches


class Quantified:
    def __init__(self, atom, lo, hi, greedy):
        self.atom = atom
        self.lo = lo
        self.hi = hi
        self.greedy = greedy


class Sequence:
    def __init__(self, items):
        self.items = items


class Parser:
    def __init__(self, pattern):
        self.pattern = pattern
        self.pos = 0
        self.group_count = 0

    def error(self, kind):
        raise PatternError(f"Pattern error: {kind}", kind)

    def peek(self, offset=0):
        pos = self.pos + offset
        if pos < len(self.pattern):
            return self.pattern[pos]
        return None

    def consume(self):
        ch = self.peek()
        self.pos += 1
        return ch

    def parse(self):
        """Parse the entire pattern."""
        branches = self.parse_alternation(top_level=True)
        if self.pos < len(self.pattern) and self.pattern[self.pos] == ')':
            self.error('unbalanced_paren')
        return branches

    def parse_alternation(self, top_level=False):
        """Parse alternation (branches separated by |)."""
        branches = []
        while True:
            branch = self.parse_concat()
            branches.append(branch)

            if self.peek() == '|':
                self.consume()
            else:
                break

        if len(branches) == 1:
            return branches[0]
        return Alternation(branches)

    def parse_concat(self):
        """Parse concatenation of atoms."""
        items = []
        while True:
            ch = self.peek()

            if ch is None or ch == ')' or ch == '|':
                break

            item = self.parse_quantified()
            items.append(item)

        if len(items) == 0:
            return Sequence([])
        elif len(items) == 1:
            return items[0]
        else:
            return Sequence(items)

    def parse_quantified(self):
        """Parse an atom followed by an optional quantifier."""
        atom = self.parse_atom()

        # Special case: if atom is Literal('{'), check if it's a well-formed quantifier
        # If so, it means no preceding atom, which is an error
        if isinstance(atom, Literal) and atom.char == '{':
            save_pos = self.pos
            # Try to parse as a bounded quantifier
            lo_str = ''
            while self.peek() and self.peek().isdigit():
                lo_str += self.consume()

            next_ch = self.peek()
            is_well_formed = False

            if next_ch == '}' and lo_str:
                # {LO}
                is_well_formed = True
            elif next_ch == ',':
                # {LO,HI} - skip the comma and HI digits
                self.consume()  # consume ','
                while self.peek() and self.peek().isdigit():
                    self.consume()
                if self.peek() == '}':
                    is_well_formed = True

            self.pos = save_pos

            if is_well_formed:
                # This is a well-formed quantifier with no preceding atom
                self.error('nothing_to_repeat')

        # Check if this is an anchor and we have a quantifier
        is_anchor = isinstance(atom, Anchor)

        # Now check for quantifier
        ch = self.peek()

        if ch == '*':
            self.consume()
            return self.apply_quantifier(atom, 0, None, start_pos=self.pos - 1, is_anchor=is_anchor)
        elif ch == '+':
            self.consume()
            return self.apply_quantifier(atom, 1, None, start_pos=self.pos - 1, is_anchor=is_anchor)
        elif ch == '?':
            self.consume()
            return self.apply_quantifier(atom, 0, 1, start_pos=self.pos - 1, is_anchor=is_anchor)
        elif ch == '{':
            # Try to parse bounded quantifier
            save_pos = self.pos
            self.consume()  # consume '{'

            # Read LO
            lo_str = ''
            while self.peek() and self.peek().isdigit():
                lo_str += self.consume()

            next_ch = self.peek()

            if next_ch == '}' and lo_str:
                # {N}
                self.consume()  # consume '}'
                lo = int(lo_str)
                hi = lo

                return self.apply_quantifier(atom, lo, hi, start_pos=self.pos - 1, is_anchor=is_anchor)

            elif next_ch == ',':
                # {N,} or {N,M}
                self.consume()  # consume ','

                hi_str = ''
                while self.peek() and self.peek().isdigit():
                    hi_str += self.consume()

                if self.peek() == '}':
                    self.consume()  # consume '}'
                    lo = int(lo_str) if lo_str else 0
                    hi = int(hi_str) if hi_str else None

                    return self.apply_quantifier(atom, lo, hi, start_pos=self.pos - 1, is_anchor=is_anchor)
                else:
                    # Not a valid quantifier, treat { as literal
                    self.pos = save_pos
                    return atom
            else:
                # Not a valid quantifier, treat { as literal
                self.pos = save_pos
                return atom

        return atom

    def apply_quantifier(self, atom, lo, hi, start_pos, is_anchor=False):
        """Apply quantifier to atom and check for errors."""
        # Check for bad_repeat (LO > HI) - first per spec
        if hi is not None and lo > hi:
            self.error('bad_repeat')

        # Check for anchor_repeat - second per spec
        if is_anchor:
            self.error('anchor_repeat')

        # Check for greedy/non-greedy
        greedy = True
        if self.peek() == '?':
            self.consume()
            greedy = False

        # Check for multiple repeat (after consuming the non-greedy ?)
        if self.peek() in ('*', '+', '?', '{'):
            next_ch = self.peek()
            if next_ch in ('*', '+', '?'):
                self.error('multiple_repeat')
            elif next_ch == '{':
                # Check if it's a valid quantifier
                save_pos = self.pos
                self.consume()
                has_digit = self.peek() and self.peek().isdigit()
                self.pos = save_pos

                if has_digit or self.peek(1) == ',':
                    self.error('multiple_repeat')

        return Quantified(atom, lo, hi, greedy)

    def parse_atom(self):
        """Parse a single atom."""
        ch = self.peek()

        if ch is None:
            self.error('nothing_to_repeat')
        elif ch == '(':
            return self.parse_group()
        elif ch == '[':
            return self.parse_class()
        elif ch == '.':
            self.consume()
            return Dot()
        elif ch == '^':
            self.consume()
            return Anchor('start')
        elif ch == '$':
            self.consume()
            return Anchor('end')
        elif ch == '\\':
            return self.parse_escape(in_class=False)
        elif ch in (')', '|', '*', '+', '?'):
            self.error('nothing_to_repeat')
        else:
            self.consume()
            return Literal(ch)

    def parse_group(self):
        """Parse a group."""
        self.consume()  # consume '('

        capturing = True
        if self.peek() == '?' and self.peek(1) == ':':
            capturing = False
            self.consume()  # consume '?'
            self.consume()  # consume ':'
        elif self.peek() == '?':
            self.error('bad_group')

        group_num = None
        if capturing:
            self.group_count += 1
            group_num = self.group_count

        body = self.parse_alternation(top_level=False)

        if self.peek() != ')':
            self.error('unbalanced_paren')

        self.consume()  # consume ')'

        return Group(capturing, body, group_num)

    def parse_class(self):
        """Parse a character class."""
        self.consume()  # consume '['

        negated = False
        if self.peek() == '^':
            negated = True
            self.consume()

        members = []

        # Special case: ] as first member
        if self.peek() == ']':
            members.append(('char', ']'))
            self.consume()

        while True:
            if self.peek() is None:
                self.error('unterminated_class')

            if self.peek() == ']':
                self.consume()
                break

            # Parse a member
            if self.peek() == '\\':
                member = self.parse_escape(in_class=True)
                if isinstance(member, Literal):
                    members.append(('char', member.char))
                elif isinstance(member, CharClass):
                    # It's a char class escape like \d, \w, \s
                    # Extract the escape type from the CharClass
                    escape_type = member.members[0][1]
                    members.append(('escape', escape_type))
                else:
                    members.append(('other', member))
            else:
                ch = self.consume()
                members.append(('char', ch))

            # Check for range
            if self.peek() == '-' and self.peek(1) is not None and self.peek(1) != ']':
                self.consume()  # consume '-'

                # Check if the start member is a class escape
                if members[-1][0] == 'escape':
                    # Start is a class escape like \d
                    self.error('bad_range')

                # Parse the end of range
                if self.peek() == '\\':
                    end_node = self.parse_escape(in_class=True)
                    if isinstance(end_node, CharClass):
                        # It's a char class escape
                        self.error('bad_range')
                    elif isinstance(end_node, Literal):
                        end_char = end_node.char
                    else:
                        self.error('bad_range')
                else:
                    if self.peek() is None:
                        self.error('unterminated_class')
                    end_char = self.consume()

                start_char = members[-1][1]
                if ord(start_char) > ord(end_char):
                    self.error('bad_range')

                # Replace the last member with a range
                members[-1] = ('range', (start_char, end_char))

        return CharClass(negated, members)

    def parse_escape(self, in_class=False):
        """Parse an escape sequence."""
        self.consume()  # consume '\'

        if self.peek() is None:
            self.error('trailing_backslash')

        ch = self.consume()

        if ch == 'd':
            return CharClass(False, [('escape', 'd')])
        elif ch == 'D':
            return CharClass(True, [('escape', 'd')])
        elif ch == 'w':
            return CharClass(False, [('escape', 'w')])
        elif ch == 'W':
            return CharClass(True, [('escape', 'w')])
        elif ch == 's':
            return CharClass(False, [('escape', 's')])
        elif ch == 'S':
            return CharClass(True, [('escape', 's')])
        elif ch == 'n':
            return Literal('\n')
        elif ch == 't':
            return Literal('\t')
        elif ch == 'r':
            return Literal('\r')
        elif ch == 'f':
            return Literal('\f')
        elif ch == 'v':
            return Literal('\v')
        elif ch == 'b':
            if in_class:
                return Literal('\b')
            else:
                return Anchor('word')
        elif ch == 'B':
            if in_class:
                self.error('bad_escape')
            else:
                return Anchor('non_word')
        elif ch.isalpha() or ch.isdigit():
            self.error('bad_escape')
        else:
            return Literal(ch)


class Matcher:
    def __init__(self, ast, text, group_count):
        self.ast = ast
        self.text = text
        self.group_count = group_count

    def is_word_char(self, ch):
        return ch.isalnum() or ch == '_'

    def check_anchor(self, anchor_type, pos):
        """Check if an anchor matches at position pos."""
        if anchor_type == 'start':
            return pos == 0
        elif anchor_type == 'end':
            return pos == len(self.text) or (pos == len(self.text) - 1 and self.text[-1] == '\n')
        elif anchor_type == 'word':
            left_word = pos > 0 and self.is_word_char(self.text[pos - 1])
            right_word = pos < len(self.text) and self.is_word_char(self.text[pos])
            return left_word != right_word
        elif anchor_type == 'non_word':
            left_word = pos > 0 and self.is_word_char(self.text[pos - 1])
            right_word = pos < len(self.text) and self.is_word_char(self.text[pos])
            return left_word == right_word

    def match_char_class(self, cc_node, pos):
        """Check if a character class matches at position pos."""
        if pos >= len(self.text):
            return False

        ch = self.text[pos]

        matched = False
        for member_type, value in cc_node.members:
            if member_type == 'char':
                if ch == value:
                    matched = True
                    break
            elif member_type == 'range':
                start, end = value
                if start <= ch <= end:
                    matched = True
                    break
            elif member_type == 'escape':
                # value is 'd', 'w', or 's'
                if value == 'd':
                    if ch.isdigit():
                        matched = True
                        break
                elif value == 'w':
                    if ch.isalnum() or ch == '_':
                        matched = True
                        break
                elif value == 's':
                    if ch in (' ', '\t', '\n', '\r', '\f', '\v'):
                        matched = True
                        break

        if cc_node.negated:
            return not matched and ch != '\n'
        else:
            return matched and ch != '\n'

    def match_node(self, node, pos, groups):
        """Try to match a node at position pos. Yields (new_pos, new_groups)."""
        if isinstance(node, Literal):
            if pos < len(self.text) and self.text[pos] == node.char:
                yield (pos + 1, groups)

        elif isinstance(node, CharClass):
            if self.match_char_class(node, pos):
                yield (pos + 1, groups)

        elif isinstance(node, Dot):
            if pos < len(self.text) and self.text[pos] != '\n':
                yield (pos + 1, groups)

        elif isinstance(node, Anchor):
            if self.check_anchor(node.anchor_type, pos):
                yield (pos, groups)

        elif isinstance(node, Group):
            group_num = node.group_num

            # Try to match the body
            for new_pos, new_groups in self.match_node(node.body, pos, groups):
                group_update = new_groups.copy()

                if group_num:
                    group_update[group_num] = (pos, new_pos)

                yield (new_pos, group_update)

        elif isinstance(node, Sequence):
            yield from self.match_sequence(node.items, pos, groups)

        elif isinstance(node, Alternation):
            # Try branches left to right
            for branch in node.branches:
                yield from self.match_node(branch, pos, groups)

        elif isinstance(node, Quantified):
            yield from self.match_quantified(node, pos, groups)

    def match_sequence(self, items, pos, groups):
        """Match a sequence of items."""
        if not items:
            yield (pos, groups)
            return

        first = items[0]
        rest = items[1:]

        for new_pos, new_groups in self.match_node(first, pos, groups):
            for rest_pos, rest_groups in self.match_sequence(rest, new_pos, new_groups):
                yield (rest_pos, rest_groups)

    def match_quantified(self, quant, pos, groups):
        """Match a quantified node using backtracking."""
        atom = quant.atom
        lo = quant.lo
        hi = quant.hi
        greedy = quant.greedy

        # Generate all possible matches with iteration counts
        def generate_matches(current_pos, count, current_groups):
            """Generate (end_pos, final_groups) for all possible match lengths."""
            if count < lo:
                # Must match at least one more time
                for next_pos, next_groups in self.match_node(atom, current_pos, current_groups):
                    # Guard: prevent infinite loops on zero-width matches
                    if next_pos > current_pos or count == 0:
                        yield from generate_matches(next_pos, count + 1, next_groups)
            else:
                # We've met the minimum
                # First option: stop here (no more iterations)
                yield (current_pos, current_groups)

                # Second option: try more iterations if allowed
                if hi is None or count < hi:
                    for next_pos, next_groups in self.match_node(atom, current_pos, current_groups):
                        # Guard: prevent infinite loops on zero-width matches
                        if next_pos > current_pos:
                            yield from generate_matches(next_pos, count + 1, next_groups)

        # Collect all matches
        matches = list(generate_matches(pos, 0, groups))

        if greedy:
            # Try longer matches first (higher end_pos)
            matches.sort(key=lambda x: x[0], reverse=True)
        else:
            # Try shorter matches first (lower end_pos)
            matches.sort(key=lambda x: x[0])

        for end_pos, final_groups in matches:
            yield (end_pos, final_groups)

    def search(self):
        """Search for the first match of the pattern in the text."""
        # Try each starting position
        for start_pos in range(len(self.text) + 1):
            # Try to match from this position
            for match_end, groups_dict in self.match_node(self.ast, start_pos, {}):
                # We found a match
                groups_list = []
                for group_num in range(1, self.group_count + 1):
                    if group_num in groups_dict:
                        groups_list.append(groups_dict[group_num])
                    else:
                        groups_list.append(None)

                return (start_pos, match_end, groups_list)

        return None


def search(pattern, text):
    """Search for pattern in text."""
    parser = Parser(pattern)
    try:
        ast = parser.parse()
    except PatternError:
        raise

    group_count = parser.group_count
    matcher = Matcher(ast, text, group_count)
    return matcher.search()
