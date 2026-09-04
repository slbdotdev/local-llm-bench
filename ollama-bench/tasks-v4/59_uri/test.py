import sys, os, re, random, threading, inspect

TOTAL = 27
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
    import uriref
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


def _missing(*a, **k):
    raise AttributeError("attribute missing from uriref")


PARSE = getattr(uriref, "parse", _missing)
UNPARSE = getattr(uriref, "unparse", _missing)
NORM = getattr(uriref, "normalize", _missing)
RESOLVE = getattr(uriref, "resolve", _missing)
SE = getattr(uriref, "UriError", None)


# ------------------------------------------------------------------ oracle --
_o_ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_o_DIGIT = "0123456789"
_o_UNRESERVED = frozenset(_o_ALPHA + _o_DIGIT + "-._~")
_o_SUBDELIMS = frozenset("!$&'()*+,;=")
_o_HEX = frozenset("0123456789abcdefABCDEF")
_o_SCHEME_TAIL = frozenset(_o_ALPHA + _o_DIGIT + "+-.")
_o_ALPHA_SET = frozenset(_o_ALPHA)
_o_DIGIT_SET = frozenset(_o_DIGIT)

_o_HOST_OK = _o_UNRESERVED | _o_SUBDELIMS | frozenset("%")
_o_USERINFO_OK = _o_HOST_OK | frozenset(":")
_o_PATH_OK = _o_USERINFO_OK | frozenset("@/")
_o_QF_OK = _o_PATH_OK | frozenset("?")

_o_KEYS = ("scheme", "userinfo", "host", "port", "path", "query", "fragment")

_o_DEFAULT_PORTS = {"http": "80", "https": "443", "ws": "80", "wss": "443"}

_o_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_o_LOWER = "abcdefghijklmnopqrstuvwxyz"


class _OErr(ValueError):
    def __init__(self, kind, message=None):
        ValueError.__init__(self, message if message is not None else kind)
        self.kind = kind


def _o_lower(s):
    out = []
    for ch in s:
        i = _o_UPPER.find(ch)
        out.append(_o_LOWER[i] if i >= 0 else ch)
    return "".join(out)


def _o_upper(s):
    out = []
    for ch in s:
        i = _o_LOWER.find(ch)
        out.append(_o_UPPER[i] if i >= 0 else ch)
    return "".join(out)


def _o_is_scheme(s):
    if not s or s[0] not in _o_ALPHA_SET:
        return False
    for ch in s[1:]:
        if ch not in _o_SCHEME_TAIL:
            return False
    return True


def _o_bad_escape(s):
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "%":
            if i + 2 >= n or s[i + 1] not in _o_HEX or s[i + 2] not in _o_HEX:
                return True
            i += 3
        else:
            i += 1
    return False


def _o_bad_chars(s, ok):
    for ch in s:
        if ch not in ok:
            return True
    return False


def _o_parse(s):
    if not isinstance(s, str):
        raise _OErr("type", "_o_parse() needs a str")
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
        if not _o_is_scheme(cand):
            raise _OErr("scheme", "bad scheme %r" % (cand,))
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
    if port is not None and _o_bad_chars(port, _o_DIGIT_SET):
        raise _OErr("port", "bad port %r" % (port,))
    if host is not None and _o_bad_chars(host, _o_HOST_OK):
        raise _OErr("host", "bad host %r" % (host,))
    if userinfo is not None and _o_bad_chars(userinfo, _o_USERINFO_OK):
        raise _OErr("userinfo", "bad userinfo")
    if _o_bad_chars(path, _o_PATH_OK):
        raise _OErr("char", "bad character in path")
    if query is not None and _o_bad_chars(query, _o_QF_OK):
        raise _OErr("char", "bad character in query")
    if fragment is not None and _o_bad_chars(fragment, _o_QF_OK):
        raise _OErr("char", "bad character in fragment")
    if _o_bad_escape(s):
        raise _OErr("escape", "malformed percent-escape")
    return {"scheme": scheme, "userinfo": userinfo, "host": host, "port": port,
            "path": path, "query": query, "fragment": fragment}


