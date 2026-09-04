"""Strict binary-to-text codecs: base64, base32, binary quoted-printable.

Standard library only (and not even much of that): plain arithmetic and
string/list indexing implement the actual codec logic.
"""

WHITESPACE = " \t\n\r\f\v"

_STD64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_URL64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
_B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_HEXDIGITS = "0123456789ABCDEF"


class CodecError(ValueError):
    def __init__(self, kind, pos):
        ValueError.__init__(self, "%s error at %d" % (kind, pos))
        self.kind = kind
        self.pos = pos


# --------------------------------------------------------------------------
# base64
# --------------------------------------------------------------------------

def b64_encode(data, urlsafe=False, pad=True):
    if type(data) is not bytes:
        raise CodecError("type", -1)
    alphabet = _URL64 if urlsafe else _STD64
    bits = 0
    nbits = 0
    out = []
    for b in data:
        bits = (bits << 8) | b
        nbits += 8
        while nbits >= 6:
            nbits -= 6
            idx = (bits >> nbits) & 0x3F
            out.append(alphabet[idx])
        bits &= (1 << nbits) - 1 if nbits else 0
    if nbits > 0:
        idx = (bits << (6 - nbits)) & 0x3F
        out.append(alphabet[idx])
    s = "".join(out)
    if pad:
        rem = len(s) % 4
        if rem:
            s += "=" * (4 - rem)
    return s


def b64_decode(text, urlsafe=False, pad=True):
    if type(text) is not str:
        raise CodecError("type", -1)
    alphabet = _URL64 if urlsafe else _STD64
    n = len(text)

    # step 2: alphabet scan
    for i in range(n):
        c = text[i]
        if c in alphabet or c == "=":
            continue
        if c in WHITESPACE:
            raise CodecError("whitespace", i)
        raise CodecError("alphabet", i)

    # step 3: padding
    if not pad:
        for i in range(n):
            if text[i] == "=":
                raise CodecError("padding", i)
    else:
        j = n
        while j > 0 and text[j - 1] == "=":
            j -= 1
        run_len = n - j
        if run_len in (1, 2):
            for i in range(j):
                if text[i] == "=":
                    raise CodecError("padding", i)
        else:
            for i in range(n):
                if text[i] == "=":
                    raise CodecError("padding", i)

    # step 4: length
    if pad:
        if n % 4 != 0:
            raise CodecError("length", n)
    else:
        if n % 4 == 1:
            raise CodecError("length", n)

    # step 5: leftover bits
    data_positions = [i for i in range(n) if text[i] != "="]
    m = len(data_positions) % 4
    if m == 2 or m == 3:
        last_idx = data_positions[-1]
        last_val = alphabet.index(text[last_idx])
        if m == 2:
            if last_val & 0xF != 0:
                raise CodecError("bits", last_idx)
        else:
            if last_val & 0x3 != 0:
                raise CodecError("bits", last_idx)

    # decode
    bits = 0
    nbits = 0
    out = bytearray()
    for i in data_positions:
        val = alphabet.index(text[i])
        bits = (bits << 6) | val
        nbits += 6
        if nbits >= 8:
            nbits -= 8
            out.append((bits >> nbits) & 0xFF)
            bits &= (1 << nbits) - 1 if nbits else 0
    return bytes(out)


# --------------------------------------------------------------------------
# base32
# --------------------------------------------------------------------------

def b32_encode(data, pad=True):
    if type(data) is not bytes:
        raise CodecError("type", -1)
    bits = 0
    nbits = 0
    out = []
    for b in data:
        bits = (bits << 8) | b
        nbits += 8
        while nbits >= 5:
            nbits -= 5
            idx = (bits >> nbits) & 0x1F
            out.append(_B32[idx])
        bits &= (1 << nbits) - 1 if nbits else 0
    if nbits > 0:
        idx = (bits << (5 - nbits)) & 0x1F
        out.append(_B32[idx])
    s = "".join(out)
    if pad:
        rem = len(s) % 8
        if rem:
            s += "=" * (8 - rem)
    return s


