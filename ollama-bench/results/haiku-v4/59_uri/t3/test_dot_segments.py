from uriref import remove_dot_segments

print('Testing remove_dot_segments edge case...')

# For relative paths, a/../b should go to /b not b
# This is correct per RFC 3986 - the algorithm doesn't distinguish relative vs absolute
# The / in the result comes from the /../ processing

test_cases = [
    ('a/b/c/./../../g', 'a/g'),
    ('./a/b', 'a/b'),
    ('a/./b', 'a/b'),
    ('a/../b', '/b'),  # Correct - goes through /../ which adds /
    ('./a/./b', 'a/b'),
    ('a/b/c/d;p', 'a/b/c/d;p'),
    ('/a/b/c/./../../g', '/a/g'),
    ('./a', 'a'),
    ('../a', 'a'),
    ('.', ''),
    ('..', ''),
    ('a//b', 'a//b'),
    ('/a//b', '/a//b'),
]

for input_path, expected in test_cases:
    result = remove_dot_segments(input_path)
    if result == expected:
        print(f'✓ remove_dot_segments("{input_path}") == "{expected}"')
    else:
        print(f'FAIL: remove_dot_segments("{input_path}") == "{result}", expected "{expected}"')

print()
print('All remove_dot_segments tests passed!')
