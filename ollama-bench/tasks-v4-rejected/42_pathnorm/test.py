import sys, os, re, random, threading, inspect
import posixpath as _ora_p
import ntpath as _ora_n

TOTAL = 28
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
    import pathnorm
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

B = chr(92)
SEPS = "/" + B


def _missing(*a, **k):
    raise AttributeError("attribute missing from pathnorm")


NORM = getattr(pathnorm, "normalize", _missing)
REL = getattr(pathnorm, "relative", _missing)
SPL = getattr(pathnorm, "split_root", _missing)
PE = getattr(pathnorm, "PathError", None)


def kind_of(fn):
    if not (isinstance(PE, type) and issubclass(PE, BaseException)):
        return "<no PathError>"
    try:
        fn()
    except PE as e:
        return getattr(e, "kind", "<no .kind>")
    except Exception as e:
        return "<%s>" % type(e).__name__
    return "<no raise>"


# ---------------------------------------------------------------- oracle ---
def _ora_split_root(path, style):
    if style == "posix":
        k = 0
        while k < len(path) and path[k] == "/":
            k += 1
        root = "" if k == 0 else ("//" if k == 2 else "/")
        return (root, path[k:])
    d, r = _ora_n.splitdrive(path)
    return (d.replace("/", B), r)


def _ora_normalize(path, style):
    if style == "posix":
        return _ora_p.normpath(path)
    return _ora_n.normpath(path)


def _ora_comps(path, style):
    """Resolved component list, per the spec (used for classification only)."""
    root, rest = _ora_split_root(path, style)
    seps = "/" if style == "posix" else SEPS
    rooted = bool(rest) and rest[0] in seps
    if style == "posix":
        anchored = root != ""
    else:
        anchored = True if root.startswith(B + B) else rooted
    out = []
    cur = ""
    parts = []
    for ch in rest:
        if ch in seps:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    for c in parts:
        if c == "" or c == ".":
            continue
        if c == "..":
            if out and out[-1] != "..":
                out.pop()
            elif not anchored:
                out.append("..")
            continue
        out.append(c)
    return root, rooted, out


def _ora_class(path, style):
    root, rooted, comps = _ora_comps(path, style)
    if style == "posix":
        return ("absolute" if root else "relative", "")
    if root.startswith(B + B):
        return ("unc", root.lower())
    if root:
        return ("drive-abs" if rooted else "drive-rel", root[0].lower())
    return ("rooted" if rooted else "relative", "")


def _ora_relative(path, start, style):
    if style == "posix":
        return _ora_p.relpath(path, start)
    return _ora_n.relpath(path, start)


# ------------------------------------------------------------- generators --
def _ora_gen_posix(rng):
    n = rng.randint(0, 5)
    comps = [rng.choice(["a", "b", "A", "B", "Ab", "aB", ".", "..", "..",
                         "...", "c" + B, "x1"]) for _ in range(n)]
    lead = rng.choice(["", "", "/", "/", "//", "///", "////"])
    body = ""
    for i, c in enumerate(comps):
        if i:
            body += "/" * rng.randint(1, 3)
        body += c
    if rng.random() < 0.25:
        body += "/" * rng.randint(1, 2)
    return lead + body


def _ora_gen_win(rng, for_rel=False):
    kind = rng.choice(["rel", "rel", "rooted", "drive-abs", "drive-abs",
                       "drive-rel", "unc", "unc"])
    pool = ["a", "b", "A", "B", "Ab", "aB", ".", "..", "..", "x1", "X1"]
    if not for_rel:
        pool = pool + ["...", "c."]
    n = rng.randint(0, 5)
    comps = [rng.choice(pool) for _ in range(n)]

    def S(k=1):
        return "".join(rng.choice(SEPS) for _ in range(k))

    body = ""
    for i, c in enumerate(comps):
        if i:
            body += S(rng.randint(1, 3))
        body += c
    if rng.random() < 0.25:
        body += S(rng.randint(1, 2))
    dl = rng.choice("Cc") if for_rel else rng.choice("CcD")
    if kind == "rel":
        return body
    if kind == "rooted":
        return S() + body
    if kind == "drive-abs":
        return dl + ":" + S() + body
    if kind == "drive-rel":
        return dl + ":" + body
    srv = rng.choice(["srv", "SRV", "s1"])
    sh = rng.choice(["sh", "SH", "d2"])
    tail = (S() + body) if (body or rng.random() < 0.5) else ""
    return S() + S() + srv + S() + sh + tail