def _o_unparse(d):
    if not isinstance(d, dict):
        raise _OErr("type", "_o_unparse() needs a dict")
    if set(d.keys()) != set(_o_KEYS):
        raise _OErr("form", "wrong key set")
    for k in _o_KEYS:
        v = d[k]
        if v is not None and not isinstance(v, str):
            raise _OErr("type", "component %s is not a str" % k)
    scheme = d["scheme"]
    userinfo = d["userinfo"]
    host = d["host"]
    port = d["port"]
    path = d["path"]
    query = d["query"]
    fragment = d["fragment"]
    if path is None:
        raise _OErr("form", "path must be a str")
    if host is None and (userinfo is not None or port is not None):
        raise _OErr("form", "userinfo/port without a host")
    if host is not None and path != "" and path[:1] != "/":
        raise _OErr("form", "authority with a rootless non-empty path")
    if host is None and path[:2] == "//":
        raise _OErr("form", "path starting with // and no authority")
    if scheme is None and host is None and ":" in path.split("/")[0]:
        raise _OErr("form", "colon in the first segment of a relative path")
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


def _o_pct(s, lower_literals=False):
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "%":
            hx = _o_upper(s[i + 1:i + 3])
            dec = chr(int(hx, 16))
            if dec in _o_UNRESERVED:
                out.append(_o_lower(dec) if lower_literals else dec)
            else:
                out.append("%" + hx)
            i += 3
        else:
            out.append(_o_lower(ch) if lower_literals else ch)
            i += 1
    return "".join(out)


def _o_rds(path):
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


def _o_canon(d):
    """Normalisation steps 2-6 applied to a component dict, then serialise."""
    scheme = d["scheme"]
    userinfo = d["userinfo"]
    host = d["host"]
    port = d["port"]
    path = d["path"]
    query = d["query"]
    fragment = d["fragment"]
    if scheme is not None:
        scheme = _o_lower(scheme)
    if host is not None:
        host = _o_pct(host, True)
    if userinfo is not None:
        userinfo = _o_pct(userinfo)
    path = _o_pct(path)
    if query is not None:
        query = _o_pct(query)
    if fragment is not None:
        fragment = _o_pct(fragment)
    if port is not None:
        if port == "":
            port = None
        else:
            port = str(int(port))
            if _o_DEFAULT_PORTS.get(scheme) == port:
                port = None
    if host is not None or path[:1] == "/":
        path = _o_rds(path)
    if host is None and path[:2] == "//":
        path = "/." + path
    return _o_unparse({"scheme": scheme, "userinfo": userinfo, "host": host,
                    "port": port, "path": path, "query": query,
                    "fragment": fragment})


def _o_normalize(s):
    return _o_canon(_o_parse(s))


def _o_merge(base, ref):
    if base["host"] is not None and base["path"] == "":
        return "/" + ref["path"]
    k = base["path"].rfind("/")
    return (base["path"][:k + 1] if k >= 0 else "") + ref["path"]


def _o_resolve(base, ref):
    if not isinstance(base, str) or not isinstance(ref, str):
        raise _OErr("type", "_o_resolve() needs two str arguments")
    b = _o_parse(base)
    if b["scheme"] is None:
        raise _OErr("base", "base must have a scheme")
    r = _o_parse(ref)
    t = {}
    if r["scheme"] is not None:
        t["scheme"] = r["scheme"]
        t["userinfo"] = r["userinfo"]
        t["host"] = r["host"]
        t["port"] = r["port"]
        t["path"] = _o_rds(r["path"])
        t["query"] = r["query"]
    else:
        if r["host"] is not None:
            t["userinfo"] = r["userinfo"]
            t["host"] = r["host"]
            t["port"] = r["port"]
            t["path"] = _o_rds(r["path"])
            t["query"] = r["query"]
        else:
            if r["path"] == "":
                t["path"] = b["path"]
                t["query"] = r["query"] if r["query"] is not None else b["query"]
            else:
                if r["path"][:1] == "/":
                    t["path"] = _o_rds(r["path"])
                else:
                    t["path"] = _o_rds(_o_merge(b, r))
                t["query"] = r["query"]
            t["userinfo"] = b["userinfo"]
            t["host"] = b["host"]
            t["port"] = b["port"]
        t["scheme"] = b["scheme"]
    t["fragment"] = r["fragment"]
    return _o_canon(t)


# ----------------------------------------------------------------- helpers --
def out_c(fn):
    """Outcome of a candidate call: ('ok', value) or ('err', kind) or ('exc', ...)."""
    try:
        v = fn()
    except Exception as e:
        if isinstance(SE, type) and issubclass(SE, BaseException) and isinstance(e, SE):
            return ("err", getattr(e, "kind", "<no .kind>"))
        return ("exc", type(e).__name__)
    return ("ok", v)


