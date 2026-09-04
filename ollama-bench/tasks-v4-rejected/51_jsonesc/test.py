import sys, os, re, random, threading, inspect

TOTAL = 25
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
    import jsonesc
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

CJE = getattr(jsonesc, "JsonError", None)

# ===================================================================
# Inlined reference oracle (all names prefixed _o_ / _O_).
# ===================================================================

_O_INF = float("inf")


class _O_JsonError(ValueError):
    def __init__(self, kind, pos, doc):
        self.kind = kind
        self.pos = pos
        self.lineno = doc.count("\n", 0, pos) + 1
        self.colno = pos - doc.rfind("\n", 0, pos)
        ValueError.__init__(self, kind)


_O_ESC = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t",
          "\b": "\\b", "\f": "\\f"}


def _o_escape(s, ensure_ascii):
    out = ['"']
    for ch in s:
        e = _O_ESC.get(ch)
        if e is not None:
            out.append(e)
            continue
        o = ord(ch)
        if o < 0x20:
            out.append("\\u%04x" % o)
        elif o < 0x7F or not ensure_ascii:
            out.append(ch)
        elif o < 0x10000:
            out.append("\\u%04x" % o)
        else:
            v = o - 0x10000
            out.append("\\u%04x\\u%04x"
                       % (0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF)))
    out.append('"')
    return "".join(out)


def _o_floatstr(x, allow_nan):
    if x != x:
        t = "NaN"
    elif x == _O_INF:
        t = "Infinity"
    elif x == -_O_INF:
        t = "-Infinity"
    else:
        return repr(x)
    if not allow_nan:
        raise ValueError("out of range float")
    return t


def _o_keystr(k):
    if isinstance(k, str):
        return k
    if isinstance(k, bool):
        return "true" if k else "false"
    if isinstance(k, int):
        return repr(k)
    if k is None:
        return "null"
    raise TypeError("bad key type")


def _o_dumps(obj, ensure_ascii=True, sort_keys=False, indent=None,
             separators=None, allow_nan=True):
    if indent is None:
        ind = None
    elif isinstance(indent, str):
        ind = indent
    else:
        ind = " " * indent
    if separators is not None:
        item_sep, key_sep = separators
    elif ind is None:
        item_sep, key_sep = ", ", ": "
    else:
        item_sep, key_sep = ",", ": "

    def write(o, level):
        if o is None:
            return "null"
        if isinstance(o, bool):
            return "true" if o else "false"
        if isinstance(o, str):
            return _o_escape(o, ensure_ascii)
        if isinstance(o, int):
            return repr(o)
        if isinstance(o, float):
            return _o_floatstr(o, allow_nan)
        if isinstance(o, dict):
            if not o:
                return "{}"
            items = [(_o_keystr(k), v) for k, v in o.items()]
            if sort_keys:
                items.sort(key=lambda kv: kv[0])
            if ind is None:
                return "{" + item_sep.join(
                    _o_escape(k, ensure_ascii) + key_sep + write(v, level)
                    for k, v in items) + "}"
            nl = "\n" + ind * (level + 1)
            body = (item_sep + nl).join(
                _o_escape(k, ensure_ascii) + key_sep + write(v, level + 1)
                for k, v in items)
            return "{" + nl + body + "\n" + ind * level + "}"
        if isinstance(o, list):
            if not o:
                return "[]"
            if ind is None:
                return "[" + item_sep.join(write(v, level) for v in o) + "]"
            nl = "\n" + ind * (level + 1)
            body = (item_sep + nl).join(write(v, level + 1) for v in o)
            return "[" + nl + body + "\n" + ind * level + "]"
        raise TypeError("bad type")

    return write(obj, 0)


_O_WS = " \t\n\r"
_O_HEX = "0123456789abcdefABCDEF"
_O_DIG = "0123456789"
_O_SIMPLE = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
             "n": "\n", "r": "\r", "t": "\t"}
_O_LITS = [("true", True), ("false", False), ("null", None),
           ("NaN", float("nan")), ("Infinity", _O_INF), ("-Infinity", -_O_INF)]


