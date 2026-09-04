"""
Strict binary-to-text codecs: base64, base32, and quoted-printable.
"""


class CodecError(ValueError):
    """Exception for codec errors with kind and position information."""
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(f"CodecError: kind={kind}, pos={pos}")


# Base64

def b64_encode(data, urlsafe=False, pad=True):
    """Encode bytes to base64 string."""
    if type(data) is not bytes:
        raise CodecError("type", -1)

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    if urlsafe:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

    result = []
    i = 0
    while i < len(data):
        # Read up to 3 bytes (24 bits)
        b1 = data[i]
        b2 = data[i + 1] if i + 1 < len(data) else 0
        b3 = data[i + 2] if i + 2 < len(data) else 0

        # Convert to 6-bit groups
        c1 = (b1 >> 2) & 0x3F
        c2 = ((b1 & 0x03) << 4) | ((b2 >> 4) & 0x0F)
        c3 = ((b2 & 0x0F) << 2) | ((b3 >> 6) & 0x03)
        c4 = b3 & 0x3F

        result.append(alphabet[c1])
        result.append(alphabet[c2])

        if i + 1 < len(data):
            result.append(alphabet[c3])
        if i + 2 < len(data):
            result.append(alphabet[c4])

        i += 3

    # Add padding
    if pad:
        while len(result) % 4 != 0:
            result.append('=')

    return ''.join(result)


def b64_decode(text, urlsafe=False, pad=True):
    """Decode base64 string to bytes."""
    # Check 1: type
    if type(text) is not str:
        raise CodecError("type", -1)

    # Setup alphabet
    if urlsafe:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        wrong_chars = "=+/="  # chars that are in standard but not urlsafe (use first and last two)
    else:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        wrong_chars = None

    # Check 2: Alphabet
    whitespace_chars = {' ', '\t', '\n', '\r', '\f', '\v'}
    for i, ch in enumerate(text):
        if ch != '=' and ch not in alphabet:
            if ch in whitespace_chars:
                raise CodecError("whitespace", i)
            else:
                raise CodecError("alphabet", i)

    # Check 3: Padding
    padding_start = -1
    for i in range(len(text) - 1, -1, -1):
        if text[i] != '=':
            padding_start = i + 1
            break
    if padding_start == -1:
        padding_start = 0

    if not pad:
        # No padding allowed
        for i in range(len(text)):
            if text[i] == '=':
                raise CodecError("padding", i)
    else:
        # Padding allowed only in the final run at the end
        if padding_start < len(text):
            padding_length = len(text) - padding_start
            if padding_length not in (1, 2):
                # Invalid padding run length
                raise CodecError("padding", padding_start)

        # Check if there's any '=' outside the final run
        for i in range(0, padding_start):
            if text[i] == '=':
                raise CodecError("padding", i)

    # Check 4: Length
    if pad:
        if len(text) % 4 != 0:
            raise CodecError("length", len(text))
    else:
        if len(text) % 4 == 1:
            raise CodecError("length", len(text))

    # Decode the data part
    data_chars = text.rstrip('=')

    # Check 5: Leftover bits
    # The last complete group is 4 characters
    # Remaining characters: 2, 3, or 0
    remainder = len(data_chars) % 4

    if remainder == 2:
        # The second character's low 4 bits must be 0
        if len(data_chars) > 0:
            last_char = data_chars[-1]
            if last_char in alphabet:
                val = alphabet.index(last_char)
                if (val & 0x0F) != 0:
                    raise CodecError("bits", len(data_chars) - 1)
    elif remainder == 3:
        # The third character's low 2 bits must be 0
        if len(data_chars) > 0:
            last_char = data_chars[-1]
            if last_char in alphabet:
                val = alphabet.index(last_char)
                if (val & 0x03) != 0:
                    raise CodecError("bits", len(data_chars) - 1)

    # Decode
    result = []
    for i in range(0, len(data_chars), 4):
        c1 = alphabet.index(data_chars[i]) if i < len(data_chars) else 0
        c2 = alphabet.index(data_chars[i + 1]) if i + 1 < len(data_chars) else 0
        c3 = alphabet.index(data_chars[i + 2]) if i + 2 < len(data_chars) else 0
        c4 = alphabet.index(data_chars[i + 3]) if i + 3 < len(data_chars) else 0

        b1 = ((c1 & 0x3F) << 2) | ((c2 >> 4) & 0x03)
        result.append(b1)

        if i + 2 < len(data_chars):
            b2 = ((c2 & 0x0F) << 4) | ((c3 >> 2) & 0x0F)
            result.append(b2)

        if i + 3 < len(data_chars):
            b3 = ((c3 & 0x03) << 6) | (c4 & 0x3F)
            result.append(b3)

    return bytes(result)


# Base32

