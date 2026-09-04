"""Hidden grader for 43_wildmatch: brace-expanding wildcard matcher over flat strings.

The oracle below (`_ora_*`) is an independent reference implementation that translates a
pattern to a Python `re` regex.  `re` is allowed here but forbidden to the candidate.
"""
import sys, os, re, random, threading, inspect

TOTAL = 29
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
    import wildmatch
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


class _MissingErr(Exception):
    pass


PE = getattr(wildmatch, "PatternError", None)
if not (isinstance(PE, type) and issubclass(PE, BaseException)):
    PE = _MissingErr


def _cand_expand(p):
    return wildmatch.expand(p)


def _cand_match(p, t, cf=False):
    return wildmatch.match(p, t, cf) if cf else wildmatch.match(p, t)


# =====================================================================
# oracle
# =====================================================================
class _OraErr(Exception):
    def __init__(self, kind):
        Exception.__init__(self, kind)
        self.kind = kind


_ORA_POSIX = {
    "digit": "0123456789",
    "upper": "".join(chr(c) for c in range(0x41, 0x5B)),
    "lower": "".join(chr(c) for c in range(0x61, 0x7B)),
    "alpha": "".join(chr(c) for c in list(range(0x41, 0x5B)) + list(range(0x61, 0x7B))),
    "alnum": "".join(chr(c) for c in list(range(0x30, 0x3A)) + list(range(0x41, 0x5B))
                     + list(range(0x61, 0x7B))),
    "xdigit": "0123456789ABCDEFabcdef",
    "space": " \t\n\x0b\x0c\r",
    "punct": "".join(chr(c) for c in range(0x21, 0x7F)
                     if not chr(c).isdigit() and not ("A" <= chr(c) <= "Z")
                     and not ("a" <= chr(c) <= "z")),
}
_ORA_LETTERS = _ORA_POSIX["alpha"]


def _ora_swap(c):
    if "a" <= c <= "z":
        return chr(ord(c) - 32)
    if "A" <= c <= "Z":
        return chr(ord(c) + 32)
    return c


def _ora_escmap(s):
    """esc[i] is True iff s[i] is escaped by the backslash in front of it."""
    esc = [False] * len(s)
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            esc[i + 1] = True
            i += 2
        else:
            i += 1
    return esc


def _ora_expand_into(p, out):
    esc = _ora_escmap(p)
    n = len(p)
    i = 0
    while i < n:
        if p[i] != "{" or esc[i]:
            i += 1
            continue
        depth = 0
        close = -1
        k = i
        while k < n:
            if not esc[k]:
                if p[k] == "{":
                    depth += 1
                elif p[k] == "}":
                    depth -= 1
                    if depth == 0:
                        close = k
                        break
            k += 1
        if close < 0:
            i += 1
            continue
        parts = []
        depth = 0
        last = i + 1
        found = False
        for t in range(i + 1, close):
            if esc[t]:
                continue
            ch = p[t]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append(p[last:t])
                last = t + 1
                found = True
        parts.append(p[last:close])
        if not found:
            i = close + 1
            continue
        head, tail = p[:i], p[close + 1:]
        for part in parts:
            _ora_expand_into(head + part + tail, out)
        return
    out.append(p)


def _ora_expand(p):
    acc = []
    _ora_expand_into(p, acc)
    return acc


def _ora_in(mem, c):
    for m in mem:
        if m[0] == "c":
            if c == m[1]:
                return True
        elif m[0] == "r":
            if m[1] <= c <= m[2]:
                return True
        elif c in _ORA_POSIX[m[1]]:
            return True
    return False


def _ora_cls_rx(mem, neg, cf):
    bits = []
    for m in mem:
        if m[0] == "c":
            bits.append(re.escape(m[1]))
        elif m[0] == "r":
            if ord(m[1]) <= ord(m[2]):
                bits.append(re.escape(m[1]) + "-" + re.escape(m[2]))
        else:
            bits.append("".join(re.escape(x) for x in _ORA_POSIX[m[1]]))
    if cf:
        for L in _ORA_LETTERS:
            if _ora_in(mem, _ora_swap(L)) and not _ora_in(mem, L):
                bits.append(re.escape(L))
    if not bits:
        return "[\\s\\S]" if neg else "(?!x)x"
    return "[" + ("^" if neg else "") + "".join(bits) + "]"