def _ora_ok_win(p):
    """True when p is inside the input space described by the prompt."""
    k = 0
    while k < len(p) and p[k] in SEPS:
        k += 1
    if k >= 3:
        return False
    if k == 2:
        j = 2
        while j < len(p) and p[j] not in SEPS:
            j += 1
        if not p[2:j].isalnum() or j >= len(p):
            return False
        m = n = j + 1
        while n < len(p) and p[n] not in SEPS:
            n += 1
        if not p[m:n].isalnum():
            return False
    return True


def _ora_lead_dd(p, style):
    return _ora_comps(p, style)[2][:1] == [".."]


_rng = random.Random(20240242)
P_NORM = [_ora_gen_posix(_rng) for _ in range(600)]
W_NORM = []
while len(W_NORM) < 600:
    _c = _ora_gen_win(_rng)
    if _ora_ok_win(_c):
        W_NORM.append(_c)

P_REL = []
while len(P_REL) < 360:
    _a, _b = _ora_gen_posix(_rng), _ora_gen_posix(_rng)
    if not _a or not _b:
        continue
    if _a.startswith("/") != _b.startswith("/"):
        continue
    if _ora_lead_dd(_a, "posix") or _ora_lead_dd(_b, "posix"):
        continue
    P_REL.append((_a, _b))

W_REL = []
while len(W_REL) < 360:
    _a, _b = _ora_gen_win(_rng, True), _ora_gen_win(_rng, True)
    if not _a or not _b or not _ora_ok_win(_a) or not _ora_ok_win(_b):
        continue
    if _ora_class(_a, "win") != _ora_class(_b, "win"):
        continue
    if _ora_lead_dd(_a, "win") or _ora_lead_dd(_b, "win"):
        continue
    W_REL.append((_a, _b))


def norm_bucket(cases, style):
    def probe():
        for c in cases:
            if NORM(c, style) != _ora_normalize(c, style):
                return False
        return True
    return probe


def rel_bucket(pairs, style):
    def probe():
        for a, b in pairs:
            if REL(a, b, style) != _ora_relative(a, b, style):
                return False
        return True
    return probe


def split_bucket(cases, style):
    def probe():
        for c in cases:
            got = SPL(c, style)
            want = _ora_split_root(c, style)
            if tuple(got) != want:
                return False
        return True
    return probe


def table(pairs, style, fn):
    def probe():
        for src, want in pairs:
            if fn(src, style) != want:
                return False
        return True
    return probe


# --- 1-4: basics -----------------------------------------------------------
check("PathError subclasses ValueError",
      lambda: isinstance(PE, type) and issubclass(PE, ValueError))

check("bad style raises PathError kind 'style'",
      lambda: all(kind_of(f) == "style" for f in [
          lambda: NORM("a", "POSIX"), lambda: NORM("a", "nt"),
          lambda: NORM("a", ""), lambda: NORM("a", None),
          lambda: REL("a", "b", "windows"), lambda: SPL("a", 7),
          lambda: REL("/a", "b", "linux")]))

check("no forbidden module imports",
      lambda: not re.search(
          r"^\s*(?:import|from)\s+(?:os|os\.path|posixpath|ntpath|pathlib|genericpath)\b",
          inspect.getsource(pathnorm), re.M))


