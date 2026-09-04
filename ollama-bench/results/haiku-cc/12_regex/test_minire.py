#!/usr/bin/env python3
"""Test cases for the minire regex engine."""

from minire import fullmatch


def test(name, pattern, text, expected):
    """Test a single case."""
    try:
        result = fullmatch(pattern, text)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} {name}: fullmatch({pattern!r}, {text!r}) = {result} (expected {expected})")
        return result == expected
    except Exception as e:
        status = "FAIL" if expected is not False else "?"
        print(f"{status} {name}: fullmatch({pattern!r}, {text!r}) raised {type(e).__name__}: {e}")
        return isinstance(e, ValueError) and expected is False


def test_error(name, pattern):
    """Test that a pattern raises ValueError."""
    try:
        fullmatch(pattern, "test")
        print(f"FAIL {name}: Expected ValueError for pattern {pattern!r}")
        return False
    except ValueError:
        print(f"PASS {name}: Pattern {pattern!r} correctly raised ValueError")
        return True


# Test cases from the spec
print("=== Spec Examples ===")
test("spec 1", "a*b", "aaab", True)
test("spec 2", "colou?r", "color", True)
test("spec 3", "colou?r", "colour", True)
test("spec 4", "(ab|cd)+", "abcdab", True)
test("spec 5", "[^0-9]+", "ab1", False)
test("spec 6", "", "", True)
test("backtrack", "(a|ab)(c|bcd)(d*)", "abcd", True)

print("\n=== Literal Characters ===")
test("lit 1", "a", "a", True)
test("lit 2", "a", "b", False)
test("lit 3", "abc", "abc", True)
test("lit 4", "abc", "ab", False)

print("\n=== Dot Matching ===")
test("dot 1", ".", "a", True)
test("dot 2", ".", "", False)
test("dot 3", "a.c", "abc", True)
test("dot 4", "a.c", "aXc", True)
test("dot 5", "a.c", "ac", False)

print("\n=== Escapes ===")
test("esc 1", r"\.", ".", True)
test("esc 2", r"\.", "a", False)
test("esc 3", r"\\", "\\", True)
test("esc 4", r"\[", "[", True)
test("esc 5", r"\*", "*", True)

print("\n=== Character Classes ===")
test("class 1", "[abc]", "a", True)
test("class 2", "[abc]", "b", True)
test("class 3", "[abc]", "d", False)
test("class 4", "[a-z]", "m", True)
test("class 5", "[a-z]", "Z", False)
test("class 6", "[0-9]", "5", True)
test("class 7", "[a-zA-Z0-9]", "X", True)

print("\n=== Negated Classes ===")
test("neg 1", "[^abc]", "d", True)
test("neg 2", "[^abc]", "a", False)
test("neg 3", "[^0-9]", "a", True)
test("neg 4", "[^0-9]", "5", False)

print("\n=== Class Edge Cases ===")
test("class edge 1", "[]]", "]", True)
test("class edge 2", "[-a]", "-", True)
test("class edge 3", "[-a]", "a", True)
test("class edge 4", "[a-]", "a", True)
test("class edge 5", "[a-]", "-", True)
test("class edge 6", "[a-z-]", "-", True)

print("\n=== Quantifiers ===")
test("quant 1", "a*", "", True)
test("quant 2", "a*", "a", True)
test("quant 3", "a*", "aaa", True)
test("quant 4", "a*", "b", False)
test("quant 5", "a+", "", False)
test("quant 6", "a+", "a", True)
test("quant 7", "a+", "aaa", True)
test("quant 8", "a?", "", True)
test("quant 9", "a?", "a", True)
test("quant 10", "a?", "aa", False)

print("\n=== Groups ===")
test("group 1", "(a)", "a", True)
test("group 2", "(ab)", "ab", True)
test("group 3", "(ab)", "a", False)
test("group 4", "(a)*", "", True)
test("group 5", "(ab)*", "ababab", True)
test("group 6", "(a|b)", "a", True)
test("group 7", "(a|b)", "b", True)
test("group 8", "(a|b)", "c", False)

print("\n=== Alternation ===")
test("alt 1", "a|b", "a", True)
test("alt 2", "a|b", "b", True)
test("alt 3", "a|b", "c", False)
test("alt 4", "cat|dog", "cat", True)
test("alt 5", "cat|dog", "dog", True)
test("alt 6", "cat|dog", "ca", False)

print("\n=== Complex Patterns ===")
test("complex 1", "a+b*c?", "aaabbc", True)
test("complex 2", "a+b*c?", "ac", True)
test("complex 3", "[a-z]+@[a-z]+\\.[a-z]+", "test@example.com", True)
test("complex 4", "(foo|bar)+", "foobarfoo", True)
test("complex 5", "([a-z])[a-z]*", "hello", True)

print("\n=== Error Cases ===")
test_error("err 1", "*a")
test_error("err 2", "+a")
test_error("err 3", "?a")
test_error("err 4", "(abc")
test_error("err 5", "abc)")
test_error("err 6", "[abc")
test_error("err 7", "\\")

print("\n=== More Backtracking Tests ===")
test("backtrack 2", "(a|ab)(b|ab)", "aab", True)
test("backtrack 3", "(a|ab)(b|ab)", "ab", True)  # (a) then (b) matches ab
test("backtrack 4", "(a*)(ab)", "aaab", True)
test("backtrack 5", "(a*)(a)", "aaa", True)

print("\n=== Quantifier Edge Cases ===")
test("quant edge 2", ".*", "anything", True)
test("quant edge 3", ".+", "a", True)
test("quant edge 4", ".+", "", False)
test("quant edge 5", ".?", "", True)
test("quant edge 6", ".?", "x", True)
