class NumError(ValueError):
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(kind)


_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.+-"


def _digits_value(s, radix):
    n = 0
    for c in s:
        if c != "_":
            if c.isdigit():
                d = ord(c) - 48
            else:
                d = ord(c.lower()) - 87
            n = n * radix + d
    return n


def _bad_underscore(run, start, hex_mode=False):
    for i, c in enumerate(run):
        if c == "_":
            if i == 0 or i + 1 == len(run):
                return start + i
            a = run[i - 1]
            b = run[i + 1]
            da = a.isdigit() or (hex_mode and a.lower() in "abcdef")
            db = b.isdigit() or (hex_mode and b.lower() in "abcdef")
            if not (da and db):
                return start + i
    return -1


def _decimal_exp(s, start):
    neg = False
    i = 0
    if s and s[0] in "+-":
        neg = s[0] == "-"
        i = 1
    n = 0
    while i < len(s):
        if s[i] != "_":
            n = n * 10 + ord(s[i]) - 48
        i += 1
    return -n if neg else n


def scan(text):
    if not isinstance(text, str):
        raise NumError("char", -1)
    if not text:
        return []
    first = -1
    if text[0] == " ":
        first = 0
    if text[-1] == " " and (first < 0 or len(text) - 1 < first):
        first = len(text) - 1
    for i in range(1, len(text)):
        if text[i] == " " and text[i - 1] == " ":
            if first < 0 or i < first:
                first = i
            break
    if first >= 0:
        raise NumError("space", first)

    out = []
    p = 0
    while p < len(text):
        q = p
        while q < len(text) and text[q] != " ":
            q += 1
        field = text[p:q]
        for j, c in enumerate(field):
            if c not in _CHARS:
                raise NumError("char", p + j)
        sign = ""
        body = field
        if body and body[0] in "+-":
            sign = body[0]
            body = body[1:]
        if not body:
            raise NumError("sign", p)
        suffix = ""
        suffix_pos = -1
        if body[-1] in "uls":
            suffix = body[-1]
            suffix_pos = p + len(field) - 1
            body = body[:-1]
            if not body:
                raise NumError("suffix", suffix_pos)
        bpos = p + (1 if sign else 0)

        if len(body) >= 2 and body[0] == "0" and body[1] in "XOB":
            raise NumError("prefix", bpos + 1)
        radix = 10
        is_radix = len(body) >= 2 and body[:2] in ("0x", "0o", "0b")
        if is_radix:
            radix = {"0x": 16, "0o": 8, "0b": 2}[body[:2]]
            digs = body[2:]
            if not digs:
                raise NumError("prefix", bpos + 2)
            for j, c in enumerate(digs):
                valid = c == "_" or c.isdigit() or (radix == 16 and c.lower() in "abcdef")
                if not valid or (radix == 8 and c > "7") or (radix == 2 and c > "1"):
                    raise NumError("digit", bpos + 2 + j)
            bad = _bad_underscore(digs, bpos + 2, radix == 16)
            if bad >= 0:
                raise NumError("underscore", bad)
            raw = digs.replace("_", "")
            value = _digits_value(digs, radix)
            if sign == "-":
                value = -value
            canon_digits = raw.lower().lstrip("0") or "0"
            canon = ("-" if value < 0 else "") + body[:2] + canon_digits
            out.append({"kind": "int", "radix": radix, "value": value, "text": canon,
                        "suffix": suffix, "start": p})
        else:
            i = 0
            a = i
            while i < len(body) and (body[i].isdigit() or body[i] == "_"):
                i += 1
            intpart = body[a:i]
            dot_pos = -1
            fracpart = ""
            if i < len(body) and body[i] == ".":
                dot_pos = bpos + i
                i += 1
                a = i
                while i < len(body) and (body[i].isdigit() or body[i] == "_"):
                    i += 1
                fracpart = body[a:i]
            exp_pos = -1
            expdigits = ""
            exp_sign = ""
            if i < len(body) and body[i] in "eE":
                exp_pos = bpos + i
                i += 1
                if i < len(body) and body[i] in "+-":
                    exp_sign = body[i]
                    i += 1
                a = i
                while i < len(body) and (body[i].isdigit() or body[i] == "_"):
                    i += 1
                expdigits = body[a:i]
            if i != len(body):
                raise NumError("syntax", bpos + i)
            bad = _bad_underscore(intpart, bpos, False)
            if bad < 0:
                bad = _bad_underscore(fracpart, bpos + (dot_pos - bpos + 1 if dot_pos >= 0 else len(intpart)), False)
            if bad < 0 and exp_pos >= 0:
                ep = exp_pos + 1 + (1 if exp_sign else 0)
                bad = _bad_underscore(expdigits, ep, False)
            if bad >= 0:
                raise NumError("underscore", bad)
            if dot_pos >= 0 and not fracpart:
                raise NumError("dangling_dot", dot_pos)
            if exp_pos >= 0 and not expdigits:
                raise NumError("exponent", exp_pos)
            iraw = intpart.replace("_", "")
            fraw = fracpart.replace("_", "")
            eraw = expdigits.replace("_", "")
            if len(iraw) >= 2 and iraw[0] == "0":
                raise NumError("leading_zero", bpos)
            is_float = dot_pos >= 0 or exp_pos >= 0
            if not is_float:
                if suffix == "s":
                    raise NumError("suffix", suffix_pos)
                value = _digits_value(iraw, 10)
                if sign == "-":
                    value = -value
                canon = ("-" if value < 0 else "") + iraw
                out.append({"kind": "int", "radix": 10, "value": value, "text": canon,
                            "suffix": suffix, "start": p})
            else:
                if suffix and suffix in "ul":
                    raise NumError("suffix", suffix_pos)
                ip = iraw or "0"
                fp = fraw if dot_pos >= 0 else "0"
                m = _digits_value(ip + fp, 10)
                ev = _decimal_exp(eraw, exp_pos) if exp_pos >= 0 else 0
                ev -= len(fp) if dot_pos >= 0 else 0
                value = m * (10.0 ** ev) if ev >= 0 else m / (10.0 ** -ev)
                if sign == "-":
                    value = -value
                ec = ""
                if exp_pos >= 0:
                    ecv = _decimal_exp(eraw, exp_pos)
                    ec = "e" + ("-" if ecv < 0 else "") + (eraw.lstrip("0") or "0")
                canon = ("-" if sign == "-" else "") + ip + "." + fp + ec
                out.append({"kind": "float", "radix": 10, "value": value, "text": canon,
                            "suffix": suffix, "start": p})
        p = q + 1
    return out


