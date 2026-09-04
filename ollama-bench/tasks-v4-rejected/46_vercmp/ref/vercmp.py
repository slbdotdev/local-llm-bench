"""Version comparison and constraint-range evaluation."""

import functools

_DIGITS = "0123456789"
_ALNUM = set("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
_BUILD_CHARS = _ALNUM | {"-"}
_WS = " \t\n\r\f\v"


class VersionError(ValueError):
    """Raised for any malformed version string or constraint expression."""


def _is_num(s):
    return len(s) > 0 and all(c in _DIGITS for c in s)


def _ident(s, allowed=_ALNUM):
    if not s:
        raise VersionError("empty identifier")
    for c in s:
        if c not in allowed:
            raise VersionError("bad character %r" % (c,))
    return int(s) if _is_num(s) else s


def parse(text):
    """Parse a version string into {'epoch','release','pre','build'}."""
    if not isinstance(text, str):
        raise VersionError("version must be a str")
    rest = text
    epoch = 0
    if ":" in rest:
        head, rest = rest.split(":", 1)
        if not _is_num(head):
            raise VersionError("bad epoch %r" % (head,))
        epoch = int(head)
    build = None
    if "+" in rest:
        rest, braw = rest.split("+", 1)
        if not braw:
            raise VersionError("empty build")
        for piece in braw.split("."):
            _ident(piece, _BUILD_CHARS)
        build = braw
    pre = None
    if "-" in rest:
        rest, praw = rest.split("-", 1)
        pre = [_ident(p) for p in praw.split(".")]
    release = [_ident(p) for p in rest.split(".")]
    return {"epoch": epoch, "release": release, "pre": pre, "build": build}


def _sign(a, b):
    return (a > b) - (a < b)


def _cmp_seg(a, b):
    an, bn = isinstance(a, int), isinstance(b, int)
    if an and bn:
        return _sign(a, b)
    if an:
        return -1
    if bn:
        return 1
    return _sign(a, b)


def _cmp_release(x, y):
    a = list(x["release"])
    b = list(y["release"])
    n = max(len(a), len(b))
    a += [0] * (n - len(a))
    b += [0] * (n - len(b))
    for u, v in zip(a, b):
        c = _cmp_seg(u, v)
        if c:
            return c
    return 0


def _cmp_parsed(x, y):
    c = _sign(x["epoch"], y["epoch"])
    if c:
        return c
    c = _cmp_release(x, y)
    if c:
        return c
    p, q = x["pre"], y["pre"]
    if p is None and q is None:
        return 0
    if p is None:
        return 1
    if q is None:
        return -1
    for u, v in zip(p, q):
        c = _cmp_seg(u, v)
        if c:
            return c
    return _sign(len(p), len(q))


def compare(a, b):
    """Return -1/0/1 for the total order over version strings."""
    return _cmp_parsed(parse(a), parse(b))


def _mk(epoch, rel, pre=None):
    return {"epoch": epoch, "release": list(rel), "pre": pre, "build": None}


_OPS = (">=", "<=", "==", "!=", ">", "<", "=", "^", "~")


def _numeric_release(p):
    r = p["release"]
    if not (1 <= len(r) <= 3):
        raise VersionError("caret/tilde needs 1-3 release segments")
    for s in r:
        if not isinstance(s, int):
            raise VersionError("caret/tilde needs numeric release segments")
    return r


def _caret(p):
    r = _numeric_release(p)
    e = p["epoch"]
    a = r[0]
    b = r[1] if len(r) > 1 else 0
    c = r[2] if len(r) > 2 else 0
    if a != 0:
        upper = [a + 1, 0, 0]
    elif len(r) == 1:
        upper = [1, 0, 0]
    elif b != 0:
        upper = [0, b + 1, 0]
    elif len(r) == 2:
        upper = [0, 1, 0]
    else:
        upper = [0, 0, c + 1]
    return [(">=", _mk(e, [a, b, c], p["pre"])), ("<", _mk(e, upper))]


def _tilde(p):
    r = _numeric_release(p)
    e = p["epoch"]
    a = r[0]
    b = r[1] if len(r) > 1 else 0
    c = r[2] if len(r) > 2 else 0
    if len(r) == 1:
        upper = [a + 1, 0, 0]
    else:
        upper = [a, b + 1, 0]
    return [(">=", _mk(e, [a, b, c], p["pre"])), ("<", _mk(e, upper))]


def _wildcard(tok):
    """Return primitives for a wildcard token, or None if tok is not one."""
    if "*" not in tok:
        return None
    if tok == "*":
        return []
    segs = tok.split(".")
    if segs[-1] != "*" or len(segs) not in (2, 3):
        raise VersionError("bad wildcard %r" % (tok,))
    for s in segs[:-1]:
        if not _is_num(s):
            raise VersionError("bad wildcard %r" % (tok,))
    nums = [int(s) for s in segs[:-1]]
    if len(nums) == 1:
        lo = [nums[0], 0, 0]
        hi = [nums[0] + 1, 0, 0]
    else:
        lo = [nums[0], nums[1], 0]
        hi = [nums[0], nums[1] + 1, 0]
    return [(">=", _mk(0, lo)), ("<", _mk(0, hi))]


def _parse_comparator(tok):
    """Return (primitives, gates) for one comparator token."""
    if not tok:
        raise VersionError("empty comparator")
    op = "="
    for cand in _OPS:
        if tok.startswith(cand):
            op = cand
            tok = tok[len(cand):]
            break
    else:
        cand = None
    if "*" in tok:
        if cand is not None:
            raise VersionError("wildcard cannot take an operator")
        prims = _wildcard(tok)
        return prims, []
    p = parse(tok)
    gates = [p] if p["pre"] is not None else []
    if op == "^":
        return _caret(p), gates
    if op == "~":
        return _tilde(p), gates
    if op == "==":
        op = "="
    return [(op, p)], gates


def _parse_constraint(text):
    if not isinstance(text, str):
        raise VersionError("constraint must be a str")
    t = "".join(ch for ch in text if ch not in _WS)
    if not t:
        raise VersionError("empty constraint")
    groups = []
    for part in t.split("||"):
        if not part:
            raise VersionError("empty and-list")
        prims = []
        gates = []
        for tok in part.split(","):
            pr, ga = _parse_comparator(tok)
            prims.extend(pr)
            gates.extend(ga)
        groups.append((prims, gates))
    return groups


def _test(op, c):
    if op == ">=":
        return c >= 0
    if op == ">":
        return c > 0
    if op == "<=":
        return c <= 0
    if op == "<":
        return c < 0
    if op == "=":
        return c == 0
    if op == "!=":
        return c != 0
    raise VersionError("bad operator")


def _match_group(pv, group):
    prims, gates = group
    if pv["pre"] is not None:
        ok = False
        for g in gates:
            if g["epoch"] == pv["epoch"] and _cmp_release(g, pv) == 0:
                ok = True
                break
        if not ok:
            return False
    for op, opv in prims:
        if not _test(op, _cmp_parsed(pv, opv)):
            return False
    return True


def satisfies(version, constraint):
    """True if version is accepted by at least one and-list of constraint."""
    pv = parse(version)
    groups = _parse_constraint(constraint)
    for g in groups:
        if _match_group(pv, g):
            return True
    return False


def sort_versions(versions):
    """Stable ascending sort of a list of version strings."""
    if isinstance(versions, str):
        raise VersionError("expected a list of version strings")
    items = list(versions)
    parsed = {}
    for i, v in enumerate(items):
        parsed[i] = parse(v)
    order = sorted(range(len(items)),
                   key=functools.cmp_to_key(
                       lambda i, j: _cmp_parsed(parsed[i], parsed[j])))
    return [items[i] for i in order]


def best_match(versions, constraint):
    """Highest version in the list satisfying the constraint, else None."""
    if isinstance(versions, str):
        raise VersionError("expected a list of version strings")
    items = list(versions)
    groups = _parse_constraint(constraint)
    best = None
    best_p = None
    for v in items:
        pv = parse(v)
        hit = False
        for g in groups:
            if _match_group(pv, g):
                hit = True
                break
        if not hit:
            continue
        if best_p is None or _cmp_parsed(pv, best_p) > 0:
            best, best_p = v, pv
    return best
