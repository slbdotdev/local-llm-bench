import sys, os, random, threading, inspect, ast

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
    import bencode
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


def _missing(*a, **k):
    raise AttributeError("attribute missing from bencode")


ENC = getattr(bencode, "encode", _missing)
DEC = getattr(bencode, "decode", _missing)
BE = getattr(bencode, "BencodeError", None)


# ===================== inlined independent oracle =====================

_O_DEPTH = 32
_O_MIN = -(2 ** 63)
_O_MAX = 2 ** 63 - 1
_O_MAXLEN = 2 ** 31 - 1


class _OErr(Exception):
    def __init__(self, kind, offset=None):
        Exception.__init__(self, kind)
        self.kind = kind
        self.offset = offset


def _o_encode(obj):
    buf = bytearray()
    _o_enc(obj, 1, buf)
    return bytes(buf)


def _o_enc(o, depth, buf):
    if type(o) is bool:
        raise _OErr("bool")
    if type(o) is int:
        if not (_O_MIN <= o <= _O_MAX):
            raise _OErr("range")
        buf.extend(b"i")
        buf.extend(("%d" % o).encode("ascii"))
        buf.extend(b"e")
        return
    if type(o) is bytes:
        buf.extend(("%d" % len(o)).encode("ascii"))
        buf.extend(b":")
        buf.extend(o)
        return
    if type(o) is list:
        if depth > _O_DEPTH:
            raise _OErr("depth")
        buf.extend(b"l")
        for it in o:
            _o_enc(it, depth + 1, buf)
        buf.extend(b"e")
        return
    if type(o) is dict:
        if depth > _O_DEPTH:
            raise _OErr("depth")
        ks = list(o.keys())
        for k in ks:
            if type(k) is not bytes:
                raise _OErr("key_type")
        buf.extend(b"d")
        ks.sort()
        for k in ks:
            buf.extend(("%d" % len(k)).encode("ascii"))
            buf.extend(b":")
            buf.extend(k)
            _o_enc(o[k], depth + 1, buf)
        buf.extend(b"e")
        return
    raise _OErr("type")


def _o_isdig(b):
    return 48 <= b <= 57


def _o_decode(data):
    if type(data) is not bytes:
        raise _OErr("type", 0)
    v, end = _o_val(data, 0, 1)
    if end != len(data):
        raise _OErr("trailing", end)
    return v


def _o_val(d, i, depth):
    n = len(d)
    if i >= n:
        raise _OErr("truncated", n)
    h = d[i]
    if h == 105:                                   # b'i'
        j = i + 1
        while j < n and d[j] != 101:
            j += 1
        if j >= n:
            raise _OErr("truncated", n)
        k = i + 1
        if k < j and d[k] == 45:
            k = i + 2
        if k >= j:
            raise _OErr("syntax", k)
        q = k
        while q < j:
            if not _o_isdig(d[q]):
                raise _OErr("syntax", q)
            q += 1
        if (j - k) > 1 and d[k] == 48:
            raise _OErr("leading_zero", k)
        if k == i + 2 and d[k] == 48:
            raise _OErr("negative_zero", i + 1)
        if (j - k) > 19:
            raise _OErr("range", i)
        val = int(d[i + 1:j].decode("ascii"))
        if not (_O_MIN <= val <= _O_MAX):
            raise _OErr("range", i)
        return val, j + 1
    if _o_isdig(h):
        j = i
        while j < n and d[j] != 58:                # b':'
            j += 1
        if j >= n:
            raise _OErr("truncated", n)
        q = i
        while q < j:
            if not _o_isdig(d[q]):
                raise _OErr("syntax", q)
            q += 1
        if (j - i) > 1 and d[i] == 48:
            raise _OErr("leading_zero", i)
        if (j - i) > 10:
            raise _OErr("range", i)
        ln = int(d[i:j].decode("ascii"))
        if ln > _O_MAXLEN:
            raise _OErr("range", i)
        if j + 1 + ln > n:
            raise _OErr("truncated", n)
        return d[j + 1:j + 1 + ln], j + 1 + ln
    if h == 108:                                   # b'l'
        if depth > _O_DEPTH:
            raise _OErr("depth", i)
        acc = []
        p = i + 1
        while True:
            if p >= n:
                raise _OErr("truncated", n)
            if d[p] == 101:
                return acc, p + 1
            item, p = _o_val(d, p, depth + 1)
            acc.append(item)
    if h == 100:                                   # b'd'
        if depth > _O_DEPTH:
            raise _OErr("depth", i)
        acc = {}
        last = None
        p = i + 1
        while True:
            if p >= n:
                raise _OErr("truncated", n)
            c = d[p]
            if c == 101:
                return acc, p + 1
            if c == 105 or c == 108 or c == 100:
                raise _OErr("key_type", p)
            if not _o_isdig(c):
                raise _OErr("syntax", p)
            key, p2 = _o_val(d, p, depth + 1)
            if last is not None:
                if key == last:
                    raise _OErr("duplicate_key", p)
                if key < last:
                    raise _OErr("key_order", p)
            last = key
            acc[key], p = _o_val(d, p2, depth + 1)
    raise _OErr("syntax", i)


