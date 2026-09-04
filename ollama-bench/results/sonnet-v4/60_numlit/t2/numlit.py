"""numlit: scan numeric literals from text and format numbers as fixed-point decimals.

Standard library only (uses only `math`), no filesystem or network access.
"""

import math


class NumError(ValueError):
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(kind)


# ---------------------------------------------------------------------------
# helpers (no calls to int/float/complex/eval/exec/round/format/Decimal/literal_eval)
# ---------------------------------------------------------------------------

_HEXLOWER = "0123456789abcdef"


def _digit_value(ch):
    return _HEXLOWER.index(ch.lower())


def _digits_to_int(s, base):
    v = 0
    for ch in s:
        v = v * base + _digit_value(ch)
    return v


DEC_DIGITS = "0123456789"
HEX_DIGITS = "0123456789abcdefABCDEF"
OCT_DIGITS = "01234567"
BIN_DIGITS = "01"

_FIELD_CHARSET = set(
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.+-"
)


def _first_bad_underscore(run, abs_start, digitset):
    n = len(run)
    for i, ch in enumerate(run):
        if ch == "_":
            ok = (
                i > 0
                and i < n - 1
                and run[i - 1] in digitset
                and run[i + 1] in digitset
            )
            if not ok:
                return abs_start + i
    return -1


def _consume_digits_underscore(s, start_idx):
    idx = start_idx
    n = len(s)
    while idx < n and (s[idx] in DEC_DIGITS or s[idx] == "_"):
        idx += 1
    return idx


# ---------------------------------------------------------------------------
# scan
# ---------------------------------------------------------------------------


def scan(text):
    if text == "":
        return []

    n = len(text)
    candidates = []
    if text[0] == " ":
        candidates.append(0)
    if text[-1] == " ":
        candidates.append(n - 1)
    for i in range(n - 1):
        if text[i] == " " and text[i + 1] == " ":
            candidates.append(i + 1)
    if candidates:
        raise NumError("space", min(candidates))

    records = []
    parts = text.split(" ")
    offset = 0
    for part in parts:
        records.append(_parse_field(part, offset))
        offset += len(part) + 1
    return records


