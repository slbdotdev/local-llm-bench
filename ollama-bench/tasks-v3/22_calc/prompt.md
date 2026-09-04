Create `expr.py` with a function `evaluate(text: str) -> float` that parses and evaluates simple arithmetic expressions.

Rules:
- Operators: `+`, `-`, `*`, `/` (left-associative)
- Operator precedence: `*` and `/` bind tighter than `+` and `-`
- Operands: non-negative integers and floats (e.g., `42`, `3.14`)
- Unary minus is NOT supported; use subtraction instead.
- Whitespace is ignored; expressions can have spaces anywhere.
- The `-` character can only appear as a binary operator (between operands/expressions), not as unary.
- If division by zero is attempted, raise `ZeroDivisionError` with message "division by zero".
- If the input is malformed (missing operand, trailing operator, invalid syntax, etc.), raise `ValueError` with a descriptive message.
- Empty string raises `ValueError`.
- Matching parentheses for grouping are NOT required (keep it simple).

Examples:
- `evaluate("2 + 3 * 4")` → `14.0` (multiplication first)
- `evaluate("10 - 5 - 2")` → `3.0` (left-associative)
- `evaluate("6 / 2")` → `3.0`
- `evaluate("10 / 0")` → raises ZeroDivisionError
- `evaluate("2 +")` → raises ValueError
- `evaluate("")` → raises ValueError
- `evaluate("3.5 + 2.5")` → `6.0`

Write a few quick checks of your own and run them with `python`, then reply "done".
