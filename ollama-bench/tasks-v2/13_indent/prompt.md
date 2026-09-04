Create `indent.py` in the current directory with a function `tokenize(src: str) -> list[tuple[str, str]]` that turns Python-like indented source into a token stream, following these rules exactly:

- Process the source line by line. Lines that are empty or contain only whitespace, and lines whose first non-space character is `#`, are ignored completely (they produce no tokens and do not affect indentation).
- Indentation is measured in leading space characters. A tab character in leading whitespace raises `ValueError`.
- For each significant line, compare its indentation with the top of an indentation stack (which starts as `[0]`):
  - Greater: push it and emit `("INDENT", "")`.
  - Smaller: pop until the top equals the new indentation, emitting one `("DEDENT", "")` per pop. If no stack entry equals the new indentation, raise `ValueError("inconsistent dedent")`.
  - Equal: nothing.
- Then emit `("LINE", text)` where `text` is the line with leading indentation removed and trailing whitespace stripped, and an inline comment (a `#` and everything after it, but not a `#` inside single or double quotes) removed, then trailing whitespace stripped again.
- After the last line, emit one `("DEDENT", "")` for each stack entry above 0, then `("EOF", "")`.

Example: `tokenize("a\n  b\n    c\n  d\ne\n")` returns
`[("LINE","a"),("INDENT",""),("LINE","b"),("INDENT",""),("LINE","c"),("DEDENT",""),("LINE","d"),("DEDENT",""),("LINE","e"),("EOF","")]`.

Write a few quick checks of your own and run them with `python`, then reply "done".
