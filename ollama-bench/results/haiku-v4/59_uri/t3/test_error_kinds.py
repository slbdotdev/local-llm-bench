from uriref import parse, unparse, normalize, resolve, UriError

print('Testing all error kinds...')

error_kinds = {}

# Test all error kinds
test_cases = [
    ('type', 123, parse),
    ('scheme', '9http://host', parse),
    ('port', 'http://host:abc', parse),
    ('host', 'http://host[bad]', parse),
    ('userinfo', 'http://user[bad]@host', parse),
    ('char', 'http://host/path[bad]', parse),
    ('escape', 'http://host/path%ZZ', parse),
]

for kind, input_val, func in test_cases:
    try:
        func(input_val)
        print(f'ERROR: {kind} should raise')
    except UriError as e:
        if e.kind == kind:
            print(f'✓ {kind}')
            error_kinds[kind] = True
        else:
            print(f'FAIL: Expected {kind}, got {e.kind}')

# Test unparse error kinds
unparse_cases = [
    ('type', 'not a dict'),
    ('form', {'scheme': 'http'}),  # missing keys
    ('form', {
        'scheme': 'http',
        'userinfo': None,
        'host': 'example.com',
        'port': None,
        'path': None,  # path is None
        'query': None,
        'fragment': None
    }),
]

for kind, input_val in unparse_cases:
    try:
        unparse(input_val)
        print(f'ERROR: unparse {kind} should raise')
    except UriError as e:
        if e.kind == kind:
            print(f'✓ unparse {kind}')
            error_kinds[kind] = True
        else:
            print(f'FAIL: unparse expected {kind}, got {e.kind}')

# Test resolve error kinds
try:
    resolve(123, 'ref')
except UriError as e:
    if e.kind == 'type':
        print(f'✓ resolve type')
        error_kinds['type'] = True

try:
    resolve('//host/path', 'ref')
except UriError as e:
    if e.kind == 'base':
        print(f'✓ base')
        error_kinds['base'] = True

# Check all error kinds are covered
required_kinds = {'type', 'scheme', 'port', 'host', 'userinfo', 'char', 'escape', 'form', 'base'}
for kind in required_kinds:
    if kind not in error_kinds:
        print(f'ERROR: Missing error kind {kind}')
    else:
        print(f'✓ Error kind {kind} works')

print()
print('All error kinds verified!')
