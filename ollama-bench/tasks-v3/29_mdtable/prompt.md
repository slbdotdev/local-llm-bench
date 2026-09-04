Create `mdtable.py` with three functions that parse and canonically re-format pipe tables.

```python
parse_table(text: str) -> tuple[list[list[str]], list[str] | None]
format_table(rows: list[list[str]], aligns: list[str] | None = None) -> str
normalize(text: str) -> str
```

`parse_table` rules:
1. Split `text` on `\n`. Ignore lines that are empty or whitespace-only. If no lines remain, return `([], None)`.
2. Leading and trailing whitespace is removed from each remaining line. The line must then start with `|` and end with `|` (a line that is just `|` qualifies). Otherwise raise `ValueError`.
3. The cells of a line are obtained by taking `line[1:-1]` and splitting it on `|` characters that are not escaped (see rule 5). Note the first and last character are removed even when they are the same character, so the line `||` has one cell, the empty string, and a line that is just `|` also has one empty cell.
4. Each raw cell segment is first stripped of leading/trailing whitespace, then unescaped: the two-character sequence `\|` becomes `|`, `\\` becomes `\`; any other backslash is kept literally together with the character after it (so `\n` stays the two characters backslash + `n`); a trailing lone backslash is kept as a literal backslash.
5. Escaping for splitting: a backslash escapes the character that follows it. So `\|` does not start a new cell, while `\\` is an escaped backslash and a `|` after it DOES split cells.
6. The second non-blank line, if every one of its unescaped cells matches the alignment pattern `:?-+:?` (at least one dash, at most one colon at each end, nothing else), is an alignment row: it is not returned as data. Each column's alignment is `"center"` if the cell has both colons, `"right"` if only a trailing colon, `"left"` otherwise (leading colon or no colon). The alignment row must have the same number of cells as the other rows, otherwise `ValueError`. `parse_table` returns `(rows, aligns)` where `aligns` is the list of alignment strings, or `None` if there was no alignment row.
7. All rows other than the alignment row must have the same number of cells as the first row; otherwise `ValueError`.

`format_table` rules:
1. If `rows` is empty, return `""`.
2. All rows must have the same length `ncols >= 1` (else `ValueError`). If `aligns` is given it must be a list of exactly `ncols` strings from `"left"`, `"right"`, `"center"` (else `ValueError`); if `aligns` is None, every column is `"left"`.
3. Column width `w_j = max(3, longest cell in column j)`, where lengths are measured on the *escaped* cell text (rule 4 below).
4. The output is: the first row of `rows`, then a separator row, then the remaining rows, each rendered as `"| "` + `" | ".join(cells)` + `" |"` and joined with `\n` (no trailing newline). A cell of column j is first escaped (each `\` becomes `\\`, then each `|` becomes `\|`), then padded with spaces to width w_j: `left` appends the spaces, `right` prepends them, `center` splits the padding in half with the extra space going to the right.
5. The separator row is rendered the same way except its cell for column j is built from w_j and the alignment: `left` -> `":" + "-"*(w_j-1)`, `right` -> `"-"*(w_j-1) + ":"`, `center` -> `":" + "-"*(w_j-2) + ":"`. It is not escaped and needs no extra padding (its length is exactly w_j).

`normalize(text)` returns `format_table(*parse_table(text))`, i.e. parse then format. `normalize` applied twice gives the same string as applied once.

Worked examples (shown as Python literals):
```python
parse_table("| a | b |\n| c | d |") == ([["a", "b"], ["c", "d"]], None)
parse_table("|") == ([[""]], None)
parse_table("| x | y |\n| :- | --: |\n| 1 | 22 |") == ([["x", "y"], ["1", "22"]], ["left", "right"])
parse_table("| a\\|b | c\\\\ |") == ([["a|b", "c\\"]], None)
normalize("| b | aa |\n| 1 | 2 |") == "| b   | aa  |\n| :-- | :-- |\n| 1   | 2   |"
normalize("| a\\|b |") == "| a\\|b |\n| :--- |"
```

Write a few quick checks of your own and run them with `python`, then reply "done".
