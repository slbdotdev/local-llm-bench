"""RFC-3986-style URI parsing, normalisation and reference resolution.

The module deliberately uses no imports at all (re / urllib / posixpath /
ipaddress / string / binascii are all forbidden).
"""

_ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_DIGIT = "0123456789"
_UNRESERVED = frozenset(_ALPHA + _DIGIT + "-._~")
_SUBDELIMS = frozenset("!$&'()*+,;=")
_HEX = frozenset("0123456789abcdefABCDEF")
_SCHEME_TAIL = frozenset(_ALPHA + _DIGIT + "+-.")
_ALPHA_SET = frozenset(_ALPHA)
_DIGIT_SET = frozenset(_DIGIT)

_HOST_OK = _UNRESERVED | _SUBDELIMS | frozenset("%")
_USERINFO_OK = _HOST_OK | frozenset(":")
_PATH_OK = _USERINFO_OK | frozenset("@/")
_QF_OK = _PATH_OK | frozenset("?")

KEYS = ("scheme", "userinfo", "host", "port", "path", "query", "fragment")

_DEFAULT_PORTS = {"http": "80", "https": "443", "ws": "80", "wss": "443"}

_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_LOWER = "abcdefghijklmnopqrstuvwxyz"


class UriError(ValueError):
    def __init__(self, kind, message=None):
        ValueError.__init__(self, message if message is not None else kind)
        self.kind = kind


def _lower(s):
    out = []
    for ch in s:
        i = _UPPER.find(ch)
        out.append(_LOWER[i] if i >= 0 else ch)
    return "".join(out)


def _upper(s):
    out = []
    for ch in s:
        i = _LOWER.find(ch)
        out.append(_UPPER[i] if i >= 0 else ch)
    return "".join(out)


def _is_scheme(s):
    if not s or s[0] not in _ALPHA_SET:
        return False
    for ch in s[1:]:
        if ch not in _SCHEME_TAIL:
            return False
    return True


def _bad_escape(s):
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "%":
            if i + 2 >= n or s[i + 1] not in _HEX or s[i + 2] not in _HEX:
                return True
            i += 3
        else:
            i += 1
    return False


def _bad_chars(s, ok):
    for ch in s:
        if ch not in ok:
            return True
    return False


def parse(s):
    if not isinstance(s, str):
        raise UriError("type", "parse() needs a str")
    rest = s
    fragment = None
    h = rest.find("#")
    if h >= 0:
        fragment = rest[h + 1:]
        rest = rest[:h]
    query = None
    q = rest.find("?")
    if q >= 0:
        query = rest[q + 1:]
        rest = rest[:q]
    scheme = None
    c = rest.find(":")
    sl = rest.find("/")
    if c >= 0 and (sl < 0 or c < sl):
        cand = rest[:c]
        if not _is_scheme(cand):
            raise UriError("scheme", "bad scheme %r" % (cand,))
        scheme = cand
        rest = rest[c + 1:]
    userinfo = host = port = None
    if rest[:2] == "//":
        auth = rest[2:]
        j = auth.find("/")
        if j >= 0:
            path = auth[j:]
            auth = auth[:j]
        else:
            path = ""
        at = auth.rfind("@")
        if at >= 0:
            userinfo = auth[:at]
            hp = auth[at + 1:]
        else:
            hp = auth
        cp = hp.rfind(":")
        if cp >= 0:
            host = hp[:cp]
            port = hp[cp + 1:]
        else:
            host = hp
    else:
        path = rest
    if port is not None and _bad_chars(port, _DIGIT_SET):
        raise UriError("port", "bad port %r" % (port,))
    if host is not None and _bad_chars(host, _HOST_OK):
        raise UriError("host", "bad host %r" % (host,))
    if userinfo is not None and _bad_chars(userinfo, _USERINFO_OK):
        raise UriError("userinfo", "bad userinfo")
    if _bad_chars(path, _PATH_OK):
        raise UriError("char", "bad character in path")
    if query is not None and _bad_chars(query, _QF_OK):
        raise UriError("char", "bad character in query")
    if fragment is not None and _bad_chars(fragment, _QF_OK):
        raise UriError("char", "bad character in fragment")
    if _bad_escape(s):
        raise UriError("escape", "malformed percent-escape")
    return {"scheme": scheme, "userinfo": userinfo, "host": host, "port": port,
            "path": path, "query": query, "fragment": fragment}


