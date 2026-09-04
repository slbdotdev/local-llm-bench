"""RFC-3986-style URI reference parser, normalizer and resolver.

Pure string processing; standard library only, no imports required.
"""


class UriError(ValueError):
    def __init__(self, kind, message=None):
        self.kind = kind
        super().__init__(message if message is not None else kind)


# ---------------------------------------------------------------------------
# Character classes
# ---------------------------------------------------------------------------

_ALPHA_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_ALPHA_LOWER = "abcdefghijklmnopqrstuvwxyz"
_DIGITS = "0123456789"
_HEXDIG = _DIGITS + "ABCDEF" + "abcdef"

UNRESERVED = _ALPHA_UPPER + _ALPHA_LOWER + _DIGITS + "-._~"
SUBDELIMS = "!$&'()*+,;="

HOST_SET = UNRESERVED + SUBDELIMS + "%"
USERINFO_SET = HOST_SET + ":"
PATH_SET = USERINFO_SET + "@/"
QUERY_SET = PATH_SET + "?"


def _is_alpha(c):
    return c in _ALPHA_UPPER or c in _ALPHA_LOWER


def _is_digit(c):
    return c in _DIGITS


def _is_hexdig(c):
    return c in _HEXDIG


def _valid_scheme_str(x):
    if not x:
        return False
    if not _is_alpha(x[0]):
        return False
    for c in x[1:]:
        if not (_is_alpha(c) or _is_digit(c) or c in "+-."):
            return False
    return True


def _check_escapes(s):
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "%":
            if i + 2 >= n or not _is_hexdig(s[i + 1]) or not _is_hexdig(s[i + 2]):
                raise UriError("escape")
            i += 3
        else:
            i += 1


# ---------------------------------------------------------------------------
# parse / unparse
# ---------------------------------------------------------------------------

_KEYS = {"scheme", "userinfo", "host", "port", "path", "query", "fragment"}


def parse(s):
    if not isinstance(s, str):
        raise UriError("type")

    hidx = s.find("#")
    if hidx != -1:
        fragment = s[hidx + 1:]
        rest = s[:hidx]
    else:
        fragment = None
        rest = s

    qidx = rest.find("?")
    if qidx != -1:
        query = rest[qidx + 1:]
        rest2 = rest[:qidx]
    else:
        query = None
        rest2 = rest

    cidx = rest2.find(":")
    lidx = rest2.find("/")
    scheme = None
    leftover = rest2
    if cidx != -1 and (lidx == -1 or cidx < lidx):
        candidate = rest2[:cidx]
        if not _valid_scheme_str(candidate):
            raise UriError("scheme")
        scheme = candidate
        leftover = rest2[cidx + 1:]

    if leftover.startswith("//"):
        rem = leftover[2:]
        sidx = rem.find("/")
        if sidx == -1:
            authority = rem
            path = ""
        else:
            authority = rem[:sidx]
            path = rem[sidx:]

        aidx = authority.rfind("@")
        if aidx != -1:
            userinfo = authority[:aidx]
            hostport = authority[aidx + 1:]
        else:
            userinfo = None
            hostport = authority

        cidx2 = hostport.rfind(":")
        if cidx2 != -1:
            host = hostport[:cidx2]
            port = hostport[cidx2 + 1:]
        else:
            host = hostport
            port = None
    else:
        host = None
        userinfo = None
        port = None
        path = leftover

    # Validation, in exact order.
    if port is not None:
        for c in port:
            if not _is_digit(c):
                raise UriError("port")

    if host is not None:
        for c in host:
            if c not in HOST_SET:
                raise UriError("host")

    if userinfo is not None:
        for c in userinfo:
            if c not in USERINFO_SET:
                raise UriError("userinfo")

    for c in path:
        if c not in PATH_SET:
            raise UriError("char")
    if query is not None:
        for c in query:
            if c not in QUERY_SET:
                raise UriError("char")
    if fragment is not None:
        for c in fragment:
            if c not in QUERY_SET:
                raise UriError("char")

    _check_escapes(s)

    return {
        "scheme": scheme,
        "userinfo": userinfo,
        "host": host,
        "port": port,
        "path": path,
        "query": query,
        "fragment": fragment,
    }


def unparse(d):
    if not isinstance(d, dict):
        raise UriError("type")
    if set(d) != _KEYS:
        raise UriError("form")
    for k in _KEYS:
        v = d[k]
        if v is not None and not isinstance(v, str):
            raise UriError("type")

    scheme = d["scheme"]
    userinfo = d["userinfo"]
    host = d["host"]
    port = d["port"]
    path = d["path"]
    query = d["query"]
    fragment = d["fragment"]

    if path is None:
        raise UriError("form")
    if host is None and (userinfo is not None or port is not None):
        raise UriError("form")
    if host is not None and not (path == "" or path.startswith("/")):
        raise UriError("form")
    if host is None and path.startswith("//"):
        raise UriError("form")
    if scheme is None and host is None:
        sidx = path.find("/")
        first_seg = path if sidx == -1 else path[:sidx]
        if ":" in first_seg:
            raise UriError("form")

    out = []
    if scheme is not None:
        out.append(scheme)
        out.append(":")
    if host is not None:
        out.append("//")
        if userinfo is not None:
            out.append(userinfo)
            out.append("@")
        out.append(host)
        if port is not None:
            out.append(":")
            out.append(port)
    out.append(path)
    if query is not None:
        out.append("?")
        out.append(query)
    if fragment is not None:
        out.append("#")
        out.append(fragment)
    return "".join(out)


