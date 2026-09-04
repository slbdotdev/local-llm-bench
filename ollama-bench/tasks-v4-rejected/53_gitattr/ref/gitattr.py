"""Reference implementation: gitattributes-style path -> attribute resolver."""


class AttrError(ValueError):
    def __init__(self, kind, msg=None):
        ValueError.__init__(self, msg if msg is not None else kind)
        self.kind = kind


_LOWER = "abcdefghijklmnopqrstuvwxyz"
_UPPER = _LOWER.upper()
_DIGIT = "0123456789"
_PUNCT = "".join(chr(c) for c in list(range(33, 48)) + list(range(58, 65))
                 + list(range(91, 97)) + list(range(123, 127)))

_POSIX = {
    "alpha": set(_LOWER + _UPPER),
    "digit": set(_DIGIT),
    "alnum": set(_LOWER + _UPPER + _DIGIT),
    "space": set(" \t\n\v\f\r"),
    "upper": set(_UPPER),
    "lower": set(_LOWER),
    "punct": set(_PUNCT),
    "xdigit": set(_DIGIT + "abcdef" + "ABCDEF"),
}

_NAME_HEAD = set(_LOWER + _UPPER + "_")
_NAME_TAIL = set(_LOWER + _UPPER + _DIGIT + "-_.")


def _valid_name(s):
    if not s:
        return False
    if s[0] not in _NAME_HEAD:
        return False
    for ch in s[1:]:
        if ch not in _NAME_TAIL:
            return False
    return True


# ---------------------------------------------------------------- line prep

def _strip_trailing_ws(line):
    end = len(line)
    while end > 0 and line[end - 1] in " \t":
        bs = 0
        k = end - 2
        while k >= 0 and line[k] == "\\":
            bs += 1
            k -= 1
        if bs % 2 == 1:
            break
        end -= 1
    return line[:end]


def _split_line(line):
    """Return (pattern_text, [attr_field, ...])."""
    out = []
    i = 0
    n = len(line)
    esc = False
    while i < n:
        c = line[i]
        if esc:
            out.append(c)
            esc = False
        elif c == "\\":
            out.append(c)
            esc = True
        elif c in " \t":
            break
        else:
            out.append(c)
        i += 1
    return "".join(out), line[i:].split()


def _parse_spec(field):
    if field[0] in "-!":
        name = field[1:]
        val = False if field[0] == "-" else None
        if "=" in name:
            raise AttrError("bad_attr_name", "bad attribute spec: %r" % (field,))
    elif "=" in field:
        k = field.index("=")
        name = field[:k]
        val = field[k + 1:]
    else:
        name = field
        val = True
    if not _valid_name(name):
        raise AttrError("bad_attr_name", "bad attribute name: %r" % (field,))
    return (name, val)


# ------------------------------------------------------------ pattern parse

DSTAR = ("**",)


def _parse_class(seg, i):
    """seg[i] == '['. Return (next_index, ('cls', neg, items))."""
    n = len(seg)
    j = i + 1
    neg = False
    if j < n and seg[j] in "!^":
        neg = True
        j += 1
    items = []
    first = True
    while True:
        if j >= n:
            raise AttrError("unterminated_class")
        c = seg[j]
        if c == "]" and not first:
            return j + 1, ("cls", neg, items)
        first = False
        if c == "[" and j + 1 < n and seg[j + 1] == ":":
            k = seg.find(":]", j + 2)
            if k < 0:
                raise AttrError("bad_posix_class", "unterminated posix class")
            nm = seg[j + 2:k]
            if nm not in _POSIX:
                raise AttrError("bad_posix_class", "unknown posix class: %r" % (nm,))
            items.append(("p", nm))
            j = k + 2
            continue
        if c == "\\":
            if j + 1 >= n:
                raise AttrError("trailing_backslash")
            ch = seg[j + 1]
            j += 2
        else:
            ch = c
            j += 1
        if j < n and seg[j] == "-" and j + 1 < n and seg[j + 1] != "]":
            j += 1
            c2 = seg[j]
            if c2 == "\\":
                if j + 1 >= n:
                    raise AttrError("trailing_backslash")
                ch2 = seg[j + 1]
                j += 2
            else:
                ch2 = c2
                j += 1
            items.append(("r", ch, ch2))
        else:
            items.append(("c", ch))


def _tokenize(seg):
    toks = []
    i = 0
    n = len(seg)
    while i < n:
        c = seg[i]
        if c == "\\":
            if i + 1 >= n:
                raise AttrError("trailing_backslash")
            toks.append(("l", seg[i + 1]))
            i += 2
        elif c == "*":
            while i < n and seg[i] == "*":
                i += 1
            toks.append(("*",))
        elif c == "?":
            toks.append(("?",))
            i += 1
        elif c == "[":
            i, tk = _parse_class(seg, i)
            toks.append(tk)
        else:
            toks.append(("l", c))
            i += 1
    return toks


