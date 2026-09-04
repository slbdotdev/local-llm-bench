"""Semantic-version parsing, comparison and range matching."""
import re
from functools import cmp_to_key

_IDENT = re.compile(r"^[0-9A-Za-z-]+$")
_NUM = re.compile(r"^(0|[1-9][0-9]*)$")
_OPS = ("==", "!=", ">=", "<=", ">", "<")


def _numeric(s):
    if not _NUM.match(s):
        raise ValueError("bad numeric component: %r" % s)
    return int(s)


def parse(s):
    """'MAJOR.MINOR.PATCH[-PRE]' -> (major, minor, patch, pre_tuple)."""
    if not isinstance(s, str):
        raise ValueError("not a string")
    core, sep, pre = s.partition("-")
    parts = core.split(".")
    if len(parts) != 3:
        raise ValueError("bad version core: %r" % s)
    major, minor, patch = (_numeric(p) for p in parts)
    ids = ()
    if sep:
        if pre == "":
            raise ValueError("empty prerelease: %r" % s)
        out = []
        for ident in pre.split("."):
            if not ident or not _IDENT.match(ident):
                raise ValueError("bad prerelease identifier: %r" % ident)
            if ident.isdigit():
                out.append(_numeric(ident))
            else:
                out.append(ident)
        ids = tuple(out)
    return (major, minor, patch, ids)


def _cmp(a, b):
    return (a > b) - (a < b)


def compare(a, b):
    """-1 / 0 / 1 by semver precedence."""
    pa, pb = parse(a), parse(b)
    c = _cmp(pa[:3], pb[:3])
    if c:
        return c
    ra, rb = pa[3], pb[3]
    if not ra and not rb:
        return 0
    if not ra:
        return 1
    if not rb:
        return -1
    for x, y in zip(ra, rb):
        xn, yn = isinstance(x, int), isinstance(y, int)
        if xn != yn:
            return -1 if xn else 1
        if x != y:
            return _cmp(x, y)
    return _cmp(len(ra), len(rb))


def sort_versions(versions):
    """Ascending by precedence, stable, input not mutated."""
    return sorted(list(versions), key=cmp_to_key(compare))


def latest(versions):
    """Highest precedence version, earliest occurrence on ties, None if empty."""
    best = None
    for v in versions:
        if best is None or compare(v, best) > 0:
            best = v
    return best


def satisfies(version, spec):
    """True if `version` meets every comma-separated constraint in `spec`."""
    parse(version)
    spec = spec.strip()
    if not spec:
        return True
    for part in spec.split(","):
        part = part.strip()
        if not part:
            raise ValueError("empty constraint")
        for op in _OPS:
            if part.startswith(op):
                rhs = part[len(op):].strip()
                break
        else:
            raise ValueError("bad constraint: %r" % part)
        c = compare(version, rhs)
        ok = {"==": c == 0, "!=": c != 0, ">=": c >= 0,
              "<=": c <= 0, ">": c > 0, "<": c < 0}[op]
        if not ok:
            return False
    return True