def _o_loads(s):
    n = len(s)

    def ws(i):
        while i < n and s[i] in _O_WS:
            i += 1
        return i

    def need(i):
        if i >= n:
            raise _O_JsonError("eof", n, s)

    def scan_string(i):
        i += 1
        buf = []
        while True:
            if i >= n:
                raise _O_JsonError("eof", n, s)
            c = s[i]
            if c == '"':
                return "".join(buf), i + 1
            if c == "\\":
                if i + 1 >= n:
                    raise _O_JsonError("eof", n, s)
                e = s[i + 1]
                if e in _O_SIMPLE:
                    buf.append(_O_SIMPLE[e])
                    i += 2
                    continue
                if e != "u":
                    raise _O_JsonError("escape", i, s)
                if i + 6 > n:
                    raise _O_JsonError("eof", n, s)
                h = s[i + 2:i + 6]
                for ch in h:
                    if ch not in _O_HEX:
                        raise _O_JsonError("escape", i, s)
                cp = int(h, 16)
                i += 6
                if 0xD800 <= cp <= 0xDBFF and s[i:i + 2] == "\\u" and i + 6 <= n:
                    h2 = s[i + 2:i + 6]
                    if all(ch in _O_HEX for ch in h2):
                        cp2 = int(h2, 16)
                        if 0xDC00 <= cp2 <= 0xDFFF:
                            cp = 0x10000 + ((cp - 0xD800) << 10) + (cp2 - 0xDC00)
                            i += 6
                buf.append(chr(cp))
                continue
            if ord(c) < 0x20:
                raise _O_JsonError("control", i, s)
            buf.append(c)
            i += 1

    def scan_number(i):
        start = i
        if s[i] == "-":
            i += 1
            need(i)
            if s[i] not in _O_DIG:
                raise _O_JsonError("value", i, s)
        isf = False
        if s[i] == "0":
            i += 1
        else:
            while i < n and s[i] in _O_DIG:
                i += 1
        if i < n and s[i] == ".":
            i += 1
            need(i)
            if s[i] not in _O_DIG:
                raise _O_JsonError("value", i, s)
            while i < n and s[i] in _O_DIG:
                i += 1
            isf = True
        if i < n and s[i] in "eE":
            j = i + 1
            if j < n and s[j] in "+-":
                j += 1
            need(j)
            if s[j] not in _O_DIG:
                raise _O_JsonError("value", j, s)
            while j < n and s[j] in _O_DIG:
                j += 1
            i = j
            isf = True
        tok = s[start:i]
        return (float(tok) if isf else int(tok)), i

    def scan_value(i):
        need(i)
        for lit, val in _O_LITS:
            if s.startswith(lit, i):
                return val, i + len(lit)
        c = s[i]
        if c == '"':
            return scan_string(i)
        if c == "{":
            return scan_object(i)
        if c == "[":
            return scan_array(i)
        if c == "-" or c in _O_DIG:
            return scan_number(i)
        raise _O_JsonError("value", i, s)

    def scan_array(i):
        i = ws(i + 1)
        out = []
        need(i)
        if s[i] == "]":
            return out, i + 1
        while True:
            v, i = scan_value(i)
            out.append(v)
            i = ws(i)
            need(i)
            if s[i] == ",":
                i = ws(i + 1)
                continue
            if s[i] == "]":
                return out, i + 1
            raise _O_JsonError("delimiter", i, s)

    def scan_object(i):
        i = ws(i + 1)
        out = {}
        need(i)
        if s[i] == "}":
            return out, i + 1
        while True:
            need(i)
            if s[i] != '"':
                raise _O_JsonError("key", i, s)
            k, i = scan_string(i)
            i = ws(i)
            need(i)
            if s[i] != ":":
                raise _O_JsonError("delimiter", i, s)
            i = ws(i + 1)
            v, i = scan_value(i)
            out[k] = v
            i = ws(i)
            need(i)
            if s[i] == ",":
                i = ws(i + 1)
                continue
            if s[i] == "}":
                return out, i + 1
            raise _O_JsonError("delimiter", i, s)

    i = ws(0)
    v, i = scan_value(i)
    i = ws(i)
    if i != n:
        raise _O_JsonError("extra", i, s)
    return v


