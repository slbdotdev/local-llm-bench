Create `minire.py` in the current directory with a function `fullmatch(pattern: str, text: str) -> bool` implementing a small regular-expression engine from scratch (do NOT import `re` or any third-party library).

Supported syntax:
- Literal characters; `.` matches any single character.
- Escapes: a backslash followed by any character matches that character literally (`\.` matches `.`, `\\` matches `\`).
- Character classes `[abc]`, ranges `[a-z0-9]`, and negated classes `[^abc]`. Inside a class `]` as the first character is literal, and `-` at the start or end is literal.
- Quantifiers `*`, `+`, `?` applying to the preceding atom (a character, `.`, a class, or a parenthesised group).
- Grouping with `( ... )` and alternation `|` (lowest precedence, allowed at top level and inside groups).
- The whole text must match (anchored at both ends).
- Raise `ValueError` for malformed patterns: unbalanced parentheses, unterminated class, a quantifier with nothing before it, a trailing backslash.

Examples: `fullmatch("a*b", "aaab")` is True; `fullmatch("colou?r", "color")` is True; `fullmatch("(ab|cd)+", "abcdab")` is True; `fullmatch("[^0-9]+", "ab1")` is False; `fullmatch("", "")` is True.

Backtracking over nested quantified groups must be correct, e.g. `fullmatch("(a|ab)(c|bcd)(d*)", "abcd")` is True.

Write a few quick checks of your own and run them with `python`, then reply "done".
