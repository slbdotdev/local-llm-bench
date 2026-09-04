import sys
from uriref import parse, unparse, normalize, resolve, UriError

print('Testing special cases and validation...')

# Test userinfo validation
print('\nTesting userinfo validation...')
try:
    parse('http://user[invalid]@host/path')
    print('ERROR: should have raised for invalid char in userinfo')
except UriError as e:
    print(f'✓ Invalid char in userinfo raises {e.kind}')

# Test that char errors come before escape errors
print('\nTesting error precedence...')
try:
    parse('http://host/path[with]%XX')
    print('ERROR: should have raised for invalid char')
except UriError as e:
    assert e.kind == 'char', f'Expected char error before escape, got {e.kind}'
    print('✓ char error takes precedence over escape error')

# Test query and fragment validation order
print('\nTesting query/fragment char validation...')
try:
    parse('http://host/path?query[invalid]')
    print('ERROR: should have raised for invalid char in query')
except UriError as e:
    assert e.kind == 'char', f'Expected char error, got {e.kind}'
    print('✓ Invalid char in query raises char error')

# Test fragment with valid chars
result = parse('http://host/path#valid_frag-ment')
assert result['fragment'] == 'valid_frag-ment', f'Expected valid_frag-ment, got {result["fragment"]}'
print('✓ parse allows valid chars in fragment')

# Test query with ? encoded
result = parse('http://host/path?a=1&b=2%3fc=3')
assert result['query'] == 'a=1&b=2%3fc=3', f'Expected a=1&b=2%3fc=3, got {result["query"]}'
print('✓ parse allows %3f (?) in query')

# Test empty port
result = parse('http://host:/')
print(f'parse("http://host:/") = {result}')
assert result['port'] == '', f'Expected empty port, got {result["port"]}'
print('✓ parse allows empty port')

# Test normalize with uppercase hex in escapes
result = normalize('http://host/path%2f%2F')
print(f'normalize with mixed case escapes: {result}')
assert '%2F' in result, 'Expected uppercase hex digits'
print('✓ normalize uppercases hex digits in escapes')

# Test normalize with lowercase unreserved
result = normalize('http://host/path%41%7e')
print(f'normalize with unreserved escapes: {result}')
assert 'A~' in result, f'Expected A~ in {result}'
print('✓ normalize decodes unreserved characters')

# Test various default port schemes
print('\nTesting scheme default ports...')
schemes_and_ports = [
    ('http', '80', False),
    ('http', '8080', True),
    ('https', '443', False),
    ('https', '444', True),
    ('ws', '80', False),
    ('wss', '443', False),
    ('ftp', '21', True),  # FTP doesn't have a default
    ('custom', '80', True),  # Unknown scheme keeps port
]

for scheme, port, should_keep in schemes_and_ports:
    uri = f'{scheme}://host:{port}/'
    result = normalize(uri)
    has_port = f':{port}' in result
    if has_port == should_keep:
        print(f'✓ normalize({scheme}:{port}) keeps_port={should_keep}')
    else:
        print(f'FAIL: normalize({scheme}:{port}) keeps_port={has_port}, expected {should_keep}')

# Test unparse with host but path not starting with /
print('\nTesting unparse structural validation...')
try:
    unparse({
        'scheme': 'http',
        'userinfo': None,
        'host': 'example.com',
        'port': None,
        'path': 'no-slash-path',
        'query': None,
        'fragment': None
    })
    print('ERROR: should reject host without / path')
except UriError as e:
    assert e.kind == 'form', f'Expected form error, got {e.kind}'
    print('✓ unparse rejects host with relative path')

# Test resolve with bad ref - bad escape sequence
print('\nTesting resolve error propagation...')
try:
    resolve('http://valid.com/', '/path%XX')
    print('ERROR: should propagate bad escape error')
except UriError as e:
    assert e.kind == 'escape', f'Expected escape error, got {e.kind}'
    print('✓ resolve propagates ref escape errors')

# Test normalization of path with only dots
result = normalize('http://host/./././')
print(f'normalize("http://host/./././"): {result}')
assert result == 'http://host/', f'Expected http://host/, got {result}'
print('✓ normalize handles multiple dot segments')

# Test empty scheme
try:
    parse(':host')
    print('ERROR: should reject empty scheme')
except UriError as e:
    assert e.kind == 'scheme', f'Expected scheme error, got {e.kind}'
    print('✓ parse rejects empty scheme')

# Test scheme that starts with digit (invalid)
try:
    parse('9scheme://host/path')
    print('ERROR: should reject scheme starting with digit')
except UriError as e:
    assert e.kind == 'scheme', f'Expected scheme error, got {e.kind}'
    print('✓ parse rejects scheme starting with digit')

# Test normalization of paths with various dot patterns
result = normalize('http://host/a/b/c/./../../d/./e')
assert result == 'http://host/a/d/e', f'Expected http://host/a/d/e, got {result}'
print('✓ normalize handles complex dot patterns')

# Test that unparse does the right thing with valid components
result = unparse({
    'scheme': 'http',
    'userinfo': 'user',
    'host': 'host.com',
    'port': '8080',
    'path': '/path',
    'query': 'q=1',
    'fragment': 'frag'
})
assert result == 'http://user@host.com:8080/path?q=1#frag', f'Got {result}'
print('✓ unparse correctly builds URI with all components')

print('\nAll special cases tested!')