def out_o(fn):
    try:
        v = fn()
    except _OErr as e:
        return ("err", e.kind)
    return ("ok", v)


def coarse(o):
    """Collapse every rejection to one marker: the exact kinds have their own checks."""
    return o if o[0] == "ok" else ("raised",)


def tbl(pairs, fn):
    """pairs: [(argument, expected outcome)]."""
    def probe():
        for arg, want in pairs:
            if out_c(lambda a=arg: fn(a)) != want:
                return False
        return True
    return probe


def tbl2(triples, fn):
    def probe():
        for a, b, want in triples:
            if out_c(lambda x=a, y=b: fn(x, y)) != want:
                return False
        return True
    return probe


def OK(v):
    return ("ok", v)


def ERR(k):
    return ("err", k)


def D(scheme, userinfo, host, port, path, query, fragment):
    return {"scheme": scheme, "userinfo": userinfo, "host": host, "port": port,
            "path": path, "query": query, "fragment": fragment}


# --- 1: visible examples ----------------------------------------------------
def visible():
    return (PARSE("http://a.com/x?y=1#z")
            == D("http", None, "a.com", None, "/x", "y=1", "z")
            and PARSE("mailto:x@y") == D("mailto", None, None, None, "x@y", None, None)
            and UNPARSE(PARSE("//u@h:8080/p")) == "//u@h:8080/p"
            and NORM("HTTP://Example.COM:80/a/./b/../c") == "http://example.com/a/c"
            and RESOLVE("http://a/b/c/d;p?q", "../g") == "http://a/b/g"
            and RESOLVE("http://a/b/c/d;p?q", "?y") == "http://a/b/c/d;p?y")


check("the visible examples from the prompt", visible)

# --- 2: parse splitting -----------------------------------------------------
check("parse: splitting into the seven components", tbl([
    ("http://a/b", OK(D("http", None, "a", None, "/b", None, None))),
    ("//h/p", OK(D(None, None, "h", None, "/p", None, None))),
    ("a", OK(D(None, None, None, None, "a", None, None))),
    ("g:h", OK(D("g", None, None, None, "h", None, None))),
    ("http://u:p@h:8/x?q#f", OK(D("http", "u:p", "h", "8", "/x", "q", "f"))),
    ("?q", OK(D(None, None, None, None, "", "q", None))),
    ("a/b:c", OK(D(None, None, None, None, "a/b:c", None, None))),
    ("http://h?a#b/c?d", OK(D("http", None, "h", None, "", "a", "b/c?d"))),
    ("//h#f", OK(D(None, None, "h", None, "", None, "f"))),
    ("//u:p@h:1/x", OK(D(None, "u:p", "h", "1", "/x", None, None))),
    ("A+b-2.c:/x", OK(D("A+b-2.c", None, None, None, "/x", None, None))),
    ("/a?b#c", OK(D(None, None, None, None, "/a", "b", "c"))),
], PARSE))

# --- 3: empty vs absent -----------------------------------------------------
check("parse: empty ('') and absent (None) components are distinguished", tbl([
    ("", OK(D(None, None, None, None, "", None, None))),
    ("//", OK(D(None, None, "", None, "", None, None))),
    ("//@", OK(D(None, "", "", None, "", None, None))),
    ("//:", OK(D(None, None, "", "", "", None, None))),
    ("//@:", OK(D(None, "", "", "", "", None, None))),
    ("//u@", OK(D(None, "u", "", None, "", None, None))),
    ("a?", OK(D(None, None, None, None, "a", "", None))),
    ("a#", OK(D(None, None, None, None, "a", None, ""))),
    ("a?#", OK(D(None, None, None, None, "a", "", ""))),
    ("//h/", OK(D(None, None, "h", None, "/", None, None))),
    ("s:", OK(D("s", None, None, None, "", None, None))),
    ("s://h", OK(D("s", None, "h", None, "", None, None))),
], PARSE))

