#!/usr/bin/env python3
"""Test the wirefmt module."""

from wirefmt import encode, decode, canon, WireError

# Test encoding
print('Testing encode...')
assert encode([]) == '()', f'Failed: {encode([])}'
assert encode(['a b', '', '~', 'x,y']) == r'(a b,~,\~,x\,y)', f'Failed: {encode(["a b", "", "~", "x,y"])}'
assert encode([[], ['\n'], 'é']) == r'((),(\x0a),é)', f'Failed: {encode([[], ["\n"], "é"])}'
print('encode tests passed!')

# Test decoding
print('Testing decode...')
result1 = decode(r'((),(\x0A),\X41,\a)')
expected1 = [[], ['\n'], 'X41', 'a']
assert result1 == expected1, f'Failed: {result1} != {expected1}'

result2 = decode(r'(a\)b)')
expected2 = ['a)b']
assert result2 == expected2, f'Failed: {result2} != {expected2}'
print('decode tests passed!')

# Test canon
print('Testing canon...')
result = canon(r'(\x41,\a,a(b,~)')
expected = r'(A,a,a\(b,~)'
assert result == expected, f'Failed: got {repr(result)}, expected {repr(expected)}'
print('canon tests passed!')

print('\nAll tests passed!')