def _ora_lit_rx(ch, cf):
    chars = [ch]
    if cf and _ora_swap(ch) != ch:
        chars.append(_ora_swap(ch))
    return "[" + "".join(re.escape(c) for c in chars) + "]"


def _ora_class(s, i, cf):
    n = len(s)
    j = i + 1
    neg = j < n and s[j] in "!^"
    if neg:
        j += 1
    body_start = j
    mem = []
    while True:
        if j >= n:
            raise _OraErr("unterminated_class")
        ch = s[j]
        if ch == "]" and j > body_start:
            return _ora_cls_rx(mem, neg, cf), j + 1
        if ch == "\\":
            if j + 1 >= n:
                raise _OraErr("trailing_backslash")
            base = s[j + 1]
            j += 2
        elif ch == "[" and s[j + 1:j + 2] == ":":
            end = s.find(":]", j + 2)
            if end < 0:
                raise _OraErr("unterminated_posix")
            nm = s[j + 2:end]
            if nm not in _ORA_POSIX:
                raise _OraErr("unknown_class")
            mem.append(("p", nm))
            j = end + 2
            continue
        else:
            base = ch
            j += 1
        if j + 1 < n and s[j] == "-" and s[j + 1] != "]":
            if s[j + 1] == "\\":
                if j + 2 >= n:
                    raise _OraErr("trailing_backslash")
                mem.append(("r", base, s[j + 2]))
                j += 3
            else:
                mem.append(("r", base, s[j + 1]))
                j += 2
        else:
            mem.append(("c", base))


def _ora_alt_rx(alt, cf):
    out = []
    i = 0
    n = len(alt)
    while i < n:
        c = alt[i]
        if c == "\\":
            if i + 1 >= n:
                raise _OraErr("trailing_backslash")
            out.append(_ora_lit_rx(alt[i + 1], cf))
            i += 2
        elif c == "*":
            out.append("[\\s\\S]*")
            i += 1
        elif c == "?":
            out.append("[\\s\\S]")
            i += 1
        elif c == "[":
            piece, i = _ora_class(alt, i, cf)
            out.append(piece)
        else:
            out.append(_ora_lit_rx(c, cf))
            i += 1
    return "".join(out)


_ORA_CACHE = {}


def _ora_match(pattern, text, cf=False):
    key = (pattern, cf)
    rxs = _ORA_CACHE.get(key)
    if rxs is None:
        rxs = [re.compile(_ora_alt_rx(a, cf)) for a in _ora_expand(pattern)]
        _ORA_CACHE[key] = rxs
    for rx in rxs:
        if rx.fullmatch(text):
            return True
    return False


# =====================================================================
# comparison helpers
# =====================================================================
def _cmp_one(pat, text, cf):
    """Compare candidate against the oracle for one (pattern, text, casefold)."""
    try:
        want = _ora_match(pat, text, cf)
        werr = None
    except _OraErr as e:
        want, werr = None, e.kind
    try:
        got = _cand_match(pat, text, cf)
        gerr = None
    except PE as e:
        got, gerr = None, getattr(e, "kind", "<no .kind>")
    except Exception as e:
        return False
    if werr is not None:
        return gerr == werr
    return gerr is None and isinstance(got, bool) and got == want


def _cmp_expand(pat):
    want = _ora_expand(pat)
    try:
        got = _cand_expand(pat)
    except Exception:
        return False
    return isinstance(got, list) and got == want


def _all(cases, fn):
    def probe():
        for c in cases:
            if not fn(*c):
                return False
        return True
    return probe


def kind_of(pat):
    try:
        _cand_match(pat, "x")
    except PE as e:
        return getattr(e, "kind", "<no .kind>")
    except Exception as e:
        return "<%s>" % type(e).__name__
    return "<no raise>"


def kinds(pairs):
    def probe():
        for pat, want in pairs:
            if kind_of(pat) != want:
                return False
        return True
    return probe


# =====================================================================
# case generation
# =====================================================================
ALPHA = "abcAB0 ._-/]!^"

LITS = "abX0._-/ "

