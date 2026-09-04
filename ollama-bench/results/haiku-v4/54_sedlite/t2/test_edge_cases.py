#!/usr/bin/env python3
from sedlite import run, ScriptError
import traceback

def test(name, script, text, expected, quiet=False, should_error=None):
    try:
        result = run(script, text, quiet=quiet)
        if should_error:
            print(f"FAIL {name}: Expected {should_error} but got: {repr(result)}")
            return False
        if result == expected:
            print(f"PASS {name}")
            return True
        else:
            print(f"FAIL {name}: Expected {repr(expected)}, got {repr(result)}")
            return False
    except ScriptError as e:
        if should_error:
            if e.kind == should_error:
                print(f"PASS {name} (error {should_error})")
                return True
            else:
                print(f"FAIL {name}: Expected {should_error}, got {e.kind}")
                return False
        else:
            print(f"FAIL {name}: Unexpected error {e.kind}: {e}")
            traceback.print_exc()
            return False

passed = 0
failed = 0

# Range with regex addresses
if test("range_regex", '/a/,/c/d', "a\nb\nc\n", ""):
    passed += 1
else:
    failed += 1

# Range that doesn't match
if test("range_no_match", '/x/,/y/d', "a\nb\nc\n", "a\nb\nc\n"):
    passed += 1
else:
    failed += 1

# Range with +N offset
if test("range_offset", '1,+1d', "a\nb\nc\n", "c\n"):
    passed += 1
else:
    failed += 1

# Range with +0 offset (same line as start)
if test("range_plus_zero", '1,+0d', "a\nb\nc\n", "b\nc\n"):
    passed += 1
else:
    failed += 1

# Multiple ranges
if test("multiple_ranges", '1d;3d', "a\nb\nc\n", "b\n"):
    passed += 1
else:
    failed += 1

# Range with regex and $
if test("range_regex_dollar", '/b/,$d', "a\nb\nc\n", "a\n"):
    passed += 1
else:
    failed += 1

# Escaped delimiter in regex
if test("escaped_delim_regex", r's/a\/b/X/', "a/b\n", "X\n"):
    passed += 1
else:
    failed += 1

# Escaped delimiter in replacement
if test("escaped_delim_repl", r's/a/x\/y/', "a\n", "x/y\n"):
    passed += 1
else:
    failed += 1

# Multiple groups and backrefs
if test("multi_backref", 's/(.)(.)/\\2\\1/', "ab\n", "ba\n"):
    passed += 1
else:
    failed += 1

# Backrefs in complex pattern
if test("backref_complex", 's/([a-z]*)\\1/X/', "aa\n", "X\n"):
    passed += 1
else:
    failed += 1

# Case-insensitive flag
if test("case_insensitive", 's/A/X/i', "aaa\n", "Xaa\n"):
    passed += 1
else:
    failed += 1

# Whitespace handling in addresses
if test("whitespace_address", '1 , 2 d', "a\nb\nc\n", "c\n"):
    passed += 1
else:
    failed += 1

# Comments in middle of script
if test("comment_middle", 's/a/X/\n#comment\ns/b/Y/', "ab\n", "XY\n"):
    passed += 1
else:
    failed += 1

# Empty lines
if test("empty_lines", 's/^$/X/', "a\n\nc\n", "a\nX\nc\n"):
    passed += 1
else:
    failed += 1

# d at end of range
if test("delete_in_range", '1,2{s/./X/;d;}', "a\nb\nc\n", "c\n", should_error="unknown_command"):
    passed += 1
else:
    failed += 1

# a/i with escaped newlines
if test("append_newline", r'1a line1\nline2', "x\n", "x\nline1\nline2\n"):
    passed += 1
else:
    failed += 1

# i with escaped tab
if test("insert_tab", r'1i \thello', "x\n", "\thello\nx\n"):
    passed += 1
else:
    failed += 1

# y with escaped characters - \n and \t only escape within the y command
# Newlines between lines aren't part of the pattern space
if test("y_escaped", r'y/a\n/X\t/', "a\n\n", "X\n\n"):
    passed += 1
else:
    failed += 1

# Empty y is allowed
if test("y_empty", 'y///', "a\n", "a\n"):
    passed += 1
else:
    failed += 1

# Step address with $ - match every line
if test("step_with_dollar", '2~1d', "a\nb\nc\nd\n", "a\n"):
    passed += 1
else:
    failed += 1

