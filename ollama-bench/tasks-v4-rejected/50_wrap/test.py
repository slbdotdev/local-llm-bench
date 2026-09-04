import sys, os, re, random, threading, inspect, unicodedata

TOTAL = 27
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
    import dwrap
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


def _missing(*a, **k):
    raise AttributeError("attribute missing from dwrap")


C_CW = getattr(dwrap, "char_width", _missing)
C_W = getattr(dwrap, "width", _missing)
C_CL = getattr(dwrap, "clusters", _missing)
C_ET = getattr(dwrap, "expand_tabs", _missing)
C_WR = getattr(dwrap, "wrap", _missing)
C_TR = getattr(dwrap, "truncate", _missing)

# ----------------------------------------------------------------------
# Inlined oracle.  Names are prefixed _orc_ so they can never collide.
# ----------------------------------------------------------------------
_ORC_ZWJ = chr(0x200D)
_ORC_ZW = (chr(0x200B), chr(0x200C), chr(0x200D), chr(0xFEFF))


def _orc_cw(ch):
    if unicodedata.combining(ch) != 0:
        return 0
    if ch in _ORC_ZW:
        return 0
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    return 1


def _orc_w(s):
    return sum(_orc_cw(c) for c in s)


def _orc_clusters(s):
    res = []
    n = len(s)
    i = 0
    while i < n:
        j = i + 1
        while j < n:
            c = s[j]
            if unicodedata.combining(c) != 0 or c in _ORC_ZW:
                j += 1
                if c == _ORC_ZWJ and j < n:
                    j += 1
                continue
            break
        res.append(s[i:j])
        i = j
    return res


def _orc_expand(s, tabsize=8):
    buf = []
    col = 0
    for ch in s:
        if ch == "\t":
            pad = tabsize - (col % tabsize)
            buf.append(" " * pad)
            col += pad
        elif ch == "\n":
            buf.append(ch)
            col = 0
        else:
            buf.append(ch)
            col += _orc_cw(ch)
    return "".join(buf)


def _orc_tokens(cl):
    """cl: cluster list of one segment -> list of (is_gap, clusters)."""
    toks = []
    k = 0
    m = len(cl)
    while k < m:
        if cl[k] == " ":
            start = k
            while k < m and cl[k] == " ":
                k += 1
            toks.append((True, cl[start:k]))
        else:
            acc = []
            while k < m and cl[k] != " ":
                acc.append(cl[k])
                if cl[k][:1] == "-":
                    toks.append((False, acc))
                    acc = []
                k += 1
            if acc:
                toks.append((False, acc))
    return toks


def _orc_seg(seg, budget):
    out = []
    cur = ""
    held = ""
    for is_gap, cls in _orc_tokens(_orc_clusters(seg)):
        body = "".join(cls)
        if is_gap:
            if cur != "":
                held = held + body
            continue
        if cur != "" and _orc_w(cur) + _orc_w(held) + _orc_w(body) <= budget:
            cur = cur + held + body
            held = ""
            continue
        if cur != "":
            out.append(cur)
            cur = ""
            held = ""
        if _orc_w(body) <= budget:
            cur = body
        else:
            piece = ""
            for c in cls:
                if piece != "" and _orc_w(piece) + _orc_w(c) > budget:
                    out.append(piece)
                    piece = ""
                piece = piece + c
            cur = piece
    if cur != "":
        out.append(cur)
    if not out:
        out.append("")
    return out


def _orc_wrap(text, budget, tabsize=8):
    res = []
    for seg in _orc_expand(text, tabsize).split("\n"):
        res.extend(_orc_seg(seg, budget))
    return res


def _orc_trunc(s, budget, ellipsis=chr(0x2026)):
    if _orc_w(s) <= budget:
        return s
    ew = _orc_w(ellipsis)
    if ew > budget:
        return ""
    room = budget - ew
    keep = []
    used = 0
    for c in _orc_clusters(s):
        cw = _orc_cw(c[0]) + sum(_orc_cw(x) for x in c[1:])
        if used + cw > room:
            break
        keep.append(c)
        used += cw
    while keep and keep[-1] == " ":
        keep.pop()
    return "".join(keep) + ellipsis


