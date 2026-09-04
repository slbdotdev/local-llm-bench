#!/usr/bin/env python3

from stackvm import run, StackUnderflow, UnknownOp, BadOperand, BadJump, DuplicateLabel

# Test large numbers (arbitrary precision)
print("Test 1: Large numbers")
result = run(["PUSH 99999999999999999999", "PUSH 1", "ADD", "PRINT"])
assert result == ["100000000000000000000"], f"Expected ['100000000000000000000'], got {result}"
print("PASS")

# Test negative numbers
print("Test 2: Negative large numbers")
result = run(["PUSH -99999999999999999999", "PUSH 1", "ADD", "PRINT"])
assert result == ["-99999999999999999998"], f"Expected ['-99999999999999999998'], got {result}"
print("PASS")

# Test multiple PUSHes and multiple PRINTs
print("Test 3: Multiple prints")
result = run(["PUSH 1", "PUSH 2", "PUSH 3", "PRINT", "PRINT", "PRINT"])
assert result == ["3", "2", "1"], f"Expected ['3', '2', '1'], got {result}"
print("PASS")

# Test backward jump
print("Test 4: Backward jump loop")
result = run(["PUSH 2", "LABEL loop", "DUP", "PRINT", "PUSH 1", "SUB", "DUP", "JNZ loop", "DROP"])
assert result == ["2", "1"], f"Expected ['2', '1'], got {result}"
print("PASS")

# Test JMP always jumps
print("Test 5: JMP always jumps")
result = run(["JMP target", "PUSH 1", "PRINT", "LABEL target"])
assert result == [], f"Expected [], got {result}"
print("PASS")

# Test SWAP before arithmetic
print("Test 6: SWAP and SUB")
result = run(["PUSH 3", "PUSH 5", "SWAP", "SUB", "PRINT"])
assert result == ["2"], f"Expected ['2'], got {result}"  # 3 - 5 = -2... wait that's wrong
# Let me recalculate: PUSH 3, PUSH 5 -> stack=[3, 5] (5 on top)
# SWAP -> stack=[5, 3] (3 on top)
# SUB pops 3, then pops 5, computes 5 - 3 = 2
# Hmm, that doesn't match my expectation
# Actually: SUB pops b (top), then pops a (next), computes a - b
# So: b = 3, a = 5, a - b = 5 - 3 = 2
print("PASS")

# Test zero in various contexts
print("Test 7: Zero arithmetic")
result = run(["PUSH 0", "PUSH 5", "ADD", "PRINT"])
assert result == ["5"], f"Expected ['5'], got {result}"
print("PASS")

# Test zero with JZ
print("Test 8: Zero with JZ")
result = run(["PUSH 0", "JZ target", "PUSH 1", "PRINT", "LABEL target"])
assert result == [], f"Expected [], got {result}"
print("PASS")

# Test negative zero (there's no such thing in integers, but let's verify)
print("Test 9: Negative zero")
result = run(["PUSH -0", "PRINT"])
assert result == ["0"], f"Expected ['0'], got {result}"
print("PASS")

# Test operations preserve deep values
print("Test 10: DROP preserves stack below")
result = run(["PUSH 1", "PUSH 2", "PUSH 3", "DROP", "PRINT", "PRINT"])
assert result == ["2", "1"], f"Expected ['2', '1'], got {result}"
print("PASS")

# Test PUSH with leading zeros
print("Test 11: PUSH with leading zeros")
result = run(["PUSH 0007", "PRINT"])
assert result == ["7"], f"Expected ['7'], got {result}"
print("PASS")

# Test PUSH with single zero
print("Test 12: PUSH 0")
result = run(["PUSH 0", "PRINT"])
assert result == ["0"], f"Expected ['0'], got {result}"
print("PASS")

# Test DIV with negative quotient
print("Test 13: DIV negative quotient")
result = run(["PUSH -7", "PUSH -2", "DIV", "PRINT"])
assert result == ["3"], f"Expected ['3'], got {result}"
print("PASS")

# Test multiple labels, only one used
print("Test 14: Multiple labels, one used")
result = run(["JMP end", "LABEL a", "PUSH 1", "PRINT", "LABEL end"])
assert result == [], f"Expected [], got {result}"
print("PASS")

# Test LABEL does nothing on execution
print("Test 15: LABEL by itself")
result = run(["LABEL here"])
assert result == [], f"Expected [], got {result}"
print("PASS")

# Test condition 0 vs 1
print("Test 16: JNZ with 1")
result = run(["PUSH 1", "JNZ target", "PUSH 1", "PRINT", "LABEL target"])
assert result == [], f"Expected [], got {result}"
print("PASS")

# Test condition negative number (should jump)
print("Test 17: JNZ with negative")
result = run(["PUSH -5", "JNZ target", "PUSH 1", "PRINT", "LABEL target"])
assert result == [], f"Expected [], got {result}"
print("PASS")

# Test empty program
print("Test 18: Empty program")
result = run([])
assert result == [], f"Expected [], got {result}"
print("PASS")

# Test single PRINT without push (should error)
print("Test 19: PRINT underflow")
try:
    run(["PRINT"])
    assert False, "Should raise StackUnderflow"
except StackUnderflow:
    print("PASS")

# Test MUL by zero
print("Test 20: MUL by zero")
result = run(["PUSH 5", "PUSH 0", "MUL", "PRINT"])
assert result == ["0"], f"Expected ['0'], got {result}"
print("PASS")

print("\nAll edge case tests passed!")
