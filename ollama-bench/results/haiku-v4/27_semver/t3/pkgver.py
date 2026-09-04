"""Semantic-version parsing, comparison and range matching."""
import re
from functools import cmp_to_key

_IDENT = re.compile(r"^[0-9A-Za-z-]+$")
_OPS = (">=", "<=", "==", "!=", ">", "<")


def parse(s):
    """Parse 'MAJOR.MINOR.PATCH' or 'MAJOR.MINOR.PATCH-PRERELEASE' into the tuple
    (major, minor, patch, pre) where major/minor/patch are ints and `pre` is a
    tuple of prerelease identifiers -- each one an int if it is purely numeric,
    else the identifier string.  `pre` is the empty tuple for a release version.

    Numeric components (major, minor, patch and numeric prerelease identifiers)
    are decimal and must not carry leading zeros: '01' is invalid, '0' is fine.
    Prerelease identifiers are dot separated, non-empty and made only of
    [0-9A-Za-z-].  The whole string must contain no whitespace and nothing
    else (no 'v' prefix, no '+build' metadata).  Anything else raises
    ValueError.
    """
    if not isinstance(s, str):
        raise ValueError("not a string")
    core, sep, pre = s.partition("-")
    parts = core.split(".")
    if len(parts) != 3:
        raise ValueError("bad version core: %r" % s)
    for p in parts:
        if not p.isdigit():
            raise ValueError("bad numeric component: %r" % p)
        # Check for leading zeros: '01' is invalid, but '0' is fine
        if len(p) > 1 and p[0] == '0':
            raise ValueError("bad numeric component: %r" % p)
    major, minor, patch = (int(p) for p in parts)
    ids = ()
    if sep:
        if pre == "":
            raise ValueError("empty prerelease: %r" % s)
        out = []
        for ident in pre.split("."):
            if not ident or not _IDENT.match(ident):
                raise ValueError("bad prerelease identifier: %r" % ident)
            # Convert purely numeric identifiers to integers
            if ident.isdigit():
                # Check for leading zeros in numeric prerelease identifiers
                if len(ident) > 1 and ident[0] == '0':
                    raise ValueError("bad prerelease identifier: %r" % ident)
                out.append(int(ident))
            else:
                out.append(ident)
        ids = tuple(out)
    return (major, minor, patch, ids)


def _cmp(a, b):
    return (a > b) - (a < b)


def compare(a, b):
    """Compare two version strings by semver precedence, returning -1, 0 or 1.

    major/minor/patch are compared numerically first.  If they are equal, a
    version WITH a prerelease has LOWER precedence than the same version
    without one (1.0.0-alpha < 1.0.0).  Two prereleases are compared identifier
    by identifier: numeric identifiers compare numerically and always rank below
    alphanumeric ones, alphanumeric identifiers compare by ASCII string order,
    and if one list is a prefix of the other the shorter one is smaller.
    """
    pa, pb = parse(a), parse(b)
    c = _cmp(pa[:3], pb[:3])
    if c:
        return c
    ra, rb = pa[3], pb[3]
    for x, y in zip(ra, rb):
        xn, yn = isinstance(x, int), isinstance(y, int)
        if xn != yn:
            return -1 if xn else 1
        if x != y:
            return _cmp(x, y)
    # Handle the case where one version is a release and the other is a prerelease
    # A release version (empty prerelease) is greater than a prerelease version
    if not ra and not rb:
        return 0
    if not ra:
        return 1  # a is a release, b is a prerelease; release > prerelease
    if not rb:
        return -1  # a is a prerelease, b is a release; prerelease < release
    return _cmp(len(ra), len(rb))


def sort_versions(versions):
    """Return a new list of the versions sorted ascending by precedence.
    Stable for equal precedence; the input sequence is never mutated."""
    return sorted(list(versions), key=cmp_to_key(compare))


def latest(versions):
    """Return the highest-precedence version string, or None for an empty
    sequence.  If several versions tie, return the earliest one in the input."""
    best = None
    for v in versions:
        if best is None or compare(v, best) > 0:
            best = v
    return best


def satisfies(version, spec):
    """True if `version` satisfies every constraint in `spec`.

    `spec` is a comma-separated list of constraints, each an operator out of
    '==', '!=', '>=', '<=', '>', '<' immediately followed by a version.
    Surrounding whitespace anywhere is ignored.  An empty/blank spec is
    satisfied by every valid version.  A missing or unknown operator, an empty
    constraint, or an unparsable version raises ValueError.
    """
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
