Create `numlit.py` in the current directory. Standard library only, no filesystem or
network access. It scans numeric literals out of a string and formats numbers as
fixed-point decimals. It must define exactly this API:

- `NumError(ValueError)` — an exception class with two attributes: `.kind` (a `str`, one
  of the kinds listed below) and `.pos` (an `int` offset).
- `scan(text)` — returns a list of token records (see below).
- `format_number(value, spec)` — returns a `str`.

# scan(text)

`text` is a `str` holding zero or more numeric literals separated by exactly one ASCII
space (U+0020). `scan("")` returns `[]`.

**Separator check, done first, before any field is parsed.** If `text` starts with a
space (offset 0), ends with a space (offset `len(text)-1`), or contains two consecutive
spaces (offset = index of the *second* space), raise `NumError` of kind `"space"` at the
leftmost such offence. Only U+0020 separates fields; every other whitespace character
(tab, newline, ...) is not a separator and is caught later as kind `"char"`.

Then each **field** — a maximal run of non-space characters, starting at offset `p0` —
is parsed independently. Every `.pos` is an absolute offset into `text`.

**A. Charset.** Every character of the field must be one of `0-9 a-z A-Z _ . + -`.
Otherwise kind `"char"` at the first offending index.

**B. Sign.** An optional leading `+` or `-`; the rest is the *body*. If the body is empty,
kind `"sign"` at `p0`.

**C. Suffix.** If the body's last character is `u`, `l` or `s`, that character is the
suffix and is removed from the body. At most ONE character is ever removed. If the body
is then empty, kind `"suffix"` at that character's offset.

**D. Structural scan** of the body, left to right. The first offending character decides:

- If the body starts with `0` followed by an uppercase `X`, `O` or `B`: kind `"prefix"` at
  the offset of that uppercase letter.
- If the body starts with `0x`, `0o` or `0b` (lowercase) it is a RADIX literal of radix
  16, 8 or 2. If nothing follows the prefix, kind `"prefix"` at the offset just past the
  prefix (which may be the end of the field). Otherwise every remaining character must be
  a digit of that radix (hex digits may be upper or lower case: `0-9 a-f A-F`) or `_`;
  the first character that is neither gives kind `"digit"` at its offset.
- Otherwise it is a DECIMAL literal. Consume `intpart` = the maximal run of `[0-9_]`
  (possibly empty); then, if the next character is `.`, consume it and `fracpart` = the
  maximal run of `[0-9_]`; then, if the next character is `e` or `E`, consume it, then an
  optional `+`/`-`, then `expdigits` = the maximal run of `[0-9_]`. If any character of
  the body is left unconsumed, kind `"syntax"` at the offset of the first leftover
  character. (So `1-2`, `1u5` and `1.2.3` are all `"syntax"` — in `1u5` step C removes
  nothing, because the last character is `5`.)

**E. Semantic checks, in EXACTLY this order.** The first one that fires wins.

1. `"underscore"` — any `_` in `intpart`, `fracpart`, `expdigits` or the radix digits that
   is not strictly between two digits *of that same run*. `.pos` = the offset of the
   leftmost such `_`. (`_1`, `1_`, `1__2`, `0x_1`, `1_.5`, `1._5`, `1e_5`, `1e+_5` and
   `1_e5` are all bad.)
2. `"dangling_dot"` — a `.` is present and `fracpart` is empty (`5.`, `5.e3`, `.`).
   `.pos` = the offset of the `.`. Note that `.5` — empty `intpart`, non-empty
   `fracpart` — is VALID.
3. `"exponent"` — an `e`/`E` is present and `expdigits` is empty (`1e`, `1e+`).
   `.pos` = the offset of the `e`/`E`.
4. `"leading_zero"` — DECIMAL only: `intpart` with its underscores removed has length >= 2
   and starts with `0` (`007`, `00`, `01.5`, `0_1`). `.pos` = the offset of the first
   character of `intpart`. Fraction digits, exponent digits and radix digits may have any
   number of leading zeros.
5. `"suffix"` — `u` or `l` on a float literal, or `s` on an integer literal. `.pos` = the
   offset of the suffix character. A literal is a FLOAT if and only if it has a `.` or an
   exponent; otherwise it is an INT.

## The record

