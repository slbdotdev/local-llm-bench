#!/usr/bin/env python3
import sys
import time
sys.path.insert(0, '.')
from wirefmt import encode, decode, canon, WireError

def test_performance():
    """Test that large inputs are handled efficiently."""
    print("Testing performance...")

    # Test 1: Flat list of 10,000 short atoms
    print("Creating flat list of 10,000 atoms...")
    atoms = ['a'] * 10000
    start = time.time()
    encoded = encode(atoms)
    decode_time = time.time()
    decoded = decode(encoded)
    end = time.time()

    print(f"  Encoded: {len(encoded)} bytes")
    print(f"  Encode time: {decode_time - start:.3f}s")
    print(f"  Decode time: {end - decode_time:.3f}s")
    assert decoded == atoms
    print("  Passed!")

    # Test 2: Deep nesting (200 levels)
    print("\nTesting deep nesting (200 levels)...")
    deep_value = "x"
    for i in range(200):
        deep_value = [deep_value]

    start = time.time()
    encoded = encode(deep_value)
    end = time.time()
    print(f"  Encoded: {len(encoded)} bytes")
    print(f"  Encode time: {end - start:.3f}s")

    start = time.time()
    decoded = decode(encoded)
    end = time.time()
    print(f"  Decode time: {end - start:.3f}s")
    assert decoded == deep_value
    print("  Passed!")

    # Test 3: Depth limit
    print("\nTesting depth limit (201 levels should fail)...")
    too_deep = "x"
    for i in range(201):
        too_deep = [too_deep]

    try:
        encode(too_deep)
        assert False, "Should have raised WireError"
    except WireError as e:
        assert e.kind == "depth" and e.pos == 0
        print(f"  Correctly raised {e.kind} at {e.pos}")

    # Test 4: Encoding and then decoding preserves idempotence
    print("\nTesting canon idempotence...")
    test_cases = [
        ["a", "b", "c"],
        [[], ["\n"], "é"],
        ["a(b", "c)d", "e,f"],
        ["~", "", "\\"],
    ]

    for value in test_cases:
        encoded = encode(value)
        c1 = canon(encoded)
        c2 = canon(c1)
        assert c1 == c2, f"canon not idempotent: {c1} != {c2}"
    print("  Passed!")

    print("\nAll performance tests passed!")

if __name__ == '__main__':
    test_performance()
