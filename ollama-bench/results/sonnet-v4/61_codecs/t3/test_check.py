import strictcodec as sc

def expect_err(fn, *args, kind=None, pos=None, **kwargs):
    try:
        r = fn(*args, **kwargs)
        raise AssertionError(f"expected error, got {r!r}")
    except sc.CodecError as e:
        assert e.kind == kind, f"expected kind={kind}, got {e.kind} (pos={e.pos})"
        if pos is not None:
            assert e.pos == pos, f"expected pos={pos}, got {e.pos} (kind={e.kind})"

# Examples from spec
assert sc.b64_encode(b"hello") == "aGVsbG8="
assert sc.b64_encode(b"hi", urlsafe=True, pad=False) == "aGk"
assert sc.b64_decode("aGVsbG8=") == b"hello"
assert sc.b32_encode(b"hi") == "NBUQ===="
assert sc.qp_encode(b"caf\xc3\xa9") == "caf=C3=A9"
assert sc.qp_decode("a=3Db") == b"a=b"

# round trips
import random
random.seed(1)
for _ in range(200):
    data = bytes(random.randrange(256) for _ in range(random.randrange(0,50)))
    for urlsafe in (False, True):
        for pad in (True, False):
            enc = sc.b64_encode(data, urlsafe=urlsafe, pad=pad)
            assert type(enc) is str
            dec = sc.b64_decode(enc, urlsafe=urlsafe, pad=pad)
            assert dec == data, (data, enc, dec)
    for pad in (True, False):
        enc = sc.b32_encode(data, pad=pad)
        dec = sc.b32_decode(enc, pad=pad)
        assert dec == data, (data, enc, dec)
    enc = sc.qp_encode(data)
    dec = sc.qp_decode(enc)
    assert dec == data, (data, enc, dec)

# type checks precedence
expect_err(sc.b64_encode, bytearray(b"x"), kind="type", pos=-1)
expect_err(sc.b64_encode, "x", kind="type", pos=-1)
expect_err(sc.b64_decode, b"aGk=", kind="type", pos=-1)
expect_err(sc.b32_encode, bytearray(b"x"), kind="type", pos=-1)
expect_err(sc.b32_decode, 5, kind="type", pos=-1)
expect_err(sc.qp_encode, "x", kind="type", pos=-1)
expect_err(sc.qp_decode, b"x", kind="type", pos=-1)

# return types
assert type(sc.b64_encode(b"")) is str
assert type(sc.b64_decode("")) is bytes
assert type(sc.b32_encode(b"")) is str
assert type(sc.b32_decode("")) is bytes
assert type(sc.qp_encode(b"")) is str
assert type(sc.qp_decode("")) is bytes

# base64 whitespace
expect_err(sc.b64_decode, "aGVsbG8=\n", kind="whitespace", pos=8)
expect_err(sc.b64_decode, " aGVsbG8=", kind="whitespace", pos=0)

# base64 alphabet - other alphabet chars
expect_err(sc.b64_decode, "aG-sbG8=", kind="alphabet", pos=2)  # '-' not allowed std
expect_err(sc.b64_decode, "aG+sbG8_", urlsafe=True, kind="alphabet", pos=2)  # '+' not allowed urlsafe... wait check

# padding examples from spec
expect_err(sc.b64_decode, "A===", kind="padding", pos=1)
expect_err(sc.b64_decode, "A=B=", kind="padding", pos=1)
expect_err(sc.b64_decode, "====", kind="padding", pos=0)

# pad=False rejects any '='
expect_err(sc.b64_decode, "aGk=", pad=False, kind="padding", pos=3)

# length
expect_err(sc.b64_decode, "aGV", kind="length", pos=3)  # len%4=3 pad=True... wait 3 chars len=3, %4!=0 -> length at pos=3
expect_err(sc.b64_decode, "a", pad=False, kind="length", pos=1)

# bits leftover: 'aGk=' should be valid (hi). Let's construct invalid bits case.
# 'aGl=' -> decode 3rd char? Let's just test a known bad-bits case: "iZ==" etc. We'll trust round trip tests cover valid cases;
# construct manually: take one data char group of 2 with nonzero low bits.
# alphabet index of 'C' is 2 (000010), low 4 bits nonzero -> "AC==" should error bits at pos1
expect_err(sc.b64_decode, "AC==", kind="bits", pos=1)

# base32 lowercase rejected
expect_err(sc.b32_decode, "nbuq====", kind="alphabet", pos=0)

# base32 padding shapes
# run length must be in (6,4,3,1); length 2 is invalid
expect_err(sc.b32_decode, "AAAAAA==", kind="padding", pos=6)

# qp trailing whitespace
expect_err(sc.qp_decode, "ab \r\ncd", kind="trailws", pos=2)
expect_err(sc.qp_decode, "ab ", kind="trailws", pos=2)

# qp char error
expect_err(sc.qp_decode, "ab\x01cd", kind="char", pos=2)

# qp eol lone \r
expect_err(sc.qp_decode, "ab\rcd", kind="eol", pos=2)
expect_err(sc.qp_decode, "ab\ncd", kind="eol", pos=2)

# qp trunc
expect_err(sc.qp_decode, "ab=", kind="trunc", pos=2)
expect_err(sc.qp_decode, "ab=c", kind="trunc", pos=2)

# qp hex
expect_err(sc.qp_decode, "a=0ab", kind="hex", pos=3)  # =0a -> 'a' lowercase invalid hex at offset of 'a'

# qp soft break with nothing after
expect_err(sc.qp_decode, "ab=\r\n", kind="eol", pos=2)

# qp length (line > 75)
long_content = "a" * 76
expect_err(sc.qp_decode, long_content, kind="length", pos=75)

print("ALL TESTS PASSED")
