import sys
from uriref import parse, unparse, normalize, resolve, UriError

print('Testing error handling...')

# Test type error
try:
    parse(123)
    print('ERROR: parse(123) should raise UriError')
except UriError as e:
    assert e.kind == 'type', f'Expected kind=type, got {e.kind}'
    print('✓ parse(123) raises UriError(type)')

# Test scheme error - invalid first character
try:
    parse('9http://example.com')
    print('ERROR: parse("9http://...") should raise UriError')
except UriError as e:
    assert e.kind == 'scheme', f'Expected kind=scheme, got {e.kind}'
    print('✓ parse("9http://...") raises UriError(scheme)')

# Test scheme error - invalid character in scheme
try:
    parse('ht@p://example.com')
    print('ERROR: parse("ht@p://...") should raise UriError')
except UriError as e:
    assert e.kind == 'scheme', f'Expected kind=scheme, got {e.kind}'
    print('✓ parse("ht@p://...") raises UriError(scheme)')

# Test port error
try:
    parse('http://example.com:abc')
    print('ERROR: parse("http://example.com:abc") should raise UriError')
except UriError as e:
    assert e.kind == 'port', f'Expected kind=port, got {e.kind}'
    print('✓ parse("http://example.com:abc") raises UriError(port)')

# Test host error
try:
    parse('http://exam[ple.com')
    print('ERROR: parse("http://exam[ple.com") should raise UriError')
except UriError as e:
    assert e.kind == 'host', f'Expected kind=host, got {e.kind}'
    print('✓ parse("http://exam[ple.com") raises UriError(host)')

# Test escape error - invalid escape
try:
    parse('http://example.com/path%GG')
    print('ERROR: parse("...%GG") should raise UriError')
except UriError as e:
    assert e.kind == 'escape', f'Expected kind=escape, got {e.kind}'
    print('✓ parse("...%GG") raises UriError(escape)')

# Test escape error - incomplete escape
try:
    parse('http://example.com/path%A')
    print('ERROR: parse("...%A") should raise UriError')
except UriError as e:
    assert e.kind == 'escape', f'Expected kind=escape, got {e.kind}'
    print('✓ parse("...%A") raises UriError(escape)')

# Test escape error - lone percent
try:
    parse('http://example.com/path%')
    print('ERROR: parse("...%") should raise UriError')
except UriError as e:
    assert e.kind == 'escape', f'Expected kind=escape, got {e.kind}'
    print('✓ parse("...%") raises UriError(escape)')

# Test unparse errors
print('\nTesting unparse error handling...')

# Type error - not dict
try:
    unparse('not a dict')
    print('ERROR: unparse("string") should raise UriError')
except UriError as e:
    assert e.kind == 'type', f'Expected kind=type, got {e.kind}'
    print('✓ unparse("string") raises UriError(type)')

# Form error - wrong keys
try:
    unparse({'scheme': 'http'})
    print('ERROR: unparse with wrong keys should raise UriError')
except UriError as e:
    assert e.kind == 'form', f'Expected kind=form, got {e.kind}'
    print('✓ unparse with wrong keys raises UriError(form)')

# Form error - path is None
try:
    unparse({
        'scheme': 'http',
        'userinfo': None,
        'host': 'example.com',
        'port': None,
        'path': None,
        'query': None,
        'fragment': None
    })
    print('ERROR: unparse with path=None should raise UriError')
except UriError as e:
    assert e.kind == 'form', f'Expected kind=form, got {e.kind}'
    print('✓ unparse with path=None raises UriError(form)')

# Form error - host=None but userinfo is not
try:
    unparse({
        'scheme': 'http',
        'userinfo': 'user',
        'host': None,
        'port': None,
        'path': '/path',
        'query': None,
        'fragment': None
    })
    print('ERROR: unparse with host=None but userinfo not None should raise UriError')
except UriError as e:
    assert e.kind == 'form', f'Expected kind=form, got {e.kind}'
    print('✓ unparse with host=None but userinfo not None raises UriError(form)')

# Test resolve errors
print('\nTesting resolve error handling...')

# Type error - not a string
try:
    resolve(123, 'ref')
    print('ERROR: resolve(123, ...) should raise UriError')
except UriError as e:
    assert e.kind == 'type', f'Expected kind=type, got {e.kind}'
    print('✓ resolve(123, ...) raises UriError(type)')

# Base error - no scheme
try:
    resolve('//example.com/path', 'ref')
    print('ERROR: resolve("//...", ...) should raise UriError')
except UriError as e:
    assert e.kind == 'base', f'Expected kind=base, got {e.kind}'
    print('✓ resolve("//...", ...) raises UriError(base)')

print('\nAll error tests passed!')