CLASSES = [
    ("[abc]", "abcd"), ("[a-c]", "abcABd"), ("[!a-c]", "adX0"), ("[^xy]", "xyab"),
    ("[]a]", "]a["), ("[a-]", "a-b"), ("[-a]", "-ab"), ("[z-a5]", "5za"),
    ("[[:digit:]]", "07a"), ("[![:space:]]", " a0"), ("[[:alpha:]0-9]", "a0Z-"),
    ("[[:upper:]x]", "Xxa"), ("[\\]]", "]a"), ("[\\-z]", "-za"),
    ("[A-Ca-c]", "AaBd"), ("[[:xdigit:]]", "fF9g"), ("[[:punct:]]", "!.a"),
    ("[b[:lower:]]", "bqA"), ("[[:alnum:]-]", "a9-."), ("[[]", "[a"),
    ("[[:lower:][:digit:]]", "a0A"), ("[![:upper:]]", "Xa0"),
]

BRACES = [
    ("{a,b}", ["a", "b"]),
    ("{,x}", ["", "x"]),
    ("{a,}", ["a", ""]),
    ("{p,q,r}", ["p", "q", "r"]),
    ("{a{b,c}}", ["{a{b,c}}", "abc"]),
    ("{}", ["{}", ""]),
    ("{x{a,b},c}", ["xa", "xb", "c"]),
    ("{1..3}", ["{1..3}", "1"]),
    ("\\{a,b\\}", ["{a,b}", "a"]),
    ("{a\\,b,c}", ["a,b", "c"]),
    ("{X,y}", ["X", "y", "x", "Y"]),
    ("{[a-c],?}", ["a", "Z"]),
]

ESCAPES = [("\\*", "*"), ("\\?", "?"), ("\\[", "["), ("\\{", "{"),
           ("\\\\", "\\"), ("\\a", "a"), ("\\-", "-"), ("\\]", "]")]


def _gen_pattern(rng, mode):
    """Return (pattern, derived_text) with pattern <= 20 chars, <=3 stars, <=3 braces."""
    pat = []
    txt = []
    stars = 0
    braces = 0
    length = 0
    for _ in range(rng.randint(1, 6)):
        r = rng.random()
        if mode == "brace":
            r = 0.30 + r * 0.25 if r < 0.5 else r
        if mode == "class" and r < 0.55:
            piece, pool = rng.choice(CLASSES)
            sample = rng.choice(pool)
        elif r < 0.28:
            piece = rng.choice(LITS)
            sample = piece if rng.random() < 0.8 else rng.choice(ALPHA)
        elif r < 0.40:
            if braces >= 3:
                continue
            piece, pool = rng.choice(BRACES)
            sample = rng.choice(pool)
            braces += 1
        elif r < 0.52:
            if stars >= 3:
                continue
            piece = "*"
            sample = "".join(rng.choice(ALPHA) for _ in range(rng.randint(0, 2)))
            stars += 1
        elif r < 0.60:
            piece = "?"
            sample = rng.choice(ALPHA)
        elif r < 0.88:
            piece, sample = rng.choice(CLASSES)
            sample = rng.choice(sample)
        else:
            piece, sample = rng.choice(ESCAPES)
        if length + len(piece) > 20:
            break
        pat.append(piece)
        txt.append(sample)
        length += len(piece)
    return "".join(pat), "".join(txt)


def _rand_text(rng):
    return "".join(rng.choice(ALPHA) for _ in range(rng.randint(0, 6)))


def _perturb(rng, s):
    out = []
    for c in s:
        r = rng.random()
        if r < 0.25:
            out.append(_ora_swap(c))
        elif r < 0.32:
            out.append(rng.choice(ALPHA))
        else:
            out.append(c)
    return "".join(out)


def gen_cases(seed, n, mode, cf=False):
    rng = random.Random(seed)
    cases = []
    while len(cases) < n:
        pat, txt = _gen_pattern(rng, mode)
        if mode == "trunc" and pat:
            cut = rng.randint(1, len(pat))
            pat = pat[:cut]
        if cf:
            txt = _perturb(rng, txt)
        cases.append((pat, txt, cf))
        if len(cases) < n:
            cases.append((pat, _rand_text(rng), cf))
        if len(cases) < n and rng.random() < 0.4:
            cases.append((pat, _perturb(rng, txt), cf))
    return cases[:n]


