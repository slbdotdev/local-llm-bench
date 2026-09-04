import sys, os, random, threading, inspect, shlex

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
    import shquote
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


def _missing(*a, **k):
    raise AttributeError("attribute missing from shquote")


SPLIT = getattr(shquote, "split", _missing)
QUOTE = getattr(shquote, "quote", _missing)
JOIN = getattr(shquote, "join", _missing)
SE = getattr(shquote, "SplitError", None)


# ---------------------------------------------------------------- oracle ---
def _ora_split(s):
    """POSIX shlex word splitting with comments disabled; raises ValueError."""
    lex = shlex.shlex(s, posix=True)
    lex.whitespace_split = True
    lex.commenters = ""
    return list(lex)


def _ora_kind(s):
    """Return the expected SplitError kind for s, or None if s is well formed."""
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "'":
            j = s.find("'", i + 1)
            if j < 0:
                return "quote"
            i = j + 1
        elif c == '"':
            i += 1
            closed = False
            while i < n:
                d = s[i]
                if d == "\\":
                    if i + 1 >= n:
                        return "escape"
                    i += 2
                elif d == '"':
                    i += 1
                    closed = True
                    break
                else:
                    i += 1
            if not closed:
                return "quote"
        elif c == "\\":
            if i + 1 >= n:
                return "escape"
            i += 2
        else:
            i += 1
    return None


def _ora_expect(s):
    """('ok', words) or ('err', kind)."""
    k = _ora_kind(s)
    try:
        w = _ora_split(s)
    except ValueError:
        return ("err", k if k is not None else "quote")
    if k is not None:
        return ("err", k)
    return ("ok", w)


def _kind_of(fn):
    if not (isinstance(SE, type) and issubclass(SE, BaseException)):
        return "<no SplitError>"
    try:
        fn()
    except SE as e:
        return getattr(e, "kind", "<no .kind>")
    except Exception as e:
        return "<%s>" % type(e).__name__
    return "<no raise>"


def _one(s):
    """Compare the candidate against the oracle for a single input."""
    want = _ora_expect(s)
    if want[0] == "ok":
        try:
            got = SPLIT(s)
        except Exception:
            return False
        return got == want[1]
    return _kind_of(lambda: SPLIT(s)) == want[1]


def _all(strings):
    def probe():
        for s in strings:
            if not _one(s):
                return False
        return True
    return probe


# ------------------------------------------------------------- generators --
_MIX = list("aab  \t\n\r'\"\\\\#$=")
_QHV = list("ab '\"'\" ")
_BHV = list("ab \\\\\\\"'x")


def _rand_str(rng, alpha, lo, hi):
    return "".join(rng.choice(alpha) for _ in range(rng.randint(lo, hi)))


def _gen(seed, alpha, count, lo=0, hi=24, trunc=False):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        s = _rand_str(rng, alpha, lo, hi)
        if trunc and s:
            s = s[:rng.randint(0, len(s))]
        out.append(s)
    return out


def _buckets(strings, k):
    return [strings[i::k] for i in range(k)]


_WORD_ALPHA = list("ab '\"\\\\ \t\n#$=/-")


def _rand_words(seed, count, lo=0, hi=10):
    rng = random.Random(seed)
    return [_rand_str(rng, _WORD_ALPHA, lo, hi) for _ in range(count)]


# ------------------------------------------------------------ 1: hygiene ---
check("SplitError subclasses ValueError",
      lambda: isinstance(SE, type) and issubclass(SE, ValueError))


def no_shlex():
    src = inspect.getsource(shquote)
    import re as _re
    return not _re.search(r"^\s*(import|from)\s+(shlex|subprocess)\b", src,
                          _re.M)


check("does not import shlex or subprocess", no_shlex)

check("kind 'type' for non-str / non-sequence arguments",
      lambda: _kind_of(lambda: SPLIT(5)) == "type"
      and _kind_of(lambda: SPLIT(None)) == "type"
      and _kind_of(lambda: SPLIT(["a"])) == "type"
      and _kind_of(lambda: QUOTE(5)) == "type"
      and _kind_of(lambda: QUOTE(None)) == "type"
      and _kind_of(lambda: JOIN("ab")) == "type"
      and _kind_of(lambda: JOIN(["a", 3])) == "type")

# ------------------------------------------------------- 4-9: semantics ----
check("basic splitting, whitespace runs, empty input",
      _all(["", " ", "  \t\n\r ", "a", "ls -l  /tmp/x", "  a\tb\nc\rd  ",
            "a\n\nb", "\ta", "a\t"]))

check("single quotes are fully literal",
      _all(["'a b'", "'a\\b'", "'a\\'", "'\\\\'", "'a\"b'", "'a\nb'",
            "'#$='", "'a'\\''b'", "echo 'hello   world'"]))

