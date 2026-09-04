"""numlit.py -- scan numeric literals out of text and format numbers as
fixed-point decimals.

Standard library only (uses only ``math``); no filesystem or network access.
"""

import math


class NumError(ValueError):
    """Raised for any rejection.  ``.kind`` is a short string tag,
    ``.pos`` is the absolute offset of the offence (-1 for format_number
    errors, which are not tied to a source offset)."""

    def __init__(self, kind, pos):
        super().__init__(kind)
        self.kind = kind
        self.pos = pos


# ---------------------------------------------------------------------------
# helpers that avoid ever *calling* int()/float()

_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"
DIGIT_VAL = {}
for _i, _c in enumerate(_ALPHABET):
    DIGIT_VAL[_c] = _i


def _digits_to_int(s, base):
    v = 0
    for ch in s:
        v = v * base + DIGIT_VAL[ch.lower()]
    return v


_CHARSET = set("0123456789")
for _c in "abcdefghijklmnopqrstuvwxyz":
    _CHARSET.add(_c)
for _c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    _CHARSET.add(_c)
for _c in "_.+-":
    _CHARSET.add(_c)

_DEC_RUN = set("0123456789_")


def _check_underscore_run(run, run_offset):
    """Return the offset of the leftmost underscore in ``run`` that is not
    strictly between two digits of that same run, or None if all are ok."""
    n = len(run)
    for idx in range(n):
        if run[idx] != "_":
            continue
        ok = (
            idx > 0
            and idx < n - 1
            and run[idx - 1] != "_"
            and run[idx + 1] != "_"
        )
        if not ok:
            return run_offset + idx
    return None


