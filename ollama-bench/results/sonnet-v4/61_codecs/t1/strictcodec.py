"""Strict binary-to-text codecs: base64, base32, binary quoted-printable.

Standard library only (no base64/binascii/quopri/codecs/re/struct/email/uu).
"""

STD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
URL_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
B32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

_WS = set(" \t\n\r\f\v")
_HEXDIGITS = set("0123456789ABCDEF")
_HEXCHARS = "0123456789ABCDEF"


class CodecError(ValueError):
    def __init__(self, kind, pos):
        super().__init__("%s error at %d" % (kind, pos))
        self.kind = kind
        self.pos = pos


# ---------------------------------------------------------------------------
# generic base-N helpers
# ---------------------------------------------------------------------------

def _encode_generic(data, alphabet, unit_bits, group_len, pad):
    bits = 0
    nbits = 0
    chars = []
    mask = (1 << unit_bits) - 1
    for b in data:
        bits = (bits << 8) | b
        nbits += 8
        while nbits >= unit_bits:
            nbits -= unit_bits
            chars.append(alphabet[(bits >> nbits) & mask])
    if nbits > 0:
        chars.append(alphabet[(bits << (unit_bits - nbits)) & mask])
    s = "".join(chars)
    if pad:
        while len(s) % group_len != 0:
            s += "="
    return s


def _decode_core(text, alphabet, unit_bits, group_len, pad, valid_pad_runs,
                  bits_map, bad_len_mod):
    alpha_set = set(alphabet)

    # Step 2: alphabet scan
    for i, c in enumerate(text):
        if c in alpha_set or c == "=":
            continue
        if c in _WS:
            raise CodecError("whitespace", i)
        raise CodecError("alphabet", i)

    n = len(text)

    # Step 3: padding
    run_start = n
    while run_start > 0 and text[run_start - 1] == "=":
        run_start -= 1
    run_len = n - run_start

    if not pad:
        for i, c in enumerate(text):
            if c == "=":
                raise CodecError("padding", i)
    else:
        if run_len in valid_pad_runs:
            for i in range(run_start):
                if text[i] == "=":
                    raise CodecError("padding", i)
        else:
            for i, c in enumerate(text):
                if c == "=":
                    raise CodecError("padding", i)

    # Step 4: length
    if pad:
        if n % group_len != 0:
            raise CodecError("length", n)
    else:
        if (n % group_len) in bad_len_mod:
            raise CodecError("length", n)

    # Step 5: leftover bits
    last_pos = -1
    count = 0
    for i, c in enumerate(text):
        if c != "=":
            last_pos = i
            count += 1
    if last_pos != -1:
        remainder = count % group_len
        if remainder in bits_map:
            bits_to_check = bits_map[remainder]
            val = alphabet.index(text[last_pos])
            m = (1 << bits_to_check) - 1
            if val & m != 0:
                raise CodecError("bits", last_pos)


def _bits_to_bytes(data_chars, alphabet, unit_bits):
    bits = 0
    nbits = 0
    out = bytearray()
    for c in data_chars:
        v = alphabet.index(c)
        bits = (bits << unit_bits) | v
        nbits += unit_bits
        while nbits >= 8:
            nbits -= 8
            out.append((bits >> nbits) & 0xFF)
    return bytes(out)


# ---------------------------------------------------------------------------
# base64
# ---------------------------------------------------------------------------

def b64_encode(data, urlsafe=False, pad=True):
    if type(data) is not bytes:
        raise CodecError("type", -1)
    alphabet = URL_ALPHABET if urlsafe else STD_ALPHABET
    return _encode_generic(data, alphabet, 6, 4, pad)


def b64_decode(text, urlsafe=False, pad=True):
    if type(text) is not str:
        raise CodecError("type", -1)
    alphabet = URL_ALPHABET if urlsafe else STD_ALPHABET
    _decode_core(
        text, alphabet, unit_bits=6, group_len=4, pad=pad,
        valid_pad_runs={1, 2}, bits_map={2: 4, 3: 2}, bad_len_mod={1},
    )
    data_chars = [c for c in text if c != "="]
    return _bits_to_bytes(data_chars, alphabet, 6)


# ---------------------------------------------------------------------------
# base32
# ---------------------------------------------------------------------------

def b32_encode(data, pad=True):
    if type(data) is not bytes:
        raise CodecError("type", -1)
    return _encode_generic(data, B32_ALPHABET, 5, 8, pad)