def b32_decode(text, pad=True):
    if type(text) is not str:
        raise CodecError("type", -1)
    alphabet = _B32
    n = len(text)

    # step 2: alphabet scan
    for i in range(n):
        c = text[i]
        if c in alphabet or c == "=":
            continue
        if c in WHITESPACE:
            raise CodecError("whitespace", i)
        raise CodecError("alphabet", i)

    # step 3: padding
    if not pad:
        for i in range(n):
            if text[i] == "=":
                raise CodecError("padding", i)
    else:
        j = n
        while j > 0 and text[j - 1] == "=":
            j -= 1
        run_len = n - j
        if run_len in (6, 4, 3, 1):
            for i in range(j):
                if text[i] == "=":
                    raise CodecError("padding", i)
        else:
            for i in range(n):
                if text[i] == "=":
                    raise CodecError("padding", i)

    # step 4: length
    if pad:
        if n % 8 != 0:
            raise CodecError("length", n)
    else:
        if n % 8 in (1, 3, 6):
            raise CodecError("length", n)

    # step 5: leftover bits
    data_positions = [i for i in range(n) if text[i] != "="]
    m = len(data_positions) % 8
    check_bits = {2: 2, 4: 4, 5: 1, 7: 3}
    if m in check_bits:
        nb = check_bits[m]
        last_idx = data_positions[-1]
        last_val = alphabet.index(text[last_idx])
        mask = (1 << nb) - 1
        if last_val & mask != 0:
            raise CodecError("bits", last_idx)

    # decode
    bits = 0
    nbits = 0
    out = bytearray()
    for i in data_positions:
        val = alphabet.index(text[i])
        bits = (bits << 5) | val
        nbits += 5
        if nbits >= 8:
            nbits -= 8
            out.append((bits >> nbits) & 0xFF)
            bits &= (1 << nbits) - 1 if nbits else 0
    return bytes(out)


# --------------------------------------------------------------------------
# quoted-printable
# --------------------------------------------------------------------------

def _two_hex_digits(b):
    return _HEXDIGITS[(b >> 4) & 0xF] + _HEXDIGITS[b & 0xF]


def qp_encode(data):
    if type(data) is not bytes:
        raise CodecError("type", -1)
    lines = []
    line = ""
    n = len(data)
    for i in range(n):
        b = data[i]
        if b == 0x20 or b == 0x09:
            unit = chr(b) if i != n - 1 else ("=20" if b == 0x20 else "=09")
        elif 33 <= b <= 126 and b != 0x3D:
            unit = chr(b)
        else:
            unit = "=" + _two_hex_digits(b)
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


def _is_hexdigit(c):
    return c in _HEXDIGITS


def _hexval(c):
    return _HEXDIGITS.index(c)


def _qp_find_char(text):
    for i in range(len(text)):
        c = text[i]
        o = ord(c)
        if (33 <= o <= 126) or c == " " or c == "\t" or c == "\r" or c == "\n":
            continue
        return i
    return None


def _qp_find_eol(text):
    n = len(text)
    for i in range(n):
        c = text[i]
        if c == "\r":
            if i + 1 >= n or text[i + 1] != "\n":
                return i
        elif c == "\n":
            if i == 0 or text[i - 1] != "\r":
                return i
    return None


def _qp_find_trunc(text):
    n = len(text)
    for i in range(n):
        if text[i] == "=":
            remaining = n - i - 1
            if remaining == 0 or remaining == 1:
                return i
    return None


def _qp_find_eol_end(text):
    n = len(text)
    for i in range(n):
        if text[i] == "=":
            remaining = n - i - 1
            if remaining == 2 and text[i + 1] == "\r" and text[i + 2] == "\n":
                if i + 3 == n:
                    return i
    return None


def _qp_find_hex(text):
    n = len(text)
    for i in range(n):
        if text[i] == "=":
            remaining = n - i - 1
            if remaining <= 1:
                continue
            if text[i + 1] == "\r" and text[i + 2] == "\n":
                continue
            if not _is_hexdigit(text[i + 1]):
                return i + 1
            if not _is_hexdigit(text[i + 2]):
                return i + 2
    return None


def _qp_split_lines(text):
    n = len(text)
    lines = []
    start = 0
    i = 0
    while i < n:
        if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
            lines.append((start, text[start:i]))
            i += 2
            start = i
            continue
        i += 1
    lines.append((start, text[start:n]))
    return lines


def qp_decode(text):
    if type(text) is not str:
        raise CodecError("type", -1)
    n = len(text)

    candidates = []
    pos = _qp_find_char(text)
    if pos is not None:
        candidates.append((pos, 1, "char"))
    pos = _qp_find_eol(text)
    if pos is not None:
        candidates.append((pos, 2, "eol"))
    pos = _qp_find_trunc(text)
    if pos is not None:
        candidates.append((pos, 3, "trunc"))
    pos = _qp_find_eol_end(text)
    if pos is not None:
        candidates.append((pos, 4, "eol"))
    pos = _qp_find_hex(text)
    if pos is not None:
        candidates.append((pos, 5, "hex"))
    if candidates:
        candidates.sort(key=lambda t: (t[0], t[1]))
        offset, _prio, kind = candidates[0]
        raise CodecError(kind, offset)

    lines = _qp_split_lines(text)

    for soff, seg in lines:
        content = seg[:-1] if seg.endswith("=") else seg
        if len(content) > 75:
            raise CodecError("length", soff + 75)

    for soff, seg in lines:
        content = seg[:-1] if seg.endswith("=") else seg
        if content.endswith(" ") or content.endswith("\t"):
            raise CodecError("trailws", soff + len(content) - 1)

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