# --- 4: unparse roundtrip ---------------------------------------------------
RAW = ["", "a", "//", "//@", "//:", "//@:", "a?", "a#", "a?#", "s:", "s://h",
       "http://u:p@h:8080/a/b?q=1&r=2#f", "//h/", "?", "#", "?#", "/", "//h",
       "mailto:x@y", "a/b:c", "s:/a/../b", "//u:p@h:1/x", "http://h?a#b?c",
       "%41%2f", "/a%20b", "s:.//x", "//h:0080", "urn:isbn:0451450523", "a:",
       "s+1-2.3://h", "//h/a/../b", "s://h:/", "./a:b", "?a=1&b=2#f"]
check("unparse(parse(x)) == x on raw strings", lambda: all(
    out_c(lambda s=s: UNPARSE(PARSE(s))) == OK(s) for s in RAW))

# --- 5: unparse structural errors -------------------------------------------
_G = D(None, None, None, None, "a", None, None)


def _mut(**kw):
    d = dict(_G)
    d.update(kw)
    return d


_extra = dict(_G)
_extra["extra"] = "x"
_missingk = dict(_G)
del _missingk["query"]
_badval = _mut(query=5)
_bothbad = dict(_badval)
_bothbad["extra"] = "x"
check("unparse: kinds 'type' and 'form', in the stated order", tbl([
    ("abc", ERR("type")), (None, ERR("type")), (5, ERR("type")),
    ([("path", "a")], ERR("type")),
    (_extra, ERR("form")), (_missingk, ERR("form")), (_badval, ERR("type")),
    (_bothbad, ERR("form")),
    (_mut(path=None), ERR("form")),
    (_mut(port="80"), ERR("form")),
    (_mut(userinfo="u"), ERR("form")),
    (_mut(host="h", path="a"), ERR("form")),
    (_mut(path="//x"), ERR("form")),
    (_mut(path="a:b"), ERR("form")),
    (_mut(path="/a:b"), OK("/a:b")),
    (_mut(path="./a:b"), OK("./a:b")),
    (_mut(scheme="s", path="a:b"), OK("s:a:b")),
    (_mut(host="h", path=""), OK("//h")),
    (_mut(host="", port="", userinfo="", path=""), OK("//@:")),
], UNPARSE))

# --- 6: the exception class -------------------------------------------------
check("UriError subclasses ValueError and carries .kind",
      lambda: isinstance(SE, type) and issubclass(SE, ValueError)
      and out_c(lambda: PARSE(5)) == ERR("type")
      and out_c(lambda: PARSE(b"a")) == ERR("type")
      and out_c(lambda: PARSE(None)) == ERR("type"))

# --- 7: scheme kind ---------------------------------------------------------
check("parse: kind 'scheme' for an ill-formed scheme", tbl([
    ("1a:b", ERR("scheme")), (":x", ERR("scheme")), ("a b:c", ERR("scheme")),
    ("a_b:c", ERR("scheme")), ("+a:b", ERR("scheme")), (".x:y", ERR("scheme")),
    ("a%20:b", ERR("scheme")), ("a/b:c", OK(D(None, None, None, None,
                                              "a/b:c", None, None))),
    ("a+b-c.d:x", OK(D("a+b-c.d", None, None, None, "x", None, None))),
    ("a1:", OK(D("a1", None, None, None, "", None, None))),
], PARSE))

# --- 8: port / host / userinfo kinds ----------------------------------------
check("parse: kinds 'port', 'host' and 'userinfo'", tbl([
    ("//h:a", ERR("port")), ("//h:8 0", ERR("port")), ("//h:80x/p", ERR("port")),
    ("//h:-1", ERR("port")), ("//h:80:90", ERR("host")), ("//h[]", ERR("host")),
    ("//a b", ERR("host")), ("//h<x>/p", ERR("host")), ("//h\\x", ERR("host")),
    ("//u<@h", ERR("userinfo")), ("//u@v@h", ERR("userinfo")),
    ("//u/@h", OK(D(None, None, "u", None, "/@h", None, None))),
    ("//h:80", OK(D(None, None, "h", "80", "", None, None))),
], PARSE))