def _o_canon(v):
    if v is None or isinstance(v, bool):
        return ("b", repr(v))
    if isinstance(v, float):
        return ("f", repr(v))
    if isinstance(v, int):
        return ("i", repr(v))
    if isinstance(v, str):
        return ("s", v)
    if isinstance(v, list):
        return ("l", tuple(_o_canon(x) for x in v))
    if isinstance(v, dict):
        return ("d", tuple(sorted((k, _o_canon(x)) for k, x in v.items())))
    return ("?", type(v).__name__)


def _o_probe(loader, s, exc):
    try:
        v = loader(s)
    except BaseException as e:
        if exc is not None and isinstance(e, exc):
            return ("err", getattr(e, "kind", "<none>"), getattr(e, "pos", None),
                    getattr(e, "lineno", None), getattr(e, "colno", None))
        return ("boom", type(e).__name__)
    try:
        return ("ok", _o_canon(v))
    except Exception:
        return ("boom", "canon")


def _o_want(s):
    return _o_probe(_o_loads, s, _O_JsonError)


def _c_got(s):
    return _o_probe(jsonesc.loads, s, CJE)


def _c_dump(obj, **kw):
    try:
        return ("ok", jsonesc.dumps(obj, **kw))
    except BaseException as e:
        return ("exc", type(e).__name__)


def _o_want_dump(obj, **kw):
    try:
        return ("ok", _o_dumps(obj, **kw))
    except BaseException as e:
        return ("exc", type(e).__name__)


# ===================================================================
# Case generation (fixed seed)
# ===================================================================

_CHARS = [
    "a", "b", "Z", "0", " ", "~", "!", "/", '"', "\\", "'",
    "\u0000", "\u0001", "\u0007", "\u000b", "\u001f", "\u007f",
    "\n", "\r", "\t", "\b", "\f",
    "\u00e9", "\u00ff", "\u07ff", "\u0800", "\u2028", "\ud7ff", "\ue000",
    "\uffff", "\U0001f600", "\U0010ffff", "\ud800", "\udbff", "\udc00",
    "\udfff",
]

_FLOATS = [
    0.0, -0.0, 1.0, -1.0, 2.0, 100.0, 0.1, 0.5, -2.75, 1e16, 1e17, 1e22,
    1e-4, 1e-5, 1e-7, 1.0 / 3.0, 3.0, 1e308, 5e-324, 2.0 ** 53,
    1.7976931348623157e308, 1234567890.0, float("inf"), float("-inf"),
    float("nan"), -1e-323, 6.02e23, 0.30000000000000004,
]

_INTS = [0, -0, 1, -1, 10, 255, -12345, 2 ** 63, -(2 ** 63) - 1, 10 ** 25,
         -(10 ** 30), 9007199254740993]


def _rand_str(rng):
    return "".join(rng.choice(_CHARS) for _ in range(rng.randint(0, 5)))


def _rand_key(rng, allow_nonstr):
    r = rng.random()
    if allow_nonstr and r < 0.30:
        k = rng.randint(0, 3)
        if k == 0:
            return rng.choice([True, False])
        if k == 1:
            return None
        if k == 2:
            return rng.randint(-1000, 1000)
        return rng.choice([10 ** 20, -7, 0])
    return _rand_str(rng)


def _rand_scalar(rng, finite_only=False):
    k = rng.randint(0, 6)
    if k == 0:
        return _rand_str(rng)
    if k == 1:
        return rng.choice([True, False, None])
    if k in (2, 3):
        f = rng.choice(_FLOATS)
        if finite_only and (f != f or f in (_O_INF, -_O_INF)):
            return 0.5
        return f
    if k == 4:
        return rng.choice(_INTS)
    if k == 5:
        return rng.uniform(-1e6, 1e6)
    return rng.randint(-9, 9)


def _rand_value(rng, depth=0, allow_nonstr=False, finite_only=False):
    r = rng.random()
    if depth >= 3 or r < 0.45:
        return _rand_scalar(rng, finite_only)
    if r < 0.72:
        return [_rand_value(rng, depth + 1, allow_nonstr, finite_only)
                for _ in range(rng.randint(0, 4))]
    return dict((_rand_key(rng, allow_nonstr),
                 _rand_value(rng, depth + 1, allow_nonstr, finite_only))
                for _ in range(rng.randint(0, 4)))


