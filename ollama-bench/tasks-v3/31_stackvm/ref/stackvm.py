"""Reference: tiny stack virtual machine with precise error handling."""

import re

_INT = re.compile(r"-?[0-9]+")


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


def _find_label(program, name, skip=None):
    for j, ins in enumerate(program):
        if j == skip:
            continue
        p = ins.split()
        if len(p) == 2 and p[0] == "LABEL" and p[1] == name:
            return j
    return -1


def run(program):
    out = []
    stack = []
    pc = 0
    while pc < len(program):
        i = pc
        parts = program[i].split()
        op = parts[0] if parts else ""
        if op == "PUSH":
            if len(parts) != 2 or not _INT.fullmatch(parts[1]):
                raise BadOperand(f"bad operand at {i}")
            stack.append(int(parts[1]))
        elif op in ("ADD", "SUB", "MUL", "DIV"):
            if len(parts) != 1:
                raise BadOperand(f"bad operand at {i}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {i}")
            b = stack.pop()
            a = stack.pop()
            if op == "ADD":
                stack.append(a + b)
            elif op == "SUB":
                stack.append(a - b)
            elif op == "MUL":
                stack.append(a * b)
            else:
                if b == 0:
                    raise ZeroDivisionError("division by zero")
                q = abs(a) // abs(b)
                stack.append(q if (a >= 0) == (b >= 0) else -q)
        elif op == "DUP":
            if len(parts) != 1:
                raise BadOperand(f"bad operand at {i}")
            if not stack:
                raise StackUnderflow(f"stack underflow at {i}")
            stack.append(stack[-1])
        elif op == "SWAP":
            if len(parts) != 1:
                raise BadOperand(f"bad operand at {i}")
            if len(stack) < 2:
                raise StackUnderflow(f"stack underflow at {i}")
            stack[-1], stack[-2] = stack[-2], stack[-1]
        elif op == "DROP":
            if len(parts) != 1:
                raise BadOperand(f"bad operand at {i}")
            if not stack:
                raise StackUnderflow(f"stack underflow at {i}")
            stack.pop()
        elif op in ("JMP", "JZ", "JNZ"):
            if len(parts) != 2:
                raise BadOperand(f"bad operand at {i}")
            take = True
            if op != "JMP":
                if not stack:
                    raise StackUnderflow(f"stack underflow at {i}")
                take = (stack.pop() == 0) if op == "JZ" else (stack.pop() != 0)
            if take:
                j = _find_label(program, parts[1])
                if j < 0:
                    raise BadJump(f"unknown label at {i}")
                pc = j
        elif op == "LABEL":
            if len(parts) != 2:
                raise BadOperand(f"bad operand at {i}")
            if _find_label(program, parts[1], skip=i) >= 0:
                raise DuplicateLabel(f"duplicate label at {i}")
        elif op == "PRINT":
            if len(parts) != 1:
                raise BadOperand(f"bad operand at {i}")
            if not stack:
                raise StackUnderflow(f"stack underflow at {i}")
            out.append(str(stack.pop()))
        else:
            raise UnknownOp(f"unknown opcode at {i}")
        pc += 1
    return out
