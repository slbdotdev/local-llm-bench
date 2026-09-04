"""numlit.py -- scan numeric literals from text and format numbers.

Standard library only, no filesystem or network access.
"""

import math


class NumError(ValueError):
    def __init__(self, kind, pos):
        super().__init__(kind, pos)
        self.kind = kind
        self.pos = pos


# --------------------------------------------------------------------------
# small helpers (no banned builtins used anywhere below)
# --------------------------------------------------------------------------

def _is_ascii_digit(c):
    return "0" <= c <= "9"


def _digit_val(c):
    o = ord(c)
    if 48 <= o <= 57:
        return o - 48
    if 97 <= o <= 122:
        return o - 87
    if 65 <= o <= 90:
        return o - 55
    return -1


def _is_radix_digit(c, radix):
    v = _digit_val(c)
    if v < 0:
        return False
    return v < radix


def _digits_to_int(s, radix):
    v = 0
    for c in s:
        v = v * radix + _digit_val(c)
    return v


def _strip_leading_zeros(s):
    i = 0
    while i < len(s) - 1 and s[i] == "0":
        i += 1
    return s[i:]


def _bad_underscore_pos(run, offset):
    n = len(run)
    for i in range(n):
        if run[i] == "_":
            if i == 0 or i == n - 1 or run[i - 1] == "_" or run[i + 1] == "_":
                return offset + i
    return None


def _is_charset_ok(c):
    if c == "_" or c == "." or c == "+" or c == "-":
        return True
    o = ord(c)
    if 48 <= o <= 57:
        return True
    if 97 <= o <= 122:
        return True
    if 65 <= o <= 90:
        return True
    return False


# --------------------------------------------------------------------------
# scan
# --------------------------------------------------------------------------

def _check_separator(text):
    n = len(text)
    if n == 0:
        return
    positions = []
    if text[0] == " ":
        positions.append(0)
    if text[-1] == " ":
        positions.append(n - 1)
    i = 0
    while i < n - 1:
        if text[i] == " " and text[i + 1] == " ":
            positions.append(i + 1)
        i += 1
    if positions:
        raise NumError("space", min(positions))


