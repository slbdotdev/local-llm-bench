import sys, os, re, random, threading, inspect

TOTAL = 30
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
    import gitattr
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

sys.setrecursionlimit(20000)

AE = getattr(gitattr, "AttrError", None)
_COMPILE = getattr(gitattr, "compile_attrs", None)
_CHECK = getattr(gitattr, "check_attrs", None)


def C(lines):
    return _COMPILE(list(lines))


def K(path, lines):
    return _CHECK(path, C(lines))


def kind(lines):
    """The candidate's AttrError .kind for these lines, or None if it does not raise.

    Anything other than an AttrError carrying a str .kind yields a marker string that
    can never equal an expected kind."""
    if not (isinstance(AE, type) and issubclass(AE, BaseException)):
        return "<no AttrError class>"
    try:
        _COMPILE(list(lines))
    except AE as e:
        k = getattr(e, "kind", None)
        return k if isinstance(k, str) else "<no .kind>"
    except Exception as e:
        return "<%s>" % type(e).__name__
    return None


def kinds(pairs):
    """pairs: list of (lines, expected kind or None)."""
    def probe():
        for ls, want in pairs:
            if kind(ls) != want:
                return False
        return True
    return probe


# =====================================================================
# Oracle: an independent reference implementation (prefix _ORC_)
# =====================================================================

class _ORC_Err(Exception):
    def __init__(self, kind):
        Exception.__init__(self, kind)
        self.kind = kind


def _ORC_posix(nm):
    if nm == "alpha":
        return lambda c: ("a" <= c <= "z") or ("A" <= c <= "Z")
    if nm == "digit":
        return lambda c: "0" <= c <= "9"
    if nm == "alnum":
        return lambda c: (("a" <= c <= "z") or ("A" <= c <= "Z")
                          or ("0" <= c <= "9"))
    if nm == "space":
        return lambda c: c in " \t\n\v\f\r"
    if nm == "upper":
        return lambda c: "A" <= c <= "Z"
    if nm == "lower":
        return lambda c: "a" <= c <= "z"
    if nm == "punct":
        return lambda c: (33 <= ord(c) <= 47 or 58 <= ord(c) <= 64
                          or 91 <= ord(c) <= 96 or 123 <= ord(c) <= 126)
    if nm == "xdigit":
        return lambda c: ("0" <= c <= "9") or ("a" <= c <= "f") or ("A" <= c <= "F")
    raise _ORC_Err("bad_posix_class")


def _ORC_class(seg, p):
    L = len(seg)
    p += 1
    neg = 0
    if p < L and (seg[p] == "!" or seg[p] == "^"):
        neg = 1
        p += 1
    preds = []
    started = 0
    while 1:
        if p >= L:
            raise _ORC_Err("unterminated_class")
        if seg[p] == "]" and started:
            p += 1
            break
        started = 1
        if seg[p] == "[" and p + 1 < L and seg[p + 1] == ":":
            q = seg.find(":]", p + 2)
            if q == -1:
                raise _ORC_Err("bad_posix_class")
            preds.append(_ORC_posix(seg[p + 2:q]))
            p = q + 2
            continue
        if seg[p] == "\\":
            if p + 1 >= L:
                raise _ORC_Err("trailing_backslash")
            lo = seg[p + 1]
            p += 2
        else:
            lo = seg[p]
            p += 1
        if p + 1 < L and seg[p] == "-" and seg[p + 1] != "]":
            p += 1
            if seg[p] == "\\":
                if p + 1 >= L:
                    raise _ORC_Err("trailing_backslash")
                hi = seg[p + 1]
                p += 2
            else:
                hi = seg[p]
                p += 1
            preds.append((lambda a, b: (lambda c: a <= c <= b))(lo, hi))
        else:
            preds.append((lambda a: (lambda c: c == a))(lo))

    def pred(ch, _ps=preds, _n=neg):
        r = 0
        for f in _ps:
            if f(ch):
                r = 1
                break
        return (not r) if _n else bool(r)

    return p, pred