def unparse(d):
    if not isinstance(d, dict):
        raise UriError("type", "unparse() needs a dict")
    if set(d.keys()) != set(KEYS):
        raise UriError("form", "wrong key set")
    for k in KEYS:
        v = d[k]
        if v is not None and not isinstance(v, str):
            raise UriError("type", "component %s is not a str" % k)
    scheme = d["scheme"]
    userinfo = d["userinfo"]
    host = d["host"]
    port = d["port"]
    path = d["path"]
    query = d["query"]
    fragment = d["fragment"]
    if path is None:
        raise UriError("form", "path must be a str")
    if host is None and (userinfo is not None or port is not None):
        raise UriError("form", "userinfo/port without a host")
    if host is not None and path != "" and path[:1] != "/":
        raise UriError("form", "authority with a rootless non-empty path")
    if host is None and path[:2] == "//":
        raise UriError("form", "path starting with // and no authority")
    if scheme is None and host is None and ":" in path.split("/")[0]:
        raise UriError("form", "colon in the first segment of a relative path")
    out = ""
    if scheme is not None:
        out += scheme + ":"
    if host is not None:
        out += "//"
        if userinfo is not None:
            out += userinfo + "@"
        out += host
        if port is not None:
            out += ":" + port
    out += path
    if query is not None:
        out += "?" + query
    if fragment is not None:
        out += "#" + fragment
    return out


def _pct(s, lower_literals=False):
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "%":
            hx = _upper(s[i + 1:i + 3])
            dec = chr(int(hx, 16))
            if dec in _UNRESERVED:
                out.append(_lower(dec) if lower_literals else dec)
            else:
                out.append("%" + hx)
            i += 3
        else:
            out.append(_lower(ch) if lower_literals else ch)
            i += 1
    return "".join(out)


def _rds(path):
    inp = path
    out = ""
    while inp:
        if inp[:3] == "../":
            inp = inp[3:]
        elif inp[:2] == "./":
            inp = inp[2:]
        elif inp[:3] == "/./":
            inp = "/" + inp[3:]
        elif inp == "/.":
            inp = "/"
        elif inp[:4] == "/../":
            inp = "/" + inp[4:]
            k = out.rfind("/")
            out = out[:k] if k >= 0 else ""
        elif inp == "/..":
            inp = "/"
            k = out.rfind("/")
            out = out[:k] if k >= 0 else ""
        elif inp == "." or inp == "..":
            inp = ""
        else:
            k = inp.find("/", 1)
            if k < 0:
                out += inp
                inp = ""
            else:
                out += inp[:k]
                inp = inp[k:]
    return out


def _canon(d):
    """Normalisation steps 2-6 applied to a component dict, then serialise."""
    scheme = d["scheme"]
    userinfo = d["userinfo"]
    host = d["host"]
    port = d["port"]
    path = d["path"]
    query = d["query"]
    fragment = d["fragment"]
    if scheme is not None:
        scheme = _lower(scheme)
    if host is not None:
        host = _pct(host, True)
    if userinfo is not None:
        userinfo = _pct(userinfo)
    path = _pct(path)
    if query is not None:
        query = _pct(query)
    if fragment is not None:
        fragment = _pct(fragment)
    if port is not None:
        if port == "":
            port = None
        else:
            port = str(int(port))
            if _DEFAULT_PORTS.get(scheme) == port:
                port = None
    if host is not None or path[:1] == "/":
        path = _rds(path)
    if host is None and path[:2] == "//":
        path = "/." + path
    return unparse({"scheme": scheme, "userinfo": userinfo, "host": host,
                    "port": port, "path": path, "query": query,
                    "fragment": fragment})


def normalize(s):
    return _canon(parse(s))


def _merge(base, ref):
    if base["host"] is not None and base["path"] == "":
        return "/" + ref["path"]
    k = base["path"].rfind("/")
    return (base["path"][:k + 1] if k >= 0 else "") + ref["path"]


def resolve(base, ref):
    if not isinstance(base, str) or not isinstance(ref, str):
        raise UriError("type", "resolve() needs two str arguments")
    b = parse(base)
    if b["scheme"] is None:
        raise UriError("base", "base must have a scheme")
    r = parse(ref)
    t = {}
    if r["scheme"] is not None:
        t["scheme"] = r["scheme"]
        t["userinfo"] = r["userinfo"]
        t["host"] = r["host"]
        t["port"] = r["port"]
        t["path"] = _rds(r["path"])
        t["query"] = r["query"]
    else:
        if r["host"] is not None:
            t["userinfo"] = r["userinfo"]
            t["host"] = r["host"]
            t["port"] = r["port"]
            t["path"] = _rds(r["path"])
            t["query"] = r["query"]
        else:
            if r["path"] == "":
                t["path"] = b["path"]
                t["query"] = r["query"] if r["query"] is not None else b["query"]
            else:
                if r["path"][:1] == "/":
                    t["path"] = _rds(r["path"])
                else:
                    t["path"] = _rds(_merge(b, r))
                t["query"] = r["query"]
            t["userinfo"] = b["userinfo"]
            t["host"] = b["host"]
            t["port"] = b["port"]
        t["scheme"] = b["scheme"]
    t["fragment"] = r["fragment"]
    return _canon(t)
