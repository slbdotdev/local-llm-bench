import sys, os, re, random, threading, inspect, warnings

warnings.simplefilter("ignore")

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
    import sedlite
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

RUN = getattr(sedlite, "run", None)
SERR = getattr(sedlite, "ScriptError", None)


# ======================================================================
#  ORACLE  (independent re-implementation; all names prefixed _ORC_)
# ======================================================================

class _ORC_Err(Exception):
    def __init__(self, kind):
        Exception.__init__(self, kind)
        self.kind = kind


_ORC_D = "/,:#_@%!"
_ORC_OPS = "sydpqai"
_ORC_DIG = "0123456789"


def _ORC_parse(src):
    i = 0
    n = len(src)
    prog = []

    def bad(m):
        raise _ORC_Err(m)

    def skipws():
        nonlocal i
        while i < n and src[i] in " \t":
            i += 1

    def num():
        nonlocal i
        s = i
        while i < n and src[i] in _ORC_DIG:
            i += 1
        return None if s == i else int(src[s:i])

    def section(d):
        nonlocal i
        buf = ""
        while True:
            if i >= n or src[i] == "\n":
                bad("unterminated")
            ch = src[i]
            if ch == "\\":
                if i + 1 >= n or src[i + 1] == "\n":
                    bad("unterminated")
                buf += src[i:i + 2]
                i += 2
                continue
            i += 1
            if ch == d:
                return buf
            buf += ch

    def mkre(raw, d, ic):
        p = ""
        k = 0
        while k < len(raw):
            if raw[k] == "\\" and k + 1 < len(raw):
                p += (d if raw[k + 1] == d else raw[k:k + 2])
                k += 2
            else:
                p += raw[k]
                k += 1
        if p == "":
            bad("bad_regex")
        try:
            return re.compile(p, re.IGNORECASE if ic else 0)
        except re.error:
            bad("bad_regex")

    def plain(raw):
        p = ""
        k = 0
        while k < len(raw):
            if raw[k] == "\\" and k + 1 < len(raw):
                c = raw[k + 1]
                p += "\n" if c == "n" else "\t" if c == "t" else c
                k += 2
            else:
                p += raw[k]
                k += 1
        return p

    def addr(second):
        nonlocal i
        if i >= n:
            return None
        ch = src[i]
        if ch == "+":
            if not second:
                return None
            i += 1
            v = num()
            if v is None:
                bad("bad_address")
            return {"k": "plus", "v": v}
        if ch == "$":
            i += 1
            return {"k": "last"}
        if ch == "/":
            i += 1
            return {"k": "re", "r": mkre(section("/"), "/", False)}
        if ch in _ORC_DIG:
            v = num()
            if (not second) and i < n and src[i] == "~":
                i += 1
                st = num()
                if st is None:
                    bad("bad_address")
                return {"k": "step", "f": v, "s": st}
            if v == 0:
                bad("bad_address")
            return {"k": "num", "v": v}
        return None

    def fin():
        nonlocal i
        skipws()
        if i >= n:
            return
        if src[i] in ";\n":
            i += 1
            return
        bad("trailing_garbage")

    while True:
        while i < n and src[i] in " \t\n;":
            i += 1
        if i >= n:
            break
        if src[i] == "#":
            while i < n and src[i] != "\n":
                i += 1
            continue
        c = {"a1": None, "a2": None, "neg": False}
        c["a1"] = addr(False)
        if c["a1"] is not None:
            skipws()
            if i < n and src[i] == ",":
                i += 1
                skipws()
                c["a2"] = addr(True)
                if c["a2"] is None:
                    bad("bad_address")
        skipws()
        nb = 0
        while i < n and src[i] == "!":
            nb += 1
            i += 1
            skipws()
        if nb > 1:
            bad("bad_bang")
        if nb == 1:
            if c["a1"] is None:
                bad("bad_bang")
            c["neg"] = True
        if i >= n or src[i] not in _ORC_OPS:
            bad("unknown_command")
        op = src[i]
        i += 1
        c["op"] = op
        if op == "q" and c["a2"] is not None:
            bad("extra_address")
        if op in "dpq":
            fin()
        elif op in "ai":
            j = src.find("\n", i)
            if j < 0:
                j = n
            t = src[i:j].lstrip(" \t")
            i = j
            if t == "":
                bad("empty_text")
            c["txt"] = plain(t)
        elif op == "y":
            if i >= n or src[i] not in _ORC_D:
                bad("bad_delimiter")
            d = src[i]
            i += 1
            a = plain(section(d))
            b = plain(section(d))
            if len(a) != len(b):
                bad("bad_y")
            c["map"] = dict(zip(a, b))
            fin()
        else:
            if i >= n or src[i] not in _ORC_D:
                bad("bad_delimiter")
            d = src[i]
            i += 1
            praw = section(d)
            rraw = section(d)
            j = i
            while j < n and src[j].isalnum():
                j += 1
            fs = src[i:j]
            i = j
            gg = ic = pp = False
            nn = None
            k = 0
            while k < len(fs):
                ch = fs[k]
                if ch in _ORC_DIG:
                    if nn is not None:
                        bad("bad_flag")
                    v = 0
                    while k < len(fs) and fs[k] in _ORC_DIG:
                        v = v * 10 + int(fs[k])
                        k += 1
                    if v == 0:
                        bad("bad_flag")
                    nn = v
                    continue
                if ch == "g":
                    if gg:
                        bad("bad_flag")
                    gg = True
                elif ch == "i":
                    if ic:
                        bad("bad_flag")
                    ic = True
                elif ch == "p":
                    if pp:
                        bad("bad_flag")
                    pp = True
                else:
                    bad("bad_flag")
                k += 1
            rx = mkre(praw, d, ic)
            k = 0
            while k < len(rraw):
                if rraw[k] == "\\" and k + 1 < len(rraw):
                    if rraw[k + 1] in "123456789" and int(rraw[k + 1]) > rx.groups:
                        bad("bad_backref")
                    k += 2
                else:
                    k += 1
            c["rx"] = rx
            c["rp"] = rraw
            c["g"] = gg
            c["pf"] = pp
            c["nf"] = 1 if nn is None else nn
            fin()
        prog.append(c)
    return prog