def _ORC_scan_seg(seg):
    p = 0
    L = len(seg)
    while p < L:
        c = seg[p]
        if c == "\\":
            if p + 1 >= L:
                raise _ORC_Err("trailing_backslash")
            p += 2
        elif c == "[":
            p, _ = _ORC_class(seg, p)
        else:
            p += 1


def _ORC_match_seg(seg, p, comp, q):
    L = len(seg)
    M = len(comp)
    if p >= L:
        return q >= M
    c = seg[p]
    if c == "*":
        while p < L and seg[p] == "*":
            p += 1
        for k in range(q, M + 1):
            if _ORC_match_seg(seg, p, comp, k):
                return True
        return False
    if q >= M:
        return False
    if c == "?":
        return _ORC_match_seg(seg, p + 1, comp, q + 1)
    if c == "\\":
        return seg[p + 1] == comp[q] and _ORC_match_seg(seg, p + 2, comp, q + 1)
    if c == "[":
        e, pred = _ORC_class(seg, p)
        return pred(comp[q]) and _ORC_match_seg(seg, e, comp, q + 1)
    return c == comp[q] and _ORC_match_seg(seg, p + 1, comp, q + 1)


def _ORC_match_segs(segs, i, comps, j):
    if i >= len(segs):
        return j >= len(comps)
    s = segs[i]
    if s == "**":
        for k in range(j, len(comps) + 1):
            if _ORC_match_segs(segs, i + 1, comps, k):
                return True
        return False
    if j >= len(comps) or s == "":
        return False
    if not _ORC_match_seg(s, 0, comps[j], 0):
        return False
    return _ORC_match_segs(segs, i + 1, comps, j + 1)


def _ORC_cut(text):
    out = []
    buf = ""
    p = 0
    while p < len(text):
        if text[p] == "\\" and p + 1 < len(text):
            buf += text[p:p + 2]
            p += 2
            continue
        if text[p] == "\\":
            buf += "\\"
            p += 1
            continue
        if text[p] == "/":
            out.append(buf)
            buf = ""
            p += 1
            continue
        buf += text[p]
        p += 1
    out.append(buf)
    return out


def _ORC_pattern(pat):
    if not pat:
        raise _ORC_Err("empty_pattern")
    segs0 = _ORC_cut(pat)
    if segs0[-1] == "" and len(segs0) > 1:
        raise _ORC_Err("trailing_slash")
    if pat[0] == "/":
        anch = True
        k = 0
        while k < len(pat) and pat[k] == "/":
            k += 1
        pat = pat[k:]
        if not pat:
            raise _ORC_Err("empty_pattern")
        segs = _ORC_cut(pat)
    else:
        segs = segs0
        anch = len(segs) > 1
    for s in segs:
        if s != "" and s != "**":
            _ORC_scan_seg(s)
    return (anch, segs)


def _ORC_match(pobj, comps):
    anch, segs = pobj
    if anch:
        return _ORC_match_segs(segs, 0, comps, 0)
    s = segs[0]
    if s == "**":
        return True
    return _ORC_match_seg(s, 0, comps[-1], 0)


_ORC_OK1 = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
_ORC_OK2 = _ORC_OK1 + "0123456789-."


def _ORC_name_ok(s):
    return bool(s) and s[0] in _ORC_OK1 and all(ch in _ORC_OK2 for ch in s[1:])


def _ORC_spec(f):
    if f[0] == "-" or f[0] == "!":
        nm = f[1:]
        if "=" in nm or not _ORC_name_ok(nm):
            raise _ORC_Err("bad_attr_name")
        return (nm, False if f[0] == "-" else None)
    if "=" in f:
        nm, _, v = f.partition("=")
        if not _ORC_name_ok(nm):
            raise _ORC_Err("bad_attr_name")
        return (nm, v)
    if not _ORC_name_ok(f):
        raise _ORC_Err("bad_attr_name")
    return (f, True)


