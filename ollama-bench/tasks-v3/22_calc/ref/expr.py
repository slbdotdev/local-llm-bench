import re

def evaluate(text: str) -> float:
    """
    Parse and evaluate a simple arithmetic expression.
    Supports +, -, *, / with proper precedence and left-associativity.
    """
    if not text or not text.strip():
        raise ValueError("empty expression")

    # Tokenize: split into numbers and operators
    tokens = re.findall(r'\d+\.?\d*|[+\-*/]', text)

    if not tokens:
        raise ValueError("no valid tokens found")

    # Validate token sequence
    if tokens[0] in ['+', '-', '*', '/']:
        raise ValueError("expression cannot start with operator")
    if tokens[-1] in ['+', '-', '*', '/']:
        raise ValueError("expression cannot end with operator")

    # Check alternation between operands and operators
    is_operand = [t not in ['+', '-', '*', '/'] for t in tokens]
    for i in range(len(tokens) - 1):
        if is_operand[i] == is_operand[i + 1]:
            if is_operand[i]:
                raise ValueError("missing operator between operands")
            else:
                raise ValueError("consecutive operators")

    # Parse numbers
    try:
        numbers = [float(t) if t not in ['+', '-', '*', '/'] else t for t in tokens]
    except ValueError:
        raise ValueError("invalid number format")

    # First pass: handle * and / (higher precedence)
    i = 1
    while i < len(numbers):
        if numbers[i] == '*':
            result = numbers[i - 1] * numbers[i + 1]
            numbers = numbers[:i - 1] + [result] + numbers[i + 2:]
        elif numbers[i] == '/':
            if numbers[i + 1] == 0:
                raise ZeroDivisionError("division by zero")
            result = numbers[i - 1] / numbers[i + 1]
            numbers = numbers[:i - 1] + [result] + numbers[i + 2:]
        else:
            i += 2

    # Second pass: handle + and - (lower precedence, left-to-right)
    result = numbers[0]
    i = 1
    while i < len(numbers):
        op = numbers[i]
        operand = numbers[i + 1]
        if op == '+':
            result += operand
        elif op == '-':
            result -= operand
        i += 2

    return result
