"""Purely lexical path normalisation / relativisation for posix and win styles."""

BS = chr(92)


class PathError(ValueError):
    def __init__(self, kind, msg=None):
        ValueError.__init__(self, msg if msg is not None else kind)
        self.kind = kind


def _seps(style):
    if style == "posix":
        return "/"
    if style == "win":
        return "/" + BS
    raise PathError("style", "bad style: %r" % (style,))


def _is_sep(ch, style):
    return ch in _seps(style)


def split_root(path, style="posix"):
    seps = _seps(style)
    if style == "posix":
        k = 0
        while k < len(path) and path[k] == "/":
            k += 1
        if k == 0:
            root = ""
        elif k == 2:
            root = "//"
        else:
            root = "/"
        return (root, path[k:])
    # win
    if (len(path) >= 2 and path[0] in seps and path[1] in seps
            and (len(path) < 3 or path[2] not in seps)):
        i = 2
        j = i
        while j < len(path) and path[j] not in seps:
            j += 1
        server = path[i:j]
        if server and j < len(path):
            m = j + 1
            n = m
            while n < len(path) and path[n] not in seps:
                n += 1
            share = path[m:n]
            if share:
                return (BS + BS + server + BS + share, path[n:])
    if len(path) >= 2 and path[1] == ":" and _isalpha(path[0]):
        return (path[:2], path[2:])
    return ("", path)


def _isalpha(ch):
    return ("a" <= ch <= "z") or ("A" <= ch <= "Z")


def _parse(path, style):
    """-> (root, rest, anchored, comps)"""
    seps = _seps(style)
    root, rest = split_root(path, style)
    rooted = bool(rest) and rest[0] in seps
    if style == "posix":
        anchored = root != ""
    else:
        if root.startswith(BS + BS):
            anchored = True
        else:
            anchored = rooted
    out = []
    cur = ""
    parts = []
    for ch in rest:
        if ch in seps:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    for c in parts:
        if c == "" or c == ".":
            continue
        if c == "..":
            if out and out[-1] != "..":
                out.pop()
            elif not anchored:
                out.append("..")
            continue
        out.append(c)
    return root, rest, rooted, out


def normalize(path, style="posix"):
    seps = _seps(style)
    root, rest, rooted, comps = _parse(path, style)
    if style == "posix":
        body = "/".join(comps)
        if root == "":
            return body if body else "."
        return root + body
    body = BS.join(comps)
    if root.startswith(BS + BS):
        if rest == "":
            return root
        return root + BS + body
    if root == "":
        if rooted:
            return BS + body
        return body if body else "."
    # drive
    if rooted:
        return root + BS + body
    return root + body


def _classify(path, style):
    root, rest, rooted, comps = _parse(path, style)
    if style == "posix":
        cls = "absolute" if root else "relative"
        key = ""
    else:
        if root.startswith(BS + BS):
            cls, key = "unc", root.lower()
        elif root:
            cls = "drive-abs" if rooted else "drive-rel"
            key = root[0].lower()
        else:
            cls = "rooted" if rooted else "relative"
            key = ""
    return cls, key, comps


def relative(path, start, style="posix"):
    _seps(style)
    pc, pk, p = _classify(path, style)
    sc, sk, s = _classify(start, style)
    if pc != sc:
        raise PathError("anchor", "%s vs %s" % (pc, sc))
    if pk != sk:
        raise PathError("root", "%s vs %s" % (pk, sk))
    if style == "win":
        fold = lambda x: x.lower()
    else:
        fold = lambda x: x
    k = 0
    while k < len(p) and k < len(s) and fold(p[k]) == fold(s[k]):
        k += 1
    out = [".."] * (len(s) - k) + p[k:]
    if not out:
        return "."
    return ("/" if style == "posix" else BS).join(out)
