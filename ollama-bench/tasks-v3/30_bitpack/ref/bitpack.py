"""Pack and unpack small integers into bytes at a fixed bit width."""


def _check_width(width):
    if not isinstance(width, int) or not 1 <= width <= 32:
        raise ValueError("width must be an int in 1..32")


def pack(width, values, signed=False):
    """Pack `values` (an iterable of ints) into bytes, `width` bits per value.

    Bits are packed MSB-first: the first value occupies the most significant
    bits of the first byte, values are concatenated back-to-back in order,
    and the final partial byte is padded with zero bits on the
    least-significant side.

    `width` must be an int with 1 <= width <= 32, otherwise ValueError.
    Each value must be an int, otherwise ValueError.  If `signed` is False,
    every value must satisfy 0 <= v < 2**width; if `signed` is True, values
    are two's-complement and must satisfy -2**(width-1) <= v < 2**(width-1).
    Out-of-range values raise ValueError.

    Examples: pack(4, [0b1010, 0b0011]) == b"\xa3"; pack(4, []) == b"".
    """
    _check_width(width)
    acc = 0
    for v in values:
        if not isinstance(v, int):
            raise ValueError("value must be an int")
        if signed:
            if not -(2 ** (width - 1)) <= v < 2 ** (width - 1):
                raise ValueError("value out of range")
        elif not 0 <= v < 2 ** width:
            raise ValueError("value out of range")
        acc = (acc << width) | (v & ((1 << width) - 1))
    total = len(values) * width
    nbytes = (total + 7) // 8
    acc <<= nbytes * 8 - total
    return acc.to_bytes(nbytes, "big")


def unpack(width, data, signed=False):
    """Inverse of pack: returns one int per `width` bits of `data`, in order.

    Bits are read MSB-first (the first value comes from the most significant
    bits of the first byte).  The number of returned values is
    len(data)*8 // width; any leftover padding bits at the end are ignored,
    whatever they contain.  If `signed` is True each field is sign-extended
    (two's complement).  `width` follows the same rules as in pack.

    Examples: unpack(4, b"\xa3") == [10, 3]; unpack(4, b"") == [].
    """
    _check_width(width)
    total = len(data) * 8
    n = total // width
    big = int.from_bytes(bytes(data), "big")
    out = []
    for i in range(n):
        v = (big >> (total - (i + 1) * width)) & ((1 << width) - 1)
        if signed and v >= 1 << (width - 1):
            v -= 1 << width
        out.append(v)
    return out