def _ORC_head(line):
    p = 0
    while p < len(line):
        if line[p] == "\\":
            p += 2
            continue
        if line[p] == " " or line[p] == "\t":
            break
        p += 1
    p = min(p, len(line))
    return line[:p], line[p:].split()


def _ORC_rstrip(line):
    p = len(line)
    while p and line[p - 1] in " \t":
        nb = 0
        r = p - 2
        while r >= 0 and line[r] == "\\":
            nb += 1
            r -= 1
        if nb % 2:
            break
        p -= 1
    return line[:p]


def _ORC_compile(lines):
    macs = {}
    rules = []
    for ln in lines:
        ln = _ORC_rstrip(ln)
        if not ln or ln[0] == "#":
            continue
        if ln[:6] == "[attr]":
            hd, fs = _ORC_head(ln[6:])
            if not _ORC_name_ok(hd):
                raise _ORC_Err("bad_macro_name")
            if not fs:
                raise _ORC_Err("no_attrs")
            if hd in macs:
                raise _ORC_Err("duplicate_macro")
            macs[hd] = [_ORC_spec(f) for f in fs]
            continue
        hd, fs = _ORC_head(ln)
        if not hd:
            raise _ORC_Err("empty_pattern")
        po = _ORC_pattern(hd)
        if not fs:
            raise _ORC_Err("no_attrs")
        rules.append((po, [_ORC_spec(f) for f in fs]))
    seen = set()
    stack = set()

    def go(m):
        if m in stack:
            raise _ORC_Err("macro_cycle")
        if m in seen:
            return
        stack.add(m)
        for (n2, _v) in macs[m]:
            if n2 in macs:
                go(n2)
        stack.discard(m)
        seen.add(m)

    for m in sorted(macs):
        go(m)
    return (rules, macs)


def _ORC_check(path, comp):
    rules, macs = comp
    comps = path.split("/")
    out = {}

    def put(sp):
        for (nm, v) in sp:
            out[nm] = v
            if v is True and nm in macs:
                put(macs[nm])

    for (po, sp) in rules:
        if _ORC_match(po, comps):
            put(sp)
    return out


def _ORC_kind(lines):
    """None if valid, else the .kind string the candidate must produce."""
    try:
        _ORC_compile(list(lines))
    except _ORC_Err as e:
        return e.kind
    return None


# =====================================================================
# Random generators (bounded)
# =====================================================================

_PLAIN = "abz09.-_"
_SPECIAL = " #*?[]!^\\+:AZ"
_PCH = "abz09.-_+:"
_ESCAPABLE = " *?[]\\#!^/-.a"
_POSIXN = ["alpha", "digit", "alnum", "space", "upper", "lower", "punct", "xdigit"]
_NAMES = ["text", "diff", "eol", "a", "b_c", "m1", "m2", "m3", "x.y", "z-w", "_q"]
_MACS = ["mac1", "mac2", "mac3", "bin", "doc"]


def _g_class(r, bad=False):
    out = "["
    if r.random() < 0.35:
        out += r.choice("!^")
    n = r.randint(1, 3)
    for i in range(n):
        k = r.random()
        if i == 0 and k < 0.12:
            out += "]"
        elif k < 0.30:
            out += r.choice(_PCH) + "-" + r.choice(_PCH)
        elif k < 0.44:
            out += "[:" + r.choice(_POSIXN) + ":]"
        elif k < 0.52:
            out += "\\" + r.choice(_ESCAPABLE)
        elif k < 0.58:
            out += "-"
        else:
            out += r.choice(_PCH)
    if bad and r.random() < 0.45:
        return out
    if bad and r.random() < 0.15:
        return "[" + r.choice(["[:word:]", "[:Alpha:]", "[:alph:]", "[:abc]"]) + "]"
    return out + "]"


