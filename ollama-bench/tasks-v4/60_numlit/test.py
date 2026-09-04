import sys, os, math, random, threading, inspect, tokenize, io, decimal
from decimal import Decimal

TOTAL = 30
fails = []
done = 0
_lock = threading.Lock()


def check(name, fn):
    global done
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)
    with _lock:
        done += 1


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


def _watchdog():
    n = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    sys.stdout.flush()
    os._exit(1)


_t = threading.Timer(45.0, _watchdog)
_t.daemon = True
_t.start()

try:
    import numlit
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

# ==========================================================================
# oracle (inlined; every helper is prefixed _ora_ so it cannot clash)
# ==========================================================================
_ORA_D = "0123456789"
_ORA_CHARSET = set("0123456789abcdefghijklmnopqrstuvwxyz"
                   "ABCDEFGHIJKLMNOPQRSTUVWXYZ_.+-")
_ORA_HEX = "0123456789abcdefABCDEF"
_ORA_ALPHA = {16: "0123456789abcdefABCDEF", 8: "01234567", 2: "01"}
_ORA_PRE = {"x": 16, "o": 8, "b": 2}
_ORA_KEYS = ["kind", "radix", "value", "text", "suffix", "start"]


class _OraErr(Exception):
    def __init__(self, kind, pos):
        Exception.__init__(self, kind)
        self.kind = kind
        self.pos = pos


def _ora_nous(s):
    return s.replace("_", "")


def _ora_lz(s):
    i = 0
    while i < len(s) - 1 and s[i] == "0":
        i += 1
    return s[i:]


def _ora_us_bad(run, base):
    for k, ch in enumerate(run):
        if ch != "_":
            continue
        if k == 0 or k == len(run) - 1:
            return base + k
        if run[k - 1] not in _ORA_HEX or run[k + 1] not in _ORA_HEX:
            return base + k
    return -1


def _ora_scan(text):
    n = len(text)
    if n == 0:
        return []
    if text[0] == " ":
        raise _OraErr("space", 0)
    for i in range(1, n):
        if text[i] == " " and text[i - 1] == " ":
            raise _OraErr("space", i)
    if text[n - 1] == " ":
        raise _OraErr("space", n - 1)
    out = []
    p = 0
    while p < n:
        q = p
        while q < n and text[q] != " ":
            q += 1
        out.append(_ora_field(text, p, q))
        p = q + 1
    return out


def _ora_field(text, p0, end):
    for i in range(p0, end):
        if text[i] not in _ORA_CHARSET:
            raise _OraErr("char", i)
    i = p0
    neg = text[i] == "-"
    if text[i] in "+-":
        i += 1
    if i >= end:
        raise _OraErr("sign", p0)
    b0, b1, suffix = i, end, ""
    if text[b1 - 1] in "uls":
        suffix = text[b1 - 1]
        b1 -= 1
        if b1 == b0:
            raise _OraErr("suffix", b1)
    body = text[b0:b1]
    L = len(body)
    radix = 10
    runs = []
    ipart = fpart = epart = rdig = ""
    has_dot = has_exp = False
    dotpos = epos = -1
    esign = 1
    if L >= 2 and body[0] == "0" and body[1] in "XOB":
        raise _OraErr("prefix", b0 + 1)
    if L >= 2 and body[0] == "0" and body[1] in "xob":
        radix = _ORA_PRE[body[1]]
        rdig = body[2:]
        if not rdig:
            raise _OraErr("prefix", b0 + 2)
        for k, ch in enumerate(rdig):
            if ch != "_" and ch not in _ORA_ALPHA[radix]:
                raise _OraErr("digit", b0 + 2 + k)
        runs.append((rdig, b0 + 2))
    else:
        j = 0
        while j < L and body[j] in "0123456789_":
            j += 1
        ipart = body[:j]
        runs.append((ipart, b0))
        if j < L and body[j] == ".":
            has_dot = True
            dotpos = j
            j += 1
            fs = j
            while j < L and body[j] in "0123456789_":
                j += 1
            fpart = body[fs:j]
            runs.append((fpart, b0 + fs))
        if j < L and body[j] in "eE":
            has_exp = True
            epos = j
            j += 1
            if j < L and body[j] in "+-":
                if body[j] == "-":
                    esign = -1
                j += 1
            es = j
            while j < L and body[j] in "0123456789_":
                j += 1
            epart = body[es:j]
            runs.append((epart, b0 + es))
        if j < L:
            raise _OraErr("syntax", b0 + j)
    for run, base in runs:
        bad = _ora_us_bad(run, base)
        if bad >= 0:
            raise _OraErr("underscore", bad)
    if has_dot and fpart == "":
        raise _OraErr("dangling_dot", b0 + dotpos)
    if has_exp and epart == "":
        raise _OraErr("exponent", b0 + epos)
    idig = _ora_nous(ipart)
    if radix == 10 and len(idig) >= 2 and idig[0] == "0":
        raise _OraErr("leading_zero", b0)
    isf = has_dot or has_exp
    if isf and suffix in ("u", "l"):
        raise _OraErr("suffix", b1)
    if (not isf) and suffix == "s":
        raise _OraErr("suffix", b1)
    if isf:
        fdig = _ora_nous(fpart)
        edig = _ora_nous(epart)
        m = int((idig if idig else "0") + fdig)
        expv = esign * int(edig) if has_exp else 0
        e = expv - len(fdig)
        mag = m * (10.0 ** e) if e >= 0 else m / (10.0 ** (-e))
        value = -mag if neg else mag
        txt = ("-" if neg else "") + (idig if idig else "0") + "."
        txt += fdig if has_dot else "0"
        if has_exp:
            txt += "e" + ("-" if expv < 0 else "") + _ora_lz(edig)
        kind = "float"
    else:
        digs = idig if radix == 10 else _ora_nous(rdig)
        value = int(digs, radix)
        if neg:
            value = -value
        if radix == 10:
            txt = ("-" if value < 0 else "") + digs
        else:
            pre = {16: "0x", 8: "0o", 2: "0b"}[radix]
            txt = ("-" if value < 0 else "") + pre + _ora_lz(digs.lower())
        kind = "int"
    return {"kind": kind, "radix": radix, "value": value, "text": txt,
            "suffix": suffix, "start": p0}


