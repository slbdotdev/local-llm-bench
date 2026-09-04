#!/usr/bin/env python3
from sedlite import run, ScriptError
import traceback

def test_case(name, script, text, expected, quiet=False, should_error=None):
    """Test a single case."""
    try:
        result = run(script, text, quiet=quiet)
        if should_error:
            print(f"FAIL {name}: Expected {should_error} but got result: {repr(result)}")
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
                print(f"FAIL {name}: Expected error {should_error}, got {e.kind}")
                return False
        else:
            print(f"FAIL {name}: Unexpected error {e.kind}: {e}")
            traceback.print_exc()
            return False
    except Exception as e:
        print(f"FAIL {name}: Unexpected exception: {e}")
        traceback.print_exc()
        return False

passed = 0
failed = 0

# Basic test cases from TASK.md
if test_case("basic_s", 's/a/X/', "abca\nxyz\n", "Xbca\nxyz\n"):
    passed += 1
else:
    failed += 1

if test_case("basic_2d", '2d', "one\ntwo\nthree\n", "one\nthree\n"):
    passed += 1
else:
    failed += 1

if test_case("basic_regex_p", '/b/p', "a\nb\n", "b\n", quiet=True):
    passed += 1
else:
    failed += 1

if test_case("basic_1a", '1a hello', "x\ny\n", "x\nhello\ny\n"):
    passed += 1
else:
    failed += 1

if test_case("basic_alternate_delim", 's,o,0,g', "foo boo\n", "f00 b00\n"):
    passed += 1
else:
    failed += 1

# Test empty input
if test_case("empty_input", 's/a/X/', "", ""):
    passed += 1
else:
    failed += 1

# Test no trailing newline
if test_case("no_trailing_newline", 's/a/X/', "abca", "Xbca\n"):
    passed += 1
else:
    failed += 1

# Test $ address
if test_case("dollar_address", '$s/x/Y/', "a\nx\n", "a\nY\n"):
    passed += 1
else:
    failed += 1

# Test y (transliterate)
if test_case("y_command", 'y/abc/xyz/', "abcabc\n", "xyzxyz\n"):
    passed += 1
else:
    failed += 1

# Test delete command
if test_case("delete_middle", '2d', "a\nb\nc\n", "a\nc\n"):
    passed += 1
else:
    failed += 1

# Test p (print) command
if test_case("print_command", '1p', "a\nb\n", "a\na\nb\n"):
    passed += 1
else:
    failed += 1

# Test p with quiet
if test_case("print_quiet", '1p', "a\nb\n", "a\n", quiet=True):
    passed += 1
else:
    failed += 1

# Test range with numbers
if test_case("range_lines", '1,2d', "a\nb\nc\n", "c\n"):
    passed += 1
else:
    failed += 1

# Test range with $
if test_case("range_dollar", '2,$d', "a\nb\nc\n", "a\n"):
    passed += 1
else:
    failed += 1

# Test negation
if test_case("negation", '2!d', "a\nb\nc\n", "b\n"):
    passed += 1
else:
    failed += 1

# Test step address
if test_case("step_address", '1~2d', "a\nb\nc\nd\ne\n", "b\nd\n"):
    passed += 1
else:
    failed += 1

# Test step with 0
if test_case("step_zero", '2~0d', "a\nb\nc\n", "a\nc\n"):
    passed += 1
else:
    failed += 1

# Test multiple commands
if test_case("multiple_commands", 's/a/X/;s/b/Y/', "ab\n", "XY\n"):
    passed += 1
else:
    failed += 1

# Test comments
if test_case("comment", '# comment\ns/a/X/', "ab\n", "Xb\n"):
    passed += 1
else:
    failed += 1

# Test s with g flag
if test_case("s_g_flag", 's/a/X/g', "aaa\n", "XXX\n"):
    passed += 1
else:
    failed += 1

# Test s with numeric flag
if test_case("s_numeric_flag", 's/a/X/2', "aaa\n", "aXa\n"):
    passed += 1
else:
    failed += 1

# Test s with g and numeric flag
if test_case("s_g_numeric", 's/a/X/g2', "aaa\n", "aXX\n"):
    passed += 1
else:
    failed += 1

