import sys, os, json, random, subprocess, threading

TOTAL = 33
fails = []
done = 0


def check(name, fn):
    global done
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)
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
    import wirefmt
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


def _missing(*a, **k):
    raise AttributeError("attribute missing from wirefmt")


ENC = getattr(wirefmt, "encode", _missing)
DEC = getattr(wirefmt, "decode", _missing)
CAN = getattr(wirefmt, "canon", _missing)
WE = getattr(wirefmt, "WireError", None)

B = chr(92)          # a single backslash
BB = B + B           # two backslashes


def deep_list(k):
    v = "z"
    for _ in range(k):
        v = [v]
    return v


def deep_text(k):
    return "(" * k + "z" + ")" * k


def errs(cases):
    """cases: list of (text, kind, pos) -- decode must raise WireError with those."""
    def probe():
        if not (isinstance(WE, type) and issubclass(WE, ValueError)):
            return False
        for text, kind, pos in cases:
            try:
                DEC(text)
                return False
            except Exception as e:
                if not isinstance(e, WE):
                    return False
                if getattr(e, "kind", None) != kind:
                    return False
                if getattr(e, "pos", None) != pos:
                    return False
        return True
    return probe


def enc_err(values, kind, pos):
    def probe():
        if not (isinstance(WE, type) and issubclass(WE, ValueError)):
            return False
        for v in values:
            try:
                ENC(v)
                return False
            except Exception as e:
                if not isinstance(e, WE):
                    return False
                if getattr(e, "kind", None) != kind:
                    return False
                if getattr(e, "pos", None) != pos:
                    return False
        return True
    return probe


# --- 1: exception type --------------------------------------------------
def exc_shape():
    if not (isinstance(WE, type) and issubclass(WE, ValueError)):
        return False
    try:
        DEC("")
    except WE as e:
        return isinstance(getattr(e, "kind", None), str) and \
            isinstance(getattr(e, "pos", None), int)
    return False


check("WireError subclasses ValueError and carries .kind/.pos", exc_shape)

# --- 2-5: encode --------------------------------------------------------
check("encode plain atoms",
      lambda: ENC("abc") == "abc" and ENC("a b") == "a b"
      and ENC("") == "~" and ENC("~") == B + "~"
      and ENC("hello world!") == "hello world!")
check("encode escapes backslash and delimiters",
      lambda: ENC(B) == BB and ENC("(") == B + "("
      and ENC(")") == B + ")" and ENC(",") == B + ","
      and ENC("a" + B + "b") == "a" + BB + "b"
      and ENC("x,y") == "x" + B + ",y")
check("encode uses lowercase two-digit hex for control characters",
      lambda: ENC("\n") == B + "x0a" and ENC("\t") == B + "x09"
      and ENC(chr(0)) == B + "x00" and ENC(chr(0x1f)) == B + "x1f"
      and ENC(chr(0x7f)) == B + "x7f"
      and ENC("a\nb") == "a" + B + "x0ab")
check("encode leaves ordinary and non-ASCII characters literal",
      lambda: ENC(" ") == " " and ENC("x") == "x" and ENC("X") == "X"
      and ENC('["]') == '["]' and ENC("é中") == "é中"
      and ENC(chr(0x20) + chr(0x7d)) == chr(0x20) + chr(0x7d))
check("encode lists and nesting",
      lambda: ENC([]) == "()" and ENC(["a"]) == "(a)"
      and ENC(["a", ""]) == "(a,~)"
      and ENC([[], ["a"]]) == "((),(a))"
      and ENC([["a", "b"], "c"]) == "((a,b),c)"
      and ENC([[[]]]) == "((()))"
      and ENC(["a b", "", "~", "x,y"]) == "(a b,~," + B + "~,x" + B + ",y)")

# --- 6-7: encode errors -------------------------------------------------
check("encode raises type error for non str/list values",
      enc_err([1, None, ("a",), {"a": 1}, ["ok", 2], [["x", 3.5]]], "type", 0))
check("encode enforces the depth limit of 200",
      lambda: ENC(deep_list(200)) == deep_text(200)
      and enc_err([deep_list(201), deep_list(260)], "depth", 0)())

# --- 8-11: decode canonical forms ---------------------------------------
check("decode plain atoms and the tilde atom",
      lambda: DEC("abc") == "abc" and DEC("a b") == "a b"
      and DEC("~") == "" and DEC(B + "~") == "~")
check("decode canonical escapes",
      lambda: DEC(BB) == B and DEC(B + "(") == "("
      and DEC(B + ")") == ")" and DEC(B + ",") == ","
      and DEC("(a" + B + ")b)") == ["a)b"]
      and DEC("(x" + B + ",y)") == ["x,y"])
