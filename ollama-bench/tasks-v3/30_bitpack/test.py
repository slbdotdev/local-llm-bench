import hashlib
import random
import subprocess
import sys

TOTAL = 22
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)


def check_raises(name, fn, exc=ValueError):
    def probe():
        try:
            fn()
        except exc:
            return True
        except Exception:
            return False
        return False
    check(name, probe)


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:12])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


# --- the visible test file (2) -----------------------------------------
def visible_untouched():
    with open("test_bitpack.py", "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    return h == "f2818a843de66a0e3d9e150c27bc2b18d0c09838ec1144ea4dd5ca4bcd82299b"


def visible_pass():
    r = subprocess.run([sys.executable, "test_bitpack.py"], capture_output=True,
                       text=True, timeout=30)
    return r.returncode == 0 and "ALL OK" in r.stdout


check("visible tests untouched", visible_untouched)
check("visible tests pass", visible_pass)

try:
    import bitpack
except Exception as e:
    fails += ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - len(fails) - 1)
    report()


def _missing(*a, **k):
    raise AttributeError("attribute missing from bitpack")


pack = getattr(bitpack, "pack", _missing)
unpack = getattr(bitpack, "unpack", _missing)

# --- extra vectors (8) -------------------------------------------------
check("pack 2-bit", lambda: pack(2, [1, 2, 3]) == b"\x6c")
check("pack 32-bit", lambda: pack(32, [1]) == b"\x00\x00\x00\x01")
check("pack signed -8 w4", lambda: pack(4, [-8], True) == b"\x80")
check("pack signed -1,1 w4", lambda: pack(4, [-1, 1], True) == b"\xf1")
check("unpack leftover ones", lambda: unpack(5, b"\xff\xff") == [31, 31, 31])
check("unpack sign ext w4", lambda: unpack(4, b"\x80", True) == [-8, 0])
check("unpack sign ext w4 pair", lambda: unpack(4, b"\x87", True) == [-8, 7])
check("unsigned max w4", lambda: pack(4, [15]) == b"\xf0")

# --- width validation (5) ----------------------------------------------
for badw in [0, -2, 33, "4"]:
    check_raises("pack width %r rejected" % (badw,), lambda badw=badw: pack(badw, [0]))
check_raises("unpack width 0 rejected", lambda: unpack(0, b"\x00"))

# --- value validation (5) ----------------------------------------------
for badv, w, sg in [([16], 4, False), ([-1], 4, False), ([-129], 8, True),
                    ([128], 8, True), ([1.5], 4, False)]:
    check_raises("pack value %r rejected" % (badv,),
                 lambda badv=badv, w=w, sg=sg: pack(w, badv, sg))

# --- seeded differential against an independent reference (2) ----------


def ref_pack(width, values, signed=False):
    stream = 0
    for v in values:
        if signed and v < 0:
            v += 1 << width
        stream = (stream << width) | v
    total = len(values) * width
    pad = (8 - total % 8) % 8
    stream <<= pad
    return stream.to_bytes((total + pad) // 8, "big")


random.seed(3030)
widths = [1, 3, 4, 7, 8, 11, 16, 31, 32]
bad_pack = bad_rt = 0
trials = 0
for i in range(150):
    w = widths[i % len(widths)]
    signed = (i % 3) != 0
    k = random.randint(0, 6)
    if signed:
        vals = [random.randint(-(2 ** (w - 1)), 2 ** (w - 1) - 1) for _ in range(k)]
    else:
        vals = [random.randint(0, 2 ** w - 1) for _ in range(k)]
    try:
        got = pack(w, vals, signed)
        want = ref_pack(w, vals, signed)
        trials += 1
        if got != want:
            bad_pack += 1
        if unpack(w, want, signed)[: len(vals)] != vals:
            bad_rt += 1
    except Exception:
        bad_pack += 1
        bad_rt += 1

check("differential pack", lambda: trials > 140 and bad_pack == 0)
check("differential unpack", lambda: trials > 140 and bad_rt == 0)

report()
