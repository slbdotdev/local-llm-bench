#!/usr/bin/env python3
from stackvm import run, BadOperand, StackUnderflow

def test_empty_instruction():
    """Test empty instruction (should raise UnknownOp)"""
    from stackvm import UnknownOp
    try:
        run(["PUSH 5", "", "PRINT"])
        assert False, "Should have raised UnknownOp"
    except UnknownOp as e:
        assert "at 1" in str(e)
        print("✓ Empty instruction raises UnknownOp")

def test_whitespace_only_instruction():
    """Test whitespace-only instruction"""
    from stackvm import UnknownOp
    try:
        run(["PUSH 5", "   ", "PRINT"])
        assert False, "Should have raised UnknownOp"
    except UnknownOp as e:
        assert "at 1" in str(e)
        print("✓ Whitespace-only instruction raises UnknownOp")

def test_label_without_operand():
    """Test LABEL without operand"""
    try:
        run(["LABEL"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 0" in str(e)
        print("✓ LABEL without operand raises BadOperand")

def test_label_with_multiple_operands():
    """Test LABEL with multiple operands"""
    try:
        run(["LABEL a b"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 0" in str(e)
        print("✓ LABEL with multiple operands raises BadOperand")

def test_jmp_without_operand():
    """Test JMP without label"""
    try:
        run(["JMP"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 0" in str(e)
        print("✓ JMP without operand raises BadOperand")

def test_jz_without_operand():
    """Test JZ without label"""
    try:
        run(["PUSH 0", "JZ"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 1" in str(e)
        print("✓ JZ without operand raises BadOperand")

def test_jnz_without_operand():
    """Test JNZ without label"""
    try:
        run(["PUSH 0", "JNZ"])
        assert False, "Should have raised BadOperand"
    except BadOperand as e:
        assert "at 1" in str(e)
        print("✓ JNZ without operand raises BadOperand")

def test_dup_without_stack():
    """Test DUP on empty stack"""
    try:
        run(["DUP"])
        assert False, "Should have raised StackUnderflow"
    except StackUnderflow as e:
        assert "at 0" in str(e)
        print("✓ DUP on empty stack raises StackUnderflow")

def test_swap_with_one_item():
    """Test SWAP with only one item on stack"""
    try:
        run(["PUSH 1", "SWAP"])
        assert False, "Should have raised StackUnderflow"
    except StackUnderflow as e:
        assert "at 1" in str(e)
        print("✓ SWAP with one item raises StackUnderflow")

def test_drop_without_stack():
    """Test DROP on empty stack"""
    try:
        run(["DROP"])
        assert False, "Should have raised StackUnderflow"
    except StackUnderflow as e:
        assert "at 0" in str(e)
        print("✓ DROP on empty stack raises StackUnderflow")

def test_multiple_prints():
    """Test multiple PRINT operations"""
    result = run(["PUSH 1", "PRINT", "PUSH 2", "PRINT", "PUSH 3", "PRINT"])
    assert result == ["1", "2", "3"]
    print("✓ Multiple prints work correctly")

def test_complex_arithmetic():
    """Test complex arithmetic: (10 - 3) * 2"""
    result = run(["PUSH 10", "PUSH 3", "SUB", "PUSH 2", "MUL", "PRINT"])
    assert result == ["14"]
    print("✓ Complex arithmetic (10 - 3) * 2 = 14")

def test_zero_push():
    """Test pushing zero"""
    result = run(["PUSH 0", "PRINT"])
    assert result == ["0"]
    print("✓ PUSH 0 works")

def test_jz_with_zero():
    """Test JZ jumps when value is zero"""
    result = run(["PUSH 0", "JZ target", "PUSH 999", "PRINT", "LABEL target", "PUSH 5", "PRINT"])
    assert result == ["5"]
    print("✓ JZ jumps correctly with zero value")

def test_jnz_with_negative():
    """Test JNZ with negative number"""
    result = run(["PUSH -5", "JNZ target", "PUSH 999", "PRINT", "LABEL target", "PUSH 10", "PRINT"])
    assert result == ["10"]
    print("✓ JNZ jumps with negative nonzero value")

def test_negative_arithmetic():
    """Test arithmetic with negative numbers"""
    result = run(["PUSH -5", "PUSH -3", "ADD", "PRINT"])
    assert result == ["-8"]
    print("✓ Addition with negative numbers: -5 + -3 = -8")

def test_push_zero_leading_digits():
    """Test PUSH 0 and other valid forms"""
    result = run(["PUSH 0", "PRINT", "PUSH 007", "PRINT"])
    # Note: "007" is interpreted as the integer 7
    assert result == ["0", "7"]
    print("✓ PUSH with leading zeros works")

if __name__ == "__main__":
    test_empty_instruction()
    test_whitespace_only_instruction()
    test_label_without_operand()
    test_label_with_multiple_operands()
    test_jmp_without_operand()
    test_jz_without_operand()
    test_jnz_without_operand()
    test_dup_without_stack()
    test_swap_with_one_item()
    test_drop_without_stack()
    test_multiple_prints()
    test_complex_arithmetic()
    test_zero_push()
    test_jz_with_zero()
    test_jnz_with_negative()
    test_negative_arithmetic()
    test_push_zero_leading_digits()
    print("\n✅ All edge case tests passed!")
