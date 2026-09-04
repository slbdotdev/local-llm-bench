"""Strict canonical bencode binary codec"""


class BencodeError(Exception):
    """Bencode error with kind and offset attributes"""
    def __init__(self, kind, offset):
        self.kind = kind
        self.offset = offset
        super().__init__(f"{kind} at offset {offset}")


def encode(obj):
    """Encode a Python object to bencode bytes"""
    # Check for bool first (before int, since bool is subclass of int)
    if type(obj) is bool:
        raise BencodeError("bool", None)

    return _encode_value(obj, depth=1)


def _encode_value(obj, depth):
    """Encode a value, checking type and constraints"""
    # Type check - exact type only
    if type(obj) is bool:
        raise BencodeError("bool", None)

    obj_type = type(obj)

    if obj_type is int:
        # Check range
        if not (-2**63 <= obj <= 2**63 - 1):
            raise BencodeError("range", None)
        return b"i" + str(obj).encode() + b"e"

    elif obj_type is bytes:
        return str(len(obj)).encode() + b":" + obj

    elif obj_type is list:
        # Check depth
        if depth > 32:
            raise BencodeError("depth", None)

        result = b"l"
        for item in obj:
            result += _encode_value(item, depth + 1)
        result += b"e"
        return result

    elif obj_type is dict:
        # Check depth
        if depth > 32:
            raise BencodeError("depth", None)

        # First, check all keys are exactly bytes in insertion order
        for key in obj:
            if type(key) is not bytes:
                raise BencodeError("key_type", None)

        # Encode dict with sorted keys
        result = b"d"
        for key in sorted(obj.keys()):
            result += _encode_value(key, depth + 1)
            result += _encode_value(obj[key], depth + 1)
        result += b"e"
        return result

    else:
        raise BencodeError("type", None)


def decode(data):
    """Decode bencode bytes to a Python object"""
    if type(data) is not bytes:
        raise BencodeError("type", 0)

    value, pos = _decode_value(data, 0, depth=1)

    if pos != len(data):
        raise BencodeError("trailing", pos)

    return value


def _decode_value(data, offset, depth):
    """
    Decode a value starting at offset.
    Returns (value, end_offset) tuple.
    """
    if offset == len(data):
        raise BencodeError("truncated", len(data))

    byte = data[offset]

    # Integer
    if byte == ord(b"i"):
        return _decode_integer(data, offset)

    # Byte string (ASCII digit)
    elif 48 <= byte <= 57:  # '0' to '9'
        return _decode_bytestring(data, offset)

    # List
    elif byte == ord(b"l"):
        return _decode_list(data, offset, depth)

    # Dict
    elif byte == ord(b"d"):
        return _decode_dict(data, offset, depth)

    # Syntax error
    else:
        raise BencodeError("syntax", offset)


def _decode_integer(data, offset):
    """Decode an integer starting with 'i'"""
    # offset points to 'i'

    # Find 'e'
    e_pos = data.find(b"e", offset + 1)
    if e_pos == -1:
        raise BencodeError("truncated", len(data))

    body = data[offset + 1:e_pos]

    # Determine where digits start (after optional '-')
    if body and body[0:1] == b"-"[0:1]:
        digit_start = 1
    else:
        digit_start = 0

    # Check for no digits
    if digit_start >= len(body):
        raise BencodeError("syntax", offset + 1 + digit_start)

    # Check all characters are digits
    for i in range(digit_start, len(body)):
        if not (48 <= body[i] <= 57):  # '0' to '9'
            raise BencodeError("syntax", offset + 1 + i)

    # Check for leading zero (multi-digit starting with 0)
    if len(body) > digit_start + 1 and body[digit_start] == ord(b"0"):
        raise BencodeError("leading_zero", offset + 1 + digit_start)

    # Check for negative zero
    if body == b"-0":
        raise BencodeError("negative_zero", offset + 1)

    # Parse the integer
    value = int(body)

    # Check range
    if not (-2**63 <= value <= 2**63 - 1):
        raise BencodeError("range", offset)

    return value, e_pos + 1


def _decode_bytestring(data, offset):
    """Decode a byte string starting at offset"""
    # offset points to first digit of length

    # Find ':'
    colon_pos = data.find(b":", offset)
    if colon_pos == -1:
        raise BencodeError("truncated", len(data))

    length_bytes = data[offset:colon_pos]

    # Check all are digits
    for i, byte in enumerate(length_bytes):
        if not (48 <= byte <= 57):  # '0' to '9'
            raise BencodeError("syntax", offset + i)

    # Check for leading zero
    if len(length_bytes) > 1 and length_bytes[0] == ord(b"0"):
        raise BencodeError("leading_zero", offset)

    # Parse length
    length = int(length_bytes)

    # Check range
    if length > 2**31 - 1:
        raise BencodeError("range", offset)

    # Check if we have enough bytes
    if colon_pos + 1 + length > len(data):
        raise BencodeError("truncated", len(data))

    value = data[colon_pos + 1:colon_pos + 1 + length]
    return value, colon_pos + 1 + length


def _decode_list(data, offset, depth):
    """Decode a list starting with 'l'"""
    # Check depth
    if depth > 32:
        raise BencodeError("depth", offset)

    result = []
    pos = offset + 1

    while True:
        if pos == len(data):
            raise BencodeError("truncated", len(data))

        if data[pos] == ord(b"e"):
            return result, pos + 1

        value, pos = _decode_value(data, pos, depth + 1)
        result.append(value)


def _decode_dict(data, offset, depth):
    """Decode a dict starting with 'd'"""
    # Check depth
    if depth > 32:
        raise BencodeError("depth", offset)

    result = {}
    pos = offset + 1
    prev_key = None

    while True:
        if pos == len(data):
            raise BencodeError("truncated", len(data))

        if data[pos] == ord(b"e"):
            return result, pos + 1

        # Check key type - must be byte string
        byte = data[pos]

        if byte == ord(b"i") or byte == ord(b"l") or byte == ord(b"d"):
            raise BencodeError("key_type", pos)

        # Key must be a digit (byte string) or syntax error
        if not (48 <= byte <= 57):  # '0' to '9'
            raise BencodeError("syntax", pos)

        # Parse key
        key, pos = _decode_bytestring(data, pos)

        # Check for duplicate key
        if key == prev_key:
            raise BencodeError("duplicate_key", pos - (len(key) + len(str(len(key))) + 1))

        # Check for key order (must be sorted)
        if prev_key is not None and key < prev_key:
            raise BencodeError("key_order", pos - (len(key) + len(str(len(key))) + 1))

        prev_key = key

        # Parse value
        value, pos = _decode_value(data, pos, depth + 1)

        result[key] = value