_ORA_ROUND = {"h": decimal.ROUND_HALF_EVEN, "u": decimal.ROUND_HALF_UP,
              "d": decimal.ROUND_DOWN, "f": decimal.ROUND_FLOOR}


def _ora_spec(spec):
    n = len(spec)
    fill, align, i = " ", ">", 0
    if n >= 2 and spec[1] in "<>^":
        fill, align, i = spec[0], spec[1], 2
    elif n >= 1 and spec[0] in "<>^":
        align, i = spec[0], 1
    sign = "-"
    if i < n and spec[i] in "+- ":
        sign = spec[i]
        i += 1
    group = False
    if i < n and spec[i] == ",":
        group = True
        i += 1
    width = 0
    s = i
    while i < n and spec[i] in _ORA_D:
        i += 1
    if i > s:
        if spec[s] == "0":
            raise _OraErr("spec", -1)
        width = int(spec[s:i])
        if width > 200:
            raise _OraErr("spec", -1)
    prec = 0
    if i < n and spec[i] == ".":
        i += 1
        s = i
        while i < n and spec[i] in _ORA_D:
            i += 1
        if i == s:
            raise _OraErr("spec", -1)
        prec = int(spec[s:i])
        if prec > 20:
            raise _OraErr("spec", -1)
    mode = "h"
    if i < n:
        if spec[i] not in "hudf":
            raise _OraErr("spec", -1)
        mode = spec[i]
        i += 1
    if i != n:
        raise _OraErr("spec", -1)
    return fill, align, sign, group, prec, width, mode


def _ora_group(s):
    parts = []
    k = len(s)
    while k > 3:
        parts.append(s[k - 3:k])
        k -= 3
    parts.append(s[:k])
    parts.reverse()
    return ",".join(parts)


def _ora_format(value, spec):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise _OraErr("type", -1)
    if not isinstance(spec, str):
        raise _OraErr("type", -1)
    if isinstance(value, float) and not math.isfinite(value):
        raise _OraErr("nonfinite", -1)
    fill, align, sign, group, prec, width, mode = _ora_spec(spec)
    with decimal.localcontext() as ctx:
        ctx.prec = 500
        dv = Decimal(value)
        units = int(dv.quantize(Decimal(1).scaleb(-prec),
                                rounding=_ORA_ROUND[mode]).scaleb(prec))
    if isinstance(value, float):
        negval = math.copysign(1.0, value) < 0
    else:
        negval = value < 0
    mag = abs(units)
    s = str(mag)
    if len(s) <= prec:
        s = "0" * (prec + 1 - len(s)) + s
    ip = s[:len(s) - prec] if prec else s
    fp = s[len(s) - prec:] if prec else ""
    if group:
        ip = _ora_group(ip)
    neg = negval or units < 0
    head = "-" if neg else ("+" if sign == "+" else (" " if sign == " " else ""))
    body = head + ip + ("." + fp if prec else "")
    pad = width - len(body)
    if pad <= 0:
        return body
    if align == "<":
        return body + fill * pad
    if align == ">":
        return fill * pad + body
    left = pad // 2
    return fill * left + body + fill * (pad - left)


# ==========================================================================
# handles on the candidate
# ==========================================================================
def _missing(*a, **k):
    raise AttributeError("attribute missing from numlit")


SCAN = getattr(numlit, "scan", _missing)
FMT = getattr(numlit, "format_number", _missing)
NE = getattr(numlit, "NumError", None)
_NE_OK = isinstance(NE, type) and issubclass(NE, BaseException)


class _NeverRaised(Exception):
    pass


_CATCH = NE if _NE_OK else _NeverRaised