def _values(seed, n, allow_nonstr=False, finite_only=False):
    rng = random.Random(seed)
    return [_rand_value(rng, 0, allow_nonstr, finite_only) for _ in range(n)]


def dump_bucket(vals, kwargs_list, lo, hi):
    def probe():
        for i, v in enumerate(vals[lo:hi]):
            kw = kwargs_list[(i + lo) % len(kwargs_list)]
            if _c_dump(v, **kw) != _o_want_dump(v, **kw):
                return False
        return True
    return probe


def loads_bucket(docs, lo, hi):
    def probe():
        for d in docs[lo:hi]:
            if _c_got(d) != _o_want(d):
                return False
        return True
    return probe


# ===================================================================
# 1: hygiene / API
# ===================================================================


def api_ok():
    src = inspect.getsource(jsonesc)
    if re.search(r"^\s*(import\s+(json|simplejson|ujson|orjson)\b"
                 r"|from\s+(json|simplejson|ujson|orjson)\b)", src, re.M):
        return False
    if not callable(getattr(jsonesc, "dumps", None)):
        return False
    if not callable(getattr(jsonesc, "loads", None)):
        return False
    if not (isinstance(CJE, type) and issubclass(CJE, ValueError)):
        return False
    return True


check("no json import; dumps/loads/JsonError(ValueError) exported", api_ok)

# ===================================================================
# 2-4: dumps, default options
# ===================================================================

VALS_A = _values(1001, 240)
DEFAULT = [{}]
check("dumps default options A", dump_bucket(VALS_A, DEFAULT, 0, 80))
check("dumps default options B", dump_bucket(VALS_A, DEFAULT, 80, 160))
check("dumps default options C", dump_bucket(VALS_A, DEFAULT, 160, 240))

# ===================================================================
# 5-6: ensure_ascii=False
# ===================================================================

VALS_B = _values(1002, 160)
NOASCII = [{"ensure_ascii": False}]
check("dumps ensure_ascii=False A", dump_bucket(VALS_B, NOASCII, 0, 80))
check("dumps ensure_ascii=False B", dump_bucket(VALS_B, NOASCII, 80, 160))

# ===================================================================
# 7-8: indent
# ===================================================================

VALS_C = _values(1003, 160)
INDENTS = [{"indent": 2}, {"indent": 0}, {"indent": "\t"}, {"indent": 4},
           {"indent": 1, "ensure_ascii": False}, {"indent": "..."}]
check("dumps with indent A", dump_bucket(VALS_C, INDENTS, 0, 80))
check("dumps with indent B", dump_bucket(VALS_C, INDENTS, 80, 160))

# ===================================================================
# 9-10: separators
# ===================================================================

VALS_D = _values(1004, 160)
SEPS = [{"separators": (",", ":")},
        {"separators": (" , ", " : ")},
        {"separators": (",", ":"), "indent": 2},
        {"separators": (", ", ": "), "indent": 2},
        {"separators": ("|", "="), "indent": "\t"},
        {"separators": (",\n", ": ")}]
check("dumps with custom separators A", dump_bucket(VALS_D, SEPS, 0, 80))
check("dumps with custom separators B", dump_bucket(VALS_D, SEPS, 80, 160))

# ===================================================================
# 11: sort_keys
# ===================================================================

VALS_E = _values(1005, 120, allow_nonstr=True)
SORTED_KW = [{"sort_keys": True}, {"sort_keys": True, "indent": 2},
             {"sort_keys": True, "ensure_ascii": False},
             {"sort_keys": True, "separators": (",", ":")}]
check("dumps sort_keys", dump_bucket(VALS_E, SORTED_KW, 0, 120))

# ===================================================================
# 12: non-string keys
# ===================================================================

KEYCASES = [
    {1: "a"}, {True: 1, False: 2}, {None: 0}, {0: 0, -0: 1},
    {10 ** 20: 1}, {-5: [1, 2]}, {"1": "s", 2: "i"},
    {1: 1, "1": 2}, {True: 1, "true": 2}, {None: 1, "null": 2},
    {"b": 1, 10: 2, None: 3, False: 4},
    {"\u00e9": 1, 7: 2}, {"a\"b": 1, "c\\d": 2},
    {"": 0}, {" ": 0, "\n": 1},
]


