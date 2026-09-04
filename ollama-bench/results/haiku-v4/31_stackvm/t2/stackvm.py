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
    defined_labels = set()  # Track labels defined during execution

    # Helper to validate PUSH operand
    def is_valid_int(s):
        if not s:
            return False
        if s[0] == '-':
            return s[1:].isdigit() and len(s) > 1
        else:
            return s.isdigit()

    # Helper for truncation toward zero division
    def truncate_div(a, b):
        if b == 0:
            raise ZeroDivisionError()
        q = abs(a) // abs(b)
        if (a < 0) != (b < 0):
            q = -q
        return q

    # First pass: scan for all well-formed labels to handle backward references and duplicate detection
    all_labels = {}
    for i, instruction in enumerate(program):
        tokens = instruction.split()
        if tokens and tokens[0] == "LABEL" and len(tokens) == 2:
            label_name = tokens[1]
            if label_name not in all_labels:
                all_labels[label_name] = []
            all_labels[label_name].append(i)

    # Execution
    while pc < len(program):
        instruction = program[pc]
        tokens = instruction.split()

        if not tokens:
            raise UnknownOp(f"at {pc}")

        opcode = tokens[0]

        if opcode == "PUSH":
            if len(tokens) != 2:
                raise BadOperand(f"at {pc}")
            operand = tokens[1]
            if not is_valid_int(operand):
                raise BadOperand(f"at {pc}")
            value = int(operand)
            stack.append(value)
            pc += 1

        elif opcode == "ADD":
            if len(tokens) != 1:
                raise BadOperand(f"at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"at {pc}")
            b = stack.pop()
            a = stack.pop()
            stack.append(a + b)
            pc += 1

        elif opcode == "SUB":
            if len(tokens) != 1:
                raise BadOperand(f"at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"at {pc}")
            b = stack.pop()
            a = stack.pop()
            stack.append(a - b)
            pc += 1

        elif opcode == "MUL":
            if len(tokens) != 1:
                raise BadOperand(f"at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"at {pc}")
            b = stack.pop()
            a = stack.pop()
            stack.append(a * b)
            pc += 1

        elif opcode == "DIV":
            if len(tokens) != 1:
                raise BadOperand(f"at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"at {pc}")
            b = stack.pop()
            a = stack.pop()
            result = truncate_div(a, b)
            stack.append(result)
            pc += 1

        elif opcode == "DUP":
            if len(tokens) != 1:
                raise BadOperand(f"at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"at {pc}")
            stack.append(stack[-1])
            pc += 1

        elif opcode == "SWAP":
            if len(tokens) != 1:
                raise BadOperand(f"at {pc}")
            if len(stack) < 2:
                raise StackUnderflow(f"at {pc}")
            stack[-1], stack[-2] = stack[-2], stack[-1]
            pc += 1

        elif opcode == "DROP":
            if len(tokens) != 1:
                raise BadOperand(f"at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"at {pc}")
            stack.pop()
            pc += 1

        elif opcode == "JMP":
            if len(tokens) != 2:
                raise BadOperand(f"at {pc}")
            label_name = tokens[1]
            if label_name not in all_labels:
                raise BadJump(f"at {pc}")
            pc = all_labels[label_name][0]

        elif opcode == "JZ":
            if len(tokens) != 2:
                raise BadOperand(f"at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"at {pc}")
            value = stack.pop()
            label_name = tokens[1]
            if value == 0:
                if label_name not in all_labels:
                    raise BadJump(f"at {pc}")
                pc = all_labels[label_name][0]
            else:
                pc += 1

        elif opcode == "JNZ":
            if len(tokens) != 2:
                raise BadOperand(f"at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"at {pc}")
            value = stack.pop()
            label_name = tokens[1]
            if value != 0:
                if label_name not in all_labels:
                    raise BadJump(f"at {pc}")
                pc = all_labels[label_name][0]
            else:
                pc += 1

        elif opcode == "LABEL":
            if len(tokens) != 2:
                raise BadOperand(f"at {pc}")
            label_name = tokens[1]
            # Check if this label has multiple definitions in the program
            if label_name in all_labels and len(all_labels[label_name]) > 1:
                raise DuplicateLabel(f"at {pc}")
            pc += 1

        elif opcode == "PRINT":
            if len(tokens) != 1:
                raise BadOperand(f"at {pc}")
            if len(stack) < 1:
                raise StackUnderflow(f"at {pc}")
            value = stack.pop()
            output.append(str(value))
            pc += 1

        else:
            raise UnknownOp(f"at {pc}")

    return output