def _g_seg(r, bad=False, cls=False):
    if r.random() < 0.14:
        return "**"
    out = ""
    for _ in range(r.randint(1, 3)):
        k = r.random()
        if cls and k < 0.62:
            out += _g_class(r, bad)
        elif k < 0.34:
            out += r.choice(_PLAIN)
        elif k < 0.52:
            out += "*"
        elif k < 0.57:
            out += "**"
        elif k < 0.67:
            out += "?"
        elif k < 0.86:
            out += _g_class(r, bad)
        elif k < 0.94:
            out += "\\" + r.choice(_ESCAPABLE)
        else:
            out += r.choice(_PLAIN)
    if bad and r.random() < 0.08:
        out += "\\"
    return out


def _g_pattern(r, bad=False, cls=False):
    p = "/" if r.random() < 0.25 else ""
    nseg = 1 if r.random() < 0.55 else r.randint(2, 3)
    segs = [_g_seg(r, bad, cls) for _ in range(nseg)]
    if bad and r.random() < 0.08:
        segs.insert(r.randrange(len(segs) + 1), "")
    p += "/".join(segs)
    if bad and r.random() < 0.10:
        p += "/"
    return p


def _g_field(r, names, bad=False):
    if bad and r.random() < 0.07:
        return r.choice(["-", "!", "=v", "9x", "-a=b", "!a=b", ".x", "a!b", "a/b"])
    nm = r.choice(names)
    k = r.random()
    if k < 0.42:
        return nm
    if k < 0.60:
        return "-" + nm
    if k < 0.74:
        return "!" + nm
    return nm + "=" + r.choice(["", "v1", "hex", "a=b", "0"])


def _g_lines(r, bad=False, macro=False, cls=False):
    names = r.sample(_NAMES, r.randint(2, 5))
    macs = r.sample(_MACS, r.randint(1, 3))
    pmac = 0.55 if macro else 0.30
    lines = []
    used = set()
    for _ in range(r.randint(2, 8)):
        k = r.random()
        if k < 0.04:
            lines.append("")
            continue
        if k < 0.07:
            lines.append("   " if r.random() < 0.5 else "\t")
            continue
        if k < 0.11:
            lines.append("# " + r.choice(["comment", "*.c text"]))
            continue
        if k < pmac and macs:
            i = r.randrange(len(macs))
            nm = macs[i]
            if nm in used and not bad:
                continue
            used.add(nm)
            pool = names + (macs if bad else macs[:i])
            body = " ".join(_g_field(r, pool, bad) for _ in range(r.randint(1, 3)))
            lines.append("[attr]" + nm + " " + body)
            continue
        pat = _g_pattern(r, bad, cls)
        fields = [_g_field(r, names + macs, bad) for _ in range(r.randint(1, 3))]
        line = pat + " " + " ".join(fields)
        if r.random() < 0.10:
            line += "  "
        if r.random() < 0.05:
            line += "\\ "
        if bad and r.random() < 0.05:
            line = " " + line
        lines.append(line)
    return lines


def _g_path(r):
    comps = []
    for _ in range(r.randint(1, 3)):
        c = ""
        for _ in range(r.randint(1, 3)):
            c += r.choice(_PLAIN if r.random() < 0.78 else _SPECIAL)
        comps.append(c)
    return "/".join(comps)


def diff_bucket(seed, n, bad=False, macro=False, cls=False, paths=5):
    """Return a zero-arg callable comparing the candidate with the oracle."""
    def run():
        r = random.Random(seed)
        for _ in range(n):
            lines = _g_lines(r, bad, macro, cls)
            want = _ORC_kind(lines)
            if want is not None:
                if kind(lines) != want:
                    return False
                continue
            if kind(lines) is not None:
                return False
            comp = C(lines)
            oc = _ORC_compile(lines)
            for _p in range(paths):
                path = _g_path(r)
                try:
                    got = _CHECK(path, comp)
                except Exception:
                    return False
                exp = _ORC_check(path, oc)
                if got != exp or sorted(got) != sorted(exp):
                    return False
        return True
    return run




# =====================================================================
# 1-4: API surface and the forbidden imports / shortcuts
# =====================================================================
check("AttrError subclasses ValueError and carries a str .kind",
      lambda: isinstance(AE, type) and issubclass(AE, ValueError)
      and callable(_COMPILE) and callable(_CHECK)
      and kind(["[ x"]) == "unterminated_class")

