#!/usr/bin/env python3
from stackvm import run, VMError, StackUnderflow, UnknownOp, BadOperand, BadJump, DuplicateLabel

def test_basic_arithmetic():
    """Test basic arithmetic operations"""
    assert run(["PUSH 2", "PUSH 3", "ADD", "PRINT"]) == ["5"]
    print("✓ Basic ADD works")

def test_division():
    """Test division with truncation toward zero"""
    assert run(["PUSH 7", "PUSH 2", "DIV", "PRINT"]) == ["3"]
    print("✓ DIV 7/2 = 3")

    assert run(["PUSH -7", "PUSH 2", "DIV", "PRINT"]) == ["-3"]
    print("✓ DIV -7/2 = -3")

def test_loop():
    """Test loop with label and conditional jump"""
    result = run(["PUSH 3", "LABEL top", "DUP", "PRINT", "PUSH 1", "SUB", "DUP", "JNZ top", "DROP"])
    assert result == ["3", "2", "1"]
    print("✓ Loop with JNZ works")

def test_conditional_jump_not_taken():
    """Test conditional jump that doesn't execute"""
    assert run(["PUSH 1", "JZ end", "PUSH 10", "PRINT", "LABEL end"]) == ["10"]
    print("✓ JZ not taken continues normally")

def test_unknown_label_ignored_when_not_jumping():
    """Test that unknown labels don't cause errors if jump is not taken"""
    assert run(["PUSH 1", "JZ nowhere"]) == []
    print("✓ Unknown label ignored when jump not taken")

def test_bad_jump():
    """Test that bad jumps raise BadJump"""
    try:
        run(["PUSH 1", "JMP nowhere"])
        assert False, "Should have raised BadJump"
    except BadJump as e:
        assert "at 1" in str(e)
        print("✓ BadJump raised correctly for taken jump to unknown label")

def test_stack_underflow():
    """Test that stack underflow is raised before duplicate label check"""
    try:
        run(["PRINT", "LABEL a", "LABEL a"])
        assert False, "Should have raised StackUnderflow"
    except StackUnderflow as e:
        assert "at 0" in str(e)
        print("✓ StackUnderflow at 0 raised (before DuplicateLabel)")

def test_stack_underflow_at_print():
    """Test stack underflow on PRINT"""
    try:
        run(["PRINT"])
        assert False, "Should have raised StackUnderflow"
    except StackUnderflow as e:
        assert "at 0" in str(e)
        print("✓ StackUnderflow at PRINT")

def test_dup():
    """Test DUP operation"""
    assert run(["PUSH 5", "DUP", "PRINT", "PRINT"]) == ["5", "5"]
    print("✓ DUP works")

def test_swap():
    """Test SWAP operation"""
    assert run(["PUSH 1", "PUSH 2", "SWAP", "PRINT", "PRINT"]) == ["1", "2"]
    print("✓ SWAP works")

def test_drop():
    """Test DROP operation"""
    assert run(["PUSH 1", "PUSH 2", "DROP", "PRINT"]) == ["1"]
    print("✓ DROP works")

def test_sub():
    """Test SUB operation (a - b where b is on top)"""
    assert run(["PUSH 10", "PUSH 3", "SUB", "PRINT"]) == ["7"]
    print("✓ SUB works (10 - 3 = 7)")

def test_mul():
    """Test MUL operation"""
    assert run(["PUSH 3", "PUSH 4", "MUL", "PRINT"]) == ["12"]
    print("✓ MUL works")

def test_bad_push_operand():
    """Test various invalid PUSH operands"""
    try:
        run(["PUSH"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 0" in str(e)
        print("✓ BadOperand for PUSH with no operand")

    try:
        run(["PUSH x"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 0" in str(e)
        print("✓ BadOperand for PUSH x")

    try:
        run(["PUSH 1.5"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 0" in str(e)
        print("✓ BadOperand for PUSH 1.5")

    try:
        run(["PUSH +3"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 0" in str(e)
        print("✓ BadOperand for PUSH +3")

    try:
        run(["PUSH 1 2"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 0" in str(e)
        print("✓ BadOperand for PUSH 1 2")

def test_bad_add_operand():
    """Test ADD with operand"""
    try:
        run(["PUSH 1", "PUSH 2", "ADD 5"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 2" in str(e)
        print("✓ BadOperand for ADD with operand")

def test_unknown_opcode():
    """Test unknown opcode"""
    try:
        run(["UNKNOWN"])
        assert False, "Should have raised UnknownOp"
    except UnknownOp as e:
        assert "at 0" in str(e)
        print("✓ UnknownOp for unknown opcode")

def test_zero_division():
    """Test division by zero"""
    try:
        run(["PUSH 1", "PUSH 0", "DIV"])
        assert False, "Should have raised ZeroDivisionError"
    except ZeroDivisionError:
        print("✓ ZeroDivisionError raised for division by zero")

def test_negative_numbers():
    """Test negative number handling"""
    assert run(["PUSH -5", "PRINT"]) == ["-5"]
    print("✓ Negative numbers work")

def test_large_numbers():
    """Test arbitrary precision integers"""
    assert run(["PUSH 999999999999999999", "PRINT"]) == ["999999999999999999"]
    print("✓ Large arbitrary precision numbers work")

def test_jnz_taken():
    """Test JNZ when condition is true"""
    result = run(["PUSH 1", "JNZ skip", "PUSH 999", "PRINT", "LABEL skip", "PUSH 10", "PRINT"])
    assert result == ["10"]
    print("✓ JNZ jumps when nonzero")

def test_jz_taken():
    """Test JZ when condition is true"""
    result = run(["PUSH 0", "JZ skip", "PUSH 999", "PRINT", "LABEL skip", "PUSH 10", "PRINT"])
    assert result == ["10"]
    print("✓ JZ jumps when zero")

if __name__ == "__main__":
    test_basic_arithmetic()
    test_division()
    test_loop()
    test_conditional_jump_not_taken()
    test_unknown_label_ignored_when_not_jumping()
    test_bad_jump()
    test_stack_underflow()
    test_stack_underflow_at_print()
    test_dup()
    test_swap()
    test_drop()
    test_sub()
    test_mul()
    test_bad_push_operand()
    test_bad_add_operand()
    test_unknown_opcode()
    test_zero_division()
    test_negative_numbers()
    test_large_numbers()
    test_jnz_taken()
    test_jz_taken()
    print("\n✅ All tests passed!")