def _ORC_hit(a, ln, ps, isl):
    k = a["k"]
    if k == "num":
        return ln == a["v"]
    if k == "last":
        return isl
    if k == "re":
        return a["r"].search(ps) is not None
    if a["s"] == 0:
        return ln == a["f"]
    return ln >= a["f"] and (ln - a["f"]) % a["s"] == 0


def _ORC_end(a, ln, ps, isl, start):
    k = a["k"]
    if k == "num":
        return ln >= a["v"]
    if k == "last":
        return isl
    if k == "re":
        return a["r"].search(ps) is not None
    return ln >= start + a["v"]


def _ORC_sel(c, s, ln, ps, isl):
    a1 = c["a1"]
    a2 = c["a2"]
    if a1 is None:
        r = True
    elif a2 is None:
        r = _ORC_hit(a1, ln, ps, isl)
    elif s[0]:
        r = True
        if _ORC_end(a2, ln, ps, isl, s[1]):
            s[0] = False
    elif _ORC_hit(a1, ln, ps, isl):
        r = True
        s[1] = ln
        one = (a2["k"] == "num" and a2["v"] <= ln) or (a2["k"] == "plus" and a2["v"] == 0)
        s[0] = not one
    else:
        r = False
    return (not r) if c["neg"] else r


def _ORC_exp(raw, m):
    res = ""
    k = 0
    while k < len(raw):
        ch = raw[k]
        if ch == "&":
            res += m.group(0)
            k += 1
        elif ch == "\\" and k + 1 < len(raw):
            c = raw[k + 1]
            if c in "123456789":
                g = m.group(int(c))
                res += g if g is not None else ""
            elif c == "n":
                res += "\n"
            elif c == "t":
                res += "\t"
            else:
                res += c
            k += 2
        else:
            res += ch
            k += 1
    return res


def _ORC_sub(c, ps):
    ms = list(c["rx"].finditer(ps))
    a = c["nf"] - 1
    if a >= len(ms):
        return ps, False
    picks = ms[a:] if c["g"] else [ms[a]]
    res = ""
    prev = 0
    for m in picks:
        res += ps[prev:m.start()]
        res += _ORC_exp(c["rp"], m)
        prev = m.end()
    res += ps[prev:]
    return res, True