def _parse_field(field, p0):
    # A. charset
    for idx, ch in enumerate(field):
        if ch not in _FIELD_CHARSET:
            raise NumError("char", p0 + idx)

    # B. sign
    sign = ""
    body = field
    body_start = p0
    if field[:1] in ("+", "-"):
        sign = field[0]
        body = field[1:]
        body_start = p0 + 1
    if body == "":
        raise NumError("sign", p0)

    # C. suffix
    suffix = ""
    suffix_pos = -1
    if body[-1] in ("u", "l", "s"):
        suffix_char = body[-1]
        suffix_pos = body_start + len(body) - 1
        rest_body = body[:-1]
        if rest_body == "":
            raise NumError("suffix", suffix_pos)
        suffix = suffix_char
        body = rest_body

    # D. structural scan
    if len(body) >= 2 and body[0] == "0" and body[1] in ("X", "O", "B"):
        raise NumError("prefix", body_start + 1)

    if len(body) >= 2 and body[0] == "0" and body[1] in ("x", "o", "b"):
        radix_char = body[1]
        radix = {"x": 16, "o": 8, "b": 2}[radix_char]
        digitset = {"x": HEX_DIGITS, "o": OCT_DIGITS, "b": BIN_DIGITS}[radix_char]
        rest = body[2:]
        rest_start = body_start + 2
        if rest == "":
            raise NumError("prefix", rest_start)
        for idx, ch in enumerate(rest):
            if not (ch in digitset or ch == "_"):
                raise NumError("digit", rest_start + idx)

        # E1. underscore
        pos = _first_bad_underscore(rest, rest_start, digitset)
        if pos != -1:
            raise NumError("underscore", pos)

        # E5. suffix (radix literals are always INT)
        if suffix == "s":
            raise NumError("suffix", suffix_pos)

        rest_clean = rest.replace("_", "")
        value = _digits_to_int(rest_clean, radix)
        if sign == "-":
            value = -value
        digits_text = rest_clean.lower().lstrip("0")
        if digits_text == "":
            digits_text = "0"
        prefix_text = {16: "0x", 8: "0o", 2: "0b"}[radix]
        text_sign = "-" if (sign == "-" and value != 0) else ""
        text_val = text_sign + prefix_text + digits_text

        record = {}
        record["kind"] = "int"
        record["radix"] = radix
        record["value"] = value
        record["text"] = text_val
        record["suffix"] = suffix
        record["start"] = p0
        return record

    # DECIMAL literal
    idx = 0
    blen = len(body)
    intpart_end = _consume_digits_underscore(body, 0)
    intpart = body[0:intpart_end]
    idx = intpart_end

    has_dot = False
    dot_pos = None
    fracpart = ""
    if idx < blen and body[idx] == ".":
        has_dot = True
        dot_pos = body_start + idx
        idx += 1
        frac_end = _consume_digits_underscore(body, idx)
        fracpart = body[idx:frac_end]
        idx = frac_end

    has_exp = False
    exp_pos = None
    exp_sign = ""
    expdigits = ""
    if idx < blen and body[idx] in ("e", "E"):
        has_exp = True
        exp_pos = body_start + idx
        idx += 1
        if idx < blen and body[idx] in ("+", "-"):
            exp_sign = body[idx]
            idx += 1
        exp_start_idx = idx
        exp_end = _consume_digits_underscore(body, idx)
        expdigits = body[exp_start_idx:exp_end]
        idx = exp_end

    if idx != blen:
        raise NumError("syntax", body_start + idx)

    is_float = has_dot or has_exp

    # E1. underscore (intpart, fracpart, expdigits in order)
    pos = _first_bad_underscore(intpart, body_start, DEC_DIGITS)
    if pos != -1:
        raise NumError("underscore", pos)
    if has_dot:
        frac_abs_start = dot_pos + 1
        pos = _first_bad_underscore(fracpart, frac_abs_start, DEC_DIGITS)
        if pos != -1:
            raise NumError("underscore", pos)
    if has_exp:
        exp_digits_abs_start = exp_pos + 1 + (1 if exp_sign else 0)
        pos = _first_bad_underscore(expdigits, exp_digits_abs_start, DEC_DIGITS)
        if pos != -1:
            raise NumError("underscore", pos)

    # E2. dangling_dot
    if has_dot and fracpart == "":
        raise NumError("dangling_dot", dot_pos)

    # E3. exponent
    if has_exp and expdigits == "":
        raise NumError("exponent", exp_pos)

    # E4. leading_zero (decimal int only... applies to intpart for both int/float per spec text,
    # but spec explicitly says "DECIMAL only" meaning radix literals excluded; float decimals
    # with e.g. "01.5" are still checked per example "01.5" in the spec text)
    intpart_clean = intpart.replace("_", "")
    if len(intpart_clean) >= 2 and intpart_clean[0] == "0":
        raise NumError("leading_zero", body_start)

    # E5. suffix
    if suffix != "":
        if is_float and suffix in ("u", "l"):
            raise NumError("suffix", suffix_pos)
        if (not is_float) and suffix == "s":
            raise NumError("suffix", suffix_pos)

    fracpart_clean = fracpart.replace("_", "")
    expdigits_clean = expdigits.replace("_", "")

    if not is_float:
        value = _digits_to_int(intpart_clean, 10)
        if sign == "-":
            value = -value
        text_val = str(value)

        record = {}
        record["kind"] = "int"
        record["radix"] = 10
        record["value"] = value
        record["text"] = text_val
        record["suffix"] = suffix
        record["start"] = p0
        return record
    else:
        d_digits = intpart_clean + fracpart_clean
        M = _digits_to_int(d_digits, 10)
        exp_value = _digits_to_int(expdigits_clean, 10) if has_exp else 0
        if has_exp and exp_sign == "-":
            exp_value = -exp_value
        E = exp_value - len(fracpart_clean)
        if E >= 0:
            magnitude = M * (10.0 ** E)
        else:
            magnitude = M / (10.0 ** (-E))
        value = -magnitude if sign == "-" else magnitude

        intpart_text = intpart_clean if intpart_clean != "" else "0"
        if has_dot:
            fracpart_text = fracpart_clean
        else:
            fracpart_text = "0"

        is_neg = value < 0 or (value == 0.0 and math.copysign(1.0, value) < 0)
        text_sign = "-" if is_neg else ""

        text_val = text_sign + intpart_text + "." + fracpart_text
        if has_exp:
            exp_digits_text = expdigits_clean.lstrip("0")
            if exp_digits_text == "":
                exp_digits_text = "0"
            exp_sign_text = "-" if exp_value < 0 else ""
            text_val += "e" + exp_sign_text + exp_digits_text

        record = {}
        record["kind"] = "float"
        record["radix"] = 10
        record["value"] = value
        record["text"] = text_val
        record["suffix"] = suffix
        record["start"] = p0
        return record