def b32_decode(text, pad=True):
    if type(text) is not str:
        raise CodecError("type", -1)
    _decode_core(
        text, B32_ALPHABET, unit_bits=5, group_len=8, pad=pad,
        valid_pad_runs={6, 4, 3, 1}, bits_map={2: 2, 4: 4, 5: 1, 7: 3},
        bad_len_mod={1, 3, 6},
    )
    data_chars = [c for c in text if c != "="]
    return _bits_to_bytes(data_chars, B32_ALPHABET, 5)


# ---------------------------------------------------------------------------
# quoted-printable
# ---------------------------------------------------------------------------

def _hex2(b):
    return _HEXCHARS[(b >> 4) & 0xF] + _HEXCHARS[b & 0xF]


def _hexval(c):
    return _HEXCHARS.index(c)


def qp_encode(data):
    if type(data) is not bytes:
        raise CodecError("type", -1)
    lines = []
    line = ""
    n = len(data)
    for i in range(n):
        b = data[i]
        if b == 0x20 or b == 0x09:
            if i != n - 1:
                unit = chr(b)
            else:
                unit = "=20" if b == 0x20 else "=09"
        elif 33 <= b <= 126 and b != 0x3D:
            unit = chr(b)
        else:
            unit = "=" + _hex2(b)

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


def _split_lines(text):
    """Split text at CRLF pairs, returning (start_offset, segment, had_crlf)."""
    segments = []
    n = len(text)
    start = 0
    i = 0
    while i < n:
        if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
            segments.append((start, text[start:i], True))
            i += 2
            start = i
        else:
            i += 1
    segments.append((start, text[start:], False))
    return segments


def qp_decode(text):
    if type(text) is not str:
        raise CodecError("type", -1)

    n = len(text)

    violations = []

    # rule i: character-level allowed-set check
    for i in range(n):
        c = text[i]
        code = ord(c)
        allowed = (33 <= code <= 126) or c == " " or c == "\t" or c == "\r" or c == "\n"
        if not allowed:
            violations.append((i, 1, "char"))

    # rule ii: CR/LF pairing
    for i in range(n):
        c = text[i]
        if c == "\r":
            if i + 1 >= n or text[i + 1] != "\n":
                violations.append((i, 2, "eol"))
        elif c == "\n":
            if i - 1 < 0 or text[i - 1] != "\r":
                violations.append((i, 2, "eol"))

    # rules iii/iv/v: '=' handling
    for i in range(n):
        if text[i] != "=":
            continue
        remaining = n - 1 - i
        if remaining == 0 or remaining == 1:
            violations.append((i, 3, "trunc"))
            continue
        c1 = text[i + 1]
        c2 = text[i + 2]
        if c1 == "\r" and c2 == "\n":
            if i + 3 >= n:
                violations.append((i, 4, "eol"))
            # else: valid soft break, no violation
        else:
            if c1 not in _HEXDIGITS:
                violations.append((i + 1, 5, "hex"))
            elif c2 not in _HEXDIGITS:
                violations.append((i + 2, 5, "hex"))

    if violations:
        violations.sort(key=lambda t: (t[0], t[1]))
        _, _, kind = violations[0]
        pos = violations[0][0]
        raise CodecError(kind, pos)

    # step 3: line length
    segments = _split_lines(text)
    for start, seg, had_crlf in segments:
        if had_crlf and seg.endswith("="):
            content = seg[:-1]
        else:
            content = seg
        if len(content) > 75:
            raise CodecError("length", start + 75)

    # step 4: trailing whitespace
    for start, seg, had_crlf in segments:
        if had_crlf and seg.endswith("="):
            content = seg[:-1]
        else:
            content = seg
        if len(content) > 0 and (content[-1] == " " or content[-1] == "\t"):
            raise CodecError("trailws", start + len(content) - 1)

    # decode
    out = bytearray()
    i = 0
    while i < n:
        c = text[i]
        if c == "=":
            if text[i + 1] == "\r" and text[i + 2] == "\n":
                i += 3
                continue
            else:
                v = _hexval(text[i + 1]) * 16 + _hexval(text[i + 2])
                out.append(v)
                i += 3
                continue
        elif c == "\r":
            out.append(0x0D)
            out.append(0x0A)
            i += 2
            continue
        else:
            out.append(ord(c))
            i += 1
    return bytes(out)
