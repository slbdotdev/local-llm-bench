"""Strict canonical bencode binary codec."""


class BencodeError(Exception):
    """Bencode error with kind and offset attributes."""

    def __init__(self, kind, offset):
        self.kind = kind
        self.offset = offset
        super().__init__(f"BencodeError: {kind} at offset {offset}")


def encode(obj):
    """Encode a Python object to bencode bytes.

    Raises BencodeError with offset=None for encoding errors.
    """
    encoder = Encoder()
    encoder.encode_value(obj, depth=1)
    return encoder.result


def decode(data):
    """Decode bencode bytes to a Python object.

    Raises BencodeError with appropriate offset for decoding errors.
    """
    if type(data) is not bytes:
        raise BencodeError("type", 0)

    decoder = Decoder(data)
    result, end_pos = decoder.parse_value(0, depth=1)

    if end_pos != len(data):
        raise BencodeError("trailing", end_pos)

    return result


class Encoder:
    """Encodes Python objects to bencode format."""

    def __init__(self):
        self.result = b""

    def encode_value(self, value, depth):
        """Encode a value, validating in exact order."""
        # 1. Check if it's a bool (before checking int)
        if type(value) is bool:
            raise BencodeError("bool", None)

        # 2. Check exact type
        value_type = type(value)
        if value_type not in (int, bytes, list, dict):
            raise BencodeError("type", None)

        # 3. Check range for ints
        if value_type is int:
            if not (-2**63 <= value <= 2**63 - 1):
                raise BencodeError("range", None)
            self.encode_int(value)
            return

        # 4. Check depth for list and dict
        if value_type in (list, dict):
            if depth > 32:
                raise BencodeError("depth", None)

        # 5. For dict, check all keys are exactly bytes (in insertion order)
        if value_type is dict:
            for key in value:
                if type(key) is not bytes:
                    raise BencodeError("key_type", None)

        # 6. Encode based on type
        if value_type is bytes:
            self.encode_bytes(value)
        elif value_type is list:
            self.encode_list(value, depth)
        elif value_type is dict:
            self.encode_dict(value, depth)

    def encode_int(self, value):
        """Encode an integer."""
        self.result += b"i" + str(value).encode() + b"e"

    def encode_bytes(self, value):
        """Encode a byte string."""
        length = len(value)
        self.result += str(length).encode() + b":" + value

    def encode_list(self, value, depth):
        """Encode a list."""
        self.result += b"l"
        for item in value:
            self.encode_value(item, depth + 1)
        self.result += b"e"

    def encode_dict(self, value, depth):
        """Encode a dictionary with sorted keys."""
        self.result += b"d"
        # Sort keys by raw byte value (ascending)
        sorted_keys = sorted(value.keys())
        for key in sorted_keys:
            self.encode_bytes(key)
            self.encode_value(value[key], depth + 1)
        self.result += b"e"


class Decoder:
    """Decodes bencode bytes to Python objects."""

    def __init__(self, data):
        self.data = data

    def parse_value(self, offset, depth):
        """Parse one value at offset. Returns (value, end_pos)."""
        if offset == len(self.data):
            raise BencodeError("truncated", len(self.data))

        byte = self.data[offset]

        # Integer
        if byte == ord(b"i"):
            return self.parse_int(offset, depth)

        # Byte string (ASCII digit)
        elif 48 <= byte <= 57:  # '0'-'9'
            return self.parse_bytes(offset, depth)

        # List
        elif byte == ord(b"l"):
            return self.parse_list(offset, depth)

        # Dict
        elif byte == ord(b"d"):
            return self.parse_dict(offset, depth)

        # Any other byte
        else:
            raise BencodeError("syntax", offset)

    def parse_int(self, offset, depth):
        """Parse an integer starting at offset."""
        # Find the ending 'e'
        i = offset + 1
        while i < len(self.data) and self.data[i] != ord(b"e"):
            i += 1

        if i == len(self.data):
            raise BencodeError("truncated", len(self.data))

        body = self.data[offset + 1:i]

        # Determine where digits start
        if body and body[0] == ord(b"-"):
            k = offset + 2
        else:
            k = offset + 1

        # 1. Check for no digits
        if k >= i:
            raise BencodeError("syntax", k)

        # 2. Check all bytes are ASCII digits
        for byte_pos in range(k, i):
            byte = self.data[byte_pos]
            if not (48 <= byte <= 57):  # '0'-'9'
                raise BencodeError("syntax", byte_pos)

        # 3. Check for leading zeros
        if i - k > 1 and self.data[k] == ord(b"0"):
            raise BencodeError("leading_zero", k)

        # 4. Check for -0
        if body == b"-0":
            raise BencodeError("negative_zero", offset + 1)

        # Convert to int
        value = int(body)

        # 5. Check range
        if not (-2**63 <= value <= 2**63 - 1):
            raise BencodeError("range", offset)

        return value, i + 1

    def parse_bytes(self, offset, depth):
        """Parse a byte string starting at offset."""
        # Find the colon
        i = offset
        while i < len(self.data) and self.data[i] != ord(b":"):
            i += 1

        if i == len(self.data):
            raise BencodeError("truncated", len(self.data))

        # 1. Check all bytes before ':' are ASCII digits
        for byte_pos in range(offset, i):
            byte = self.data[byte_pos]
            if not (48 <= byte <= 57):  # '0'-'9'
                raise BencodeError("syntax", byte_pos)

        # 2. Check for leading zeros
        if i - offset > 1 and self.data[offset] == ord(b"0"):
            raise BencodeError("leading_zero", offset)

        # Get length
        length = int(self.data[offset:i])

        # 3. Check length range
        if length > 2**31 - 1:
            raise BencodeError("range", offset)

        # 4. Check if enough bytes remain
        data_start = i + 1
        data_end = data_start + length

        if data_end > len(self.data):
            raise BencodeError("truncated", len(self.data))

        value = self.data[data_start:data_end]
        return value, data_end

    def parse_list(self, offset, depth):
        """Parse a list starting at offset."""
        # Check depth
        if depth > 32:
            raise BencodeError("depth", offset)

        elements = []
        pos = offset + 1

        while True:
            if pos == len(self.data):
                raise BencodeError("truncated", len(self.data))

            if self.data[pos] == ord(b"e"):
                return elements, pos + 1

            element, pos = self.parse_value(pos, depth + 1)
            elements.append(element)

    def parse_dict(self, offset, depth):
        """Parse a dict starting at offset."""
        # Check depth
        if depth > 32:
            raise BencodeError("depth", offset)

        result = {}
        pos = offset + 1
        prev_key = None

        while True:
            if pos == len(self.data):
                raise BencodeError("truncated", len(self.data))

            if self.data[pos] == ord(b"e"):
                return result, pos + 1

            # Key must be a byte string
            byte = self.data[pos]
            key_start = pos

            # 1. Check key type (no i, l, d)
            if byte in (ord(b"i"), ord(b"l"), ord(b"d")):
                raise BencodeError("key_type", pos)

            # 2. Check key starts with digit
            if not (48 <= byte <= 57):  # '0'-'9'
                raise BencodeError("syntax", pos)

            # 3. Parse key and check order
            key, pos = self.parse_bytes(key_start, depth + 1)

            if key == prev_key:
                raise BencodeError("duplicate_key", key_start)

            if prev_key is not None and key < prev_key:
                raise BencodeError("key_order", key_start)

            prev_key = key

            # 4. Parse value
            value, pos = self.parse_value(pos, depth + 1)
            result[key] = value
