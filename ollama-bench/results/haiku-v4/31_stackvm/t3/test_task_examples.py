#!/usr/bin/env python3
"""Test all examples from TASK.md"""
from stackvm import run, StackUnderflow, BadJump

# Example 1
result = run(["PUSH 2", "PUSH 3", "ADD", "PRINT"])
assert result == ["5"], f"Expected ['5'], got {result}"
print("✓ Example 1: run(['PUSH 2', 'PUSH 3', 'ADD', 'PRINT']) == ['5']")

# Example 2
result = run(["PUSH 7", "PUSH 2", "DIV", "PRINT"])
assert result == ["3"], f"Expected ['3'], got {result}"
print("✓ Example 2: run(['PUSH 7', 'PUSH 2', 'DIV', 'PRINT']) == ['3']")

# Example 3
result = run(["PUSH -7", "PUSH 2", "DIV", "PRINT"])
assert result == ["-3"], f"Expected ['-3'], got {result}"
print("✓ Example 3: run(['PUSH -7', 'PUSH 2', 'DIV', 'PRINT']) == ['-3']")

# Example 4
result = run(["PUSH 3", "LABEL top", "DUP", "PRINT", "PUSH 1", "SUB", "DUP", "JNZ top", "DROP"])
assert result == ["3", "2", "1"], f"Expected ['3', '2', '1'], got {result}"
print("✓ Example 4: Loop with JNZ produces ['3', '2', '1']")

# Example 5
result = run(["PUSH 1", "JZ end", "PUSH 10", "PRINT", "LABEL end"])
assert result == ["10"], f"Expected ['10'], got {result}"
print("✓ Example 5: JZ not taken, prints 10")

# Example 6
result = run(["PUSH 1", "JZ nowhere"])
assert result == [], f"Expected [], got {result}"
print("✓ Example 6: run(['PUSH 1', 'JZ nowhere']) == []")

# Example 7
try:
    run(["PUSH 1", "JMP nowhere"])
    assert False, "Should have raised BadJump"
except BadJump as e:
    assert "at 1" in str(e)
    print("✓ Example 7: run(['PUSH 1', 'JMP nowhere']) raises BadJump")

# Example 8
try:
    run(["PRINT", "LABEL a", "LABEL a"])
    assert False, "Should have raised StackUnderflow"
except StackUnderflow as e:
    assert "at 0" in str(e), f"Expected 'at 0' in error message, got: {e}"
    print("✓ Example 8: StackUnderflow at 0 raised (before DuplicateLabel)")

# Example 9
try:
    run(["PRINT"])
    assert False, "Should have raised StackUnderflow"
except StackUnderflow as e:
    assert "at 0" in str(e), f"Expected 'at 0' in error message, got: {e}"
    print("✓ Example 9: run(['PRINT']) raises StackUnderflow at 0")

print("\n✅ All task examples passed!")
