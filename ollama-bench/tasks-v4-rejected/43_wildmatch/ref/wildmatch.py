"""Reference solution: brace-expanding wildcard matcher over flat strings."""


class PatternError(ValueError):
    def __init__(self, kind, message=None):
        ValueError.__init__(self, message or kind)
        self.kind = kind


# --------------------------------------------------------------------------
# brace expansion
# --------------------------------------------------------------------------

def _split_parts(body):
    """Split a group body on depth-0 unescaped commas; None if there are none."""
    parts = []
    cur = []
    depth = 0
    found = False
    i = 0
    n = len(body)
    while i < n:
        c = body[i]
        if c == "\\":
            cur.append(c)
            if i + 1 < n:
                cur.append(body[i + 1])
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
            found = True
            i += 1
            continue
        cur.append(c)
        i += 1
    parts.append("".join(cur))
    return parts if found else None


def _find_group(p):
    """Return (open_idx, close_idx, parts) of the first expandable group, or None."""
    i = 0
    n = len(p)
    while i < n:
        c = p[i]
        if c == "\\":
            i += 2
            continue
        if c != "{":
            i += 1
            continue
        depth = 0
        k = i
        close = -1
        while k < n:
            ch = p[k]
            if ch == "\\":
                k += 2
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    close = k
                    break
            k += 1
        if close < 0:
            i += 1
            continue
        parts = _split_parts(p[i + 1:close])
        if parts is None:
            i = close + 1
            continue
        return i, close, parts
    return None


def expand(pattern):
    g = _find_group(pattern)
    if g is None:
        return [pattern]
    i, close, parts = g
    prefix = pattern[:i]
    suffix = pattern[close + 1:]
    out = []
    for part in parts:
        out.extend(expand(prefix + part + suffix))
    return out


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

_PUNCT = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

POSIX = {
    "digit": set("0123456789"),
    "upper": set(chr(c) for c in range(65, 91)),
    "lower": set(chr(c) for c in range(97, 123)),
    "alpha": set(chr(c) for c in range(65, 91)) | set(chr(c) for c in range(97, 123)),
    "alnum": (set(chr(c) for c in range(65, 91)) | set(chr(c) for c in range(97, 123))
              | set("0123456789")),
    "xdigit": set("0123456789ABCDEFabcdef"),
    "space": set(" \t\n\v\f\r"),
    "punct": set(_PUNCT),
}


def _parse_class(p, i):
    """Parse a bracket expression starting at p[i] == '['.  Returns (item, next_i)."""
    n = len(p)
    j = i + 1
    neg = False
    if j < n and p[j] in "!^":
        neg = True
        j += 1
    members = []
    first = True
    while True:
        if j >= n:
            raise PatternError("unterminated_class")
        c = p[j]
        if c == "]" and not first:
            return ("class", neg, members), j + 1
        first = False
        if c == "\\":
            if j + 1 >= n:
                raise PatternError("trailing_backslash")
            ch = p[j + 1]
            j += 2
        elif c == "[" and j + 1 < n and p[j + 1] == ":":
            k = p.find(":]", j + 2)
            if k < 0:
                raise PatternError("unterminated_posix")
            name = p[j + 2:k]
            if name not in POSIX:
                raise PatternError("unknown_class")
            members.append(("cls", name))
            j = k + 2
            continue
        else:
            ch = c
            j += 1
        # possible range
        if j < n and p[j] == "-" and j + 1 < n and p[j + 1] != "]":
            if p[j + 1] == "\\":
                if j + 2 >= n:
                    raise PatternError("trailing_backslash")
                members.append(("rng", ch, p[j + 2]))
                j += 3
            else:
                members.append(("rng", ch, p[j + 1]))
                j += 2
        else:
            members.append(("ch", ch))


def _parse(p):
    items = []
    i = 0
    n = len(p)
    while i < n:
        c = p[i]
        if c == "\\":
            if i + 1 >= n:
                raise PatternError("trailing_backslash")
            items.append(("lit", p[i + 1]))
            i += 2
        elif c == "*":
            if not items or items[-1][0] != "star":
                items.append(("star",))
            i += 1
        elif c == "?":
            items.append(("any",))
            i += 1
        elif c == "[":
            item, i = _parse_class(p, i)
            items.append(item)
        else:
            items.append(("lit", c))
            i += 1
    return items


# --------------------------------------------------------------------------
# matching
# --------------------------------------------------------------------------

def _swap(c):
    if "a" <= c <= "z":
        return chr(ord(c) - 32)
    if "A" <= c <= "Z":
        return chr(ord(c) + 32)
    return c


def _member_hit(m, c):
    if m[0] == "ch":
        return c == m[1]
    if m[0] == "rng":
        return m[1] <= c <= m[2]
    return c in POSIX[m[1]]


def _item_match(it, c, cf):
    kind = it[0]
    if kind == "any":
        return True
    if kind == "lit":
        return c == it[1] or (cf and _swap(c) == it[1])
    neg, members = it[1], it[2]
    hit = False
    for m in members:
        if _member_hit(m, c) or (cf and _member_hit(m, _swap(c))):
            hit = True
            break
    return (not hit) if neg else hit


def _match_items(items, text, cf):
    n = len(text)
    reach = [False] * (n + 1)
    reach[0] = True
    for it in items:
        if it[0] == "star":
            first = -1
            for idx in range(n + 1):
                if reach[idx]:
                    first = idx
                    break
            if first < 0:
                return False
            reach = [idx >= first for idx in range(n + 1)]
            continue
        new = [False] * (n + 1)
        any_new = False
        for idx in range(n):
            if reach[idx] and _item_match(it, text[idx], cf):
                new[idx + 1] = True
                any_new = True
        if not any_new:
            return False
        reach = new
    return reach[n]


def match(pattern, text, casefold=False):
    parsed = [_parse(alt) for alt in expand(pattern)]
    for items in parsed:
        if _match_items(items, text, casefold):
            return True
    return False


def filter(patterns, texts, casefold=False):
    parsed = []
    for pat in patterns:
        for alt in expand(pat):
            parsed.append(_parse(alt))
    out = []
    for t in texts:
        for items in parsed:
            if _match_items(items, t, casefold):
                out.append(t)
                break
    return out
