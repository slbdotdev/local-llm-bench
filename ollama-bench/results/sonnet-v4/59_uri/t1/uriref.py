"""RFC-3986-style URI reference parser, normalizer and resolver.

Pure string processing, standard library only, no imports required.
"""

ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
DIGIT = "0123456789"
HEXDIG = "0123456789ABCDEFabcdef"

UNRESERVED = ALPHA + DIGIT + "-._~"
SUB_DELIMS = "!$&'()*+,;="

HOST_CHARS = UNRESERVED + SUB_DELIMS + "%"
USERINFO_CHARS = HOST_CHARS + ":"
PATH_CHARS = USERINFO_CHARS + "@/"
QF_CHARS = PATH_CHARS + "?"


class UriError(ValueError):
    def __init__(self, kind, msg=None):
        super().__init__(msg or kind)
        self.kind = kind


def _all_in(s, allowed):
    for ch in s:
        if ch not in allowed:
            return False
    return True


def _valid_scheme(s):
    if len(s) == 0:
        return False
    if s[0] not in ALPHA:
        return False
    for ch in s[1:]:
        if ch not in ALPHA and ch not in DIGIT and ch not in "+-.":
            return False
    return True


def _check_escapes(s):
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "%":
            if i + 2 < n and s[i + 1] in HEXDIG and s[i + 2] in HEXDIG:
                i += 3
            else:
                raise UriError("escape")
        else:
            i += 1


def parse(s):
    if not isinstance(s, str):
        raise UriError("type")

    rest = s

    if "#" in rest:
        i = rest.index("#")
        fragment = rest[i + 1:]
        rest = rest[:i]
    else:
        fragment = None

    if "?" in rest:
        i = rest.index("?")
        query = rest[i + 1:]
        rest = rest[:i]
    else:
        query = None

    c_idx = rest.find(":")
    l_idx = rest.find("/")
    scheme = None
    if c_idx != -1 and (l_idx == -1 or c_idx < l_idx):
        scheme_str = rest[:c_idx]
        if not _valid_scheme(scheme_str):
            raise UriError("scheme")
        scheme = scheme_str
        rest = rest[c_idx + 1:]

    if rest.startswith("//"):
        remainder = rest[2:]
        si = remainder.find("/")
        if si == -1:
            authority = remainder
            path = ""
        else:
            authority = remainder[:si]
            path = remainder[si:]

        if "@" in authority:
            ai = authority.rindex("@")
            userinfo = authority[:ai]
            hostport = authority[ai + 1:]
        else:
            userinfo = None
            hostport = authority

        if ":" in hostport:
            ci = hostport.rindex(":")
            host = hostport[:ci]
            port = hostport[ci + 1:]
        else:
            host = hostport
            port = None
    else:
        host = None
        userinfo = None
        port = None
        path = rest

    if port is not None and not _all_in(port, DIGIT):
        raise UriError("port")
    if host is not None and not _all_in(host, HOST_CHARS):
        raise UriError("host")
    if userinfo is not None and not _all_in(userinfo, USERINFO_CHARS):
        raise UriError("userinfo")
    if not _all_in(path, PATH_CHARS):
        raise UriError("char")
    if query is not None and not _all_in(query, QF_CHARS):
        raise UriError("char")
    if fragment is not None and not _all_in(fragment, QF_CHARS):
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


_REQUIRED_KEYS = {"scheme", "userinfo", "host", "port", "path", "query", "fragment"}


def unparse(d):
    if not isinstance(d, dict):
        raise UriError("type")
    if set(d.keys()) != _REQUIRED_KEYS:
        raise UriError("form")

    for k in _REQUIRED_KEYS:
        v = d[k]
        if not (isinstance(v, str) or v is None):
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
        si = path.find("/")
        first_seg = path[:si] if si != -1 else path
        if ":" in first_seg:
            raise UriError("form")

    result = ""
    if scheme is not None:
        result += scheme + ":"
    if host is not None:
        result += "//"
        if userinfo is not None:
            result += userinfo + "@"
        result += host
        if port is not None:
            result += ":" + port
    result += path
    if query is not None:
        result += "?" + query
    if fragment is not None:
        result += "#" + fragment
    return result


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
            if "/" in out:
                out = out[:out.rindex("/")]
            else:
                out = ""
        elif inp == "/..":
            inp = "/"
            if "/" in out:
                out = out[:out.rindex("/")]
            else:
                out = ""
        elif inp == "." or inp == "..":
            inp = ""
        else:
            if inp.startswith("/"):
                tail = inp[1:]
                if "/" in tail:
                    idx = tail.index("/")
                    seg = "/" + tail[:idx]
                else:
                    seg = inp
                inp = inp[len(seg):]
            else:
                if "/" in inp:
                    idx = inp.index("/")
                    seg = inp[:idx]
                else:
                    seg = inp
                inp = inp[len(seg):]
            out += seg
    return out