# ===================== helpers =====================

def _same(a, b):
    """Deep equality that also demands identical Python types."""
    if type(a) is not type(b):
        return False
    if type(a) is list:
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if type(a) is dict:
        if len(a) != len(b):
            return False
        ka, kb = sorted(a.keys()), sorted(b.keys())
        if ka != kb:
            return False
        return all(_same(a[k], b[k]) for k in ka)
    return a == b


def dec_out(data):
    """Candidate decode outcome as a comparable tuple."""
    try:
        return ("ok", DEC(data))
    except Exception as e:
        if isinstance(BE, type) and isinstance(e, BE):
            return ("err", getattr(e, "kind", "<no .kind>"),
                    getattr(e, "offset", "<no .offset>"))
        return ("wrong-exc", type(e).__name__, None)


def o_dec_out(data):
    try:
        return ("ok", _o_decode(data))
    except _OErr as e:
        return ("err", e.kind, e.offset)


def enc_out(obj):
    try:
        return ("ok", ENC(obj))
    except Exception as e:
        if isinstance(BE, type) and isinstance(e, BE):
            return ("err", getattr(e, "kind", "<no .kind>"),
                    getattr(e, "offset", "<no .offset>"))
        return ("wrong-exc", type(e).__name__, None)


def dkind(data):
    o = dec_out(data)
    return o[1] if o[0] == "err" else ("<%s>" % o[0])


def dpair(data):
    o = dec_out(data)
    return (o[1], o[2]) if o[0] == "err" else ("<%s>" % o[0], None)


def ekind(obj):
    o = enc_out(obj)
    return o[1] if o[0] == "err" else ("<%s>" % o[0])


def epair(obj):
    o = enc_out(obj)
    return (o[1], o[2]) if o[0] == "err" else ("<%s>" % o[0], None)


def all_dkinds(pairs):
    def probe():
        for data, want in pairs:
            if dkind(data) != want:
                return False
        return True
    return probe


def all_dpairs(pairs):
    def probe():
        for data, want in pairs:
            if dpair(data) != want:
                return False
        return True
    return probe


def all_ekinds(pairs):
    def probe():
        for obj, want in pairs:
            if ekind(obj) != want:
                return False
        return True
    return probe


def rand_obj(rng, depth):
    r = rng.random()
    if depth >= 4 or r < 0.42:
        if rng.random() < 0.5:
            if rng.random() < 0.35:
                return rng.choice([0, 1, -1, 9, -9, 10, -10, 255, -256,
                                   10 ** 12, -(10 ** 12), 2 ** 63 - 1, -(2 ** 63)])
            return rng.randint(-100000, 100000)
        return bytes(rng.randrange(256) for _ in range(rng.randint(0, 6)))
    if r < 0.72:
        return [rand_obj(rng, depth + 1) for _ in range(rng.randint(0, 4))]
    d = {}
    for _ in range(rng.randint(0, 4)):
        kl = rng.randint(0, 3)
        k = bytes(rng.choice([0x61, 0x62, 0xFF, 0x30, 0x80, 0x7A])
                  for _ in range(kl))
        d[k] = rand_obj(rng, depth + 1)
    return d


_rng = random.Random(20260903)
CORPUS = [rand_obj(_rng, 0) for _ in range(320)]
CANON = [_o_encode(x) for x in CORPUS]


def nest(n, kind):
    v = 7
    for _ in range(n):
        v = [v] if kind == "l" else {b"k": v}
    return v


# ===================== 1: API =====================

check("BencodeError subclasses Exception; encode/decode present",
      lambda: isinstance(BE, type) and issubclass(BE, Exception)
      and callable(ENC) and callable(DEC))

# ===================== 2-7: encode on valid input =====================

check("encode integers canonically",
      lambda: ENC(0) == b"i0e" and ENC(1) == b"i1e" and ENC(-1) == b"i-1e"
      and ENC(42) == b"i42e" and ENC(-42) == b"i-42e"
      and ENC(1000) == b"i1000e" and ENC(-1000) == b"i-1000e"
      and type(ENC(0)) is bytes)
