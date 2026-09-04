#!/usr/bin/env python3
from stackvm import run, DuplicateLabel

def test_duplicate_label():
    """Test that duplicate label is raised when executing a duplicate label"""
    try:
        run(["LABEL a", "LABEL a"])
        assert False, "Should have raised DuplicateLabel"
    except DuplicateLabel as e:
        assert "at 0" in str(e), f"Error message should contain 'at 0', got: {e}"
        print("✓ DuplicateLabel raised correctly when first label detects a duplicate")

def test_no_duplicate_if_one_label():
    """Test that no error if only one label"""
    result = run(["LABEL a", "PUSH 5", "PRINT"])
    assert result == ["5"]
    print("✓ Single label is OK")

if __name__ == "__main__":
    test_duplicate_label()
    test_no_duplicate_if_one_label()
    print("\n✅ DuplicateLabel tests passed!")
