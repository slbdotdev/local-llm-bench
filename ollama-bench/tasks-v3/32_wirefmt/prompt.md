Create `wirefmt.py`: a text codec for nested string data. A *value* is either a `str` (an
**atom**) or a `list` of values (arbitrarily nested).

```python
encode(value) -> str
decode(text: str) -> value          # str or list
canon(text: str) -> str             # == encode(decode(text))

class WireError(ValueError):        # .kind: str   .pos: int
    ...
```

`WireError` must subclass `ValueError`, and every raised instance must have a `.kind`
attribute (one of the exact strings listed below) and a `.pos` attribute (an `int`, a 0-based
index into the input text). In this prompt `r"..."` means a Python raw string, so `r"\~"` is
the two characters backslash and tilde.

## 1. `encode` — the canonical form

1. A list encodes as `"("` + `","`.join(encoded items) + `")"`. The empty list encodes as `"()"`.
2. A non-empty atom encodes as its characters, each rewritten by the first rule that applies:
   * a backslash becomes two backslashes;
   * `(` becomes `r"\("`, `)` becomes `r"\)"`, `,` becomes `r"\,"`, `~` becomes `r"\~"`;
   * any character with codepoint `< 0x20`, or `== 0x7f`, becomes `\x` followed by exactly two
     **lowercase** hex digits: newline becomes `r"\x0a"`, `chr(0x7f)` becomes `r"\x7f"`,
     `chr(0)` becomes `r"\x00"`;
   * every other character, including space, `x`, `[`, `"` and non-ASCII characters such as
     `é`, is emitted literally.
3. The empty atom `""` encodes as `"~"` (a lone tilde). Note `encode("~") == r"\~"`.
4. Lists may nest at most 200 deep (a list whose items are all atoms has depth 1). Encoding a
   value nested 201 or more deep raises `WireError` with kind `"depth"` and `pos` 0.
5. Encoding anything that is not a `str` and not a `list`, at any nesting level, raises
   `WireError` with kind `"type"` and `pos` 0.

## 2. `decode` — accepts a larger language

`decode` accepts every string `encode` can produce, plus the extra forms in rules 8 and 9.
It parses exactly one value spanning the whole input.

6. A `(` at the start of a value opens a list. Its items are values separated by `,`, and the
   list is ended by `)`. `()` is the empty list.
7. Otherwise the value is an atom: its characters run up to the next unescaped `,` or `)`, or
   to the end of the input. An unescaped `(` **inside** an atom (that is, not at the atom's
   first position) is an ordinary literal character, so `decode("(a(b)") == ["a(b"]`. `,` and
   `)` always end an atom, so they must be escaped to appear inside one.
8. `\x` followed by exactly two hex digits of **either** case decodes to that codepoint, so
   `r"\x0A"` and `r"\x0a"` both decode to a newline and `r"\x41"` decodes to `"A"`. The `x`
   itself must be lowercase: `r"\X41"` is rule 9 applied to `X` and decodes to the three
   characters `"X41"`.
9. A backslash followed by any printable ASCII character (codepoints `0x20`..`0x7e`) **other
   than** `x` decodes to just that character. This makes `r"\\"`, `r"\("`, `r"\)"`, `r"\,"` and
   `r"\~"` work, and it also allows redundant escapes: `r"\a"` decodes to `"a"`, `r"\ "` to a
   space, `r"\7"` to `"7"`.
10. Any other backslash is an error of kind `"escape"`: a backslash at the very end of the
    input, a backslash followed by a control character or by a non-ASCII character, or `\x` not
    followed by two hex digits.
11. An unescaped `~` is legal only when it is the atom's **entire** text; that atom is then
    `""`. A `~` anywhere else in an atom is an error of kind `"tilde"`. Inside a longer atom a
    literal tilde must be written `r"\~"` or `r"\x7e"`.
12. Nesting more than 200 lists deep is an error of kind `"depth"`.

## 3. `canon`

13. `canon(text)` returns `encode(decode(text))`; errors propagate unchanged. Therefore
    `canon(canon(t)) == canon(t)` for every `t` that decodes.

## 4. Errors

14. `"escape"` — a malformed backslash escape (rule 10). `pos` = index of the backslash.
15. `"tilde"` — an unescaped `~` that is not a whole atom (rule 11). `pos` = index of the `~`.
16. `"empty"` — an atom with zero characters where a value is required: at the very start of
    the input, directly after a `(` (except in `()`, which is the empty list), or directly
    after a `,`. Write `~` for an empty atom. `pos` = the index at which that empty atom
    starts, which may equal `len(text)`.
17. `"delim"` — a `,` or `)` reached at top level, with no list open.
    `pos` = index of that character.
18. `"unterminated"` — the input ends while at least one list is still open. `pos` = `len(text)`.
19. `"trailing"` — a character other than `,` or `)` in a position where a delimiter or the end
    of the input was required: directly after a `)` that closed a nested list, or directly
    after the `)` that closed the top-level value. (A `,` or `)` in those positions is either a
    normal delimiter or, at top level, a `"delim"` error.) `pos` = index of that character.
20. `"depth"` — a `(` that would open list number 201. `pos` = index of that `(`. `"depth"` is
    also raised by `encode` (rule 4); `"type"` is raised only by `encode` (rule 5).

**Precedence.** If the input has more than one problem, report the one whose `pos` is
**smallest**. If two problems are detected at the same `pos`, report the one that comes first
in this list:

```
"escape" > "depth" > "tilde" > "empty" > "delim" > "unterminated" > "trailing" > "type"
```

So `decode(",")` raises `"empty"` at 0, not `"delim"`; `decode("(a,")` raises `"empty"` at 3,
not `"unterminated"`; and `decode("(")` raises `"empty"` at 1. Smallest `pos` wins over that
list: `decode(r"(~a,\xzz)")` raises `"tilde"` at 1, while `decode(r"(\xzz,~a)")` raises
`"escape"` at 1.

## 5. Performance

21. `decode` followed by `encode` of a flat list of 200,000 short atoms (a string of about
    1.4 MB) must finish in well under 5 seconds. A parser that repeatedly slices off the front
    of the remaining input (`text = text[1:]`) is quadratic and will not make it.
22. Input nested exactly 200 lists deep must decode and re-encode correctly without tripping
    over Python's recursion limit. Prefer an iterative parser.

## Worked examples (Python literals)

```python
encode(["a b", "", "~", "x,y"])   == r"(a b,~,\~,x\,y)"
encode([[], ["\n"], "é"])         == r"((),(\x0a),é)"
encode([])                        == "()"
decode(r"((),(\x0A),\X41,\a)")    == [[], ["\n"], "X41", "a"]
decode(r"(a\)b)")                 == ["a)b"]
canon(r"(\x41,\a,a(b,~)")         == r"(A,a,a\(b,~)"
```

Write a few quick checks of your own and run them with `python`, then reply "done".