check("does not import re/fnmatch",
      lambda: not re.search(r"^[ \t]*(?:import|from)[ \t]+(?:re|fnmatch)\b",
                            inspect.getsource(gitattr), re.M))

check("does not import glob/pathlib/os/string",
      lambda: not re.search(
          r"^[ \t]*(?:import|from)[ \t]+(?:glob|pathlib|os|os\.path|string)\b",
          inspect.getsource(gitattr), re.M))

check("does not use the isalpha/isdigit/... character-class shortcuts",
      lambda: not re.search(
          r"\.is(?:alpha|digit|alnum|upper|lower|space|ascii|printable)[ \t]*\(",
          inspect.getsource(gitattr)))

# =====================================================================
# 5-10: resolution, the returned dict, macros
# =====================================================================
check("visible examples",
      lambda: K("a/b.txt", ["*.txt text", "/doc/*.txt -text diff=plain"]) == {"text": True}
      and K("doc/b.txt", ["*.txt text", "/doc/*.txt -text diff=plain"])
      == {"text": False, "diff": "plain"}
      and K("x.png", ["[attr]bin -diff -text", "*.png bin", "*.png diff=hex"])
      == {"bin": True, "diff": "hex", "text": False}
      and K("a/q/z", ["a/**/z !k", "**/z k=1"]) == {"k": "1"})

check("later lines override PER ATTRIBUTE, not per line",
      lambda: K("x.c", ["* a b=1", "*.c -a"]) == {"a": False, "b": "1"}
      and K("x.c", ["* a b=1 c", "*.c -a", "*.c b=2"])
      == {"a": False, "b": "2", "c": True}
      and K("x.h", ["* a b=1", "*.c -a"]) == {"a": True, "b": "1"}
      and K("x.c", ["*.c a", "* -a"]) == {"a": False}
      and K("x.c", ["* k=", "*.c k=a=b"]) == {"k": "a=b"})

check("dict holds exactly the mentioned names; !name is present as None",
      lambda: K("z", ["* !k"]) == {"k": None}
      and K("z", ["* k", "* !k"]) == {"k": None}
      and K("z", ["* !k", "* k"]) == {"k": True}
      and K("z", ["*.c t"]) == {}
      and K("z", ["# nothing", "", "   "]) == {}
      and K("z", ["* j="]) == {"j": ""})

check("macro expands only when set, at the point of its field",
      lambda: K("z", ["[attr]m -d -t", "* m d=1"]) == {"m": True, "d": "1", "t": False}
      and K("z", ["[attr]m -d -t", "* d=1 m"]) == {"m": True, "d": False, "t": False}
      and K("z", ["[attr]m -d -t", "* m", "* d=1"])
      == {"m": True, "d": "1", "t": False}
      and K("z", ["[attr]m d=9", "* d=1 m d=2"]) == {"m": True, "d": "2"})

check("-m, !m and m=v never expand; the macro name is itself recorded",
      lambda: K("z", ["[attr]m t", "* -m"]) == {"m": False}
      and K("z", ["[attr]m t", "* !m"]) == {"m": None}
      and K("z", ["[attr]m t", "* m=1"]) == {"m": "1"}
      and K("z", ["[attr]m t", "* m -m"]) == {"m": False, "t": True}
      and K("z", ["[attr]m t", "* -m m"]) == {"m": True, "t": True})

check("macros nest to any depth and may be defined after use",
      lambda: K("z", ["* m1", "[attr]m1 m2", "[attr]m2 t=9"])
      == {"m1": True, "m2": True, "t": "9"}
      and K("z", ["[attr]a b -q", "[attr]b c", "[attr]c q", "* a"])
      == {"a": True, "b": True, "c": True, "q": False}
      and K("z", ["[attr]a -b", "[attr]b t", "* a"]) == {"a": True, "b": False}
      and K("z", ["[attr]m t", "*.x m"]) == {})

