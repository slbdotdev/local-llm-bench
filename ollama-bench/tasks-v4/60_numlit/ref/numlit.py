"""numlit -- a numeric literal scanner and a fixed-point number formatter."""

import math

_DEC = "0123456789"
_CHARSET = set("0123456789abcdefghijklmnopqrstuvwxyz"
               "ABCDEFGHIJKLMNOPQRSTUVWXYZ_.+-")
_RADIX_PREFIX = {"x": 16, "o": 8, "b": 2}
_RADIX_CHARS = {16: "0123456789abcdef", 8: "01234567", 2: "01", 10: _DEC}
_HEXCHARS = "0123456789abcdef"
_VALS = {}
for _i in range(len(_HEXCHARS)):
    _VALS[_HEXCHARS[_i]] = _i


class NumError(ValueError):
    """Raised for a bad literal or a bad format spec."""

    def __init__(self, kind, pos):
        ValueError.__init__(self, kind + " at " + str(pos))
        self.kind = kind
        self.pos = pos


def _digits_to_int(digits, radix):
    v = 0
    for ch in digits:
        v = v * radix + _VALS[ch.lower()]
    return v


def _strip_us(s):
    out = []
    for ch in s:
        if ch != "_":
            out.append(ch)
    return "".join(out)


def _strip_zeros(s):
    i = 0
    while i < len(s) - 1 and s[i] == "0":
        i += 1
    return s[i:]


def _isdig(ch):
    return ch in _DEC or ch in "abcdefABCDEF"


def _bad_underscore(run, base):
    """Offset of the leftmost underscore in run not strictly between digits."""
    for k in range(len(run)):
        if run[k] != "_":
            continue
        if k == 0 or k == len(run) - 1:
            return base + k
        if not _isdig(run[k - 1]) or not _isdig(run[k + 1]):
            return base + k
    return -1


def scan(text):
    n = len(text)
    if n == 0:
        return []
    if text[0] == " ":
        raise NumError("space", 0)
    for i in range(1, n):
        if text[i] == " " and text[i - 1] == " ":
            raise NumError("space", i)
    if text[n - 1] == " ":
        raise NumError("space", n - 1)
    out = []
    p = 0
    while p < n:
        q = p
        while q < n and text[q] != " ":
            q += 1
        out.append(_field(text, p, q))
        p = q + 1
    return out


def _field(text, p0, end):
    for i in range(p0, end):
        if text[i] not in _CHARSET:
            raise NumError("char", i)
    i = p0
    neg = False
    if text[i] == "+" or text[i] == "-":
        neg = text[i] == "-"
        i += 1
    if i >= end:
        raise NumError("sign", p0)
    b0 = i
    b1 = end
    suffix = ""
    if text[b1 - 1] in "uls":
        suffix = text[b1 - 1]
        b1 -= 1
        if b1 == b0:
            raise NumError("suffix", b1)
    body = text[b0:b1]
    L = len(body)
    radix = 10
    runs = []
    has_dot = False
    dotpos = -1
    has_exp = False
    epos = -1
    esign = 1
    ipart = ""
    fpart = ""
    epart = ""
    rdigits = ""
    if L >= 2 and body[0] == "0" and body[1] in "XOB":
        raise NumError("prefix", b0 + 1)
    if L >= 2 and body[0] == "0" and body[1] in "xob":
        radix = _RADIX_PREFIX[body[1]]
        rdigits = body[2:]
        if rdigits == "":
            raise NumError("prefix", b0 + 2)
        allowed = _RADIX_CHARS[radix]
        for k in range(len(rdigits)):
            ch = rdigits[k]
            if ch != "_" and ch.lower() not in allowed:
                raise NumError("digit", b0 + 2 + k)
        runs.append((rdigits, b0 + 2))
    else:
        j = 0
        while j < L and (body[j] in _DEC or body[j] == "_"):
            j += 1
        ipart = body[0:j]
        runs.append((ipart, b0))
        if j < L and body[j] == ".":
            has_dot = True
            dotpos = j
            j += 1
            fs = j
            while j < L and (body[j] in _DEC or body[j] == "_"):
                j += 1
            fpart = body[fs:j]
            runs.append((fpart, b0 + fs))
        if j < L and (body[j] == "e" or body[j] == "E"):
            has_exp = True
            epos = j
            j += 1
            if j < L and (body[j] == "+" or body[j] == "-"):
                if body[j] == "-":
                    esign = -1
                j += 1
            es = j
            while j < L and (body[j] in _DEC or body[j] == "_"):
                j += 1
            epart = body[es:j]
            runs.append((epart, b0 + es))
        if j < L:
            raise NumError("syntax", b0 + j)
    for run, base in runs:
        bad = _bad_underscore(run, base)
        if bad >= 0:
            raise NumError("underscore", bad)
    if has_dot and fpart == "":
        raise NumError("dangling_dot", b0 + dotpos)
    if has_exp and epart == "":
        raise NumError("exponent", b0 + epos)
    idigits = _strip_us(ipart)
    if radix == 10 and len(idigits) >= 2 and idigits[0] == "0":
        raise NumError("leading_zero", b0)
    is_float = has_dot or has_exp
    if is_float and (suffix == "u" or suffix == "l"):
        raise NumError("suffix", b1)
    if (not is_float) and suffix == "s":
        raise NumError("suffix", b1)
    if is_float:
        fdigits = _strip_us(fpart)
        edigits = _strip_us(epart)
        head = idigits
        if head == "":
            head = "0"
        m = _digits_to_int(head + fdigits, 10)
        expv = 0
        if has_exp:
            expv = esign * _digits_to_int(edigits, 10)
        e = expv - len(fdigits)
        if e >= 0:
            mag = m * (10.0 ** e)
        else:
            mag = m / (10.0 ** (-e))
        value = -mag if neg else mag
        txt = "-" if neg else ""
        txt = txt + (idigits if idigits else "0") + "."
        txt = txt + (fdigits if has_dot else "0")
        if has_exp:
            txt = txt + "e"
            if expv < 0:
                txt = txt + "-"
            txt = txt + _strip_zeros(edigits)
        kind = "float"
    else:
        if radix == 10:
            digs = idigits
        else:
            digs = _strip_us(rdigits)
        value = _digits_to_int(digs, radix)
        if neg:
            value = -value
        if radix == 10:
            txt = ("-" if value < 0 else "") + digs
        else:
            pre = "0x" if radix == 16 else ("0o" if radix == 8 else "0b")
            txt = ("-" if value < 0 else "") + pre + _strip_zeros(digs.lower())
        kind = "int"
    rec = {}
    rec["kind"] = kind
    rec["radix"] = radix
    rec["value"] = value
    rec["text"] = txt
    rec["suffix"] = suffix
    rec["start"] = p0
    return rec


