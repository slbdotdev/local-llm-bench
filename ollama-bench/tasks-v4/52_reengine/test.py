import sys, os, ast, random, threading, inspect, warnings, re

TOTAL = 31
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
    import reengine
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

_SEARCH = getattr(reengine, "search", None)
_PE = getattr(reengine, "PatternError", None)

try:
    _SRC = inspect.getsource(reengine)
except Exception:
    _SRC = ""


# ------------------------------------------------------------------ helpers


def _ORC_imports():
    """Set of module names imported by the candidate module."""
    out = set()
    try:
        tree = ast.parse(_SRC)
    except Exception:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.add(node.module.split(".")[0])
    return out


def _ORC_names():
    """Bare names the candidate uses that it does not define itself."""
    try:
        tree = ast.parse(_SRC)
    except Exception:
        return None
    defined = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            defined.add(node.id)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                defined.add(a.asname or a.name.split(".")[0])
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            used.add(node.id)
    return used - defined


def _ORC_norm(r):
    """Normalise a candidate result, tolerating list/tuple containers."""
    if r is None:
        return None
    s, e, g = r
    return (int(s), int(e),
            [None if x is None else (int(x[0]), int(x[1])) for x in g])


def _ORC_kind(pattern, text="abc"):
    try:
        _SEARCH(pattern, text)
    except Exception as e:
        if not isinstance(e, ValueError):
            return "<%s>" % type(e).__name__
        if not (isinstance(_PE, type) and isinstance(e, _PE)):
            return "<not PatternError>"
        return getattr(e, "kind", "<no kind attribute>")
    return "<no raise>"


def _ORC_kinds(pairs):
    def probe():
        for pat, want in pairs:
            if _ORC_kind(pat) != want:
                return False
            if _ORC_kind(pat, "") != want:
                return False
        return True
    return probe


def _ORC_cases(table):
    def probe():
        for pat, text, want in table:
            if _ORC_norm(_SEARCH(pat, text)) != want:
                return False
        return True
    return probe


# ------------------------------------------------------- oracle: stdlib re