Each record is a `dict` whose `list(record.keys())` is EXACTLY
`["kind", "radix", "value", "text", "suffix", "start"]`, in that order:

- `"kind"`: `"int"` or `"float"` (a `str`).
- `"radix"`: the `int` 10, 16, 8 or 2. Floats are always 10.
- `"value"`: exactly of type `int` for ints and exactly of type `float` for floats
  (`type(v) is int` / `type(v) is float`).
- `"text"`: the canonical text (see below).
- `"suffix"`: the suffix character, or `""` if there was none.
- `"start"`: the `int` absolute offset of the field's first character, sign included.

**Integer value**: the digits read in the given radix, negated if the sign was `-`.

**Float value**, computed by exactly this procedure (it pins the result bit for bit): let
D be the `intpart` digits followed by the `fracpart` digits, underscores removed, where an
empty `intpart` counts as `0`; let M be D read as an integer; let E be (the explicit
exponent value, or 0 if there is no exponent) minus the number of `fracpart` digits after
underscores are removed. The magnitude is `M * (10.0 ** E)` if `E >= 0`, else
`M / (10.0 ** -E)`, computed exactly that way with Python floats. Negate it if the sign
was `-` — so `-0.0` is produced for a negative zero.

**Canonical `"text"`:**

- INT radix 10: a `-` only if the value is negative (never `+`; `-0` canonicalises to
  `"0"`), then the decimal digits with underscores removed.
- INT radix 16/8/2: the sign (`-` only, and never for zero), then `0x`/`0o`/`0b`, then the
  digits with underscores removed, LOWERCASED, with leading zeros stripped but keeping at
  least one digit. So `0x000` -> `"0x0"` and `-0x00Ff` -> `"-0xff"`.
- FLOAT: the sign — `-` if and only if the value is negative, INCLUDING negative zero, so
  `-0.0` -> `"-0.0"` while `+0.0` -> `"0.0"` — then the `intpart` digits (underscores
  removed, `0` if empty), then `.`, then the `fracpart` digits (underscores removed, or
  `0` if the literal had no `.` at all), then, only if the literal had an exponent, `e`,
  then `-` if the exponent value is negative (never `+`), then the exponent digits with
  leading zeros stripped, keeping at least one digit. Examples: `.5` -> `"0.5"`,
  `1e5` -> `"1.0e5"`, `1_0.2_5E+0_07` -> `"10.25e7"`, `1e000` -> `"1.0e0"`,
  `1e-0_3` -> `"1.0e-3"`.

# format_number(value, spec)

Renders `value` (an `int` or a `float`) as a fixed-point decimal string according to the
mini format spec `spec` (a `str`). Returns exactly a `str`.

The spec has these sections, in EXACTLY this order, all optional:

    [fill align][sign][,][width][.precision][mode]

- **fill/align**: if `spec[1]` is one of `< > ^`, then `spec[0]` is the fill character (any
  character at all) and `spec[1]` is the alignment; otherwise, if `spec[0]` is one of
  `< > ^`, it is the alignment and the fill is `" "`. Default: alignment `>`, fill `" "`.
- **sign**: one of `+`, `-`, `" "` (a space). `-` means a sign only when negative; `+`
  means always a sign; `" "` means a space for non-negative and `-` for negative.
  Default `-`.
- **`,`**: group the INTEGER digits in threes from the right with `,` (never the fraction
  digits).
- **width**: the maximal run of decimal digits at this point, value 0..200, and it must not
  start with `0` (a leading zero is a spec error, so a bare `0` width is an error too).
  Default 0.
- **.precision**: `.` followed by the maximal run of decimal digits, which must be
  non-empty and have value 0..20. Default 0.
- **mode**: one of `h` (half-even: ties go to the even last digit), `u` (half-up: ties go
  away from zero), `d` (toward zero, i.e. truncate), `f` (floor, i.e. toward negative
  infinity). Default `h`.

**Rendering.** The EXACT numeric value of `value` is rounded to `precision` decimal places
using the mode. For a float the exact value is its exact binary value
(`float.as_integer_ratio()` gives it exactly), so a tie happens only when that exact value
is exactly halfway — `0.5`, `2.5` and `0.125` at precision 2 are ties, `2.675` is not. Do
all of this with integer arithmetic. The digits are written as: the integer digits (at
least one, `0` when zero, grouped if `,` was given), then, if `precision > 0`, a `.` and
exactly `precision` fraction digits. The sign character required by the sign policy is
prefixed.