def _c_scan(text):
    try:
        return ("ok", SCAN(text))
    except _CATCH as e:
        return ("err", getattr(e, "kind", "<no kind>"), getattr(e, "pos", "<no pos>"))
    except Exception as e:
        return ("boom", type(e).__name__)


def _o_scan(text):
    try:
        return ("ok", _ora_scan(text))
    except _OraErr as e:
        return ("err", e.kind, e.pos)


def _c_fmt(value, spec):
    try:
        return ("ok", FMT(value, spec))
    except _CATCH as e:
        return ("err", getattr(e, "kind", "<no kind>"), getattr(e, "pos", "<no pos>"))
    except Exception as e:
        return ("boom", type(e).__name__)


def _o_fmt(value, spec):
    try:
        return ("ok", _ora_format(value, spec))
    except _OraErr as e:
        return ("err", e.kind, e.pos)


def _core(res):
    """Reduce a scan result to the non-canonical-form core (no `text`)."""
    if res[0] != "ok" or not isinstance(res[1], list):
        return res
    out = []
    for r in res[1]:
        if not isinstance(r, dict):
            return ("bad-record",)
        try:
            out.append((r["kind"], r["radix"], r["value"], r["suffix"], r["start"]))
        except Exception:
            return ("bad-record",)
    return ("ok", out)


def _texts(res):
    if res[0] != "ok" or not isinstance(res[1], list):
        return res
    try:
        return ("ok", [r["text"] for r in res[1]])
    except Exception:
        return ("bad-record",)


def _core_pairs(texts):
    def probe():
        for t in texts:
            if _core(_c_scan(t)) != _core(_o_scan(t)):
                return False
        return True
    return probe


def _err_pairs(cases):
    """cases: list of (text, kind, pos)."""
    def probe():
        for t, kind, pos in cases:
            if _c_scan(t) != ("err", kind, pos):
                return False
        return True
    return probe


def _text_pairs(cases):
    def probe():
        for t, want in cases:
            if _texts(_c_scan(t)) != ("ok", want):
                return False
        return True
    return probe


def _fmt_pairs(cases):
    def probe():
        for value, spec, want in cases:
            if _c_fmt(value, spec) != ("ok", want):
                return False
        return True
    return probe


# ==========================================================================
# generators
# ==========================================================================
def _sprinkle(rng, d):
    if len(d) < 2 or rng.random() < 0.6:
        return d
    out = d[0]
    for ch in d[1:]:
        if rng.random() < 0.25 and out[-1] != "_":
            out += "_"
        out += ch
    return out


def _gen_int(rng):
    if rng.random() < 0.55:
        if rng.random() < 0.15:
            d = "0"
        else:
            d = rng.choice("123456789") + "".join(
                rng.choice(_ORA_D) for _ in range(rng.randint(0, 7)))
        core = _sprinkle(rng, d)
    else:
        pre, alpha = rng.choice([("0x", "0123456789abcdefABCDEF"),
                                 ("0o", "01234567"), ("0b", "01")])
        d = "".join(rng.choice(alpha) for _ in range(rng.randint(1, 8)))
        core = pre + _sprinkle(rng, d)
    return (rng.choice(["", "", "+", "-"]) + core
            + rng.choice(["", "", "", "u", "l"]))


def _gen_float(rng):
    ip = ""
    if rng.random() < 0.85:
        if rng.random() < 0.2:
            ip = "0"
        else:
            ip = rng.choice("123456789") + "".join(
                rng.choice(_ORA_D) for _ in range(rng.randint(0, 4)))
    dot = rng.random() < 0.8 or ip == ""
    core = _sprinkle(rng, ip) if ip else ""
    if dot:
        fp = "".join(rng.choice(_ORA_D) for _ in range(rng.randint(1, 6)))
        core += "." + _sprinkle(rng, fp)
    if (not dot) or rng.random() < 0.5:
        ed = "".join(rng.choice(_ORA_D) for _ in range(rng.randint(1, 2)))
        core += (rng.choice("eE") + rng.choice(["", "", "+", "-"])
                 + _sprinkle(rng, ed))
    return (rng.choice(["", "", "+", "-"]) + core
            + rng.choice(["", "", "", "s"]))


_ODD = "@#$%^&()[]{}!~`'\";:?/\\|<>=\t\né "


def _mutate(rng, s):
    op = rng.randint(0, 9)
    i = rng.randrange(len(s) + 1)
    if op == 0:
        return s[:i] + rng.choice(_ODD) + s[i:]
    if op == 1:
        return s[:i] + "_" + s[i:]
    if op == 2:
        return s[:i] + "." + s[i:]
    if op == 3:
        return s[:i] + rng.choice("ulse+-") + s[i:]
    if op == 4:
        return s[:i] + "0" + s[i:]
    if op == 5 and s:
        j = rng.randrange(len(s))
        return s[:j] + s[j + 1:]
    if op == 6:
        return s[:i] + rng.choice("xXoObB") + s[i:]
    if op == 7:
        return s.upper()
    if op == 8 and s:
        j = rng.randrange(len(s))
        return s[:j] + rng.choice("0123456789abefxoXO._+-") + s[j + 1:]
    return s + rng.choice(["e", "E", ".", "_", "+", "-", "u", "s"])


