#!/usr/bin/env python3
"""Advanced tests for wirefmt including error precedence and performance."""

import time
from wirefmt import encode, decode, canon, WireError

print("Testing error precedence...\n")

# Test that when multiple errors could occur, we report the one at the smallest position
def check_error_pos_kind(text, expected_kind, expected_pos, description):
    """Test that error occurs at expected position with expected kind."""
    try:
        decode(text)
        print(f"FAIL: {description} - No error raised")
        return False
    except WireError as e:
        if e.pos == expected_pos and e.kind == expected_kind:
            print(f"PASS: {description}")
            return True
        else:
            print(f"FAIL: {description} - Got {e.kind} at {e.pos}, expected {expected_kind} at {expected_pos}")
            return False

# Test precedence: smallest pos always wins
check_error_pos_kind(",(", "empty", 0, "Empty at 0, escape at 2 - smallest pos wins")

# Test precedence at same position: escape > depth > tilde > empty > ...
# This is harder to test without manually crafting deeply nested inputs

# Test that we correctly handle nested structures
print("\nTesting complex nested structures...\n")

# Deeply nested with multiple items
complex = [["a", "b"], [["c"]], "d", []]
encoded = encode(complex)
decoded = decode(encoded)
if decoded == complex:
    print("PASS: Complex nested structure round-trips")
else:
    print(f"FAIL: Complex structure - got {decoded}, expected {complex}")

# Test with special characters throughout
special = ["\n", "\x00", "\x7f", "\\", "(", ")", ",", "~"]
encoded = encode(special)
decoded = decode(encoded)
if decoded == special:
    print("PASS: Special characters round-trip")
else:
    print(f"FAIL: Special chars - got {decoded}")

# Test performance: 200,000 short atoms in a flat list
print("\nTesting performance...\n")

start = time.time()
# Create a list with 200,000 atoms
large_list = ["atom"] * 200000
# Should encode quickly
encoded_large = encode(large_list)
encode_time = time.time() - start

print(f"  Encoding 200,000 atoms took {encode_time:.2f}s (should be < 5s)")

if encode_time > 5:
    print("FAIL: Encoding too slow")
else:
    print("PASS: Encoding performance OK")

# Decode should also be fast
start = time.time()
decoded_large = decode(encoded_large)
decode_time = time.time() - start

print(f"  Decoding 200,000 atoms took {decode_time:.2f}s (should be < 5s)")

if decode_time > 5:
    print("FAIL: Decoding too slow")
else:
    print("PASS: Decoding performance OK")

if decoded_large == large_list:
    print("PASS: Large list round-trips correctly")
else:
    print("FAIL: Large list doesn't round-trip")

# Test deep nesting without recursion limits
print("\nTesting deep nesting...\n")

# Need 199 iterations to get depth 200 (starting from empty list)
deep = []
for i in range(199):
    deep = [deep]

start = time.time()
encoded_deep = encode(deep)
encode_time = time.time() - start

decoded_deep = decode(encoded_deep)
decode_time = time.time() - start

if decoded_deep == deep:
    print(f"PASS: Depth 200 encodes/decodes correctly (encode: {encode_time:.3f}s, decode: {decode_time:.3f}s)")
else:
    print("FAIL: Deep nesting doesn't round-trip")

# Test canon idempotence
print("\nTesting canon idempotence...\n")

test_inputs = [
    "(a,b,c)",
    "(~)",
    r"(\x41,\a)",
    "((),())",
    r"(a\(b,c\)d)",
]

for text in test_inputs:
    canonical = canon(text)
    canonical2 = canon(canonical)
    if canonical == canonical2:
        print(f"PASS: canon(canon(text)) == canon(text) for {repr(text)}")
    else:
        print(f"FAIL: canon not idempotent for {repr(text)}")
        print(f"  First: {repr(canonical)}")
        print(f"  Second: {repr(canonical2)}")

print("\nAll advanced tests completed!")
