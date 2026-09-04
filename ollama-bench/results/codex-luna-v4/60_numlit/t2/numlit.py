"""Numeric literal scanner and exact fixed-point formatter."""


class NumError(ValueError):
    def __init__(self, kind, pos):
        self.kind = kind
        self.pos = pos
        super().__init__(kind)


def _digits_value(s, radix):
    n = 0
    for c in s:
        if c != "_":
            if "0" <= c <= "9":
                d = ord(c) - ord("0")
            else:
                d = ord(c.lower()) - ord("a") + 10
            n = n * radix + d
    return n


def _underscore_error(s, base):
    for i, c in enumerate(s):
        if c == "_" and (i == 0 or i + 1 == len(s) or
                          not (s[i - 1].isdigit() and s[i + 1].isdigit())):
            return base + i
    return None


def _plain_digits(s):
    return s.replace("_", "")


def _parse_signed_digits(s):
    neg = False
    if s and s[0] in "+-":
        neg = s[0] == "-"
        s = s[1:]
    n = _digits_value(s, 10)
    return -n if neg else n


def scan(text):
    if not isinstance(text, str):
        raise NumError("char", 0)
    if text == "":
        return []
    first = None
    if text[0] == " ":
        first = 0
    if text[-1] == " ":
        first = text.__len__() - 1 if first is None else min(first, text.__len__() - 1)
    for i in range(1, text.__len__()):
        if text[i] == " " and text[i - 1] == " ":
            first = i if first is None else min(first, i)
            break
    if first is not None:
        raise NumError("space", first)

    out = []
    p = 0
    allowed = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.+-"
    while p < text.__len__():
        q = p
        while q < text.__len__() and text[q] != " ":
            q += 1
        field = text[p:q]
        for j, c in enumerate(field):
            if c not in allowed:
                raise NumError("char", p + j)
        sign = ""
        body = field
        if body and body[0] in "+-":
            sign, body = body[0], body[1:]
        if not body:
            raise NumError("sign", p)
        suffix = ""
        suffix_pos = -1
        if body[-1:] in ("u", "l", "s"):
            suffix = body[-1]
            suffix_pos = p + len(field) - 1
            body = body[:-1]
            if not body:
                raise NumError("suffix", suffix_pos)
        body_base = p + (1 if sign else 0)
        if len(body) >= 2 and body[0] == "0" and body[1] in "XOB":
            raise NumError("prefix", body_base + 1)

        radix = 10
        is_radix = len(body) >= 2 and body[:2] in ("0x", "0o", "0b")
        if is_radix:
            radix = {"0x": 16, "0o": 8, "0b": 2}[body[:2]]
            digs = body[2:]
            if not digs:
                raise NumError("prefix", body_base + 2)
            valid = "0123456789abcdefABCDEF_" if radix == 16 else "01234567_" if radix == 8 else "01_"
            for j, c in enumerate(digs):
                if c not in valid:
                    raise NumError("digit", body_base + 2 + j)
            ue = _underscore_error(digs, body_base + 2)
            if ue is not None:
                raise NumError("underscore", ue)
            n = _digits_value(digs, radix)
            if sign == "-":
                n = -n
            clean = _plain_digits(digs).lower().lstrip("0") or "0"
            canon = ("-" if n < 0 else "") + ("0x" if radix == 16 else "0o" if radix == 8 else "0b") + clean
            out.append({"kind": "int", "radix": radix, "value": n, "text": canon, "suffix": suffix, "start": p})
        else:
            i = 0
            a = i
            while i < len(body) and body[i] in "0123456789_":
                i += 1
            intpart = body[a:i]
            dot_pos = -1
            fracpart = ""
            if i < len(body) and body[i] == ".":
                dot_pos = i
                i += 1
                a = i
                while i < len(body) and body[i] in "0123456789_":
                    i += 1
                fracpart = body[a:i]
            exp_pos = -1
            expdigits = ""
            exp_sign = ""
            if i < len(body) and body[i] in "eE":
                exp_pos = i
                i += 1
                if i < len(body) and body[i] in "+-":
                    exp_sign, i = body[i], i + 1
                a = i
                while i < len(body) and body[i] in "0123456789_":
                    i += 1
                expdigits = body[a:i]
            if i != len(body):
                raise NumError("syntax", body_base + i)
            for part, off in ((intpart, 0), (fracpart, dot_pos + 1 if dot_pos >= 0 else 0), (expdigits, exp_pos + 1 if exp_pos >= 0 else 0)):
                ue = _underscore_error(part, body_base + off)
                if ue is not None:
                    raise NumError("underscore", ue)
            if dot_pos >= 0 and not fracpart:
                raise NumError("dangling_dot", body_base + dot_pos)
            if exp_pos >= 0 and not expdigits:
                raise NumError("exponent", body_base + exp_pos)
            clean_i = _plain_digits(intpart)
            if len(clean_i) >= 2 and clean_i[0] == "0":
                raise NumError("leading_zero", body_base)
            is_float = dot_pos >= 0 or exp_pos >= 0
            if suffix and ((suffix in "ul" and is_float) or (suffix == "s" and not is_float)):
                raise NumError("suffix", suffix_pos)
            if not is_float:
                n = _digits_value(intpart, 10)
                if sign == "-": n = -n
                canon = ("-" if n < 0 else "") + (clean_i or "0")
                out.append({"kind": "int", "radix": 10, "value": n, "text": canon, "suffix": suffix, "start": p})
            else:
                ci = clean_i or "0"
                cf = _plain_digits(fracpart)
                cd = ci + cf
                m = _digits_value(cd, 10)
                e = _parse_signed_digits((exp_sign or "+") + expdigits) if exp_pos >= 0 else 0
                e -= len(cf)
                try:
                    mag = m * (10.0 ** e) if e >= 0 else m / (10.0 ** -e)
                except OverflowError:
                    mag = 1e309 if m else 0.0
                if sign == "-": mag = -mag
                exp_canon = ""
                if exp_pos >= 0:
                    ev = _parse_signed_digits((exp_sign or "+") + expdigits)
                    ed = _plain_digits(expdigits).lstrip("0") or "0"
                    exp_canon = "e" + ("-" if ev < 0 else "") + ed
                sign_canon = "-" if sign == "-" else ""
                canon = sign_canon + ci + "." + (cf or "0") + exp_canon
                out.append({"kind": "float", "radix": 10, "value": mag, "text": canon, "suffix": suffix, "start": p})
        p = q + 1
    return out