# =====================================================================
# 11-15: patterns
# =====================================================================
check("anchoring: leading /, embedded /, basename-only otherwise",
      lambda: K("b/c", ["b t"]) == {}
      and K("a/b", ["b t"]) == {"t": True}
      and K("a", ["/a t"]) == {"t": True}
      and K("x/a", ["/a t"]) == {}
      and K("a", ["///a t"]) == {"t": True}
      and K("a/b", ["a/b t"]) == {"t": True}
      and K("x/a/b", ["a/b t"]) == {}
      and K("a/b", ["a//b t"]) == {}
      and K("a/b", [r"a\/b t"]) == {}
      and K(r"a\/b", [r"a\/b t"]) == {})

check("**, * and ? -- three ** positions, and a**b is just a*b",
      lambda: K("a", ["a/** t"]) == {"t": True}
      and K("a/b/c", ["a/** t"]) == {"t": True}
      and K("b/a", ["a/** t"]) == {}
      and K("x", ["**/x t"]) == {"t": True}
      and K("a/b/x", ["**/x t"]) == {"t": True}
      and K("a/b", ["a/**/b t"]) == {"t": True}
      and K("a/x/y/b", ["a/**/b t"]) == {"t": True}
      and K("a/b/c", ["** t"]) == {"t": True}
      and K("a/c", ["/a*c t"]) == {}
      and K("abc", ["/a*c t"]) == {"t": True}
      and K("a/c", ["/a?c t"]) == {}
      and K("axc", ["/a?c t"]) == {"t": True}
      and K("aXb", ["/a**b t"]) == {"t": True}
      and K("a/b", ["/a**b t"]) == {}
      and K("ab", ["/**b t"]) == {"t": True})

check("escapes in patterns and in attribute fields",
      lambda: K("a ", [r"a\  t"]) == {"t": True}
      and K("a", [r"a\  t"]) == {}
      and K("#x", [r"\#x t"]) == {"t": True}
      and K("#x", ["#x t"]) == {}
      and K("a*b", [r"a\*b t"]) == {"t": True}
      and K("axb", [r"a\*b t"]) == {}
      and K("a" + chr(92) + "b", ["a" + chr(92) * 2 + "b t"]) == {"t": True}
      and K("a.c", ["*.c\tt\t-d"]) == {"t": True, "d": False}
      and K("a?b", [r"a\?b t"]) == {"t": True})

check("bracket classes: ] and - edge literals, reversed ranges, ! and ^",
      lambda: K("]x", ["[]-]x t"]) == {"t": True}
      and K("-x", ["[]-]x t"]) == {"t": True}
      and K("ax", ["[]-]x t"]) == {}
      and K("-", ["[a-] t"]) == {"t": True}
      and K("a", ["[a-] t"]) == {"t": True}
      and K("zx", ["[z-a]x t"]) == {}
      and K("Qx", ["[z-aQ]x t"]) == {"t": True}
      and K("-", [r"[\-z] t"]) == {"t": True}
      and K("y", [r"[\-z] t"]) == {}
      and K("]", [r"[\]] t"]) == {"t": True}
      and K("a", ["[^0-9] t"]) == {"t": True}
      and K("5", ["[^0-9] t"]) == {}
      and K("a", ["[!0-9] t"]) == {"t": True}
      and K("5", ["[!0-9] t"]) == {}
      and K("bx", ["[!]a]x t"]) == {"t": True}
      and K("]x", ["[!]a]x t"]) == {}
      and K("^", ["[!^] t"]) == {}
      and K("a", ["[!^] t"]) == {"t": True})


