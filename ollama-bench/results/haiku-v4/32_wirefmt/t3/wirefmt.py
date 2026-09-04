class WireError(ValueError):
    """Exception for wire format errors."""
    def __init__(self, kind: str, pos: int):
        self.kind = kind
        self.pos = pos
        super().__init__(f"WireError: {kind} at {pos}")


def encode(value) -> str:
    """Encode a value (str or list) to canonical wire format."""
    # Check type and depth iteratively
    stack = [(value, 0)]  # (value, list_depth)
    max_depth = 0

    while stack:
        val, list_depth = stack.pop()

        if isinstance(val, list):
            max_depth = max(max_depth, list_depth + 1)
            if list_depth + 1 > 200:
                raise WireError("depth", 0)
            for item in val:
                stack.append((item, list_depth + 1))
        elif isinstance(val, str):
            # Strings don't affect depth
            pass
        else:
            raise WireError("type", 0)

    def encode_atom(s: str) -> str:
        if not s:
            return "~"
        result = []
        for c in s:
            if c == '\\':
                result.append('\\\\')
            elif c in '(),~':
                result.append('\\' + c)
            elif ord(c) < 0x20 or ord(c) == 0x7f:
                result.append(f'\\x{ord(c):02x}')
            else:
                result.append(c)
        return ''.join(result)

    # Encode iteratively using a work stack
    work_stack = [(value, 'encode')]
    result_stack = []

    while work_stack:
        val, state = work_stack.pop()

        if state == 'encode':
            if isinstance(val, str):
                # Encode atom directly
                result_stack.append(encode_atom(val))
            else:  # list
                if not val:
                    result_stack.append('()')
                else:
                    # Push join marker and items in reverse order
                    work_stack.append((len(val), 'join_list'))
                    for i in range(len(val) - 1, -1, -1):
                        work_stack.append((val[i], 'encode'))
        elif state == 'join_list':
            # val is the number of items to join
            num_items = val
            items = []
            for _ in range(num_items):
                items.insert(0, result_stack.pop())
            result_stack.append('(' + ','.join(items) + ')')

    return result_stack[0]


def decode(text: str):
    """Decode wire format text to a value (str or list)."""
    errors = []
    pos = [0]
    depth = [0]

    # Pre-scan for escape errors
    def pre_scan():
        i = 0
        while i < len(text):
            c = text[i]

            if c == '\\':
                if i + 1 >= len(text):
                    errors.append(("escape", i))
                elif text[i + 1] == 'x':
                    if i + 3 >= len(text):
                        errors.append(("escape", i))
                    elif not all(ch in '0123456789abcdefABCDEF' for ch in text[i+2:i+4]):
                        errors.append(("escape", i))
                    i += 4
                    continue
                elif ord(text[i + 1]) >= 0x20 and ord(text[i + 1]) <= 0x7e and text[i + 1] != 'x':
                    i += 2
                    continue
                else:
                    errors.append(("escape", i))
                i += 1
                continue

            i += 1

    pre_scan()

    def parse_atom():
        start = pos[0]
        result = []
        tilde_pos = -1

        while pos[0] < len(text):
            c = text[pos[0]]

            if c == '\\':
                next_c = text[pos[0] + 1]
                if next_c == 'x':
                    hex_chars = text[pos[0]+2:pos[0]+4]
                    try:
                        result.append(chr(int(hex_chars, 16)))
                        pos[0] += 4
                    except ValueError:
                        # Invalid hex - error already recorded in pre_scan
                        # Skip past the bad escape
                        pos[0] += 4
                else:
                    result.append(next_c)
                    pos[0] += 2
            elif c == ')' or c == ',':
                break
            elif c == '(':
                # Unescaped ( not at start - allowed as literal
                result.append(c)
                pos[0] += 1
            elif c == '~':
                tilde_pos = pos[0]
                result.append(c)
                pos[0] += 1
            else:
                result.append(c)
                pos[0] += 1

        atom = ''.join(result)

        # Check tilde rules: ~ is only legal as entire atom
        if tilde_pos >= 0:
            if atom != '~':
                # Tilde not as whole atom - error
                errors.append(("tilde", tilde_pos))
            else:
                # ~ as whole atom means empty string
                return ""

        # Check for empty atom (invalid except for ~)
        if not atom:
            errors.append(("empty", start))
            return ""

        return atom

    def parse_list():
        depth[0] += 1
        if depth[0] > 200:
            errors.append(("depth", pos[0]))
            return []

        start_paren = pos[0]
        pos[0] += 1  # consume '('

        # Check for empty list
        if pos[0] < len(text) and text[pos[0]] == ')':
            pos[0] += 1
            depth[0] -= 1
            return []

        items = []

        # Parse items
        while True:
            if pos[0] >= len(text):
                # End of input without closing ). Try to parse next value
                # This will add "empty" error if we were expecting a value
                parse_value()  # This adds errors if the value is empty
                # Then add unterminated
                errors.append(("unterminated", len(text)))
                depth[0] -= 1
                return items

            c = text[pos[0]]

            if c == ')':
                pos[0] += 1
                depth[0] -= 1
                return items
            elif c == ',':
                # Comma: should not appear here, it means empty preceding atom
                errors.append(("empty", pos[0]))
                pos[0] += 1  # skip the comma
            else:
                # Parse the next item (atom or list)
                if c == '(':
                    items.append(parse_list())
                else:
                    items.append(parse_atom())

                # After parsing an item, check for delimiter
                if pos[0] < len(text):
                    if text[pos[0]] == ',':
                        pos[0] += 1
                        # Next iteration will try to parse next value
                    elif text[pos[0]] == ')':
                        pos[0] += 1
                        depth[0] -= 1
                        return items
                # If at end of input, loop will check pos >= len at top

    def parse_value():
        if pos[0] >= len(text):
            errors.append(("empty", len(text)))
            return ""

        c = text[pos[0]]

        if c == '(':
            return parse_list()
        elif c == ')' or c == ',':
            # Trying to parse a value but found a delimiter
            errors.append(("empty", pos[0]))
            return ""
        else:
            return parse_atom()

    # Parse the value
    value = parse_value()

    # Check for trailing content at top level
    if pos[0] < len(text):
        if depth[0] == 0 and text[pos[0]] in ',)':
            errors.append(("delim", pos[0]))
        else:
            errors.append(("trailing", pos[0]))

    # Raise the first error if any
    if errors:
        precedence = {
            "escape": 0,
            "depth": 1,
            "tilde": 2,
            "empty": 3,
            "delim": 4,
            "unterminated": 5,
            "trailing": 6,
            "type": 7,
        }
        errors.sort(key=lambda x: (x[1], precedence[x[0]]))
        kind, error_pos = errors[0]
        raise WireError(kind, error_pos)

    return value


def canon(text: str) -> str:
    """Return the canonical form: encode(decode(text))."""
    return encode(decode(text))