check("decode lowercase hex escapes",
      lambda: DEC(B + "x0a") == "\n" and DEC(B + "x00") == chr(0)
      and DEC(B + "x7f") == chr(0x7f) and DEC(B + "x7e") == "~"
      and DEC("(a" + B + "x0ab)") == ["a\nb"])
check("decode lists and nesting",
      lambda: DEC("()") == [] and DEC("(a)") == ["a"]
      and DEC("(a,~)") == ["a", ""] and DEC("((),(a))") == [[], ["a"]]
      and DEC("((a,b),c)") == [["a", "b"], "c"]
      and DEC("(())") == [[]] and DEC("((),())") == [[], []])

# --- 12-14: decode's extra accepted forms -------------------------------
check("decode accepts uppercase hex digits",
      lambda: DEC(B + "x0A") == "\n" and DEC(B + "x7F") == chr(0x7f)
      and DEC(B + "x41") == "A" and DEC(B + "xFF") == chr(255)
      and DEC("(" + B + "x0A," + B + "x0a)") == ["\n", "\n"])
check("decode accepts redundant escapes of printable ASCII",
      lambda: DEC(B + "a") == "a" and DEC(B + " ") == " "
      and DEC(B + "7") == "7" and DEC(B + ".") == "."
      and DEC(B + "X41") == "X41" and DEC("(" + B + "q" + B + "Z)") == ["qZ"])
check("decode treats '(' inside an atom as a literal",
      lambda: DEC("(a(b)") == ["a(b"] and DEC("a(b") == "a(b"
      and DEC("(a,b(c)") == ["a", "b(c"])

# --- 15-16: canon -------------------------------------------------------
CANON_CASES = [
    ("(" + B + "x41," + B + "a,a(b,~)", "(A,a,a" + B + "(b,~)"),
    ("(" + B + "X41)", "(X41)"),
    ("(" + B + "x0A)", "(" + B + "x0a)"),
    ("(" + B + "x7E)", "(" + B + "~)"),
    ("(~)", "(~)"),
    ("(" + B + "~)", "(" + B + "~)"),
    ("()", "()"),
    ("(a" + B + ")b)", "(a" + B + ")b)"),
    ("~", "~"),
    ("a(b", "a" + B + "(b"),
    ("(" + B + " ," + B + "7)", "( ,7)"),
    ("(" + B + "x00," + B + "x1F)", "(" + B + "x00," + B + "x1f)"),
    ("((),(" + B + "x0A)," + B + "X41," + B + "a)",
     "((),(" + B + "x0a),X41,a)"),
]

check("canon normalises to the canonical form",
      lambda: all(CAN(src) == want for src, want in CANON_CASES))
check("canon is idempotent",
      lambda: all(CAN(CAN(src)) == CAN(src) for src, _w in CANON_CASES)
      and all(CAN(want) == want for _s, want in CANON_CASES))

# --- 17-18: random round trips ------------------------------------------
ALPHA = ["a", "Z", " ", "(", ")", ",", "~", B, "x", "X", "\n", "\t",
         chr(0), chr(0x7f), "é", "0", '"', "[", "|", chr(0x1f)]


def rand_value(rng, depth):
    if depth <= 0 or rng.random() < 0.45:
        return "".join(rng.choice(ALPHA) for _ in range(rng.randint(0, 6)))
    return [rand_value(rng, depth - 1) for _ in range(rng.randint(0, 4))]


def rand_values():
    rng = random.Random(20240902)
    return [rand_value(rng, 4) for _ in range(300)]


def rt_decode():
    for v in rand_values():
        if DEC(ENC(v)) != v:
            return False
    return True


def rt_canon():
    for v in rand_values():
        t = ENC(v)
        if CAN(t) != t:
            return False
    return True


check("random values survive encode then decode", rt_decode)
check("encode output is already canonical for random values", rt_canon)

# --- 19-25: individual error kinds --------------------------------------
check("error kind 'escape'",
      errs([("(a" + B, "escape", 2),
            (B, "escape", 0),
            ("(" + B + "xzz)", "escape", 1),
            ("(" + B + "x0)", "escape", 1),
            ("(" + B + "x)", "escape", 1),
            ("(a" + B + "\n)", "escape", 2),
            ("(" + B + "é)", "escape", 1)]))
check("error kind 'tilde'",
      errs([("(a~b)", "tilde", 2),
            ("(~a)", "tilde", 1),
            ("~x", "tilde", 0),
            ("(a,~~)", "tilde", 3),
            ("(~(a))", "tilde", 1)]))