def keycases():
    for kw in ({}, {"sort_keys": True}, {"indent": 2},
               {"sort_keys": True, "separators": (",", ":")}):
        for d in KEYCASES:
            if _c_dump(d, **kw) != _o_want_dump(d, **kw):
                return False
    return True


check("dumps coerces non-string keys", keycases)

# ===================================================================
# 13: allow_nan
# ===================================================================


def nan_cases():
    nan = float("nan")
    inf = _O_INF
    cases = [nan, inf, -inf, [1, nan], {"a": inf}, [[[-inf]]],
             {"a": [1.0, 2.0]}, [1, 2], {"x": {"y": nan}}, [inf, 1, nan],
             {True: nan}, 1.5, "NaN", [0.0, -0.0]]
    for c in cases:
        for kw in ({"allow_nan": False}, {"allow_nan": True},
                   {"allow_nan": False, "indent": 2},
                   {"allow_nan": True, "separators": (",", ":")}):
            got = _c_dump(c, **kw)
            want = _o_want_dump(c, **kw)
            if got != want:
                return False
    return True


check("dumps allow_nan", nan_cases)

# ===================================================================
# 14: TypeError for unsupported values and keys
# ===================================================================


def type_errors():
    bad = [(1, 2), set([1]), b"x", bytearray(b"x"), object(), 1 + 2j,
           [1, (2,)], {"a": {1, 2}}, {"a": [None, b"z"]},
           {(1, 2): 1}, {1.5: 1}, {b"k": 1}, {"a": {2.5: 1}}]
    for c in bad:
        for kw in ({}, {"indent": 2}):
            got = _c_dump(c, **kw)
            if got != ("exc", "TypeError"):
                return False
    ok = [{"a": 1}, [1, 2], 1.5, "x", None, True, {}, []]
    for c in ok:
        if _c_dump(c)[0] != "ok":
            return False
    return True


check("dumps raises TypeError for unsupported values/keys", type_errors)

# ===================================================================
# 15: float formatting corners
# ===================================================================


def float_corners():
    vals = list(_FLOATS) + [
        -0.0, 1e15, 1e16, 123456789012345680.0, 0.0001, 0.00001,
        1e100, -1e-100, 4.9e-324, 2.220446049250313e-16, 1e21, 1e20,
        99999999999999999999.0, 0.1 + 0.2, -3.0, 7.0, 1e-323,
    ]
    for v in vals:
        for kw in ({}, {"ensure_ascii": False}, {"indent": 2}):
            if _c_dump([v], **kw) != _o_want_dump([v], **kw):
                return False
            if _c_dump(v, **kw) != _o_want_dump(v, **kw):
                return False
    for v in _INTS + [True, False, None]:
        if _c_dump(v) != _o_want_dump(v):
            return False
    return True


check("dumps number formatting corners", float_corners)

# ===================================================================
# 16: string escaping corners
# ===================================================================


def string_corners():
    single = [c for c in _CHARS]
    combos = ["", "/", "a/b", "\\/", "\u0000\u001f\u007f",
              "line\nnext", "tab\there", "\"q\"", "back\\slash",
              "\U0001f600\U0001f600", "\ud83d", "\ude00",
              "\ud83d\ud83d\ude00", "\u2028\u2029", "\u00ad\u200b",
              "e\u0301", "\u007e\u007f\u0080", "\ud800a\udc00",
              "abc" * 5]
    for s in single + combos:
        for kw in ({}, {"ensure_ascii": False}):
            if _c_dump(s, **kw) != _o_want_dump(s, **kw):
                return False
            if _c_dump({s: s}, **kw) != _o_want_dump({s: s}, **kw):
                return False
    return True


check("dumps string escaping corners", string_corners)

# ===================================================================
# valid documents for loads
# ===================================================================

_DOC_KW = [{}, {"indent": 2}, {"indent": 0}, {"ensure_ascii": False},
           {"separators": (" , ", " : ")}, {"separators": (",", ":")},
           {"separators": ("\t,\t", "\t:\t")}, {"indent": "\t"},
           {"ensure_ascii": False, "indent": 1}]


