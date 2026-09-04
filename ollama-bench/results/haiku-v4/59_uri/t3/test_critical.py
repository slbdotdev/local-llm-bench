from uriref import parse, unparse, normalize, resolve

print('Testing critical functionality...')

# Test that path is always a string, never None
test_uris = [
    'http://host',
    '//host',
    'path',
    '',
    'http://host:80',
    'http://host/path',
]

print('\nTesting path is always a string:')
for uri in test_uris:
    result = parse(uri)
    assert isinstance(result['path'], str), f'path must be string for {uri}'
    assert result['path'] is not None, f'path must not be None for {uri}'
    print(f'✓ parse("{uri}").path is string')

# Test that other components can be None or string
print('\nTesting component type handling:')
result = parse('http://host')
assert result['scheme'] == 'http'
assert result['userinfo'] is None
assert result['host'] == 'host'
assert result['port'] is None
assert result['path'] == ''
assert result['query'] is None
assert result['fragment'] is None
print('✓ Component types correct for http://host')

# Test empty string components
result = parse('//host//')
assert result['path'] == '//', 'path should be //'
print('✓ Empty double-slash path preserved')

# Test that unparse recreates exactly what was parsed
test_cases = [
    'http://example.com',
    '//example.com',
    '/path',
    'path',
    '?query',
    '#fragment',
    'http://u:p@h:8080/p?q#f',
]

print('\nTesting parse/unparse roundtrip:')
for uri in test_cases:
    parsed = parse(uri)
    unparsed = unparse(parsed)
    assert unparsed == uri, f'Roundtrip failed for {uri}: got {unparsed}'
    print(f'✓ {uri}')

# Test normalization is idempotent
print('\nTesting normalization idempotence:')
test_uris = [
    'http://example.com',
    'http://example.com:80',
    'HTTP://EXAMPLE.COM',
    'http://example.com/path',
    'http://example.com/./path',
]

for uri in test_uris:
    norm1 = normalize(uri)
    norm2 = normalize(norm1)
    assert norm1 == norm2, f'Normalization not idempotent: {norm1} != {norm2}'
    print(f'✓ normalize is idempotent for {uri}')

# Test that resolve always returns an absolute URI
print('\nTesting resolve returns absolute URIs:')
test_cases = [
    ('http://example.com/a/b', 'c'),
    ('http://example.com/a/b', '../c'),
    ('http://example.com/a/b', '/c'),
    ('http://example.com/a/b', 'http://other.com/c'),
]

for base, ref in test_cases:
    result = resolve(base, ref)
    parsed = parse(result)
    assert parsed['scheme'] is not None, f'resolve result must have scheme: {result}'
    print(f'✓ resolve("{base}", "{ref}") returns absolute URI')

print()
print('All critical functionality tests pass!')
