Create `jsonesc.py` in the current directory: a self-contained JSON serializer and
parser. Do NOT import `json`, `simplejson` or any third-party library (writing the
escaping and the scanner yourself is the whole point). `math`, `re` and the rest of
the standard library are fine.

The module must export `dumps`, `loads` and `JsonError`.

## `JsonError`

```python
class JsonError(ValueError): ...
```

Raised by `loads` only. Every instance must carry:

* `.kind`  - one of the strings `"eof"`, `"value"`, `"key"`, `"delimiter"`,
  `"escape"`, `"control"`, `"extra"` (defined below),
* `.pos`   - 0-based index into the document of the offending character,
* `.lineno` - `document.count("\n", 0, pos) + 1`,
* `.colno`  - `pos - document.rfind("\n", 0, pos)` (so 1-based within the line).

## `dumps`

```python
def dumps(obj, *, ensure_ascii=True, sort_keys=False, indent=None,
          separators=None, allow_nan=True) -> str
```

Supported values are exactly `dict`, `list`, `str`, `int`, `float`, `bool` and
`None`. Any other value anywhere in the structure (including a `tuple`, a `set` or
`bytes`) raises `TypeError`. Input never contains reference cycles.

**Scalars.**

* `None` -> `null`; `True` -> `true`; `False` -> `false`. `bool` is checked before
  `int`, so `True` is never written as `1`.
* `int` -> `repr(x)` (arbitrary precision; no size limit).
* `float`: if `x != x` -> `NaN`; if `x == float("inf")` -> `Infinity`; if
  `x == float("-inf")` -> `-Infinity`. If `allow_nan` is false those three cases
  raise `ValueError` instead. Every other float is written as `repr(x)` exactly -
  so `1.0` -> `1.0`, `-0.0` -> `-0.0`, `1e16` -> `1e+16`, `0.1` -> `0.1`,
  `1/3` -> `0.3333333333333333`. Never `str()`-with-your-own-formatting, never
  `%g`, never strip a trailing `.0`.

**Strings.** A string is written between double quotes with these replacements,
applied per character:

* `"` -> `\"` and `\` -> `\\`.
* U+0008 -> `\b`, U+000C -> `\f`, U+000A -> `\n`, U+000D -> `\r`, U+0009 -> `\t`.
* Any other character with a code point below U+0020 -> `\u` followed by exactly
  four **lowercase** hex digits, e.g. U+001F -> `\u001f`.
* `/` (U+002F) is **never** escaped.
* If `ensure_ascii` is true, every remaining character outside the range
  U+0020..U+007E is escaped as `\uXXXX` with four lowercase hex digits - note that
  this includes U+007F (DEL) -> `\u007f`. A character above U+FFFF is written as
  the two `\uXXXX` escapes of its UTF-16 surrogate pair, e.g. U+1F600 ->
  `\ud83d\ude00`. A lone surrogate character (U+D800..U+DFFF) present in the Python
  string is written as its own single `\uXXXX` escape.
* If `ensure_ascii` is false, every remaining character (including U+007F, non-ASCII
  characters, astral characters and lone surrogates) is emitted literally.

**Object keys.** A key that is a `str` is used as is. Otherwise it is coerced to a
string first, checking `bool` before `int`: `True` -> `true`, `False` -> `false`,
an `int` -> `repr(k)`, `None` -> `null`. Any other key type raises `TypeError`.
The coerced key is then written as a JSON string with the rules above (so a key
`"a\"b"` is escaped normally). Coercion may produce two identical keys; both are
emitted, in the dict's iteration order.

**Ordering.** Members are emitted in the dict's iteration order. If `sort_keys` is
true they are sorted by their *coerced* key string with a stable ascending sort
(plain Python string comparison), so `{1: 0, "!": 0}` sorted gives `"!"` then `"1"`.

**Separators.** `separators`, when given, is a `(item_separator, key_separator)`
pair used verbatim. When it is `None` the default is `(", ", ": ")` if `indent` is
`None`, and `(",", ": ")` otherwise.

**Indentation.** `indent` may be `None`, a non-negative `int` (meaning that many
spaces) or a `str` used as the indent unit. With `indent=None` no newlines are
produced at all. Otherwise, writing a non-empty container at nesting level `L`
(the top-level value is at level 0) produces:

```
{ + NL(L+1) + member + ITEM + NL(L+1) + member ... + "\n" + UNIT*L + }
```

where `NL(k)` is `"\n"` followed by `UNIT` repeated `k` times, `UNIT` is the indent
unit and `ITEM` is the item separator, written verbatim (if you pass
`separators=(", ", ": ")` together with an indent you therefore get a trailing space
before each newline). Arrays behave identically with `[`/`]`. An **empty** dict or
list is always written as `{}` / `[]` with no newline inside, at any indent.

## `loads`

```python
def loads(s: str) -> object
```

Parses one JSON document and returns Python data, or raises `JsonError`. Whitespace
is exactly the four characters space, `\t`, `\n`, `\r`. The algorithm is a plain
recursive descent scan; every error position below is fully determined by it.

Wherever the scanner needs a character but the document is exhausted, it raises
`kind="eof"` with `pos = len(s)`. That covers a missing value, a missing delimiter,
a string with no closing quote, an escape cut off by the end of the document, and a
number cut short (`-`, `1.`, `1e`, `1e+` at the end of input).

**Top level.** Skip whitespace, scan one value, skip whitespace; if the position is
not `len(s)`, raise `kind="extra"` at that position.

**Value** at position `p` (after whitespace):

* If the document starts at `p` with one of the six literals `true`, `false`,
  `null`, `NaN`, `Infinity`, `-Infinity` (tried in that order), consume it and
  produce `True` / `False` / `None` / a NaN float / `inf` / `-inf`. Note this is a
  pure prefix test: `"nullx"` parses `null` and then fails with `kind="extra"` at 4,
  while `"nul"` never matches and fails as below.
* Otherwise `"` starts a string, `{` an object, `[` an array, and `-` or an ASCII
  digit a number.
