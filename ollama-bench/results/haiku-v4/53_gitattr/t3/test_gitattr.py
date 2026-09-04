#!/usr/bin/env python3
"""Test suite for gitattr.py"""

from gitattr import AttrError, compile_attrs, check_attrs

def test_basic_examples():
    """Test basic examples from the spec."""
    print("Testing basic examples...")

    # Example 1
    c = compile_attrs(["*.txt text", "/doc/*.txt -text diff=plain"])
    result1 = check_attrs("a/b.txt", c)
    assert result1 == {"text": True}, f"Expected {{'text': True}}, got {result1}"
    print("OK: Example 1a passed")

    result2 = check_attrs("doc/b.txt", c)
    assert result2 == {"text": False, "diff": "plain"}, f"Expected {{'text': False, 'diff': 'plain'}}, got {result2}"
    print("OK: Example 1b passed")

    # Example 2 - with macros
    c2 = compile_attrs(["[attr]bin -diff -text", "*.png bin", "*.png diff=hex"])
    result3 = check_attrs("x.png", c2)
    assert result3 == {"bin": True, "diff": "hex", "text": False}, f"Expected {{'bin': True, 'diff': 'hex', 'text': False}}, got {result3}"
    print("OK: Example 2 passed")

    # Example 3 - globstar
    c3 = compile_attrs(["a/**/z !k", "**/z k=1"])
    result4 = check_attrs("a/q/z", c3)
    assert result4 == {"k": "1"}, f"Expected {{'k': '1'}}, got {result4}"
    print("OK: Example 3 passed")

    # Example 4 - error handling
    try:
        compile_attrs(["[ x"])
        assert False, "Should have raised AttrError"
    except AttrError as e:
        assert e.kind == "unterminated_class", f"Expected 'unterminated_class', got {e.kind}"
        print("OK: Example 4 passed")


if __name__ == "__main__":
    test_basic_examples()
    print("All basic tests passed!")