def gen_brace_patterns(seed, n):
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        pat, _ = _gen_pattern(rng, "brace")
        out.append((pat,))
    return out


def slice_cases(cases, k, i):
    return [c for j, c in enumerate(cases) if j % k == i]


# =====================================================================
# 1-2: API surface and forbidden imports
# =====================================================================
check("PatternError subclasses ValueError and carries .kind",
      lambda: isinstance(getattr(wildmatch, "PatternError", None), type)
      and issubclass(wildmatch.PatternError, ValueError)
      and kind_of("[abc") == "unterminated_class")

check("does not import fnmatch/re/glob/pathlib",
      lambda: not re.search(r"^[ \t]*(?:import|from)[ \t]+(?:fnmatch|re|glob|pathlib)\b",
                            inspect.getsource(wildmatch), re.M))

# =====================================================================
# 3-8: brace expansion
# =====================================================================
check("expand: cross product order, leftmost group slowest",
      lambda: _cand_expand("a{b,c}d") == ["abd", "acd"]
      and _cand_expand("{a,b}{c,d}") == ["ac", "ad", "bc", "bd"]
      and _cand_expand("{a,b}{c,d}{e,f}")
      == ["ace", "acf", "ade", "adf", "bce", "bcf", "bde", "bdf"]
      and _cand_expand("plain") == ["plain"]
      and _cand_expand("") == [""])

check("expand: a group with no depth-0 comma stays literal",
      lambda: _cand_expand("{a}") == ["{a}"]
      and _cand_expand("{}") == ["{}"]
      and _cand_expand("{1..3}") == ["{1..3}"]
      and _cand_expand("{a{b,c}}") == ["{a{b,c}}"]
      and _cand_expand("{a}{b,c}") == ["{a}b", "{a}c"]
      and _cand_expand("x{a{b,c}}y{d,e}") == ["x{a{b,c}}yd", "x{a{b,c}}ye"])

check("expand: unmatched braces are literal characters",
      lambda: _cand_expand("{a,b") == ["{a,b"]
      and _cand_expand("a}b") == ["a}b"]
      and _cand_expand("{a{b,c}") == ["{ab", "{ac"]
      and _cand_expand("}{a,b}") == ["}a", "}b"]
      and _cand_expand("{a,b}}") == ["a}", "b}"])

check("expand: escaped braces and commas do not open/close/split",
      lambda: _cand_expand("\\{a,b\\}") == ["\\{a,b\\}"]
      and _cand_expand("{a\\,b,c}") == ["a\\,b", "c"]
      and _cand_expand("\\{a,b}") == ["\\{a,b}"]
      and _cand_expand("{a,b\\}c}") == ["a", "b\\}c"]
      and _cand_expand("\\\\{a,b}") == ["\\\\a", "\\\\b"])

check("expand: empty alternatives, nesting, duplicates kept",
      lambda: _cand_expand("a{,b}") == ["a", "ab"]
      and _cand_expand("{,}") == ["", ""]
      and _cand_expand("{a,}z") == ["az", "z"]
      and _cand_expand("{a,b{c,d}}") == ["a", "bc", "bd"]
      and _cand_expand("{x{a,b},c}") == ["xa", "xb", "c"]
      and _cand_expand("{a,a}") == ["a", "a"]
      and _cand_expand("{,{p,q}}") == ["", "p", "q"])

_BP = gen_brace_patterns(4301, 260)
check("expand: randomised differential A", _all(slice_cases(_BP, 2, 0), _cmp_expand))
check("expand: randomised differential B", _all(slice_cases(_BP, 2, 1), _cmp_expand))

# =====================================================================
# 9-14: matching semantics
# =====================================================================
check("wildcards match the whole flat text, including / and dots",
      _all([("a*c", "abbbc", False), ("a*c", "ac", False), ("*", "", False),
            ("*", "a/b/.c", False), ("a*", "a", False), ("*a", "xa", False),
            ("a?c", "abc", False), ("a?c", "ac", False), ("?", "", False),
            ("", "", False), ("", "x", False), ("a*b*c", "axxbyyc", False),
            ("a*b*c", "abd", False), ("*/*", "a/b", False), ("?", "/", False),
            ("*.log", ".log", False), ("a", "ab", False), ("ab", "a", False),
            ("\\*x", "*x", False), ("\\*x", "yx", False)], _cmp_one))

