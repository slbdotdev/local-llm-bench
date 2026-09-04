"""Strict binary-to-text codecs: base64, base32, binary quoted-printable.

Standard library only, no banned modules/functions. See TASK.md for the
full specification.
"""

STD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
URL_ALPHABET = STD_ALPHABET[:-2] + "-_"
B32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

HEXDIGITS = "0123456789ABCDEF"
HEXVAL = {c: i for i, c in enumerate(HEXDIGITS)}
HEXCHARS = set(HEXDIGITS)

WHITESPACE = set(" \t\n\r\f\v")


class CodecError(ValueError):
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__("%s at %d" % (kind, pos))


# ---------------------------------------------------------------------------
# base64
# ---------------------------------------------------------------------------

def b64_encode(data, urlsafe=False, pad=True):
    if type(data) is not bytes:
        raise CodecError("type", -1)
    alphabet = URL_ALPHABET if urlsafe else STD_ALPHABET
    bits = 0
    nbits = 0
    out = []
    for b in data:
        bits = (bits << 8) | b
        nbits += 8
        while nbits >= 6:
            nbits -= 6
            out.append(alphabet[(bits >> nbits) & 0x3F])
    if nbits > 0:
        out.append(alphabet[(bits << (6 - nbits)) & 0x3F])
    s = "".join(out)
    if pad:
        rem = len(s) % 4
        if rem:
            s += "=" * (4 - rem)
    return s


def b64_decode(text, urlsafe=False, pad=True):
    if type(text) is not str:
        raise CodecError("type", -1)
    alphabet = URL_ALPHABET if urlsafe else STD_ALPHABET
    alpha_set = set(alphabet)
    rev = {c: i for i, c in enumerate(alphabet)}

    # Step 2: alphabet scan
    for i, ch in enumerate(text):
        if ch in alpha_set or ch == "=":
            continue
        if ch in WHITESPACE:
            raise CodecError("whitespace", i)
        raise CodecError("alphabet", i)

    n = len(text)

    # Step 3: padding
    run_len = 0
    j = n - 1
    while j >= 0 and text[j] == "=":
        run_len += 1
        j -= 1
    run_start = n - run_len
    valid_run = pad and run_len in (1, 2)
    for i, ch in enumerate(text):
        if ch == "=":
            if valid_run and i >= run_start:
                continue
            raise CodecError("padding", i)

    # Step 4: length
    if pad:
        if n % 4 != 0:
            raise CodecError("length", n)
    else:
        if n % 4 == 1:
            raise CodecError("length", n)

    # Step 5: leftover bits
    data_positions = [i for i, ch in enumerate(text) if ch != "="]
    ndata = len(data_positions)
    rem = ndata % 4
    if rem == 2 or rem == 3:
        last_pos = data_positions[-1]
        val = rev[text[last_pos]]
        mask = 0xF if rem == 2 else 0x3
        if val & mask != 0:
            raise CodecError("bits", last_pos)

    # Decode
    bits = 0
    nbits = 0
    out = bytearray()
    for i in data_positions:
        val = rev[text[i]]
        bits = (bits << 6) | val
        nbits += 6
        if nbits >= 8:
            nbits -= 8
            out.append((bits >> nbits) & 0xFF)
    return bytes(out)


# ---------------------------------------------------------------------------
# base32
# ---------------------------------------------------------------------------

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
            out.append(B32_ALPHABET[(bits >> nbits) & 0x1F])
    if nbits > 0:
        out.append(B32_ALPHABET[(bits << (5 - nbits)) & 0x1F])
    s = "".join(out)
    if pad:
        rem = len(s) % 8
        if rem:
            s += "=" * (8 - rem)
    return s


