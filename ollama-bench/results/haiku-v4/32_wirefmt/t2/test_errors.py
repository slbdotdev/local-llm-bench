#!/usr/bin/env python3
"""Test error handling in wirefmt."""

from wirefmt import encode, decode, canon, WireError

def test_error(text, expected_kind, expected_pos, description):
    """Test that decoding text raises the expected error."""
    try:
        decode(text)
        print(f"FAIL: {description} - No error raised")
        return False
    except WireError as e:
        if e.kind == expected_kind and e.pos == expected_pos:
            print(f"PASS: {description}")
            return True
        else:
            print(f"FAIL: {description} - Got {e.kind} at {e.pos}, expected {expected_kind} at {expected_pos}")
            return False

print("Testing error conditions...\n")

# Rule 16: empty - no value where one is required
test_error("", "empty", 0, "Empty input")
test_error(",", "empty", 0, "Comma at start")
test_error("(", "empty", 1, "Unclosed list with empty value after paren")
test_error(")", "empty", 0, "Closing paren as first char (empty value)")

# Test that empty list works
try:
    result = decode("()")
    if result == []:
        print("PASS: Empty list decodes correctly")
    else:
        print(f"FAIL: Empty list gave {result}")
except Exception as e:
    print(f"FAIL: Empty list raised {e}")

# Rule 18: unterminated - unclosed list
test_error("(a", "unterminated", 2, "List missing closing paren")
test_error("(a,b", "unterminated", 4, "List missing closing paren with multiple items")

# Rule 14: escape - malformed backslash
test_error("a\\", "escape", 1, "Backslash at end")
test_error("\\x0", "escape", 0, "\\x with only one hex digit")
test_error("\\x", "escape", 0, "\\x with no hex digits")
test_error("\\x0g", "escape", 0, "\\x with non-hex digit")

# Rule 15: tilde - unescaped tilde not as entire atom
test_error("~a", "tilde", 0, "Tilde followed by other chars")
test_error("a~", "tilde", 1, "Tilde after other chars")
test_error("(a~b)", "tilde", 2, "Tilde in middle of list item")

# Rule 16: empty after comma or open paren
test_error("(,", "empty", 1, "Empty after open paren then comma")
test_error("(a,)", "empty", 3, "Empty after comma before close")
test_error("(a,,b)", "empty", 3, "Empty between two commas")

# Test encode errors
print("\nTesting encode errors...\n")

# Rule 5: type error
try:
    encode(42)
    print("FAIL: Non-list/non-string should error")
except WireError as e:
    if e.kind == "type" and e.pos == 0:
        print("PASS: Non-list/non-string raises type error")
    else:
        print(f"FAIL: Got {e.kind} at {e.pos}")

try:
    encode({"a": "b"})
    print("FAIL: Dict should error")
except WireError as e:
    if e.kind == "type" and e.pos == 0:
        print("PASS: Dict raises type error")
    else:
        print(f"FAIL: Got {e.kind} at {e.pos}")

# Test depth limit
print("\nTesting depth limit...\n")

def make_nested_list(nesting_levels):
    """Create a nested list with given number of nesting levels (depth)."""
    result = []
    for _ in range(nesting_levels):
        result = [result]
    return result

# make_nested_list(200) creates [[...]] with 200 nesting levels (depth 200)
# But each iteration wraps it, so we need (depth-1) iterations to get depth
# Actually: after k iterations, we have k+1 levels of nesting
# So to get depth 200, we need 199 iterations
try:
    encode(make_nested_list(199))
    print("PASS: Depth 200 encodes OK (199 wraps)")
except WireError as e:
    print(f"FAIL: Depth 200 should be OK, got {e.kind}")

# After 200 iterations, we have 201 levels (depth 201)
try:
    encode(make_nested_list(200))
    print("FAIL: Depth 201 should error")
except WireError as e:
    if e.kind == "depth":
        print("PASS: Depth 201 raises depth error (200 wraps)")
    else:
        print(f"FAIL: Got {e.kind} instead of depth")

# Test special characters
print("\nTesting special characters...\n")

# Test newline
result = encode(["\n"])
expected = "(\\x0a)"  # List with one item (newline encoded as \x0a)
if result == expected:
    print("PASS: Newline encodes correctly")
else:
    print(f"FAIL: Newline encoded as {repr(result)}, expected {repr(expected)}")

# Test that decode handles uppercase hex
result = decode("\\x0A")
expected = "\n"
if result == expected:
    print("PASS: Uppercase hex X0A decodes correctly")
else:
    print(f"FAIL: Got {repr(result)}, expected {repr(expected)}")

# Test escape sequences that should work
result = decode("\\a")
expected = "a"
if result == expected:
    print("PASS: Redundant escape \\a works")
else:
    print(f"FAIL: Got {repr(result)}, expected {repr(expected)}")

result = decode("\\ ")
expected = " "
if result == expected:
    print("PASS: Escaped space works")
else:
    print(f"FAIL: Got {repr(result)}, expected {repr(expected)}")

print("\nAll tests completed!")
