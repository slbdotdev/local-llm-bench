class WireError(ValueError):
    """Exception for wire format errors."""
    def __init__(self, kind, pos, message=None):
        self.kind = kind
        self.pos = pos
        if message is None:
            message = f"{kind} at {pos}"
        super().__init__(message)


def encode(value):
    """Encode a value (str or list) to canonical wire format."""
    # Check type and depth first
    _check_type_and_depth(value, 0)
    return _encode_value(value)


def _check_type_and_depth(value, depth):
    """Check that value is str or list, and depth <= 200."""
    if not isinstance(value, (str, list)):
        raise WireError("type", 0)
    if isinstance(value, list):
        if depth >= 200:
            raise WireError("depth", 0)
        for item in value:
            _check_type_and_depth(item, depth + 1)


def _encode_value(value):
    """Recursively encode a value."""
    if isinstance(value, list):
        items = [_encode_value(item) for item in value]
        return "(" + ",".join(items) + ")"
    else:  # str
        if value == "":
            return "~"

        result = []
        for char in value:
            if char == "\\":
                result.append("\\\\")
            elif char == "(":
                result.append("\\(")
            elif char == ")":
                result.append("\\)")
            elif char == ",":
                result.append("\\,")
            elif char == "~":
                result.append("\\~")
            elif ord(char) < 0x20 or ord(char) == 0x7f:
                result.append(f"\\x{ord(char):02x}")
            else:
                result.append(char)
        return "".join(result)


def decode(text):
    """Decode wire format text to a value (str or list)."""
    parser = Parser(text)
    return parser.parse_top_level()


class Parser:
    """Parser for wire format."""

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.depth = 0
        self.errors = []  # List of (kind, pos) tuples

    def parse_top_level(self):
        """Parse a single value at top level."""
        value = self._parse_value()

        # Check for trailing content
        if self.pos < len(self.text):
            if self.text[self.pos] in ",)":
                self.errors.append(("delim", self.pos))
            else:
                self.errors.append(("trailing", self.pos))

        if self.errors:
            self._raise_best_error()

        return value

    def _parse_value(self):
        """Parse a value (list or atom) at current position."""
        if self.pos >= len(self.text):
            self.errors.append(("empty", self.pos))
            return None

        if self.text[self.pos] == "(":
            return self._parse_list()
        else:
            return self._parse_atom()

    def _parse_list(self):
        """Parse a list: ( item1 , item2 , ... )."""
        self.depth += 1
        if self.depth > 200:
            self.errors.append(("depth", self.pos))
            self.depth -= 1
            return None

        start_pos = self.pos
        self.pos += 1  # consume '('

        # Empty list case
        if self.pos < len(self.text) and self.text[self.pos] == ")":
            self.pos += 1
            self.depth -= 1
            return []

        # Non-empty list
        items = []
        while True:
            if self.pos >= len(self.text):
                # We need a value here but reached end of input
                self.errors.append(("empty", self.pos))
                self.errors.append(("unterminated", self.pos))
                self.depth -= 1
                return None

            ch = self.text[self.pos]

            # Check for invalid start of value
            if ch == ")":
                self.errors.append(("empty", self.pos))
                self.pos += 1
                self.depth -= 1
                return None

            if ch == ",":
                self.errors.append(("empty", self.pos))
                self.pos += 1
                self.depth -= 1
                return None

            # Parse a value (can be a list or an atom)
            value = self._parse_value()
            if value is None:
                self.depth -= 1
                return None
            items.append(value)

            # Expect comma or closing paren
            if self.pos >= len(self.text):
                self.errors.append(("unterminated", self.pos))
                self.depth -= 1
                return None

            ch = self.text[self.pos]
            if ch == ",":
                self.pos += 1
                # After comma, check for valid next position
                if self.pos >= len(self.text):
                    self.errors.append(("empty", self.pos))
                    self.depth -= 1
                    return None
                # If next is ) or comma, that's an empty atom error (handled in next iteration)
            elif ch == ")":
                self.pos += 1
                self.depth -= 1
                return items
            else:
                self.errors.append(("trailing", self.pos))
                self.depth -= 1
                return None

    def _parse_atom(self):
        """Parse an atom (string value)."""
        start_pos = self.pos
        chars = []

        while self.pos < len(self.text):
            ch = self.text[self.pos]

            # Stop at delimiters
            if ch == "," or ch == ")":
                break

            if ch == "\\":
                # Escape sequence
                escape_pos = self.pos
                if self.pos + 1 >= len(self.text):
                    self.errors.append(("escape", escape_pos))
                    return None

                next_ch = self.text[self.pos + 1]

                if next_ch == "x":
                    # Hex escape: \xHH
                    if self.pos + 3 >= len(self.text):
                        self.errors.append(("escape", escape_pos))
                        return None
                    hex_part = self.text[self.pos + 2:self.pos + 4]
                    if not (len(hex_part) == 2 and all(c in "0123456789abcdefABCDEF" for c in hex_part)):
                        self.errors.append(("escape", escape_pos))
                        return None
                    codepoint = int(hex_part, 16)
                    chars.append(chr(codepoint))
                    self.pos += 4
                elif 0x20 <= ord(next_ch) <= 0x7e and next_ch != "x":
                    # Printable ASCII character escape
                    chars.append(next_ch)
                    self.pos += 2
                else:
                    # Invalid escape: control char or non-ASCII after backslash
                    self.errors.append(("escape", escape_pos))
                    return None

            elif ch == "~":
                # Tilde: valid only if entire atom is just ~
                if len(chars) == 0:
                    # Check if this is the end of the atom
                    if self.pos + 1 >= len(self.text) or self.text[self.pos + 1] in ",)":
                        self.pos += 1
                        return ""
                    else:
                        # Tilde followed by more content
                        self.errors.append(("tilde", self.pos))
                        return None
                else:
                    # Tilde not at start
                    self.errors.append(("tilde", self.pos))
                    return None

            elif ch == "(":
                # Opening paren inside atom is a literal character
                chars.append(ch)
                self.pos += 1

            else:
                # Regular character
                chars.append(ch)
                self.pos += 1

        # End of atom
        if len(chars) == 0:
            self.errors.append(("empty", start_pos))
            return None

        return "".join(chars)

    def _raise_best_error(self):
        """Raise the error with smallest pos and highest precedence."""
        precedence = {
            "escape": 0,
            "depth": 1,
            "tilde": 2,
            "empty": 3,
            "delim": 4,
            "unterminated": 5,
            "trailing": 6,
            "type": 7
        }

        best_error = min(self.errors, key=lambda e: (e[1], precedence[e[0]]))
        raise WireError(best_error[0], best_error[1])


def canon(text):
    """Return the canonical form: encode(decode(text))."""
    return encode(decode(text))