check("encode byte strings canonically",
      lambda: ENC(b"") == b"0:" and ENC(b"a") == b"1:a"
      and ENC(b"spam") == b"4:spam"
      and ENC(b"\x00\xff:e") == b"4:\x00\xff:e"
      and ENC(b"x" * 100) == b"100:" + b"x" * 100)
check("encode lists canonically",
      lambda: ENC([]) == b"le" and ENC([1]) == b"li1ee"
      and ENC([b"a", 3]) == b"l1:ai3ee"
      and ENC([[], [[]]]) == b"llelleee")
check("encode dicts canonically, keys sorted by raw unsigned byte value",
      lambda: ENC({}) == b"de"
      and ENC({b"b": 1, b"a": 2}) == b"d1:ai2e1:bi1ee"
      and ENC({b"a": 1, b"": 2}) == b"d0:i2e1:ai1ee"
      and ENC({b"ab": 1, b"a": 2}) == b"d1:ai2e2:abi1ee"
      and ENC({b"\xff": 1, b"~": 2}) == b"d1:~i2e1:\xffi1ee"
      and ENC({b"B": 1, b"a": 2}) == b"d1:Bi1e1:ai2ee")
check("encode nested structures",
      lambda: ENC({b"cow": b"moo", b"spam": [b"a", {b"z": 1}]})
      == b"d3:cow3:moo4:spaml1:ad1:zi1eeee"
      and ENC([{}, [], b"", 0]) == b"ldele0:i0ee")
check("encode 64-bit boundary integers",
      lambda: ENC(2 ** 63 - 1) == b"i9223372036854775807e"
      and ENC(-(2 ** 63)) == b"i-9223372036854775808e")
check("encode nesting exactly at the depth limit (32)",
      lambda: ENC(nest(32, "l")) == b"l" * 32 + b"i7e" + b"e" * 32
      and ENC(nest(32, "d")) == b"d1:k" * 32 + b"i7e" + b"e" * 32)

# ===================== 8-13: decode on valid input =====================

check("decode integers",
      lambda: DEC(b"i0e") == 0 and DEC(b"i-1e") == -1 and DEC(b"i42e") == 42
      and DEC(b"i-9223372036854775808e") == -(2 ** 63)
      and DEC(b"i9223372036854775807e") == 2 ** 63 - 1
      and type(DEC(b"i0e")) is int)
check("decode byte strings",
      lambda: DEC(b"0:") == b"" and DEC(b"1:a") == b"a"
      and DEC(b"3:i0e") == b"i0e" and DEC(b"4:\x00\xff:e") == b"\x00\xff:e"
      and type(DEC(b"1:a")) is bytes)
check("decode lists",
      lambda: DEC(b"le") == [] and DEC(b"li1ee") == [1]
      and DEC(b"l1:ai3ee") == [b"a", 3] and type(DEC(b"le")) is list)
check("decode dicts",
      lambda: DEC(b"de") == {} and DEC(b"d0:i2e1:ai1ee") == {b"": 2, b"a": 1}
      and DEC(b"d3:cow3:moo4:spam4:eggse")
      == {b"cow": b"moo", b"spam": b"eggs"}
      and type(DEC(b"de")) is dict)
check("decode nested and empty containers",
      lambda: DEC(b"li0eli1eee") == [0, [1]]
      and DEC(b"ldele0:i0ee") == [{}, [], b"", 0]
      and DEC(b"d1:al1:be1:bdee") == {b"a": [b"b"], b"b": {}})
check("decode nesting exactly at the depth limit (32)",
      lambda: DEC(b"l" * 32 + b"i7e" + b"e" * 32) == nest(32, "l")
      and DEC(b"d1:k" * 32 + b"i7e" + b"e" * 32) == nest(32, "d"))

# ===================== 14-18: randomised differential (valid) ==========


def diff_encode():
    for obj, want in zip(CORPUS, CANON):
        if ENC(obj) != want:
            return False
    return True


def diff_decode():
    for obj, data in zip(CORPUS, CANON):
        if not _same(DEC(data), obj):
            return False
    return True


def diff_roundtrip():
    for obj in CORPUS:
        if not _same(DEC(ENC(obj)), obj):
            return False
    return True


def diff_reencode():
    for data in CANON:
        if ENC(DEC(data)) != data:
            return False
    return True


