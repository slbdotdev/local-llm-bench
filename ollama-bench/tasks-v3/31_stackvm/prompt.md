Create `stackvm.py`, a tiny stack virtual machine:

```python
def run(program: list[str]) -> list[str]
```

plus exception classes defined in the module: `VMError(Exception)`, and subclasses `StackUnderflow`, `UnknownOp`, `BadOperand`, `BadJump`, `DuplicateLabel` (each a subclass of `VMError`).

Execution model:
- The instructions are the strings of `program`, executed in order by 0-based index, starting at index 0. Each instruction is split on whitespace (`instruction.split()`): the first token is the opcode, the remaining tokens are its operands. Opcodes are case-sensitive. An empty or whitespace-only instruction is an unknown opcode.
- Executing a non-jump instruction continues at the next index; a taken jump continues at the jump target; running past the last index halts. `run` returns the list of strings printed by `PRINT`, in order (it never prints to stdout).
- The stack holds arbitrary-precision Python ints (no wrapping).
- Every `VMError` message must contain the 0-based index of the offending instruction, formatted like `at 2` (e.g. `"stack underflow at 2"`).

Opcodes:
- `PUSH n` pushes the integer `n`. The operand must be an optional `-` followed by one or more ASCII digits (`PUSH 7`, `PUSH -3` are valid); anything else (`PUSH`, `PUSH x`, `PUSH 1.5`, `PUSH +3`, `PUSH 1 2`) is `BadOperand`.
- `ADD`, `SUB`, `MUL`, `DIV` pop `b` (the top value) then `a`, and push `a OP b`. So `SUB` computes the deeper value minus the top value. `DIV` truncates toward zero: `7/2 -> 3`, `-7/2 -> -3`, `7/-2 -> -3`. Division by zero raises the builtin `ZeroDivisionError`.
- `DUP` pushes a copy of the top value. `SWAP` exchanges the top two values. `DROP` discards the top value.
- `JMP L` / `JZ L` / `JNZ L`: `JZ` pops a value first and jumps only if it equals 0; `JNZ` pops first and jumps only if it is nonzero; `JMP` always jumps. The pop happens before the label check, so `JZ` on an empty stack is `StackUnderflow` even if the label is unknown, while a jump whose condition is false with an unknown label raises nothing. A taken jump continues at the first well-formed `LABEL L` instruction anywhere in the program; if no instruction defines `L`, the jump raises `BadJump`.
- `LABEL L` defines the label `L` (a single token). Executing it does nothing else. If at execution time another well-formed `LABEL L` instruction exists anywhere in the program, raise `DuplicateLabel` (checks are lazy: an error in an earlier instruction, like a stack underflow, happens first).
- `PRINT` pops a value and appends `str(value)` to the output.

Error cases (all raised at the index of the offending instruction):
- `StackUnderflow` — an opcode needs more values than the stack has.
- `UnknownOp` — the opcode is none of those above.
- `BadOperand` — wrong number of tokens for the opcode (e.g. `ADD 5`, `DUP 1`, `JMP`, `LABEL`), or a malformed `PUSH` operand.
- `BadJump` — a taken jump to a label that no instruction defines.
- `DuplicateLabel` — executing a `LABEL L` while another `LABEL L` exists anywhere in the program.

`run` never catches its own errors. The grader runs every program in a subprocess with a timeout, so a non-terminating program simply fails those checks.

Worked examples:
```python
run(["PUSH 2", "PUSH 3", "ADD", "PRINT"]) == ["5"]
run(["PUSH 7", "PUSH 2", "DIV", "PRINT"]) == ["3"]
run(["PUSH -7", "PUSH 2", "DIV", "PRINT"]) == ["-3"]
run(["PUSH 3", "LABEL top", "DUP", "PRINT", "PUSH 1", "SUB", "DUP", "JNZ top", "DROP"]) == ["3", "2", "1"]
run(["PUSH 1", "JZ end", "PUSH 10", "PRINT", "LABEL end"]) == ["10"]
run(["PUSH 1", "JZ nowhere"]) == []   # jump not taken, unknown label ignored
run(["PRINT"])          # raises StackUnderflow, message contains "at 0"
run(["PUSH 1", "JMP nowhere"])   # raises BadJump
run(["PRINT", "LABEL a", "LABEL a"])   # raises StackUnderflow (at 0), not DuplicateLabel
```

Write a few quick checks of your own and run them with `python`, then reply "done".