# ---------------------------------------------------------------------------
# remove_dot_segments
# ---------------------------------------------------------------------------

def remove_dot_segments(path):
    inp = path
    out = ""
    while inp:
        if inp.startswith("../"):
            inp = inp[3:]
        elif inp.startswith("./"):
            inp = inp[2:]
        elif inp.startswith("/./"):
            inp = "/" + inp[3:]
        elif inp == "/.":
            inp = "/"
        elif inp.startswith("/../"):
            inp = "/" + inp[4:]
            idx = out.rfind("/")
            out = "" if idx == -1 else out[:idx]
        elif inp == "/..":
            inp = "/"
            idx = out.rfind("/")
            out = "" if idx == -1 else out[:idx]
        elif inp == "." or inp == "..":
            inp = ""
        else:
            if inp.startswith("/"):
                rest = inp[1:]
                nidx = rest.find("/")
                if nidx == -1:
                    seg = inp
                    inp = ""
                else:
                    seg = "/" + rest[:nidx]
                    inp = inp[len(seg):]
            else:
                nidx = inp.find("/")
                if nidx == -1:
                    seg = inp
                    inp = ""
                else:
                    seg = inp[:nidx]
                    inp = inp[nidx:]
            out += seg
    return out


# ---------------------------------------------------------------------------
# normalize
# ---------------------------------------------------------------------------

def _upper_hex_pair(pair):
    res = []
    for c in pair:
        if c in "abcdef":
            res.append(chr(ord(c) - 32))
        else:
            res.append(c)
    return "".join(res)


def _lower_ascii_letters(x):
    res = []
    for c in x:
        if c in _ALPHA_UPPER:
            res.append(chr(ord(c) + 32))
        else:
            res.append(c)
    return "".join(res)


def _canon_escapes(x):
    if x is None:
        return None
    out = []
    i = 0
    n = len(x)
    while i < n:
        c = x[i]
        if c == "%" and i + 2 < n and _is_hexdig(x[i + 1]) and _is_hexdig(x[i + 2]):
            hex2 = _upper_hex_pair(x[i + 1] + x[i + 2])
            val = int(hex2, 16)
            ch = chr(val)
            if ch in UNRESERVED:
                out.append(ch)
            else:
                out.append("%" + hex2)
            i += 3
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _lower_host_outside_escapes(x):
    res = []
    i = 0
    n = len(x)
    while i < n:
        c = x[i]
        if c == "%" and i + 2 < n and _is_hexdig(x[i + 1]) and _is_hexdig(x[i + 2]):
            res.append(x[i:i + 3])
            i += 3
        else:
            if c in _ALPHA_UPPER:
                c = chr(ord(c) + 32)
            res.append(c)
            i += 1
    return "".join(res)


def _normalize_components(scheme, userinfo, host, port, path, query, fragment):
    if scheme is not None:
        scheme = _lower_ascii_letters(scheme)

    userinfo = _canon_escapes(userinfo)
    host = _canon_escapes(host)
    path = _canon_escapes(path)
    query = _canon_escapes(query)
    fragment = _canon_escapes(fragment)

    if host is not None:
        host = _lower_host_outside_escapes(host)

    if port is not None:
        if port == "":
            port = None
        else:
            val = int(port)
            port = str(val)
            if scheme in ("http", "ws") and port == "80":
                port = None
            elif scheme in ("https", "wss") and port == "443":
                port = None

    if host is not None or path.startswith("/"):
        path = remove_dot_segments(path)

    if host is None and path.startswith("//"):
        path = "/." + path

    return unparse({
        "scheme": scheme,
        "userinfo": userinfo,
        "host": host,
        "port": port,
        "path": path,
        "query": query,
        "fragment": fragment,
    })


def normalize(s):
    d = parse(s)
    return _normalize_components(
        d["scheme"], d["userinfo"], d["host"], d["port"],
        d["path"], d["query"], d["fragment"],
    )


# ---------------------------------------------------------------------------
# resolve
# ---------------------------------------------------------------------------

def resolve(base, ref):
    if not isinstance(base, str) or not isinstance(ref, str):
        raise UriError("type")

    B = parse(base)
    if B["scheme"] is None:
        raise UriError("base")

    R = parse(ref)

    if R["scheme"] is not None:
        t_scheme = R["scheme"]
        t_userinfo = R["userinfo"]
        t_host = R["host"]
        t_port = R["port"]
        t_query = R["query"]
        t_path = remove_dot_segments(R["path"])
    elif R["host"] is not None:
        t_scheme = B["scheme"]
        t_userinfo = R["userinfo"]
        t_host = R["host"]
        t_port = R["port"]
        t_query = R["query"]
        t_path = remove_dot_segments(R["path"])
    else:
        t_scheme = B["scheme"]
        t_userinfo = B["userinfo"]
        t_host = B["host"]
        t_port = B["port"]
        if R["path"] == "":
            t_path = B["path"]
            t_query = R["query"] if R["query"] is not None else B["query"]
        else:
            t_query = R["query"]
            if R["path"].startswith("/"):
                t_path = remove_dot_segments(R["path"])
            else:
                if B["host"] is not None and B["path"] == "":
                    merged = "/" + R["path"]
                else:
                    idx = B["path"].rfind("/")
                    prefix = "" if idx == -1 else B["path"][:idx + 1]
                    merged = prefix + R["path"]
                t_path = remove_dot_segments(merged)

    t_fragment = R["fragment"]

    return _normalize_components(
        t_scheme, t_userinfo, t_host, t_port, t_path, t_query, t_fragment,
    )