def _ORC_compile(pattern):
    """Compile with the oracle; None means 'skip this pattern'."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            return re.compile(pattern)
    except Exception:
        return None


def _ORC_expect(rx, text):
    m = rx.search(text)
    if m is None:
        return None
    g = []
    for i in range(rx.groups):
        sp = m.span(i + 1)
        g.append(None if sp == (-1, -1) else (sp[0], sp[1]))
    return (m.start(), m.end(), g)


# ------------------------------------------------------- pattern generator

_BS = "\\"
_ALPHA = "abc01_ -. \n\t"
_LITS = "abc01_ -.:/=,~!@#%<>&"

# weights: lit dot esc ctrl anch cls grp | pq brace lazy alt depth
_MODES = {
    "mix":   ((34, 8, 14, 4, 6, 6, 28), 0.58, 0.45, 0.35, 0.38, 2),
    "cls":   ((8, 3, 5, 2, 3, 55, 24), 0.55, 0.40, 0.30, 0.30, 2),
    "esc":   ((10, 4, 46, 14, 4, 6, 16), 0.55, 0.40, 0.30, 0.30, 2),
    "anch":  ((26, 6, 10, 3, 30, 5, 20), 0.50, 0.40, 0.30, 0.35, 2),
    "grp":   ((22, 5, 8, 2, 4, 5, 54), 0.55, 0.40, 0.35, 0.60, 2),
    "quant": ((30, 8, 12, 4, 4, 8, 34), 0.85, 0.85, 0.30, 0.30, 2),
    "lazy":  ((30, 8, 12, 4, 4, 8, 34), 0.80, 0.35, 0.85, 0.35, 2),
    "deep":  ((30, 7, 12, 4, 5, 8, 34), 0.55, 0.45, 0.35, 0.40, 3),
}
_ANCHORS = ("^", "$", _BS + "b", _BS + "B")


def _ORC_pick(rng, weights):
    tot = sum(weights)
    x = rng.random() * tot
    acc = 0.0
    for i, w in enumerate(weights):
        acc += w
        if x < acc:
            return i
    return len(weights) - 1


def _ORC_lit(rng):
    c = rng.choice(_LITS)
    if c in ".^$*+?{}[]()|" + _BS + "-":
        return _BS + c
    return c


def _ORC_class(rng):
    for _ in range(50):
        s = _ORC_class1(rng)
        if not any(x in s for x in ("--", "[[", "&&", "||", "~~", "[.", "[:",
                                    "[=")):
            return s
    return "[abc]"


def _ORC_class1(rng):
    out = []
    neg = rng.random() < 0.35
    n = rng.randint(1, 3)
    lead = rng.random() < 0.18
    for _ in range(n):
        r = rng.random()
        if r < 0.25:
            a = rng.choice("aA0_ -")
            b = rng.choice("cZ9_z")
            if ord(a) > ord(b):
                a, b = b, a
            out.append(a + "-" + b)
        elif r < 0.45:
            out.append(_BS + rng.choice("dwsDWS"))
        elif r < 0.6:
            out.append(_BS + rng.choice("-]" + _BS + "nt^"))
        elif r < 0.72:
            out.append(rng.choice(["-", "^"]))
        else:
            c = rng.choice("abc01_ .$*+?()|")
            out.append(_BS + c if c in _BS + "]^-" else c)
    body = "".join(out)
    if rng.random() < 0.2:
        body += "-"
    return "[" + ("^" if neg else "") + ("]" if lead else "") + body + "]"


def _ORC_atom(rng, cfg, depth, st):
    kind = _ORC_pick(rng, cfg[0])
    if kind == 0:
        return _ORC_lit(rng), False
    if kind == 1:
        return ".", False
    if kind == 2:
        return _BS + rng.choice("dwsDWS"), False
    if kind == 3:
        return _BS + rng.choice("nt"), False
    if kind == 4 and st["anch"] < 3:
        st["anch"] += 1
        return rng.choice(_ANCHORS), False
    if kind == 5:
        return _ORC_class(rng), False
    if depth <= 0 or st["nodes"] > 7:
        return _ORC_lit(rng), False
    st["nodes"] += 1
    inner, bq = _ORC_alt(rng, cfg, depth - 1, st)
    if rng.random() < 0.3:
        return "(?:" + inner + ")", bq
    return "(" + inner + ")", bq


def _ORC_piece(rng, cfg, depth, st):
    a, bq = _ORC_atom(rng, cfg, depth, st)
    if a in _ANCHORS:
        return a, False
    if rng.random() >= cfg[1]:
        return a, bq
    if bq:
        # body can already loop: keep the search space small
        q = rng.choice(["?", "{0,1}", "{1}", "{0}"])
        big = False
    elif rng.random() >= cfg[2]:
        q = rng.choice(["*", "+", "?"])
        big = q != "?"
    else:
        m = rng.randint(0, 3)
        r2 = rng.random()
        if r2 < 0.34:
            q = "{%d}" % m
            big = m > 1
        elif r2 < 0.67:
            q = "{%d,}" % m
            big = True
        else:
            hi = m + rng.randint(0, 3)
            q = "{%d,%d}" % (m, hi)
            big = hi > 1
    if rng.random() < cfg[3]:
        q += "?"
    return a + q, big or bq


def _ORC_cat(rng, cfg, depth, st):
    n = rng.randint(0, 4) if depth < cfg[5] else rng.randint(1, 4)
    parts = [_ORC_piece(rng, cfg, depth, st) for _ in range(n)]
    return "".join(p[0] for p in parts), any(p[1] for p in parts)


def _ORC_alt(rng, cfg, depth, st):
    r = rng.random()
    n = 3 if r < cfg[4] * 0.2 else (2 if r < cfg[4] else 1)
    parts = [_ORC_cat(rng, cfg, depth, st) for _ in range(n)]
    return "|".join(p[0] for p in parts), any(p[1] for p in parts)


def _ORC_pattern(rng, mode):
    cfg = _MODES[mode]
    st = {"nodes": 0, "anch": 0}
    return _ORC_alt(rng, cfg, cfg[5], st)[0]


def _ORC_text(rng):
    n = rng.randint(0, 9)
    return "".join(rng.choice(_ALPHA) for _ in range(n))


def _ORC_diff(seed, mode, npat, ntext=3):
    def probe():
        rng = random.Random(seed)
        for _ in range(npat):
            pat = _ORC_pattern(rng, mode)
            texts = [_ORC_text(rng) for _ in range(ntext)]
            rx = _ORC_compile(pat)
            if rx is None:
                continue
            for t in texts:
                if _ORC_norm(_SEARCH(pat, t)) != _ORC_expect(rx, t):
                    return False
        return True
    return probe


# ---------------------------------------------------------------- 1-3: bans

check("does not import re / regex / sre_compile / sre_parse / _sre",
      lambda: bool(_SRC) and _ORC_imports() is not None
      and not (_ORC_imports() & {"re", "regex", "sre_compile", "sre_parse",
                                 "_sre", "sre_constants"}))
check("does not use importlib or __import__",
      lambda: bool(_SRC) and _ORC_imports() is not None
      and "importlib" not in _ORC_imports()
      and "__import__" not in (_ORC_names() or {"__import__"}))
check("does not use the eval / exec / compile builtins",
      lambda: bool(_SRC) and _ORC_names() is not None
      and not (_ORC_names() & {"eval", "exec"})
      and "compile" not in _ORC_names())

# ------------------------------------------------- 4-6: API strictness


def api_exc():
    if not (isinstance(_PE, type) and issubclass(_PE, ValueError)):
        return False
    try:
        _SEARCH("(a", "")
    except _PE as e:
        return isinstance(getattr(e, "kind", None), str)
    return False


def api_types():
    r = _SEARCH("(a)(b)?c", "xxacz")
    if type(r) is not tuple or len(r) != 3:
        return False
    s, e, g = r
    if type(s) is not int or type(e) is not int:
        return False
    if type(g) is not list or len(g) != 2:
        return False
    if type(g[0]) is not tuple or len(g[0]) != 2:
        return False
    if type(g[0][0]) is not int or type(g[0][1]) is not int:
        return False
    if g[1] is not None:
        return False
    r2 = _SEARCH("zz", "abc")
    if r2 is not None:
        return False
    r3 = _SEARCH("ab", "xaby")
    return type(r3) is tuple and r3[2] == [] and type(r3[2]) is list


def api_values():
    return (_ORC_norm(_SEARCH("", "abc")) == (0, 0, [])
            and _ORC_norm(_SEARCH("()", "abc")) == (0, 0, [(0, 0)])
            and _SEARCH("q", "") is None
            and _ORC_norm(_SEARCH("a*", "b")) == (0, 0, [])
            and _ORC_norm(_SEARCH("(a)|(b)", "zb")) == (1, 2, [None, (1, 2)])
            and _ORC_norm(_SEARCH("x$", "x")) == (0, 1, [])
            and _ORC_norm(_SEARCH("(?:a)(b)", "ab")) == (0, 2, [(1, 2)]))


check("PatternError subclasses ValueError and carries a string .kind", api_exc)
check("exact return container types (tuple / list / int / None)", api_types)
check("None, empty matches and non-participating groups", api_values)

# ------------------------------------------------- 7-15: error kinds

check("kind unbalanced_paren / bad_group",
      _ORC_kinds([("(a", "unbalanced_paren"), ("a)", "unbalanced_paren"),
                  ("((a)", "unbalanced_paren"), (")", "unbalanced_paren"),
                  ("(?:a", "unbalanced_paren"), ("a(", "unbalanced_paren"),
                  ("(?P<x>a)", "bad_group"), ("(?=a)", "bad_group"),
                  ("(?", "bad_group"), ("(?<a)", "bad_group")]))
check("kind unterminated_class",
      _ORC_kinds([("[", "unterminated_class"), ("[]", "unterminated_class"),
                  ("[^]", "unterminated_class"), ("[abc", "unterminated_class"),
                  ("a[b-", "unterminated_class"),
                  ("[]a", "unterminated_class"),
                  ("x[^a-z", "unterminated_class")]))
check("kind bad_range",
      _ORC_kinds([("[z-a]", "bad_range"), ("[9-0]", "bad_range"),
                  ("[a-Z]", "bad_range"), ("[" + _BS + "d-z]", "bad_range"),
                  ("[a-" + _BS + "w]", "bad_range"),
                  ("[abc][z-a]", "bad_range"),
                  ("[" + _BS + "]-" + _BS + "[]", "bad_range")]))
check("kind trailing_backslash",
      _ORC_kinds([(_BS, "trailing_backslash"), ("a" + _BS, "trailing_backslash"),
                  ("[a" + _BS, "trailing_backslash"),
                  ("(a" + _BS, "trailing_backslash"),
                  ("[" + _BS + "d" + _BS, "trailing_backslash")]))
check("kind bad_escape",
      _ORC_kinds([(_BS + "q", "bad_escape"), (_BS + "1", "bad_escape"),
                  (_BS + "A", "bad_escape"), (_BS + "Z", "bad_escape"),
                  (_BS + "x41", "bad_escape"), ("[" + _BS + "B]", "bad_escape"),
                  ("[" + _BS + "y]", "bad_escape"),
                  ("a|" + _BS + "0", "bad_escape")]))
check("kind nothing_to_repeat",
      _ORC_kinds([("*a", "nothing_to_repeat"), ("?x", "nothing_to_repeat"),
                  ("+", "nothing_to_repeat"), ("(*)", "nothing_to_repeat"),
                  ("(?:*a)", "nothing_to_repeat"), ("a|*", "nothing_to_repeat"),
                  ("{2}", "nothing_to_repeat"), ("{2,1}", "nothing_to_repeat"),
                  ("a|{0,3}", "nothing_to_repeat"),
                  ("(a)|?", "nothing_to_repeat")]))
check("kind multiple_repeat",
      _ORC_kinds([("a**", "multiple_repeat"), ("a*?*", "multiple_repeat"),
                  ("a?{2}", "multiple_repeat"), ("a{1,2}+", "multiple_repeat"),
                  ("a*+", "multiple_repeat"), ("(a)?*", "multiple_repeat"),
                  ("a{2}{3}", "multiple_repeat"), ("a+??", "multiple_repeat")]))
check("kind anchor_repeat",
      _ORC_kinds([("^*", "anchor_repeat"), ("a$?", "anchor_repeat"),
                  ("a" + _BS + "b+", "anchor_repeat"),
                  (_BS + "B{2}", "anchor_repeat"),
                  ("^{0,2}", "anchor_repeat"), ("a$*?", "anchor_repeat")]))
check("kind bad_repeat",
      _ORC_kinds([("a{3,1}", "bad_repeat"), ("a{1,0}", "bad_repeat"),
                  ("(ab){10,2}", "bad_repeat"), ("a{2,1}?", "bad_repeat"),
                  ("x{0,}y{5,4}", "bad_repeat")]))
check("error precedence on doubly malformed patterns",
      _ORC_kinds([("(a{3,1}", "bad_repeat"), ("*[abc", "nothing_to_repeat"),
                  ("[abc*", "unterminated_class"),
                  ("(" + _BS + "q", "bad_escape"),
                  ("(a**", "multiple_repeat"), ("[z-a", "bad_range"),
                  ("(^*", "anchor_repeat"), ("a)(", "unbalanced_paren"),
                  ("[a" + _BS, "trailing_backslash"),
                  ("^{2,1}", "bad_repeat"), ("^*+", "anchor_repeat"),
                  ("(([a-", "unterminated_class"),
                  ("[" + _BS + "d-z](", "bad_range"),
                  ("(?:*)", "nothing_to_repeat"),
                  ("(a" + _BS, "trailing_backslash"),
                  ("a{1,2}{3}", "multiple_repeat")]))

# ------------------------------------------- 16-21: hand-written behaviour

_ORC_LOOK = [
    ('{', 'a{b', (1, 2, [])),
    ('a{x}', 'za{x}', (1, 5, [])),
    ('a{', 'ba{', (1, 3, [])),
    ('a{2', 'a{2', (0, 3, [])),
    ('a{}', 'a{}', (0, 3, [])),
    ('a{,}', 'a{,}', (0, 1, [])),
    ('a{2,x}', 'a{2,x}', (0, 6, [])),
    (']', 'a]b', (1, 2, [])),
    ('}', 'x}', (1, 2, [])),
    ('[]]', 'a]', (1, 2, [])),
    ('[]]', 'ab', None),
    ('[^]]', ']a', (1, 2, [])),
    ('[]a]', 'za', (1, 2, [])),
    ('[-a]', 'b-c', (1, 2, [])),
    ('[a-]', 'x-', (1, 2, [])),
    ('[a\\-z]', 'q-q', (1, 2, [])),
    ('a*{', 'aaa{', (0, 4, [])),
    ('()', 'xy', (0, 0, [(0, 0)])),
    ('(|a)', 'aa', (0, 0, [(0, 0)])),
    ('a||b', 'b', (0, 0, [])),
    ('', 'abc', (0, 0, [])),
    ('[\\b]', 'a\x08b', (1, 2, [])),
    ('\\-', 'a-b', (1, 2, [])),
    ('[.]', 'a.b', (1, 2, [])),
    ('[[a]', 'z[b', (1, 2, [])),
    ('[$*+?]', 'q+', (1, 2, [])),
    ('a{1}{', 'a{', (0, 2, [])),
    ('[\\]]', 'x]', (1, 2, [])),
    ('[^-a]', '-b', (1, 2, [])),
    ('x{0,}', 'xxx', (0, 3, [])),
]
_ORC_ANCH = [
    ('^a', 'ab', (0, 1, [])),
    ('^a', 'ba', None),
    ('a$', 'ba', (1, 2, [])),
    ('a$', 'a\n', (0, 1, [])),
    ('a$', 'a\nb', None),
    ('.$', 'x\n', (0, 1, [])),
    ('^$', '\n', (0, 0, [])),
    ('^$', '', (0, 0, [])),
    ('^$', 'ab', None),
    ('$', 'ab\n', (2, 2, [])),
    ('$', 'ab\n\n', (3, 3, [])),
    ('\\bfoo\\b', 'a foo b', (2, 5, [])),
    ('\\bfoo\\b', 'afoo b', None),
    ('\\Bar', 'bar car', (1, 3, [])),
    ('\\b', '', None),
    ('\\b', '_a', (0, 0, [])),
    ('a\\b', 'ab a', (3, 4, [])),
    ('^', 'abc', (0, 0, [])),
    ('.', '\n', None),
    ('.', 'a\nb', (0, 1, [])),
    ('[^a]', 'a\nb', (1, 2, [])),
    ('^\\Ba', 'ab', None),
    ('\\B', 'ab', (1, 1, [])),
    ('\\B$', 'ab', None),
    ('\\d\\b\\w', '1 2', None),
    ('\\W', 'a b', (1, 2, [])),
    ('\\S+', '  ab ', (2, 4, [])),
    ('\\s', 'a\tb', (1, 2, [])),
    ('[\\d\\s]+', 'a1 2b', (1, 4, [])),
    ('[^\\w]', 'ab-c', (2, 3, [])),
]
_ORC_GREED = [
    ('a*', 'baaa', (0, 0, [])),
    ('a*?', 'baaa', (0, 0, [])),
    ('a+?b', 'aaab', (0, 4, [])),
    ('<.*>', '<a><b>', (0, 6, [])),
    ('<.*?>', '<a><b>', (0, 3, [])),
    ('a??', 'aa', (0, 0, [])),
    ('a??b', 'aab', (1, 3, [])),
    ('(a|ab)(c|bcd)', 'abcd', (0, 4, [(0, 1), (1, 4)])),
    ('.*?', 'abc', (0, 0, [])),
    ('(a|ab)(c|bcd)(d*)', 'abcd', (0, 4, [(0, 1), (1, 4), (4, 4)])),
    ('a*a', 'aaa', (0, 3, [])),
    ('a*?a', 'aaa', (0, 1, [])),
    ('.*b', 'abab', (0, 4, [])),
    ('.*?b', 'abab', (0, 2, [])),
    ('(a+)(a*)', 'aaa', (0, 3, [(0, 3), (3, 3)])),
    ('(a+?)(a*)', 'aaa', (0, 3, [(0, 1), (1, 3)])),
    ('[ab]*?b', 'aabab', (0, 3, [])),
    ('x*', 'abc', (0, 0, [])),
    ('(a*)*?', 'aaa', (0, 0, [None])),
    ('(?:ab|a)(b?)', 'ab', (0, 2, [(2, 2)])),
]
_ORC_BOUND = [
    ('a{2,3}', 'aaaa', (0, 3, [])),
    ('a{2,3}?', 'aaaa', (0, 2, [])),
    ('a{0}', 'aaa', (0, 0, [])),
    ('a{0}b', 'ab', (1, 2, [])),
    ('a{3,}', 'aaaaa', (0, 5, [])),
    ('a{,2}', 'aaa', (0, 2, [])),
    ('a{,2}?', 'aaa', (0, 0, [])),
    ('(ab){2}', 'ababab', (0, 4, [(2, 4)])),
    ('a{2,}?', 'aaaa', (0, 2, [])),
    ('(a{2}){2}', 'aaaa', (0, 4, [(2, 4)])),
    ('a{1,1}', 'ba', (1, 2, [])),
    ('(a|b){3}', 'abab', (0, 3, [(2, 3)])),
    ('(a|b){3}?', 'abab', (0, 3, [(2, 3)])),
    ('[abc]{2,4}x', 'abcax', (0, 5, [])),
    ('(){3}', '', (0, 0, [(0, 0)])),
    ('(a?){3}', 'a', (0, 1, [(1, 1)])),
    ('(a?){3}b', 'b', (0, 1, [(0, 0)])),
    ('a{0,0}', 'aaa', (0, 0, [])),
    ('(?:a|){2}', 'a', (0, 1, [])),
    ('\\d{2,4}', '1234567', (0, 4, [])),
]
_ORC_GRP = [
    ('(a*)*', 'aaa', (0, 3, [(3, 3)])),
    ('(a*)+', 'aaa', (0, 3, [(3, 3)])),
    ('(a?)*', 'aaa', (0, 3, [(3, 3)])),
    ('(){3}', 'x', (0, 0, [(0, 0)])),
    ('(?:(a)|(b))+', 'ab', (0, 2, [(0, 1), (1, 2)])),
    ('(a)|(b)', 'b', (0, 1, [None, (0, 1)])),
    ('(a(b)?)+', 'aba', (0, 3, [(2, 3), (1, 2)])),
    ('((a)|b)*', 'ab', (0, 2, [(1, 2), (0, 1)])),
    ('(a|b)*', 'ab', (0, 2, [(1, 2)])),
    ('(?:a|(b))*', 'ba', (0, 2, [(0, 1)])),
    ('(a*)*b', 'aaab', (0, 4, [(3, 3)])),
    ('(|a)*', 'aa', (0, 0, [(0, 0)])),
    ('((a)*)*', 'aa', (0, 2, [(2, 2), (1, 2)])),
    ('(a)*', 'b', (0, 0, [None])),
    ('(a)?', 'b', (0, 0, [None])),
    ('(a)|b', 'b', (0, 1, [None])),
    ('(?:(a)b)?c', 'c', (0, 1, [None])),
    ('((a)|(b))+', 'ab', (0, 2, [(1, 2), (0, 1), (1, 2)])),
    ('(a(b)*)+', 'abba', (0, 4, [(3, 4), (2, 3)])),
    ('((a)b|a(c))*', 'abac', (0, 4, [(2, 4), (0, 1), (3, 4)])),
    ('(x)(y)?(z)', 'xz', (0, 2, [(0, 1), None, (1, 2)])),
    ('((((a))))', 'a', (0, 1, [(0, 1), (0, 1), (0, 1), (0, 1)])),
    ('(a)(?:(b)|c)', 'ac', (0, 2, [(0, 1), None])),
    ('(?:(a)|b)+', 'ba', (0, 2, [(1, 2)])),
]

check("constructs that look malformed but are literal / legal",
      _ORC_cases(_ORC_LOOK))
def visible():
    if _SEARCH("^b", "ab") is not None:
        return False
    return _ORC_cases([
        ("a+b", "xaaab", (1, 5, [])),
        (r"(\d+)-(\d+)", "sum 12-345!", (4, 10, [(4, 6), (7, 10)])),
        ("colou?r", "color", (0, 5, [])),
        ("(x)|(y)", "wy", (1, 2, [None, (1, 2)])),
    ])()


check("visible examples", visible)
check("anchors, dot, $ before a trailing newline, word boundaries",
      _ORC_cases(_ORC_ANCH))
check("greedy versus non-greedy", _ORC_cases(_ORC_GREED))
check("bounded repetition {m,n}", _ORC_cases(_ORC_BOUND))
check("group capture across repetitions and empty-loop repeats",
      _ORC_cases(_ORC_GRP))

# --------------------------------------- 22-29: randomised differential

check("differential A: mixed syntax, index bucket 1",
      _ORC_diff(910001, "mix", 1000))
check("differential B: mixed syntax, index bucket 2",
      _ORC_diff(910002, "mix", 1000))
check("differential C: character classes", _ORC_diff(910003, "cls", 1000))
check("differential D: escapes and class escapes",
      _ORC_diff(910004, "esc", 1000))
check("differential E: anchors and boundaries",
      _ORC_diff(910005, "anch", 1000))
check("differential F: groups and alternation",
      _ORC_diff(910006, "grp", 1000))
check("differential G: bounded quantifiers", _ORC_diff(910007, "quant", 1000))
check("differential H: non-greedy quantifiers", _ORC_diff(910008, "lazy", 800))
check("differential I: deeper nesting", _ORC_diff(910009, "deep", 500))

_t.cancel()
report()