def _gen_value(rng):
    r = rng.random()
    if r < 0.20:
        k = rng.randint(0, 9)
        return rng.randint(-(10 ** k), 10 ** k)
    if r < 0.45:
        return rng.randint(-5000, 5000) + rng.choice(
            [0.5, 0.25, 0.75, 0.125, 0.375, 0.625, 0.875, 0.0625, 0.03125])
    if r < 0.58:
        return rng.choice([0.0, -0.0, 0.5, -0.5, 2.5, -2.5, 0.125, -0.125,
                           1.5, -1.5, 0.05, -0.05, 3.5, -3.5])
    if r < 0.82:
        return rng.randint(-(10 ** 6), 10 ** 6) / (2 ** rng.randint(0, 20))
    return rng.randint(-(10 ** 9), 10 ** 9) / (10 ** rng.randint(1, 6))


def _gen_spec(rng, mode=None):
    s = ""
    if rng.random() < 0.45:
        if rng.random() < 0.6:
            s += rng.choice("*.-_#xA 0")
        s += rng.choice("<>^")
    s += rng.choice(["", "", "+", "-", " "])
    if rng.random() < 0.3:
        s += ","
    if rng.random() < 0.45:
        s += str(rng.randint(1, 22))
    if rng.random() < 0.6:
        s += "." + str(rng.randint(0, 8))
    if mode is not None:
        s += mode
    elif rng.random() < 0.5:
        s += rng.choice("hudf")
    return s


# ==========================================================================
# 1-14: valid behaviour
# ==========================================================================
check("scan: empty text and start offsets",
      lambda: _c_scan("") == ("ok", [])
      and _core(_c_scan("42 -0x1f 3.5 7e2")) == _core(_o_scan("42 -0x1f 3.5 7e2"))
      and [r["start"] for r in SCAN("1 22 333 4")] == [0, 2, 5, 9])

check("scan: decimal integer values",
      _core_pairs(["0", "7", "42", "-7", "+3", "1234567890", "-1234567890",
                   "9", "-0", "+0", "1_000", "12_345_678", "-9_9"]))

check("scan: radix 16/8/2 integer values",
      _core_pairs(["0x0", "0x1F", "0xff", "0xFF", "0xdeadBEEF", "-0x10",
                   "+0x10", "0o0", "0o17", "-0o777", "0b0", "0b1010",
                   "-0b1111", "0x00ff", "0b0001", "0o007", "0x1_f", "0b1_0"]))

check("scan: float values are exact",
      _core_pairs([".5", "0.5", "1.25", "-1.25", "3.0", "0.0", "-0.0", "1e5",
                   "1E5", "1e+5", "1e-5", "-2.5e3", "0.1", "12.375",
                   "9.5e-3", "1e0", "0e0", ".125", "100.0", "7.0e2",
                   "1_0.2_5E+0_07", "1e000", "1e-0_3"]))

check("scan: signs and suffixes on valid literals",
      _core_pairs(["12u", "12l", "-12u", "+12l", "0xffu", "0b11l", "1.5s",
                   "-1.5s", "1e5s", ".5s", "0u", "0l", "0.0s", "+0.5s"]))

check("scan: underscores in legal positions",
      _core_pairs(["1_0", "1_000_000", "0x1_2_3", "0b1_0_1", "0o1_7",
                   "1_0.2_5", "1.0_1", "1e1_0", "1e+1_0", "1e-1_0",
                   "0.000_1", "1_2_3.4_5_6e7_8"]))

_rng = random.Random(20250901)
_VINT = [_gen_int(_rng) for _ in range(500)]
_VFLT = [_gen_float(_rng) for _ in range(500)]
_VLINE = []
for _i in range(220):
    _k = _rng.randint(0, 4)
    _VLINE.append(" ".join(
        (_gen_int(_rng) if _rng.random() < 0.5 else _gen_float(_rng))
        for _ in range(_k)))

check("scan differential: random valid integers", _core_pairs(_VINT))
check("scan differential: random valid floats", _core_pairs(_VFLT))
check("scan differential: random valid multi-field lines", _core_pairs(_VLINE))

check("format_number: defaults and precision",
      _fmt_pairs([(0, "", "0"), (7, "", "7"), (-7, "", "-7"), (1234, "", "1234"),
                  (1.0, ".3", "1.000"), (12.5, ".1", "12.5"),
                  (-12.5, ".1", "-12.5"), (0.0, ".2", "0.00"),
                  (3, ".4", "3.0000"), (1.25, ".1", "1.2"),
                  (1.75, ".1", "1.8"), (123456789, "", "123456789"),
                  (0.5, "", "0"), (1.5, "", "2"), (-1.5, "", "-2"),
                  (10 ** 20, "", "100000000000000000000")]))

