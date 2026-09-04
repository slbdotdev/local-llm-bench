Create `csvparse.py` with a function `parse_csv(text: str) -> list[list[str]]` that parses RFC 4180 CSV.

Rules:
- Split input by lines (handling both `\n` and `\r\n`). Each line is one record (list of fields).
- Fields are separated by commas. Fields may be quoted with `"` or unquoted.
- Quoted fields can contain commas, newlines, and literal `"` (escaped as `""`). Quotes outside fields or unescaped inside unquoted fields are errors.
- A `\r\n` inside a quoted field is preserved verbatim as `\r\n` (do not normalise line endings inside quoted fields).
- Unquoted fields must not contain quotes or newlines. Leading/trailing spaces in unquoted fields are kept.
- An empty input returns an empty list. A file with just one empty line returns `[[""]]`.
- If a field starts with `"`, it must end with an unescaped `"`. Malformed quotes raise `ValueError`.
- Trailing newlines are ignored; a file ending with `\n` returns the same rows as without it.

Examples:
- `"a,b\nc"` → `[["a,b\nc"]]` (one quoted field spanning two lines)
- `"a""b",c` → `[["a\"b", "c"]]` (escaped quote in quoted field)
- `a,"b` → raises ValueError (unmatched quote)
- `a,b\nc,d` → `[["a", "b"], ["c", "d"]]`
- `` → `[]`
- `a` → `[["a"]]`

Write a few quick checks of your own and run them with `python`, then reply "done".