check("bracket basics: members, ranges, both negation spellings",
      _all([("[abc]", "b", False), ("[abc]", "d", False), ("[a-c]", "b", False),
            ("[a-c]", "d", False), ("[!a-c]", "d", False), ("[!a-c]", "a", False),
            ("[^a-c]", "d", False), ("[^a-c]", "b", False), ("[a-cx0-9]", "7", False),
            ("[a-cx0-9]", "y", False), ("x[ab]y", "xay", False), ("[abc]", "ab", False),
            ("[!a]", "", False), ("[^]", "^", False), ("[a^]", "^", False)], _cmp_one))

check("bracket edges: ']' first, '-' first/last, escapes inside",
      _all([("[]]", "]", False), ("[]a]", "a", False), ("[]a]", "]", False),
            ("[!]a]", "b", False), ("[!]a]", "]", False), ("[^]x]", "]", False),
            ("[a-]", "-", False), ("[a-]", "a", False), ("[a-]", "b", False),
            ("[-a]", "-", False), ("[-ac]", "c", False), ("[\\]]", "]", False),
            ("[\\]]", "a", False), ("[\\-z]", "-", False), ("[\\-z]", "z", False),
            ("[\\-z]", "b", False), ("[a\\]b]", "]", False), ("[[]", "[", False),
            ("[[]", "a", False)], _cmp_one))

check("reversed ranges match nothing but the rest of the class still applies",
      _all([("[z-a]", "a", False), ("[z-a]", "z", False), ("[z-a]", "m", False),
            ("[z-a5]", "5", False), ("[z-a5]", "a", False), ("[5z-a]", "5", False),
            ("[!z-a]", "q", False), ("[!z-a5]", "5", False), ("[!z-a5]", "q", False),
            ("[c-a-x]", "-", False), ("[9-0]", "5", False)], _cmp_one))

def posix_sets():
    probe = ("0", "5", "a", "z", "A", "Z", "f", "F", "g", " ", "\t", "\n", "\v", "\f",
             "\r", "!", "_", "~", "/", "]", "\\", "^", "-", "\xe9", "\xc9", "\xb5", "\xa0")
    for name in ("digit", "alpha", "alnum", "space", "upper", "lower", "punct",
                 "xdigit"):
        pat = "[[:%s:]]" % name
        for ch in probe:
            if not _cmp_one(pat, ch, False):
                return False
    return True


check("POSIX class member sets are exactly right (ASCII only)", posix_sets)

check("POSIX classes mixed with members and inside negated classes",
      _all([("[[:digit:]x-z]", "y", False), ("[[:digit:]x-z]", "4", False),
            ("[[:digit:]x-z]", "b", False), ("[![:digit:]]", "a", False),
            ("[![:digit:]]", "7", False), ("[^[:space:]]", " ", False),
            ("[^[:space:]]", "q", False), ("[[:alpha:][:digit:]]", "3", False),
            ("[[:alpha:][:digit:]]", "-", False), ("[b[:upper:]]", "b", False),
            ("[b[:upper:]]", "Q", False), ("[[:digit:]-z]", "-", False),
            ("[[:digit:]-z]", "z", False), ("[[:digit:]-z]", "m", False),
            ("[![:punct:]a]", "a", False), ("[![:punct:]a]", "b", False),
            ("*[[:digit:]]", "ab7", False), ("*[[:digit:]]", "ab7c", False)], _cmp_one))

# =====================================================================
# 15-16: casefold
# =====================================================================
check("casefold: literals and plain class members",
      _all([("A", "a", True), ("A", "a", False), ("a", "A", True),
            ("[A]", "a", True), ("[a]", "A", True), ("[abc]", "B", True),
            ("AB*", "abxy", True), ("\\A", "a", True), ("?", "A", True),
            ("[_]", "_", True), ("\xc9", "\xe9", True),
            ("x[!a]", "xA", True), ("[!a]", "A", True), ("[!a]", "b", True),
            ("[^ab]", "B", True), ("[!a]", "A", False)], _cmp_one))