**Negative zero.** The result is negative if and only if `value` is negative — and for a
float that means `-0.0` counts as negative — or the rounded value is negative. When a
negative value rounds to zero magnitude the `-` is still emitted:
`format_number(-0.001, ".2") == "-0.00"`, `format_number(-0.0, ".2") == "-0.00"`,
`format_number(-0.6, "d") == "-0"`. Ints have no negative zero:
`format_number(0, "") == "0"` and `format_number(-0, "+") == "+0"`.

**Padding.** If the rendered string is shorter than `width`, pad it with the fill character
up to exactly `width` using the alignment: `<` left, `>` right, `^` centre with the extra
character on the RIGHT when the padding is odd. If it is already at least `width` long,
return it unchanged; never truncate.

**Errors** from `format_number` are `NumError` with `.pos == -1`, checked in EXACTLY this
order:

1. `"type"` — `value` is not an `int` or a `float`, or it is a `bool` (bools are rejected
   even though `bool` is a subclass of `int`), or `spec` is not a `str`.
2. `"nonfinite"` — `value` is a float nan or infinity.
3. `"spec"` — the spec does not match the grammar: unknown trailing characters, sections
   out of order, a `.` with no digits after it, precision > 20, a width with a leading
   zero, width > 200, an unknown mode letter, or a duplicated section.

# STRICTNESS REQUIREMENTS

1. Every rejection must raise `NumError` (never a bare `ValueError`, `TypeError` or
   `AssertionError`) with the exact `.kind` string and the exact `.pos` offset given
   above.
2. The separator check comes before any field parsing, and within a field the order is
   charset, sign, suffix-strip, structural scan, then the five semantic checks in the
   listed order. When several things are wrong the FIRST rule in that order wins.
3. `list(record.keys())` must be exactly `["kind", "radix", "value", "text", "suffix",
   "start"]`, in that order.
4. `type(record["value"])` must be exactly `int` for ints and exactly `float` for floats,
   and `record["radix"]`/`record["start"]` must be `int`s.
5. `"text"` must be exactly the canonical form: radix digits lowercased with leading zeros
   stripped, no `+` sign ever, `-0` canonicalised to `"0"` for ints but `-0.0` kept as
   `"-0.0"` for floats, floats always showing an `intpart`, a `.` and a `fracpart`.
6. Leading zeros are an error for decimal integer parts (`007`, `0_1`) but are fine in
   fraction digits, exponent digits and radix digits.
7. `.5` is valid, `5.` is `"dangling_dot"`; an underscore is only legal strictly between
   two digits of the same digit run.
8. `format_number` must round the EXACT value with the requested tie rule; `-0.0` and
   negative values that round to zero must still print a `-`.
9. The bans below are checked by reading your source.

# BANS

- Do not import `re`, `ast`, `decimal`, `fractions` or `json`.
- Do not CALL any of these names anywhere in the module: `int`, `float`, `complex`,
  `eval`, `exec`, `round`, `format`, `Decimal`, `literal_eval`. Using `int` or `float` as
  a bare name (`isinstance(x, float)`) is fine — only calls are banned.
- Do not use `%`-style string formatting or `str.format`/f-string format specifiers: no
  string literal in the module may contain a `{...:...}` placeholder, and no string
  literal may be the left operand of `%`.

# Examples

    scan("42 -7 3.5") == [
        {"kind": "int",   "radix": 10, "value": 42,   "text": "42",  "suffix": "", "start": 0},
        {"kind": "int",   "radix": 10, "value": -7,   "text": "-7",  "suffix": "", "start": 3},
        {"kind": "float", "radix": 10, "value": 3.5,  "text": "3.5", "suffix": "", "start": 6},
    ]
    scan("0x1F")[0]["value"] == 31 and scan("0x1F")[0]["text"] == "0x1f"
    scan("12u")[0]["suffix"] == "u"
    scan("1+2")  # raises NumError, .kind == "syntax", .pos == 1
    format_number(1234.5678, ",.2") == "1,234.57"
    format_number(-3.5, "8.1") == "    -3.5"

Write a few quick checks of your own and run them with `python`, then reply "done".
