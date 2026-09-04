#!/usr/bin/env python3
"""Test all division truncation cases"""
from stackvm import run

# Test 7 / 2 = 3
result = run(["PUSH 7", "PUSH 2", "DIV", "PRINT"])
assert result == ["3"], f"Expected ['3'], got {result}"
print("✓ 7 / 2 = 3 (truncates toward zero)")

# Test -7 / 2 = -3
result = run(["PUSH -7", "PUSH 2", "DIV", "PRINT"])
assert result == ["-3"], f"Expected ['-3'], got {result}"
print("✓ -7 / 2 = -3 (truncates toward zero)")

# Test 7 / -2 = -3
result = run(["PUSH 7", "PUSH -2", "DIV", "PRINT"])
assert result == ["-3"], f"Expected ['-3'], got {result}"
print("✓ 7 / -2 = -3 (truncates toward zero)")

# Test -7 / -2 = 3
result = run(["PUSH -7", "PUSH -2", "DIV", "PRINT"])
assert result == ["3"], f"Expected ['3'], got {result}"
print("✓ -7 / -2 = 3 (truncates toward zero)")

# Test 10 / 3 = 3
result = run(["PUSH 10", "PUSH 3", "DIV", "PRINT"])
assert result == ["3"], f"Expected ['3'], got {result}"
print("✓ 10 / 3 = 3 (truncates toward zero)")

# Test -10 / 3 = -3
result = run(["PUSH -10", "PUSH 3", "DIV", "PRINT"])
assert result == ["-3"], f"Expected ['-3'], got {result}"
print("✓ -10 / 3 = -3 (truncates toward zero)")

print("\n✅ All division cases verified!")
