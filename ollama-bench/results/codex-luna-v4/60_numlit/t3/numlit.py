class NumError(ValueError):
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        ValueError.__init__(self, kind)


_DIGITS = "0123456789"
_HEX = "0123456789abcdefABCDEF"


def _number(s, radix):
    n = 0
    for c in s:
        if c != "_":
            if c in _DIGITS:
                d = ord(c) - ord("0")
            else:
                d = ord(c.lower()) - ord("a") + 10
            n = n * radix + d
    return n


def _underscores(run, pos, radix_digits=False):
    bad = []
    for i, c in enumerate(run):
        if c == "_":
            if i == 0 or i + 1 == len(run):
                bad.append(pos + i)
            else:
                a = run[i - 1]
                b = run[i + 1]
                if radix_digits:
                    ok_a = a in _HEX and (a.isdigit() or a.lower() in "abcdef")
                    ok_b = b in _HEX and (b.isdigit() or b.lower() in "abcdef")
                else:
                    ok_a = a in _DIGITS
                    ok_b = b in _DIGITS
                if not (ok_a and ok_b):
                    bad.append(pos + i)
    return bad


def _raise(kind, pos):
    raise NumError(kind, pos)


def _scan_field(field, start):
    allowed = _DIGITS + "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.+-"
    for i, c in enumerate(field):
        if c not in allowed:
            _raise("char", start + i)

    sign = ""
    body_start = start
    body = field
    if body and body[0] in "+-":
        sign = body[0]
        body = body[1:]
        body_start += 1
    if not body:
        _raise("sign", start)

    suffix = ""
    suffix_pos = start + len(field) - 1
    if body[-1] in "uls":
        suffix = body[-1]
        body = body[:-1]
        if not body:
            _raise("suffix", suffix_pos)

    negative = sign == "-"
    if body.startswith("0") and len(body) > 1 and body[1] in "XOB":
        _raise("prefix", body_start + 1)

    radix = 10
    radix_digits = None
    radix_pos = 0
    dot_pos = None
    exp_pos = None
    intpart = fracpart = expdigits = ""
    exp_negative = False
    if body.startswith("0x") or body.startswith("0o") or body.startswith("0b"):
        radix = {"x": 16, "o": 8, "b": 2}[body[1]]
        radix_digits = body[2:]
        radix_pos = body_start + 2
        if not radix_digits:
            _raise("prefix", radix_pos)
        valid = _HEX if radix == 16 else _DIGITS[:radix]
        for i, c in enumerate(radix_digits):
            if c != "_" and c not in valid:
                _raise("digit", radix_pos + i)
    else:
        i = 0
        while i < len(body) and body[i] in _DIGITS + "_":
            i += 1
        intpart = body[:i]
        if i < len(body) and body[i] == ".":
            dot_pos = body_start + i
            i += 1
            j = i
            while i < len(body) and body[i] in _DIGITS + "_":
                i += 1
            fracpart = body[j:i]
        if i < len(body) and body[i] in "eE":
            exp_pos = body_start + i
            i += 1
            if i < len(body) and body[i] in "+-":
                exp_negative = body[i] == "-"
                i += 1
            j = i
            while i < len(body) and body[i] in _DIGITS + "_":
                i += 1
            expdigits = body[j:i]
        if i != len(body):
            _raise("syntax", body_start + i)

    bad = []
    if radix_digits is not None:
        bad = _underscores(radix_digits, radix_pos, True)
    else:
        if intpart:
            bad += _underscores(intpart, body_start)
        if fracpart:
            fp = body_start + (dot_pos - body_start) + 1
            bad += _underscores(fracpart, fp)
        if expdigits:
            ep = exp_pos + 1
            if body[exp_pos - body_start + 1] in "+-":
                ep += 1
            bad += _underscores(expdigits, ep)
    if bad:
        _raise("underscore", min(bad))
    if dot_pos is not None and not fracpart:
        _raise("dangling_dot", dot_pos)
    if exp_pos is not None and not expdigits:
        _raise("exponent", exp_pos)

    if radix_digits is None:
        clean_int = intpart.replace("_", "")
        if len(clean_int) >= 2 and clean_int[0] == "0":
            _raise("leading_zero", body_start)
        is_float = dot_pos is not None or exp_pos is not None
        if is_float and suffix and suffix in "ul":
            _raise("suffix", suffix_pos)
        if not is_float and suffix == "s":
            _raise("suffix", suffix_pos)
        if is_float:
            a = clean_int or "0"
            b = fracpart.replace("_", "") if dot_pos is not None else "0"
            digits = (clean_int or "0") + (fracpart.replace("_", "") if fracpart else "")
            mantissa = _number(digits, 10)
            exponent = 0
            if exp_pos is not None:
                exponent = _number(expdigits, 10)
                if exp_negative:
                    exponent = -exponent
            exponent -= len(fracpart.replace("_", ""))
            try:
                magnitude = mantissa * (10.0 ** exponent) if exponent >= 0 else mantissa / (10.0 ** -exponent)
            except OverflowError:
                magnitude = 1.0e309 if exponent >= 0 else 0.0
            value = -magnitude if negative else magnitude
            canonical = ("-" if negative else "") + a + "." + b
            if exp_pos is not None:
                ed = expdigits.replace("_", "").lstrip("0") or "0"
                canonical += "e" + ("-" if exponent + len(fracpart.replace("_", "")) < 0 else "") + ed
            return {"kind": "float", "radix": 10, "value": value, "text": canonical, "suffix": suffix, "start": start}
        value = _number(clean_int, 10)
        if negative:
            value = -value
        canonical = ("-" if value < 0 else "") + (clean_int or "0")
        return {"kind": "int", "radix": 10, "value": value, "text": canonical, "suffix": suffix, "start": start}

    if suffix == "s":
        _raise("suffix", suffix_pos)
    value = _number(radix_digits, radix)
    if negative:
        value = -value
    clean = radix_digits.replace("_", "").lower().lstrip("0") or "0"
    prefix = {16: "0x", 8: "0o", 2: "0b"}[radix]
    canonical = ("-" if value < 0 else "") + prefix + clean
    return {"kind": "int", "radix": radix, "value": value, "text": canonical, "suffix": suffix, "start": start}