def _parse_field(f, p0):
    n = len(f)

    # A. charset
    for i in range(n):
        if not _is_charset_ok(f[i]):
            raise NumError("char", p0 + i)

    # B. sign
    if f[0] == "+" or f[0] == "-":
        sign = f[0]
        body_start = 1
    else:
        sign = ""
        body_start = 0

    body = f[body_start:]
    body_offset = p0 + body_start
    if body == "":
        raise NumError("sign", p0)

    # C. suffix
    suffix = ""
    suffix_pos = -1
    last = body[-1]
    if last == "u" or last == "l" or last == "s":
        suffix = last
        suffix_pos = body_offset + len(body) - 1
        body = body[:-1]
        if body == "":
            raise NumError("suffix", suffix_pos)

    core = body
    core_offset = body_offset

    # D. structural scan
    is_radix = False
    radix = 10
    intpart = ""
    intpart_offset = core_offset
    has_dot = False
    dot_pos = -1
    fracpart = None
    frac_offset = -1
    has_exp = False
    exp_pos = -1
    exp_sign = ""
    expdigits = ""
    expdigits_offset = -1
    rest = ""
    rest_offset = -1

    if len(core) >= 2 and core[0] == "0" and core[1] in ("X", "O", "B"):
        raise NumError("prefix", core_offset + 1)

    if len(core) >= 2 and core[0] == "0" and core[1] in ("x", "o", "b"):
        is_radix = True
        radix = {"x": 16, "o": 8, "b": 2}[core[1]]
        rest = core[2:]
        rest_offset = core_offset + 2
        if rest == "":
            raise NumError("prefix", rest_offset)
        for i in range(len(rest)):
            c = rest[i]
            if c == "_":
                continue
            if not _is_radix_digit(c, radix):
                raise NumError("digit", rest_offset + i)
    else:
        idx = 0
        clen = len(core)
        while idx < clen and (_is_ascii_digit(core[idx]) or core[idx] == "_"):
            idx += 1
        intpart = core[0:idx]
        intpart_offset = core_offset

        if idx < clen and core[idx] == ".":
            has_dot = True
            dot_pos = core_offset + idx
            idx += 1
            j = idx
            while j < clen and (_is_ascii_digit(core[j]) or core[j] == "_"):
                j += 1
            fracpart = core[idx:j]
            frac_offset = core_offset + idx
            idx = j

        if idx < clen and (core[idx] == "e" or core[idx] == "E"):
            has_exp = True
            exp_pos = core_offset + idx
            idx += 1
            if idx < clen and (core[idx] == "+" or core[idx] == "-"):
                exp_sign = core[idx]
                idx += 1
            expdigits_offset = core_offset + idx
            j = idx
            while j < clen and (_is_ascii_digit(core[j]) or core[j] == "_"):
                j += 1
            expdigits = core[idx:j]
            idx = j

        if idx != clen:
            raise NumError("syntax", core_offset + idx)

    # E. semantic checks
    if is_radix:
        bp = _bad_underscore_pos(rest, rest_offset)
        if bp is not None:
            raise NumError("underscore", bp)
    else:
        candidates = []
        bp = _bad_underscore_pos(intpart, intpart_offset)
        if bp is not None:
            candidates.append(bp)
        if fracpart is not None:
            bp = _bad_underscore_pos(fracpart, frac_offset)
            if bp is not None:
                candidates.append(bp)
        if has_exp:
            bp = _bad_underscore_pos(expdigits, expdigits_offset)
            if bp is not None:
                candidates.append(bp)
        if candidates:
            raise NumError("underscore", min(candidates))

        if has_dot and fracpart == "":
            raise NumError("dangling_dot", dot_pos)

        if has_exp and expdigits == "":
            raise NumError("exponent", exp_pos)

        intpart_clean = intpart.replace("_", "")
        if len(intpart_clean) >= 2 and intpart_clean[0] == "0":
            raise NumError("leading_zero", intpart_offset)

    is_float = (not is_radix) and (has_dot or has_exp)

    if suffix != "":
        if is_float and (suffix == "u" or suffix == "l"):
            raise NumError("suffix", suffix_pos)
        if (not is_float) and suffix == "s":
            raise NumError("suffix", suffix_pos)

    # build record
    if is_radix:
        digits = rest.replace("_", "")
        mag = _digits_to_int(digits, radix)
        value = -mag if sign == "-" else mag
        hx = {16: hex, 8: oct, 2: bin}[radix]
        text = ("-" if value < 0 else "") + hx(mag)
        kind = "int"
        record = {
            "kind": kind,
            "radix": radix,
            "value": value,
            "text": text,
            "suffix": suffix,
            "start": p0,
        }
        return record

    if not is_float:
        digits = intpart.replace("_", "")
        if digits == "":
            digits = "0"
        mag = _digits_to_int(digits, 10)
        value = -mag if sign == "-" else mag
        text = str(value)
        record = {
            "kind": "int",
            "radix": 10,
            "value": value,
            "text": text,
            "suffix": suffix,
            "start": p0,
        }
        return record

    # float
    intpart_clean = intpart.replace("_", "")
    frac_clean = fracpart.replace("_", "") if has_dot and fracpart is not None else ""
    d_str = (intpart_clean if intpart_clean != "" else "0") + frac_clean
    m = _digits_to_int(d_str, 10)
    frac_len = len(frac_clean)

    exp_val = 0
    if has_exp:
        exp_clean = expdigits.replace("_", "")
        exp_val = _digits_to_int(exp_clean, 10)
        if exp_sign == "-":
            exp_val = -exp_val

    e = exp_val - frac_len
    if e >= 0:
        magnitude = m * (10.0 ** e)
    else:
        magnitude = m / (10.0 ** (-e))

    value = -magnitude if sign == "-" else magnitude

    intpart_txt = intpart_clean if intpart_clean != "" else "0"
    fracpart_txt = frac_clean if has_dot else "0"
    text = "-" if sign == "-" else ""
    text = text + intpart_txt + "." + fracpart_txt
    if has_exp:
        exp_clean2 = expdigits.replace("_", "")
        exp_txt = _strip_leading_zeros(exp_clean2)
        text = text + "e" + ("-" if exp_sign == "-" else "") + exp_txt

    record = {
        "kind": "float",
        "radix": 10,
        "value": value,
        "text": text,
        "suffix": suffix,
        "start": p0,
    }
    return record


def scan(text):
    if text == "":
        return []
    _check_separator(text)
    fields = text.split(" ")
    records = []
    pos = 0
    for f in fields:
        records.append(_parse_field(f, pos))
        pos += len(f) + 1
    return records


