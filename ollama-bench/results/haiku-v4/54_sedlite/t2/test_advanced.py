#!/usr/bin/env python3
from sedlite import run, ScriptError

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
            print(f"       Expected bytes: {expected.encode()}")
            print(f"       Got bytes:      {result.encode()}")
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
            return False

passed = 0
failed = 0

# Test complex range with regex
if test("range_regex_complex", '/start/,/end/s/x/X/', "x\nstart\nx\nend\nx\n", "x\nstart\nX\nend\nx\n"):
    passed += 1
else:
    failed += 1

# Test multiple matches in one line
if test("multiple_matches_g", 's/a/X/g', "aaa\n", "XXX\n"):
    passed += 1
else:
    failed += 1

# Test numeric flag with no g
if test("numeric_flag_no_g", 's/a/X/3', "aaaaa\n", "aaXaa\n"):
    passed += 1
else:
    failed += 1

# Test numeric flag beyond match count
if test("numeric_no_match", 's/a/X/5', "aa\n", "aa\n"):
    passed += 1
else:
    failed += 1

# Test g flag with numeric flag
if test("g_and_numeric", 's/a/X/2g', "aaaaa\n", "aXXXX\n"):
    passed += 1
else:
    failed += 1

# Test p flag without replacement
if test("p_no_replacement", 's/x/X/p', "abc\n", "abc\n"):
    passed += 1
else:
    failed += 1

# Test d with address range that never closes
if test("range_never_closes", '/start/,/never/d', "start\na\nb\n", ""):
    passed += 1
else:
    failed += 1

# Test multiple d commands
if test("multiple_deletes", '1d;3d;5d', "a\nb\nc\nd\ne\nf\n", "b\nd\nf\n"):
    passed += 1
else:
    failed += 1

# Test a and i in same script
if test("append_and_insert", '1i first\n1a second', "a\n", "first\na\nsecond\n"):
    passed += 1
else:
    failed += 1

# Test negation on range
if test("negate_range2", '2,3!d', "a\nb\nc\nd\n", "b\nc\n"):
    passed += 1
else:
    failed += 1

# Test q with address range (should error - q doesn't support ranges)
if test("q_range", '2,3q', "a\nb\nc\nd\n", None, should_error="extra_address"):
    passed += 1
else:
    failed += 1

# Test q with no output before quit
if test("q_no_output", '1q', "a\nb\n", "a\n"):
    passed += 1
else:
    failed += 1

# Test empty input
if test("empty_input2", 's/a/X/', "", ""):
    passed += 1
else:
    failed += 1

# Test input with only newlines (empty lines, . doesn't match empty)
if test("only_newlines", 's/./X/', "\n\n", "\n\n"):
    passed += 1
else:
    failed += 1

# Test regex with groups and backrefs
if test("complex_backref", 's/([a-z])([a-z])/\\2\\1/g', "abc\n", "bac\n"):
    passed += 1
else:
    failed += 1

# Test y command with special chars
if test("y_special", 'y/abc/123/', "aabbcc\n", "112233\n"):
    passed += 1
else:
    failed += 1

# Test & in replacement with multiple matches
if test("ampersand_g", 's/a/(&)/g', "aaa\n", "(a)(a)(a)\n"):
    passed += 1
else:
    failed += 1

# Test dollar address with range
if test("range_to_dollar", '2,$d', "a\nb\nc\n", "a\n"):
    passed += 1
else:
    failed += 1

# Test negation with dollar
if test("negate_dollar", '$!d', "a\nb\nc\n", "c\n"):
    passed += 1
else:
    failed += 1

# Test step address that matches nothing
if test("step_no_match", '5~2d', "a\nb\nc\n", "a\nb\nc\n"):
    passed += 1
else:
    failed += 1

# Test range with step address (1~2 matches lines 1,3,5; range 1~2,4 deletes lines 1-4)
if test("range_step", '1~2,4d', "a\nb\nc\nd\ne\n", "e\n"):
    passed += 1
else:
    failed += 1

# Test i with embedded newlines
if test("i_multiline", r'1i line1\nline2', "x\n", "line1\nline2\nx\n"):
    passed += 1
else:
    failed += 1

# Test a with embedded tabs
if test("a_tab", r'1a \t\t', "x\n", "x\n\t\t\n"):
    passed += 1
else:
    failed += 1

# Test escaped backslash in replacement
if test("escape_backslash", r's/a/\\/g', "aaa\n", "\\\\\\\n"):
    passed += 1
else:
    failed += 1

# Test replacement with backslash before digit
if test("backslash_before_digit", r's/a/\0/', "a\n", "0\n"):
    passed += 1
else:
    failed += 1

# Test s with i flag and regex
if test("s_i_flag_regex", 's/[A-Z]/x/i', "ABC\n", "xBC\n"):
    passed += 1
else:
    failed += 1

# Test regex with escaped special chars
if test("regex_escaped_dot", r's/a\.b/X/', "a.b\nab\n", "X\nab\n"):
    passed += 1
else:
    failed += 1

# Test multiple ranges that overlap
if test("overlapping_ranges", '1,3d\n2,4p', "a\nb\nc\nd\ne\n", "d\ne\n"):
    passed += 1
else:
    failed += 1

# Test command after q (should not execute)
if test("command_after_q", '2q\n3s/a/X/', "a\na\na\n", "a\na\n"):
    passed += 1
else:
    failed += 1

# Test very long line
long_line = "a" * 1000 + "\n"
if test("long_line", 's/a/X/g', long_line, "X" * 1000 + "\n"):
    passed += 1
else:
    failed += 1

# Test s with all flag combinations (g=global, i=case-insensitive, p=print, 2=start from 2nd match)
# Matches: A(0), a(1), A(2), a(3) with case-insensitive 'a'
# Replace from match 2: positions 1,2,3 -> AXXX, print and auto-print
if test("s_all_flags", 's/a/X/gip2', "AaAa\n", "AXXX\nAXXX\n"):
    passed += 1
else:
    failed += 1

# Test empty script (should auto-print)
if test("empty_script", '', "a\nb\n", "a\nb\n"):
    passed += 1
else:
    failed += 1

# Test script with only comments
if test("only_comments", "# comment 1\n# comment 2", "a\nb\n", "a\nb\n"):
    passed += 1
else:
    failed += 1

# Test sed with alternation in regex
if test("regex_alternation", 's/a|b/X/', "abc\n", "Xbc\n"):
    passed += 1
else:
    failed += 1

# Error cases

# Error: second number in flags
if test("error_double_number", 's/a/X/12', "a\n", None, should_error="bad_flag"):
    passed += 1
else:
    failed += 1

# Error: unknown flag
if test("error_unknown_flag", 's/a/X/x', "a\n", None, should_error="bad_flag"):
    passed += 1
else:
    failed += 1

# Error: bad address in range
if test("error_range_bad", '1,bad/d', "a\n", None, should_error="bad_address"):
    passed += 1
else:
    failed += 1

# Error: unterminated y command
if test("error_y_unterminated", 'y/ab/c', "a\n", None, should_error="unterminated"):
    passed += 1
else:
    failed += 1

print(f"\nPassed: {passed}, Failed: {failed}")
