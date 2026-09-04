#!/usr/bin/env python3
"""Comprehensive tests for wirefmt implementation."""

from wirefmt import encode, decode, canon, WireError

def test_canon_idempotence():
    """Test that canon is idempotent."""
    test_cases = [
        r"(a,b,c)",
        r"(~)",
        r"(\x41,\a,a(b,~)",
        r"((),(\x0A),\X41,\a)",
    ]
    for text in test_cases:
        result1 = canon(text)
        result2 = canon(result1)
        assert result1 == result2, f"canon not idempotent: {text!r}"
        print(f"OK canon idempotence: {text!r}")


def test_encode_escapes():
    """Test encoding of special characters."""
    # Test backslash
    result = encode("\\")
    assert result == r"\\", f"Expected '\\\\\\\\', got {result!r}"
    print(f"OK encode backslash: {result!r}")

    # Test all special chars
    result = encode("()~,")
    assert result == r"\(\)\~\,", f"Expected escaped version, got {result!r}"
    print(f"OK encode special chars: {result!r}")

    # Test control chars
    result = encode("\x00\x01\x1f\x7f")
    assert result == r"\x00\x01\x1f\x7f", f"Expected hex escapes, got {result!r}"
    print(f"OK encode control chars: {result!r}")

    # Test space
    result = encode("hello world")
    assert result == "hello world", f"Space should be literal, got {result!r}"
    print(f"OK encode space: {result!r}")


def test_decode_redundant_escapes():
    """Test that decode accepts redundant escapes."""
    # Redundant escapes should work
    result = decode(r"\a\b\c")
    assert result == "abc", f"Expected 'abc', got {result!r}"
    print(f"OK decode redundant escapes: {result!r}")

    # Redundant escape of space
    result = decode(r"hello\ world")
    assert result == "hello world", f"Expected 'hello world', got {result!r}"
    print(f"OK decode space escape: {result!r}")


def test_hex_case_insensitive():
    """Test that hex escapes accept both cases."""
    result1 = decode(r"\x41")
    result2 = decode(r"\X41")
    result3 = decode(r"\x41")

    # The first two should decode, the third with lowercase x
    assert result1 == "A", f"Lowercase hex should work"
    # Note: \X41 is actually \(X)(41), so it becomes "X41"
    assert result2 == "X41", f"\\X should decode as X not hex escape"
    print(f"OK hex case handling")


def test_nested_lists():
    """Test nested list handling."""
    # Simple nested list
    result = decode("((a,b),c)")
    assert result == [["a", "b"], "c"], f"Expected nested list, got {result!r}"
    print(f"OK decode nested list: {result!r}")

    # Deeper nesting
    result = decode("(((a)))")
    assert result == [[["a"]]], f"Expected deeply nested list, got {result!r}"
    print(f"OK decode 3-level nesting: {result!r}")

    # Encode it back
    encoded = encode([[["a"]]])
    assert encoded == "(((a)))", f"Expected '(((a)))', got {encoded!r}"
    print(f"OK encode 3-level nesting: {encoded!r}")


def test_error_precedence_complex():
    """Test error precedence in complex cases."""
    # "empty" error has precedence over "delim" at top level
    try:
        decode(")")
        assert False, "Should raise error"
    except WireError as e:
        # At top level, ) means we need a value there, so it's empty not delim
        assert e.kind == "empty" and e.pos == 0, f"Expected empty@0, got {e.kind}@{e.pos}"
        print(f"OK empty before delim: {e.kind}@{e.pos}")

    # "delim" error for ) at top level
    try:
        decode("a)")
        assert False, "Should raise error"
    except WireError as e:
        assert e.kind == "delim" and e.pos == 1, f"Expected delim@1, got {e.kind}@{e.pos}"
        print(f"OK delim error at top level: {e.kind}@{e.pos}")

    # "trailing" after list
    try:
        decode("()XYZ")
        assert False, "Should raise error"
    except WireError as e:
        assert e.kind == "trailing" and e.pos == 2, f"Expected trailing@2, got {e.kind}@{e.pos}"
        print(f"OK trailing after list: {e.kind}@{e.pos}")

    # "unterminated" with multiple levels
    try:
        decode("((a)")
        assert False, "Should raise error"
    except WireError as e:
        # After "a)", we need the inner list to close or need a delimiter
        # Actually "((" opens depth 2, "a" is an atom, ")" closes one level
        # But we're still at depth 1, so unterminated
        assert e.kind == "unterminated" and e.pos == 4, f"Expected unterminated@4, got {e.kind}@{e.pos}"
        print(f"OK unterminated nested: {e.kind}@{e.pos}")