def diff_types():
    """Decoded byte strings are bytes (never str), ints never bool."""
    for data in CANON:
        got = DEC(data)
        stack = [got]
        while stack:
            v = stack.pop()
            if type(v) is list:
                stack.extend(v)
            elif type(v) is dict:
                for k in v:
                    if type(k) is not bytes:
                        return False
                stack.extend(v.values())
            elif type(v) is not bytes and type(v) is not int:
                return False
            elif type(v) is bool:
                return False
    return True


check("randomised differential: encode matches the reference (320 objects)",
      diff_encode)
check("randomised differential: decode matches the reference (320 encodings)",
      diff_decode)
check("randomised differential: decode(encode(x)) == x with identical types",
      diff_roundtrip)
check("randomised differential: encode(decode(d)) == d on canonical data",
      diff_reencode)
check("decoded values use exactly int/bytes/list/dict", diff_types)

# ===================== 19-22: encode strictness =====================

check("encode rejects bool with kind 'bool', anywhere in the object",
      all_ekinds([(True, "bool"), (False, "bool"), ([True], "bool"),
                  ([1, [2, False]], "bool"), ({b"a": True}, "bool"),
                  ({b"a": [1, True]}, "bool")]))
check("encode rejects other types with kind 'type', out-of-range ints with 'range'",
      all_ekinds([("spam", "type"), (bytearray(b"a"), "type"),
                  (memoryview(b"a"), "type"), ((1, 2), "type"),
                  ({1, 2}, "type"), (1.0, "type"), (None, "type"),
                  ([b"a", "b"], "type"), ({b"a": None}, "type"),
                  (2 ** 63, "range"), (-(2 ** 63) - 1, "range"),
                  ([10 ** 30], "range"), ({b"a": 2 ** 63}, "range")]))


def enc_keys():
    if ekind({1: b"v"}) != "key_type":
        return False
    if ekind({b"a": 1, "b": 2}) != "key_type":
        return False
    if ekind({b"a": 1, None: 2}) != "key_type":
        return False
    # every key is checked before any value is encoded
    if ekind({b"z": True, 5: b"x"}) != "key_type":
        return False
    # values are visited in sorted key order, so b"a"'s error wins
    if ekind({b"b": True, b"a": "s"}) != "type":
        return False
    if ekind({b"b": "s", b"a": True}) != "bool":
        return False
    return True


check("encode key_type, and keys checked before values / values in sorted order",
      enc_keys)


def enc_depth():
    if ekind(nest(33, "l")) != "depth":
        return False
    if ekind(nest(33, "d")) != "depth":
        return False
    if ekind(nest(40, "l")) != "depth":
        return False
    # an int or bytes at depth 33 is fine
    if ENC(nest(32, "l")) != b"l" * 32 + b"i7e" + b"e" * 32:
        return False
    # every encode error carries .offset None
    for obj in (True, "s", 2 ** 63, {1: 2}, nest(33, "l"), [b"a", 4.0]):
        if epair(obj)[1] is not None:
            return False
    return True


check("encode depth limit is 32, and every encode error has .offset None",
      enc_depth)

# ===================== 23-28: decode strictness =====================

check("decode rejects non-bytes input with kind 'type' at offset 0, "
      "and over-long lengths/ints with 'range'",
      all_dpairs([("li1ee", ("type", 0)), (bytearray(b"le"), ("type", 0)),
                  (memoryview(b"le"), ("type", 0)), (None, ("type", 0)),
                  (5, ("type", 0)),
                  (b"i9223372036854775808e", ("range", 0)),
                  (b"i-9223372036854775809e", ("range", 0)),
                  (b"l" + b"i99999999999999999999e" + b"e", ("range", 1)),
                  (b"99999999999:x", ("range", 0)),
                  (b"3000000000:x", ("range", 0))]))
check("decode rejects leading zeros and -0, with the stated precedence",
      all_dpairs([(b"i03e", ("leading_zero", 1)),
                  (b"i00e", ("leading_zero", 1)),
                  (b"i-01e", ("leading_zero", 2)),
                  (b"i-00e", ("leading_zero", 2)),
                  (b"i-0e", ("negative_zero", 1)),
                  (b"li-0ee", ("negative_zero", 2)),
                  (b"01:a", ("leading_zero", 0)),
                  (b"00:", ("leading_zero", 0)),
                  (b"l01:ae", ("leading_zero", 1)),
                  (b"d02:abi0ee", ("leading_zero", 1))]))
check("decode syntax errors report the right offset",
      all_dpairs([(b"ie", ("syntax", 1)), (b"i-e", ("syntax", 2)),
                  (b"i1x2e", ("syntax", 2)), (b"i1-2e", ("syntax", 2)),
                  (b"i--1e", ("syntax", 2)),
                  (b"x", ("syntax", 0)), (b"e", ("syntax", 0)),
                  (b"lxe", ("syntax", 1)),
                  (b"12a:xxx", ("syntax", 2)),
                  (b"d1:ae", ("syntax", 4)),
                  (b"li1e:e", ("syntax", 4))]))