def posix_probe():
    tbl = {
        "alpha": "aZ", "digit": "07", "alnum": "a7", "space": " \t",
        "upper": "AQ", "lower": "aq", "punct": "+:", "xdigit": "fF9",
    }
    no = {
        "alpha": "0+", "digit": "a+", "alnum": "+ ", "space": "a0",
        "upper": "a0", "lower": "A0", "punct": "a0", "xdigit": "gG",
    }
    for nm, yes in tbl.items():
        for ch in yes:
            if K(ch, ["[[:%s:]] t" % nm]) != {"t": True}:
                return False
        for ch in no[nm]:
            if K(ch, ["[[:%s:]] t" % nm]) != {}:
                return False
    if K("q", ["[[:digit:][:lower:]] t"]) != {"t": True}:
        return False
    if K("-", ["[[:alpha:]-z] t"]) != {"t": True}:
        return False
    if K("Q", ["[![:lower:]0-9] t"]) != {"t": True}:
        return False
    if K("q", ["[![:lower:]0-9] t"]) != {}:
        return False
    return True


check("POSIX classes, all eight, mixed with members", posix_probe)

# =====================================================================
# 16-20: error kinds and error precedence
# =====================================================================
check("kind of every pattern error", kinds([
    (["/"], "trailing_slash"),
    (["a/ t"], "trailing_slash"),
    (["a/b/ t"], "trailing_slash"),
    (["// t"], "trailing_slash"),
    ([" * t"], "empty_pattern"),
    (["\t* t"], "empty_pattern"),
    (["a\\"], "trailing_backslash"),
    (["[a\\"], "trailing_backslash"),
    (["[a-\\"], "trailing_backslash"),
    (["["], "unterminated_class"),
    (["[] t"], "unterminated_class"),
    (["[!] t"], "unterminated_class"),
    (["[a- t"], "unterminated_class"),
    (["x[ab t"], "unterminated_class"),
    (["[[:word:]] t"], "bad_posix_class"),
    (["[[:Alpha:]] t"], "bad_posix_class"),
    (["[[:alpha] t"], "bad_posix_class"),
    (["[[: t"], "bad_posix_class"),
]))

check("kind of every attribute-field and macro-header error", kinds([
    (["*.c"], "no_attrs"),
    (["* "], "no_attrs"),
    (["[attr]m"], "no_attrs"),
    (["[attr]m "], "no_attrs"),
    (["* -"], "bad_attr_name"),
    (["* !"], "bad_attr_name"),
    (["* =v"], "bad_attr_name"),
    (["* 9x"], "bad_attr_name"),
    (["* .x"], "bad_attr_name"),
    (["* -a=b"], "bad_attr_name"),
    (["* !a=b"], "bad_attr_name"),
    (["* a/b"], "bad_attr_name"),
    (["* a b\\"], "bad_attr_name"),
    (["[attr]m -a=b"], "bad_attr_name"),
    (["[attr] m t"], "bad_macro_name"),
    (["[attr]9m t"], "bad_macro_name"),
    (["[attr]-m t"], "bad_macro_name"),
    (["[attr]m/x t"], "bad_macro_name"),
]))

check("kind of duplicate macros and cycles; cycles come last", kinds([
    (["[attr]m t", "[attr]m d"], "duplicate_macro"),
    (["[attr]m m"], "macro_cycle"),
    (["[attr]m1 m2", "[attr]m2 m1"], "macro_cycle"),
    (["[attr]m1 -m2", "[attr]m2 !m1"], "macro_cycle"),
    (["[attr]a b", "[attr]b c", "[attr]c a"], "macro_cycle"),
    (["[attr]a b=1", "[attr]b a=2", "* -"], "bad_attr_name"),
    (["[attr]a b", "[attr]b a", "["], "unterminated_class"),
    (["[attr]m t", "[attr]m d", "[attr]m1 m1"], "duplicate_macro"),
]))

check("error precedence inside one line", kinds([
    (["[ -x"], "unterminated_class"),
    (["[ -"], "unterminated_class"),
    (["a/ -"], "trailing_slash"),
    (["[/ t"], "trailing_slash"),
    ([" [ -"], "empty_pattern"),
    (["a" + chr(92) + "[b" + chr(92)], "trailing_backslash"),
    (["[[:zz:] t"], "bad_posix_class"),
    (["[a][ t"], "unterminated_class"),
    (["[attr]9m -"], "bad_macro_name"),
    (["[attr]9m"], "bad_macro_name"),
    (["[attr]m t", "[attr]m -"], "duplicate_macro"),
    (["x/[[:q:]]/[ t"], "bad_posix_class"),
]))