# Only line case
if test("single_line", '1s/a/X/', "a", "X\n"):
    passed += 1
else:
    failed += 1

# Range that closes on first line (addr2 is plain number <= current line, range stays INACTIVE)
if test("range_close_immediately", '2,1d', "a\nb\nc\n", "a\nb\nc\n"):
    passed += 1
else:
    failed += 1

# p command with quiet and substitution
if test("p_with_quiet_after_s", 's/a/X/p', "aa\n", "Xa\nXa\n"):
    passed += 1
else:
    failed += 1

# Multiple p flags should error
if test("s_double_p", "s/a/X/pp", "a\n", None, should_error="bad_flag"):
    passed += 1
else:
    failed += 1

# a/i on multiple addresses
if test("append_multiple", '1a one\n2a two', "a\nb\n", "a\none\nb\ntwo\n"):
    passed += 1
else:
    failed += 1

# Negation with range
if test("negate_range", '1,2!d', "a\nb\nc\n", "a\nb\n"):
    passed += 1
else:
    failed += 1

# Regex with ^ and $
# p matches lines that are exactly "b", so it prints those lines in addition to auto-print
if test("regex_anchors", '/^b$/p', "a\nb\nc\n", "a\nb\nb\nc\n"):
    passed += 1
else:
    failed += 1

# Regex with +
if test("regex_plus", 's/a+/X/', "aaa\n", "X\n"):
    passed += 1
else:
    failed += 1

# Regex with [...]
if test("regex_class", 's/[ab]/X/', "abc\n", "Xbc\n"):
    passed += 1
else:
    failed += 1

# Regex with negated class
if test("regex_neg_class", 's/[^ab]/X/', "abc\n", "abX\n"):
    passed += 1
else:
    failed += 1

# s with i flag on regex
if test("s_case_insensitive_regex", 's/HELLO/hi/i', "hello\n", "hi\n"):
    passed += 1
else:
    failed += 1

# Unterminated regex (newline in middle)
if test("unterminated_newline", "s/a\nb/X/", "a\n", None, should_error="unterminated"):
    passed += 1
else:
    failed += 1

# Trailing backslash in s command
if test("backslash_at_end", "s/a/X\\", "a\n", None, should_error="unterminated"):
    passed += 1
else:
    failed += 1

# Plus address as first address (should error)
if test("plus_first", "+1d", "a\n", None, should_error="bad_address"):
    passed += 1
else:
    failed += 1

# First~step as second address (should error)
if test("step_second", "1,1~2d", "a\n", None, should_error="bad_address"):
    passed += 1
else:
    failed += 1

# Regex address with escaped delimiter
# Pattern ^a/b$ matches lines with "a/b"
if test("regex_escaped_slash", r"/a\/b/p", "a/b\nc\n", "a/b\na/b\nc\n"):
    passed += 1
else:
    failed += 1

# Test step address 0~0 - matches only line 0 which doesn't exist
if test("step_zero_no_match", "0~0d", "a\nb\n", "a\nb\n"):
    passed += 1
else:
    failed += 1

# Script ending in backslash (inside s)
if test("script_ends_backslash", "s/a/X\\", "a\n", None, should_error="unterminated"):
    passed += 1
else:
    failed += 1

# Empty pattern space after operations
if test("empty_pattern", 's/.*//', "abc\n", "\n"):
    passed += 1
else:
    failed += 1

# Multiple consecutive delimiters in s
if test("s_empty_sections", "s,,,", "a\n", None, should_error="bad_regex"):
    passed += 1
else:
    failed += 1

# Spaces in flags section (causes error)
if test("spaces_in_flags", "s/a/X/ g", "aa\n", None, should_error="trailing_garbage"):
    passed += 1
else:
    failed += 1

# Test that step address works correctly with different step sizes
if test("step_3", "1~3d", "a\nb\nc\nd\ne\nf\n", "b\nc\ne\nf\n"):
    passed += 1
else:
    failed += 1

# Range that starts but never closes
if test("unclosed_range", "/a/,/zzz/d", "a\nb\nc\n", ""):
    passed += 1
else:
    failed += 1

# When d is executed, no later commands run on that line (1a doesn't get to run on line 1)
if test("range_restart", "1,2d\n1a new", "a\nb\nc\n", "c\n"):
    passed += 1
else:
    failed += 1

print(f"\nPassed: {passed}, Failed: {failed}")