# ---------------------------------------------------------------------------
# format_number
# ---------------------------------------------------------------------------


def _parse_spec(spec):
    idx = 0
    n = len(spec)
    fill = " "
    align = ">"
    if n >= 2 and spec[1] in ("<", ">", "^"):
        fill = spec[0]
        align = spec[1]
        idx = 2
    elif n >= 1 and spec[0] in ("<", ">", "^"):
        align = spec[0]
        idx = 1

    sign_char = "-"
    if idx < n and spec[idx] in ("+", "-", " "):
        sign_char = spec[idx]
        idx += 1

    comma = False
    if idx < n and spec[idx] == ",":
        comma = True
        idx += 1

    width_val = 0
    if idx < n and spec[idx] in DEC_DIGITS:
        j = idx
        while j < n and spec[j] in DEC_DIGITS:
            j += 1
        width_str = spec[idx:j]
        idx = j
        if width_str[0] == "0":
            raise NumError("spec", -1)
        width_val = _digits_to_int(width_str, 10)
        if width_val > 200:
            raise NumError("spec", -1)

    precision_val = 0
    if idx < n and spec[idx] == ".":
        idx += 1
        j = idx
        while j < n and spec[j] in DEC_DIGITS:
            j += 1
        prec_str = spec[idx:j]
        if prec_str == "":
            raise NumError("spec", -1)
        idx = j
        precision_val = _digits_to_int(prec_str, 10)
        if precision_val > 20:
            raise NumError("spec", -1)

    mode = "h"
    if idx < n and spec[idx] in ("h", "u", "d", "f"):
        mode = spec[idx]
        idx += 1

    if idx != n:
        raise NumError("spec", -1)

    return fill, align, sign_char, comma, width_val, precision_val, mode


def _round_magnitude(num_abs, den_abs, precision, mode, is_neg):
    scaled = num_abs * (10 ** precision)
    q, r = divmod(scaled, den_abs)
    if mode == "d":
        return q
    if mode == "f":
        if is_neg and r > 0:
            return q + 1
        return q
    if mode == "u":
        if 2 * r >= den_abs:
            return q + 1
        return q
    # mode == "h" : half-even
    if 2 * r > den_abs:
        return q + 1
    if 2 * r < den_abs:
        return q
    if q % 2 == 1:
        return q + 1
    return q


def format_number(value, spec):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NumError("type", -1)
    if not isinstance(spec, str):
        raise NumError("type", -1)

    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        raise NumError("nonfinite", -1)

    fill, align, sign_char, comma, width_val, precision_val, mode = _parse_spec(spec)

    if type(value) is int:
        num = value
        den = 1
        is_neg_original = value < 0
    else:
        num, den = value.as_integer_ratio()
        is_neg_original = value < 0 or (
            value == 0.0 and math.copysign(1.0, value) < 0
        )

    num_abs = -num if num < 0 else num
    den_abs = den

    digits_int = _round_magnitude(num_abs, den_abs, precision_val, mode, is_neg_original)

    total_str = str(digits_int)
    if precision_val > 0:
        if len(total_str) < precision_val + 1:
            total_str = total_str.rjust(precision_val + 1, "0")
        int_part_str = total_str[: len(total_str) - precision_val]
        frac_part_str = total_str[len(total_str) - precision_val :]
    else:
        int_part_str = total_str
        frac_part_str = ""

    if comma:
        int_part_str = _group_thousands(int_part_str)

    if is_neg_original:
        sign_prefix = "-"
    elif sign_char == "+":
        sign_prefix = "+"
    elif sign_char == " ":
        sign_prefix = " "
    else:
        sign_prefix = ""

    body = int_part_str
    if precision_val > 0:
        body += "." + frac_part_str

    result = sign_prefix + body

    if len(result) < width_val:
        pad_total = width_val - len(result)
        if align == "<":
            result = result + fill * pad_total
        elif align == "^":
            left = pad_total // 2
            right = pad_total - left
            result = fill * left + result + fill * right
        else:  # ">"
            result = fill * pad_total + result

    return result


def _group_thousands(s):
    n = len(s)
    if n <= 3:
        return s
    parts = []
    i = n
    while i > 3:
        parts.append(s[i - 3 : i])
        i -= 3
    parts.append(s[:i])
    parts.reverse()
    return ",".join(parts)
