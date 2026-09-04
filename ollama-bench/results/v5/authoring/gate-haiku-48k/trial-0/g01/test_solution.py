#!/usr/bin/env python3
"""Test the transform function against examples."""

import sys
sys.path.insert(0, "/mnt/d/local-llm-bench/ollama-bench/results/v5/authoring/gate-suite/g01/seed")

from solution import transform
from specification import EXAMPLES


def test_examples():
    """Test all examples from specification."""
    for i, (input_data, expected_output) in enumerate(EXAMPLES):
        result = transform(input_data)
        if result == expected_output:
            print(f"Example {i+1}: PASS")
        else:
            print(f"Example {i+1}: FAIL")
            print(f"  Input: {input_data}")
            print(f"  Expected: {expected_output}")
            print(f"  Got: {result}")
            return False

    print("\nAll examples passed!")
    return True


if __name__ == "__main__":
    success = test_examples()
    sys.exit(0 if success else 1)
