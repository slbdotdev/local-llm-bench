import sys, os, io, random, threading, inspect, tokenize

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
    import strictcodec
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()

# ==========================================================================
# oracle -- an independent inlined implementation; every name is _ora_*
# ==========================================================================
_ORA_B64S = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
_ORA_B64U = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
_ORA_B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_ORA_WS = " \t\n\r\f\v"
_ORA_HEX = "0123456789ABCDEF"


def _ora_pack(data, alpha, bpc, group, pad):
    bits = []
    for b in data:
        for s in (7, 6, 5, 4, 3, 2, 1, 0):
            bits.append((b >> s) & 1)
    while len(bits) % bpc:
        bits.append(0)
    out = []
    for i in range(0, len(bits), bpc):
        v = 0
        for j in range(bpc):
            v = v * 2 + bits[i + j]
        out.append(alpha[v])
    if pad:
        while len(out) % group:
            out.append("=")
    return "".join(out)


def _ora_b64_encode(data, urlsafe=False, pad=True):
    return _ora_pack(data, _ORA_B64U if urlsafe else _ORA_B64S, 6, 4, pad)


def _ora_b32_encode(data, pad=True):
    return _ora_pack(data, _ORA_B32, 5, 8, pad)


def _ora_unpack(text, alpha, bpc, group, pad, runs, badmods, zbits):
    """Return ('ok', bytes) or ('err', kind, pos)."""
    for i, ch in enumerate(text):
        if ch == "=" or ch in alpha:
            continue
        return ("err", "whitespace" if ch in _ORA_WS else "alphabet", i)
    n = len(text)
    run = 0
    while run < n and text[n - 1 - run] == "=":
        run += 1
    limit = (n - run) if (pad and run in runs) else n
    for i in range(limit):
        if text[i] == "=":
            return ("err", "padding", i)
    if pad:
        if n % group:
            return ("err", "length", n)
    elif (n % group) in badmods:
        return ("err", "length", n)
    dlen = n - run
    g = dlen % group
    if g in zbits:
        if alpha.index(text[dlen - 1]) % (2 ** zbits[g]):
            return ("err", "bits", dlen - 1)
    bits = []
    for i in range(dlen):
        v = alpha.index(text[i])
        for s in range(bpc - 1, -1, -1):
            bits.append((v >> s) & 1)
    out = bytearray()
    for i in range(0, (len(bits) // 8) * 8, 8):
        v = 0
        for j in range(8):
            v = v * 2 + bits[i + j]
        out.append(v)
    return ("ok", bytes(out))


def _ora_b64_decode(text, urlsafe=False, pad=True):
    return _ora_unpack(text, _ORA_B64U if urlsafe else _ORA_B64S, 6, 4, pad,
                       (1, 2), (1,), {2: 4, 3: 2})


def _ora_b32_decode(text, pad=True):
    return _ora_unpack(text, _ORA_B32, 5, 8, pad,
                       (6, 4, 3, 1), (1, 3, 6), {2: 2, 4: 4, 5: 1, 7: 3})


def _ora_qp_encode(data):
    lines = []
    line = ""
    n = len(data)
    for i in range(n):
        b = data[i]
        if b == 0x20 or b == 0x09:
            unit = chr(b) if i != n - 1 else ("=20" if b == 0x20 else "=09")
        elif 33 <= b <= 126 and b != 0x3D:
            unit = chr(b)
        else:
            unit = "=" + _ORA_HEX[b // 16] + _ORA_HEX[b % 16]
        if len(line) + len(unit) > 75:
            lines.append(line + "=")
            line = ""
        if len(unit) == 1 and (unit == " " or unit == "\t") and len(line) + 1 > 72:
            unit = "=20" if unit == " " else "=09"
            if len(line) + 3 > 75:
                lines.append(line + "=")
                line = ""
        line += unit
    lines.append(line)
    return "\r\n".join(lines)


def _ora_qp_scan(text):
    n = len(text)
    best = None
    for i in range(n):
        ch = text[i]
        o = ord(ch)
        cand = None
        if not (33 <= o <= 126 or ch in " \t\r\n"):
            cand = (i, 0, "char")
        elif ch == "\r":
            if i + 1 >= n or text[i + 1] != "\n":
                cand = (i, 1, "eol")
        elif ch == "\n":
            if i == 0 or text[i - 1] != "\r":
                cand = (i, 1, "eol")
        elif ch == "=":
            if n - i - 1 <= 1:
                cand = (i, 2, "trunc")
            elif text[i + 1] == "\r" and text[i + 2] == "\n":
                if i + 3 == n:
                    cand = (i, 3, "eol")
            elif text[i + 1] not in _ORA_HEX:
                cand = (i + 1, 4, "hex")
            elif text[i + 2] not in _ORA_HEX:
                cand = (i + 2, 4, "hex")
        if cand is not None and (best is None or cand[:2] < best[:2]):
            best = cand
    return best


def _ora_qp_lines(text):
    segs = []
    pos = 0
    while True:
        j = text.find("\r\n", pos)
        if j < 0:
            segs.append((pos, text[pos:]))
            return segs
        seg = text[pos:j]
        if seg[-1:] == "=":
            seg = seg[:-1]
        segs.append((pos, seg))
        pos = j + 2


def _ora_qp_decode(text):
    bad = _ora_qp_scan(text)
    if bad is not None:
        return ("err", bad[2], bad[0])
    segs = _ora_qp_lines(text)
    for start, seg in segs:
        if len(seg) > 75:
            return ("err", "length", start + 75)
    for start, seg in segs:
        if seg[-1:] == " " or seg[-1:] == "\t":
            return ("err", "trailws", start + len(seg) - 1)
    out = bytearray()
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "=":
            if text[i + 1] == "\r":
                i += 3
            else:
                out.append(_ORA_HEX.index(text[i + 1]) * 16 + _ORA_HEX.index(text[i + 2]))
                i += 3
        elif ch == "\r":
            out.append(13)
            out.append(10)
            i += 2
        else:
            out.append(ord(ch))
            i += 1
    return ("ok", bytes(out))


# ==========================================================================
# handles on the candidate
# ==========================================================================
def _missing(*a, **k):
    raise AttributeError("attribute missing from strictcodec")


B64E = getattr(strictcodec, "b64_encode", _missing)
B64D = getattr(strictcodec, "b64_decode", _missing)
B32E = getattr(strictcodec, "b32_encode", _missing)
B32D = getattr(strictcodec, "b32_decode", _missing)
QPE = getattr(strictcodec, "qp_encode", _missing)
QPD = getattr(strictcodec, "qp_decode", _missing)
CE = getattr(strictcodec, "CodecError", None)
_CE_OK = isinstance(CE, type) and issubclass(CE, ValueError)

_CAND = {"b64": B64D, "b32": B32D, "qp": QPD}


def _call(fn, *a):
    """('ok', value) / ('err', kind, pos) / ('bad', reason)."""
    try:
        v = fn(*a)
    except Exception as e:
        if _CE_OK and isinstance(e, CE):
            return ("err", getattr(e, "kind", "<none>"), getattr(e, "pos", "<none>"))
        return ("bad", "raised " + type(e).__name__)
    return ("ok", v)


def _dec(fn, want, *a):
    got = _call(fn, *a)
    if want[0] == "ok":
        return got[0] == "ok" and type(got[1]) is bytes and got[1] == want[1]
    return got == want


def _err(fn, kind, pos, *a):
    return _call(fn, *a) == ("err", kind, pos)


def _one(entry):
    """entry = (codec, args_tuple, expected) with expected ('ok', b)/('err', k, p)."""
    return _dec(_CAND[entry[0]], entry[2], *entry[1])


def _set(entries):
    def probe():
        for e in entries:
            if not _one(e):
                return False
        return True
    return probe


def E(kind, pos):
    return ("err", kind, pos)


def K(data):
    return ("ok", data)


# ==========================================================================
# 1: exception shape
# ==========================================================================
def ce_shape():
    if not _CE_OK:
        return False
    if _call(B64D, "A") != ("err", "length", 1):
        return False
    try:
        B64D("A")
    except ValueError as e:
        return (isinstance(getattr(e, "kind", None), str)
                and type(getattr(e, "pos", None)) is int)
    return False


check("CodecError subclasses ValueError and carries .kind / .pos", ce_shape)

# ==========================================================================
# 2-7: encoders
# ==========================================================================
_B64_VEC = [(b"", "", ""), (b"f", "Zg==", "Zg"), (b"fo", "Zm8=", "Zm8"),
            (b"foo", "Zm9v", "Zm9v"), (b"foob", "Zm9vYg==", "Zm9vYg"),
            (b"fooba", "Zm9vYmE=", "Zm9vYmE"), (b"foobar", "Zm9vYmFy", "Zm9vYmFy"),
            (b"\x00", "AA==", "AA"), (b"\x00\x00\x00", "AAAA", "AAAA"),
            (b"\xff\xff\xff", "////", "////"), (b"\xff", "/w==", "/w"),
            (b"\xfb\xef", "++8=", "++8"), (b"sure.", "c3VyZS4=", "c3VyZS4")]

check("base64 encode: standard alphabet, pad=True and pad=False",
      lambda: all(B64E(d) == p and B64E(d, False, True) == p and B64E(d, False, False) == u
                  for d, p, u in _B64_VEC))

check("base64 encode: urlsafe alphabet",
      lambda: all(B64E(d, True) == p.replace("+", "-").replace("/", "_")
                  and B64E(d, True, False) == u.replace("+", "-").replace("/", "_")
                  for d, p, u in _B64_VEC))

_B32_VEC = [(b"", ""), (b"f", "MY======"), (b"fo", "MZXQ===="), (b"foo", "MZXW6==="),
            (b"foob", "MZXW6YQ="), (b"fooba", "MZXW6YTB"), (b"foobar", "MZXW6YTBOI======"),
            (b"\x00", "AA======"), (b"\xff\xff\xff\xff\xff", "77777777"),
            (b"\x00\x00\x00\x00\x00", "AAAAAAAA")]

check("base32 encode: fixed vectors, pad=True and pad=False",
      lambda: all(B32E(d) == p and B32E(d, True) == p and B32E(d, False) == p.replace("=", "")
                  for d, p in _B32_VEC))

_QP_VEC = [(b"", ""), (b"hello", "hello"), (b"a=b", "a=3Db"),
           (b"caf\xc3\xa9", "caf=C3=A9"), (b"\x00\x01\x7f\x80\xff", "=00=01=7F=80=FF"),
           (b"a b", "a b"), (b"\r\n", "=0D=0A"), (b"~!", "~!"),
           (b"\xde\xad\xbe\xef", "=DE=AD=BE=EF"), (b"a\tb", "a\tb"),
           (b" ", "=20"), (b"\t", "=09"), (b"x ", "x=20"), (b"x\t", "x=09"),
           (b"  x", "  x"), (b"=", "=3D")]

check("qp encode: fixed vectors with uppercase hex escapes",
      lambda: all(QPE(d) == s for d, s in _QP_VEC))


def qp_columns():
    for n in range(70, 82):
        d = b"a" * n
        if QPE(d) != _ora_qp_encode(d):
            return False
    for n in (24, 25, 26, 40):
        d = b"\xff" * n
        if QPE(d) != _ora_qp_encode(d):
            return False
    for n in (70, 73, 74, 75, 76, 77):
        d = b"a" * n + b"\xff" + b"b" * 20
        if QPE(d) != _ora_qp_encode(d):
            return False
    got = QPE(b"a" * 80)
    return (got == "a" * 75 + "=\r\n" + "a" * 5
            and all(len(ln) <= 76 for ln in got.split("\r\n")))


check("qp encode: soft line breaks at the 75/76 column boundary", qp_columns)


def qp_trailing():
    for n in (72, 73, 74, 75, 76):
        for filler in (b"a", b"\xff"):
            for ws in (b" ", b"\t"):
                d = filler * n + ws + b"z" * 8
                if QPE(d) != _ora_qp_encode(d):
                    return False
    rng = random.Random(5150)
    for _ in range(120):
        d = bytes(rng.choice([32, 9, 97, 255, 61]) for _ in range(rng.randrange(0, 200)))
        got = QPE(d)
        if got != _ora_qp_encode(d):
            return False
        for ln in got.split("\r\n"):
            body = ln[:-1] if ln[-1:] == "=" else ln
            if len(body) > 75 or body[-1:] == " " or body[-1:] == "\t":
                return False
    return True


check("qp encode: no line content ends in space or tab", qp_trailing)

# ==========================================================================
# 8-13: randomised round-trip / valid-decode differentials
# ==========================================================================
def _gen_data(seed, count, maxlen, alphabet=None):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        n = rng.randrange(0, maxlen + 1)
        if alphabet is None:
            out.append(bytes(rng.randrange(256) for _ in range(n)))
        else:
            out.append(bytes(rng.choice(alphabet) for _ in range(n)))
    return out


_D_SMALL = _gen_data(11, 150, 12)
_D_BIG = _gen_data(12, 40, 400)
_D_ALL = _D_SMALL + _D_BIG


def b64_roundtrip():
    for d in _D_ALL:
        for us in (False, True):
            for pad in (False, True):
                enc = B64E(d, us, pad)
                if type(enc) is not str or enc != _ora_b64_encode(d, us, pad):
                    return False
                if not _dec(B64D, ("ok", d), enc, us, pad):
                    return False
    return True


def b32_roundtrip():
    for d in _D_ALL:
        for pad in (False, True):
            enc = B32E(d, pad)
            if type(enc) is not str or enc != _ora_b32_encode(d, pad):
                return False
            if not _dec(B32D, ("ok", d), enc, pad):
                return False
    return True


def _qp_rt(data):
    def probe():
        for d in data:
            enc = QPE(d)
            if type(enc) is not str or enc != _ora_qp_encode(d):
                return False
            if not _dec(QPD, ("ok", d), enc):
                return False
        return True
    return probe


check("base64 round-trip differential (random data, all flag combinations)", b64_roundtrip)
check("base32 round-trip differential (random data, both pad settings)", b32_roundtrip)
check("quoted-printable round-trip differential (random binary data)",
      _qp_rt(_D_SMALL + _gen_data(13, 30, 400)))
check("quoted-printable round-trip differential (space / tab / CR LF heavy data)",
      _qp_rt(_gen_data(14, 60, 250, [32, 9, 61, 13, 10, 65, 122, 0, 255, 126, 33])
             + _gen_data(15, 40, 200, [32, 9, 32, 32, 97])))


def decode_valid():
    rng = random.Random(21)
    for _ in range(150):
        d = bytes(rng.randrange(256) for _ in range(rng.randrange(0, 60)))
        us, pad = rng.choice([False, True]), rng.choice([False, True])
        txt = _ora_b64_encode(d, us, pad)
        if not _dec(B64D, _ora_b64_decode(txt, us, pad), txt, us, pad):
            return False
        pad2 = rng.choice([False, True])
        txt2 = _ora_b32_encode(d, pad2)
        if not _dec(B32D, _ora_b32_decode(txt2, pad2), txt2, pad2):
            return False
    return True


check("decoding valid base64 / base32 texts produced independently", decode_valid)

_QPD_VEC = [("qp", ("",), K(b"")), ("qp", ("hello",), K(b"hello")),
            ("qp", ("a=3Db",), K(b"a=b")), ("qp", ("=00=FF",), K(b"\x00\xff")),
            ("qp", ("a\r\nb",), K(b"a\r\nb")), ("qp", ("a=\r\nb",), K(b"ab")),
            ("qp", ("a\r\n\r\nb",), K(b"a\r\n\r\nb")), ("qp", ("=\r\nx",), K(b"x")),
            ("qp", ("a b\tc",), K(b"a b\tc")), ("qp", ("=3D=3D",), K(b"==")),
            ("qp", ("x" * 75,), K(b"x" * 75)),
            ("qp", ("x" * 75 + "=\r\ny",), K(b"x" * 75 + b"y")),
            ("qp", ("=41=42=43",), K(b"ABC")), ("qp", ("~",), K(b"~")),
            ("qp", ("!",), K(b"!")), ("qp", ("a\r\nb\r\nc",), K(b"a\r\nb\r\nc"))]

check("qp decode: soft breaks, hard CR LF line breaks and escapes", _set(_QPD_VEC))

# ==========================================================================
# 13: return types and 'type' errors
# ==========================================================================
_NOT_BYTES = [bytearray(b"ab"), memoryview(b"ab"), "ab", 5, None, [1, 2], (1,), 1.0, True]
_NOT_STR = [b"AAAA", bytearray(b"AAAA"), 5, None, ["A"], 1.0, True, memoryview(b"A")]


def types_and_type_errors():
    if not (type(B64E(b"x")) is str and type(B32E(b"x")) is str and type(QPE(b"x")) is str):
        return False
    if not (type(B64D("eA==")) is bytes and type(B32D("PA======")) is bytes):
        return False
    if not (type(QPD("x")) is bytes and type(QPD("")) is bytes and type(B64D("")) is bytes):
        return False
    for v in _NOT_BYTES:
        for fn in (B64E, B32E, QPE):
            if not _err(fn, "type", -1, v):
                return False
    for v in _NOT_STR:
        for fn in (B64D, B32D, QPD):
            if not _err(fn, "type", -1, v):
                return False
    return _err(B64D, "type", -1, b"!!!") and _err(QPD, "type", -1, b"=")


check("exact return types, and 'type' errors at pos -1", types_and_type_errors)

# ==========================================================================
# 14-21: base64 / base32 strictness
# ==========================================================================
check("base64 padding rules", _set([
    ("b64", ("A===",), E("padding", 1)),
    ("b64", ("A=B=",), E("padding", 1)),
    ("b64", ("====",), E("padding", 0)),
    ("b64", ("==A=",), E("padding", 0)),
    ("b64", ("=A==",), E("padding", 0)),
    ("b64", ("AB=CD===",), E("padding", 2)),
    ("b64", ("AAAA====",), E("padding", 4)),
    ("b64", ("Zm8=Zm8=",), E("padding", 3)),
    ("b64", ("Zg==", False, False), E("padding", 2)),
    ("b64", ("Zm9vYmE=", False, False), E("padding", 7)),
    ("b64", ("Zg==",), K(b"f")),
    ("b64", ("Zm8=",), K(b"fo")),
    ("b64", ("",), K(b"")),
]))

check("base64 leftover-bit rule", _set([
    ("b64", ("Zh==",), E("bits", 1)),
    ("b64", ("ZB==",), E("bits", 1)),
    ("b64", ("Zm9=",), E("bits", 2)),
    ("b64", ("Zh", False, False), E("bits", 1)),
    ("b64", ("Zm9", False, False), E("bits", 2)),
    ("b64", ("//==",), E("bits", 1)),
    ("b64", ("///=",), E("bits", 2)),
    ("b64", ("AAAA/x==",), E("bits", 5)),
    ("b64", ("/w==",), K(b"\xff")),
    ("b64", ("//8=",), K(b"\xff\xff")),
    ("b64", ("//8", False, False), K(b"\xff\xff")),
]))

check("base64 alphabet errors, including the other alphabet", _set([
    ("b64", ("*AAA",), E("alphabet", 0)),
    ("b64", ("AA*A",), E("alphabet", 2)),
    ("b64", ("-AAA",), E("alphabet", 0)),
    ("b64", ("A_AA",), E("alphabet", 1)),
    ("b64", ("+AAA", True), E("alphabet", 0)),
    ("b64", ("AA/A", True), E("alphabet", 2)),
    ("b64", ("AAA\x00",), E("alphabet", 3)),
    ("b64", ("AéAA",), E("alphabet", 1)),
    ("b64", ("A-_A", True), K(b"\x03\xef\xc0")),
    ("b32", ("0AAAAAAA",), E("alphabet", 0)),
    ("b32", ("A1AAAAAA",), E("alphabet", 1)),
    ("b32", ("AAAAAAA8",), E("alphabet", 7)),
]))

check("whitespace is rejected everywhere", _set([
    ("b64", ("AAAA\n",), E("whitespace", 4)),
    ("b64", (" AAAA",), E("whitespace", 0)),
    ("b64", ("AA\tAA",), E("whitespace", 2)),
    ("b64", ("AAAA\r\nAAAA",), E("whitespace", 4)),
    ("b64", ("A\x0bAA",), E("whitespace", 1)),
    ("b64", ("A\x0cAA",), E("whitespace", 1)),
    ("b64", ("Zm9vYmFy\n", False, False), E("whitespace", 8)),
    ("b64", ("Zg==\n",), E("whitespace", 4)),
    ("b32", ("MZXW6YTB\n",), E("whitespace", 8)),
    ("b32", ("\nMZXW6YTB",), E("whitespace", 0)),
    ("b32", ("MZXW6YTB ", False), E("whitespace", 8)),
]))

check("base64 length rules under both pad settings", _set([
    ("b64", ("A",), E("length", 1)),
    ("b64", ("AA",), E("length", 2)),
    ("b64", ("AAA",), E("length", 3)),
    ("b64", ("AAAAA",), E("length", 5)),
    ("b64", ("==",), E("length", 2)),
    ("b64", ("=",), E("length", 1)),
    ("b64", ("A", False, False), E("length", 1)),
    ("b64", ("AAAAA", False, False), E("length", 5)),
    ("b64", ("AAAAAAAAA", False, False), E("length", 9)),
    ("b64", ("AA", False, False), K(b"\x00")),
    ("b64", ("AAA", False, False), K(b"\x00\x00")),
    ("b64", ("", False, False), K(b"")),
]))

check("base32 padding-run lengths and length rules", _set([
    ("b32", ("A=======",), E("padding", 1)),
    ("b32", ("AA=====",), E("padding", 2)),
    ("b32", ("MZXW6Y==",), E("padding", 6)),
    ("b32", ("========",), E("padding", 0)),
    ("b32", ("MY=XW6==",), E("padding", 2)),
    ("b32", ("MY======", False), E("padding", 2)),
    ("b32", ("MZXW6YTBA",), E("length", 9)),
    ("b32", ("M",), E("length", 1)),
    ("b32", ("M", False), E("length", 1)),
    ("b32", ("MZX", False), E("length", 3)),
    ("b32", ("MZXW6Y", False), E("length", 6)),
    ("b32", ("MY", False), K(b"f")),
    ("b32", ("MZXW6YQ", False), K(b"foob")),
    ("b32", ("MY======",), K(b"f")),
]))

check("base32 leftover bits and lowercase rejection", _set([
    ("b32", ("MZ======",), E("bits", 1)),
    ("b32", ("MZXX====",), E("bits", 3)),
    ("b32", ("MZXW7===",), E("bits", 4)),
    ("b32", ("MZXW6YR=",), E("bits", 6)),
    ("b32", ("MZ", False), E("bits", 1)),
    ("b32", ("MZXW6YR", False), E("bits", 6)),
    ("b32", ("mzxw6ytb",), E("alphabet", 0)),
    ("b32", ("MZxW6YTB",), E("alphabet", 2)),
    ("b32", ("My======",), E("alphabet", 1)),
    ("b32", ("MZXQ====",), K(b"fo")),
    ("b32", ("MZXW6YQ=",), K(b"foob")),
]))

check("decoder error precedence order", _set([
    # whitespace / alphabet beat padding, length and bits
    ("b64", ("A A===",), E("whitespace", 1)),
    ("b64", ("*A===",), E("alphabet", 0)),
    ("b64", ("Zh\n==",), E("whitespace", 2)),
    ("b64", ("Zh=-",), E("alphabet", 3)),
    ("b32", ("mz======",), E("alphabet", 0)),
    # padding beats length and bits
    ("b64", ("Z===",), E("padding", 1)),
    ("b64", ("Zh==", False, False), E("padding", 2)),
    ("b32", ("M=======",), E("padding", 1)),
    # length beats bits
    ("b64", ("Zh=",), E("length", 3)),
    ("b64", ("ZhAAA", False, False), E("length", 5)),
    ("b32", ("MZXW6Z", False), E("length", 6)),
]))

# ==========================================================================
# 22-25: quoted-printable strictness
# ==========================================================================
check("qp requires uppercase hex, with 'hex' at the offending offset", _set([
    ("qp", ("=0a",), E("hex", 2)),
    ("qp", ("=aB",), E("hex", 1)),
    ("qp", ("=ff",), E("hex", 1)),
    ("qp", ("=Ff",), E("hex", 2)),
    ("qp", ("x=g0y",), E("hex", 2)),
    ("qp", ("x=0gy",), E("hex", 3)),
    ("qp", ("a==3Db",), E("hex", 2)),
    ("qp", ("= 0",), E("hex", 1)),
    ("qp", ("=0 ",), E("hex", 2)),
    ("qp", ("=41=4z",), E("hex", 5)),
    ("qp", ("=AB",), K(b"\xab")),
    ("qp", ("=0A",), K(b"\x0a")),
]))

check("qp 75-character line-content limit", _set([
    ("qp", ("x" * 75,), K(b"x" * 75)),
    ("qp", ("x" * 76,), E("length", 75)),
    ("qp", ("x" * 100,), E("length", 75)),
    ("qp", ("x" * 76 + "=\r\ny",), E("length", 75)),
    ("qp", ("ab\r\n" + "x" * 80,), E("length", 79)),
    ("qp", ("x" * 75 + "\r\n" + "y" * 75,), K(b"x" * 75 + b"\r\n" + b"y" * 75)),
    ("qp", ("x" * 75 + "\r\n" + "y" * 75 + "\r\n" + "z" * 76,), E("length", 229)),
    ("qp", ("x" * 73 + "=41" + "y",), E("length", 75)),
    ("qp", ("x" * 72 + "=41",), K(b"x" * 72 + b"A")),
    ("qp", ("x" * 75 + "=\r\ny",), K(b"x" * 75 + b"y")),
]))

check("qp trailing space / tab on a line is rejected", _set([
    ("qp", ("ab ",), E("trailws", 2)),
    ("qp", ("ab\t",), E("trailws", 2)),
    ("qp", ("abc =\r\nd",), E("trailws", 3)),
    ("qp", ("abc\t\r\nd",), E("trailws", 3)),
    ("qp", ("abcd\r\nxyz \r\nq",), E("trailws", 9)),
    ("qp", (" ",), E("trailws", 0)),
    ("qp", (" \r\na",), E("trailws", 0)),
    ("qp", ("a b",), K(b"a b")),
    ("qp", (" a",), K(b" a")),
    ("qp", ("ab=20",), K(b"ab ")),
    # the character scan still beats the trailing-whitespace rule
    ("qp", ("ab \r\n=0a",), E("hex", 7)),
]))

check("qp 'eol', 'trunc' and 'char' cases", _set([
    ("qp", ("=",), E("trunc", 0)),
    ("qp", ("a=",), E("trunc", 1)),
    ("qp", ("a=4",), E("trunc", 1)),
    ("qp", ("=4",), E("trunc", 0)),
    ("qp", ("=41=",), E("trunc", 3)),
    ("qp", ("a\rb",), E("eol", 1)),
    ("qp", ("a\nb",), E("eol", 1)),
    ("qp", ("\n",), E("eol", 0)),
    ("qp", ("a\r",), E("eol", 1)),
    ("qp", ("ab\r\n\n",), E("eol", 4)),
    ("qp", ("a=\r\n",), E("eol", 1)),
    ("qp", ("=\r\n",), E("eol", 0)),
    ("qp", ("a=\rb",), E("eol", 2)),
    ("qp", ("\x00",), E("char", 0)),
    ("qp", ("a\x1fb",), E("char", 1)),
    ("qp", ("abé",), E("char", 2)),
    ("qp", ("=\x7f0",), E("char", 1)),
    ("qp", ("a=\r\nb",), K(b"ab")),
]))

# ==========================================================================
# 26-27: randomised mutation differentials
# ==========================================================================
_WSCH = [" ", "\t", "\n", "\r", "\x0b", "\x0c"]
_JUNK = list("*!$%^&()[]{}<>?,.;:'\"\\|`~#@") + ["\x00", "\x01", "é", "☃"]


def _mutate_bt(rng, text, alpha, other):
    n = len(text)
    op = rng.randrange(10)
    if n == 0:
        op = rng.choice([0, 3, 6])
    if op == 0:
        i = rng.randrange(n + 1)
        return text[:i] + rng.choice(_WSCH) + text[i:]
    if op == 1:
        i = rng.randrange(n)
        return text[:i] + rng.choice(_JUNK) + text[i + 1:]
    if op == 2:
        i = rng.randrange(n)
        return text[:i] + rng.choice(other) + text[i + 1:]
    if op == 3:
        i = rng.randrange(n + 1)
        return text[:i] + "=" + text[i:]
    if op == 4:
        i = rng.randrange(n)
        return text[:i] + text[i + 1:]
    if op == 5:
        return text.replace("=", "", 1) + "="
    if op == 6:
        return text + "=" * rng.randrange(1, 4)
    if op == 7:
        body = text.rstrip("=")
        if not body or body[-1] not in alpha:
            return text + "A"
        i = len(body) - 1
        j = (alpha.index(body[i]) + rng.randrange(1, len(alpha))) % len(alpha)
        return text[:i] + alpha[j] + text[i + 1:]
    if op == 8:
        return text[:rng.randrange(n)]
    i = rng.randrange(n)
    ch = text[i]
    return text[:i] + (ch.lower() if ch.isupper() else ch.upper()) + text[i + 1:]


def mutate_bt(seed, count):
    def probe():
        rng = random.Random(seed)
        for _ in range(count):
            d = bytes(rng.randrange(256) for _ in range(rng.randrange(0, 20)))
            if rng.random() < 0.5:
                us, pad = rng.choice([False, True]), rng.choice([False, True])
                txt = _ora_b64_encode(d, us, pad)
                for _k in range(rng.randrange(1, 3)):
                    txt = _mutate_bt(rng, txt, _ORA_B64U if us else _ORA_B64S,
                                     "+/" if us else "-_")
                if not _dec(B64D, _ora_b64_decode(txt, us, pad), txt, us, pad):
                    return False
            else:
                pad = rng.choice([False, True])
                txt = _ora_b32_encode(d, pad)
                for _k in range(rng.randrange(1, 3)):
                    txt = _mutate_bt(rng, txt, _ORA_B32, "0189abcdefz")
                if not _dec(B32D, _ora_b32_decode(txt, pad), txt, pad):
                    return False
        return True
    return probe


check("randomised mutation differential: base64 / base32 kinds and offsets",
      mutate_bt(31337, 900))


def _gen_qp_text(rng):
    lines = []
    for _ in range(rng.randrange(1, 4)):
        line = ""
        target = rng.randrange(0, 78)
        while len(line) < target:
            r = rng.random()
            if r < 0.55:
                line += chr(rng.randrange(33, 127))
            elif r < 0.7:
                line += rng.choice(" \t")
            else:
                b = rng.randrange(256)
                line += "=" + _ORA_HEX[b // 16] + _ORA_HEX[b % 16]
        if rng.random() < 0.3:
            line += "="
        lines.append(line)
    return "\r\n".join(lines)


def _mutate_qp(rng, text):
    n = len(text)
    op = rng.randrange(9)
    if n == 0:
        op = 0
    if op == 0:
        i = rng.randrange(n + 1)
        return text[:i] + rng.choice([" ", "\t", "=", "\r", "\n", "\r\n", "=\r\n",
                                      "\x00", "\x1f", "é", "=41"]) + text[i:]
    if op == 1:
        i = rng.randrange(n)
        return text[:i] + text[i].lower() + text[i + 1:]
    if op == 2:
        i = rng.randrange(n)
        return text[:i] + text[i + 1:]
    if op == 3:
        return text + rng.choice(["=", "=4", " ", "\t", "\r\n", "=\r\n", "\n", "\r"])
    if op == 4:
        i = rng.randrange(n + 1)
        return text[:i] + "q" * rng.randrange(1, 30) + text[i:]
    if op == 5:
        j = text.find("=\r\n")
        if j < 0:
            return text + " "
        return text[:j] + rng.choice([" ", "\t"]) + text[j:]
    if op == 6:
        i = rng.randrange(n)
        return text[:i] + rng.choice(_JUNK) + text[i + 1:]
    if op == 7:
        return text[:rng.randrange(n)]
    i = rng.randrange(n)
    return text[:i] + "=" + text[i + 1:]


def mutate_qp(seed, count):
    def probe():
        rng = random.Random(seed)
        for _ in range(count):
            if rng.random() < 0.4:
                d = bytes(rng.randrange(256) for _ in range(rng.randrange(0, 90)))
                txt = _ora_qp_encode(d)
            else:
                txt = _gen_qp_text(rng)
            for _k in range(rng.randrange(0, 3)):
                txt = _mutate_qp(rng, txt)
            if not _dec(QPD, _ora_qp_decode(txt), txt):
                return False
        return True
    return probe


check("randomised mutation differential: quoted-printable kinds and offsets",
      mutate_qp(90210, 700))

# ==========================================================================
# 28-29: bans
# ==========================================================================
_BAN_MOD = ("base64", "binascii", "quopri", "codecs", "re", "struct", "email", "uu")
_BAN_NAME = ("hex", "fromhex", "hexlify", "unhexlify", "b64encode", "b64decode",
             "b32encode", "b32decode", "b2a_qp", "a2b_qp", "eval", "exec")


def _toks():
    src = inspect.getsource(strictcodec)
    return [(t.type, t.string) for t in
            tokenize.generate_tokens(io.StringIO(src).readline)]


def no_banned_modules():
    toks = _toks()
    n = len(toks)
    dynamic = any(t[0] == tokenize.NAME and t[1] in ("__import__", "import_module")
                  for t in toks)
    for i in range(n):
        ty, s = toks[i]
        if ty == tokenize.NAME and s in ("import", "from"):
            j = i + 1
            while j < n and toks[j][0] not in (tokenize.NEWLINE, tokenize.ENDMARKER):
                if toks[j][0] == tokenize.NAME and toks[j][1] in _BAN_MOD:
                    return False
                j += 1
        if dynamic and ty == tokenize.STRING and s.strip("bruBRU'\"") in _BAN_MOD:
            return False
    return True


def no_banned_calls():
    toks = _toks()
    for i in range(len(toks) - 1):
        ty, s = toks[i]
        if ty == tokenize.NAME and s in _BAN_NAME:
            if toks[i + 1][0] == tokenize.OP and toks[i + 1][1] == "(":
                return False
    return True


check("strictcodec.py imports no banned module", no_banned_modules)
check("strictcodec.py calls no banned function", no_banned_calls)

_t.cancel()
report()