def _parse_field(field, p0):
    # A. charset
    for i, ch in enumerate(field):
        if ch not in _CHARSET:
            raise NumError("char", p0 + i)

    # B. sign
    if field[0] in "+-":
        sign = field[0]
        body = field[1:]
        body_offset = p0 + 1
    else:
        sign = ""
        body = field
        body_offset = p0

    if body == "":
        raise NumError("sign", p0)

    # C. suffix
    suffix = ""
    suffix_pos = None
    if body[-1] in "uls":
        suffix = body[-1]
        suffix_pos = body_offset + len(body) - 1
        body2 = body[:-1]
    else:
        body2 = body

    if body2 == "":
        raise NumError("suffix", suffix_pos)

    # D. structural scan
    radix = 10
    is_radix = False
    intpart = fracpart = expdigits = ""
    intpart_offset = fracpart_offset = expdigits_offset = None
    dot_offset = None
    exp_offset = None
    exp_sign = ""
    has_dot = False
    has_exp = False
    rest = None
    rest_offset = None

    if len(body2) >= 2 and body2[0] == "0" and body2[1] in "XOB":
        raise NumError("prefix", body_offset + 1)

    if len(body2) >= 2 and body2[0] == "0" and body2[1] in "xob":
        is_radix = True
        radix = {"x": 16, "o": 8, "b": 2}[body2[1]]
        rest = body2[2:]
        rest_offset = body_offset + 2
        if rest == "":
            raise NumError("prefix", rest_offset)
        for i, ch in enumerate(rest):
            if ch == "_":
                continue
            v = DIGIT_VAL.get(ch.lower())
            if v is None or v >= radix:
                raise NumError("digit", rest_offset + i)
    else:
        pos = 0
        n = len(body2)
        while pos < n and body2[pos] in _DEC_RUN:
            pos += 1
        intpart = body2[:pos]
        intpart_offset = body_offset
        if pos < n and body2[pos] == ".":
            has_dot = True
            dot_offset = body_offset + pos
            pos += 1
            start = pos
            while pos < n and body2[pos] in _DEC_RUN:
                pos += 1
            fracpart = body2[start:pos]
            fracpart_offset = body_offset + start
        if pos < n and body2[pos] in "eE":
            has_exp = True
            exp_offset = body_offset + pos
            pos += 1
            if pos < n and body2[pos] in "+-":
                exp_sign = body2[pos]
                pos += 1
            start = pos
            while pos < n and body2[pos] in _DEC_RUN:
                pos += 1
            expdigits = body2[start:pos]
            expdigits_offset = body_offset + start
        if pos != n:
            raise NumError("syntax", body_offset + pos)

    # E. semantic checks, in exactly this order
    if is_radix:
        u_pos = _check_underscore_run(rest, rest_offset)
        if u_pos is not None:
            raise NumError("underscore", u_pos)
    else:
        u_pos = None
        for run, off in (
            (intpart, intpart_offset),
            (fracpart, fracpart_offset),
            (expdigits, expdigits_offset),
        ):
            if off is None:
                continue
            p = _check_underscore_run(run, off)
            if p is not None:
                u_pos = p
                break
        if u_pos is not None:
            raise NumError("underscore", u_pos)

        if has_dot and fracpart == "":
            raise NumError("dangling_dot", dot_offset)

        if has_exp and expdigits == "":
            raise NumError("exponent", exp_offset)

        intpart_clean_check = intpart.replace("_", "")
        if len(intpart_clean_check) >= 2 and intpart_clean_check[0] == "0":
            raise NumError("leading_zero", intpart_offset)

    is_float = (not is_radix) and (has_dot or has_exp)

    if suffix in ("u", "l") and is_float:
        raise NumError("suffix", suffix_pos)
    if suffix == "s" and not is_float:
        raise NumError("suffix", suffix_pos)

    # build the record
    if is_radix:
        digits_clean = rest.replace("_", "")
        magnitude = _digits_to_int(digits_clean, radix)
        value = -magnitude if sign == "-" else magnitude
        stripped = digits_clean.lower().lstrip("0")
        if stripped == "":
            stripped = "0"
        sign_out = "-" if value < 0 else ""
        prefix_txt = {16: "0x", 8: "0o", 2: "0b"}[radix]
        text = sign_out + prefix_txt + stripped
        kind = "int"
    elif not is_float:
        intpart_clean = intpart.replace("_", "")
        magnitude = _digits_to_int(intpart_clean, 10)
        value = -magnitude if sign == "-" else magnitude
        sign_out = "-" if value < 0 else ""
        text = sign_out + intpart_clean
        kind = "int"
        radix = 10
    else:
        intpart_clean = intpart.replace("_", "")
        fracpart_clean = fracpart.replace("_", "")
        d_digits = (intpart_clean if intpart_clean != "" else "0") + fracpart_clean
        m = _digits_to_int(d_digits, 10)
        exp_digits_clean = expdigits.replace("_", "")
        exp_mag = _digits_to_int(exp_digits_clean, 10) if exp_digits_clean != "" else 0
        exp_signed = -exp_mag if exp_sign == "-" else exp_mag
        e = exp_signed - len(fracpart_clean)
        if e >= 0:
            magnitude = m * (10.0 ** e)
        else:
            magnitude = m / (10.0 ** (-e))
        value = -magnitude if sign == "-" else magnitude
        sign_out = "-" if sign == "-" else ""
        intpart_txt = intpart_clean if intpart_clean != "" else "0"
        fracpart_txt = fracpart_clean if has_dot else "0"
        text = sign_out + intpart_txt + "." + fracpart_txt
        if has_exp:
            exp_txt = exp_digits_clean.lstrip("0")
            if exp_txt == "":
                exp_txt = "0"
            exp_sign_txt = "-" if exp_signed < 0 else ""
            text = text + "e" + exp_sign_txt + exp_txt
        kind = "float"
        radix = 10

    record = {}
    record["kind"] = kind
    record["radix"] = radix
    record["value"] = value
    record["text"] = text
    record["suffix"] = suffix
    record["start"] = p0
    return record


