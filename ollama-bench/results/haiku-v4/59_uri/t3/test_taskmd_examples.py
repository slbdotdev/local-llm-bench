from uriref import parse, unparse, normalize, resolve

# Test examples from TASK.md
print('Testing examples from TASK.md:')
print()

# Example 1
result = parse('http://a.com/x?y=1#z')
expected = {'scheme': 'http', 'userinfo': None, 'host': 'a.com', 'port': None, 'path': '/x', 'query': 'y=1', 'fragment': 'z'}
assert result == expected, f'parse example 1 failed'
print('✓ parse("http://a.com/x?y=1#z") correct')

# Example 2
result = parse('mailto:x@y')
expected = {'scheme': 'mailto', 'userinfo': None, 'host': None, 'port': None, 'path': 'x@y', 'query': None, 'fragment': None}
assert result == expected, f'parse example 2 failed'
print('✓ parse("mailto:x@y") correct')

# Example 3
result = unparse(parse('//u@h:8080/p'))
expected = '//u@h:8080/p'
assert result == expected, f'unparse example failed'
print('✓ unparse(parse("//u@h:8080/p")) == "//u@h:8080/p"')

# Example 4
result = normalize('HTTP://Example.COM:80/a/./b/../c')
expected = 'http://example.com/a/c'
assert result == expected, f'normalize example failed: got {result}'
print('✓ normalize("HTTP://Example.COM:80/a/./b/../c") == "http://example.com/a/c"')

# Example 5
result = resolve('http://a/b/c/d;p?q', '../g')
expected = 'http://a/b/g'
assert result == expected, f'resolve example 1 failed: got {result}'
print('✓ resolve("http://a/b/c/d;p?q", "../g") == "http://a/b/g"')

# Example 6
result = resolve('http://a/b/c/d;p?q', '?y')
expected = 'http://a/b/c/d;p?y'
assert result == expected, f'resolve example 2 failed: got {result}'
print('✓ resolve("http://a/b/c/d;p?q", "?y") == "http://a/b/c/d;p?y"')

print()
print('All examples from TASK.md pass!')
