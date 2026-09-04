"""Strict binary-to-text codecs: base64, base32, and quoted-printable."""


class CodecError(ValueError):
    """Exception for codec validation errors."""

    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(f"CodecError(kind={kind!r}, pos={pos})")


# Base64 implementation
B64_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
B64_URLSAFE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"


def b64_encode(data, urlsafe=False, pad=True):
    """Encode bytes to base64 string."""
    if type(data) is not bytes:
        raise CodecError("type", -1)

    alphabet = B64_URLSAFE if urlsafe else B64_ALPHABET
    result = []

    # Process the data in groups of 3 bytes (24 bits)
    for i in range(0, len(data), 3):
        chunk = data[i:i+3]

        # Convert bytes to a single number (big-endian)
        num = 0
        for byte in chunk:
            num = (num << 8) | byte

        # Pad with zeros on the right to align
        # 1 byte = 8 bits, need to shift left by 16 bits
        # 2 bytes = 16 bits, need to shift left by 8 bits
        # 3 bytes = 24 bits, no shift needed
        if len(chunk) == 1:
            num <<= 16
            # Extract 4 groups of 6 bits (but only first 2 are data)
            result.append(alphabet[(num >> 18) & 0x3F])
            result.append(alphabet[(num >> 12) & 0x3F])
        elif len(chunk) == 2:
            num <<= 8
            # Extract 4 groups of 6 bits (but only first 3 are data)
            result.append(alphabet[(num >> 18) & 0x3F])
            result.append(alphabet[(num >> 12) & 0x3F])
            result.append(alphabet[(num >> 6) & 0x3F])
        else:  # len(chunk) == 3
            # Extract 4 groups of 6 bits
            result.append(alphabet[(num >> 18) & 0x3F])
            result.append(alphabet[(num >> 12) & 0x3F])
            result.append(alphabet[(num >> 6) & 0x3F])
            result.append(alphabet[num & 0x3F])

    output = "".join(result)

    if pad:
        # Pad to multiple of 4
        remainder = len(output) % 4
        if remainder:
            output += "=" * (4 - remainder)

    return output