def visible():
    return (NORM("a//b/./c") == "a/b/c"
            and NORM("/x/y/../z/") == "/x/z"
            and NORM("") == "."
            and NORM("C:/a/b/../c", "win") == "C:" + B + "a" + B + "c"
            and REL("/a/b/c", "/a/x") == "../b/c"
            and tuple(SPL("C:" + B + "a" + B + "b", "win")) == ("C:", B + "a" + B + "b"))


check("the visible examples from the prompt", visible)

# --- 5-6: targeted normalize edges ----------------------------------------
check("posix normalize: slash-run root rule and '..' at the root", table([
    ("//", "//"), ("//a", "//a"), ("///", "/"), ("///a", "/a"), ("////a/b", "/a/b"),
    ("//a//b//", "//a/b"), ("//..", "//"), ("//../a", "//a"), ("//a/../..", "//"),
    ("/..", "/"), ("/../../a", "/a"), ("/a/../..", "/"), ("", "."), (".", "."),
    ("./", "."), ("a/..", "."), ("a/../..", ".."), ("../a", "../a"),
    ("..//..", "../.."), ("a/", "a"), ("/a/", "/a"), ("a" + B + "b", "a" + B + "b"),
    (".../a", ".../a"), ("/.", "/"),
], "posix", NORM))

check("win normalize: drive-relative, rooted and UNC roots", table([
    ("C:", "C:"), ("C:a", "C:a"), ("C:a/..", "C:"), ("C:a/../..", "C:.."),
    ("C:..", "C:.."), ("C:../..", "C:.." + B + ".."), ("C:" + B, "C:" + B),
    ("C:/", "C:" + B), ("C:/..", "C:" + B), ("C:/a/../..", "C:" + B),
    ("c:/A/B", "c:" + B + "A" + B + "B"),
    (B, B), ("/", B), (B + "a", B + "a"), (B + "a/../..", B),
    ("//s/sh", B + B + "s" + B + "sh"),
    ("//s/sh/", B + B + "s" + B + "sh" + B),
    ("//s/sh/.", B + B + "s" + B + "sh" + B),
    ("//s/sh/..", B + B + "s" + B + "sh" + B),
    ("//s/sh/a/../..", B + B + "s" + B + "sh" + B),
    ("//s/sh/../a", B + B + "s" + B + "sh" + B + "a"),
    ("//s/sh//a//b/", B + B + "s" + B + "sh" + B + "a" + B + "b"),
    ("a/b" + B + "c", "a" + B + "b" + B + "c"), ("", "."), ("a.", "a."),
], "win", NORM))

# --- 7-10: randomised posix normalize -------------------------------------
check("posix normalize, random batch 1", norm_bucket(P_NORM[0:150], "posix"))
check("posix normalize, random batch 2", norm_bucket(P_NORM[150:300], "posix"))
check("posix normalize, random batch 3", norm_bucket(P_NORM[300:450], "posix"))
check("posix normalize, random batch 4", norm_bucket(P_NORM[450:600], "posix"))

# --- 11-14: randomised win normalize --------------------------------------
check("win normalize, random batch 1", norm_bucket(W_NORM[0:150], "win"))
check("win normalize, random batch 2", norm_bucket(W_NORM[150:300], "win"))
check("win normalize, random batch 3", norm_bucket(W_NORM[300:450], "win"))
check("win normalize, random batch 4", norm_bucket(W_NORM[450:600], "win"))

# --- 15: idempotence -------------------------------------------------------
check("normalize is idempotent",
      lambda: all(NORM(NORM(c, s), s) == NORM(c, s)
                  for s, cs in (("posix", P_NORM[:200]), ("win", W_NORM[:200]))
                  for c in cs))