def scan(text):
    if text == "":
        return []

    n = len(text)
    for i in range(n):
        if text[i] == " ":
            if i == 0:
                raise NumError("space", 0)
            if i == n - 1:
                raise NumError("space", i)
            if text[i + 1] == " ":
                raise NumError("space", i + 1)

    records = []
    idx = 0
    for field in text.split(" "):
        p0 = idx
        idx += len(field) + 1
        records.append(_parse_field(field, p0))
    return records


# ---------------------------------------------------------------------------
# format_number

_DIGITS09 = set("0123456789")


def _parse_spec(spec):
    n = len(spec)
    idx = 0
    fill = " "
    align = ">"
    if n >= 2 and spec[1] in "<>^":
        fill = spec[0]
        align = spec[1]
        idx = 2
    elif n >= 1 and spec[0] in "<>^":
        align = spec[0]
        idx = 1

    sign = "-"
    if idx < n and spec[idx] in "+- ":
        sign = spec[idx]
        idx += 1

    comma = False
    if idx < n and spec[idx] == ",":
        comma = True
        idx += 1

    width = 0
    if idx < n and spec[idx] in _DIGITS09:
        start = idx
        while idx < n and spec[idx] in _DIGITS09:
            idx += 1
        run = spec[start:idx]
        if run[0] == "0":
            raise NumError("spec", -1)
        width = _digits_to_int(run, 10)
        if width > 200:
            raise NumError("spec", -1)

    precision = 0
    if idx < n and spec[idx] == ".":
        idx += 1
        start = idx
        while idx < n and spec[idx] in _DIGITS09:
            idx += 1
        run = spec[start:idx]
        if run == "":
            raise NumError("spec", -1)
        precision = _digits_to_int(run, 10)
        if precision > 20:
            raise NumError("spec", -1)

    mode = "h"
    if idx < n:
        if spec[idx] in "hufd":
            mode = spec[idx]
            idx += 1
        else:
            raise NumError("spec", -1)

    if idx != n:
        raise NumError("spec", -1)

    return fill, align, sign, comma, width, precision, mode


def format_number(value, spec):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NumError("type", -1)
    if not isinstance(spec, str):
        raise NumError("type", -1)

    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise NumError("nonfinite", -1)

    fill, align, sign_policy, comma, width, precision, mode = _parse_spec(spec)

    scale = 10 ** precision

    if isinstance(value, int):
        neg = value < 0
        q_final = abs(value) * scale
    else:
        neg = math.copysign(1.0, value) < 0
        num, den = value.as_integer_ratio()
        magnitude_num = abs(num)
        scaled = magnitude_num * scale
        q, r = divmod(scaled, den)
        if mode == "d":
            q_final = q
        elif mode == "f":
            q_final = q + 1 if (neg and r > 0) else q
        elif mode == "u":
            q_final = q + 1 if 2 * r >= den else q
        else:  # half-even
            if 2 * r > den:
                q_final = q + 1
            elif 2 * r < den:
                q_final = q
            else:
                q_final = q + 1 if q % 2 == 1 else q

    integer_part = q_final // scale
    frac_val = q_final - integer_part * scale

    int_str = str(integer_part)
    if comma:
        n = len(int_str)
        first_len = n % 3
        if first_len == 0:
            first_len = 3
        parts = [int_str[:first_len]]
        i = first_len
        while i < n:
            parts.append(int_str[i:i + 3])
            i += 3
        int_str = ",".join(parts)

    if sign_policy == "+":
        sign_char = "-" if neg else "+"
    elif sign_policy == " ":
        sign_char = "-" if neg else " "
    else:
        sign_char = "-" if neg else ""

    digits_str = int_str
    if precision > 0:
        frac_str = str(frac_val)
        pad = precision - len(frac_str)
        if pad > 0:
            frac_str = ("0" * pad) + frac_str
        digits_str = digits_str + "." + frac_str

    result = sign_char + digits_str

    if len(result) < width:
        pad_len = width - len(result)
        if align == "<":
            result = result + fill * pad_len
        elif align == "^":
            left = pad_len // 2
            right = pad_len - left
            result = (fill * left) + result + (fill * right)
        else:
            result = (fill * pad_len) + result

    return result