def b64_decode(text, urlsafe=False, pad=True):
    """Decode base64 string to bytes."""
    # Check type
    if type(text) is not str:
        raise CodecError("type", -1)

    alphabet = B64_URLSAFE if urlsafe else B64_ALPHABET
    other_alphabet = B64_ALPHABET if urlsafe else B64_URLSAFE

    # Create lookup tables
    lookup = {}
    for i, c in enumerate(alphabet):
        lookup[c] = i

    # Step 2: Alphabet validation
    equals_start = -1
    data_chars = []

    for i, c in enumerate(text):
        if c == '=':
            if equals_start == -1:
                equals_start = i
            data_chars.append(None)
        elif c in alphabet:
            data_chars.append(lookup[c])
        else:
            # Check if it's whitespace
            if c in ' \t\n\r\f\v':
                raise CodecError("whitespace", i)
            # Check if it's from the other alphabet
            elif c in other_alphabet:
                raise CodecError("alphabet", i)
            else:
                raise CodecError("alphabet", i)

    # Step 3: Padding validation
    if not pad:
        # No = allowed when pad=False
        if '=' in text:
            for i, c in enumerate(text):
                if c == '=':
                    raise CodecError("padding", i)
    else:
        # With pad=True, check that = only appears at the end
        if equals_start != -1:
            # Find the extent of the final = run
            equals_end = equals_start
            while equals_end < len(text) and text[equals_end] == '=':
                equals_end += 1

            equals_run_len = equals_end - equals_start

            # Check if this is a valid final run
            if equals_run_len > 2 or equals_end != len(text):
                # Invalid run - find the first offending =
                raise CodecError("padding", equals_start)

    # Step 4: Length validation
    if pad:
        if len(text) % 4 != 0 and text != "":
            raise CodecError("length", len(text))
    else:
        if len(text) % 4 == 1:
            raise CodecError("length", len(text))

    # Step 5: Leftover bits validation
    # Count actual data characters (non-= characters)
    data_only = [c for c in data_chars if c is not None]

    if len(data_only) > 0:
        final_group_size = len(data_only) % 4
        if final_group_size == 2:
            # The second character's low 4 bits must be zero
            if data_only[-1] & 0x0F != 0:
                # Find the position of the last data character
                last_data_pos = -1
                for i in range(len(text) - 1, -1, -1):
                    if text[i] != '=':
                        last_data_pos = i
                        break
                raise CodecError("bits", last_data_pos)
        elif final_group_size == 3:
            # The third character's low 2 bits must be zero
            if data_only[-1] & 0x03 != 0:
                # Find the position of the last data character
                last_data_pos = -1
                for i in range(len(text) - 1, -1, -1):
                    if text[i] != '=':
                        last_data_pos = i
                        break
                raise CodecError("bits", last_data_pos)

    # Decode
    result = []
    data_bits = []

    for c in data_only:
        data_bits.extend([
            (c >> 5) & 1,
            (c >> 4) & 1,
            (c >> 3) & 1,
            (c >> 2) & 1,
            (c >> 1) & 1,
            c & 1
        ])

    # Convert bits to bytes, discarding padding bits
    for i in range(0, len(data_bits) - (len(data_bits) % 8), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | data_bits[i + j]
        result.append(byte)

    return bytes(result)


# Base32 implementation
B32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def b32_encode(data, pad=True):
    """Encode bytes to base32 string."""
    if type(data) is not bytes:
        raise CodecError("type", -1)

    result = []

    # Process in groups of 5 bytes (40 bits = 8 * 5-bit groups)
    for i in range(0, len(data), 5):
        chunk = data[i:i+5]

        # Convert to bits
        bits = []
        for byte in chunk:
            for j in range(7, -1, -1):
                bits.append((byte >> j) & 1)

        # Pad bits to multiple of 5
        while len(bits) % 5 != 0:
            bits.append(0)

        # Convert 5-bit groups to characters
        for j in range(0, len(bits), 5):
            val = 0
            for k in range(5):
                val = (val << 1) | bits[j + k]
            result.append(B32_ALPHABET[val])

    output = "".join(result)

    if pad:
        # Pad to multiple of 8
        remainder = len(output) % 8
        if remainder:
            output += "=" * (8 - remainder)

    return output


def b32_decode(text, pad=True):
    """Decode base32 string to bytes."""
    # Check type
    if type(text) is not str:
        raise CodecError("type", -1)

    # Create lookup table
    lookup = {}
    for i, c in enumerate(B32_ALPHABET):
        lookup[c] = i

    # Step 2: Alphabet validation
    equals_start = -1
    data_chars = []

    for i, c in enumerate(text):
        if c == '=':
            if equals_start == -1:
                equals_start = i
            data_chars.append(None)
        elif c in lookup:
            data_chars.append(lookup[c])
        else:
            # Check if it's whitespace
            if c in ' \t\n\r\f\v':
                raise CodecError("whitespace", i)
            else:
                raise CodecError("alphabet", i)

    # Step 3: Padding validation
    if not pad:
        # No = allowed when pad=False
        if '=' in text:
            for i, c in enumerate(text):
                if c == '=':
                    raise CodecError("padding", i)
    else:
        # With pad=True, check valid padding patterns
        if equals_start != -1:
            equals_end = equals_start
            while equals_end < len(text) and text[equals_end] == '=':
                equals_end += 1

            equals_run_len = equals_end - equals_start

            # Valid run lengths for base32: 6, 4, 3, or 1
            # This depends on the number of data characters
            num_data_chars = sum(1 for c in data_chars if c is not None)

            # Calculate expected padding
            if equals_run_len == 6:
                # 2 data chars: 2*5=10 bits, need 16 bits total (2 bytes), so 6 padding
                expected_data = 2
            elif equals_run_len == 4:
                # 4 data chars: 4*5=20 bits, need 24 bits total (3 bytes), so 4 padding
                expected_data = 4
            elif equals_run_len == 3:
                # 5 data chars: 5*5=25 bits, need 32 bits total (4 bytes), so 3 padding
                expected_data = 5
            elif equals_run_len == 1:
                # 7 data chars: 7*5=35 bits, need 40 bits total (5 bytes), so 1 padding
                expected_data = 7
            else:
                # Invalid padding run length
                raise CodecError("padding", equals_start)

            # Check if the run is at the end
            if equals_end != len(text):
                raise CodecError("padding", equals_start)

    # Step 4: Length validation
    if pad:
        if len(text) % 8 != 0 and text != "":
            raise CodecError("length", len(text))
    else:
        if len(text) % 8 in [1, 3, 6]:
            raise CodecError("length", len(text))

    # Step 5: Leftover bits validation
    data_only = [c for c in data_chars if c is not None]

    if len(data_only) > 0:
        final_group_size = len(data_only) % 8

        # Map group size to required zero bits
        zero_bits_map = {
            2: 2,  # 2*5=10 bits, need 2 zero bits for byte alignment
            4: 4,  # 4*5=20 bits, need 4 zero bits
            5: 1,  # 5*5=25 bits, need 1 zero bit
            7: 3   # 7*5=35 bits, need 3 zero bits
        }

        if final_group_size in zero_bits_map:
            required_zeros = zero_bits_map[final_group_size]
            last_val = data_only[-1]

            # Check if the low bits are zero
            if required_zeros > 0:
                mask = (1 << required_zeros) - 1
                if last_val & mask != 0:
                    # Find position of last data character
                    last_data_pos = -1
                    for i in range(len(text) - 1, -1, -1):
                        if text[i] != '=':
                            last_data_pos = i
                            break
                    raise CodecError("bits", last_data_pos)

    # Decode
    result = []
    bits = []

    for c in data_only:
        for i in range(4, -1, -1):
            bits.append((c >> i) & 1)

    # Convert bits to bytes
    for i in range(0, len(bits) - (len(bits) % 8), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        result.append(byte)

    return bytes(result)


# Quoted-printable implementation
def qp_encode(data):
    """Encode bytes to quoted-printable string."""
    if type(data) is not bytes:
        raise CodecError("type", -1)

    lines = []
    line = ""

    for i, b in enumerate(data):
        if b == 0x20 or b == 0x09:  # space or tab
            if i != len(data) - 1:
                unit = chr(b)
            else:
                unit = "=20" if b == 0x20 else "=09"
        elif 33 <= b <= 126 and b != 0x3D:  # printable, not '='
            unit = chr(b)
        else:
            # Convert to hex
            hex_str = "0123456789ABCDEF"
            unit = "=" + hex_str[(b >> 4) & 0x0F] + hex_str[b & 0x0F]

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
    # Check type
    if type(text) is not str:
        raise CodecError("type", -1)

    # Step 2: Character-level scan
    for i, c in enumerate(text):
        # Check valid characters: ASCII 33-126, space, tab, CR, LF
        if c == '\r':
            # Must be followed by LF
            if i + 1 >= len(text) or text[i + 1] != '\n':
                raise CodecError("eol", i)
        elif c == '\n':
            # Must be preceded by CR
            if i == 0 or text[i - 1] != '\r':
                raise CodecError("eol", i)
        elif c == '=':
            # Handle soft line break and hex escapes
            if i + 1 >= len(text):
                raise CodecError("trunc", i)

            if i + 2 >= len(text):
                raise CodecError("trunc", i)

            # Check if it's a soft line break (= CR LF)
            if text[i + 1:i + 3] == '\r\n':
                # Check if anything follows the LF
                if i + 3 >= len(text):
                    # Nothing after LF - this is an eol error at the = position
                    # Actually, re-reading: "if nothing at all follows that LF, it is eol at the offset of the ="
                    # But wait, let me check the exact wording again
                    # "if nothing at all follows that LF, it is "eol" at the offset of the ="
                    # This means the soft break is at the very end, which is technically fine for soft breaks
                    # Let me re-read: an "=" followed by CR LF is a soft line break
                    # But if nothing follows the LF, it's an eol error
                    # So a soft break must have something after it
                    raise CodecError("eol", i)
            else:
                # Must be followed by two hex digits
                if i + 2 >= len(text):
                    raise CodecError("trunc", i)

                hex1 = text[i + 1]
                hex2 = text[i + 2]

                if not ((hex1 >= '0' and hex1 <= '9') or (hex1 >= 'A' and hex1 <= 'F')):
                    raise CodecError("hex", i + 1)

                if not ((hex2 >= '0' and hex2 <= '9') or (hex2 >= 'A' and hex2 <= 'F')):
                    raise CodecError("hex", i + 2)
        elif c == ' ' or c == '\t':
            pass  # Will be checked in step 4
        elif ord(c) < 33 or ord(c) > 126:
            raise CodecError("char", i)

    # Step 3: Line length
    lines = text.split('\r\n')
    pos = 0

    for line_idx, line in enumerate(lines):
        # Remove trailing soft break if present
        line_content = line
        if line_content.endswith('='):
            line_content = line_content[:-1]

        if len(line_content) > 75:
            raise CodecError("length", pos + 75)

        pos += len(line) + 2  # +2 for \r\n

    # Step 4: Trailing whitespace
    pos = 0
    lines = text.split('\r\n')

    for line_idx, line in enumerate(lines):
        # Get line content (without soft break)
        line_content = line
        if line_content.endswith('='):
            line_content = line_content[:-1]

        if line_content and (line_content[-1] == ' ' or line_content[-1] == '\t'):
            raise CodecError("trailws", pos + len(line_content) - 1)

        pos += len(line) + 2  # +2 for \r\n

    # Decode
    result = []
    i = 0

    while i < len(text):
        if text[i] == '=':
            if i + 2 < len(text) and text[i + 1:i + 3] == '\r\n':
                # Soft line break - skip it
                i += 3
            else:
                # Hex escape
                hex1 = text[i + 1]
                hex2 = text[i + 2]

                # Convert hex to byte
                val = 0
                if hex1 >= '0' and hex1 <= '9':
                    val += (ord(hex1) - ord('0')) * 16
                else:
                    val += (ord(hex1) - ord('A') + 10) * 16

                if hex2 >= '0' and hex2 <= '9':
                    val += ord(hex2) - ord('0')
                else:
                    val += ord(hex2) - ord('A') + 10

                result.append(val)
                i += 3
        elif text[i:i+2] == '\r\n':
            # Hard line break
            result.append(ord('\r'))
            result.append(ord('\n'))
            i += 2
        else:
            # Regular character
            result.append(ord(text[i]))
            i += 1

    return bytes(result)