check("format_number: width, fill and alignment",
      _fmt_pairs([(42, "6", "    42"), (42, "<6", "42    "),
                  (42, "^6", "  42  "), (42, "^7", "  42   "),
                  (42, "*>6", "****42"), (42, "*<6", "42****"),
                  (42, "*^7", "**42***"), (42, "2", "42"), (42, "1", "42"),
                  (-3.5, "8.1", "    -3.5"), (42, ">3", " 42"),
                  (1.5, "x^9.2", "xx1.50xxx")]))

check("format_number: grouping and sign policies",
      _fmt_pairs([(1234567, ",", "1,234,567"), (-1234567, ",", "-1,234,567"),
                  (100, ",", "100"), (1000, ",", "1,000"),
                  (1234.5678, ",.2", "1,234.57"), (12, "+", "+12"),
                  (12, "-", "12"), (12, " ", " 12"), (-12, "+", "-12"),
                  (-12, " ", "-12"), (0, "+", "+0"), (0, " ", " 0"),
                  (1234567.5, "+,.1", "+1,234,567.5"),
                  (999, ",", "999"), (1000000, ",", "1,000,000")]))


def _fmt_diff(cases):
    def probe():
        for value, spec in cases:
            if _c_fmt(value, spec) != _o_fmt(value, spec):
                return False
        return True
    return probe


_rng2 = random.Random(777001)
_FCASES = {}
for _m in "hudf":
    _FCASES[_m] = [(_gen_value(_rng2), _gen_spec(_rng2, _m)) for _ in range(320)]
_FMIX = [(_gen_value(_rng2), _gen_spec(_rng2)) for _ in range(400)]

check("format_number differential: modes h and u",
      _fmt_diff(_FCASES["h"] + _FCASES["u"]))
check("format_number differential: modes d and f",
      _fmt_diff(_FCASES["d"] + _FCASES["f"] + _FMIX))

# ==========================================================================
# 15-30: strictness
# ==========================================================================
_KEYS = ["kind", "radix", "value", "text", "suffix", "start"]


def _contract():
    if not (isinstance(NE, type) and issubclass(NE, ValueError)):
        return False
    try:
        SCAN("1  2")
        return False
    except NE as e:
        if getattr(e, "kind", None) != "space" or getattr(e, "pos", None) != 2:
            return False
        if not isinstance(e.kind, str) or not isinstance(e.pos, int):
            return False
    for t in ["0", "-7", "0x1F", "1.5", "-0.0", "1e5s", "0b1_0u"]:
        recs = SCAN(t)
        if not isinstance(recs, list) or len(recs) != 1:
            return False
        r = recs[0]
        if not isinstance(r, dict) or list(r.keys()) != _KEYS:
            return False
        w = _ora_scan(t)[0]
        for k in _KEYS:
            if r[k] != w[k] or type(r[k]) is not type(w[k]):
                return False
        if type(r["radix"]) is not int or type(r["start"]) is not int:
            return False
        if r["kind"] == "int" and type(r["value"]) is not int:
            return False
        if r["kind"] == "float" and type(r["value"]) is not float:
            return False
    if type(SCAN("3")[0]["value"]) is bool:
        return False
    return True


check("NumError contract, record key order and exact value types", _contract)


def _canon_text():
    cases = [("0", ["0"]), ("-0", ["0"]), ("+0", ["0"]), ("-7", ["-7"]),
             ("+7", ["7"]), ("1_000", ["1000"]), ("0x000", ["0x0"]),
             ("-0x00Ff", ["-0xff"]), ("0xFF", ["0xff"]),
             ("-0x0", ["0x0"]), ("0o007", ["0o7"]), ("0b0001", ["0b1"]),
             ("-0b0000", ["0b0"]), ("0x1_F", ["0x1f"]), ("+0o10", ["0o10"]),
             ("-0o0", ["0o0"]),
             (".5", ["0.5"]), ("1e5", ["1.0e5"]), ("1_0.2_5E+0_07", ["10.25e7"]),
             ("1e000", ["1.0e0"]), ("1e-0_3", ["1.0e-3"]), ("-0.0", ["-0.0"]),
             ("+0.0", ["0.0"]), ("-0e0", ["-0.0e0"]), ("0.50", ["0.50"]),
             ("3.0", ["3.0"]), ("-1.25e-2", ["-1.25e-2"]), ("1E+5", ["1.0e5"]),
             ("0.000", ["0.000"]), ("-.5", ["-0.5"]), ("1e-0", ["1.0e0"]),
             ("7e02", ["7.0e2"]), ("0.5s", ["0.5"]),
             ("42 -0x1f 3.5", ["42", "-0x1f", "3.5"])]
    for t, want in cases:
        if _texts(_c_scan(t)) != ("ok", want):
            return False
    for t in _VINT + _VFLT + _VLINE:
        if _texts(_c_scan(t)) != _texts(_o_scan(t)):
            return False
    return True


check("canonical text for integers, radix integers and floats", _canon_text)