check("the first invalid line in file order decides", kinds([
    (["* t", "[ x", "* -"], "unterminated_class"),
    (["* -", "[ x"], "bad_attr_name"),
    (["# [ x", "* t"], None),
    (["", "  ", "[attr]m t", "a/ t", "* ="], "trailing_slash"),
    (["*.c t", "[attr]m1 m1", "* -"], "bad_attr_name"),
    (["[attr]m t", "* m", "[attr]m d"], "duplicate_macro"),
]))


# =====================================================================
# 21-24: canonical result form and input handling
# =====================================================================
def canon_values():
    r = K("z", ["* s -u !n v=1 e="])
    if type(r) is not dict:
        return False
    if sorted(r) != ["e", "n", "s", "u", "v"]:
        return False
    if r["s"] is not True or r["u"] is not False or r["n"] is not None:
        return False
    if type(r["v"]) is not str or r["v"] != "1" or r["e"] != "":
        return False
    for k2 in r:
        if type(k2) is not str:
            return False
    r2 = K("z", ["[attr]m -u !n", "* m"])
    return (r2["m"] is True and r2["u"] is False and r2["n"] is None
            and type(r2) is dict)


check("canonical values: real True/False/None, str values, plain dict", canon_values)


def canon_keys():
    c = C(["*.c a", "* b=1", "x/y !q"])
    d1 = _CHECK("f.c", c)
    if d1 != {"a": True, "b": "1"}:
        return False
    d1["ZZZ"] = 1
    d1.clear()
    d2 = _CHECK("f.c", c)
    if d2 != {"a": True, "b": "1"} or d2 is d1:
        return False
    if _CHECK("x/y", c) != {"b": "1", "q": None}:
        return False
    if _CHECK("f.c", c) != {"a": True, "b": "1"}:
        return False
    if _CHECK("q.h", c) != {"b": "1"}:
        return False
    return True


check("compiled object is reusable; each call returns a fresh exact dict", canon_keys)


def input_forms():
    src = ["*.c text", "[attr]m -d", "* m"]
    keep = list(src)
    c = _COMPILE(src)
    if src != keep:
        return False
    want = {"text": True, "m": True, "d": False}
    if _CHECK("a.c", c) != want:
        return False
    if _CHECK("a.c", _COMPILE(tuple(src))) != want:
        return False
    if _CHECK("a.c", _COMPILE(iter(src))) != want:
        return False
    if _CHECK("a.c", _COMPILE(x for x in src)) != want:
        return False
    if _CHECK("a.c", _COMPILE([])) != {}:
        return False
    return True


check("accepts any iterable of lines and does not mutate it", input_forms)

check("valid but unusual lines must NOT raise", kinds([
    (["a//b t"], None),
    ([r"a\/ t"], None),
    (["[attr]m1 m2 -m2", "[attr]m2 t"], None),
    (["[attr]m- t"], None),
    (["", "   ", "\t", "# * bad ["], None),
    (["* k="], None),
    (["* a.b-c_d"], None),
    (["[z-a] t"], None),
    (["[]] t"], None),
    ([r"\# t"], None),
    (["* undefinedmacro"], None),
    (["** t"], None),
]))

# =====================================================================
# 25-30: randomized differential against the oracle
# =====================================================================
check("random: mixed files, bucket A", diff_bucket(101, 2200))
check("random: mixed files, bucket B", diff_bucket(202, 2200))
check("random: macro-heavy files", diff_bucket(505, 2200, macro=True))
check("random: class-heavy patterns", diff_bucket(707, 2200, cls=True))
check("random: files containing invalid lines, bucket A",
      diff_bucket(909, 2200, bad=True))
check("random: files containing invalid lines, bucket B",
      diff_bucket(1010, 2200, bad=True, cls=True))

report()
