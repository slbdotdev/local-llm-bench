class VMError(Exception):
    pass

class StackUnderflow(VMError):
    pass

class UnknownOp(VMError):
    pass

class BadOperand(VMError):
    pass

class BadJump(VMError):
    pass

class DuplicateLabel(VMError):
    pass

def run(program: list[str]) -> list[str]:
    stack = []
    output = []
    pc = 0  # program counter

    # First pass: find all well-formed labels
    labels = {}
    for i, instruction in enumerate(program):
        tokens = instruction.split()
        if tokens and tokens[0] == "LABEL" and len(tokens) == 2:
            label = tokens[1]
            if label not in labels:
                labels[label] = i

    while pc < len(program):
        instruction = program[pc]
        tokens = instruction.split()

        if not tokens:
            raise UnknownOp(f"unknown op at {pc}")

        opcode = tokens[0]
        operands = tokens[1:]

        if opcode == "PUSH":
            if len(operands) != 1:
                raise BadOperand(f"bad operand at {pc}")
            operand = operands[0]
            # Check if operand is valid: optional '-' followed by ASCII digits
            if not operand:
                raise BadOperand(f"bad operand at {pc}")
            if operand[0] == '-':
                if len(operand) == 1:
                    raise BadOperand(f"bad operand at {pc}")
                if not operand[1:].isdigit():
                    raise BadOperand(f"bad operand at {pc}")
            else:
                if not operand.isdigit():
                    raise BadOperand(f"bad operand at {pc}")
            stack.append(int(operand))

        elif opcode == "ADD":
            if len(operands) != 0:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {pc}")
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)

        elif opcode == "SUB":
            if len(operands) != 0:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {pc}")
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)

        elif opcode == "MUL":
            if len(operands) != 0:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {pc}")
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)

        elif opcode == "DIV":
            if len(operands) != 0:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {pc}")
            b = stack.pop()
            a = stack.pop()
            if b == 0:
                raise ZeroDivisionError()
            stack.append(int(a / b))

        elif opcode == "DUP":
            if len(operands) != 0:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"stack underflow at {pc}")
            stack.append(stack[-1])

        elif opcode == "SWAP":
            if len(operands) != 0:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {pc}")
            stack[-1], stack[-2] = stack[-2], stack[-1]

        elif opcode == "DROP":
            if len(operands) != 0:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"stack underflow at {pc}")
            stack.pop()

        elif opcode == "JMP":
            if len(operands) != 1:
                raise BadOperand(f"bad operand at {pc}")
            label = operands[0]
            if label not in labels:
                raise BadJump(f"bad jump at {pc}")
            pc = labels[label]
            continue

        elif opcode == "JZ":
            if len(operands) != 1:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"stack underflow at {pc}")
            value = stack.pop()
            label = operands[0]
            if value == 0:
                if label not in labels:
                    raise BadJump(f"bad jump at {pc}")
                pc = labels[label]
                continue

        elif opcode == "JNZ":
            if len(operands) != 1:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"stack underflow at {pc}")
            value = stack.pop()
            label = operands[0]
            if value != 0:
                if label not in labels:
                    raise BadJump(f"bad jump at {pc}")
                pc = labels[label]
                continue

        elif opcode == "LABEL":
            if len(operands) != 1:
                raise BadOperand(f"bad operand at {pc}")
            label = operands[0]
            # Check for duplicate labels
            count = 0
            for i, inst in enumerate(program):
                tokens = inst.split()
                if tokens and tokens[0] == "LABEL" and len(tokens) == 2 and tokens[1] == label:
                    count += 1
            if count > 1:
                raise DuplicateLabel(f"duplicate label at {pc}")

        elif opcode == "PRINT":
            if len(operands) != 0:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"stack underflow at {pc}")
            value = stack.pop()
            output.append(str(value))

        else:
            raise UnknownOp(f"unknown op at {pc}")

        pc += 1

    return output