# --- 9: char / escape kinds -------------------------------------------------
check("parse: kinds 'char' and 'escape'", tbl([
    ("a b", ERR("char")), ("/p<", ERR("char")), ("a?q<", ERR("char")),
    ("a#f<", ERR("char")), ("a#b#c", ERR("char")), ("a[b", ERR("char")),
    ("%", ERR("escape")), ("%A", ERR("escape")), ("%GG", ERR("escape")),
    ("%zz", ERR("escape")), ("a%2", ERR("escape")), ("%%41", ERR("escape")),
    ("a?b%", ERR("escape")), ("a#%1g", ERR("escape")),
    ("%41%ff%Ab", OK(D(None, None, None, None, "%41%ff%Ab", None, None))),
    ("a?b/c?d", OK(D(None, None, None, None, "a", "b/c?d", None))),
], PARSE))

# --- 10: validation order ---------------------------------------------------
check("parse: the stated order of the validation checks", tbl([
    ("1a://h:zz/ ", ERR("scheme")), ("1a:%", ERR("scheme")),
    ("//h:zz/ x", ERR("port")), ("//h[:zz", ERR("port")), ("//h:8%0", ERR("port")),
    ("//u<@h[", ERR("host")), ("// x/y%", ERR("host")), ("//h</a b", ERR("host")),
    ("//u<@h/ ", ERR("userinfo")), ("//u|@h/x y", ERR("userinfo")),
    ("a %", ERR("char")), ("a?b c%", ERR("char")), ("a#b<%", ERR("char")),
], PARSE))

# --- 11: resolve argument checks --------------------------------------------
check("resolve: kinds 'type' and 'base', base checked before ref is parsed", tbl2([
    (5, "a", ERR("type")), ("http://a", 5, ERR("type")), (None, None, ERR("type")),
    ("http://a", b"g", ERR("type")),
    ("a/b", "g", ERR("base")), ("//h/p", "g", ERR("base")), ("", "g", ERR("base")),
    ("a/b", "%zz", ERR("base")), ("/x", "1a:b", ERR("base")),
    ("1a:b", "g", ERR("scheme")), ("http://a", "%zz", ERR("escape")),
    ("http://a", "1a:b", ERR("scheme")), ("http://h:z/a", "g", ERR("port")),
], RESOLVE))

# --- 12: percent-encoding canonicalisation ----------------------------------
check("normalize: uppercase hex, and only unreserved escapes are decoded", tbl([
    ("http://h/%7e%2f%41%5a?%2a#%2d", OK("http://h/~%2FAZ?%2A#-")),
    ("//%41%42.com/", OK("//ab.com/")),
    ("http://h/a%c3%a9", OK("http://h/a%C3%A9")),
    ("//U%7EX@h/", OK("//U~X@h/")),
    ("http://h/%2E%2e/a", OK("http://h/a")),
    ("s:%30%39%2D%2e%5F%7E%20", OK("s:09-._~%20")),
    ("//h/?%3f%26=%25#%23", OK("//h/?%3F%26=%25#%23")),
], NORM))

# --- 13: case and port canonicalisation -------------------------------------
check("normalize: scheme/host case and the port rules", tbl([
    ("HTTP://H/A", OK("http://h/A")), ("HtTp://h:80/", OK("http://h/")),
    ("https://h:443", OK("https://h")), ("ws://h:80", OK("ws://h")),
    ("wss://h:443", OK("wss://h")), ("http://h:443", OK("http://h:443")),
    ("ftp://h:21", OK("ftp://h:21")), ("http://h:080", OK("http://h")),
    ("http://h:0080/", OK("http://h/")), ("http://h:8080", OK("http://h:8080")),
    ("http://h:", OK("http://h")), ("//h:00", OK("//h:0")),
    ("HTTP://h:0000000", OK("http://h:0")), ("//h:80", OK("//h:80")),
    ("HTTP://U@H", OK("http://U@h")),
], NORM))

# --- 14: empty vs absent survives normalisation -----------------------------
check("normalize: empty and absent components stay distinct", tbl([
    ("http://h?", OK("http://h?")), ("http://h#", OK("http://h#")),
    ("http://h", OK("http://h")), ("//", OK("//")), ("//@", OK("//@")),
    ("//:", OK("//")), ("http://h/?#", OK("http://h/?#")), ("", OK("")),
    ("a?", OK("a?")), ("?", OK("?")), ("#", OK("#")), ("s:", OK("s:")),
    ("//h?#", OK("//h?#")),
], NORM))

