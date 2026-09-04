"""A backtracking regular expression engine."""


class PatternError(ValueError):
    """Exception raised for malformed regex patterns."""
    def __init__(self, kind, message=""):
        self.kind = kind
        super().__init__(message)


# Character sets for escapes
DIGIT_CHARS = set("0123456789")
WORD_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")
SPACE_CHARS = set(" \t\n\r\f\v")


def is_word_char(c):
    """Check if character is a word character."""
    return c in WORD_CHARS


class PatternParser:
    """Parse a regex pattern into an AST."""

    def __init__(self, pattern):
        self.pattern = pattern
        self.pos = 0
        self.group_count = 0

    def error(self, kind):
        raise PatternError(kind)

    def peek(self):
        """Look at current character without consuming."""
        if self.pos < len(self.pattern):
            return self.pattern[self.pos]
        return None

    def consume(self):
        """Consume and return current character."""
        if self.pos < len(self.pattern):
            c = self.pattern[self.pos]
            self.pos += 1
            return c
        return None

    def parse(self):
        """Parse the entire pattern."""
        branches = self.parse_branches(allow_paren=False)
        if self.pos < len(self.pattern):
            self.error("unbalanced_paren")
        return branches

    def parse_branches(self, allow_paren=True):
        """Parse branches separated by |."""
        branches = []
        branch = self.parse_sequence()
        branches.append(branch)

        while self.peek() == "|":
            self.consume()  # consume |
            branch = self.parse_sequence()
            branches.append(branch)

        if allow_paren and self.peek() == ")":
            # This is normal, will be consumed by caller
            pass
        elif not allow_paren and self.peek() is not None:
            if self.peek() != ")":
                pass  # Will check at top level

        if len(branches) == 1:
            return branches[0]
        else:
            return ("alternation", branches)

    def parse_sequence(self):
        """Parse a sequence of quantified atoms."""
        items = []

        while True:
            if self.peek() is None:
                break
            if self.peek() in "|)":
                break

            item = self.parse_atom()
            item = self.parse_quantifier(item)
            items.append(item)

        if len(items) == 0:
            return ("empty",)
        elif len(items) == 1:
            return items[0]
        else:
            return ("sequence", items)

    def parse_atom(self):
        """Parse an atom."""
        c = self.peek()

        if c is None:
            return ("empty",)
        elif c == "(":
            self.consume()
            if self.peek() == "?":
                self.consume()
                if self.peek() == ":":
                    self.consume()
                    body = self.parse_branches(allow_paren=True)
                    if self.peek() != ")":
                        self.error("unbalanced_paren")
                    self.consume()
                    return ("non_group", body)
                else:
                    self.error("bad_group")
            else:
                self.group_count += 1
                group_num = self.group_count
                body = self.parse_branches(allow_paren=True)
                if self.peek() != ")":
                    self.error("unbalanced_paren")
                self.consume()
                return ("group", group_num, body)
        elif c == "[":
            return self.parse_char_class()
        elif c == ".":
            self.consume()
            return ("dot",)
        elif c == "^":
            self.consume()
            return ("anchor", "^")
        elif c == "$":
            self.consume()
            return ("anchor", "$")
        elif c == "\\":
            return self.parse_escape()
        elif c in "*+?|)":
            # These should not be consumed as literals - they're quantifiers or special
            return ("empty",)
        else:
            self.consume()
            return ("lit", c)

    def parse_escape(self):
        """Parse an escape sequence outside a character class."""
        self.consume()  # consume backslash

        c = self.peek()
        if c is None:
            self.error("trailing_backslash")

        self.consume()

        # Special escape sequences
        if c == "d":
            return ("class", DIGIT_CHARS, False)
        elif c == "D":
            return ("class", DIGIT_CHARS, True)
        elif c == "w":
            return ("class", WORD_CHARS, False)
        elif c == "W":
            return ("class", WORD_CHARS, True)
        elif c == "s":
            return ("class", SPACE_CHARS, False)
        elif c == "S":
            return ("class", SPACE_CHARS, True)
        elif c == "n":
            return ("lit", "\n")
        elif c == "t":
            return ("lit", "\t")
        elif c == "r":
            return ("lit", "\r")
        elif c == "f":
            return ("lit", "\f")
        elif c == "v":
            return ("lit", "\v")
        elif c == "b":
            return ("anchor", "\\b")
        elif c == "B":
            return ("anchor", "\\B")
        elif c.isalpha() or c.isdigit():
            self.error("bad_escape")
        else:
            # Literal escape
            return ("lit", c)

    def parse_char_class(self):
        """Parse a character class [...]."""
        self.consume()  # consume [

        negated = False
        if self.peek() == "^":
            self.consume()
            negated = True

        members = []

        # Special case: ] as first member
        if self.peek() == "]":
            self.consume()
            members.append("]")

        while True:
            c = self.peek()
            if c is None:
                self.error("unterminated_class")
            if c == "]":
                self.consume()
                break

            # Parse a member
            if c == "\\":
                self.consume()
                next_c = self.peek()
                if next_c is None:
                    self.error("trailing_backslash")
                self.consume()

                if next_c == "n":
                    members.append("\n")
                elif next_c == "t":
                    members.append("\t")
                elif next_c == "r":
                    members.append("\r")
                elif next_c == "f":
                    members.append("\f")
                elif next_c == "v":
                    members.append("\v")
                elif next_c == "b":
                    members.append("\b")  # backspace in class
                elif next_c == "B":
                    self.error("bad_escape")
                elif next_c == "d":
                    members.append(("class_esc", "d"))
                elif next_c == "D":
                    members.append(("class_esc", "D"))
                elif next_c == "w":
                    members.append(("class_esc", "w"))
                elif next_c == "W":
                    members.append(("class_esc", "W"))
                elif next_c == "s":
                    members.append(("class_esc", "s"))
                elif next_c == "S":
                    members.append(("class_esc", "S"))
                elif next_c.isalpha() or next_c.isdigit():
                    self.error("bad_escape")
                else:
                    members.append(next_c)
            else:
                self.consume()
                members.append(c)

            # Check for range
            if self.peek() == "-" and self.pos + 1 < len(self.pattern) and self.pattern[self.pos + 1] != "]":
                self.consume()  # consume -

                # Parse range end
                c2 = self.peek()
                if c2 is None:
                    self.error("unterminated_class")

                if c2 == "\\":
                    self.consume()
                    next_c = self.peek()
                    if next_c is None:
                        self.error("trailing_backslash")
                    self.consume()

                    if next_c in "dDwWsS":
                        self.error("bad_range")
                    else:
                        # Literal escape
                        c2_val = next_c
                else:
                    self.consume()
                    c2_val = c2

                # Check for class escapes in range
                if isinstance(members[-1], tuple) and members[-1][0] == "class_esc":
                    self.error("bad_range")

                # Check if c2_val is class escape
                if c2_val in "dDwWsS":
                    self.error("bad_range")

                # Check reversed range
                c1_val = members[-1]
                if ord(c1_val) > ord(c2_val):
                    self.error("bad_range")

                # Replace last member with range
                members[-1] = ("range", c1_val, c2_val)

        return ("char_class", members, negated)

    def parse_quantifier(self, atom):
        """Parse quantifier after an atom."""
        # Check if atom is an anchor
        if atom[0] == "anchor":
            pass  # Will check after quantifier is parsed

        c = self.peek()

        # Rule 7: Check for quantifier without preceding atom
        if atom == ("empty",) and c is not None and c in "*+?":
            self.error("nothing_to_repeat")

        if atom == ("empty",) and c == "{":
            # Look ahead to see if it's a valid quantifier
            saved_pos = self.pos
            self.consume()

            # Read digits
            digits = ""
            while self.peek() and self.peek().isdigit():
                digits += self.consume()

            if self.peek() == "}":
                # This is a valid quantifier
                self.pos = saved_pos
                self.error("nothing_to_repeat")
            elif self.peek() == ",":
                # Could be valid quantifier
                self.consume()
                digits2 = ""
                while self.peek() and self.peek().isdigit():
                    digits2 += self.consume()
                if self.peek() == "}":
                    # This is a valid quantifier
                    self.pos = saved_pos
                    self.error("nothing_to_repeat")
                else:
                    # Not a valid quantifier
                    self.pos = saved_pos
            else:
                # Not a valid quantifier
                self.pos = saved_pos

        if c is not None and c == "*":
            self.consume()
            greedy = True
            if self.peek() == "?":
                self.consume()
                greedy = False

            # Check bad_repeat is not applicable here (always 0..inf)
            # Check anchor
            if atom[0] == "anchor":
                self.error("anchor_repeat")

            # Check for multiple repeat
            next_c = self.peek()
            if next_c is not None and next_c in "*+?":
                self.error("multiple_repeat")
            if next_c == "{":
                if self.is_valid_quantifier():
                    self.error("multiple_repeat")

            return ("quantifier", atom, 0, float("inf"), greedy)

        elif c is not None and c == "+":
            self.consume()
            greedy = True
            if self.peek() == "?":
                self.consume()
                greedy = False

            # Check bad_repeat is not applicable here (always 1..inf)
            # Check anchor
            if atom[0] == "anchor":
                self.error("anchor_repeat")

            # Check for multiple repeat
            next_c = self.peek()
            if next_c is not None and next_c in "*+?":
                self.error("multiple_repeat")
            if next_c == "{":
                if self.is_valid_quantifier():
                    self.error("multiple_repeat")

            return ("quantifier", atom, 1, float("inf"), greedy)

        elif c is not None and c == "?":
            self.consume()
            greedy = True
            if self.peek() == "?":
                self.consume()
                greedy = False

            # Check bad_repeat is not applicable here (always 0..1)
            # Check anchor
            if atom[0] == "anchor":
                self.error("anchor_repeat")

            # Check for multiple repeat
            next_c = self.peek()
            if next_c is not None and next_c in "*+?":
                self.error("multiple_repeat")
            if next_c == "{":
                if self.is_valid_quantifier():
                    self.error("multiple_repeat")

            return ("quantifier", atom, 0, 1, greedy)

        elif c is not None and c == "{":
            saved_pos = self.pos
            self.consume()

            # Read LO
            lo_str = ""
            while self.peek() and self.peek().isdigit():
                lo_str += self.consume()

            if self.peek() == "}":
                if lo_str:
                    self.consume()
                    lo = int(lo_str)
                    hi = lo
                    greedy = True
                    if self.peek() == "?":
                        self.consume()
                        greedy = False

                    # Check bad_repeat (lo > hi) first
                    if lo > hi:
                        self.error("bad_repeat")

                    # Check anchor
                    if atom[0] == "anchor":
                        self.error("anchor_repeat")

                    # Check for multiple repeat
                    next_c = self.peek()
                    if next_c is not None and next_c in "*+?":
                        self.error("multiple_repeat")
                    if next_c == "{":
                        if self.is_valid_quantifier():
                            self.error("multiple_repeat")

                    return ("quantifier", atom, lo, hi, greedy)
                else:
                    # {}, not a quantifier
                    self.pos = saved_pos
                    return atom

            elif self.peek() == ",":
                self.consume()
                hi_str = ""
                while self.peek() and self.peek().isdigit():
                    hi_str += self.consume()

                if self.peek() == "}":
                    self.consume()
                    lo = int(lo_str) if lo_str else 0
                    hi = int(hi_str) if hi_str else float("inf")
                    greedy = True
                    if self.peek() == "?":
                        self.consume()
                        greedy = False

                    # Check bad_repeat (lo > hi) first
                    if lo > hi and hi != float("inf"):
                        self.error("bad_repeat")

                    # Check anchor
                    if atom[0] == "anchor":
                        self.error("anchor_repeat")

                    # Check for multiple repeat
                    next_c = self.peek()
                    if next_c is not None and next_c in "*+?":
                        self.error("multiple_repeat")
                    if next_c == "{":
                        if self.is_valid_quantifier():
                            self.error("multiple_repeat")

                    return ("quantifier", atom, lo, hi, greedy)
                else:
                    # Not a valid quantifier
                    self.pos = saved_pos
                    return atom
            else:
                # Not a valid quantifier
                self.pos = saved_pos
                return atom

        return atom

    def is_valid_quantifier(self):
        """Check if next character starts a valid quantifier."""
        c = self.peek()
        if c is None or c not in "*+?{":
            return False
        if c is not None and c in "*+?":
            return True
        if c == "{":
            saved_pos = self.pos
            self.consume()

            lo_str = ""
            while self.peek() and self.peek().isdigit():
                lo_str += self.consume()

            is_valid = False
            if self.peek() == "}" and lo_str:
                is_valid = True
            elif self.peek() == ",":
                is_valid = True

            self.pos = saved_pos
            return is_valid

        return False