* Otherwise raise `kind="value"` at `p`.

**Number.** Scan, starting at `p`: an optional `-`; then, if the next character is
`0`, exactly that one digit, else the run of ASCII digits; then optionally `.`
followed by one or more digits; then optionally `e`/`E`, an optional `+`/`-` and one
or more digits. If a digit is required at some index `i` and the character actually
there is not one, raise `kind="value"` at `i` (so `"-x"` fails at 1, `"[1.]"` at 3,
`"1e+x"` at 3). The scan simply stops at the first character that cannot continue -
it never complains about what follows, so `"01"` scans the number `0` and then the
caller reports `kind="extra"` at 1, and `"[01]"` reports `kind="delimiter"` at 2.
The scanned token becomes a Python `float` if it contained a `.` or an exponent and
an `int` otherwise (so `"1e2"` is `100.0`, `"-0"` is `0`, `"-0.0"` is `-0.0`, and
`"1e400"` is `inf`).

**String.** After the opening quote, characters are copied until the closing quote.

* A character with code point below U+0020 is not allowed unescaped:
  `kind="control"` at its index.
* After a backslash: `"`, `\`, `/`, `b`, `f`, `n`, `r`, `t` produce the obvious
  character. `u` must be followed by four hex digits (either case). Any other
  character after the backslash, or a non-hex-digit among those four characters,
  raises `kind="escape"` at the index of the **backslash**.
* A `\uXXXX` in the range D800..DBFF is combined with an immediately following
  `\uXXXX` in the range DC00..DFFF into the single astral character, consuming all
  12 characters. If the following text is not such a low-surrogate escape, the high
  surrogate is kept as the lone surrogate character `chr(cp)` (and likewise a lone
  low surrogate is kept as is). No error is ever raised for a lone surrogate.

**Array.** After `[`, skip whitespace; `]` closes an empty array. Otherwise scan a
value, skip whitespace, and require `,` (then skip whitespace and scan the next
value) or `]`; any other character raises `kind="delimiter"` at its index. There is
no trailing-comma allowance: `"[1,]"` scans a value at index 3 and so fails with
`kind="value"` at 3.

**Object.** After `{`, skip whitespace; `}` closes an empty object. Otherwise a
member is: a string key - any other character raises `kind="key"` at its index -
then whitespace, then `:` (else `kind="delimiter"` at that index), then whitespace,
then a value. After a member, whitespace, then `,` (skip whitespace and read the
next member) or `}`, else `kind="delimiter"` at that index. So the document
`{"a":1,}` fails with `kind="key"` at 7. Duplicate keys are allowed: the last one wins.

## Examples

```python
dumps({"b": 1, "a": [1, 2]})                 == '{"b": 1, "a": [1, 2]}'
dumps([1, {"x": None}], separators=(",", ":")) == '[1,{"x":null}]'
dumps({"a": [1]}, indent=2)                  == '{\n  "a": [\n    1\n  ]\n}'
dumps({"k": "héllo"})                   == '{"k": "h\\u00e9llo"}'
loads('{"a": [1, 2.5, true, null], "b": {}}') == {"a": [1, 2.5, True, None], "b": {}}
# loads('[1, 2') raises JsonError with kind "eof", pos 5, lineno 1, colno 6
```

Write a few quick checks of your own and run them with `python`, then reply "done".
