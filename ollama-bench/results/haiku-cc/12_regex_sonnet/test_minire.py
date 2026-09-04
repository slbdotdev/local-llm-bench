from minire import fullmatch

def check(pattern, text, expected):
    got = fullmatch(pattern, text)
    status = "OK" if got == expected else "FAIL"
    print(f"{status}: fullmatch({pattern!r}, {text!r}) = {got} (expected {expected})")
    assert got == expected, f"fullmatch({pattern!r}, {text!r}) = {got}, expected {expected}"

# basics
check("a*b", "aaab", True)
check("a*b", "b", True)
check("a*b", "aaa", False)
check("colou?r", "color", True)
check("colou?r", "colour", True)
check("colou?r", "colouur", False)
check("(ab|cd)+", "abcdab", True)
check("(ab|cd)+", "abc", False)
check("[^0-9]+", "ab1", False)
check("[^0-9]+", "abZ", True)
check("", "", True)
check("", "x", False)
check(".", "x", True)
check(".", "", False)
check("a.c", "abc", True)
check(r"a\.c", "a.c", True)
check(r"a\.c", "abc", False)
check(r"\\", "\\", True)
check("[a-z0-9]+", "abc123", True)
check("[a-z0-9]+", "ABC", False)
check("[]a]+", "]a]a", True)  # ] literal first char in class
check("[a-]+", "a-a-", True)  # trailing - literal
check("[-a]+", "a-a-", True)  # leading - literal

# nested backtracking case
check("(a|ab)(c|bcd)(d*)", "abcd", True)
check("(a|ab)(c|bcd)(d*)", "abcdd", True)
check("(a|ab)(c|bcd)(d*)", "abcx", False)

# quantifiers on groups
check("(ab)*", "ababab", True)
check("(ab)*", "aba", False)
check("(a|b)*c", "aabbac", True)

# malformed patterns -> ValueError
for bad in ["(a", "a)", "[abc", "*a", "a\\", "a**"[:1]+"*"]:
    pass

def check_error(pattern):
    try:
        fullmatch(pattern, "x")
    except ValueError:
        print(f"OK: fullmatch({pattern!r}, ...) raised ValueError as expected")
    else:
        raise AssertionError(f"fullmatch({pattern!r}, ...) did NOT raise ValueError")

check_error("(a")
check_error("a)")
check_error("[abc")
check_error("*a")
check_error("a\\")
check_error("+a")
check_error("a*+")  # '+' has nothing before it (already consumed by '*')

print("All checks passed.")