# Test s with p flag
# Without g flag, only first match is replaced: "Xaa", then p prints it: "Xaa\nXaa\n"
if test_case("s_p_flag", 's/a/X/p', "aaa\n", "Xaa\nXaa\n"):
    passed += 1
else:
    failed += 1

# Test i command (insert)
if test_case("i_command", '1i inserted', "a\nb\n", "inserted\na\nb\n"):
    passed += 1
else:
    failed += 1

# Test a command (append)
if test_case("a_command", '1a appended', "a\nb\n", "a\nappended\nb\n"):
    passed += 1
else:
    failed += 1

# Test q command
# Line 1: auto-print "a", Line 2: q applied, emit "b", quit
if test_case("q_command", '2q', "a\nb\nc\n", "a\nb\n"):
    passed += 1
else:
    failed += 1

# Test q with quiet
# Line 1: quiet so no auto-print, Line 2: q applied but quiet so no emit of pattern space, quit
if test_case("q_quiet", '2q', "a\nb\nc\n", "", quiet=True):
    passed += 1
else:
    failed += 1

# Test & in replacement
if test_case("s_ampersand", 's/a/[&]/', "a\n", "[a]\n"):
    passed += 1
else:
    failed += 1

# Test backreferences
if test_case("s_backref", 's/(.)\\1/X/', "aa\n", "X\n"):
    passed += 1
else:
    failed += 1

# Test \n in replacement
if test_case("s_newline_repl", 's/a/X\\nY/', "a\n", "X\nY\n"):
    passed += 1
else:
    failed += 1

# Test \t in replacement
if test_case("s_tab_repl", 's/a/X\\tY/', "a\n", "X\tY\n"):
    passed += 1
else:
    failed += 1

# Error tests

# bad_regex - empty regex
if test_case("error_empty_regex", 's///X/', "a\n", None, should_error="bad_regex"):
    passed += 1
else:
    failed += 1

# bad_regex - invalid regex
if test_case("error_invalid_regex", 's/(/X/', "a\n", None, should_error="bad_regex"):
    passed += 1
else:
    failed += 1

# bad_delimiter - invalid character as delimiter
if test_case("error_bad_delim", 'sxa', "a\n", None, should_error="bad_delimiter"):
    passed += 1
else:
    failed += 1

# bad_flag - unknown flag
if test_case("error_bad_flag_unknown", 's/a/X/z', "a\n", None, should_error="bad_flag"):
    passed += 1
else:
    failed += 1

# bad_flag - repeated flag
if test_case("error_bad_flag_repeat", 's/a/X/gg', "a\n", None, should_error="bad_flag"):
    passed += 1
else:
    failed += 1

# bad_flag - flag 0
if test_case("error_bad_flag_zero", 's/a/X/0', "a\n", None, should_error="bad_flag"):
    passed += 1
else:
    failed += 1

# bad_backref
if test_case("error_backref", 's/(a)/\\2/', "a\n", None, should_error="bad_backref"):
    passed += 1
else:
    failed += 1

# bad_address - line 0
if test_case("error_line_zero", '0d', "a\n", None, should_error="bad_address"):
    passed += 1
else:
    failed += 1

# bad_bang - ! with no address
if test_case("error_bang_no_addr", '!d', "a\n", None, should_error="bad_bang"):
    passed += 1
else:
    failed += 1

# bad_bang - multiple !
if test_case("error_bang_multiple", '1!!d', "a\n", None, should_error="bad_bang"):
    passed += 1
else:
    failed += 1

# unknown_command
if test_case("error_unknown_cmd", 'x', "a\n", None, should_error="unknown_command"):
    passed += 1
else:
    failed += 1

# extra_address on q
if test_case("error_extra_addr_q", '1,2q', "a\nb\nc\n", None, should_error="extra_address"):
    passed += 1
else:
    failed += 1

# bad_y - unequal lengths
if test_case("error_y_length", 'y/abc/de/', "a\n", None, should_error="bad_y"):
    passed += 1
else:
    failed += 1

# empty_text for a
if test_case("error_empty_a", '1a', "a\n", None, should_error="empty_text"):
    passed += 1
else:
    failed += 1

# trailing_garbage
if test_case("error_trailing_garbage", '1d x', "a\n", None, should_error="trailing_garbage"):
    passed += 1
else:
    failed += 1

print(f"\nPassed: {passed}, Failed: {failed}")