# --------------------------------------------------------------------------
# format_number
# --------------------------------------------------------------------------

def _group_thousands(s):
    n = len(s)
    if n <= 3:
        return s
    parts = []
    i = n
    while i > 3:
        parts.append(s[i - 3:i])
        i -= 3
    parts.append(s[0:i])
    parts.reverse()
    return ",".join(parts)


def _pad(s, width, fill, align):
    if len(s) >= width:
        return s
    padlen = width - len(s)
    if align == "<":
        return s + fill * padlen
    if align == "^":
        left = padlen // 2
        right = padlen - left
        return (fill * left) + s + (fill * right)
    return (fill * padlen) + s


def format_number(value, spec):
    is_bad_type = False
    if isinstance(value, bool):
        is_bad_type = True
    elif not isinstance(value, (int, float)):
        is_bad_type = True
    elif not isinstance(spec, str):
        is_bad_type = True

    if is_bad_type:
        raise NumError("type", -1)

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise NumError("nonfinite", -1)

    n = len(spec)
    idx = 0

    if n >= 2 and spec[1] in ("<", ">", "^"):
        fill = spec[0]
        align = spec[1]
        idx = 2
    elif n >= 1 and spec[0] in ("<", ">", "^"):
        fill = " "
        align = spec[0]
        idx = 1
    else:
        fill = " "
        align = ">"
        idx = 0

    sign_mode = "-"
    if idx < n and spec[idx] in ("+", "-", " "):
        sign_mode = spec[idx]
        idx += 1

    group = False
    if idx < n and spec[idx] == ",":
        group = True
        idx += 1

    width = 0
    j = idx
    while j < n and _is_ascii_digit(spec[j]):
        j += 1
    wdigits = spec[idx:j]
    if wdigits != "":
        if wdigits[0] == "0":
            raise NumError("spec", -1)
        wval = _digits_to_int(wdigits, 10)
        if wval > 200:
            raise NumError("spec", -1)
        width = wval
    idx = j

    precision = 0
    if idx < n and spec[idx] == ".":
        idx += 1
        k = idx
        while k < n and _is_ascii_digit(spec[k]):
            k += 1
        pdigits = spec[idx:k]
        if pdigits == "":
            raise NumError("spec", -1)
        pval = _digits_to_int(pdigits, 10)
        if pval > 20:
            raise NumError("spec", -1)
        precision = pval
        idx = k

    mode = "h"
    if idx < n and spec[idx] in ("h", "u", "d", "f"):
        mode = spec[idx]
        idx += 1

    if idx != n:
        raise NumError("spec", -1)

    # exact value as a fraction
    if isinstance(value, float):
        num, den = value.as_integer_ratio()
        is_value_negative = math.copysign(1.0, value) < 0
    else:
        num, den = value, 1
        is_value_negative = value < 0

    scale = 10 ** precision
    numerator = num * scale
    is_neg = numerator < 0
    abs_num = -numerator if is_neg else numerator
    q, r = divmod(abs_num, den)
    twice_r = 2 * r

    if mode == "d":
        q_rounded = q
    elif mode == "f":
        if is_neg:
            q_rounded = q if r == 0 else q + 1
        else:
            q_rounded = q
    elif mode == "u":
        q_rounded = q + 1 if twice_r >= den else q
    else:  # 'h' half-even
        if twice_r > den:
            q_rounded = q + 1
        elif twice_r < den:
            q_rounded = q
        else:
            q_rounded = q + 1 if (q % 2 != 0) else q

    s_val = -q_rounded if is_neg else q_rounded
    result_negative = is_value_negative or (s_val < 0)

    magnitude = -s_val if s_val < 0 else s_val
    digs = str(magnitude)

    if precision > 0:
        if len(digs) <= precision:
            digs = ("0" * (precision - len(digs) + 1)) + digs
        frac_digits = digs[len(digs) - precision:]
        int_digits = digs[0:len(digs) - precision]
        if int_digits == "":
            int_digits = "0"
    else:
        int_digits = digs
        frac_digits = ""

    if group:
        int_digits = _group_thousands(int_digits)

    if result_negative:
        schar = "-"
    elif sign_mode == "+":
        schar = "+"
    elif sign_mode == " ":
        schar = " "
    else:
        schar = ""

    body = schar + int_digits
    if precision > 0:
        body = body + "." + frac_digits

    return _pad(body, width, fill, align)
