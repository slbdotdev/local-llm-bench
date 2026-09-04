"""Strict canonical bencode binary codec."""


class BencodeError(Exception):
    """Exception raised for bencode encoding/decoding errors."""

    def __init__(self, kind, offset):
        self.kind = kind
        self.offset = offset
        super().__init__(f"{kind} at offset {offset}")


def encode(obj):
    """Encode a Python object to canonical bencode bytes.

    Raises BencodeError on invalid input.
    """
    try:
        result = _encode_value(obj, depth=1)
        return result
    except BencodeError:
        raise


def _encode_value(value, depth):
    """Recursively encode a value, tracking depth."""
    # 1. Check for bool first (before int check since bool is subclass of int)
    if type(value) is bool:
        raise BencodeError("bool", None)

    # 2. Check exact type
    if type(value) not in (int, bytes, list, dict):
        raise BencodeError("type", None)

    # 3. Check range for int
    if type(value) is int:
        if value < -(2**63) or value > 2**63 - 1:
            raise BencodeError("range", None)
        return b"i" + str(value).encode() + b"e"

    # For bytes
    if type(value) is bytes:
        return str(len(value)).encode() + b":" + value

    # For list and dict, check depth
    if depth > 32:
        raise BencodeError("depth", None)

    # 4. Handle list
    if type(value) is list:
        result = b"l"
        for item in value:
            result += _encode_value(item, depth + 1)
        result += b"e"
        return result

    # 5. Handle dict
    if type(value) is dict:
        # First check all keys before any value
        for key in value:
            if type(key) is not bytes:
                raise BencodeError("key_type", None)

        # Process values in sorted key order
        result = b"d"
        sorted_keys = sorted(value.keys())
        for key in sorted_keys:
            result += str(len(key)).encode() + b":" + key
            result += _encode_value(value[key], depth + 1)
        result += b"e"
        return result


def decode(data):
    """Decode bencode bytes to a Python object.

    Raises BencodeError on invalid input.
    """
    # Check type of input
    if type(data) is not bytes:
        raise BencodeError("type", 0)

    # Parse one value from offset 0
    value, end_offset = _decode_value(data, 0, depth=1)

    # Check that nothing follows the top-level value
    if end_offset != len(data):
        raise BencodeError("trailing", end_offset)

    return value


def _decode_value(data, offset, depth):
    """Recursively decode a value starting at offset.

    Returns (value, end_offset) where end_offset is the offset after the value.
    Raises BencodeError on invalid input.
    """
    # Check if we're at end of data
    if offset >= len(data):
        raise BencodeError("truncated", len(data))

    byte = data[offset]

    # Integer: starts with 'i' (0x69)
    if byte == ord('i'):
        return _decode_integer(data, offset, depth)

    # Byte string: starts with ASCII digit
    if ord('0') <= byte <= ord('9'):
        return _decode_bytestring(data, offset, depth)

    # List: starts with 'l' (0x6C)
    if byte == ord('l'):
        return _decode_list(data, offset, depth)

    # Dict: starts with 'd' (0x64)
    if byte == ord('d'):
        return _decode_dict(data, offset, depth)

    # Any other byte
    raise BencodeError("syntax", offset)


def _decode_integer(data, offset, depth):
    """Decode an integer starting with 'i'."""
    # Find the 'e' terminator
    e_index = data.find(ord('e'), offset + 1)
    if e_index == -1:
        raise BencodeError("truncated", len(data))

    body = data[offset + 1:e_index]

    # Determine where digits start
    if len(body) > 0 and body[0:1] == b'-':
        k = offset + 2
    else:
        k = offset + 1

    # 1. Check if there are no digits
    if k >= e_index:
        raise BencodeError("syntax", k)

    # 2. Check for non-digit characters
    for i in range(k, e_index):
        byte = data[i]
        if not (ord('0') <= byte <= ord('9')):
            raise BencodeError("syntax", i)

    # 3. Check for leading zero
    if e_index - k > 1 and data[k] == ord('0'):
        raise BencodeError("leading_zero", k)

    # 4. Check for -0
    if body == b'-0':
        raise BencodeError("negative_zero", offset + 1)

    # Convert to integer
    value = int(body)

    # 5. Check range
    if value < -(2**63) or value > 2**63 - 1:
        raise BencodeError("range", offset)

    return value, e_index + 1


def _decode_bytestring(data, offset, depth):
    """Decode a byte string starting with ASCII digit."""
    # Find the ':' separator
    colon_index = data.find(ord(':'), offset)
    if colon_index == -1:
        raise BencodeError("truncated", len(data))

    length_bytes = data[offset:colon_index]

    # 1. Check for non-digit characters in length
    for i in range(offset, colon_index):
        byte = data[i]
        if not (ord('0') <= byte <= ord('9')):
            raise BencodeError("syntax", i)

    # 2. Check for leading zero
    if colon_index - offset > 1 and data[offset] == ord('0'):
        raise BencodeError("leading_zero", offset)

    # Convert length
    length = int(length_bytes)

    # 3. Check range
    if length > 2**31 - 1:
        raise BencodeError("range", offset)

    # 4. Check if enough bytes remain
    bytes_start = colon_index + 1
    bytes_end = bytes_start + length
    if bytes_end > len(data):
        raise BencodeError("truncated", len(data))

    return data[bytes_start:bytes_end], bytes_end


def _decode_list(data, offset, depth):
    """Decode a list starting with 'l'."""
    # Check depth
    if depth > 32:
        raise BencodeError("depth", offset)

    result = []
    p = offset + 1

    while True:
        # Check if we're at end
        if p >= len(data):
            raise BencodeError("truncated", len(data))

        # Check for end marker
        if data[p] == ord('e'):
            return result, p + 1

        # Parse element
        element, p = _decode_value(data, p, depth + 1)
        result.append(element)


def _decode_dict(data, offset, depth):
    """Decode a dict starting with 'd'."""
    # Check depth
    if depth > 32:
        raise BencodeError("depth", offset)

    result = {}
    p = offset + 1
    prev_key = None

    while True:
        # Check if we're at end
        if p >= len(data):
            raise BencodeError("truncated", len(data))

        # Check for end marker
        if data[p] == ord('e'):
            return result, p + 1

        # Parse key (must be a byte string)
        key_byte = data[p]
        key_start = p  # Track where key parsing starts

        # 1. Check if it's an invalid key type
        if key_byte == ord('i') or key_byte == ord('l') or key_byte == ord('d'):
            raise BencodeError("key_type", p)

        # 2. Check for non-digit (invalid syntax)
        if not (ord('0') <= key_byte <= ord('9')):
            raise BencodeError("syntax", p)

        # 3. Parse the key as a byte string
        key, p = _decode_bytestring(data, key_start, depth + 1)

        # Check for duplicate key
        if key == prev_key:
            raise BencodeError("duplicate_key", key_start)

        # Check for key order (must be sorted)
        if prev_key is not None and key < prev_key:
            raise BencodeError("key_order", key_start)

        prev_key = key

        # 4. Parse the value
        value, p = _decode_value(data, p, depth + 1)

        result[key] = value
