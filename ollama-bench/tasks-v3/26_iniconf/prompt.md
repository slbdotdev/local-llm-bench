Create `iniconf.py` in the current directory: a strict INI-style configuration parser and serializer. Standard library only.

Define an exception `ConfigError(ValueError)` and two functions.

## `parse(text: str) -> dict`
Returns a `dict` mapping section name -> `dict` of key -> value (all `str`). Insertion order must follow first appearance in the text.

Line handling:
- Line endings `\r\n` and `\r` are treated exactly like `\n`.
- Every line is stripped of leading/trailing whitespace before being classified.
- A blank line, or a line whose first character (after stripping) is `#` or `;`, is ignored. There are NO inline comments: `k = a # b` gives the value `a # b`.

A stripped line starting with `[` is a section header:
- It must end with `]`, otherwise `ConfigError`.
- The name is the text between the brackets, stripped. It must be non-empty and must not contain `[` or `]`, otherwise `ConfigError`.
- A repeated section header re-opens the existing section (its keys are added to the section already recorded; the section keeps its original position).

Any other line is a key/value line:
- It must contain `=`; split on the FIRST `=`. The key is the left part stripped and must be non-empty, otherwise `ConfigError`.
- A key/value line before any section header is a `ConfigError`.
- A key that already exists in the section being filled is a `ConfigError` (even if the section was re-opened later).
- The value is the right part stripped, then unquoted (below).

Unquoting: if the stripped value has length >= 2 and both starts and ends with `"`, it is a quoted value: the outer quotes are removed and the body is unescaped, where `\\` -> `\`, `\"` -> `"`, `\n` -> newline, `\t` -> tab. Any other backslash escape, a backslash at the end of the body, or an unescaped `"` inside the body is a `ConfigError`. Otherwise the value is taken literally with no escape processing at all (so `k = a\nb` is the four characters `a`, `\`, `n`, `b`, and `k = "abc` is the literal `"abc`).

## `dumps(cfg: dict) -> str`
The inverse. Sections in `cfg` order, keys in each section's order. Each section is `[name]` on its own line followed by one `key = value` line per key (exactly one space either side of `=`). Sections are separated by exactly one blank line, and the whole result ends with a single `\n`. `dumps({})` returns `""`.

A value is written quoted (outer `"` plus the four escapes above applied to `\`, `"`, newline and tab) if and only if it is empty, or differs from its own `.strip()`, or contains any of `"`, `\`, newline, tab. Otherwise it is written literally.

`parse(dumps(cfg)) == cfg` must hold for any cfg whose section names and keys are non-empty and free of `=`, `[`, `]`, `#`, `;` and whitespace, whatever the values contain.

## Examples
- `parse("[a]\nx = 1\n; note\n[b]\ny = hello world\n")` -> `{"a": {"x": "1"}, "b": {"y": "hello world"}}`
- `parse('[a]\np = "  padded\\t "\nq = "" \n')` -> `{"a": {"p": "  padded\t ", "q": ""}}`
- `parse("[a]\nk = v = w\n")` -> `{"a": {"k": "v = w"}}`
- `dumps({"s": {"a": "x", "b": " y", "c": ""}})` -> `'[s]\na = x\nb = " y"\nc = ""\n'`
- `parse("x = 1\n")`, `parse('[a]\nk = "\\q"\n')` and `parse("[a]\nk=1\nk=2\n")` all raise `ConfigError`.

Write a few quick checks of your own and run them with `python`, then reply "done".