# --- 15: dot-segment removal ------------------------------------------------
check("normalize: remove_dot_segments edge cases", tbl([
    ("http://h/..", OK("http://h/")), ("http://h/a/../..", OK("http://h/")),
    ("http://h/a/b/../../../c", OK("http://h/c")),
    ("http://h/a/b/.", OK("http://h/a/b/")), ("http://h/./", OK("http://h/")),
    ("http://h/a//b/../", OK("http://h/a//")),
    ("http://h/..a/./b/..", OK("http://h/..a/")),
    ("http:/a/../..", OK("http:/")), ("http:/.", OK("http:/")),
    ("http:/..", OK("http:/")), ("s:/a/b/../c/./d/..", OK("s:/a/c/")),
    ("s://h/./../a", OK("s://h/a")), ("s://h/a/..", OK("s://h/")),
    ("s:/...//a", OK("s:/...//a")), ("s:/a/b/..c", OK("s:/a/b/..c")),
], NORM))

# --- 16: relative paths keep their dot segments -----------------------------
check("normalize: relative paths are left alone; an empty path stays empty", tbl([
    ("a/../b", OK("a/../b")), ("./a", OK("./a")), ("../a%7e", OK("../a~")),
    ("http://h", OK("http://h")), ("http:a/../b", OK("http:a/../b")),
    ("http:/a/../b", OK("http:/b")), ("..", OK("..")), (".", OK(".")),
    ("s:.", OK("s:.")), ("//h", OK("//h")), ("a/./b", OK("a/./b")),
], NORM))

# --- 17: the recomposition guard --------------------------------------------
check("the '//' path with no authority is prefixed with '/.'",
      lambda: out_c(lambda: RESOLVE("urn:a", "/.//x")) == OK("urn:/.//x")
      and out_c(lambda: RESOLVE("urn:a", "/..//x")) == OK("urn:/.//x")
      and out_c(lambda: NORM("http:/.//x")) == OK("http:/.//x")
      and out_c(lambda: NORM("s:/a/..//b")) == OK("s:/.//b")
      and out_c(lambda: RESOLVE("http://h/a", "/.//x")) == OK("http://h//x")
      and out_c(lambda: RESOLVE("s:/a/b", "..//c")) == OK("s:/.//c"))

# --- 18-19: the RFC resolution tables ---------------------------------------
_B = "http://a/b/c/d;p?q"
NORMAL = [("g:h", "g:h"), ("g", "http://a/b/c/g"), ("./g", "http://a/b/c/g"),
          ("g/", "http://a/b/c/g/"), ("/g", "http://a/g"), ("//g", "http://g"),
          ("?y", "http://a/b/c/d;p?y"), ("g?y", "http://a/b/c/g?y"),
          ("#s", "http://a/b/c/d;p?q#s"), ("g#s", "http://a/b/c/g#s"),
          ("g?y#s", "http://a/b/c/g?y#s"), (";x", "http://a/b/c/;x"),
          ("g;x", "http://a/b/c/g;x"), ("g;x?y#s", "http://a/b/c/g;x?y#s"),
          ("", "http://a/b/c/d;p?q"), (".", "http://a/b/c/"),
          ("./", "http://a/b/c/"), ("..", "http://a/b/"), ("../", "http://a/b/"),
          ("../g", "http://a/b/g"), ("../..", "http://a/"),
          ("../../", "http://a/"), ("../../g", "http://a/g")]
ABNORMAL = [("../../../g", "http://a/g"), ("../../../../g", "http://a/g"),
            ("/./g", "http://a/g"), ("/../g", "http://a/g"),
            ("g.", "http://a/b/c/g."), (".g", "http://a/b/c/.g"),
            ("g..", "http://a/b/c/g.."), ("..g", "http://a/b/c/..g"),
            ("./../g", "http://a/b/g"), ("./g/.", "http://a/b/c/g/"),
            ("g/./h", "http://a/b/c/g/h"), ("g/../h", "http://a/b/c/h"),
            ("g;x=1/./y", "http://a/b/c/g;x=1/y"),
            ("g;x=1/../y", "http://a/b/c/y"),
            ("g?y/./x", "http://a/b/c/g?y/./x"),
            ("g?y/../x", "http://a/b/c/g?y/../x"),
            ("g#s/./x", "http://a/b/c/g#s/./x"),
            ("g#s/../x", "http://a/b/c/g#s/../x"), ("http:g", "http:g")]
check("resolve: the normal reference examples",
      tbl2([(_B, r, OK(w)) for r, w in NORMAL], RESOLVE))