def _parse_spec(spec):
    i = 0
    fill, align = " ", ">"
    if len(spec) >= 2 and spec[1] in "<>^":
        fill, align, i = spec[0], spec[1], 2
    elif i < len(spec) and spec[i] in "<>^":
        align, i = spec[i], i + 1
    sign = "-"
    if i < len(spec) and spec[i] in "+- ":
        sign, i = spec[i], i + 1
    grouping = False
    if i < len(spec) and spec[i] == ",":
        grouping, i = True, i + 1
    width = 0
    if i < len(spec) and spec[i].isdigit():
        a = i
        while i < len(spec) and spec[i].isdigit():
            i += 1
        wtext = spec[a:i]
        if wtext[0] == "0":
            raise NumError("spec", -1)
        for c in wtext:
            width = width * 10 + ord(c) - 48
        if width > 200:
            raise NumError("spec", -1)
    precision = 0
    if i < len(spec) and spec[i] == ".":
        i += 1
        a = i
        while i < len(spec) and spec[i].isdigit():
            i += 1
        if a == i:
            raise NumError("spec", -1)
        for c in spec[a:i]:
            precision = precision * 10 + ord(c) - 48
        if precision > 20:
            raise NumError("spec", -1)
    mode = "h"
    if i < len(spec):
        if spec[i] not in "hudf" or i + 1 != len(spec):
            raise NumError("spec", -1)
        mode = spec[i]
    return fill, align, sign, grouping, width, precision, mode


def _group(s):
    parts = []
    while len(s) > 3:
        parts.append(s[-3:])
        s = s[:-3]
    parts.append(s)
    return ",".join(reversed(parts))


def format_number(value, spec):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isinstance(spec, str):
        raise NumError("type", -1)
    if isinstance(value, float) and (value != value or (value != 0.0 and value == value * 2)):
        raise NumError("nonfinite", -1)
    fill, align, sign_policy, grouping, width, precision, mode = _parse_spec(spec)
    negative = value < 0 or (isinstance(value, float) and value == 0.0 and value.hex().startswith("-"))
    if isinstance(value, int):
        num, den = ( -value if value < 0 else value), 1
    else:
        num, den = value.as_integer_ratio()
        if num < 0:
            num = -num
    scale = 10 ** precision
    whole, rem = divmod(num * scale, den)
    twice = rem * 2
    inc = False
    if mode == "u":
        inc = twice >= den
    elif mode == "h":
        inc = twice > den or (twice == den and (whole & 1) == 1)
    elif mode == "f":
        inc = negative and rem != 0
    if inc:
        whole += 1
    digits = str(whole)
    if precision:
        if len(digits) <= precision:
            digits = "0" * (precision + 1 - len(digits)) + digits
        integer, fraction = digits[:-precision], digits[-precision:]
        rendered = integer + "." + fraction
    else:
        rendered = digits
    if grouping:
        if precision:
            rendered = _group(rendered[:-precision-1]) + rendered[-precision-1:]
        else:
            rendered = _group(rendered)
    if negative:
        prefix = "-"
    elif sign_policy == "+":
        prefix = "+"
    elif sign_policy == " ":
        prefix = " "
    else:
        prefix = ""
    rendered = prefix + rendered
    if len(rendered) < width:
        n = width - len(rendered)
        if align == "<":
            rendered += fill * n
        elif align == "^":
            left = n // 2
            rendered = fill * left + rendered + fill * (n - left)
        else:
            rendered = fill * n + rendered
    return rendered