def _canon_escapes(component):
    if component is None:
        return None
    parts = []
    i = 0
    n = len(component)
    while i < n:
        ch = component[i]
        if ch == "%" and i + 2 < n and component[i + 1] in HEXDIG and component[i + 2] in HEXDIG:
            hex2 = (component[i + 1] + component[i + 2]).upper()
            val = int(hex2, 16)
            decoded = chr(val)
            if decoded in UNRESERVED:
                parts.append(decoded)
            else:
                parts.append("%" + hex2)
            i += 3
        else:
            parts.append(ch)
            i += 1
    return "".join(parts)


def _lowercase_host(h):
    if h is None:
        return None
    parts = []
    i = 0
    n = len(h)
    while i < n:
        if h[i] == "%" and i + 2 < n:
            parts.append(h[i:i + 3])
            i += 3
        else:
            ch = h[i]
            if ch in ALPHA:
                parts.append(ch.lower())
            else:
                parts.append(ch)
            i += 1
    return "".join(parts)


def _normalize_components(d):
    scheme = d["scheme"]
    userinfo = d["userinfo"]
    host = d["host"]
    port = d["port"]
    path = d["path"]
    query = d["query"]
    fragment = d["fragment"]

    # 1. lowercase scheme
    if scheme is not None:
        scheme = scheme.lower()

    # 2. canonicalize percent-escapes
    userinfo = _canon_escapes(userinfo)
    host = _canon_escapes(host)
    path = _canon_escapes(path)
    query = _canon_escapes(query)
    fragment = _canon_escapes(fragment)

    # 3. lowercase host letters outside escapes
    host = _lowercase_host(host)

    # 4. port normalization
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

    # 5. remove dot segments
    if host is not None or path.startswith("/"):
        path = remove_dot_segments(path)

    # 6. recomposition guard
    if host is None and path.startswith("//"):
        path = "/." + path

    return {
        "scheme": scheme,
        "userinfo": userinfo,
        "host": host,
        "port": port,
        "path": path,
        "query": query,
        "fragment": fragment,
    }


def normalize(s):
    d = parse(s)
    n = _normalize_components(d)
    return unparse(n)


def resolve(base, ref):
    if not isinstance(base, str) or not isinstance(ref, str):
        raise UriError("type")

    B = parse(base)
    if B["scheme"] is None:
        raise UriError("base")

    R = parse(ref)

    if R["scheme"] is not None:
        T = {
            "scheme": R["scheme"],
            "userinfo": R["userinfo"],
            "host": R["host"],
            "port": R["port"],
            "path": remove_dot_segments(R["path"]),
            "query": R["query"],
            "fragment": R["fragment"],
        }
    elif R["host"] is not None:
        T = {
            "scheme": B["scheme"],
            "userinfo": R["userinfo"],
            "host": R["host"],
            "port": R["port"],
            "path": remove_dot_segments(R["path"]),
            "query": R["query"],
            "fragment": R["fragment"],
        }
    else:
        if R["path"] == "":
            path = B["path"]
            query = R["query"] if R["query"] is not None else B["query"]
        else:
            query = R["query"]
            if R["path"].startswith("/"):
                path = remove_dot_segments(R["path"])
            else:
                if B["host"] is not None and B["path"] == "":
                    merged = "/" + R["path"]
                else:
                    if "/" in B["path"]:
                        merged = B["path"][:B["path"].rindex("/") + 1] + R["path"]
                    else:
                        merged = R["path"]
                path = remove_dot_segments(merged)
        T = {
            "scheme": B["scheme"],
            "userinfo": B["userinfo"],
            "host": B["host"],
            "port": B["port"],
            "path": path,
            "query": query,
            "fragment": R["fragment"],
        }

    N = _normalize_components(T)
    return unparse(N)
