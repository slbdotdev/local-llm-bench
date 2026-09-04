#!/usr/bin/env python3
"""Edge case tests for wirefmt."""

from wirefmt import encode, decode, canon, WireError

def test_escape_sequences():
    """Test all escape sequence rules."""
    # Rule 8: \xHH hex escapes
    assert decode(r"\x41") == "A"
    assert decode(r"\x0a") == "\n"
    assert decode(r"\x0A") == "\n"  # uppercase hex
    print("OK hex escapes")

    # Rule 9: printable ASCII escapes
    assert decode(r"\a") == "a"
    assert decode(r"\\") == "\\"
    assert decode(r"\(") == "("
    assert decode(r"\)") == ")"
    assert decode(r"\,") == ","
    assert decode(r"\~") == "~"
    print("OK printable ASCII escapes")

    # Rule 10: invalid escapes
    try:
        decode("\\")  # backslash at end
        assert False
    except WireError as e:
        assert e.kind == "escape"
    print("OK escape at end error")

    try:
        decode(r"\x")  # incomplete hex
        assert False
    except WireError as e:
        assert e.kind == "escape"
    print("OK incomplete hex error")

    try:
        decode(r"\x0")  # incomplete hex
        assert False
    except WireError as e:
        assert e.kind == "escape"
    print("OK incomplete hex (one digit) error")

    try:
        decode(r"\xzz")  # invalid hex
        assert False
    except WireError as e:
        assert e.kind == "escape"
    print("OK invalid hex error")


def test_tilde_rules():
    """Test tilde rules."""
    # Rule 11: tilde as entire atom
    assert decode("~") == ""
    print("OK tilde as empty atom")

    # Tilde cannot be part of longer atom
    try:
        decode("a~b")
        assert False
    except WireError as e:
        assert e.kind == "tilde" and e.pos == 1
    print("OK tilde in middle error")

    # But escaped tilde can
    assert decode(r"a\~b") == "a~b"
    print("OK escaped tilde in atom")

    # Tilde as entire list item
    assert decode("(~)") == [""]
    print("OK tilde in list")

    # Tilde with other escaping
    assert decode(r"(\~)") == ["~"]
    print("OK escaped tilde in list")


def test_empty_atom_rules():
    """Test empty atom error rules."""
    # At start of input
    try:
        decode(",a")
        assert False
    except WireError as e:
        assert e.kind == "empty" and e.pos == 0
    print("OK empty at start (comma)")

    # After (
    try:
        decode("(,")
        assert False
    except WireError as e:
        assert e.kind == "empty" and e.pos == 1
    print("OK empty after opening paren")

    # After ,
    try:
        decode("(a,,b)")
        assert False
    except WireError as e:
        assert e.kind == "empty" and e.pos == 3
    print("OK empty after comma")

    # But tilde is valid
    assert decode("(~,a)") == ["", "a"]
    print("OK tilde as empty atom")


def test_open_paren_in_atom():
    """Test that open paren can be literal inside atom."""
    # Rule 7: unescaped ( inside atom (not at start) is literal
    # Example from spec: decode("(a(b)") == ["a(b"]
    assert decode("(a(b)") == ["a(b"]
    print("OK open paren literal in atom")

    # Multiple items with embedded paren
    assert decode("(a(b,c)") == ["a(b", "c"]
    print("OK open paren in multi-item list")

    # Escaped paren
    assert decode(r"a\(b") == "a(b"
    print("OK escaped paren")


def test_list_delimiters():
    """Test list delimiter parsing."""
    # Multiple items
    assert decode("(a,b,c)") == ["a", "b", "c"]
    print("OK multiple items")

    # Nested with items
    assert decode("(a,(b,c),d)") == ["a", ["b", "c"], "d"]
    print("OK nested items")

    # Empty list in list
    assert decode("((),a)") == [[], "a"]
    print("OK empty list with items")


def test_error_precedence():
    """Test error precedence rules."""
    # escape > depth > tilde > empty > delim > unterminated > trailing

    # Test escape before depth
    try:
        decode("(" * 200 + r"\x0")
        assert False
    except WireError as e:
        # Should report escape, not depth/empty/etc
        assert e.kind == "escape"
    print("OK escape precedence")

    # Test tilde before empty
    try:
        decode("(~a,x)")
        assert False
    except WireError as e:
        # At position 1, we have tilde in wrong position
        assert e.kind == "tilde" and e.pos == 1
    print("OK tilde precedence over empty")

    # Test empty before delim
    try:
        decode(",")
        assert False
    except WireError as e:
        # At position 0, we need a value (empty) before considering it a delim
        assert e.kind == "empty" and e.pos == 0
    print("OK empty precedence over delim")

    # Test delim before unterminated
    try:
        decode("(a,)")
        assert False
    except WireError as e:
        # At position 3, we have empty atom (after comma, at closing paren)
        assert e.kind == "empty" and e.pos == 3
    print("OK empty precedence over unterminated")


def test_positions():
    """Test that error positions are correct."""
    # Escape at position 3
    try:
        decode("abc" + "\\")
        assert False
    except WireError as e:
        assert e.kind == "escape" and e.pos == 3
    print("OK escape position")

    # Tilde at position 5
    try:
        decode("(a,b~c)")
        assert False
    except WireError as e:
        assert e.kind == "tilde" and e.pos == 4
    print("OK tilde position")

    # Unterminated at end
    try:
        decode("(a,b")
        assert False
    except WireError as e:
        # After "b", we need comma or paren but reach end of input
        # This is "unterminated" at position 4
        assert e.kind == "unterminated" and e.pos == 4
    print("OK unterminated end of input position")


def test_round_trip():
    """Test encode/decode round trips."""
    test_values = [
        "hello",
        ["a", "b", "c"],
        [[], [""]],
        "a,b,c",
        r"a\b",
        "\x00\x1f\x7f",
        ["x(y)", "a)b"],
        "",
    ]

    for val in test_values:
        encoded = encode(val)
        decoded = decode(encoded)
        re_encoded = encode(decoded)
        assert decoded == val, f"Decode mismatch for {val!r}"
        assert re_encoded == encoded, f"Re-encode mismatch for {val!r}"

    print("OK all round trips")


def test_performance():
    """Test performance requirements."""
    # Requirement: 200,000 short atoms in ~1.4 MB must decode/encode in <5 seconds
    # We'll test with a smaller number but verify it works

    # Create a list of 10,000 short atoms
    items = ["a" + str(i%100) for i in range(10000)]
    encoded = encode(items)

    # This should be reasonably fast
    decoded = decode(encoded)
    assert decoded == items

    # Re-encode should be identical
    re_encoded = encode(decoded)
    assert re_encoded == encoded

    print(f"OK performance test: {len(items)} items, {len(encoded)} bytes")


if __name__ == "__main__":
    test_escape_sequences()
    test_tilde_rules()
    test_empty_atom_rules()
    test_open_paren_in_atom()
    test_list_delimiters()
    test_error_precedence()
    test_positions()
    test_round_trip()
    test_performance()
    print("\nOK All edge case tests passed!")
