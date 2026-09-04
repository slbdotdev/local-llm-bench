"""Strict binary-to-text codecs: base64, base32, and quoted-printable."""


class CodecError(ValueError):
    """Exception for codec errors with kind and position information."""
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(f"CodecError: {kind} at {pos}")


# Base64 codec

B64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
B64_URLSAFE_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def b64_encode(data, urlsafe=False, pad=True):
    """Encode bytes to base64 string."""
    if type(data) is not bytes:
        raise CodecError("type", -1)

    alphabet = B64_URLSAFE_ALPHABET if urlsafe else B64_ALPHABET
    result = []

    # Process 3 bytes at a time
    for i in range(0, len(data), 3):
        chunk = data[i:i+3]

        # Convert chunk to 24-bit integer (or less for final chunk)
        value = 0
        for byte in chunk:
            value = (value << 8) | byte

        # Shift left to align with 6-bit groups
        bits_to_shift = 24 - (len(chunk) * 8)
        value <<= bits_to_shift

        # Extract 6-bit groups
        for j in range(4 - bits_to_shift // 6):
            if j < len(chunk) + 1 or bits_to_shift == 0:
                six_bits = (value >> (18 - j * 6)) & 0x3F
                result.append(alphabet[six_bits])

    # Add padding if needed
    if pad:
        padding_needed = (4 - len(result) % 4) % 4
        result.extend(['='] * padding_needed)

    return ''.join(result)


def b64_decode(text, urlsafe=False, pad=True):
    """Decode base64 string to bytes."""
    # 1. Type check
    if type(text) is not str:
        raise CodecError("type", -1)

    alphabet = B64_URLSAFE_ALPHABET if urlsafe else B64_ALPHABET
    other_alphabet = B64_ALPHABET if urlsafe else B64_URLSAFE_ALPHABET
    whitespace_chars = {' ', '\t', '\n', '\r', '\f', '\v'}

    # 2. Alphabet check
    for i, char in enumerate(text):
        if char not in alphabet and char != '=':
            if char in whitespace_chars:
                raise CodecError("whitespace", i)
            elif char in other_alphabet:
                raise CodecError("alphabet", i)
            else:
                raise CodecError("alphabet", i)

    # 3. Padding check
    if pad:
        # Find the final run of '='
        if text:
            # Count trailing '='
            trailing_eq_count = 0
            for i in range(len(text) - 1, -1, -1):
                if text[i] == '=':
                    trailing_eq_count += 1
                else:
                    break

            # Valid padding lengths are 0, 1, or 2
            if trailing_eq_count > 2:
                raise CodecError("padding", len(text) - trailing_eq_count)

            # Check for '=' before the final run
            if trailing_eq_count > 0:
                for i in range(len(text) - trailing_eq_count - 1):
                    if text[i] == '=':
                        raise CodecError("padding", i)
    else:
        # pad=False: no '=' allowed anywhere
        if '=' in text:
            raise CodecError("padding", text.index('='))

    # 4. Length check
    if pad:
        if len(text) % 4 != 0:
            raise CodecError("length", len(text))
    else:
        if len(text) % 4 == 1:
            raise CodecError("length", len(text))

    # 5. Leftover bits check - decode and check
    # Get data characters (without '=')
    data_chars = []
    data_positions = []
    for i, char in enumerate(text):
        if char != '=':
            data_chars.append(char)
            data_positions.append(i)

    if data_chars:
        # Check last group for leftover bits
        final_group_size = len(data_chars) % 4
        if final_group_size == 2:
            # Last char's low 4 bits must be 0
            last_char = data_chars[-1]
            six_bits = alphabet.index(last_char)
            if (six_bits & 0x0F) != 0:
                raise CodecError("bits", data_positions[-1])
        elif final_group_size == 3:
            # Last char's low 2 bits must be 0
            last_char = data_chars[-1]
            six_bits = alphabet.index(last_char)
            if (six_bits & 0x03) != 0:
                raise CodecError("bits", data_positions[-1])

    # Decode
    result = []

    # Build value from data characters - 4 chars = 24 bits = 3 bytes
    value = 0
    for i, char in enumerate(data_chars):
        six_bits = alphabet.index(char)
        value = (value << 6) | six_bits

        # Every 4 data chars = 3 bytes
        if (i + 1) % 4 == 0:
            result.append((value >> 16) & 0xFF)
            result.append((value >> 8) & 0xFF)
            result.append(value & 0xFF)
            value = 0

    # Handle remaining bits
    remaining = len(data_chars) % 4
    if remaining == 1:
        # 1 char = 6 bits, no full byte
        pass
    elif remaining == 2:
        # 2 chars = 12 bits = 1 byte (with 4 padding bits in low positions)
        result.append((value >> 4) & 0xFF)
    elif remaining == 3:
        # 3 chars = 18 bits = 2 bytes (with 2 padding bits in low positions)
        result.append((value >> 10) & 0xFF)
        result.append((value >> 2) & 0xFF)

    return bytes(result)


# Base32 codec

B32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def b32_encode(data, pad=True):
    """Encode bytes to base32 string."""
    if type(data) is not bytes:
        raise CodecError("type", -1)

    result = []

    # Process 5 bytes at a time (40 bits = 8 5-bit chars)
    for i in range(0, len(data), 5):
        chunk = data[i:i+5]

        # Convert chunk to integer
        value = 0
        for byte in chunk:
            value = (value << 8) | byte

        # Shift left to align with 5-bit groups
        bits_to_shift = 40 - (len(chunk) * 8)
        value <<= bits_to_shift

        # Extract 5-bit groups
        num_chars = (len(chunk) * 8 + 4) // 5  # ceil(bits / 5)
        for j in range(8):
            if j < num_chars:
                five_bits = (value >> (35 - j * 5)) & 0x1F
                result.append(B32_ALPHABET[five_bits])

    # Add padding if needed
    if pad:
        padding_needed = (8 - len(result) % 8) % 8
        result.extend(['='] * padding_needed)

    return ''.join(result)


def b32_decode(text, pad=True):
    """Decode base32 string to bytes."""
    # 1. Type check
    if type(text) is not str:
        raise CodecError("type", -1)

    whitespace_chars = {' ', '\t', '\n', '\r', '\f', '\v'}

    # 2. Alphabet check
    for i, char in enumerate(text):
        if char not in B32_ALPHABET and char != '=':
            if char in whitespace_chars:
                raise CodecError("whitespace", i)
            else:
                # Check if it's a lowercase letter or invalid char
                raise CodecError("alphabet", i)

    # 3. Padding check
    if pad:
        # Find the final run of '='
        if text:
            # Count trailing '='
            trailing_eq_count = 0
            for i in range(len(text) - 1, -1, -1):
                if text[i] == '=':
                    trailing_eq_count += 1
                else:
                    break

            # Valid padding lengths for base32 are 1, 3, 4, or 6
            valid_padding = {1, 3, 4, 6}
            if trailing_eq_count not in valid_padding:
                if trailing_eq_count > 0:
                    raise CodecError("padding", len(text) - trailing_eq_count)

            # Check for '=' before the final run
            if trailing_eq_count > 0:
                for i in range(len(text) - trailing_eq_count - 1):
                    if text[i] == '=':
                        raise CodecError("padding", i)
    else:
        # pad=False: no '=' allowed anywhere
        if '=' in text:
            raise CodecError("padding", text.index('='))

    # 4. Length check
    if pad:
        if len(text) % 8 != 0:
            raise CodecError("length", len(text))
    else:
        invalid_lengths = {1, 3, 6}
        if len(text) % 8 in invalid_lengths:
            raise CodecError("length", len(text))

    # 5. Leftover bits check
    data_chars = []
    data_positions = []
    for i, char in enumerate(text):
        if char != '=':
            data_chars.append(char)
            data_positions.append(i)

    if data_chars:
        final_group_size = len(data_chars) % 8
        # Valid sizes are 2, 4, 5, 7 (0 is also valid)
        # Check bits for 2, 4, 5, 7
        if final_group_size == 2:
            # Last char's low 2 bits must be 0
            last_char = data_chars[-1]
            five_bits = B32_ALPHABET.index(last_char)
            if (five_bits & 0x03) != 0:
                raise CodecError("bits", data_positions[-1])
        elif final_group_size == 4:
            # Last char's low 4 bits must be 0
            last_char = data_chars[-1]
            five_bits = B32_ALPHABET.index(last_char)
            if (five_bits & 0x0F) != 0:
                raise CodecError("bits", data_positions[-1])
        elif final_group_size == 5:
            # Last char's low 1 bit must be 0
            last_char = data_chars[-1]
            five_bits = B32_ALPHABET.index(last_char)
            if (five_bits & 0x01) != 0:
                raise CodecError("bits", data_positions[-1])
        elif final_group_size == 7:
            # Last char's low 3 bits must be 0
            last_char = data_chars[-1]
            five_bits = B32_ALPHABET.index(last_char)
            if (five_bits & 0x07) != 0:
                raise CodecError("bits", data_positions[-1])

    # Decode
    result = []

    # Build value from data characters
    value = 0
    for i, char in enumerate(data_chars):
        five_bits = B32_ALPHABET.index(char)
        value = (value << 5) | five_bits

        # Every 8 data chars = 5 bytes
        if (i + 1) % 8 == 0:
            result.append((value >> 32) & 0xFF)
            result.append((value >> 24) & 0xFF)
            result.append((value >> 16) & 0xFF)
            result.append((value >> 8) & 0xFF)
            result.append(value & 0xFF)
            value = 0

    # Handle remaining bits
    remaining = len(data_chars) % 8
    if remaining == 2:
        # 2 chars = 10 bits = 1 byte (with 2 padding bits in low positions)
        result.append((value >> 2) & 0xFF)
    elif remaining == 4:
        # 4 chars = 20 bits = 2 bytes (with 4 padding bits in low positions)
        result.append((value >> 12) & 0xFF)
        result.append((value >> 4) & 0xFF)
    elif remaining == 5:
        # 5 chars = 25 bits = 3 bytes (with 1 padding bit in low position)
        result.append((value >> 17) & 0xFF)
        result.append((value >> 9) & 0xFF)
        result.append((value >> 1) & 0xFF)
    elif remaining == 7:
        # 7 chars = 35 bits = 4 bytes (with 3 padding bits in low positions)
        result.append((value >> 27) & 0xFF)
        result.append((value >> 19) & 0xFF)
        result.append((value >> 11) & 0xFF)
        result.append((value >> 3) & 0xFF)

    return bytes(result)


# Quoted-printable codec

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
            # Convert to =XX format with uppercase hex
            unit = "=" + format(b, '02X')

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
    # 1. Type check
    if type(text) is not str:
        raise CodecError("type", -1)

    # 2. Character-level scan
    valid_chars = set(chr(c) for c in range(33, 127)) | {' ', '\t', '\r', '\n'}

    for i, char in enumerate(text):
        if char not in valid_chars:
            raise CodecError("char", i)

    # Check line endings and '=' rules
    i = 0
    while i < len(text):
        char = text[i]

        # Check for improper line endings
        if char == '\r':
            if i + 1 >= len(text) or text[i + 1] != '\n':
                raise CodecError("eol", i)
            i += 2
            continue
        elif char == '\n':
            raise CodecError("eol", i)

        # Check for '=' (escape or soft line break)
        if char == '=':
            # Check if it's a soft line break (=\r\n)
            if i + 2 < len(text) and text[i + 1] == '\r' and text[i + 2] == '\n':
                i += 3
                continue
            elif i + 2 == len(text) and text[i + 1] == '\r' and text[i + 2] == '\n':
                # This is the last soft break
                i += 3
                continue

            # Check if it's at end or only one char follows
            if i + 1 >= len(text):
                raise CodecError("trunc", i)

            if i + 2 > len(text):
                raise CodecError("trunc", i)

            # Must be followed by two hex digits
            if i + 2 >= len(text):
                raise CodecError("trunc", i)

            hex1 = text[i + 1]
            hex2 = text[i + 2]

            if hex1 not in '0123456789ABCDEF':
                raise CodecError("hex", i + 1)

            if hex2 not in '0123456789ABCDEF':
                raise CodecError("hex", i + 2)

            i += 3
            continue

        i += 1

    # 3. Line length check
    lines_data = text.split('\r\n')
    offset = 0
    for line_idx, line in enumerate(lines_data):
        # Content is the line without trailing '=' (soft break) at the end
        content = line
        if content.endswith('=') and line_idx < len(lines_data) - 1:
            content = content[:-1]

        if len(content) > 75:
            raise CodecError("length", offset + 75)

        offset += len(line) + 2  # +2 for \r\n

    # 4. Trailing whitespace check
    offset = 0
    for line_idx, line in enumerate(lines_data):
        content = line
        if content.endswith('=') and line_idx < len(lines_data) - 1:
            # Soft break line
            content = content[:-1]

        if content and content[-1] in (' ', '\t'):
            raise CodecError("trailws", offset + len(content) - 1)

        offset += len(line) + 2

    # Decode
    result = []
    i = 0
    while i < len(text):
        char = text[i]

        if char == '=':
            # Check for soft line break
            if i + 2 < len(text) and text[i + 1] == '\r' and text[i + 2] == '\n':
                i += 3
                continue
            elif i + 2 == len(text) and text[i + 1] == '\r' and text[i + 2] == '\n':
                i += 3
                continue

            # Decode hex escape
            hex_str = text[i + 1:i + 3]
            byte_val = int(hex_str, 16)
            result.append(byte_val)
            i += 3
        elif char == '\r':
            # Hard line break
            result.append(ord('\r'))
            result.append(ord('\n'))
            i += 2
        else:
            result.append(ord(char))
            i += 1

    return bytes(result)
