"""A small JSON serializer/parser with precise escaping and error positions."""

INF = float("inf")


class JsonError(ValueError):
    def __init__(self, kind, pos, doc):
        self.kind = kind
        self.pos = pos
        self.lineno = doc.count("\n", 0, pos) + 1
        self.colno = pos - doc.rfind("\n", 0, pos)
        ValueError.__init__(self, "%s: line %d column %d (char %d)"
                            % (kind, self.lineno, self.colno, pos))


# ---------------------------------------------------------------- dumps

_ESC = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t",
        "\b": "\\b", "\f": "\\f"}


def _escape(s, ensure_ascii):
    out = ['"']
    for ch in s:
        e = _ESC.get(ch)
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
            out.append("\\u%04x\\u%04x" % (0xD800 + (v >> 10), 0xDC00 + (v & 0x3FF)))
    out.append('"')
    return "".join(out)


def _floatstr(x, allow_nan):
    if x != x:
        t = "NaN"
    elif x == INF:
        t = "Infinity"
    elif x == -INF:
        t = "-Infinity"
    else:
        return repr(x)
    if not allow_nan:
        raise ValueError("out of range float value: %r" % (x,))
    return t


def _keystr(k):
    if isinstance(k, str):
        return k
    if isinstance(k, bool):
        return "true" if k else "false"
    if isinstance(k, int):
        return repr(k)
    if k is None:
        return "null"
    raise TypeError("unsupported key type: %s" % type(k).__name__)


def dumps(obj, *, ensure_ascii=True, sort_keys=False, indent=None,
          separators=None, allow_nan=True):
    if indent is None:
        ind = None
    elif isinstance(indent, str):
        ind = indent
    elif isinstance(indent, bool):
        raise TypeError("indent must be an int or a str")
    elif isinstance(indent, int):
        ind = " " * indent
    else:
        raise TypeError("indent must be an int or a str")

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
            return _escape(o, ensure_ascii)
        if isinstance(o, int):
            return repr(o)
        if isinstance(o, float):
            return _floatstr(o, allow_nan)
        if isinstance(o, dict):
            if not o:
                return "{}"
            items = [(_keystr(k), v) for k, v in o.items()]
            if sort_keys:
                items.sort(key=lambda kv: kv[0])
            if ind is None:
                body = item_sep.join(_escape(k, ensure_ascii) + key_sep
                                     + write(v, level) for k, v in items)
                return "{" + body + "}"
            nl = "\n" + ind * (level + 1)
            body = (item_sep + nl).join(
                _escape(k, ensure_ascii) + key_sep + write(v, level + 1)
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
        raise TypeError("unsupported type: %s" % type(o).__name__)

    return write(obj, 0)


# ---------------------------------------------------------------- loads

_WS = " \t\n\r"
_HEX = "0123456789abcdefABCDEF"
_DIGITS = "0123456789"
_SIMPLE = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f",
           "n": "\n", "r": "\r", "t": "\t"}
_LITERALS = [("true", True), ("false", False), ("null", None),
             ("NaN", float("nan")), ("Infinity", INF), ("-Infinity", -INF)]


def loads(s):
    n = len(s)

    def ws(i):
        while i < n and s[i] in _WS:
            i += 1
        return i

    def need(i):
        if i >= n:
            raise JsonError("eof", n, s)

    def scan_string(i):
        i += 1
        buf = []
        while True:
            if i >= n:
                raise JsonError("eof", n, s)
            c = s[i]
            if c == '"':
                return "".join(buf), i + 1
            if c == "\\":
                if i + 1 >= n:
                    raise JsonError("eof", n, s)
                e = s[i + 1]
                if e in _SIMPLE:
                    buf.append(_SIMPLE[e])
                    i += 2
                    continue
                if e != "u":
                    raise JsonError("escape", i, s)
                if i + 6 > n:
                    raise JsonError("eof", n, s)
                h = s[i + 2:i + 6]
                for ch in h:
                    if ch not in _HEX:
                        raise JsonError("escape", i, s)
                cp = int(h, 16)
                i += 6
                if 0xD800 <= cp <= 0xDBFF and s[i:i + 2] == "\\u" and i + 6 <= n:
                    h2 = s[i + 2:i + 6]
                    if all(ch in _HEX for ch in h2):
                        cp2 = int(h2, 16)
                        if 0xDC00 <= cp2 <= 0xDFFF:
                            cp = 0x10000 + ((cp - 0xD800) << 10) + (cp2 - 0xDC00)
                            i += 6
                buf.append(chr(cp))
                continue
            if ord(c) < 0x20:
                raise JsonError("control", i, s)
            buf.append(c)
            i += 1

    def scan_number(i):
        start = i
        if s[i] == "-":
            i += 1
            need(i)
            if s[i] not in _DIGITS:
                raise JsonError("value", i, s)
        isfloat = False
        if s[i] == "0":
            i += 1
        else:
            while i < n and s[i] in _DIGITS:
                i += 1
        if i < n and s[i] == ".":
            i += 1
            need(i)
            if s[i] not in _DIGITS:
                raise JsonError("value", i, s)
            while i < n and s[i] in _DIGITS:
                i += 1
            isfloat = True
        if i < n and s[i] in "eE":
            j = i + 1
            if j < n and s[j] in "+-":
                j += 1
            need(j)
            if s[j] not in _DIGITS:
                raise JsonError("value", j, s)
            while j < n and s[j] in _DIGITS:
                j += 1
            i = j
            isfloat = True
        tok = s[start:i]
        return (float(tok) if isfloat else int(tok)), i

    def scan_value(i, depth):
        need(i)
        for lit, val in _LITERALS:
            if s.startswith(lit, i):
                return val, i + len(lit)
        c = s[i]
        if c == '"':
            return scan_string(i)
        if c == "{":
            return scan_object(i, depth)
        if c == "[":
            return scan_array(i, depth)
        if c == "-" or c in _DIGITS:
            return scan_number(i)
        raise JsonError("value", i, s)

    def scan_array(i, depth):
        i = ws(i + 1)
        out = []
        need(i)
        if s[i] == "]":
            return out, i + 1
        while True:
            v, i = scan_value(i, depth + 1)
            out.append(v)
            i = ws(i)
            need(i)
            if s[i] == ",":
                i = ws(i + 1)
                continue
            if s[i] == "]":
                return out, i + 1
            raise JsonError("delimiter", i, s)

    def scan_object(i, depth):
        i = ws(i + 1)
        out = {}
        need(i)
        if s[i] == "}":
            return out, i + 1
        while True:
            need(i)
            if s[i] != '"':
                raise JsonError("key", i, s)
            k, i = scan_string(i)
            i = ws(i)
            need(i)
            if s[i] != ":":
                raise JsonError("delimiter", i, s)
            i = ws(i + 1)
            v, i = scan_value(i, depth + 1)
            out[k] = v
            i = ws(i)
            need(i)
            if s[i] == ",":
                i = ws(i + 1)
                continue
            if s[i] == "}":
                return out, i + 1
            raise JsonError("delimiter", i, s)

    i = ws(0)
    v, i = scan_value(i, 0)
    i = ws(i)
    if i != n:
        raise JsonError("extra", i, s)
    return v
