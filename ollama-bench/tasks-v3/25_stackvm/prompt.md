Create `vm.py` in the current directory implementing a tiny stack-based virtual machine.

Define an exception class `VMError(Exception)` and a function `run(program: str) -> list` that executes a program and returns the list of printed integers, in the order they were printed.

**Program format.** `program` is a string of newline-separated instructions. Blank lines and lines starting with `#` are ignored. Leading/trailing whitespace on each line is stripped. Each remaining line is one instruction: an uppercase opcode, optionally followed by a single space and an argument.

**Opcodes** (the VM has an integer stack, initially empty):
- `PUSH n` — push integer `n` (`n` is an optional leading `-` then one or more digits) onto the stack.
- `POP` — pop and discard the top value.
- `ADD`, `SUB`, `MUL` — pop `b`, pop `a`, push `a+b`, `a-b`, or `a*b` respectively.
- `DIV` — pop `b`, pop `a`, push `a // b` (Python floor division). Raise `VMError` if `b == 0`.
- `DUP` — duplicate the top value.
- `SWAP` — swap the top two values.
- `PRINT` — pop the top value and append it to the output list.
- `LABEL name` — marks a jump target named `name` at this position; has no effect on the stack.
- `JMP name` — unconditionally continue execution right after the matching `LABEL name` line.
- `JZ name` — pop the top value; if it equals `0`, continue execution right after the matching `LABEL name` line; otherwise continue with the next line as normal.
- `HALT` — stop execution immediately.

**Errors** (all raise `VMError`, a program never crashes with any other exception type):
- An opcode not in the list above.
- `PUSH` with a missing or non-integer argument.
- `POP`, `ADD`, `SUB`, `MUL`, `DIV`, `DUP`, `SWAP`, `PRINT`, or `JZ` executed when the stack does not have enough values for that operation (e.g. `ADD` needs 2, `PRINT` needs 1).
- `DIV` when the divisor is `0`.
- `JMP`/`JZ` naming a label that does not exist anywhere in the program — checked once, up front, before any instruction runs (so an unreachable bad jump is still an error).
- Two `LABEL` lines with the same name anywhere in the program — checked up front.
- The program runs off the end (falls past the last line) without executing `HALT`.
- Execution takes more than 100000 instruction-steps (an infinite loop) — treat this as a `VMError` too, not a hang.

**Examples.**
```
PUSH 3
PUSH 4
ADD
PRINT
HALT
```
`run(...) == [7]`.

```
PUSH 3
LABEL loop
DUP
PRINT
PUSH 1
SUB
DUP
JZ end
JMP loop
LABEL end
HALT
```
`run(...) == [3, 2, 1]`.

```
PUSH 5
PUSH 0
DIV
HALT
```
raises `VMError`.

A program consisting of just `HALT` returns `[]`. A program that never contains `HALT` (e.g. just `PUSH 1`) raises `VMError`, even though no error opcode was hit.

Write a few quick checks of your own and run them with `python`, then reply "done".
