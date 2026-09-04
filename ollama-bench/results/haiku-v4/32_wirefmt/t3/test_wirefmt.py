#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from wirefmt import encode, decode, canon, WireError

def test_encode():
    print("Testing encode...")

    result = encode(["a b", "", "~", "x,y"])
    expected = r"(a b,~,\~,x\,y)"
    print(f"encode(['a b', '', '~', 'x,y']) = {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Mismatch: {result} != {expected}"

    result = encode([[], ["\n"], "é"])
    expected = r"((),(\x0a),é)"
    print(f"encode([[], ['\\n'], 'é']) = {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Mismatch: {result} != {expected}"

    result = encode([])
    expected = "()"
    print(f"encode([]) = {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Mismatch: {result} != {expected}"

    print("encode tests passed!\n")

def test_decode():
    print("Testing decode...")

    result = decode(r"((),(\x0A),\X41,\a)")
    expected = [[], ["\n"], "X41", "a"]
    print(f"decode(r'((),(...))') = {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Mismatch: {result} != {expected}"

    result = decode(r"(a\)b)")
    expected = ["a)b"]
    print(f"decode(r'(a\\)b)') = {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Mismatch: {result} != {expected}"

    print("decode tests passed!\n")

def test_canon():
    print("Testing canon...")

    result = canon(r"(\x41,\a,a(b,~)")
    expected = r"(A,a,a\(b,~)"
    print(f"canon(r'(\\x41,\\a,a(b,~)') = {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Mismatch: {result} != {expected}"

    print("canon tests passed!\n")

def test_roundtrip():
    print("Testing roundtrip (canon idempotent)...")

    t = r"(\x41,\a,a(b,~)"
    c1 = canon(t)
    c2 = canon(c1)
    print(f"canon(t) = {c1}")
    print(f"canon(canon(t)) = {c2}")
    assert c1 == c2, f"Not idempotent: {c1} != {c2}"

    print("Roundtrip test passed!\n")

def test_errors():
    print("Testing error handling...")

    # Test "empty" error
    try:
        decode(",")
        assert False, "Should have raised WireError"
    except WireError as e:
        print(f"decode(',') raised {e.kind} at {e.pos}")
        assert e.kind == "empty" and e.pos == 0

    # Test "empty" at position 3
    try:
        decode("(a,")
        assert False, "Should have raised WireError"
    except WireError as e:
        print(f"decode('(a,') raised {e.kind} at {e.pos}")
        assert e.kind == "empty" and e.pos == 3

    # Test "empty" at position 1
    try:
        decode("(")
        assert False, "Should have raised WireError"
    except WireError as e:
        print(f"decode('(') raised {e.kind} at {e.pos}")
        assert e.kind == "empty" and e.pos == 1

    # Test precedence: tilde at 1 vs empty at 3
    try:
        decode(r"(~a,\xzz)")
        assert False, "Should have raised WireError"
    except WireError as e:
        print(f"decode(r'(~a,\\xzz)') raised {e.kind} at {e.pos}")
        assert e.kind == "tilde" and e.pos == 1

    # Test precedence: escape at 1 vs tilde at 5
    try:
        decode(r"(\xzz,~a)")
        assert False, "Should have raised WireError"
    except WireError as e:
        print(f"decode(r'(\\xzz,~a)') raised {e.kind} at {e.pos}")
        assert e.kind == "escape" and e.pos == 1

    print("Error tests passed!\n")

if __name__ == '__main__':
    test_encode()
    test_decode()
    test_canon()
    test_roundtrip()
    test_errors()
    print("All tests passed!")