# ----------------------------------------------------------------------
# Case generators
# ----------------------------------------------------------------------
_WIDE = [chr(x) for x in (0x4E2D, 0x65E5, 0x3042, 0xFF21, 0x30C4)]
_AMB = [chr(x) for x in (0x2026, 0x00B1, 0x00E9, 0x2010)]
_HALF = [chr(x) for x in (0xFF76, 0xFF9E, 0xFF6F)]
_MARK = [chr(x) for x in (0x0301, 0x0308, 0x0327, 0x0653)]
_ZWC = [chr(x) for x in (0x200B, 0x200C, 0x200D, 0xFEFF)]
_LET = list("abcdefg")


def _gen_ascii(rng, n):
    out = []
    for _ in range(n):
        r = rng.random()
        if r < 0.70:
            out.append(rng.choice(_LET))
        elif r < 0.95:
            out.append(" ")
        else:
            out.append("-")
    return "".join(out)


def _gen_spaces(rng, n):
    out = []
    for _ in range(n):
        r = rng.random()
        if r < 0.45:
            out.append(rng.choice(_LET))
        else:
            out.append(" " * rng.randint(1, 4))
    return "".join(out)


def _gen_hyphen(rng, n):
    out = []
    for _ in range(n):
        r = rng.random()
        if r < 0.55:
            out.append(rng.choice(_LET))
        elif r < 0.85:
            out.append("-" * rng.randint(1, 2))
        else:
            out.append(" ")
    return "".join(out)


def _gen_wide(rng, n):
    out = []
    for _ in range(n):
        r = rng.random()
        if r < 0.45:
            out.append(rng.choice(_WIDE))
        elif r < 0.65:
            out.append(rng.choice(_LET))
        elif r < 0.78:
            out.append(rng.choice(_AMB))
        elif r < 0.88:
            out.append(rng.choice(_HALF))
        else:
            out.append(" ")
    return "".join(out)


def _gen_marks(rng, n):
    out = []
    for _ in range(n):
        r = rng.random()
        if r < 0.30:
            out.append(rng.choice(_LET))
        elif r < 0.45:
            out.append(rng.choice(_WIDE))
        elif r < 0.70:
            out.append(rng.choice(_MARK))
        elif r < 0.88:
            out.append(rng.choice(_ZWC))
        else:
            out.append(" ")
    return "".join(out)


def _gen_long(rng, n):
    pool = _LET + _WIDE + _MARK + _ZWC + ["-"]
    return "".join(rng.choice(pool) for _ in range(n))


def _gen_tabs(rng, n):
    out = []
    for _ in range(n):
        r = rng.random()
        if r < 0.45:
            out.append(rng.choice(_LET))
        elif r < 0.60:
            out.append(rng.choice(_WIDE))
        elif r < 0.80:
            out.append("\t")
        elif r < 0.90:
            out.append(" ")
        else:
            out.append("\n")
    return "".join(out)


def _gen_lines(rng, n):
    out = []
    for _ in range(n):
        r = rng.random()
        if r < 0.45:
            out.append(rng.choice(_LET))
        elif r < 0.65:
            out.append("\n")
        elif r < 0.85:
            out.append(" ")
        else:
            out.append(rng.choice(_WIDE))
    return "".join(out)


def _gen_mixed(rng, n):
    pool = _LET + _WIDE + _AMB + _HALF + _MARK + _ZWC + [" ", " ", "  ", "-", "\t", "\n"]
    return "".join(rng.choice(pool) for _ in range(n))


# ----------------------------------------------------------------------
# Differential drivers
# ----------------------------------------------------------------------

def diff_width(seed, gen, cases=300, maxlen=24):
    def probe():
        rng = random.Random(seed)
        for _ in range(cases):
            s = gen(rng, rng.randint(0, maxlen))
            if C_W(s) != _orc_w(s):
                return False
        return True
    return probe


def diff_clusters(seed, gen, cases=300, maxlen=24):
    def probe():
        rng = random.Random(seed)
        for _ in range(cases):
            s = gen(rng, rng.randint(0, maxlen))
            got = C_CL(s)
            if got != _orc_clusters(s):
                return False
            if "".join(got) != s:
                return False
        return True
    return probe


