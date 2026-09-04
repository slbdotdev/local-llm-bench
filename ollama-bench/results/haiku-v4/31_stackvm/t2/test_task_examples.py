#!/usr/bin/env python3

from stackvm import run, StackUnderflow, BadJump, DuplicateLabel

# Worked examples from TASK.md

print("Example 1: run(['PUSH 2', 'PUSH 3', 'ADD', 'PRINT']) == ['5']")
assert run(["PUSH 2", "PUSH 3", "ADD", "PRINT"]) == ["5"]
print("PASS")

print("Example 2: run(['PUSH 7', 'PUSH 2', 'DIV', 'PRINT']) == ['3']")
assert run(["PUSH 7", "PUSH 2", "DIV", "PRINT"]) == ["3"]
print("PASS")

print("Example 3: run(['PUSH -7', 'PUSH 2', 'DIV', 'PRINT']) == ['-3']")
assert run(["PUSH -7", "PUSH 2", "DIV", "PRINT"]) == ["-3"]
print("PASS")

print("Example 4: run(['PUSH 3', 'LABEL top', 'DUP', 'PRINT', 'PUSH 1', 'SUB', 'DUP', 'JNZ top', 'DROP']) == ['3', '2', '1']")
assert run(["PUSH 3", "LABEL top", "DUP", "PRINT", "PUSH 1", "SUB", "DUP", "JNZ top", "DROP"]) == ["3", "2", "1"]
print("PASS")

print("Example 5: run(['PUSH 1', 'JZ end', 'PUSH 10', 'PRINT', 'LABEL end']) == ['10']")
assert run(["PUSH 1", "JZ end", "PUSH 10", "PRINT", "LABEL end"]) == ["10"]
print("PASS")

print("Example 6: run(['PUSH 1', 'JZ nowhere']) == []")
assert run(["PUSH 1", "JZ nowhere"]) == []
print("PASS")

print("Example 7: run(['PRINT']) raises StackUnderflow with 'at 0'")
try:
    run(["PRINT"])
    assert False, "Should raise StackUnderflow"
except StackUnderflow as e:
    assert "at 0" in str(e)
    print(f"PASS - {e}")

print("Example 8: run(['PUSH 1', 'JMP nowhere']) raises BadJump")
try:
    run(["PUSH 1", "JMP nowhere"])
    assert False, "Should raise BadJump"
except BadJump as e:
    assert "at 1" in str(e)
    print(f"PASS - {e}")

print("Example 9: run(['PRINT', 'LABEL a', 'LABEL a']) raises StackUnderflow (at 0), not DuplicateLabel")
try:
    run(["PRINT", "LABEL a", "LABEL a"])
    assert False, "Should raise StackUnderflow"
except StackUnderflow as e:
    assert "at 0" in str(e)
    print(f"PASS - {e}")
except DuplicateLabel as e:
    assert False, f"Should raise StackUnderflow, not DuplicateLabel: {e}"

print("\nAll TASK.md examples work correctly!")