def _make_docs(seed, n):
    rng = random.Random(seed)
    vals = _values(seed + 7, n)
    docs = []
    for i, v in enumerate(vals):
        kw = _DOC_KW[i % len(_DOC_KW)]
        d = _o_dumps(v, **kw)
        pre = "".join(rng.choice(_O_WS) for _ in range(rng.randint(0, 3)))
        post = "".join(rng.choice(_O_WS) for _ in range(rng.randint(0, 3)))
        docs.append(pre + d + post)
    return docs


DOCS = _make_docs(2001, 240)
check("loads valid documents A", loads_bucket(DOCS, 0, 80))
check("loads valid documents B", loads_bucket(DOCS, 80, 160))
check("loads valid documents C", loads_bucket(DOCS, 160, 240))

# ===================================================================
# 20: number tokens
# ===================================================================


def number_docs():
    docs = ["0", "-0", "0.0", "-0.0", "1", "-1", "1.0", "1e2", "1E2", "1e+2",
            "1e-2", "1e0", "1E-0", "0e0", "0.5", "-0.5e-3", "1e400", "-1e400",
            "1e-400", "123456789012345678901234567890", "1.5e300",
            "0.000001", "10000000000000000", "1e007", "-0e-0", "9007199254740993",
            "1.7976931348623157e308", "5e-324", "2.5E+00010", "0.1",
            "NaN", "Infinity", "-Infinity", "[NaN, Infinity, -Infinity]",
            "[0, -0, 0.0, -0.0]", "{\"a\": 1e400, \"b\": -0.0}"]
    rng = random.Random(2222)
    for _ in range(140):
        s = ""
        if rng.random() < 0.5:
            s += "-"
        s += rng.choice(["0", "1", "9", "12", "907", "100000", "3"])
        if rng.random() < 0.6:
            s += "." + rng.choice(["0", "5", "25", "000", "999999999999999999"])
        if rng.random() < 0.6:
            s += rng.choice(["e", "E"]) + rng.choice(["", "+", "-"]) + \
                rng.choice(["0", "1", "7", "17", "300", "400", "0007"])
        docs.append(s)
    for d in docs:
        if _c_got(d) != _o_want(d):
            return False
    return True


check("loads number tokens", number_docs)

# ===================================================================
# 21: string escapes
# ===================================================================


def escape_docs():
    docs = ['""', '"a"', '"\\u0000"', '"\\u001f"', '"\\u007f"', '"\\/"', '"/"',
            '"\\\\"', '"\\""', '"\\b\\f\\n\\r\\t"', '"\\u00e9"', '"\\u2028"',
            '"\\ud83d\\ude00"', '"\\uD83D\\uDE00"', '"\\ud800"', '"\\udfff"',
            '"\\ud800a"', '"\\ud800\\ud800"', '"\\ud800\\u0041"',
            '"\\udc00\\udc00"', '"\\ud800\\udbff"', '"a\\ud83d\\ude00b"',
            '"\\uffff"', '"\\uFFFF"', '"\\u0041\\u0042"', '"\\ud83dx"',
            '"\\ud800\\udc00\\ud800"', '"\\uabcd\\uABCD"']
    rng = random.Random(3333)
    pieces = ['\\"', "\\\\", "\\/", "\\b", "\\f", "\\n", "\\r", "\\t",
              "\\u0041", "\\u00e9", "\\ud83d", "\\ude00", "\\ud83d\\ude00",
              "\\u0000", "\\u001f", "\\uD800", "\\uDC00", "a", "z", " ", "/",
              "\u00e9", "\U0001f600"]
    for _ in range(140):
        body = "".join(rng.choice(pieces) for _ in range(rng.randint(0, 6)))
        docs.append('"' + body + '"')
    for d in docs:
        if _c_got(d) != _o_want(d):
            return False
    return True


check("loads string escapes and surrogates", escape_docs)

# ===================================================================
# 22-24: malformed documents / error positions
# ===================================================================

