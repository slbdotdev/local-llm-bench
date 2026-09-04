import sys
from uriref import parse, unparse, normalize, resolve, UriError

print('Testing comprehensive cases...')

# Test various URIs
test_cases = [
    'http://example.com',
    'http://example.com:80',
    'http://example.com/path',
    'http://example.com/path?query',
    'http://example.com/path#fragment',
    'http://user:pass@example.com/path',
    '//example.com/path',
    '/path',
    'path',
    'path?query',
    'path#fragment',
    'http://example.com/path/./to/../file',
    'http://example.com/',
    'http://example.com/a/b/c',
]

print('Testing parse and unparse roundtrip...')
for uri in test_cases:
    try:
        parsed = parse(uri)
        unparsed = unparse(parsed)
        if unparsed != uri:
            print(f"MISMATCH: {uri} -> {unparsed}")
        else:
            print(f'✓ {uri}')
    except UriError as e:
        print(f'ERROR parsing {uri}: {e.kind}')

# Test normalization preserves valid URIs when already normalized
print('\nTesting normalization...')
norm_tests = [
    ('http://example.com', 'http://example.com'),
    ('HTTP://EXAMPLE.COM', 'http://example.com'),
    ('http://example.com:80', 'http://example.com'),
    ('https://example.com:443', 'https://example.com'),
    ('http://example.com/', 'http://example.com/'),
]

for input_uri, expected in norm_tests:
    result = normalize(input_uri)
    if result == expected:
        print(f'✓ normalize({input_uri}) == {expected}')
    else:
        print(f'FAIL: normalize({input_uri}) got {result}, expected {expected}')

# Test resolve with RFC 3986 reference examples
print('\nTesting resolve...')
resolve_tests = [
    ('http://a/b/c/d;p?q', 'g:h', 'g:h'),
    ('http://a/b/c/d;p?q', './g', 'http://a/b/c/g'),
    ('http://a/b/c/d;p?q', 'g/', 'http://a/b/c/g/'),
    ('http://a/b/c/d;p?q', '/g', 'http://a/g'),
    ('http://a/b/c/d;p?q', '//g', 'http://g'),
    ('http://a/b/c/d;p?q', '?y', 'http://a/b/c/d;p?y'),
    ('http://a/b/c/d;p?q', 'g?y', 'http://a/b/c/g?y'),
    ('http://a/b/c/d;p?q', '#s', 'http://a/b/c/d;p?q#s'),
    ('http://a/b/c/d;p?q', 'g#s', 'http://a/b/c/g#s'),
    ('http://a/b/c/d;p?q', 'g?y#s', 'http://a/b/c/g?y#s'),
    ('http://a/b/c/d;p?q', '../g', 'http://a/b/g'),
    ('http://a/b/c/d;p?q', '../../g', 'http://a/g'),
]

for base, ref, expected in resolve_tests:
    result = resolve(base, ref)
    if result == expected:
        print(f'✓ resolve(..., "{ref}")')
    else:
        print(f'FAIL: resolve(..., "{ref}") got {result}, expected {expected}')

print('\nAll comprehensive tests completed!')
