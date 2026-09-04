#!/usr/bin/env python3
"""Quick tests for csvlite.py"""

from csvlite import parse

def test_case(name, text, expected):
    result = parse(text)
    if result == expected:
        print(f"[PASS] {name}")
        return True
    else:
        print(f"[FAIL] {name}")
        print(f"  Input: {repr(text)}")
        print(f"  Expected: {expected}")
        print(f"  Got: {result}")
        return False

# Run tests
all_pass = True

# Basic cases
all_pass &= test_case("Empty string", "", [])
all_pass &= test_case("Simple case", "a,b", [["a", "b"]])
all_pass &= test_case("With trailing newline", "a,b\n", [["a", "b"]])
all_pass &= test_case("With \\r\\n", "a,b\r\n", [["a", "b"]])
all_pass &= test_case("With just \\r", "a,b\r", [["a", "b"]])

# Empty fields
all_pass &= test_case("Empty field in middle", "a,,b", [["a", "", "b"]])
all_pass &= test_case("Empty field at start", ",b", [["", "b"]])
all_pass &= test_case("Empty field at end", "a,", [["a", ""]])
all_pass &= test_case("Just comma", ",", [["", ""]])

# Quoted fields
all_pass &= test_case("Quoted field with comma", 'a,"b,c",d', [["a", "b,c", "d"]])
all_pass &= test_case("Quoted field with newline", 'a,"b\nc",d', [["a", "b\nc", "d"]])
all_pass &= test_case("Quoted empty field", '"",b', [["", "b"]])

# Escaped quotes
all_pass &= test_case("Escaped quote in quoted field", '"a""b"', [['a"b']])
all_pass &= test_case("Escaped quotes multiple", '"a""b""c"', [['a"b"c']])

# Multiple rows
all_pass &= test_case("Two rows", "a,b\nc,d", [["a", "b"], ["c", "d"]])
all_pass &= test_case("Three rows with empty", "a\n\nb", [["a"], [""], ["b"]])

# Spaces preservation
all_pass &= test_case("Unquoted spaces preserved", "a , b", [["a ", " b"]])
all_pass &= test_case("Quoted spaces", '"a , b"', [["a , b"]])

# Just newline
all_pass &= test_case("Just newline", "\n", [[""]])

# Complex
all_pass &= test_case("Complex mix", 'name,"age","city"\nAlice,"30","New York"\nBob,"25","LA"',
                      [["name", "age", "city"], ["Alice", "30", "New York"], ["Bob", "25", "LA"]])

print("\n" + ("="*40))
if all_pass:
    print("All tests passed!")
else:
    print("Some tests failed!")