check("double quotes: backslash escapes only quote and backslash",
      _all(['"a\\nb"', '"a\\\\b"', '"a\\"b"', '"\\$"', '"\\a"', '"\\\\"',
            '"\\""', '"a\\b\\"c"', '"\\\\n"', '"a\\\nb"', '"a\'b"',
            '"a b\tc"', '"\\#"', '"\\="']))

check("backslash outside quotes",
      _all(["a\\ b c", "\\\\", "\\ ", "\\'", '\\"', "a\\\nb", "\\a\\b",
            "a\\\tb", "\\#a", "x\\\\y", "a\\'b", "\\\r"]))

check("quotes are word-internal; empty quoted words",
      _all(["a'b'c", 'x""y', "''", '""', "'' \"\"", "a'' ''b", '"a"\'b\'c',
            '""""', "''''", "a''b", '"" ""', "x''", "''x", 'a""b""c']))

check("no comment handling: # is an ordinary character",
      _all(["a #b", "#", "a#b", "# a b", "a b # c d", "'#'", '"#"', "\\#"]))

# ----------------------------------------------- 10: errors + precedence ---


def err_kinds():
    cases = [
        ("a\\", "escape"), ("\\", "escape"), ('"a\\', "escape"),
        ('"\\', "escape"), ("'a", "quote"), ('"a', "quote"),
        ("'a\\", "quote"), ("'", "quote"), ('"', "quote"),
        ('"\\"', "quote"), ("a 'b c", "quote"), ('a "b\\', "escape"),
        ("'a' 'b", "quote"), ("a\\ b\\", "escape"), ("''\\", "escape"),
        ("\\'", None), ("'a\\'", None), ('"a\\"b"', None),
    ]
    for s, k in cases:
        if k is None:
            try:
                if SPLIT(s) != _ora_split(s):
                    return False
            except Exception:
                return False
        elif _kind_of(lambda s=s: SPLIT(s)) != k:
            return False
    return True


check("error kinds and escape-beats-quote precedence", err_kinds)

# --------------------------------------------------- 11-14: quote / join ---
_QWORDS = ["", "a", "a b", "it's", "'", "''", "a'b'c", "\\", "a\\b", '"',
           'a"b', "a\nb", "a\tb", "-x", "--flag=v", "/a/b.c", "@%+=:,./_-",
           "#", "$HOME", "a#b", "*", "~", "a b'c\"d", " ", "  ", "\n",
           "0", "_", "a=b", "x;y", "(a)", "a|b", "!", "^", "[a]", "{a}",
           "a\rb", "\\'", "'\\'", "e'", "'e"]


def quote_exact():
    for w in _QWORDS:
        if QUOTE(w) != shlex.quote(w):
            return False
    return True


check("quote() matches the reference on curated words", quote_exact)


def roundtrip(words):
    def probe():
        for w in words:
            q = QUOTE(w)
            if q != shlex.quote(w):
                return False
            if SPLIT(q) != [w]:
                return False
        return True
    return probe


_RW = _rand_words(9001, 300, 0, 10)
check("quote() round-trip on random words (A)", roundtrip(_RW[0::2]))
check("quote() round-trip on random words (B)", roundtrip(_RW[1::2]))


def join_roundtrip():
    rng = random.Random(4242)
    pool = _rand_words(777, 120, 0, 8) + _QWORDS
    for _ in range(200):
        ws = [rng.choice(pool) for _ in range(rng.randint(0, 5))]
        j = JOIN(ws)
        if j != " ".join(shlex.quote(w) for w in ws):
            return False
        if SPLIT(j) != ws:
            return False
    return True


check("join() round-trip on random word lists", join_roundtrip)

# ------------------------------------------- 15-27: randomised differential
_FAM_A = _gen(1001, _MIX, 480, 0, 24)
for _i, _b in enumerate(_buckets(_FAM_A, 4)):
    check("differential: mixed alphabet, bucket %d" % _i, _all(_b))

_FAM_B = _gen(2002, _QHV, 360, 0, 14)
for _i, _b in enumerate(_buckets(_FAM_B, 3)):
    check("differential: quote-heavy, bucket %d" % _i, _all(_b))

_FAM_C = _gen(3003, _BHV, 360, 0, 14)
for _i, _b in enumerate(_buckets(_FAM_C, 3)):
    check("differential: backslash-heavy, bucket %d" % _i, _all(_b))

_FAM_D = _gen(4004, _MIX, 360, 1, 20, trunc=True)
for _i, _b in enumerate(_buckets(_FAM_D, 3)):
    check("differential: truncated (error-prone), bucket %d" % _i, _all(_b))

_t.cancel()
report()
