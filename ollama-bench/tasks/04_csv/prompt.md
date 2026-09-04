Create `csvlite.py` in the current directory with a function `parse(text: str) -> list[list[str]]` that parses RFC 4180 style CSV text into rows of string fields.

Requirements:
- Fields are separated by commas; records by `\n` or `\r\n`.
- A field may be wrapped in double quotes. Inside quotes, commas and newlines are literal, and a doubled quote `""` means one literal `"` character.
- Unquoted empty fields are empty strings (`a,,b` -> `["a", "", "b"]`). A line with nothing at all between separators like `,` is `["", ""]`.
- A trailing newline at the end of the text does not produce an extra empty record, and an empty input returns `[]`.
- Leading/trailing spaces in unquoted fields are preserved as-is.
- Do NOT import the standard `csv` module; implement the state machine yourself.

Write a few quick checks of your own and run them with `python`, then reply "done".