def _ORC_run(script, text, quiet=False):
    prog = _ORC_parse(script)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    state = [[False, 0] for _ in prog]
    out = []
    N = len(lines)
    ln = 0
    stop = False
    while ln < N and not stop:
        ln += 1
        ps = lines[ln - 1]
        pend = []
        killed = False
        for k in range(len(prog)):
            c = prog[k]
            if not _ORC_sel(c, state[k], ln, ps, ln == N):
                continue
            op = c["op"]
            if op == "p":
                out.append(ps)
            elif op == "i":
                out.append(c["txt"])
            elif op == "a":
                pend.append(c["txt"])
            elif op == "y":
                mp = c["map"]
                ps = "".join(mp[z] if z in mp else z for z in ps)
            elif op == "s":
                ps, did = _ORC_sub(c, ps)
                if did and c["pf"]:
                    out.append(ps)
            elif op == "d":
                killed = True
                break
            else:
                stop = True
                break
        if not killed and not quiet:
            out.append(ps)
        out.extend(pend)
    return "".join(z + "\n" for z in out)


# ======================================================================
#  script / text generators
# ======================================================================

LIT = "abcXY -"
TXTCH = "aabbcXY .-"


def g_re(r, d, want_delim=False, depth=0):
    """returns (pattern_text, ngroups)"""
    parts = []
    ng = 0
    k = r.randrange(1, 4)
    if want_delim:
        parts.append("\\" + d)
    for _ in range(k):
        t = r.randrange(12)
        if t < 5:
            at = r.choice(LIT)
            quant = True
        elif t == 5:
            at = "."
            quant = True
        elif t == 6:
            at = r.choice(["[abc]", "[^ab]", "[a-c]", "[bX]"])
            quant = True
        elif t == 7:
            at = "\\" + r.choice(".*[]+?^$\\")
            quant = True
        elif t == 8 and depth == 0:
            inner = "".join(r.choice(LIT) for _ in range(r.randrange(1, 3)))
            if r.random() < 0.4:
                inner += "|" + "".join(r.choice(LIT) for _ in range(r.randrange(1, 3)))
            at = "(" + inner + ")"
            ng += 1
            quant = False
        elif t == 9:
            at = r.choice(LIT) + "|" + r.choice(LIT)
            quant = False
        else:
            at = r.choice(LIT)
            quant = True
        if quant and r.random() < 0.35:
            at += r.choice("*+?")
        parts.append(at)
    s = "".join(parts)
    if r.random() < 0.12:
        s = "^" + s
    if r.random() < 0.12:
        s = s + "$"
    return s, ng


def g_rep(r, d, ng):
    out = []
    for _ in range(r.randrange(0, 4)):
        t = r.randrange(10)
        if t < 4:
            out.append(r.choice("ZQ-_ "))
        elif t == 4:
            out.append("&")
        elif t == 5 and ng:
            out.append("\\%d" % r.randrange(1, ng + 1))
        elif t == 6:
            out.append(r.choice(["\\n", "\\t", "\\\\", "\\&"]))
        elif t == 7:
            out.append("\\" + d)
        else:
            out.append(r.choice("ZQ"))
    return "".join(out)


def g_flags(r, allow):
    fs = []
    if "g" in allow and r.random() < 0.4:
        fs.append("g")
    if "i" in allow and r.random() < 0.25:
        fs.append("i")
    if "p" in allow and r.random() < 0.25:
        fs.append("p")
    if "N" in allow and r.random() < 0.4:
        fs.append(str(r.randrange(1, 4)))
    r.shuffle(fs)
    return "".join(fs)


def g_text(r):
    s = ""
    while s.strip(" \t") == "":
        s = ""
        for _ in range(r.randrange(1, 6)):
            t = r.randrange(10)
            if t < 7:
                s += r.choice("abcXY")
            elif t == 7:
                s += r.choice(["\\n", "\\t", "\\\\"])
            else:
                s += r.choice("; #")
    return s