def _spec_error():
    raise NumError("spec", -1)


def format_number(value, spec):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isinstance(spec, str):
        raise NumError("type", -1)
    if isinstance(value, float) and (value != value or value == 1e309 or value == -1e309):
        raise NumError("nonfinite", -1)
    fill, align, i = " ", ">", 0
    if len(spec) >= 2 and spec[1] in "<>^":
        fill, align, i = spec[0], spec[1], 2
    elif i < len(spec) and spec[i] in "<>^":
        align, i = spec[i], i + 1
    sign_policy = "-"
    if i < len(spec) and spec[i] in "+- ":
        sign_policy, i = spec[i], i + 1
    grouping = False
    if i < len(spec) and spec[i] == ",":
        grouping, i = True, i + 1
    width = 0
    start = i
    while i < len(spec) and spec[i].isdigit(): i += 1
    if i > start:
        w = spec[start:i]
        if w[0] == "0": _spec_error()
        width = _digits_value(w, 10)
        if width > 200: _spec_error()
    precision = 0
    if i < len(spec) and spec[i] == ".":
        i += 1; start = i
        while i < len(spec) and spec[i].isdigit(): i += 1
        if i == start: _spec_error()
        precision = _digits_value(spec[start:i], 10)
        if precision > 20: _spec_error()
    mode = "h"
    if i < len(spec):
        if spec[i] not in "hudf" or i + 1 != len(spec): _spec_error()
        mode, i = spec[i], i + 1
    if isinstance(value, int):
        num, den = value, 1
        negative = value < 0
    else:
        num, den = value.as_integer_ratio()
        negative = num < 0 or (num == 0 and value.hex().startswith("-"))
    anum = -num if num < 0 else num
    scale = 10 ** precision
    q, rem = divmod(anum * scale, den)
    inc = False
    if mode == "u": inc = rem * 2 >= den
    elif mode == "h": inc = rem * 2 > den or (rem * 2 == den and q % 2 == 1)
    elif mode == "f" and negative: inc = rem != 0
    if inc: q += 1
    whole, frac = divmod(q, scale)
    digs = str(whole)
    if grouping:
        chunks = []
        while digs: chunks.append(digs[-3:]); digs = digs[:-3]
        digs = ",".join(reversed(chunks))
    rendered = digs + (("." + str(frac).rjust(precision, "0")) if precision else "")
    if negative or sign_policy == "+": prefix = "-" if negative else "+"
    elif sign_policy == " ": prefix = " "
    else: prefix = ""
    rendered = prefix + rendered
    if len(rendered) < width:
        n = width - len(rendered)
        if align == "<": rendered += fill * n
        elif align == "^": rendered = fill * (n // 2) + rendered + fill * (n - n // 2)
        else: rendered = fill * n + rendered
    return rendered
