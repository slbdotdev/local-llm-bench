import sys

TOTAL = 22
fails = []


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = f"{name} raised {type(e).__name__}"
    if not ok:
        fails.append(name)


def check_raises(name, fn, exc):
    try:
        fn()
    except exc:
        return
    except Exception as e:
        fails.append(f"{name}: wrong exception {type(e).__name__}")
        return
    fails.append(f"{name}: no {exc.__name__}")


F = None
try:
    import csvparse
    F = csvparse.parse_csv
except Exception as e:
    fails.append(f"import failed: {e!r}")

if F is not None:
    # Basic cases
    check("empty string", lambda: F("") == [])
    check("single empty field", lambda: F("a") == [["a"]])
    check("single line two fields", lambda: F("a,b") == [["a", "b"]])
    check("two lines", lambda: F("a,b\nc,d") == [["a", "b"], ["c", "d"]])

    # Quoted field spanning lines
    check("quoted newline", lambda: F('"a,b\nc"') == [["a,b\nc"]])

    # Escaped quotes
    check("escaped quote in quoted", lambda: F('"a""b",c') == [["a\"b", "c"]])
    check("consecutive escaped quotes", lambda: F('"a""""b"') == [["a\"\"b"]])

    # CRLF handling
    check("CRLF line ending", lambda: F("a,b\r\nc,d") == [["a", "b"], ["c", "d"]])
    check("CRLF in quoted field", lambda: F('"a\r\nb"') == [["a\r\nb"]])

    # Trailing newlines
    check("trailing newline ignored", lambda: F("a\n") == [["a"]])
    check("trailing CRLF ignored", lambda: F("a\r\n") == [["a"]])

    # Edge cases
    check("comma-only line", lambda: F(",") == [["", ""]])
    check("quoted empty field", lambda: F('""') == [[""]])
    check("mixed quotes", lambda: F('"",a,""') == [["", "a", ""]])

    # Error cases
    error_cases = [
        ('a,"b',        "unmatched quote at end"),
        ('a,b"c',       "quote in unquoted field"),
        ('"a"b"',       "quote after closing quote"),
        ('"',           "unclosed quote alone"),
        ('a,b\n"c',     "unclosed quote after newline"),
    ]
    for bad, desc in error_cases:
        check_raises(desc, lambda t=bad: F(t), ValueError)

    # Whitespace preservation in unquoted fields
    check("leading space unquoted", lambda: F(" a") == [[" a"]])
    check("trailing space unquoted", lambda: F("a ") == [["a "]])
    check("spaces in quoted", lambda: F('" a "') == [[" a "]])

    n = max(0, min(TOTAL, TOTAL - len(fails)))
else:
    n = 0

print(f"SCORE {n}/{TOTAL}")
if fails:
    print("FAIL", fails[:10])
    sys.exit(1)
print("PASS")
