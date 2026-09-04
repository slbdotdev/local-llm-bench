#!/usr/bin/env python
"""Test cases for the calc.evaluate() function."""

import sys
from calc import evaluate


def test_evaluate():
    """Run test cases for the evaluate function."""
    tests = [
        # (expression, expected_value, expected_error)
        ("1 + 2", 3.0, None),
        ("2 + 3 * 4", 14.0, None),
        ("(2 + 3) * 4", 20.0, None),
        ("-3 * -2", 6.0, None),
        ("3.5 + .5", 4.0, None),
        ("10 / 2", 5.0, None),
        ("1.0 + 2.5", 3.5, None),
        ("(10 + 5) / 3", 5.0, None),
        ("-5 + 3", -2.0, None),
        ("--5", 5.0, None),
        ("1 / 0", None, ZeroDivisionError),
        ("", None, ValueError),
        ("   ", None, ValueError),
        ("2+", None, ValueError),
        ("2+3)", None, ValueError),
        ("(2+3", None, ValueError),
        ("2 & 3", None, ValueError),
        ("2 @ 3", None, ValueError),
    ]

    passed = 0
    failed = 0

    for expr, expected_value, expected_error in tests:
        try:
            result = evaluate(expr)
            if expected_error is not None:
                print(f"FAIL: evaluate('{expr}') should raise {expected_error.__name__}, but got {result}")
                failed += 1
            elif abs(result - expected_value) < 1e-9:
                print(f"PASS: evaluate('{expr}') = {result}")
                passed += 1
            else:
                print(f"FAIL: evaluate('{expr}') = {result}, expected {expected_value}")
                failed += 1
        except Exception as e:
            if expected_error is not None and isinstance(e, expected_error):
                print(f"PASS: evaluate('{expr}') raised {type(e).__name__}: {e}")
                passed += 1
            else:
                print(f"FAIL: evaluate('{expr}') raised {type(e).__name__}: {e}")
                failed += 1

    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = test_evaluate()
    sys.exit(0 if success else 1)
