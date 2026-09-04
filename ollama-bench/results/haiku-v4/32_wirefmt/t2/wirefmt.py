"""
A text codec for nested string data.
"""


class WireError(ValueError):
    """Error raised during encode/decode operations."""

    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(f"WireError({kind} at {pos})")


def encode(value):
    """
    Encode a value (str or list) to its canonical wire format.

    Raises WireError if:
    - value is not str or list (kind="type", pos=0)
    - nesting depth exceeds 200 (kind="depth", pos=0)
    """
    if not isinstance(value, (str, list)):
        raise WireError("type", 0)

    _check_depth(value, 0, 200)

    return _encode_value(value)


def _check_depth(value, current_depth, max_depth):
    """Check if value exceeds max nesting depth using iterative approach."""
    # Use a stack to avoid recursion limit
    stack = [(value, current_depth)]

    while stack:
        current_value, depth = stack.pop()

        if isinstance(current_value, list):
            if depth + 1 > max_depth:
                raise WireError("depth", 0)
            # Add items to stack for checking
            for item in current_value:
                stack.append((item, depth + 1))


def _encode_value(value):
    """Encode a single value."""
    if isinstance(value, str):
        return _encode_atom(value)
    else:  # list
        items = [_encode_value(item) for item in value]
        return "(" + ",".join(items) + ")"


def _encode_atom(atom):
    """Encode an atom (string)."""
    if not atom:
        return "~"

    result = []
    for char in atom:
        code = ord(char)
        if char == "\\":
            result.append("\\\\")
        elif char == "(":
            result.append(r"\(")
        elif char == ")":
            result.append(r"\)")
        elif char == ",":
            result.append(r"\,")
        elif char == "~":
            result.append(r"\~")
        elif code < 0x20 or code == 0x7f:
            result.append(f"\\x{code:02x}")
        else:
            result.append(char)

    return "".join(result)


def decode(text):
    """
    Decode wire format text to a value (str or list).

    Parses exactly one value spanning the whole input.
    Raises WireError with various kinds on invalid input.
    """
    parser = Parser(text)
    value = parser.parse_value()

    # Check that we consumed all input
    if parser.pos < len(text):
        raise WireError("trailing", parser.pos)

    return value


class Parser:
    """Parser for wire format."""

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.depth = 0

    def parse_value(self):
        """Parse one value (list or atom)."""
        if self.pos >= len(self.text):
            raise WireError("empty", self.pos)

        if self.text[self.pos] == "(":
            return self.parse_list()
        else:
            return self.parse_atom()

    def parse_list(self):
        """Parse a list starting with '('."""
        if self.pos >= len(self.text) or self.text[self.pos] != "(":
            raise ValueError("Expected (")

        opening_pos = self.pos
        self.pos += 1
        self.depth += 1

        if self.depth > 200:
            raise WireError("depth", opening_pos)

        items = []

        # Check for empty list
        if self.pos < len(self.text) and self.text[self.pos] == ")":
            self.pos += 1
            self.depth -= 1
            return items

        # Check if we're at EOF (empty value after open paren)
        if self.pos >= len(self.text):
            raise WireError("empty", self.pos)

        # Parse items
        while self.pos < len(self.text):
            ch = self.text[self.pos]

            # Check for empty value
            if ch == ")" or ch == ",":
                raise WireError("empty", self.pos)

            # Parse the value (could be list or atom)
            if ch == "(":
                item = self.parse_list()
            else:
                item = self.parse_atom()

            items.append(item)

            # After parsing a value, we must be at a delimiter or end
            if self.pos >= len(self.text):
                raise WireError("unterminated", len(self.text))

            ch = self.text[self.pos]
            if ch == ",":
                self.pos += 1
                # After comma, check for valid next item
                if self.pos >= len(self.text):
                    raise WireError("empty", self.pos)
                if self.text[self.pos] in (")", ","):
                    raise WireError("empty", self.pos)
                # Continue to parse next item
            elif ch == ")":
                self.pos += 1
                self.depth -= 1
                return items
            else:
                # Unexpected character after value
                raise WireError("trailing", self.pos)

        # Reached end with unterminated list
        raise WireError("unterminated", len(self.text))

    def parse_atom(self):
        """Parse an atom (characters up to delimiter or end)."""
        if self.pos >= len(self.text):
            raise WireError("empty", self.pos)

        result = []
        start_pos = self.pos

        while self.pos < len(self.text):
            ch = self.text[self.pos]

            if ch == "\\":
                # Escape sequence
                if self.pos + 1 >= len(self.text):
                    raise WireError("escape", self.pos)

                next_ch = self.text[self.pos + 1]
                next_code = ord(next_ch)

                if next_ch == "x":
                    # \x followed by two hex digits
                    if self.pos + 3 >= len(self.text):
                        raise WireError("escape", self.pos)

                    hex_str = self.text[self.pos + 2:self.pos + 4]
                    if len(hex_str) != 2 or not all(c in "0123456789abcdefABCDEF" for c in hex_str):
                        raise WireError("escape", self.pos)

                    code = int(hex_str, 16)
                    result.append(chr(code))
                    self.pos += 4

                elif 0x20 <= next_code <= 0x7e:
                    # Printable ASCII (other than x)
                    result.append(next_ch)
                    self.pos += 2

                else:
                    # Control or non-ASCII after backslash
                    raise WireError("escape", self.pos)

            elif ch == "(":
                # Paren inside atom (not at start) is literal
                result.append(ch)
                self.pos += 1

            elif ch in (",", ")"):
                # End of atom
                break

            elif ch == "~":
                # Tilde only allowed as entire atom
                if result:
                    # Tilde after other characters
                    raise WireError("tilde", self.pos)
                # Tilde as first character - check if it's the entire atom
                if self.pos + 1 < len(self.text) and self.text[self.pos + 1] not in (",", ")"):
                    # Tilde followed by non-delimiter (error)
                    raise WireError("tilde", self.pos)
                # Tilde is the entire atom
                self.pos += 1
                return ""

            else:
                # Regular character
                result.append(ch)
                self.pos += 1

        if not result:
            raise WireError("empty", start_pos)

        return "".join(result)


def canon(text):
    """
    Return the canonical form of wire format text.

    Equivalent to encode(decode(text)).
    """
    value = decode(text)
    return encode(value)