def g_addr(r, kinds, second):
    k = r.choice(kinds)
    if k == "num":
        return str(r.randrange(1, 6))
    if k == "last":
        return "$"
    if k == "re":
        return "/" + g_re(r, "/")[0] + "/"
    if k == "step":
        return "%d~%d" % (r.randrange(0, 4), r.randrange(0, 4))
    return "+" + str(r.randrange(0, 3))


def g_cmd(r, cfg):
    op = r.choice(cfg["ops"])
    ad = ""
    mode = r.choice(cfg["amodes"])
    if op == "q" and mode == "range":
        mode = "one"
    if mode == "one":
        ad = g_addr(r, cfg["a1"], False)
    elif mode == "range":
        ad = g_addr(r, cfg["a1"], False) + "," + g_addr(r, cfg["a2"], True)
    if ad and r.random() < cfg.get("neg", 0.0):
        ad += "!"
    if ad and r.random() < 0.15:
        ad += " "
    if op == "d":
        body = "d"
    elif op == "p":
        body = "p"
    elif op == "q":
        body = "q"
    elif op in "ai":
        body = op + (" " if r.random() < 0.8 else "") + g_text(r)
    elif op == "y":
        d = r.choice(cfg["delims"])
        n = r.randrange(0, 4)
        src = "".join(r.choice("abcXY") for _ in range(n))
        dst = "".join(r.choice("ZQ-.") for _ in range(n))
        if r.random() < 0.2 and n:
            src = src[:-1] + "\\" + d
            dst = dst[:-1] + "\\n"
        body = "y" + d + src + d + dst + d
    else:
        d = r.choice(cfg["delims"])
        pat, ng = g_re(r, d, want_delim=(d != "/" and r.random() < 0.25))
        body = "s" + d + pat + d + g_rep(r, d, ng) + d + g_flags(r, cfg["flags"])
    return ad + body, op


def g_script(r, cfg):
    n = r.randrange(cfg["nlo"], cfg["nhi"] + 1)
    outp = []
    for _ in range(n):
        c, op = g_cmd(r, cfg)
        outp.append((c, op))
    s = ""
    for idx, (c, op) in enumerate(outp):
        if idx:
            if op == "?" or outp[idx - 1][1] in "ai":
                s += "\n"
            else:
                s += r.choice([";", "\n", " ; ", ";\n"])
        if cfg.get("noise") and r.random() < 0.3:
            s += r.choice(["", " ", "  ", "\n", ";", "# note\n", "\n\n", "\t"])
        s += c
    if cfg.get("noise") and r.random() < 0.3:
        s += r.choice(["", ";", "\n", "\n# end", " "])
    return s


def g_text_input(r):
    n = r.randrange(0, 7)
    ls = []
    for _ in range(n):
        ls.append("".join(r.choice(TXTCH) for _ in range(r.randrange(0, 9))))
    body = "\n".join(ls)
    if n and r.random() < 0.8:
        body += "\n"
    return body


# ======================================================================
#  differential driver
# ======================================================================


def _cand(script, text, quiet):
    try:
        v = RUN(script, text, quiet)
    except Exception as e:
        if isinstance(SERR, type) and isinstance(e, SERR):
            return ("err", getattr(e, "kind", "<no .kind>"))
        return ("boom", type(e).__name__)
    if type(v) is not str:
        return ("boom", "non-str")
    return ("ok", v)


def _orc(script, text, quiet):
    try:
        return ("ok", _ORC_run(script, text, quiet))
    except _ORC_Err as e:
        return ("err", e.kind)


def bucket(seed, cfg, ncases):
    """Semantics only: scripts the spec rejects are skipped here."""
    def go():
        r = random.Random(seed)
        for _ in range(ncases):
            sc = g_script(r, cfg)
            tx = g_text_input(r)
            q = r.random() < 0.3
            want = _orc(sc, tx, q)
            if want[0] == "err":
                continue
            if _cand(sc, tx, q) != want:
                return False
        return True
    return go


BASE = {"ops": ["s"], "amodes": ["none"], "a1": ["num"], "a2": ["num"],
        "delims": "/", "flags": "gip", "nlo": 1, "nhi": 1, "neg": 0.0}


def C(**kw):
    d = dict(BASE)
    d.update(kw)
    return d