BADDOCS = ["", " ", "   \n  ", "[", "{", "[1", "[1,", "[1,]", "[,1]", "[1,,2]",
           "{\"a\"", "{\"a\":", "{\"a\":1", "{\"a\":1,", "{\"a\":1,}", "{,}",
           "{1:2}", "{'a':1}", "{\"a\" 1}", "{\"a\"::1}", "[01]", "01", "1 2",
           "nul", "tru", "truex", "[tru]", "nullx", "NaNx", "Infinit",
           "\"abc", "\"ab\\", "\"ab\\x\"", "\"ab\\u12\"", "\"ab\\u12g4\"",
           "\"ab\\U0041\"", "\"a\nb\"", "\"a\u0001b\"", "\"a\u007fb\"",
           "-", "-x", "1.", "1.x", "1e", "1e+", "1e+x", "+1", ".5", "[.5]",
           "[1.]", "[00]", "[-]", "[--1]", "[+1]", "[1 2]", "[]]", "[}",
           "{]", "x", "@", "\ud800", "[1,2]]", "{\"a\":1}}", "[[[]]",
           "\n\n  [1,\n 2 3]", "{\n \"a\": 1,\n \"b\" 2\n}",
           "[\n  1,\n  \"a\nb\"\n]", "\t{\"k\"\t:\t}", "[\"\\ud800\\u00zz\"]",
           "{\"a\":1,\"a\"}", "[true,]", "[1][2]", "  1  2  ",
           "{\"\\u0041\":1,}", "[\"\\\"]"]

_MUT_CHARS = list("{}[],:\"\\ xu0-e.19tn") + ["\n", "\t", " ", "\u0001",
                                             "\u001f", "\u00e9"]


def _mutations(seed, n):
    rng = random.Random(seed)
    base = []
    for v in _values(seed + 11, 60):
        base.append(_o_dumps(v, **_DOC_KW[rng.randrange(len(_DOC_KW))]))
    base += ['{"a": [1, "b\\u00e9", true], "c": {"d": null}}',
             '[1.5e3, -0.0, "\\ud83d\\ude00", {"k": []}]',
             '{"x":{"y":{"z":[1,2,3]}}}', '["a\\/b", "c\\\\d", "\\u001f"]']
    out = []
    while len(out) < n:
        d = base[rng.randrange(len(base))]
        if len(d) > 120:
            continue
        m = rng.randint(0, 3)
        if not d:
            continue
        p = rng.randrange(len(d))
        if m == 0:
            s = d[:p] + d[p + 1:]
        elif m == 1:
            s = d[:p] + rng.choice(_MUT_CHARS) + d[p:]
        elif m == 2:
            s = d[:p] + rng.choice(_MUT_CHARS) + d[p + 1:]
        else:
            s = d[:p]
        out.append(s)
    return out


MUTS = _mutations(4001, 450)
check("loads error reporting on mutated documents A", loads_bucket(MUTS, 0, 150))
check("loads error reporting on mutated documents B", loads_bucket(MUTS, 150, 300))


def bad_explicit():
    for d in BADDOCS:
        if _c_got(d) != _o_want(d):
            return False
    return True


check("loads error reporting on malformed documents", bad_explicit)
check("loads error reporting on mutated documents C", loads_bucket(MUTS, 300, 450))

# ===================================================================
# 25: round trip
# ===================================================================


def _desurrogate(v):
    # An adjacent pair of lone surrogates re-combines on the way back in, so
    # the round trip is only the identity for strings without surrogates.
    if isinstance(v, str):
        return "".join("S" if 0xD800 <= ord(c) <= 0xDFFF else c for c in v)
    if isinstance(v, list):
        return [_desurrogate(x) for x in v]
    if isinstance(v, dict):
        return dict((_desurrogate(k), _desurrogate(x)) for k, x in v.items())
    return v


def round_trip():
    vals = [_desurrogate(v) for v in _values(5006, 120)]
    for i, v in enumerate(vals):
        kw = _DOC_KW[i % len(_DOC_KW)]
        r = _c_dump(v, **kw)
        if r[0] != "ok":
            return False
        got = _c_got(r[1])
        try:
            want = ("ok", _o_canon(v))
        except Exception:
            return False
        if got != want:
            return False
        if _o_want(r[1]) != want:
            return False
    return True


check("loads(dumps(x)) round trip", round_trip)

_t.cancel()
report()
