#!/usr/bin/env python3
"""Test wirefmt implementation."""

from wirefmt import encode, decode, canon, WireError

def test_encode():
    """Test encoding."""
    # Test 1
    result = encode(["a b", "", "~", "x,y"])
    expected = r"(a b,~,\~,x\,y)"
    assert result == expected, f"Expected {expected!r}, got {result!r}"
    print(f"OK encode test 1: {result!r}")

    # Test 2
    result = encode([[], ["\n"], "é"])
    expected = r"((),(\x0a),é)"
    assert result == expected, f"Expected {expected!r}, got {result!r}"
    print(f"OK encode test 2: {result!r}")

    # Test 3
    result = encode([])
    expected = "()"
    assert result == expected, f"Expected {expected!r}, got {result!r}"
    print(f"OK encode test 3: {result!r}")

    # Test empty string
    result = encode("")
    expected = "~"
    assert result == expected, f"Expected {expected!r}, got {result!r}"
    print(f"OK encode test 4 (empty string): {result!r}")

    # Test tilde
    result = encode("~")
    expected = r"\~"
    assert result == expected, f"Expected {expected!r}, got {result!r}"
    print(f"OK encode test 5 (tilde): {result!r}")


def test_decode():
    """Test decoding."""
    # Test 1
    result = decode(r"((),(\x0A),\X41,\a)")
    expected = [[], ["\n"], "X41", "a"]
    assert result == expected, f"Expected {expected!r}, got {result!r}"
    print(f"OK decode test 1: {result!r}")

    # Test 2
    result = decode(r"(a\)b)")
    expected = ["a)b"]
    assert result == expected, f"Expected {expected!r}, got {result!r}"
    print(f"OK decode test 2: {result!r}")

    # Test 3: empty atom with tilde
    result = decode("~")
    expected = ""
    assert result == expected, f"Expected {expected!r}, got {result!r}"
    print(f"OK decode test 3 (empty atom): {result!r}")

    # Test 4: empty list
    result = decode("()")
    expected = []
    assert result == expected, f"Expected {expected!r}, got {result!r}"
    print(f"OK decode test 4 (empty list): {result!r}")


def test_canon():
    """Test canonicalization."""
    result = canon(r"(\x41,\a,a(b,~)")
    expected = r"(A,a,a\(b,~)"
    assert result == expected, f"Expected {expected!r}, got {result!r}"
    print(f"OK canon test: {result!r}")


def test_errors():
    """Test error handling."""
    # Test empty atom at start
    try:
        decode(",")
        assert False, "Should raise WireError"
    except WireError as e:
        assert e.kind == "empty" and e.pos == 0, f"Expected empty@0, got {e.kind}@{e.pos}"
        print(f"OK error test 1: {e.kind}@{e.pos}")

    # Test unterminated list
    try:
        decode("(a,")
        assert False, "Should raise WireError"
    except WireError as e:
        assert e.kind == "empty" and e.pos == 3, f"Expected empty@3, got {e.kind}@{e.pos}"
        print(f"OK error test 2: {e.kind}@{e.pos}")

    # Test empty after opening paren
    try:
        decode("(")
        assert False, "Should raise WireError"
    except WireError as e:
        assert e.kind == "empty" and e.pos == 1, f"Expected empty@1, got {e.kind}@{e.pos}"
        print(f"OK error test 3: {e.kind}@{e.pos}")

    # Test tilde error
    try:
        decode(r"(~a,\xzz)")
        assert False, "Should raise WireError"
    except WireError as e:
        # Should report tilde before escape because same pos, tilde has higher precedence
        # Actually wait, the tilde is at position 1, escape is at position 5
        # So it should report tilde at 1
        assert e.kind == "tilde" and e.pos == 1, f"Expected tilde@1, got {e.kind}@{e.pos}"
        print(f"OK error test 4: {e.kind}@{e.pos}")

    # Test escape error
    try:
        decode(r"(\xzz,~a)")
        assert False, "Should raise WireError"
    except WireError as e:
        # escape at 1, tilde at 6, so report escape
        assert e.kind == "escape" and e.pos == 1, f"Expected escape@1, got {e.kind}@{e.pos}"
        print(f"OK error test 5: {e.kind}@{e.pos}")

    # Test depth error
    try:
        # Create deeply nested structure - we'll need to build this carefully
        # Let's create a list 201 levels deep
        text = "(" * 201
        decode(text)
        assert False, "Should raise WireError"
    except WireError as e:
        # The 201st opening paren should trigger depth error
        assert e.kind == "depth" and e.pos == 200, f"Expected depth@200, got {e.kind}@{e.pos}"
        print(f"OK error test 6: {e.kind}@{e.pos}")


if __name__ == "__main__":
    print("Testing encode...")
    test_encode()
    print("\nTesting decode...")
    test_decode()
    print("\nTesting canon...")
    test_canon()
    print("\nTesting errors...")
    test_errors()
    print("\nOK All tests passed!")