MIX = dict(ops=["s", "y", "d", "p", "q", "a", "i"],
           amodes=["none", "one", "one", "range", "range"],
           a1=["num", "last", "re", "step"], a2=["num", "last", "re", "plus"],
           delims="/,:#_@%!", flags="gipN", neg=0.25, nlo=1, nhi=4, noise=True)


def kind_of(script):
    try:
        RUN(script, "aXb\nbc\nc a\n", False)
    except Exception as e:
        if isinstance(SERR, type) and isinstance(e, SERR):
            return getattr(e, "kind", "<no .kind>")
        return "<%s>" % type(e).__name__
    return "<no raise>"


def kinds(pairs):
    def go():
        for sc, want in pairs:
            if kind_of(sc) != want:
                return False
        return True
    return go


# ---------------------------------------------------------------- 1-3

try:
    SRC = inspect.getsource(sedlite)
except Exception:
    SRC = ""
_NC = re.sub(r"(?m)#.*$", "", SRC)

check("ScriptError subclasses ValueError and carries .kind",
      lambda: isinstance(SERR, type) and issubclass(SERR, ValueError)
      and kind_of("x") == "unknown_command"
      and kind_of("s/a/b/z") == "bad_flag")
check("ban: no re.sub / re.subn / Match.expand",
      lambda: SRC != "" and re.search(r"\.\s*subn?\s*\(", _NC) is None
      and re.search(r"\.\s*expand\s*\(", _NC) is None)
check("ban: no str.translate / str.maketrans",
      lambda: SRC != "" and re.search(r"translate|maketrans", _NC) is None)

# ---------------------------------------------------------------- 4

check("canonical output form",
      lambda: type(RUN("", "a\n")) is str
      and RUN("", "") == "" and RUN("d", "a\nb\n") == ""
      and RUN("p", "", True) == "" and RUN("", "a\nb\n", True) == ""
      and RUN("s/a/X/", "a") == "X\n" and RUN("", "a\n\n") == "a\n\n"
      and RUN("", "\n") == "\n" and RUN("1i x", "a\n", True) == "x\n"
      and RUN("a y", "a\n", True) == "y\n"
      and RUN("s/a/1\\n2/", "a\n") == "1\n2\n"
      and RUN("d;p", "a\n") == "" and RUN("q", "a\nb\n") == "a\n")

# ---------------------------------------------------------------- 5-8

check("error kinds: addresses", kinds([
    ("1,p", "bad_address"), ("0p", "bad_address"), ("3~p", "bad_address"),
    ("1,+p", "bad_address"), ("1,0p", "bad_address"), ("/a/,p", "bad_address"),
    ("0,2p", "bad_address"), ("/ap", "unterminated"), ("1,/ap", "unterminated"),
    ("/a\\", "unterminated"), ("//p", "bad_regex"), ("/(/p", "bad_regex"),
    ("1,//p", "bad_regex"), ("/a[/p", "bad_regex")]))
check("error kinds: command letter, ! and extra address", kinds([
    ("!p", "bad_bang"), ("1!!p", "bad_bang"), ("1! !p", "bad_bang"),
    ("!!p", "bad_bang"), ("x", "unknown_command"), ("1", "unknown_command"),
    ("1,2", "unknown_command"), ("+1p", "unknown_command"),
    ("1,2~3p", "unknown_command"), ("", "<no raise>"), ("1 P", "unknown_command"),
    ("1,2q", "extra_address"), ("/a/,/b/q", "extra_address"),
    ("1,+2 q", "extra_address"), ("$,$!q", "extra_address")]))
check("error kinds: s command", kinds([
    ("s*a*b*", "bad_delimiter"), ("s", "bad_delimiter"), ("1s", "bad_delimiter"),
    ("s a b ", "bad_delimiter"), ("s/a/b", "unterminated"), ("s/a", "unterminated"),
    ("s,a,b", "unterminated"), ("s/a/b/x", "bad_flag"), ("s/a/b/gg", "bad_flag"),
    ("s/a/b/0", "bad_flag"), ("s/a/b/1g2", "bad_flag"), ("s/a/b/pp", "bad_flag"),
    ("s//x/", "bad_regex"), ("s/(/x/", "bad_regex"), ("s/a[b/x/", "bad_regex"),
    ("s/(a)/\\2/", "bad_backref"), ("s/a/\\1/", "bad_backref"),
    ("s/(a)(b)/\\5/", "bad_backref"), ("s/a/b/ p", "trailing_garbage"),
    ("s/a/b/g x", "trailing_garbage")]))
