Create `calc.py` in the current directory with a function `evaluate(expr: str) -> float` that evaluates arithmetic expressions given as strings.

Requirements:
- Operators `+ - * /`, parentheses, unary minus (e.g. `-3 * -2`), integer and decimal literals like `2`, `3.5`, `.5`.
- Standard precedence (`*` `/` before `+` `-`), left-to-right associativity, arbitrary whitespace.
- Return a float. Division by zero raises `ZeroDivisionError`.
- Invalid input (unbalanced parentheses, unknown characters, empty string, trailing operators like `2+`) raises `ValueError`.
- Do NOT use `eval`, `exec`, `ast`, or any third-party library. Write a real tokenizer and recursive-descent (or shunting-yard) parser.

Write a few quick checks of your own and run them with `python`, then reply "done".
