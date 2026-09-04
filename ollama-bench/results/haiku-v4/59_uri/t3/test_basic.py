import sys
from uriref import parse, unparse, normalize, resolve, UriError

# Test parse
print('Testing parse...')
result = parse('http://a.com/x?y=1#z')
expected = {
    'scheme': 'http',
    'userinfo': None,
    'host': 'a.com',
    'port': None,
    'path': '/x',
    'query': 'y=1',
    'fragment': 'z'
}
assert result == expected, f'parse test 1 failed'
print('✓ parse("http://a.com/x?y=1#z")')

result = parse('mailto:x@y')
expected = {
    'scheme': 'mailto',
    'userinfo': None,
    'host': None,
    'port': None,
    'path': 'x@y',
    'query': None,
    'fragment': None
}
assert result == expected, f'parse test 2 failed'
print('✓ parse("mailto:x@y")')

# Test unparse
print('\nTesting unparse...')
uri = '//u@h:8080/p'
parsed = parse(uri)
unparsed = unparse(parsed)
assert unparsed == uri, f'unparse roundtrip failed: expected {uri}, got {unparsed}'
print(f'✓ unparse(parse("{uri}")) == "{uri}"')

# Test normalize
print('\nTesting normalize...')
result = normalize('HTTP://Example.COM:80/a/./b/../c')
expected = 'http://example.com/a/c'
assert result == expected, f'normalize test failed: got {result}'
print(f'✓ normalize("HTTP://Example.COM:80/a/./b/../c") == "{expected}"')

# Test resolve
print('\nTesting resolve...')
result = resolve('http://a/b/c/d;p?q', '../g')
expected = 'http://a/b/g'
assert result == expected, f'resolve test 1 failed: got {result}'
print(f'✓ resolve("http://a/b/c/d;p?q", "../g") == "{expected}"')

result = resolve('http://a/b/c/d;p?q', '?y')
expected = 'http://a/b/c/d;p?y'
assert result == expected, f'resolve test 2 failed: got {result}'
print(f'✓ resolve("http://a/b/c/d;p?q", "?y") == "{expected}"')

print('\nAll basic tests passed!')