check("error kinds: y, a/i, trailing garbage", kinds([
    ("y/ab/c/", "bad_y"), ("y/a/bc/", "bad_y"), ("y/ab/cd", "unterminated"),
    ("y*ab*cd*", "bad_delimiter"), ("y", "bad_delimiter"),
    ("y/a\\nb/xy/", "bad_y"), ("a", "empty_text"), ("i  ", "empty_text"),
    ("1a", "empty_text"), ("1,2i\t", "empty_text"), ("p x", "trailing_garbage"),
    ("d 1", "trailing_garbage"), ("q z", "trailing_garbage"),
    ("y/ab/cd/ z", "trailing_garbage"), ("q;x", "unknown_command"),
    ("p;;d;", "<no raise>")]))

# ---------------------------------------------------------------- 9-10

check("error precedence on doubly-malformed scripts", kinds([
    ("1,x", "bad_address"), ("1,2!!q", "bad_bang"), ("!s*a*b*", "bad_bang"),
    ("1,2x", "unknown_command"), ("1,2q x", "extra_address"),
    ("1,2q;s/a/b/z", "extra_address"), ("s*a*b/x/", "bad_delimiter"),
    ("s*a*b", "bad_delimiter"), ("s/(/x/z/", "bad_flag"),
    ("s/(/x/gg", "bad_flag"), ("s/(/\\1/", "bad_regex"),
    ("s/(a)/\\3/ x", "bad_backref"), ("y/ab/c/ x", "bad_y"),
    ("y*ab*c*", "bad_delimiter"), ("s/a/b/x;q q", "bad_flag"),
    ("p x;!d", "trailing_garbage"), ("1,2 !!p", "bad_bang"),
    ("/a/,+q", "bad_address"), ("1a x;s/a/b/z", "<no raise>")]))


def _strict():
    for sc, k in [("s/(a)(b)/\\5/", "bad_backref"), ("s/a/b/G", "bad_flag"),
                  ("s/a/b/00", "bad_flag"), ("s/a/b/2 3", "trailing_garbage"),
                  ("1,2q", "extra_address"), ("y/abc/xy/", "bad_y"),
                  ("d x", "trailing_garbage"), ("s/a/b/1g1", "bad_flag"),
                  ("i\\", "<no raise>")]:
        if kind_of(sc) != k:
            return False
    return (RUN("2~0p", "a\nb\nc\n", True) == "b\n"
            and RUN("0~3p", "1\n2\n3\n4\n5\n6\n7\n", True) == "3\n6\n"
            and RUN("   \n# c\n;;", "a\nb\n") == "a\nb\n"
            and RUN("2,1p", "a\nb\nc\n", True) == "b\n"
            and RUN("/b/,+0p", "a\nb\nc\nb\n", True) == "b\nb\n")


check("strict rejections a lax parser would accept", _strict)

# ---------------------------------------------------------------- 11-12


def mutants(seed, ncases, ops):
    def go():
        r = random.Random(seed)
        cfg = C(**MIX)
        for _ in range(ncases):
            sc = g_script(r, cfg)
            tx = g_text_input(r)
            for _ in range(r.randrange(1, 3)):
                if not sc:
                    break
                k = r.randrange(len(sc))
                m = r.choice(ops)
                if m == 0:
                    sc = sc[:k]
                elif m == 1:
                    sc = sc[:k] + r.choice("!,~+*/0[()\\ zP") + sc[k:]
                elif m == 2:
                    sc = sc[:k] + sc[k + 1:]
                else:
                    sc = sc[:k] + r.choice(["q", "!", ",", "s/a", "//", "\\5",
                                            "y/ab/c/", "0", " x", "~"]) + sc[k:]
            if _cand(sc, tx, False) != _orc(sc, tx, False):
                return False
        return True
    return go


