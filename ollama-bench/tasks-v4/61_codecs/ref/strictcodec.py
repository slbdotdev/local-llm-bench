"""strictcodec.py -- strict base64 / base32 / quoted-printable codecs (stdlib only)."""

_B64_STD = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_B64_URL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
_B32_A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_WS = " \t\n\r\f\v"
_HEXD = "0123456789ABCDEF"


class CodecError(ValueError):
    def __init__(self, kind, pos):
        ValueError.__init__(self, "%s error at %d" % (kind, pos))
        self.kind = kind
        self.pos = pos


# ---------------------------------------------------------------- helpers
def _encode_bits(data, alpha, bpc, group, pad):
    out = []
    acc = 0
    nbits = 0
    for b in data:
        acc = (acc << 8) | b
        nbits += 8
        while nbits >= bpc:
            nbits -= bpc
            out.append(alpha[(acc >> nbits) & ((1 << bpc) - 1)])
        acc &= (1 << nbits) - 1
    if nbits:
        out.append(alpha[(acc << (bpc - nbits)) & ((1 << bpc) - 1)])
    if pad:
        while len(out) % group:
            out.append("=")
    return "".join(out)


def _decode_bits(text, alpha, bpc, group, pad, ok_runs, bad_mods, zbits):
    if type(text) is not str:
        raise CodecError("type", -1)
    aset = set(alpha)
    for i in range(len(text)):
        ch = text[i]
        if ch in aset or ch == "=":
            continue
        raise CodecError("whitespace" if ch in _WS else "alphabet", i)
    n = len(text)
    run = 0
    while run < n and text[n - 1 - run] == "=":
        run += 1
    allowed_from = n - run if (pad and run in ok_runs) else n
    for i in range(allowed_from):
        if text[i] == "=":
            raise CodecError("padding", i)
    if pad:
        if n % group != 0:
            raise CodecError("length", n)
    else:
        if n % group in bad_mods:
            raise CodecError("length", n)
    dlen = n - run
    g = dlen % group
    if g in zbits:
        val = alpha.index(text[dlen - 1])
        if val & ((1 << zbits[g]) - 1):
            raise CodecError("bits", dlen - 1)
    out = bytearray()
    acc = 0
    nbits = 0
    for i in range(dlen):
        acc = (acc << bpc) | alpha.index(text[i])
        nbits += bpc
        while nbits >= 8:
            nbits -= 8
            out.append((acc >> nbits) & 255)
        acc &= (1 << nbits) - 1
    return bytes(out)


# ---------------------------------------------------------------- base64
def b64_encode(data, urlsafe=False, pad=True):
    if type(data) is not bytes:
        raise CodecError("type", -1)
    return _encode_bits(data, _B64_URL if urlsafe else _B64_STD, 6, 4, pad)


def b64_decode(text, urlsafe=False, pad=True):
    return _decode_bits(text, _B64_URL if urlsafe else _B64_STD, 6, 4, pad,
                        (1, 2), (1,), {2: 4, 3: 2})


# ---------------------------------------------------------------- base32
def b32_encode(data, pad=True):
    if type(data) is not bytes:
        raise CodecError("type", -1)
    return _encode_bits(data, _B32_A, 5, 8, pad)


def b32_decode(text, pad=True):
    return _decode_bits(text, _B32_A, 5, 8, pad,
                        (6, 4, 3, 1), (1, 3, 6), {2: 2, 4: 4, 5: 1, 7: 3})


# ------------------------------------------------------- quoted-printable
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
                unit = " " if b == 0x20 else "\t"
            else:
                unit = "=20" if b == 0x20 else "=09"
        elif 33 <= b <= 126 and b != 0x3D:
            unit = chr(b)
        else:
            unit = "=" + _HEXD[b >> 4] + _HEXD[b & 15]
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


def _qp_scan(text):
    n = len(text)
    best = None
    for i in range(n):
        ch = text[i]
        o = ord(ch)
        cand = None
        if not (33 <= o <= 126 or ch == " " or ch == "\t" or ch == "\r" or ch == "\n"):
            cand = (i, 0, "char")
        elif ch == "\r":
            if i + 1 >= n or text[i + 1] != "\n":
                cand = (i, 1, "eol")
        elif ch == "\n":
            if i == 0 or text[i - 1] != "\r":
                cand = (i, 1, "eol")
        elif ch == "=":
            if n - i - 1 <= 1:
                cand = (i, 2, "trunc")
            elif text[i + 1] == "\r" and text[i + 2] == "\n":
                if i + 3 == n:
                    cand = (i, 3, "eol")
            elif text[i + 1] not in _HEXD:
                cand = (i + 1, 4, "hex")
            elif text[i + 2] not in _HEXD:
                cand = (i + 2, 4, "hex")
        if cand is not None:
            if best is None or (cand[0], cand[1]) < (best[0], best[1]):
                best = cand
    return best


def _qp_lines(text):
    segs = []
    pos = 0
    while True:
        j = text.find("\r\n", pos)
        if j < 0:
            segs.append((pos, text[pos:]))
            return segs
        seg = text[pos:j]
        if seg[-1:] == "=":
            seg = seg[:-1]
        segs.append((pos, seg))
        pos = j + 2


def qp_decode(text):
    if type(text) is not str:
        raise CodecError("type", -1)
    bad = _qp_scan(text)
    if bad is not None:
        raise CodecError(bad[2], bad[0])
    segs = _qp_lines(text)
    for start, seg in segs:
        if len(seg) > 75:
            raise CodecError("length", start + 75)
    for start, seg in segs:
        if seg[-1:] == " " or seg[-1:] == "\t":
            raise CodecError("trailws", start + len(seg) - 1)
    out = bytearray()
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "=":
            if text[i + 1] == "\r":
                i += 3
            else:
                out.append(_HEXD.index(text[i + 1]) * 16 + _HEXD.index(text[i + 2]))
                i += 3
        elif ch == "\r":
            out.append(13)
            out.append(10)
            i += 2
        else:
            out.append(ord(ch))
            i += 1
    return bytes(out)
