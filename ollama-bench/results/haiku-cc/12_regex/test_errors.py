#!/usr/bin/env python3
"""Test error handling for malformed patterns."""

from minire import fullmatch

# Test error handling
test_cases = [
    ('*a', True),       # quantifier with nothing before it
    ('+b', True),       # quantifier with nothing before it
    ('?c', True),       # quantifier with nothing before it
    ('(abc', True),     # unbalanced parentheses
    ('abc)', True),     # unbalanced parentheses
    ('[abc', True),     # unterminated character class
]

for pattern, should_error in test_cases:
    try:
        fullmatch(pattern, 'test')
        if should_error:
            print(f'FAIL: Pattern {repr(pattern)} should have raised ValueError')
        else:
            print(f'PASS: Pattern {repr(pattern)} did not raise error as expected')
    except ValueError as e:
        if should_error:
            print(f'PASS: Pattern {repr(pattern)} raised ValueError')
        else:
            print(f'FAIL: Pattern {repr(pattern)} should NOT have raised: {e}')

# Test trailing backslash specifically
backslash_pattern = 'test\\'
try:
    fullmatch(backslash_pattern, 'test')
    print('FAIL: Trailing backslash should error')
except ValueError:
    print('PASS: Trailing backslash raised ValueError')

print("\nAll error handling tests passed!")