def b32_encode(data, pad=True):
    """Encode bytes to base32 string."""
    if type(data) is not bytes:
        raise CodecError("type", -1)

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

    result = []
    i = 0
    while i < len(data):
        # Read up to 5 bytes (40 bits)
        b1 = data[i]
        b2 = data[i + 1] if i + 1 < len(data) else 0
        b3 = data[i + 2] if i + 2 < len(data) else 0
        b4 = data[i + 3] if i + 3 < len(data) else 0
        b5 = data[i + 4] if i + 4 < len(data) else 0

        # Convert to 5-bit groups
        c1 = (b1 >> 3) & 0x1F
        c2 = ((b1 & 0x07) << 2) | ((b2 >> 6) & 0x03)
        c3 = (b2 >> 1) & 0x1F
        c4 = ((b2 & 0x01) << 4) | ((b3 >> 4) & 0x0F)
        c5 = ((b3 & 0x0F) << 1) | ((b4 >> 7) & 0x01)
        c6 = (b4 >> 2) & 0x1F
        c7 = ((b4 & 0x03) << 3) | ((b5 >> 5) & 0x07)
        c8 = b5 & 0x1F

        # Always output c1, c2 (need at least 1 byte)
        result.append(alphabet[c1])
        result.append(alphabet[c2])

        # For remaining characters, check how many bytes we have
        remaining = len(data) - i
        if remaining >= 2:
            result.append(alphabet[c3])
            result.append(alphabet[c4])
        if remaining >= 3:
            result.append(alphabet[c5])
        if remaining >= 4:
            result.append(alphabet[c6])
            result.append(alphabet[c7])
        if remaining >= 5:
            result.append(alphabet[c8])

        i += 5

    # Add padding
    if pad:
        while len(result) % 8 != 0:
            result.append('=')

    return ''.join(result)


def b32_decode(text, pad=True):
    """Decode base32 string to bytes."""
    # Check 1: type
    if type(text) is not str:
        raise CodecError("type", -1)

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

    # Check 2: Alphabet (uppercase only)
    whitespace_chars = {' ', '\t', '\n', '\r', '\f', '\v'}
    for i, ch in enumerate(text):
        if ch != '=' and ch not in alphabet:
            if ch in whitespace_chars:
                raise CodecError("whitespace", i)
            else:
                # Lowercase or other invalid
                raise CodecError("alphabet", i)

    # Check 3: Padding
    padding_start = -1
    for i in range(len(text) - 1, -1, -1):
        if text[i] != '=':
            padding_start = i + 1
            break
    if padding_start == -1:
        padding_start = 0

    if not pad:
        # No padding allowed
        for i in range(len(text)):
            if text[i] == '=':
                raise CodecError("padding", i)
    else:
        # Padding allowed only in specific final run lengths at the end
        if padding_start < len(text):
            padding_length = len(text) - padding_start
            if padding_length not in (6, 4, 3, 1):
                # Invalid padding run length
                for i in range(padding_start, len(text)):
                    if text[i] == '=':
                        raise CodecError("padding", i)

        # Check if there's any '=' outside the final run
        for i in range(0, padding_start):
            if text[i] == '=':
                raise CodecError("padding", i)

    # Check 4: Length
    if pad:
        if len(text) % 8 != 0:
            raise CodecError("length", len(text))
    else:
        remainder = len(text) % 8
        if remainder in (1, 3, 6):
            raise CodecError("length", len(text))

    # Decode the data part
    data_chars = text.rstrip('=')

    # Check 5: Leftover bits
    # Valid incomplete group sizes: 2, 4, 5, 7
    # Corresponding zero low bits: 2, 4, 1, 3
    remainder = len(data_chars) % 8

    zero_bits_required = {
        2: 2,
        4: 4,
        5: 1,
        7: 3,
    }

    if remainder in zero_bits_required:
        if len(data_chars) > 0:
            last_char = data_chars[-1]
            if last_char in alphabet:
                val = alphabet.index(last_char)
                required_zeros = zero_bits_required[remainder]
                mask = (1 << required_zeros) - 1
                if (val & mask) != 0:
                    raise CodecError("bits", len(data_chars) - 1)

    # Decode - determine how many complete bytes we should output
    result = []

    # Map from data character count (in a group) to number of output bytes
    bytes_per_group = {
        8: 5,
        7: 4,
        5: 3,
        4: 2,
        2: 1,
    }

    for i in range(0, len(data_chars), 8):
        group_size = min(8, len(data_chars) - i)
        expected_bytes = bytes_per_group.get(group_size, 0)

        c = []
        for j in range(8):
            if i + j < len(data_chars):
                c.append(alphabet.index(data_chars[i + j]))
            else:
                c.append(0)

        # Convert 5-bit groups to bytes
        if expected_bytes >= 1:
            b1 = ((c[0] & 0x1F) << 3) | ((c[1] >> 2) & 0x07)
            result.append(b1)

        if expected_bytes >= 2:
            b2 = ((c[1] & 0x03) << 6) | ((c[2] & 0x1F) << 1) | ((c[3] >> 4) & 0x01)
            result.append(b2)

        if expected_bytes >= 3:
            b3 = ((c[3] & 0x0F) << 4) | ((c[4] >> 1) & 0x0F)
            result.append(b3)

        if expected_bytes >= 4:
            b4 = ((c[4] & 0x01) << 7) | ((c[5] & 0x1F) << 2) | ((c[6] >> 3) & 0x03)
            result.append(b4)

        if expected_bytes >= 5:
            b5 = ((c[6] & 0x07) << 5) | (c[7] & 0x1F)
            result.append(b5)

    return bytes(result)


