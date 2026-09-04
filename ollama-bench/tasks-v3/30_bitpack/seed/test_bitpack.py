import sys

from bitpack import pack, unpack

fails = []


def check(name, cond):
    if not cond:
        fails.append(name)
        print("FAIL:", name)


check("4-bit vector", pack(4, [0b1010, 0b0011]) == b"\xa3")
check("4-bit unpack", unpack(4, b"\xa3") == [10, 3])
check("1-bit pack", pack(1, [1, 0, 1]) == b"\xa0")
check("1-bit unpack", unpack(1, b"\xa0") == [1, 0, 1, 0, 0, 0, 0, 0])
check("12-bit vector", pack(12, [0xABC, 0xDEF]) == b"\xab\xcd\xef")
check("2-bit pack", pack(2, [1, 2, 3]) == b"\x6c")
check("8-bit signed -1 pack", pack(8, [-1], True) == b"\xff")
check("8-bit signed -1 unpack", unpack(8, b"\xff", True) == [-1])
check("signed min pack", pack(8, [-128], True) == b"\x80")
check("signed min unpack", unpack(8, b"\x80", True) == [-128])
check(
    "roundtrip 11-bit signed",
    unpack(11, pack(11, [0, 1, 1023, -1024, -1], True), True) == [0, 1, 1023, -1024, -1],
)
check("unpack ignores padding", unpack(3, b"\xff") == [7, 7])
check("unpack ignores zero padding", unpack(3, b"\xa0") == [5, 0])
check("empty pack", pack(4, []) == b"")
check("empty unpack", unpack(4, b"") == [])

try:
    pack(4, [16])
    check("unsigned 2**width rejected", False)
except ValueError:
    check("unsigned 2**width rejected", True)

try:
    pack(0, [0])
    check("width 0 rejected", False)
except ValueError:
    check("width 0 rejected", True)

try:
    pack(33, [0])
    check("width 33 rejected", False)
except ValueError:
    check("width 33 rejected", True)

if fails:
    print(f"{len(fails)} failing")
    sys.exit(1)
print("ALL OK")
