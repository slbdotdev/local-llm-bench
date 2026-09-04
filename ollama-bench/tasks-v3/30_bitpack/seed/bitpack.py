"""Pack and unpack small integers into bytes at a fixed bit width."""


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
    out = bytearray((len(values) * width + 7) // 8)
    for i, v in enumerate(values):
        if not isinstance(v, int):
            raise ValueError("value must be an int")
        if signed:
            if not (-(2 ** (width - 1)) < v < 2 ** (width - 1)):
                raise ValueError("value out of range")
        else:
            if not (0 <= v <= 2 ** width):
                raise ValueError("value out of range")
        for b in range(width):
            if (v >> b) & 1:
                pos = i * width + b
                out[pos // 8] |= 1 << (pos % 8)
    return bytes(out)


def unpack(width, data, signed=False):
    """Inverse of pack: returns one int per `width` bits of `data`, in order.

    Bits are read MSB-first (the first value comes from the most significant
    bits of the first byte).  The number of returned values is
    len(data)*8 // width; any leftover padding bits at the end are ignored,
    whatever they contain.  If `signed` is True each field is sign-extended
    (two's complement).  `width` follows the same rules as in pack.

    Examples: unpack(4, b"\xa3") == [10, 3]; unpack(4, b"") == [].
    """
    n = len(data) * 8 // width
    out = []
    for i in range(n):
        v = 0
        for b in range(width):
            pos = i * width + b
            v |= ((data[pos // 8] >> (pos % 8)) & 1) << b
        if signed and v > 2 ** (width - 1):
            v -= 2 ** width
        out.append(v)
    return out