check("error kind 'space' at the leftmost offence",
      _err_pairs([(" ", "space", 0), ("  ", "space", 0), (" 1", "space", 0),
                  ("1 ", "space", 1), ("1  2", "space", 2),
                  ("1 2  3", "space", 4), ("1   2", "space", 2),
                  ("12 34 ", "space", 5), (" 1 2", "space", 0),
                  ("\t ", "space", 1), ("1 2 ", "space", 3),
                  ("1 2  ", "space", 4), ("a  b", "space", 2)]))

check("error kinds 'char', 'sign', 'syntax' and 'exponent'",
      _err_pairs([("1\t2", "char", 1), ("é", "char", 0),
                  ("1;2", "char", 1), ("1@", "char", 1), ("1 2$", "char", 3),
                  ("a1&", "char", 2), ("1\n2", "char", 1),
                  ("+", "sign", 0), ("-", "sign", 0), ("1 +", "sign", 2),
                  ("-u", "suffix", 1), ("+s", "suffix", 1), ("u", "suffix", 0),
                  ("l", "suffix", 0), ("s", "suffix", 0),
                  ("1-2", "syntax", 1), ("1u5", "syntax", 1),
                  ("1.2.3", "syntax", 3), ("abc", "syntax", 0),
                  ("1+2", "syntax", 1), ("--1", "syntax", 1),
                  ("1e5e5", "syntax", 3), ("1.5.", "syntax", 3),
                  ("12x", "syntax", 2), ("1 1e2e", "syntax", 5),
                  ("1e", "exponent", 1), ("1e+", "exponent", 1),
                  ("1e-", "exponent", 1), ("1E", "exponent", 1),
                  ("1.5e", "exponent", 3), (".5E-", "exponent", 2),
                  ("-1e+", "exponent", 2)]))

check("error kinds 'prefix' and 'digit'",
      _err_pairs([("0X1", "prefix", 1), ("0O7", "prefix", 1),
                  ("0B1", "prefix", 1), ("-0X1f", "prefix", 2),
                  ("0X", "prefix", 1), ("0x", "prefix", 2), ("0o", "prefix", 2),
                  ("0b", "prefix", 2), ("-0x", "prefix", 3),
                  ("0xu", "prefix", 2), ("0xg", "digit", 2),
                  ("0x1g", "digit", 3), ("0o8", "digit", 2),
                  ("0o178", "digit", 4), ("0b2", "digit", 2),
                  ("0b1012", "digit", 5), ("0x1.5", "digit", 3),
                  ("0b1.0", "digit", 3), ("0xff.", "digit", 4),
                  ("0x1p3", "digit", 3), ("1 0o9", "digit", 4)]))

check("error kind 'underscore'",
      _err_pairs([("_1", "underscore", 0), ("1_", "underscore", 1),
                  ("1__2", "underscore", 1), ("0x_1", "underscore", 2),
                  ("0x1_", "underscore", 3), ("1_.5", "underscore", 1),
                  ("1._5", "underscore", 2), ("1e_5", "underscore", 2),
                  ("1e+_5", "underscore", 3), ("1_e5", "underscore", 1),
                  ("1.5_", "underscore", 3), ("1.5e5_", "underscore", 5),
                  ("_", "underscore", 0), ("__", "underscore", 0),
                  ("-_1", "underscore", 1), ("1_0._1", "underscore", 4),
                  ("0b1__0", "underscore", 3), ("1 1_", "underscore", 3),
                  ("1__0u", "underscore", 1)]))

check("error kind 'dangling_dot' and that .5 stays valid",
      lambda: _err_pairs(
          [("5.", "dangling_dot", 1), (".", "dangling_dot", 0),
           ("5.e3", "dangling_dot", 1), ("-5.", "dangling_dot", 2),
           ("0.", "dangling_dot", 1), ("1.E5", "dangling_dot", 1),
           ("12.", "dangling_dot", 2), ("1 2.", "dangling_dot", 3),
           (".e5", "dangling_dot", 0), ("-.", "dangling_dot", 1),
           (".s", "dangling_dot", 0)])()
      and _core(_c_scan(".5")) == _core(_o_scan(".5"))
      and _texts(_c_scan(".5 .125 -.5")) == ("ok", ["0.5", "0.125", "-0.5"]))

check("error kind 'leading_zero'",
      _err_pairs([("007", "leading_zero", 0), ("00", "leading_zero", 0),
                  ("01.5", "leading_zero", 0), ("0_1", "leading_zero", 0),
                  ("-007", "leading_zero", 1), ("+00", "leading_zero", 1),
                  ("0123456", "leading_zero", 0), ("00.5e3", "leading_zero", 0),
                  ("01e5", "leading_zero", 0), ("007u", "leading_zero", 0),
                  ("1 007", "leading_zero", 2), ("0_0", "leading_zero", 0),
                  ("00000", "leading_zero", 0)]))