_ALIGNS = "<>^"
_SIGNS = "+- "
_MODES = "hudf"


def _parse_spec(spec):
    n = len(spec)
    fill = " "
    align = ">"
    i = 0
    if n >= 2 and spec[1] in _ALIGNS:
        fill = spec[0]
        align = spec[1]
        i = 2
    elif n >= 1 and spec[0] in _ALIGNS:
        align = spec[0]
        i = 1
    sign = "-"
    if i < n and spec[i] in _SIGNS:
        sign = spec[i]
        i += 1
    group = False
    if i < n and spec[i] == ",":
        group = True
        i += 1
    width = 0
    s = i
    while i < n and spec[i] in _DEC:
        i += 1
    if i > s:
        if spec[s] == "0":
            raise NumError("spec", -1)
        width = _digits_to_int(spec[s:i], 10)
        if width > 200:
            raise NumError("spec", -1)
    prec = 0
    if i < n and spec[i] == ".":
        i += 1
        s = i
        while i < n and spec[i] in _DEC:
            i += 1
        if i == s:
            raise NumError("spec", -1)
        prec = _digits_to_int(spec[s:i], 10)
        if prec > 20:
            raise NumError("spec", -1)
    mode = "h"
    if i < n:
        if spec[i] not in _MODES:
            raise NumError("spec", -1)
        mode = spec[i]
        i += 1
    if i != n:
        raise NumError("spec", -1)
    return fill, align, sign, group, prec, width, mode


def _group3(s):
    out = []
    k = len(s)
    while k > 3:
        out.append(s[k - 3:k])
        k -= 3
    out.append(s[0:k])
    out.reverse()
    return ",".join(out)


def format_number(value, spec):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NumError("type", -1)
    if not isinstance(spec, str):
        raise NumError("type", -1)
    if isinstance(value, float) and not math.isfinite(value):
        raise NumError("nonfinite", -1)
    fill, align, sign, group, prec, width, mode = _parse_spec(spec)
    if isinstance(value, float):
        num, den = value.as_integer_ratio()
        negval = math.copysign(1.0, value) < 0
    else:
        num, den = value, 1
        negval = value < 0
    scaled = num * (10 ** prec)
    q = scaled // den
    r = scaled - q * den
    if mode == "f":
        rounded = q
    elif mode == "d":
        rounded = q if (scaled >= 0 or r == 0) else q + 1
    else:
        twice = 2 * r
        if twice > den:
            rounded = q + 1
        elif twice < den:
            rounded = q
        elif mode == "u":
            rounded = q + 1 if scaled > 0 else q
        else:
            rounded = q if q % 2 == 0 else q + 1
    mag = -rounded if rounded < 0 else rounded
    s = str(mag)
    if len(s) <= prec:
        s = "0" * (prec + 1 - len(s)) + s
    ipart = s[0:len(s) - prec] if prec else s
    fpart = s[len(s) - prec:] if prec else ""
    if group:
        ipart = _group3(ipart)
    neg = negval or rounded < 0
    if neg:
        head = "-"
    elif sign == "+":
        head = "+"
    elif sign == " ":
        head = " "
    else:
        head = ""
    body = head + ipart + ("." + fpart if prec else "")
    pad = width - len(body)
    if pad <= 0:
        return body
    if align == "<":
        return body + fill * pad
    if align == ">":
        return fill * pad + body
    left = pad // 2
    return fill * left + body + fill * (pad - left)
