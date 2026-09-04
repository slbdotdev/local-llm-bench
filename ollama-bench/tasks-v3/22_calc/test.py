import sys

TOTAL = 32
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
    import expr
    F = expr.evaluate
except Exception as e:
    fails.append(f"import failed: {e!r}")

if F is not None:
    # Basic arithmetic
    check("addition", lambda: F("2 + 3") == 5.0)
    check("subtraction", lambda: F("10 - 3") == 7.0)
    check("multiplication", lambda: F("3 * 4") == 12.0)
    check("division", lambda: F("10 / 2") == 5.0)

    # Operator precedence
    check("mult before add", lambda: F("2 + 3 * 4") == 14.0)
    check("div before add", lambda: F("10 + 6 / 2") == 13.0)
    check("mult and div left-to-right", lambda: F("12 / 2 * 3") == 18.0)

    # Left associativity
    check("sub left-assoc", lambda: F("10 - 5 - 2") == 3.0)
    check("add left-assoc", lambda: F("1 + 2 + 3") == 6.0)
    check("mixed left-assoc", lambda: F("20 - 3 - 2 + 1") == 16.0)

    # Floats
    check("float addition", lambda: F("3.5 + 2.5") == 6.0)
    check("float division", lambda: F("7.5 / 2.5") == 3.0)
    check("int and float", lambda: F("2 + 3.5") == 5.5)

    # Whitespace handling
    check("spaces everywhere", lambda: F("  2  +  3  ") == 5.0)
    check("no spaces", lambda: F("2+3*4") == 14.0)
    check("tabs and spaces", lambda: F("2\t+\n3") == 5.0)

    # Zero cases
    check("zero operand", lambda: F("0 + 5") == 5.0)
    check("subtraction to zero", lambda: F("5 - 5") == 0.0)
    check("zero result division", lambda: F("0 / 5") == 0.0)

    # Complex expressions
    check("multiple operations", lambda: F("100 - 50 + 25") == 75.0)
    check("mixed operators", lambda: F("2 * 3 + 4 * 5") == 26.0)
    check("complex", lambda: F("5 + 3 * 2 - 6 / 2") == 8.0)

    # Error cases: division by zero
    def _div_by_zero():
        try:
            F("10 / 0")
        except ZeroDivisionError as e:
            return "division by zero" in str(e)
        return False

    check("div by zero raises ZeroDivisionError('division by zero')", _div_by_zero)

    # Error cases: malformed input
    error_cases = [
        ("", "empty string"),
        ("+", "operator only"),
        ("2 +", "trailing operator"),
        ("+ 2", "leading operator"),
        ("2 + + 3", "double operator"),
        ("2 +* 3", "invalid sequence"),
        ("2 3", "missing operator"),
        (" ", "whitespace only"),
        ("2 +3+", "ends with operator"),
    ]
    for text, desc in error_cases:
        check_raises(desc, lambda t=text: F(t), ValueError)

    n = max(0, min(TOTAL, TOTAL - len(fails)))
else:
    n = 0

print(f"SCORE {n}/{TOTAL}")
if fails:
    print("FAIL", fails[:10])
    sys.exit(1)
print("PASS")