def diff_expand(seed, gen, sizes, cases=300, maxlen=20):
    def probe():
        rng = random.Random(seed)
        for _ in range(cases):
            s = gen(rng, rng.randint(0, maxlen))
            ts = rng.choice(sizes)
            if C_ET(s, ts) != _orc_expand(s, ts):
                return False
        return True
    return probe


def diff_wrap(seed, gen, budgets, cases=300, maxlen=26, sizes=(8,)):
    def probe():
        rng = random.Random(seed)
        for _ in range(cases):
            s = gen(rng, rng.randint(0, maxlen))
            b = rng.choice(budgets)
            ts = rng.choice(sizes)
            got = C_WR(s, b, ts)
            want = _orc_wrap(s, b, ts)
            if not isinstance(got, list) or got != want:
                return False
        return True
    return probe


def diff_trunc(seed, gen, budgets, ells, cases=300, maxlen=22):
    def probe():
        rng = random.Random(seed)
        for _ in range(cases):
            s = gen(rng, rng.randint(0, maxlen))
            b = rng.choice(budgets)
            e = rng.choice(ells)
            if C_TR(s, b, e) != _orc_trunc(s, b, e):
                return False
        return True
    return probe


# ----------------------------------------------------------------------
# 1: import ban
# ----------------------------------------------------------------------
def no_banned():
    src = inspect.getsource(dwrap)
    return re.search(r"^\s*(import|from)\s+(textwrap|wcwidth)\b", src, re.M) is None


check("does not import textwrap or wcwidth", no_banned)

# ----------------------------------------------------------------------
# 2-3: char_width
# ----------------------------------------------------------------------
check("char_width: ASCII, wide, fullwidth, halfwidth, ambiguous",
      lambda: [C_CW(c) for c in ["a", " ", "-", chr(0x4E2D), chr(0xFF21),
                                 chr(0x3042), chr(0xFF76), chr(0x2026),
                                 chr(0x00B1), chr(0x00E9)]]
      == [1, 1, 1, 2, 2, 2, 1, 1, 1, 1])
check("char_width: combining marks and zero-width characters",
      lambda: [C_CW(c) for c in [chr(0x0301), chr(0x0308), chr(0x0653),
                                 chr(0x200B), chr(0x200C), chr(0x200D),
                                 chr(0xFEFF)]] == [0] * 7)

# ----------------------------------------------------------------------
# 4-5: width
# ----------------------------------------------------------------------
check("width differential: wide / halfwidth / ambiguous mixes",
      diff_width(1001, _gen_wide))
check("width differential: combining marks and zero-width joiners",
      diff_width(1002, _gen_marks))

# ----------------------------------------------------------------------
# 6-8: clusters
# ----------------------------------------------------------------------
check("clusters differential: combining marks and zero-width",
      diff_clusters(2001, _gen_marks))
check("clusters differential: mixed text",
      diff_clusters(2002, _gen_mixed))


def cluster_edges():
    cases = [
        ("", []),
        ("a", ["a"]),
        ("a" + chr(0x0301), ["a" + chr(0x0301)]),
        (chr(0x0301) + "a", [chr(0x0301), "a"]),
        (chr(0x0301) + chr(0x0308), [chr(0x0301) + chr(0x0308)]),
        ("a" + chr(0x200D) + "b", ["a" + chr(0x200D) + "b"]),
        (chr(0x200D) + "a", [chr(0x200D), "a"]),
        ("a" + chr(0x200D), ["a" + chr(0x200D)]),
        (" " + chr(0x0301) + " ", [" " + chr(0x0301), " "]),
        ("a" + chr(0x200B) + "b", ["a" + chr(0x200B), "b"]),
        ("a" + chr(0x200D) + "b" + chr(0x0301) + "c",
         ["a" + chr(0x200D) + "b" + chr(0x0301), "c"]),
    ]
    for s, want in cases:
        if C_CL(s) != want or want != _orc_clusters(s):
            return False
    return True


check("clusters: hand-checked edge cases (empty, leading mark, ZWJ, space+mark)",
      cluster_edges)

# ----------------------------------------------------------------------
# 9-10: expand_tabs
# ----------------------------------------------------------------------
check("expand_tabs differential: ASCII text, tabsize 1..8",
      diff_expand(3001, _gen_tabs, [1, 2, 3, 4, 8]))