def b32_decode(text, pad=True):
    if type(text) is not str:
        raise CodecError("type", -1)
    alpha_set = set(B32_ALPHABET)
    rev = {c: i for i, c in enumerate(B32_ALPHABET)}

    # Step 2: alphabet scan
    for i, ch in enumerate(text):
        if ch in alpha_set or ch == "=":
            continue
        if ch in WHITESPACE:
            raise CodecError("whitespace", i)
        raise CodecError("alphabet", i)

    n = len(text)

    # Step 3: padding
    run_len = 0
    j = n - 1
    while j >= 0 and text[j] == "=":
        run_len += 1
        j -= 1
    run_start = n - run_len
    valid_run = pad and run_len in (6, 4, 3, 1)
    for i, ch in enumerate(text):
        if ch == "=":
            if valid_run and i >= run_start:
                continue
            raise CodecError("padding", i)

    # Step 4: length
    if pad:
        if n % 8 != 0:
            raise CodecError("length", n)
    else:
        if n % 8 in (1, 3, 6):
            raise CodecError("length", n)

    # Step 5: leftover bits
    data_positions = [i for i, ch in enumerate(text) if ch != "="]
    ndata = len(data_positions)
    rem = ndata % 8
    bits_map = {2: 2, 4: 4, 5: 1, 7: 3}
    if rem in bits_map:
        last_pos = data_positions[-1]
        val = rev[text[last_pos]]
        mask = (1 << bits_map[rem]) - 1
        if val & mask != 0:
            raise CodecError("bits", last_pos)

    # Decode
    bits = 0
    nbits = 0
    out = bytearray()
    for i in data_positions:
        val = rev[text[i]]
        bits = (bits << 5) | val
        nbits += 5
        if nbits >= 8:
            nbits -= 8
            out.append((bits >> nbits) & 0xFF)
    return bytes(out)


# ---------------------------------------------------------------------------
# quoted-printable
# ---------------------------------------------------------------------------

def _qp_hex2(b):
    return HEXDIGITS[(b >> 4) & 0xF] + HEXDIGITS[b & 0xF]


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
            unit = "=" + _qp_hex2(b)

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
    if type(text) is not str:
        raise CodecError("type", -1)

    n = len(text)
    allowed = set(chr(x) for x in range(33, 127)) | {" ", "\t", "\r", "\n"}

    best = None  # (offset, rule_index, kind)

    def consider(offset, rule_index, kind):
        nonlocal best
        if best is None or (offset, rule_index) < (best[0], best[1]):
            best = (offset, rule_index, kind)

    # Rule 1: character-level validity
    for i in range(n):
        if text[i] not in allowed:
            consider(i, 1, "char")

    # Rule 2: CR/LF pairing
    for i in range(n):
        c = text[i]
        if c == "\r":
            if i + 1 >= n or text[i + 1] != "\n":
                consider(i, 2, "eol")
        elif c == "\n":
            if i - 1 < 0 or text[i - 1] != "\r":
                consider(i, 2, "eol")

    # Rules 3, 4, 5: '=' escapes
    for i in range(n):
        if text[i] != "=":
            continue
        remaining = n - i - 1
        if remaining == 0 or remaining == 1:
            consider(i, 3, "trunc")
            continue
        if text[i + 1] == "\r" and text[i + 2] == "\n":
            if i + 3 >= n:
                consider(i, 4, "eol")
            continue
        h1 = text[i + 1]
        if h1 not in HEXCHARS:
            consider(i + 1, 5, "hex")
            continue
        h2 = text[i + 2]
        if h2 not in HEXCHARS:
            consider(i + 2, 5, "hex")
            continue

    if best is not None:
        raise CodecError(best[2], best[0])

    # Split into lines at every CR LF
    lines = []
    start = 0
    i = 0
    while i < n:
        if text[i] == "\r" and i + 1 < n and text[i + 1] == "\n":
            lines.append((start, i))
            i += 2
            start = i
        else:
            i += 1
    lines.append((start, n))

    contents = []
    for (s, e) in lines:
        raw = text[s:e]
        if raw.endswith("="):
            content = raw[:-1]
        else:
            content = raw
        contents.append((s, content))

    # Step 3: line length
    for (s, content) in contents:
        if len(content) > 75:
            raise CodecError("length", s + 75)

    # Step 4: trailing whitespace
    for (s, content) in contents:
        if len(content) > 0 and content[-1] in (" ", "\t"):
            raise CodecError("trailws", s + len(content) - 1)

    # Decode
    out = bytearray()
    i = 0
    while i < n:
        c = text[i]
        if c == "=":
            if text[i + 1] == "\r" and text[i + 2] == "\n":
                i += 3
                continue
            val = HEXVAL[text[i + 1]] * 16 + HEXVAL[text[i + 2]]
            out.append(val)
            i += 3
            continue
        if c == "\r":
            out.append(0x0D)
            out.append(0x0A)
            i += 2
            continue
        out.append(ord(c))
        i += 1
    return bytes(out)
