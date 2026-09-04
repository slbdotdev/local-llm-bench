import sys
from uriref import parse, unparse, normalize, resolve, UriError

print('Testing edge cases...')

# Test parse with empty authority components
result = parse('//')
print(f"parse('//') = {result}")
assert result['host'] == '', f"Expected empty host for '//', got {result['host']}"
assert result['userinfo'] is None, f"Expected None userinfo for '//', got {result['userinfo']}"
assert result['port'] is None, f"Expected None port for '//', got {result['port']}"
print('✓ parse("//") has empty host')

# Test parse with //@
result = parse('//@')
print(f"parse('//@') = {result}")
assert result['userinfo'] == '', f"Expected empty userinfo for '//@', got {result['userinfo']}"
assert result['host'] == '', f"Expected empty host for '//@', got {result['host']}"
print('✓ parse("//@") has empty userinfo and host')

# Test parse with //:
result = parse('//:')
print(f"parse('://:') host={result['host']}, port={result['port']}")
assert result['host'] == '', f"Expected empty host for '//:', got {result['host']}"
assert result['port'] == '', f"Expected empty port for '//:', got {result['port']}"
print('✓ parse("//:")  has empty host and port')

# Test percent-encoding in normalize
print('\nTesting percent-encoding...')
result = normalize('http://example.com/path%2f')
print(f"normalize('http://example.com/path%2f') = {result}")
assert '%2F' in result, f"Expected %2F to remain (/ is reserved), got {result}"
print('✓ normalize preserves %2F for /')

result = normalize('http://example.com/path%7e')
print(f"normalize('http://example.com/path%7e') = {result}")
assert '~' in result, f"Expected ~ to be decoded (~ is unreserved), got {result}"
print('✓ normalize decodes %7e to ~')

# Test path dot segment removal
print('\nTesting dot segment removal...')
result = normalize('http://example.com/a/b/c/./../../g')
print(f"normalize('http://example.com/a/b/c/./../../g') = {result}")
assert result == 'http://example.com/a/g', f"Expected http://example.com/a/g, got {result}"
print('✓ normalize correctly handles complex dot segments')

# Test relative path resolution
print('\nTesting relative paths...')
result = resolve('http://a/b/c', 'g')
print(f"resolve('http://a/b/c', 'g') = {result}")
assert result == 'http://a/b/g', f"Expected http://a/b/g, got {result}"
print('✓ resolve correctly merges relative paths')

result = resolve('http://a/b/c/', 'g')
print(f"resolve('http://a/b/c/', 'g') = {result}")
assert result == 'http://a/b/c/g', f"Expected http://a/b/c/g, got {result}"
print('✓ resolve correctly merges when base ends with /')

# Test with empty path
result = resolve('http://a/b/c', '')
print(f"resolve('http://a/b/c', '') = {result}")
assert result == 'http://a/b/c', f"Expected http://a/b/c, got {result}"
print('✓ resolve with empty ref preserves base')

# Test query resolution
result = resolve('http://a/b/c?d=1', '?e=2')
print(f"resolve('http://a/b/c?d=1', '?e=2') = {result}")
assert result == 'http://a/b/c?e=2', f"Expected http://a/b/c?e=2, got {result}"
print('✓ resolve correctly replaces query')

# Test fragment resolution
result = resolve('http://a/b/c#d', '#e')
print(f"resolve('http://a/b/c#d', '#e') = {result}")
assert result == 'http://a/b/c#e', f"Expected http://a/b/c#e, got {result}"
print('✓ resolve correctly replaces fragment')

# Test scheme resolution
result = resolve('http://a/b/c', 'https://b/d')
print(f"resolve('http://a/b/c', 'https://b/d') = {result}")
assert result == 'https://b/d', f"Expected https://b/d, got {result}"
print('✓ resolve with ref scheme uses ref scheme')

# Test default ports
print('\nTesting default port normalization...')
result = normalize('http://example.com:80/path')
print(f"normalize('http://example.com:80/path') = {result}")
assert ':80' not in result, f"Expected default port 80 to be removed for http, got {result}"
print('✓ normalize removes default port 80 for http')

result = normalize('https://example.com:443/path')
print(f"normalize('https://example.com:443/path') = {result}")
assert ':443' not in result, f"Expected default port 443 to be removed for https, got {result}"
print('✓ normalize removes default port 443 for https')

result = normalize('http://example.com:8080/path')
print(f"normalize('http://example.com:8080/path') = {result}")
assert ':8080' in result, f"Expected port 8080 to remain, got {result}"
print('✓ normalize keeps non-default ports')

# Test case folding
print('\nTesting case folding...')
result = normalize('HTTP://EXAMPLE.COM/PATH')
print(f"normalize('HTTP://EXAMPLE.COM/PATH') = {result}")
assert result.startswith('http://example.com'), f"Expected http://example.com (lowercase), got {result}"
assert '/PATH' in result, f"Expected path to keep case, got {result}"
print('✓ normalize lowercases scheme and host but not path')

# Test path normalization guard - only applies if path starts with //
print('\nTesting path normalization guard...')
# This should apply the guard
result = normalize('///')  # No scheme, host is empty, path is ///
print(f"normalize('///') = {result}")
# Actually this will be parsed as host='' path='/'

# Test a relative path that would resolve to starting with //
result = parse('x://y')
print(f"parse('x://y') = {result}")
# scheme is x, then we have //y which is authority with host y, path ''

# Try a URI where normalization guard applies
parsed = {'scheme': None, 'userinfo': None, 'host': None, 'port': None, 'path': '//x', 'query': None, 'fragment': None}
result = unparse(parsed)
print(f"unparse with path='//x' = {result}")

print('\nAll edge case tests passed!')