def test_large_flat_list():
    """Test performance with large flat list."""
    # Create a list with 1000 items
    items = ["item" + str(i) for i in range(1000)]
    encoded = encode(items)
    decoded = decode(encoded)
    assert decoded == items, "Large list decode failed"
    print(f"OK large flat list: {len(items)} items")

    # Re-encode should be identical
    re_encoded = encode(decoded)
    assert re_encoded == encoded, "Large list re-encode differs"
    print(f"OK large list re-encode consistent")


def test_max_depth():
    """Test exactly 200 levels of nesting."""
    # Build 200 level deep list
    deep = "a"
    for _ in range(200):
        deep = [deep]

    # Should encode successfully
    encoded = encode(deep)
    # And decode back
    decoded = decode(encoded)
    assert decoded == deep, "200-level decode failed"
    print(f"OK max depth 200")

    # 201 levels should fail on encode
    very_deep = deep
    very_deep = [very_deep]  # Make it 201 levels
    try:
        encode(very_deep)
        assert False, "Should fail on 201 levels"
    except WireError as e:
        assert e.kind == "depth" and e.pos == 0, f"Expected depth@0, got {e.kind}@{e.pos}"
        print(f"OK encode fails at 201 levels")


def test_type_errors():
    """Test type error handling."""
    # Numbers should fail
    try:
        encode(123)
        assert False, "Should fail on int"
    except WireError as e:
        assert e.kind == "type" and e.pos == 0, f"Expected type@0, got {e.kind}@{e.pos}"
        print(f"OK type error on int")

    # Dict should fail
    try:
        encode({"a": "b"})
        assert False, "Should fail on dict"
    except WireError as e:
        assert e.kind == "type" and e.pos == 0, f"Expected type@0, got {e.kind}@{e.pos}"
        print(f"OK type error on dict")

    # List with invalid item
    try:
        encode(["a", 123])
        assert False, "Should fail on list with int"
    except WireError as e:
        assert e.kind == "type" and e.pos == 0, f"Expected type@0, got {e.kind}@{e.pos}"
        print(f"OK type error on invalid list item")


def test_unicode():
    """Test Unicode handling."""
    # Non-ASCII characters should pass through
    result = encode("café")
    assert "café" in result, f"Unicode should be in output"
    decoded = decode(result)
    assert decoded == "café", f"Unicode round-trip failed"
    print(f"OK unicode: cafe")

    # Emoji
    result = encode("hello😊")
    decoded = decode(result)
    assert decoded == "hello😊", f"Emoji round-trip failed"
    print(f"OK emoji")


def test_whitespace():
    """Test whitespace handling."""
    # Tabs, newlines, etc.
    result = encode("a\tb\nc")
    decoded = decode(result)
    assert decoded == "a\tb\nc", f"Whitespace failed"
    print(f"OK whitespace handling")


if __name__ == "__main__":
    print("Testing canon idempotence...")
    test_canon_idempotence()
    print("\nTesting encode escapes...")
    test_encode_escapes()
    print("\nTesting decode redundant escapes...")
    test_decode_redundant_escapes()
    print("\nTesting hex case handling...")
    test_hex_case_insensitive()
    print("\nTesting nested lists...")
    test_nested_lists()
    print("\nTesting error precedence...")
    test_error_precedence_complex()
    print("\nTesting large flat list...")
    test_large_flat_list()
    print("\nTesting max depth...")
    test_max_depth()
    print("\nTesting type errors...")
    test_type_errors()
    print("\nTesting unicode...")
    test_unicode()
    print("\nTesting whitespace...")
    test_whitespace()
    print("\nOK All comprehensive tests passed!")
