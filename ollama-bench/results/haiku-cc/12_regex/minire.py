"""
A small regular expression engine implemented from scratch.
"""


def fullmatch(pattern: str, text: str) -> bool:
    r"""
    Match a regex pattern against text.
    The entire text must match (anchored at both ends).

    Supported syntax:
    - Literal characters
    - . matches any single character
    - Escapes: \x matches x literally
    - Character classes: [abc], [a-z], [^abc]
    - Quantifiers: *, +, ?
    - Grouping: (...)
    - Alternation: |

    Raises ValueError for malformed patterns.
    """
    try:
        regex = parse(pattern)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid pattern: {e}")

    # Match from position 0 and check if we can reach the end
    possible_ends = regex.match(text, 0)
    return len(text) in possible_ends


# === AST Classes ===

class Regex:
    """Base class for regex AST nodes."""

    def match(self, text, pos):
        """
        Returns a set of possible ending positions after matching.
        An empty set means no match.
        """
        raise NotImplementedError


class Literal(Regex):
    """Matches a single literal character."""

    def __init__(self, char):
        self.char = char

    def match(self, text, pos):
        if pos < len(text) and text[pos] == self.char:
            return {pos + 1}
        return set()


class Dot(Regex):
    """Matches any single character."""

    def match(self, text, pos):
        if pos < len(text):
            return {pos + 1}
        return set()


class CharClass(Regex):
    """Matches a character class like [abc] or [a-z]."""

    def __init__(self, chars, negated=False):
        self.chars = chars  # set of characters
        self.negated = negated

    def match(self, text, pos):
        if pos >= len(text):
            return set()

        char = text[pos]
        in_class = char in self.chars

        if self.negated:
            in_class = not in_class

        if in_class:
            return {pos + 1}
        return set()


class Alternation(Regex):
    """Matches left | right."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def match(self, text, pos):
        return self.left.match(text, pos) | self.right.match(text, pos)


class Concatenation(Regex):
    """Matches a sequence of regexes."""

    def __init__(self, regexes):
        self.regexes = regexes

    def match(self, text, pos):
        if not self.regexes:
            return {pos}

        current_positions = {pos}
        for regex in self.regexes:
            next_positions = set()
            for p in current_positions:
                next_positions |= regex.match(text, p)
            current_positions = next_positions
            if not current_positions:
                break

        return current_positions


class Quantifier(Regex):
    """Matches a regex 0 to max_count times (at least min_count times)."""

    def __init__(self, regex, min_count, max_count):
        self.regex = regex
        self.min_count = min_count
        self.max_count = max_count

    def match(self, text, pos):
        result_positions = set()
        current_positions = {pos}
        count = 0

        # Try matching 0 to max_count times (greedy)
        while count <= self.max_count:
            # If we've matched enough times, add this position to results
            if count >= self.min_count:
                result_positions |= current_positions

            # Stop if we've reached max_count
            if count == self.max_count:
                break

            # Try to match one more time
            next_positions = set()
            for p in current_positions:
                next_positions |= self.regex.match(text, p)

            # If no progress, stop
            if not next_positions:
                break

            current_positions = next_positions
            count += 1

        return result_positions


# === Parser ===

def parse(pattern: str):
    """Parse a regex pattern into an AST."""
    parser = Parser(pattern)
    regex = parser.parse_alternation()
    if parser.pos != len(pattern):
        raise ValueError(f"Unexpected character at position {parser.pos}")
    return regex


class Parser:
    """Recursive descent parser for regex patterns."""

    def __init__(self, pattern):
        self.pattern = pattern
        self.pos = 0

    def parse_alternation(self):
        """Parse alternation (lowest precedence): expr | expr | ..."""
        left = self.parse_concatenation()

        if self.pos < len(self.pattern) and self.pattern[self.pos] == '|':
            self.pos += 1
            right = self.parse_alternation()
            return Alternation(left, right)

        return left

    def parse_concatenation(self):
        """Parse concatenation: expr expr expr ..."""
        regexes = []

        # Stop at end, |, or )
        while self.pos < len(self.pattern) and self.pattern[self.pos] not in '|)':
            regexes.append(self.parse_quantifier())

        if not regexes:
            return Concatenation([])

        return Concatenation(regexes)

    def parse_quantifier(self):
        """Parse quantifiers: atom, atom*, atom+, atom?"""
        atom = self.parse_atom()

        if self.pos < len(self.pattern):
            ch = self.pattern[self.pos]
            if ch == '*':
                self.pos += 1
                return Quantifier(atom, 0, float('inf'))
            elif ch == '+':
                self.pos += 1
                return Quantifier(atom, 1, float('inf'))
            elif ch == '?':
                self.pos += 1
                return Quantifier(atom, 0, 1)

        return atom

    def parse_atom(self):
        """Parse an atom: literal, ., [class], or (group)."""
        if self.pos >= len(self.pattern):
            raise ValueError("Unexpected end of pattern")

        ch = self.pattern[self.pos]

        if ch == '\\':
            # Escape sequence
            self.pos += 1
            if self.pos >= len(self.pattern):
                raise ValueError("Trailing backslash")
            escaped_ch = self.pattern[self.pos]
            self.pos += 1
            return Literal(escaped_ch)

        elif ch == '.':
            # Dot matches any character
            self.pos += 1
            return Dot()

        elif ch == '[':
            # Character class
            return self.parse_char_class()

        elif ch == '(':
            # Grouped expression
            self.pos += 1
            regex = self.parse_alternation()
            if self.pos >= len(self.pattern) or self.pattern[self.pos] != ')':
                raise ValueError("Unbalanced parentheses")
            self.pos += 1
            return regex

        elif ch in '*+?)':
            raise ValueError(f"Quantifier '{ch}' has nothing to repeat")

        else:
            # Literal character
            self.pos += 1
            return Literal(ch)

    def parse_char_class(self):
        """Parse a character class: [abc], [a-z], [^abc]."""
        self.pos += 1  # consume '['

        if self.pos >= len(self.pattern):
            raise ValueError("Unterminated character class")

        negated = False
        if self.pattern[self.pos] == '^':
            negated = True
            self.pos += 1

        chars = []

        while self.pos < len(self.pattern):
            ch = self.pattern[self.pos]

            # Check for end of class
            if ch == ']' and chars:
                self.pos += 1
                return CharClass(set(chars), negated)

            if ch == '\\':
                # Escaped character
                self.pos += 1
                if self.pos >= len(self.pattern):
                    raise ValueError("Unterminated character class")
                chars.append(self.pattern[self.pos])
                self.pos += 1

            elif ch == '-':
                # Check if this is a range or a literal hyphen
                if chars and self.pos + 1 < len(self.pattern) and self.pattern[self.pos + 1] != ']':
                    # This is a range
                    prev_char = chars.pop()
                    self.pos += 1  # consume '-'

                    # Get the end character
                    if self.pos < len(self.pattern) and self.pattern[self.pos] == '\\':
                        self.pos += 1
                        if self.pos >= len(self.pattern):
                            raise ValueError("Unterminated character class")
                        end_char = self.pattern[self.pos]
                        self.pos += 1
                    else:
                        end_char = self.pattern[self.pos]
                        self.pos += 1

                    # Add all characters in the range
                    for code in range(ord(prev_char), ord(end_char) + 1):
                        chars.append(chr(code))
                else:
                    # Literal hyphen
                    chars.append('-')
                    self.pos += 1

            else:
                # Regular character
                chars.append(ch)
                self.pos += 1

        raise ValueError("Unterminated character class")