check("resolve: the abnormal reference examples",
      tbl2([(_B, r, OK(w)) for r, w in ABNORMAL], RESOLVE))

# --- 20-25: randomised differential tests -----------------------------------
_TOK = ["a", "B", "/", "//", ".", "..", "%2F", "%7e", "%zz", "%", "?", "#", ":",
        "@", "h", "-", "~", "80", ":80", "x", "%3A", "[", " ", "+", ";p",
        "..%2f", "a:", "://", "0", "%C3", "_", "!", "=", "%2E"]


def gen(rng, lo=0, hi=6):
    return "".join(rng.choice(_TOK) for _ in range(rng.randint(lo, hi)))


def diff_parse(seed, n):
    def probe():
        rng = random.Random(seed)
        for _ in range(n):
            s = gen(rng)
            a = coarse(out_c(lambda s=s: PARSE(s)))
            b = coarse(out_o(lambda s=s: _o_parse(s)))
            if a != b:
                return False
            if b[0] == "ok":
                if out_c(lambda s=s: UNPARSE(PARSE(s))) != ("ok", s):
                    return False
        return True
    return probe


def diff_norm(seed, n):
    def probe():
        rng = random.Random(seed)
        for _ in range(n):
            s = gen(rng)
            if (coarse(out_c(lambda s=s: NORM(s)))
                    != coarse(out_o(lambda s=s: _o_normalize(s)))):
                return False
        return True
    return probe


_BASES = ["http://a/b/c/d;p?q", "http://a", "http://a/", "http://a/b/",
          "s://u@h:8/p/q?r#f", "urn:a:b", "http:x/y", "s:/p/q", "S://H:80/A%2fB",
          "s://", "s:", "http://h?x"]


def diff_resolve(seed, n, wild):
    def probe():
        rng = random.Random(seed)
        for _ in range(n):
            r = gen(rng)
            b = gen(rng, 1, 5) if wild and rng.random() < 0.5 else rng.choice(_BASES)
            a = coarse(out_c(lambda b=b, r=r: RESOLVE(b, r)))
            e = coarse(out_o(lambda b=b, r=r: _o_resolve(b, r)))
            if a != e:
                return False
        return True
    return probe


def diff_kinds(seed, n):
    """Only the cases the oracle rejects: the kind must match exactly."""
    def probe():
        rng = random.Random(seed)
        seen = 0
        for _ in range(n):
            s = gen(rng, 1, 5)
            e = out_o(lambda s=s: _o_normalize(s))
            if e[0] != "err":
                continue
            seen += 1
            if out_c(lambda s=s: NORM(s)) != e:
                return False
            if out_c(lambda s=s: PARSE(s)) != out_o(lambda s=s: _o_parse(s)):
                return False
        return seen >= 60
    return probe


check("randomised differential: parse and the unparse roundtrip",
      diff_parse(1001, 400))
check("randomised differential: normalize (A)", diff_norm(2002, 400))
check("randomised differential: normalize (B)", diff_norm(3003, 400))
check("randomised differential: resolve (A)", diff_resolve(4004, 350, False))
check("randomised differential: resolve (B, unusual bases)",
      diff_resolve(5005, 350, True))
check("randomised differential: the error kinds of rejected inputs",
      diff_kinds(6006, 500))

# --- 26-27: banned modules --------------------------------------------------
_SRC = ""
try:
    _SRC = inspect.getsource(uriref)
except Exception:
    _SRC = ""


def _imports(mods):
    """True if the candidate source imports any of mods, in any spelling."""
    ms = set(mods)
    for raw in _SRC.splitlines():
        line = raw.strip()
        head = None
        if line.startswith("from "):
            head = line[5:].split(" import ")[0]
        elif line.startswith("import "):
            head = line[7:]
        if head is not None:
            for part in head.split(","):
                name = part.strip().split(" as ")[0].strip().split(".")[0]
                if name in ms:
                    return True
        for m in ms:
            if re.search(r"""(?:__import__|import_module)\s*\(\s*['"]%s\b""" % m,
                         line):
                return True
    return False


check("does not import re, urllib or posixpath",
      lambda: bool(_SRC) and not _imports(["re", "urllib", "posixpath"]))
check("does not import ipaddress, string or binascii",
      lambda: bool(_SRC) and not _imports(["ipaddress", "string", "binascii"]))

_t.cancel()
report()