check("error kind 'suffix' pairing",
      lambda: _err_pairs(
          [("1.5u", "suffix", 3), ("1.5l", "suffix", 3), ("1e5u", "suffix", 3),
           ("1e5l", "suffix", 3), (".5u", "suffix", 2), ("-1.5u", "suffix", 4),
           ("5s", "suffix", 1), ("0s", "suffix", 1), ("0xffs", "suffix", 4),
           ("0b1s", "suffix", 3), ("-42s", "suffix", 3), ("0o7s", "suffix", 3),
           ("1 2.5l", "suffix", 5)])()
      and _core(_c_scan("5u 5l 1.5s 0xffl .5s 1e5s")) ==
      _core(_o_scan("5u 5l 1.5s 0xffl .5s 1e5s")))

check("error precedence between the field checks",
      _err_pairs([("\t ", "space", 1), (" \t", "space", 0),
                  ("1\t2 ", "space", 3), ("+@", "char", 1), ("@+", "char", 0),
                  ("1_.@", "char", 3), ("0X1_", "prefix", 1),
                  ("0Xg", "prefix", 1), ("0xg_", "digit", 2),
                  ("0x_g", "digit", 3), ("_0.", "underscore", 0),
                  ("1_.", "underscore", 1), ("_1e", "underscore", 0),
                  ("007.", "dangling_dot", 3), ("00.", "dangling_dot", 2),
                  (".e", "dangling_dot", 0), ("00e", "exponent", 2),
                  ("007e", "exponent", 3), ("00s", "leading_zero", 0),
                  ("007u.", "syntax", 3), ("0_s", "underscore", 1),
                  ("00.5u", "leading_zero", 0), ("0_1s", "leading_zero", 0),
                  ("1e_5s", "underscore", 2), ("5.u", "dangling_dot", 1),
                  ("1.e5u", "dangling_dot", 1), ("1eu", "exponent", 1)]))

_rng3 = random.Random(4242042)
_MUT = []
while len(_MUT) < 900:
    _base = _gen_int(_rng3) if _rng3.random() < 0.5 else _gen_float(_rng3)
    _s = _mutate(_rng3, _base)
    if _rng3.random() < 0.3:
        _s = _mutate(_rng3, _s)
    try:                      # skip anything the spec's own arithmetic cannot do
        _ora_scan(_s)
    except _OraErr:
        pass
    except Exception:
        continue
    _MUT.append(_s)


def _mut_diff():
    seen_err = 0
    for t in _MUT:
        got, want = _c_scan(t), _o_scan(t)
        if want[0] == "err":
            seen_err += 1
            if got != want:
                return False
        else:
            if _core(got) != _core(want) or _texts(got) != _texts(want):
                return False
    return seen_err > 300


check("scan differential: mutated literals, exact kind and pos", _mut_diff)

_TIE = []
for _v in [0.5, -0.5, 1.5, -1.5, 2.5, -2.5, 3.5, -3.5, 4.5, -4.5, 0.0, -0.0]:
    _TIE.append((_v, ""))
for _v in [0.125, -0.125, 0.375, -0.375, 0.625, -0.625, 0.875, -0.875,
           2.125, -2.125, 10.625, -10.625, 0.25, -0.25, 0.75, -0.75]:
    _TIE.append((_v, ".2"))
for _v in [0.0625, -0.0625, 0.1875, -0.1875, 1.03125, -1.03125]:
    _TIE.append((_v, ".3"))
for _v in [2.675, -2.675, 1.005, -1.005, 8.835, -8.835]:
    _TIE.append((_v, ".2"))
for _v in [5, -5, 15, -15, 25, -25]:
    _TIE.append((_v, ""))


def _ties():
    for value, base in _TIE:
        for m in "hudf":
            if _c_fmt(value, base + m) != _o_fmt(value, base + m):
                return False
            if _c_fmt(value, base) != _o_fmt(value, base):
                return False
    return True


check("format_number: exact ties under every mode", _ties)

_NZ = [(-0.0, ".2", "-0.00"), (-0.0, "", "-0"), (-0.0, ".0", "-0"),
       (-0.001, ".2", "-0.00"), (-0.6, "d", "-0"), (-0.6, "", "-1"),
       (-0.4, "", "-0"), (-0.4, "u", "-0"), (-0.5, "d", "-0"),
       (-0.0, "+", "-0"), (-0.0, " ", "-0"), (-0.0, "+.3", "-0.000"),
       (0.0, ".2", "0.00"), (0.0, "+", "+0"), (0, "", "0"), (-0, "+", "+0"),
       (0, ".2", "0.00"), (-0.0001, ".3", "-0.000"), (-0.0, "6.2", " -0.00"),
       (-0.0, "<6.2", "-0.00 "), (-0.4, "f", "-1"), (-0.0, "f", "-0"),
       (0.4, "f", "0"), (-0.0, ",.2", "-0.00"), (-0.25, ".1", "-0.2"),
       (-0.25, ".1u", "-0.3"), (-0.05, ".1d", "-0.0")]

check("format_number: negative zero", _fmt_pairs(_NZ))