check("casefold: ranges and POSIX classes",
      _all([("[a-c]", "B", True), ("[X-Z]", "y", True), ("[0-9]", "a", True),
            ("[a-c]", "D", True), ("[A-C]", "b", True), ("[[:upper:]]", "q", True),
            ("[[:lower:]]", "Q", True), ("[[:upper:]]", "q", False),
            ("[[:xdigit:]]", "F", True), ("[[:xdigit:]]", "G", True),
            ("[[:digit:]]", "a", True), ("[![:upper:]]", "q", True),
            ("[![:lower:]]", "Q", True), ("[![:digit:]]", "A", True),
            ("[!a-c]", "B", True), ("[!a-c]", "D", True),
            ("{A,b}", "a", True), ("{A,b}", "B", True)], _cmp_one))

# =====================================================================
# 17-18: errors
# =====================================================================
check("error kinds",
      kinds([("a\\", "trailing_backslash"), ("\\", "trailing_backslash"),
             ("[a\\", "trailing_backslash"), ("[a-\\", "trailing_backslash"),
             ("[abc", "unterminated_class"), ("[", "unterminated_class"),
             ("[]", "unterminated_class"), ("[!]", "unterminated_class"),
             ("[^]", "unterminated_class"), ("a*[x-", "unterminated_class"),
             ("[[:dig", "unterminated_posix"), ("[[:", "unterminated_posix"),
             ("[[:foo:]]", "unknown_class"), ("[[:Digit:]]", "unknown_class"),
             ("[[:word:]x]", "unknown_class")]))

check("error precedence: leftmost failure wins, and later alternatives are parsed",
      kinds([("[[:alpha:]", "unterminated_class"), ("[[:foo:]", "unknown_class"),
             ("[a][bc", "unterminated_class"), ("[a]x\\", "trailing_backslash"),
             ("[a\\]", "unterminated_class"), ("*[[:foo:]]\\", "unknown_class"),
             ("{a,[bc}", "unterminated_class"), ("{a,x}\\", "trailing_backslash"),
             ("{[z,a}", "unterminated_class")]))

# =====================================================================
# 19: filter
# =====================================================================
def filter_probe():
    f = getattr(wildmatch, "filter", None)
    if f is None:
        return False
    if f(["*.log", "a?"], ["x.log", "ab", "abc"]) != ["x.log", "ab"]:
        return False
    if f([], ["a", "b"]) != []:
        return False
    if f(["*"], []) != []:
        return False
    if f(["a", "b"], ["b", "a", "b"]) != ["b", "a", "b"]:
        return False
    if f(["{a,b}?"], ["ax", "bx", "cx", "ax"]) != ["ax", "bx", "ax"]:
        return False
    if f(["A*"], ["ax", "Ax", "bx"], True) != ["ax", "Ax"]:
        return False
    if f(["[[:digit:]]"], ["1", "a", "1"]) != ["1", "1"]:
        return False
    try:
        f(["[a"], ["x"])
    except PE:
        return True
    except Exception:
        return False
    return False


check("filter(): order preserved, duplicates kept, any-pattern semantics", filter_probe)

# =====================================================================
# 20-28: randomised differential families
# =====================================================================
_GEN = gen_cases(4311, 330, "general")
for _i in range(3):
    check("randomised differential, general patterns (bucket %d)" % (_i + 1),
          _all(slice_cases(_GEN, 3, _i), _cmp_one))

_CLS = gen_cases(4322, 300, "class")
for _i in range(3):
    check("randomised differential, bracket-heavy patterns (bucket %d)" % (_i + 1),
          _all(slice_cases(_CLS, 3, _i), _cmp_one))

_CF = gen_cases(4333, 260, "general", cf=True)
for _i in range(2):
    check("randomised differential, casefold=True (bucket %d)" % (_i + 1),
          _all(slice_cases(_CF, 2, _i), _cmp_one))

_TRUNC = gen_cases(4344, 260, "trunc")
check("randomised differential, truncated/malformed patterns",
      _all(_TRUNC, _cmp_one))

_t.cancel()
report()