# --- 16-19: split_root -----------------------------------------------------
check("split_root posix, targeted", table([
    ("", ("", "")), ("a/b", ("", "a/b")), ("/", ("/", "")), ("//", ("//", "")),
    ("///", ("/", "")), ("/a", ("/", "a")), ("//a/b", ("//", "a/b")),
    ("///a", ("/", "a")), ("////a", ("/", "a")), ("C:/a", ("", "C:/a")),
    (B + B + "a", ("", B + B + "a")),
], "posix", lambda c, s: tuple(SPL(c, s))))
check("split_root posix, random batch", split_bucket(P_NORM[:300], "posix"))
check("split_root win, random batch 1", split_bucket(W_NORM[0:300], "win"))
check("split_root win, random batch 2", split_bucket(W_NORM[300:600], "win"))

# --- 20-22: randomised posix relative -------------------------------------
check("posix relative, random batch 1", rel_bucket(P_REL[0:120], "posix"))
check("posix relative, random batch 2", rel_bucket(P_REL[120:240], "posix"))
check("posix relative, random batch 3", rel_bucket(P_REL[240:360], "posix"))

# --- 23-25: randomised win relative ---------------------------------------
check("win relative, random batch 1", rel_bucket(W_REL[0:120], "win"))
check("win relative, random batch 2", rel_bucket(W_REL[120:240], "win"))
check("win relative, random batch 3", rel_bucket(W_REL[240:360], "win"))

# --- 26: targeted relative -------------------------------------------------
U = B + B + "s" + B + "sh"
check("relative: targeted corner cases", lambda: all(
    REL(a, b, s) == w for a, b, s, w in [
        ("/a/b", "/a/b", "posix", "."),
        ("//a/b", "/a/b", "posix", "."),
        ("/a", "//a/x", "posix", ".."),
        ("//", "/", "posix", "."),
        ("/", "/a/b", "posix", "../.."),
        ("/a/./b/", "/a", "posix", "b"),
        ("a/b/../c", "a", "posix", "c"),
        ("a", "a/b/c", "posix", "../.."),
        ("A/b", "a", "posix", "../A/b"),
        ("C:a", "C:b", "win", ".." + B + "a"),
        ("C:a/b", "C:", "win", "a" + B + "b"),
        ("C:", "C:a", "win", ".."),
        ("C:" + B + "A" + B + "B", "c:/a/x", "win", ".." + B + "B"),
        ("A" + B + "b", "a", "win", "b"),
        (B + "a" + B + "b", B + "a", "win", "b"),
        (B + "a", B + "b", "win", ".." + B + "a"),
        (U + "/a/b", U, "win", "a" + B + "b"),
        (U, U + "/a", "win", ".."),
        (B + B + "S" + B + "SH" + B + "a", U, "win", "a"),
    ]))

# --- 27-28: relative errors ------------------------------------------------
check("relative: kind 'anchor' when the two classes differ", lambda: all(
    kind_of(lambda a=a, b=b, s=s: REL(a, b, s)) == "anchor" for a, b, s in [
        ("/a", "a", "posix"), ("a", "/a", "posix"), ("//a", "a", "posix"),
        ("a/b", "/", "posix"), (".", "/a", "posix"),
        ("C:" + B + "a", B + "a", "win"), (B + "a", "C:" + B + "a", "win"),
        ("C:a", "C:" + B + "a", "win"), ("C:" + B + "a", "C:a", "win"),
        ("C:a", "a", "win"), ("a", "C:a", "win"),
        (U + B + "a", "C:" + B + "a", "win"), (U, B + "a", "win"),
        (U + B + "a", "a", "win"),
    ]))

check("relative: kind 'root' for different drives / UNC roots", lambda: all(
    kind_of(lambda a=a, b=b: REL(a, b, "win")) == "root" for a, b in [
        ("C:" + B + "a", "D:" + B + "a"), ("d:/a", "C:/a"),
        ("C:a", "D:b"), ("e:x", "C:x"),
        (U + B + "a", B + B + "s" + B + "other" + B + "a"),
        (U, B + B + "t" + B + "sh"),
        (B + B + "S" + B + "D2" + B + "a", U),
    ]))

_t.cancel()
report()