def _fmt_errs():
    class _Weird(object):
        pass
    cases = [((True, ""), ("type", -1)), ((False, ".2"), ("type", -1)),
             ((True, 5), ("type", -1)), (("1", ""), ("type", -1)),
             ((None, ""), ("type", -1)), (([1], ""), ("type", -1)),
             ((_Weird(), ""), ("type", -1)), ((1.0, 5), ("type", -1)),
             ((1, None), ("type", -1)), ((1, b""), ("type", -1)),
             ((True, "zzz"), ("type", -1)), ((float("nan"), 5), ("type", -1)),
             ((float("nan"), ""), ("nonfinite", -1)),
             ((float("inf"), ""), ("nonfinite", -1)),
             ((float("-inf"), ".2"), ("nonfinite", -1)),
             ((float("nan"), "zzz"), ("nonfinite", -1)),
             ((float("inf"), "0"), ("nonfinite", -1)),
             ((1.0, "0"), ("spec", -1)), ((1.0, "01"), ("spec", -1)),
             ((1.0, "."), ("spec", -1)), ((1.0, ".21"), ("spec", -1)),
             ((1.0, ".99"), ("spec", -1)), ((1.0, "201"), ("spec", -1)),
             ((1.0, "999"), ("spec", -1)), ((1.0, "z"), ("spec", -1)),
             ((1.0, ".2z"), ("spec", -1)), ((1.0, "++"), ("spec", -1)),
             ((1.0, ",,"), ("spec", -1)), ((1.0, ".2.3"), ("spec", -1)),
             ((1.0, "5,"), ("spec", -1)), ((1.0, "h5"), ("spec", -1)),
             ((1.0, "hh"), ("spec", -1)), ((1.0, "  "), ("spec", -1)),
             ((1.0, "*"), ("spec", -1)), ((1.0, "e"), ("spec", -1)),
             ((1.0, ".2h5"), ("spec", -1)), ((1.0, ",5.2u!"), ("spec", -1))]
    for (v, s), want in cases:
        if _c_fmt(v, s) != ("err",) + want:
            return False
    ok = [(1.0, ""), (1.0, ".20"), (1.0, "200"), (1.0, ".0"), (1.0, "1"),
          (1.0, "^"), (1.0, "*^"), (1.0, ",5.2u"), (1.0, " ,200.20f")]
    for v, s in ok:
        if _c_fmt(v, s) != _o_fmt(v, s):
            return False
    return True


check("format_number: error precedence and pos == -1", _fmt_errs)

# ---- bans ---------------------------------------------------------------
_BAN_MODS = {"re", "ast", "decimal", "fractions", "json"}
_BAN_CALLS = {"int", "float", "complex", "eval", "exec", "round", "format",
              "Decimal", "literal_eval"}


def _sig_tokens():
    src = inspect.getsource(numlit)
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    skip = (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
            tokenize.DEDENT, tokenize.ENDMARKER)
    return toks, [t for t in toks if t.type not in skip]


def _ban_calls():
    toks, sig = _sig_tokens()
    for i, t in enumerate(sig):
        if t.type == tokenize.NAME and t.string in _BAN_CALLS:
            nxt = sig[i + 1] if i + 1 < len(sig) else None
            if nxt is not None and nxt.type == tokenize.OP and nxt.string == "(":
                return False
        if t.type == tokenize.NAME and t.string == "__import__":
            for j in range(i + 1, min(i + 4, len(sig))):
                if sig[j].type == tokenize.STRING:
                    if sig[j].string.strip("'\"bru") in _BAN_MODS:
                        return False
    # import statements
    n = len(toks)
    for i, t in enumerate(toks):
        if t.type == tokenize.NAME and t.string in ("import", "from"):
            j = i + 1
            while j < n and toks[j].type not in (tokenize.NEWLINE, tokenize.NL):
                w = toks[j]
                if w.type == tokenize.NAME and w.string in _BAN_MODS:
                    return False
                if w.type == tokenize.STRING and \
                        w.string.strip("'\"bru") in _BAN_MODS:
                    return False
                j += 1
    return True


def _ban_fmt():
    toks, sig = _sig_tokens()
    for i, t in enumerate(sig):
        if t.type == tokenize.STRING:
            s = t.string
            if "{" in s and ":" in s and "}" in s:
                return False
            nxt = sig[i + 1] if i + 1 < len(sig) else None
            if nxt is not None and nxt.type == tokenize.OP and nxt.string == "%":
                return False
    # f-string format specifiers (Python 3.12+ tokenises them separately)
    _mid = getattr(tokenize, "FSTRING_MIDDLE", -99)
    for i, t in enumerate(sig):
        if t.type == _mid and i > 0 and sig[i - 1].type == tokenize.OP \
                and sig[i - 1].string in (":", "!"):
            return False
    return True


check("bans: forbidden modules and forbidden calls", _ban_calls)
check("bans: no percent or brace string formatting", _ban_fmt)

_t.cancel()
report()
