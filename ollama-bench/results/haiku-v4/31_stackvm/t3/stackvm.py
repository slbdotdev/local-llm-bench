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
    """Execute a stack virtual machine program."""
    stack = []
    output = []
    pc = 0  # program counter

    while pc < len(program):
        instruction = program[pc]
        tokens = instruction.split()

        if not tokens:
            raise UnknownOp(f"unknown opcode at {pc}")

        opcode = tokens[0]
        operands = tokens[1:]

        if opcode == "PUSH":
            if len(operands) != 1:
                raise BadOperand(f"bad operand at {pc}")
            operand = operands[0]
            # Must be optional - followed by one or more digits
            if operand.startswith('-'):
                if len(operand) == 1 or not operand[1:].isdigit():
                    raise BadOperand(f"bad operand at {pc}")
            else:
                if not operand or not operand.isdigit():
                    raise BadOperand(f"bad operand at {pc}")
            stack.append(int(operand))
            pc += 1

        elif opcode == "ADD":
            if operands:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {pc}")
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
            pc += 1

        elif opcode == "SUB":
            if operands:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {pc}")
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)
            pc += 1

        elif opcode == "MUL":
            if operands:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {pc}")
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)
            pc += 1

        elif opcode == "DIV":
            if operands:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {pc}")
            b = stack.pop()
            a = stack.pop()
            stack.append(int(a / b))  # Truncate toward zero
            pc += 1

        elif opcode == "DUP":
            if operands:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"stack underflow at {pc}")
            stack.append(stack[-1])
            pc += 1

        elif opcode == "SWAP":
            if operands:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {pc}")
            stack[-1], stack[-2] = stack[-2], stack[-1]
            pc += 1

        elif opcode == "DROP":
            if operands:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"stack underflow at {pc}")
            stack.pop()
            pc += 1

        elif opcode == "JMP":
            if len(operands) != 1:
                raise BadOperand(f"bad operand at {pc}")
            label = operands[0]
            # Find the label
            target_pc = None
            for i, inst in enumerate(program):
                inst_tokens = inst.split()
                if inst_tokens and inst_tokens[0] == "LABEL" and len(inst_tokens) == 2 and inst_tokens[1] == label:
                    target_pc = i
                    break
            if target_pc is None:
                raise BadJump(f"bad jump at {pc}")
            pc = target_pc

        elif opcode == "JZ":
            if len(operands) != 1:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"stack underflow at {pc}")
            value = stack.pop()
            label = operands[0]
            if value == 0:
                # Find the label
                target_pc = None
                for i, inst in enumerate(program):
                    inst_tokens = inst.split()
                    if inst_tokens and inst_tokens[0] == "LABEL" and len(inst_tokens) == 2 and inst_tokens[1] == label:
                        target_pc = i
                        break
                if target_pc is None:
                    raise BadJump(f"bad jump at {pc}")
                pc = target_pc
            else:
                pc += 1

        elif opcode == "JNZ":
            if len(operands) != 1:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"stack underflow at {pc}")
            value = stack.pop()
            label = operands[0]
            if value != 0:
                # Find the label
                target_pc = None
                for i, inst in enumerate(program):
                    inst_tokens = inst.split()
                    if inst_tokens and inst_tokens[0] == "LABEL" and len(inst_tokens) == 2 and inst_tokens[1] == label:
                        target_pc = i
                        break
                if target_pc is None:
                    raise BadJump(f"bad jump at {pc}")
                pc = target_pc
            else:
                pc += 1

        elif opcode == "LABEL":
            if len(operands) != 1:
                raise BadOperand(f"bad operand at {pc}")
            label = operands[0]
            # Check if another well-formed LABEL with this name exists
            count = 0
            for inst in program:
                inst_tokens = inst.split()
                if inst_tokens and inst_tokens[0] == "LABEL" and len(inst_tokens) == 2 and inst_tokens[1] == label:
                    count += 1
            if count > 1:
                raise DuplicateLabel(f"duplicate label at {pc}")
            pc += 1

        elif opcode == "PRINT":
            if operands:
                raise BadOperand(f"bad operand at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"stack underflow at {pc}")
            value = stack.pop()
            output.append(str(value))
            pc += 1

        else:
            raise UnknownOp(f"unknown opcode at {pc}")

    return output