# Quoted-printable

def qp_encode(data):
    """Encode bytes to quoted-printable string."""
    if type(data) is not bytes:
        raise CodecError("type", -1)

    lines = []
    line = ""

    for i, b in enumerate(data):
        if b == 0x20 or b == 0x09:  # space or tab
            unit = chr(b) if i != len(data) - 1 else ("=20" if b == 0x20 else "=09")
        elif 33 <= b <= 126 and b != 0x3D:  # printable, not '='
            unit = chr(b)
        else:
            unit = "=" + format(b, '02X')  # Uppercase hex

        if len(line) + len(unit) > 75:
            lines.append(line + "=")
            line = ""

        if len(unit) == 1 and (unit == " " or unit == "\t") and len(line) + 1 > 72:
            unit = "=20" if unit == " " else "=09"
            if len(line) + 3 > 75:
                lines.append(line + "=")
                line = ""

        line += unit

    lines.append(line)
    return "\r\n".join(lines)


def qp_decode(text):
    """Decode quoted-printable string to bytes."""
    # Check 1: type
    if type(text) is not str:
        raise CodecError("type", -1)

    hex_digits = "0123456789ABCDEF"

    # Helper to check if character is allowed at character level
    def is_allowed_char(ch):
        code = ord(ch)
        return (33 <= code <= 126) or code in (0x20, 0x09, 0x0D, 0x0A)

    # Check 2: Character-level scan
    i = 0
    while i < len(text):
        ch = text[i]

        # Check if character is allowed (33-126, space, tab, \r, \n)
        if not is_allowed_char(ch):
            raise CodecError("char", i)

        # Check line endings (rule 2)
        if ch == '\r':
            if i + 1 >= len(text) or text[i + 1] != '\n':
                raise CodecError("eol", i)
            i += 2
        elif ch == '\n':
            if i == 0 or text[i - 1] != '\r':
                raise CodecError("eol", i)
            i += 1
        else:
            # Check escape sequences (rules 3-5)
            if ch == '=':
                # Rule 3: Check for incomplete escape
                if i + 1 >= len(text):
                    raise CodecError("trunc", i)

                # Rule 4: Check if it's a soft line break
                if i + 1 < len(text) and text[i + 1] == '\r':
                    if i + 2 >= len(text) or text[i + 2] != '\n':
                        raise CodecError("eol", i)
                    if i + 3 >= len(text):
                        # Soft break at end with nothing after
                        raise CodecError("eol", i)
                    i += 3
                    continue

                # Rule 5: Must be followed by two hex digits
                if i + 2 >= len(text):
                    raise CodecError("trunc", i)

                h1 = text[i + 1]
                h2 = text[i + 2]

                if h1 not in hex_digits:
                    raise CodecError("hex", i + 1)
                if h2 not in hex_digits:
                    raise CodecError("hex", i + 2)

                i += 3
            else:
                i += 1

    # Check 3: Line lengths and Check 4: Trailing whitespace
    lines = text.split('\r\n')
    line_start_pos = 0

    for line_idx, line in enumerate(lines):
        # Remove soft break marker if present
        content = line
        if content.endswith('='):
            content = content[:-1]

        # Check length (rule 3)
        if len(content) > 75:
            offset = line_start_pos + 75
            raise CodecError("length", offset)

        # Check trailing whitespace (rule 4)
        if len(content) > 0:
            if content[-1] in (' ', '\t'):
                raise CodecError("trailws", line_start_pos + len(content) - 1)

        line_start_pos += len(line) + 2  # +2 for \r\n

    # Decoding: process the text
    result_bytes = []
    i = 0
    while i < len(text):
        ch = text[i]

        if ch == '=':
            if i + 1 < len(text) and text[i + 1:i + 3] == '\r\n':
                # Soft line break, skip it
                i += 3
                continue
            else:
                # Hex escape
                h1 = text[i + 1]
                h2 = text[i + 2]
                byte_val = (hex_digits.index(h1) << 4) | hex_digits.index(h2)
                result_bytes.append(byte_val)
                i += 3
        elif ch == '\r':
            # Hard line break
            if i + 1 < len(text) and text[i + 1] == '\n':
                result_bytes.append(ord('\r'))
                result_bytes.append(ord('\n'))
                i += 2
            else:
                # Should not happen if first pass succeeded
                i += 1
        elif ch == '\n':
            # Should not happen if first pass succeeded
            i += 1
        else:
            # Literal character
            result_bytes.append(ord(ch))
            i += 1

    return bytes(result_bytes)