check("expand_tabs differential: wide characters shift the tab stop",
      diff_expand(3002, _gen_mixed, [2, 4, 5, 8, 16]))

# ----------------------------------------------------------------------
# 11-22: wrap
# ----------------------------------------------------------------------
check("wrap differential: ASCII words, budgets 3-12 (A)",
      diff_wrap(4001, _gen_ascii, [3, 4, 5, 6, 8, 10, 12]))
check("wrap differential: ASCII words, budgets 2-7 (B)",
      diff_wrap(4002, _gen_ascii, [2, 3, 4, 5, 6, 7]))
check("wrap differential: runs of spaces preserved verbatim",
      diff_wrap(4003, _gen_spaces, [3, 4, 5, 6, 8, 11]))
check("wrap differential: hyphen break opportunities",
      diff_wrap(4004, _gen_hyphen, [2, 3, 4, 5, 7, 9]))
check("wrap differential: wide characters straddling the budget",
      diff_wrap(4005, _gen_wide, [2, 3, 4, 5, 6, 7, 9]))
check("wrap differential: combining marks and zero-width characters",
      diff_wrap(4006, _gen_marks, [1, 2, 3, 4, 6, 8]))
check("wrap differential: long unbreakable words",
      diff_wrap(4007, _gen_long, [2, 3, 4, 5, 7, 10], cases=300, maxlen=28))
check("wrap differential: budget 1 and 2",
      diff_wrap(4008, _gen_mixed, [1, 2]))
check("wrap differential: multi-line text with blank lines",
      diff_wrap(4009, _gen_lines, [2, 3, 5, 8]))
check("wrap differential: tabs inside the text, tabsize 1..8",
      diff_wrap(4010, _gen_tabs, [3, 4, 6, 9], sizes=(1, 2, 3, 4, 8)))
check("wrap differential: everything mixed (A)",
      diff_wrap(4011, _gen_mixed, [1, 2, 3, 4, 5, 6, 8, 12], sizes=(2, 4, 8)))
check("wrap differential: everything mixed (B)",
      diff_wrap(4012, _gen_mixed, [3, 5, 7, 9, 13], cases=300, maxlen=34,
                sizes=(3, 5, 8)))

# ----------------------------------------------------------------------
# 23-26: truncate
# ----------------------------------------------------------------------
_ELL = [chr(0x2026), "...", "", ">>", chr(0x4E2D), chr(0x2026) + " "]
check("truncate differential: ASCII text",
      diff_trunc(5001, _gen_ascii, [0, 1, 2, 3, 5, 8, 12, 40], _ELL))
check("truncate differential: wide characters",
      diff_trunc(5002, _gen_wide, [0, 1, 2, 3, 4, 5, 6, 9, 30], _ELL))
check("truncate differential: trailing spaces and combining marks",
      diff_trunc(5003, _gen_spaces, [1, 2, 3, 4, 6, 9, 20], _ELL))
check("truncate differential: mixed text, small budgets, odd ellipses",
      diff_trunc(5004, _gen_marks, [0, 1, 2, 3, 4, 5, 7, 11], _ELL))

# ----------------------------------------------------------------------
# 27: argument validation
# ----------------------------------------------------------------------


def raises_ve(fn):
    try:
        fn()
    except ValueError:
        return True
    except Exception:
        return False
    return False


def validation():
    probes = [
        lambda: C_WR("abc", 0),
        lambda: C_WR("abc", -1),
        lambda: C_WR("abc", True),
        lambda: C_WR("abc", 5, 0),
        lambda: C_WR("abc", 5, -3),
        lambda: C_ET("abc", 0),
        lambda: C_ET("abc", -1),
        lambda: C_TR("abc", -1),
        lambda: C_TR("abc", True),
    ]
    for p in probes:
        if not raises_ve(p):
            return False
    # these must NOT raise
    if C_TR("abc", 0) != "":
        return False
    if C_WR("abc", 1) != _orc_wrap("abc", 1):
        return False
    return True


check("ValueError for budget/tabsize out of range or bool", validation)

_t.cancel()
report()