check("decode trailing data and truncation report the right offset",
      all_dpairs([(b"i1ee", ("trailing", 3)), (b"lee", ("trailing", 2)),
                  (b"0:x", ("trailing", 2)), (b"dei0e", ("trailing", 2)),
                  (b"1:ab", ("trailing", 3)),
                  (b"", ("truncated", 0)), (b"i12", ("truncated", 3)),
                  (b"3:ab", ("truncated", 4)), (b"l", ("truncated", 1)),
                  (b"li1e", ("truncated", 4)), (b"d1:a", ("truncated", 4)),
                  (b"d1:ai1e", ("truncated", 7)), (b"12", ("truncated", 2))]))
check("decode dict key errors: key_type, duplicate_key, key_order",
      all_dpairs([(b"di0ei1ee", ("key_type", 1)),
                  (b"dlei1ee", ("key_type", 1)),
                  (b"ddei1ee", ("key_type", 1)),
                  (b"d1:ai0ei1ei2ee", ("key_type", 7)),
                  (b"d1:ai0e1:ai1ee", ("duplicate_key", 7)),
                  (b"d0:i0e0:i1ee", ("duplicate_key", 6)),
                  (b"d1:bi0e1:ai1ee", ("key_order", 7)),
                  (b"d2:abi0e1:ai1ee", ("key_order", 8)),
                  (b"d1:\xffi0e1:ai1ee", ("key_order", 7)),
                  (b"d1:ai0e0:i1ee", ("key_order", 7)),
                  (b"dxi0ee", ("syntax", 1))]))
check("decode depth limit is 32",
      all_dpairs([(b"l" * 33 + b"e" * 33, ("depth", 32)),
                  (b"d1:k" * 33 + b"e" * 33, ("depth", 128)),
                  (b"l" * 40 + b"e" * 40, ("depth", 32))]))

# ===================== 29-30: randomised mutation differential ========

MUTS = []
_mr = random.Random(7717)
for _base in CANON[:200]:
    for _ in range(3):
        b = bytearray(_base)
        op = _mr.randrange(6)
        if not b:
            b = bytearray(b"le")
        p = _mr.randrange(len(b))
        if op == 0:
            del b[p:]
        elif op == 1:
            b[p] = _mr.randrange(256)
        elif op == 2:
            b.insert(p, _mr.choice(b"0123456789ilde:-x"))
        elif op == 3:
            del b[p]
        elif op == 4:
            b.extend(bytes([_mr.choice(b"e0i:l")]))
        else:
            b.insert(p, 48)
        MUTS.append(bytes(b))


def mut_kind():
    for data in MUTS:
        want = o_dec_out(data)
        got = dec_out(data)
        if want[0] == "ok":
            if got[0] != "ok" or not _same(got[1], want[1]):
                return False
        else:
            if got[0] != "err" or got[1] != want[1]:
                return False
    return True


def mut_offset():
    for data in MUTS:
        want = o_dec_out(data)
        got = dec_out(data)
        if want[0] == "ok":
            if got[0] != "ok" or not _same(got[1], want[1]):
                return False
        else:
            if got[0] != "err" or got[1] != want[1] or got[2] != want[2]:
                return False
    return True


check("randomised mutation differential: same outcome and error kind (600 cases)",
      mut_kind)
check("randomised mutation differential: same error offset too (600 cases)",
      mut_offset)

# ===================== bans =====================

BANNED_MODS = ("bencodepy", "pickle", "json", "ast")
BANNED_NAMES = ("eval", "exec")


def _src():
    try:
        return inspect.getsource(bencode)
    except Exception:
        try:
            with open(getattr(bencode, "__file__", ""), "r",
                      encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except Exception:
            return ""


def bans():
    src = _src()
    if not src.strip():
        return False
    try:
        tree = ast.parse(src)
    except Exception:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in BANNED_MODS:
                    return False
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in BANNED_MODS:
                return False
        elif isinstance(node, ast.Name):
            if node.id in BANNED_NAMES or node.id == "__import__":
                return False
        elif isinstance(node, ast.Attribute):
            if node.attr in BANNED_NAMES:
                return False
    for m in BANNED_MODS:
        if getattr(bencode, m, None) is not None:
            return False
    return True


check("no banned module (bencodepy/pickle/json/ast) and no eval/exec", bans)

_t.cancel()
report()