check("error kind 'empty'",
      errs([("", "empty", 0),
            ("(,a)", "empty", 1),
            ("(a,)", "empty", 3),
            ("(,)", "empty", 1),
            ("((),)", "empty", 4),
            ("(a,,b)", "empty", 3)]))
check("error kind 'delim'",
      errs([("a,b", "delim", 1),
            ("a)", "delim", 1),
            ("(),", "delim", 2),
            ("(a))", "delim", 3),
            ("~,a", "delim", 1)]))
check("error kind 'unterminated'",
      errs([("(a", "unterminated", 2),
            ("((a)", "unterminated", 4),
            ("(a,b", "unterminated", 4),
            ("(()", "unterminated", 3),
            ("(a" + B + "x41", "unterminated", 6)]))
check("error kind 'trailing'",
      errs([("()x", "trailing", 2),
            ("((a)b)", "trailing", 4),
            ("(a)(", "trailing", 3),
            ("(a)b", "trailing", 3),
            ("(())x", "trailing", 4)]))
check("error kind 'depth' from decode",
      lambda: DEC(deep_text(200)) == deep_list(200)
      and errs([("(" * 201 + ")" * 201, "depth", 200),
                ("(" * 250, "depth", 200),
                ("(" * 201 + "z", "depth", 200)])())

# --- 26-28: precedence --------------------------------------------------
check("precedence: 'empty' beats 'delim' at the same position",
      errs([(",", "empty", 0), (")", "empty", 0)]))
check("precedence: 'empty' beats 'unterminated' at the same position",
      errs([("(a,", "empty", 3), ("(", "empty", 1), ("(,", "empty", 1),
            ("((a,", "empty", 4)]))
check("precedence: the smallest position wins",
      errs([("(~a," + B + "xzz)", "tilde", 1),
            ("(" + B + "xzz,~a)", "escape", 1),
            ("(a~b", "tilde", 2),
            ("(a,)x", "empty", 3),
            ("(a" + B + ",b~c", "tilde", 5)]))

# --- 29: tricky round trips ---------------------------------------------
TRICKY = ["", "~", B, "(", ")", ",", "()", "(,)", "a~b", "\n", chr(0x7f),
          "é中", " lead and trail ", "x", "X41", B + "x41",
          ["", ""], [[], [[]]], ["a,b", "c)d", "e(f"], [["~"], "~", ""]]
check("encode/decode round trip on tricky values",
      lambda: all(DEC(ENC(v)) == v for v in TRICKY)
      and all(CAN(ENC(v)) == ENC(v) for v in TRICKY))

# --- 30-33: performance, in a subprocess --------------------------------
script = (
    "import json, time, wirefmt\n"
    "N = 200000\n"
    "atoms = ['a%d' % i for i in range(N)]\n"
    "text = '(' + ','.join(atoms) + ')'\n"
    "t0 = time.perf_counter()\n"
    "v = wirefmt.decode(text)\n"
    "out = wirefmt.encode(v)\n"
    "el = time.perf_counter() - t0\n"
    "print(json.dumps(['flat_decode', v == atoms]), flush=True)\n"
    "print(json.dumps(['flat_encode', out == text]), flush=True)\n"
    "print(json.dumps(['flat_time', el]), flush=True)\n"
    "d = '(' * 200 + 'z' + ')' * 200\n"
    "try:\n"
    "    ok = wirefmt.encode(wirefmt.decode(d)) == d\n"
    "except Exception:\n"
    "    ok = False\n"
    "print(json.dumps(['deep', ok]), flush=True)\n"
)
out = ""
try:
    r = subprocess.run([sys.executable, "-c", script], capture_output=True,
                       text=True, timeout=25)
    out = r.stdout or ""
except subprocess.TimeoutExpired as e:
    o = e.output
    out = o if isinstance(o, str) else (o or b"").decode("utf-8", "replace")
except Exception:
    out = ""
got = {}
for line in (out or "").splitlines():
    try:
        k, v = json.loads(line)
        got[k] = v
    except Exception:
        pass

check("decode of a 200,000-atom flat list is correct",
      lambda: got.get("flat_decode") is True)
check("encode of a 200,000-atom flat list is correct",
      lambda: got.get("flat_encode") is True)
check("decode+encode of a 200,000-atom flat list runs in under 5 s",
      lambda: isinstance(got.get("flat_time"), float) and got["flat_time"] < 5.0)
check("200-deep nesting decodes and re-encodes",
      lambda: got.get("deep") is True)

report()
