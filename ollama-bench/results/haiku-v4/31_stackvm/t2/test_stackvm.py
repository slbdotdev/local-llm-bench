#!/usr/bin/env python3

from stackvm import run, VMError, StackUnderflow, UnknownOp, BadOperand, BadJump, DuplicateLabel

# Test basic arithmetic
print("Test 1: Basic ADD")
result = run(["PUSH 2", "PUSH 3", "ADD", "PRINT"])
assert result == ["5"], f"Expected ['5'], got {result}"
print("PASS")

# Test division
print("Test 2: DIV with positive numbers")
result = run(["PUSH 7", "PUSH 2", "DIV", "PRINT"])
assert result == ["3"], f"Expected ['3'], got {result}"
print("PASS")

print("Test 3: DIV with negative dividend")
result = run(["PUSH -7", "PUSH 2", "DIV", "PRINT"])
assert result == ["-3"], f"Expected ['-3'], got {result}"
print("PASS")

# Test DUP, PRINT, SUB, JNZ loop
print("Test 4: DUP, SUB, JNZ loop")
result = run(["PUSH 3", "LABEL top", "DUP", "PRINT", "PUSH 1", "SUB", "DUP", "JNZ top", "DROP"])
assert result == ["3", "2", "1"], f"Expected ['3', '2', '1'], got {result}"
print("PASS")

# Test JZ
print("Test 5: JZ (jump not taken, then jump taken)")
result = run(["PUSH 1", "JZ end", "PUSH 10", "PRINT", "LABEL end"])
assert result == ["10"], f"Expected ['10'], got {result}"
print("PASS")

# Test JZ with unknown label (jump not taken)
print("Test 6: JZ with unknown label (jump not taken, should be ignored)")
result = run(["PUSH 1", "JZ nowhere"])
assert result == [], f"Expected [], got {result}"
print("PASS")

# Test StackUnderflow
print("Test 7: StackUnderflow")
try:
    run(["PRINT"])
    assert False, "Should have raised StackUnderflow"
except StackUnderflow as e:
    assert "at 0" in str(e), f"Error message should contain 'at 0', got {e}"
    print(f"PASS (got expected error: {e})")

# Test BadJump
print("Test 8: BadJump")
try:
    run(["PUSH 1", "JMP nowhere"])
    assert False, "Should have raised BadJump"
except BadJump as e:
    assert "at 1" in str(e), f"Error message should contain 'at 1', got {e}"
    print(f"PASS (got expected error: {e})")

# Test error precedence: StackUnderflow before DuplicateLabel
print("Test 9: Error precedence (StackUnderflow before DuplicateLabel)")
try:
    run(["PRINT", "LABEL a", "LABEL a"])
    assert False, "Should have raised StackUnderflow"
except StackUnderflow as e:
    assert "at 0" in str(e), f"Error should be at 0, got {e}"
    print(f"PASS (got expected error: {e})")
except DuplicateLabel as e:
    assert False, f"Should raise StackUnderflow, not DuplicateLabel: {e}"

# Test more opcodes
print("Test 10: SUB operation")
result = run(["PUSH 5", "PUSH 3", "SUB", "PRINT"])
assert result == ["2"], f"Expected ['2'], got {result}"
print("PASS")

print("Test 11: MUL operation")
result = run(["PUSH 3", "PUSH 4", "MUL", "PRINT"])
assert result == ["12"], f"Expected ['12'], got {result}"
print("PASS")

print("Test 12: SWAP operation")
result = run(["PUSH 5", "PUSH 3", "SWAP", "PRINT", "PRINT"])
assert result == ["5", "3"], f"Expected ['5', '3'], got {result}"
print("PASS")

print("Test 13: DROP operation")
result = run(["PUSH 5", "PUSH 3", "DROP", "PRINT"])
assert result == ["5"], f"Expected ['5'], got {result}"
print("PASS")

# Test PUSH validation
print("Test 14: PUSH with invalid operand (1.5)")
try:
    run(["PUSH 1.5"])
    assert False, "Should have raised BadOperand"
except BadOperand as e:
    assert "at 0" in str(e), f"Error should be at 0, got {e}"
    print(f"PASS (got expected error: {e})")

print("Test 15: PUSH with invalid operand (+3)")
try:
    run(["PUSH +3"])
    assert False, "Should have raised BadOperand"
except BadOperand as e:
    assert "at 0" in str(e), f"Error should be at 0, got {e}"
    print(f"PASS (got expected error: {e})")

print("Test 16: PUSH with no operand")
try:
    run(["PUSH"])
    assert False, "Should have raised BadOperand"
except BadOperand as e:
    assert "at 0" in str(e), f"Error should be at 0, got {e}"
    print(f"PASS (got expected error: {e})")

print("Test 17: ADD with extra operand")
try:
    run(["PUSH 1", "PUSH 2", "ADD 5"])
    assert False, "Should have raised BadOperand"
except BadOperand as e:
    assert "at 2" in str(e), f"Error should be at 2, got {e}"
    print(f"PASS (got expected error: {e})")

print("Test 18: DUP with stack underflow")
try:
    run(["DUP"])
    assert False, "Should have raised StackUnderflow"
except StackUnderflow as e:
    assert "at 0" in str(e), f"Error should be at 0, got {e}"
    print(f"PASS (got expected error: {e})")

print("Test 19: Unknown opcode")
try:
    run(["FOO"])
    assert False, "Should have raised UnknownOp"
except UnknownOp as e:
    assert "at 0" in str(e), f"Error should be at 0, got {e}"
    print(f"PASS (got expected error: {e})")

print("Test 20: Empty instruction (whitespace only)")
try:
    run(["  "])
    assert False, "Should have raised UnknownOp"
except UnknownOp as e:
    assert "at 0" in str(e), f"Error should be at 0, got {e}"
    print(f"PASS (got expected error: {e})")

print("Test 21: DIV by zero")
try:
    run(["PUSH 5", "PUSH 0", "DIV"])
    assert False, "Should have raised ZeroDivisionError"
except ZeroDivisionError as e:
    print(f"PASS (got expected error: ZeroDivisionError)")

print("Test 22: Negative divisor")
result = run(["PUSH 7", "PUSH -2", "DIV", "PRINT"])
assert result == ["-3"], f"Expected ['-3'], got {result}"
print("PASS")

print("Test 23: DuplicateLabel error")
try:
    run(["LABEL a", "LABEL a"])
    assert False, "Should have raised DuplicateLabel"
except DuplicateLabel as e:
    assert "at 0" in str(e), f"Error should be at 0, got {e}"
    print(f"PASS (got expected error: {e})")

print("Test 24: JNZ (jump taken)")
result = run(["PUSH 5", "JNZ target", "PUSH 10", "PRINT", "LABEL target"])
assert result == [], f"Expected [], got {result}"
print("PASS")

print("Test 25: JNZ (jump not taken)")
result = run(["PUSH 0", "JNZ target", "PUSH 10", "PRINT", "LABEL target"])
assert result == ["10"], f"Expected ['10'], got {result}"
print("PASS")

print("\nAll tests passed!")
