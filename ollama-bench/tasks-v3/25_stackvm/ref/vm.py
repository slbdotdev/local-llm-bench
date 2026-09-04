class VMError(Exception):
    pass


_NEEDS_ARG = {"PUSH", "LABEL", "JMP", "JZ"}
_NO_ARG = {"POP", "ADD", "SUB", "MUL", "DIV", "DUP", "SWAP", "PRINT", "HALT"}
_ALL_OPS = _NEEDS_ARG | _NO_ARG
_STACK_NEEDS = {"POP": 1, "ADD": 2, "SUB": 2, "MUL": 2, "DIV": 2, "DUP": 1, "SWAP": 2, "PRINT": 1, "JZ": 1}
_MAX_STEPS = 100000


def _parse_int(s):
    if s is None or not (s.lstrip("-").isdigit() and s not in ("", "-")):
        return None
    return int(s)


def run(program: str) -> list:
    instrs = []
    for raw in program.split("\n"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if " " in line:
            op, arg = line.split(" ", 1)
            arg = arg.strip()
        else:
            op, arg = line, None
        if op not in _ALL_OPS:
            raise VMError(f"unknown instruction: {op}")
        if op in _NEEDS_ARG and (arg is None or arg == ""):
            raise VMError(f"{op} requires an argument")
        if op in _NO_ARG and arg not in (None, ""):
            raise VMError(f"{op} takes no argument")
        if op == "PUSH":
            n = _parse_int(arg)
            if n is None:
                raise VMError(f"PUSH requires an integer argument, got {arg!r}")
            instrs.append((op, n))
        else:
            instrs.append((op, arg))

    labels = {}
    for i, (op, arg) in enumerate(instrs):
        if op == "LABEL":
            if arg in labels:
                raise VMError(f"duplicate label: {arg}")
            labels[arg] = i
    for op, arg in instrs:
        if op in ("JMP", "JZ") and arg not in labels:
            raise VMError(f"undefined label: {arg}")

    stack = []
    output = []
    pc = 0
    steps = 0
    halted = False
    while pc < len(instrs):
        steps += 1
        if steps > _MAX_STEPS:
            raise VMError("step limit exceeded")
        op, arg = instrs[pc]
        need = _STACK_NEEDS.get(op)
        if need is not None and len(stack) < need:
            raise VMError(f"stack underflow: {op}")
        if op == "PUSH":
            stack.append(arg)
        elif op == "POP":
            stack.pop()
        elif op == "ADD":
            b = stack.pop(); a = stack.pop(); stack.append(a + b)
        elif op == "SUB":
            b = stack.pop(); a = stack.pop(); stack.append(a - b)
        elif op == "MUL":
            b = stack.pop(); a = stack.pop(); stack.append(a * b)
        elif op == "DIV":
            b = stack.pop(); a = stack.pop()
            if b == 0:
                raise VMError("division by zero")
            stack.append(a // b)
        elif op == "DUP":
            stack.append(stack[-1])
        elif op == "SWAP":
            stack[-1], stack[-2] = stack[-2], stack[-1]
        elif op == "PRINT":
            output.append(stack.pop())
        elif op == "LABEL":
            pass
        elif op == "JMP":
            pc = labels[arg]
        elif op == "JZ":
            v = stack.pop()
            if v == 0:
                pc = labels[arg]
        elif op == "HALT":
            halted = True
            break
        pc += 1

    if not halted:
        raise VMError("program did not HALT")
    return output