class Matcher:
    """Match a parsed pattern against text using backtracking."""

    def __init__(self, pattern_ast, text, group_count):
        self.pattern = pattern_ast
        self.text = text
        self.group_count = group_count

    def search(self):
        """Search for pattern in text."""
        for start_pos in range(len(self.text) + 1):
            for end_pos, groups in self.match_at(self.pattern, start_pos, {}):
                # Collect groups in order
                groups_list = [None] * self.group_count
                for group_num in range(1, self.group_count + 1):
                    if group_num in groups:
                        groups_list[group_num - 1] = groups[group_num]

                return (start_pos, end_pos, groups_list)

        return None

    def match_at(self, ast, pos, groups):
        """
        Match ast starting at pos, yielding all possible (end_pos, groups) pairs in order.
        """
        if ast == ("empty",):
            yield (pos, groups)
            return

        if ast[0] == "lit":
            c = ast[1]
            if pos < len(self.text) and self.text[pos] == c:
                yield (pos + 1, groups)
            return

        if ast[0] == "dot":
            if pos < len(self.text) and self.text[pos] != "\n":
                yield (pos + 1, groups)
            return

        if ast[0] == "anchor":
            anchor_type = ast[1]
            if anchor_type == "^":
                if pos == 0:
                    yield (pos, groups)
            elif anchor_type == "$":
                if pos == len(self.text) or (pos == len(self.text) - 1 and self.text[pos] == "\n"):
                    yield (pos, groups)
            elif anchor_type == "\\b":
                # Word boundary
                left_is_word = pos > 0 and is_word_char(self.text[pos - 1])
                right_is_word = pos < len(self.text) and is_word_char(self.text[pos])
                if left_is_word != right_is_word:
                    yield (pos, groups)
            elif anchor_type == "\\B":
                # Non-word boundary
                left_is_word = pos > 0 and is_word_char(self.text[pos - 1])
                right_is_word = pos < len(self.text) and is_word_char(self.text[pos])
                if left_is_word == right_is_word:
                    yield (pos, groups)
            return

        if ast[0] == "class":
            char_set, negated = ast[1], ast[2]
            if pos >= len(self.text):
                return
            c = self.text[pos]
            is_in = c in char_set
            if negated:
                is_in = not is_in
            if is_in:
                yield (pos + 1, groups)
            return

        if ast[0] == "char_class":
            members, negated = ast[1], ast[2]
            if pos >= len(self.text):
                return
            c = self.text[pos]
            is_in = self.char_in_class(c, members)
            if negated:
                is_in = not is_in
            if is_in:
                yield (pos + 1, groups)
            return

        if ast[0] == "sequence":
            items = ast[1]
            yield from self.match_sequence(items, pos, groups)
            return

        if ast[0] == "alternation":
            branches = ast[1]
            for branch in branches:
                yield from self.match_at(branch, pos, groups)
            return

        if ast[0] == "group":
            group_num = ast[1]
            body = ast[2]
            for end_pos, new_groups in self.match_at(body, pos, groups):
                new_groups = dict(new_groups)
                new_groups[group_num] = (pos, end_pos)
                yield (end_pos, new_groups)
            return

        if ast[0] == "non_group":
            body = ast[1]
            yield from self.match_at(body, pos, groups)
            return

        if ast[0] == "quantifier":
            body = ast[1]
            lo = ast[2]
            hi = ast[3]
            greedy = ast[4]

            yield from self.match_quantified(body, lo, hi, greedy, pos, groups)
            return

    def match_sequence(self, items, pos, groups):
        """Match a sequence of items."""
        if not items:
            yield (pos, groups)
            return

        first = items[0]
        rest = items[1:]

        for next_pos, next_groups in self.match_at(first, pos, groups):
            for final_pos, final_groups in self.match_sequence(rest, next_pos, next_groups):
                yield (final_pos, final_groups)

    def match_quantified(self, body, lo, hi, greedy, pos, groups):
        """Match a quantified body with proper backtracking."""
        # Use a recursive helper that tries different numbers of iterations
        yield from self._quantified_helper(body, lo, hi, greedy, 0, pos, groups)

    def _quantified_helper(self, body, lo, hi, greedy, iterations, pos, groups):
        """Helper for match_quantified that handles backtracking within iterations."""
        if iterations < lo:
            # Mandatory iteration
            for end_pos, new_groups in self.match_at(body, pos, groups):
                yield from self._quantified_helper(body, lo, hi, greedy, iterations + 1, end_pos, new_groups)
        elif iterations >= hi:
            # Reached maximum iterations
            yield (pos, groups)
        else:
            # Optional iteration - try based on greedy/non-greedy
            optional_matches = list(self.match_at(body, pos, groups))

            if greedy:
                # Greedy: try optional iterations first
                if optional_matches:
                    for end_pos, new_groups in optional_matches:
                        # Check if we consumed characters
                        if end_pos == pos and iterations > 0:
                            # Empty match on non-first iteration after previous non-empty
                            # Don't try further iterations
                            break
                        # Try more iterations
                        yield from self._quantified_helper(body, lo, hi, greedy, iterations + 1, end_pos, new_groups)

                # Then try without additional iteration
                yield (pos, groups)
            else:
                # Non-greedy: try without additional iteration first
                yield (pos, groups)

                # Then try optional iterations if they exist
                if optional_matches:
                    for end_pos, new_groups in optional_matches:
                        # Check if we consumed characters
                        if end_pos == pos and iterations > 0:
                            # Empty match on non-first iteration - don't continue
                            break
                        # Try more iterations
                        yield from self._quantified_helper(body, lo, hi, greedy, iterations + 1, end_pos, new_groups)

    def char_in_class(self, c, members):
        """Check if character is in class."""
        for member in members:
            if isinstance(member, str):
                if c == member:
                    return True
            elif isinstance(member, tuple):
                if member[0] == "class_esc":
                    esc_type = member[1]
                    if esc_type == "d" and c in DIGIT_CHARS:
                        return True
                    elif esc_type == "D" and c not in DIGIT_CHARS:
                        return True
                    elif esc_type == "w" and c in WORD_CHARS:
                        return True
                    elif esc_type == "W" and c not in WORD_CHARS:
                        return True
                    elif esc_type == "s" and c in SPACE_CHARS:
                        return True
                    elif esc_type == "S" and c not in SPACE_CHARS:
                        return True
                elif member[0] == "range":
                    c1, c2 = member[1], member[2]
                    if c1 <= c <= c2:
                        return True
        return False


def search(pattern, text):
    """Search for pattern in text."""
    parser = PatternParser(pattern)
    ast = parser.parse()
    group_count = parser.group_count

    matcher = Matcher(ast, text, group_count)
    return matcher.search()