check("randomized malformed scripts: kind agrees (A)", mutants(41, 500, [0, 1, 2]))
check("randomized malformed scripts: kind agrees (B)", mutants(42, 500, [1, 2, 3]))

# ---------------------------------------------------------------- 13-30

check("api basics",
      lambda: RUN("", "a\nb\n") == "a\nb\n" and RUN("p", "a", True) == "a\n"
      and RUN("s/a/X/", "abca\nxyz\n") == "Xbca\nxyz\n"
      and RUN("2d", "one\ntwo\nthree\n") == "one\nthree\n"
      and RUN("1a hello", "x\ny\n") == "x\nhello\ny\n"
      and RUN("s,o,0,g", "foo boo\n") == "f00 b00\n")

check("s: g and numeric flags", bucket(
    12, C(ops=["s"], flags="gN", nlo=1, nhi=2), 250))
check("s: i and p flags", bucket(
    13, C(ops=["s"], flags="gipN", nlo=1, nhi=2), 250))
check("s: replacement escapes", bucket(
    14, C(ops=["s"], flags="gN", nlo=1, nhi=3), 250))
check("s/y: alternate delimiters", bucket(
    15, C(ops=["s", "y"], delims="/,:#_@%!", flags="gipN", nlo=1, nhi=3), 250))
check("y: transliteration", bucket(
    16, C(ops=["y"], delims="/,:@", nlo=1, nhi=3), 200))
check("a/i: queued and immediate text", bucket(
    17, C(ops=["a", "i"], amodes=["none", "one"], a1=["num", "last", "re"],
          nlo=1, nhi=3), 200))
check("d: cycle end and auto-print", bucket(
    18, C(ops=["d", "s", "a"], amodes=["none", "one"], a1=["num", "re"],
          flags="g", nlo=1, nhi=3), 250))
check("p and quiet mode", bucket(
    19, C(ops=["p", "s"], amodes=["none", "one"], a1=["num", "last", "re"],
          flags="gp", nlo=1, nhi=3), 250))
check("q: quit interactions", bucket(
    20, C(ops=["q", "a", "p", "s"], amodes=["none", "one"], a1=["num", "last", "re"],
          flags="gp", nlo=1, nhi=4), 250))
check("addresses: numeric, $ and first~step", bucket(
    21, C(ops=["p", "d", "s"], amodes=["one"], a1=["num", "last", "step"],
          flags="g", nlo=1, nhi=3), 250))
check("addresses: regex", bucket(
    22, C(ops=["p", "d", "s", "y"], amodes=["one"], a1=["re"], flags="g",
          delims="/,", nlo=1, nhi=3), 250))
check("ranges: numeric endpoints", bucket(
    24, C(ops=["p", "s", "d"], amodes=["range"], a1=["num", "last", "step"],
          a2=["num", "last"], flags="g", nlo=1, nhi=3), 250))
check("ranges: regex and +N endpoints", bucket(
    25, C(ops=["p", "s", "d", "a"], amodes=["range"], a1=["re", "num", "step"],
          a2=["re", "num", "plus"], flags="g", nlo=1, nhi=3), 300))
check("ranges and negation with !", bucket(
    27, C(ops=["p", "s", "d", "a", "i", "q"], amodes=["one", "range"],
          a1=["num", "re", "step", "last"], a2=["num", "re", "last", "plus"],
          flags="gp", neg=0.6, nlo=1, nhi=3), 300))
check("mixed scripts A", bucket(31, C(**MIX), 300))
check("mixed scripts B (longer, noisy)", bucket(
    34, C(**dict(MIX, nlo=3, nhi=6)), 300))


def _stress():
    r = random.Random(51)
    cfg = C(**dict(MIX, nlo=4, nhi=8))
    for _ in range(250):
        sc = g_script(r, cfg)
        n = r.randrange(6, 13)
        tx = "\n".join("".join(r.choice(TXTCH) for _ in range(r.randrange(0, 11)))
                       for _ in range(n))
        if r.random() < 0.7:
            tx += "\n"
        q = r.random() < 0.4
        want = _orc(sc, tx, q)
        if want[0] == "err":
            continue
        if _cand(sc, tx, q) != want:
            return False
    return True


check("stress: long scripts on long inputs", _stress)

report()