def _split_segments(pat):
    segs = []
    cur = []
    i = 0
    n = len(pat)
    while i < n:
        c = pat[i]
        if c == "\\":
            cur.append(c)
            if i + 1 < n:
                cur.append(pat[i + 1])
                i += 2
            else:
                i += 1
            continue
        if c == "/":
            segs.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    segs.append("".join(cur))
    return segs


def _has_unescaped_slash(pat):
    return len(_split_segments(pat)) > 1


def _compile_pattern(pat):
    if pat == "":
        raise AttrError("empty_pattern")
    # trailing unescaped '/' ?
    if pat.endswith("/"):
        bs = 0
        k = len(pat) - 2
        while k >= 0 and pat[k] == "\\":
            bs += 1
            k -= 1
        if bs % 2 == 0:
            raise AttrError("trailing_slash")
    if pat.startswith("/"):
        anchored = True
        while pat.startswith("/"):
            pat = pat[1:]
    else:
        anchored = _has_unescaped_slash(pat)
    if pat == "":
        raise AttrError("empty_pattern")
    raw = _split_segments(pat)
    segs = []
    never = False
    for s in raw:
        if s == "":
            never = True
            segs.append([])
        elif s == "**" and anchored:
            segs.append(DSTAR)
        else:
            segs.append(_tokenize(s))
    return (anchored, segs, never)


# ----------------------------------------------------------------- matching

def _cls_has(item_list, neg, ch):
    hit = False
    for it in item_list:
        if it[0] == "c":
            if ch == it[1]:
                hit = True
        elif it[0] == "r":
            if it[1] <= ch <= it[2]:
                hit = True
        else:
            if ch in _POSIX[it[1]]:
                hit = True
        if hit:
            break
    return (not hit) if neg else hit


def _tok_match(tok, ch):
    if tok[0] == "l":
        return ch == tok[1]
    if tok[0] == "?":
        return True
    return _cls_has(tok[2], tok[1], ch)


def _seg_match(toks, comp):
    ti = 0
    ci = 0
    star_t = -1
    star_c = 0
    nt = len(toks)
    nc = len(comp)
    while ci < nc:
        if ti < nt and toks[ti][0] == "*":
            star_t = ti
            ti += 1
            star_c = ci
            continue
        if ti < nt and _tok_match(toks[ti], comp[ci]):
            ti += 1
            ci += 1
            continue
        if star_t >= 0:
            star_c += 1
            ci = star_c
            ti = star_t + 1
            continue
        return False
    while ti < nt and toks[ti][0] == "*":
        ti += 1
    return ti == nt


def _segs_match(segs, si, comps, ci):
    ns = len(segs)
    nc = len(comps)
    while si < ns:
        seg = segs[si]
        if seg is DSTAR:
            if si + 1 == ns:
                return True
            for k in range(ci, nc + 1):
                if _segs_match(segs, si + 1, comps, k):
                    return True
            return False
        if ci >= nc:
            return False
        if not (seg and _seg_match(seg, comps[ci])):
            return False
        si += 1
        ci += 1
    return ci == nc


def _matches(rule, comps):
    anchored, segs, never = rule
    if never:
        return False
    if anchored:
        return _segs_match(segs, 0, comps, 0)
    return bool(segs[0]) and _seg_match(segs[0], comps[-1])


# ------------------------------------------------------------------ compile

def compile_attrs(lines):
    macros = {}
    rules = []
    for raw in lines:
        line = _strip_trailing_ws(raw)
        if line == "":
            continue
        if line[0] == "#":
            continue
        if line.startswith("[attr]"):
            body = line[6:]
            name, fields = _split_line(body)
            if not _valid_name(name):
                raise AttrError("bad_macro_name", "bad macro name: %r" % (name,))
            if not fields:
                raise AttrError("no_attrs")
            if name in macros:
                raise AttrError("duplicate_macro", "duplicate macro: %r" % (name,))
            macros[name] = [_parse_spec(f) for f in fields]
            continue
        pat, fields = _split_line(line)
        if pat == "":
            raise AttrError("empty_pattern")
        rule = _compile_pattern(pat)
        if not fields:
            raise AttrError("no_attrs")
        specs = [_parse_spec(f) for f in fields]
        rules.append((rule, specs))
    # cycle detection over macro references
    state = {}

    def visit(nm):
        st = state.get(nm, 0)
        if st == 1:
            raise AttrError("macro_cycle", "macro cycle at %r" % (nm,))
        if st == 2:
            return
        state[nm] = 1
        for (n2, _v) in macros[nm]:
            if n2 in macros:
                visit(n2)
        state[nm] = 2

    for nm in list(macros):
        visit(nm)
    return (rules, macros)


def check_attrs(path, compiled):
    rules, macros = compiled
    comps = path.split("/")
    res = {}

    def apply(specs):
        for (name, val) in specs:
            res[name] = val
            if val is True and name in macros:
                apply(macros[name])

    for (rule, specs) in rules:
        if _matches(rule, comps):
            apply(specs)
    return res