def scan(text):
    if text == "":
        return []
    first = None
    if text[0] == " ":
        first = 0
    if text[-1] == " ":
        first = len(text) - 1 if first is None else first
    for i in range(1, len(text)):
        if text[i] == " " and text[i - 1] == " ":
            if first is None or i < first:
                first = i
    if first is not None:
        _raise("space", first)
    result = []
    p = 0
    while p < len(text):
        q = text.find(" ", p)
        if q < 0:
            q = len(text)
        result.append(_scan_field(text[p:q], p))
        p = q + 1
    return result


def _spec(spec):
    fill, align, sign, comma = " ", ">", "-", False
    i = 0
    if len(spec) >= 2 and spec[1] in "<>^":
        fill, align, i = spec[0], spec[1], 2
    elif spec and spec[0] in "<>^":
        align, i = spec[0], 1
    if i < len(spec) and spec[i] in "+- ":
        sign, i = spec[i], i + 1
    if i < len(spec) and spec[i] == ",":
        comma, i = True, i + 1
    wstart = i
    while i < len(spec) and spec[i] in _DIGITS:
        i += 1
    width = 0
    if i > wstart:
        if spec[wstart] == "0":
            _raise("spec", -1)
        width = _number(spec[wstart:i], 10)
        if width > 200:
            _raise("spec", -1)
    precision = 0
    if i < len(spec) and spec[i] == ".":
        i += 1
        pstart = i
        while i < len(spec) and spec[i] in _DIGITS:
            i += 1
        if i == pstart:
            _raise("spec", -1)
        precision = _number(spec[pstart:i], 10)
        if precision > 20:
            _raise("spec", -1)
    mode = "h"
    if i < len(spec):
        if i + 1 != len(spec) or spec[i] not in "hudf":
            _raise("spec", -1)
        mode = spec[i]
        i += 1
    if i != len(spec):
        _raise("spec", -1)
    return fill, align, sign, comma, width, precision, mode


def _group(s):
    pieces = []
    while len(s) > 3:
        pieces.append(s[-3:])
        s = s[:-3]
    pieces.append(s)
    return ",".join(reversed(pieces))


def format_number(value, spec):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isinstance(spec, str):
        _raise("type", -1)
    if isinstance(value, float) and (value != value or value == 1.0e309 or value == -1.0e309):
        _raise("nonfinite", -1)
    fill, align, sign_policy, comma, width, precision, mode = _spec(spec)
    negative = value < 0
    if isinstance(value, float) and value == 0.0:
        negative = value.hex().startswith("-")
    if isinstance(value, int):
        numerator, denominator = (value if value >= 0 else -value), 1
    else:
        numerator, denominator = value.as_integer_ratio()
        if numerator < 0:
            numerator = -numerator
    scale = 10 ** precision
    scaled_num = numerator * scale
    quotient, remainder = divmod(scaled_num, denominator)
    increment = False
    if mode == "u":
        increment = remainder * 2 >= denominator
    elif mode == "h":
        increment = remainder * 2 > denominator or (remainder * 2 == denominator and quotient % 2 == 1)
    elif mode == "f" and negative and remainder:
        increment = True
    if increment:
        quotient += 1
    digits = str(quotient)
    if precision:
        if len(digits) <= precision:
            digits = "0" * (precision + 1 - len(digits)) + digits
        whole, fraction = digits[:-precision], digits[-precision:]
        if comma:
            whole = _group(whole)
        body = whole + "." + fraction
    else:
        body = _group(digits) if comma else digits
    if negative:
        prefix = "-"
    elif sign_policy == "+":
        prefix = "+"
    elif sign_policy == " ":
        prefix = " "
    else:
        prefix = ""
    rendered = prefix + body
    padding = width - len(rendered)
    if padding > 0:
        if align == "<":
            rendered += fill * padding
        elif align == "^":
            left = padding // 2
            rendered = fill * left + rendered + fill * (padding - left)
        else:
            rendered = fill * padding + rendered
    return rendered
