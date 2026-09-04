"""RFC-3986-style URI reference parser, normalizer and resolver.

Pure string processing, standard library only (no imports at all needed).
"""

ALPHA_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHA_LOWER = "abcdefghijklmnopqrstuvwxyz"
ALPHA = ALPHA_UPPER + ALPHA_LOWER
DIGIT = "0123456789"
HEXDIG = DIGIT + "ABCDEF" + "abcdef"

UNRESERVED = ALPHA + DIGIT + "-._~"
SUBDELIMS = "!$&'()*+,;="

HOST_SET = UNRESERVED + SUBDELIMS + "%"
USERINFO_SET = HOST_SET + ":"
PATH_SET = USERINFO_SET + "@/"
QF_SET = PATH_SET + "?"
PORT_SET = DIGIT

_KEYS = {"scheme", "userinfo", "host", "port", "path", "query", "fragment"}


class UriError(ValueError):
    def __init__(self, kind, msg=None):
        self.kind = kind
        super().__init__(msg if msg is not None else kind)


def _valid_scheme(candidate):
    if candidate == "":
        return False
    if candidate[0] not in ALPHA:
        return False
    for ch in candidate[1:]:
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

    fragment = None
    if "#" in rest:
        idx = rest.index("#")
        fragment = rest[idx + 1:]
        rest = rest[:idx]

    query = None
    if "?" in rest:
        idx = rest.index("?")
        query = rest[idx + 1:]
        rest = rest[:idx]

    scheme = None
    c = rest.find(":")
    l = rest.find("/")
    if c != -1 and (l == -1 or c < l):
        candidate = rest[:c]
        if not _valid_scheme(candidate):
            raise UriError("scheme")
        scheme = candidate
        rest = rest[c + 1:]

    if rest.startswith("//"):
        rem = rest[2:]
        idx = rem.find("/")
        if idx == -1:
            authority = rem
            path = ""
        else:
            authority = rem[:idx]
            path = rem[idx:]

        if "@" in authority:
            at = authority.rindex("@")
            userinfo = authority[:at]
            hostport = authority[at + 1:]
        else:
            userinfo = None
            hostport = authority

        if ":" in hostport:
            colon = hostport.rindex(":")
            host = hostport[:colon]
            port = hostport[colon + 1:]
        else:
            host = hostport
            port = None
    else:
        host = None
        userinfo = None
        port = None
        path = rest

    # Validation, in exact order.
    if port is not None:
        for ch in port:
            if ch not in PORT_SET:
                raise UriError("port")

    if host is not None:
        for ch in host:
            if ch not in HOST_SET:
                raise UriError("host")

    if userinfo is not None:
        for ch in userinfo:
            if ch not in USERINFO_SET:
                raise UriError("userinfo")

    for ch in path:
        if ch not in PATH_SET:
            raise UriError("char")
    if query is not None:
        for ch in query:
            if ch not in QF_SET:
                raise UriError("char")
    if fragment is not None:
        for ch in fragment:
            if ch not in QF_SET:
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
    if set(d.keys()) != _KEYS:
        raise UriError("form")
    for k in _KEYS:
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
        idx = path.find("/")
        first_seg = path if idx == -1 else path[:idx]
        if ":" in first_seg:
            raise UriError("form")

    parts = []
    if scheme is not None:
        parts.append(scheme)
        parts.append(":")
    if host is not None:
        parts.append("//")
        if userinfo is not None:
            parts.append(userinfo)
            parts.append("@")
        parts.append(host)
        if port is not None:
            parts.append(":")
            parts.append(port)
    parts.append(path)
    if query is not None:
        parts.append("?")
        parts.append(query)
    if fragment is not None:
        parts.append("#")
        parts.append(fragment)
    return "".join(parts)


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
                idx = inp.find("/", 1)
            else:
                idx = inp.find("/")
            if idx == -1:
                seg = inp
                inp = ""
            else:
                seg = inp[:idx]
                inp = inp[idx:]
            out = out + seg
    return out


def _lower_ascii(s):
    out = []
    for ch in s:
        if "A" <= ch <= "Z":
            out.append(chr(ord(ch) + 32))
        else:
            out.append(ch)
    return "".join(out)


def _canon_component(s, is_host=False):
    out = []
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "%" and i + 2 < n and s[i + 1] in HEXDIG and s[i + 2] in HEXDIG:
            hex2 = (s[i + 1] + s[i + 2]).upper()
            val = int(hex2, 16)
            c = chr(val)
            if c in UNRESERVED:
                if is_host and "A" <= c <= "Z":
                    c = chr(ord(c) + 32)
                out.append(c)
            else:
                out.append("%" + hex2)
            i += 3
        else:
            if is_host and "A" <= ch <= "Z":
                ch = chr(ord(ch) + 32)
            out.append(ch)
            i += 1
    return "".join(out)


def _normalize_dict(d):
    scheme = d["scheme"]
    userinfo = d["userinfo"]
    host = d["host"]
    port = d["port"]
    path = d["path"]
    query = d["query"]
    fragment = d["fragment"]

    # 1. scheme lowercased
    if scheme is not None:
        scheme = _lower_ascii(scheme)

    # 2 & 3. percent-escape canonicalization (+ host case folding)
    if userinfo is not None:
        userinfo = _canon_component(userinfo, is_host=False)
    if host is not None:
        host = _canon_component(host, is_host=True)
    path = _canon_component(path, is_host=False)
    if query is not None:
        query = _canon_component(query, is_host=False)
    if fragment is not None:
        fragment = _canon_component(fragment, is_host=False)

    # 4. port
    if port is not None:
        if port == "":
            port = None
        else:
            stripped = port.lstrip("0")
            if stripped == "":
                stripped = "0"
            port = stripped
            if scheme in ("http", "ws") and port == "80":
                port = None
            elif scheme in ("https", "wss") and port == "443":
                port = None

    # 5. dot segments
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
    nd = _normalize_dict(d)
    return unparse(nd)


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
            "query": R["query"],
            "path": remove_dot_segments(R["path"]),
        }
    elif R["host"] is not None:
        T = {
            "scheme": B["scheme"],
            "userinfo": R["userinfo"],
            "host": R["host"],
            "port": R["port"],
            "query": R["query"],
            "path": remove_dot_segments(R["path"]),
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
            "query": query,
            "path": path,
        }

    T["fragment"] = R["fragment"]

    NT = _normalize_dict(T)
    return unparse(NT)
