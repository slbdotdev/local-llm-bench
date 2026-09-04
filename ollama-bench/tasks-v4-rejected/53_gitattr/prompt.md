Create `gitattr.py` in the current directory: a gitattributes-style resolver that maps a
path to a set of attributes. It is pure string processing (no filesystem access, standard
library only) and must define exactly this API:

```python
class AttrError(ValueError): ...           # must subclass ValueError; has a .kind str

def compile_attrs(lines)                   # -> an opaque compiled object of your choice
def check_attrs(path, compiled)            # -> dict: attribute name -> resolved value
```

`lines` is any iterable of strings (a list, a tuple, a generator …), each one line of an
attributes file with no trailing newline; iterate it once and do not modify it.
`compile_attrs` raises `AttrError` if any line is invalid (see section 8 for the complete
list). The value it returns is what gets passed back as `compiled`; it must stay usable
for any number of later `check_attrs` calls, which never modify it.

Every `AttrError` instance must carry an attribute `.kind` whose value is exactly one of
the ten lowercase strings listed in section 8, naming why the input was rejected.

Forbidden imports — write everything yourself: `re`, `fnmatch`, `glob`, `pathlib`, `os`
(including `os.path`) and `string`. Also forbidden are the character-classification string
methods `.isalpha()`, `.isdigit()`, `.isalnum()`, `.isupper()`, `.islower()`,
`.isspace()`, `.isascii()` and `.isprintable()`: the character classes of section 6 are
defined here in ASCII terms and you must implement those definitions literally.

A **path** is a non-empty string of one or more non-empty components joined by `/`, with
no leading and no trailing `/`. Components are raw text and are never escaped; a component
may contain any character except `/` (so `a b`, `#x`, `*`, `a\b` are all valid
components). Matching is case sensitive. Paths are always valid; you never validate them.

Throughout, a character of a line is **escaped** iff it is immediately preceded by an odd
number of backslashes. "Unescaped `X`" always means that.

## 1. Reading one line — exact order

1. Strip trailing whitespace: repeatedly, while the line ends with a space or a tab,
   remove that final character unless it is escaped. Leading whitespace is never stripped.
2. If the line is now empty, skip it (it contributes nothing).
3. If the line now begins with `#`, it is a comment: skip it. (This first `#` cannot be
   escaped, since nothing precedes it; a line beginning with `\#` is not a comment.)
4. If the line now begins with the six literal characters `[attr]`, it is a **macro
   definition** (section 5). Otherwise it is a **rule line**.
5. Split the line into fields. The first field runs from the start of the line up to (not
   including) the first unescaped space or tab, or to the end of the line; for a rule line
   that field is the **pattern**, for a macro definition line it is the six characters
   `[attr]` followed by the **macro name**. Everything after that first field is split on
   runs of spaces and tabs into zero or more **attribute fields**; backslashes in those
   fields are ordinary characters, so an attribute field can never contain whitespace.
   Only the pattern is allowed to contain escaped whitespace.

## 2. Attribute fields

An attribute field is one of these four forms; the resolved value is given on the right:

- `name`         -> `True`   (set)
- `-name`        -> `False`  (unset)
- `!name`        -> `None`   (unspecified)
- `name=value`   -> the string `value` (the text after the FIRST `=`, which may itself
  contain `=`, and which may be empty: `name=` resolves to `""`)

A **name** must be non-empty, its first character must be an ASCII letter or `_`, and
every later character must be an ASCII letter, digit, `-`, `_` or `.`. Anything else is
invalid. `-name=v` and `!name=v` are invalid (the `-`/`!` forms may not carry a value).

## 3. Rule lines and resolution

`check_attrs(path, compiled)` walks the rule lines in file order (macro definition lines
never match anything) and, for every rule whose pattern matches the path, applies that
rule's attribute fields **left to right** to an accumulating result dict, each field
storing `name -> value`, overwriting any value that name already had.

So overriding is **per attribute, not per line**: a later matching line only changes the
attributes it actually mentions; attributes set by an earlier matching line and not
mentioned again keep their earlier value.

The returned dict contains exactly the names that were stored at least once while
resolving this path — including names stored with the value `None` by a `!name` field,
which are present in the dict with value `None`. A name that no matching line ever
mentions is **absent** from the dict entirely. If no rule matches, the dict is empty.

The returned value's exact form is part of the specification:

- it is a plain `dict` (`type(result) is dict`), with `str` keys;
- a set attribute's value is the boolean `True` itself, so `result[name] is True` — not
  `1`, not `"true"`; an unset attribute's value is `False` itself, so
  `result[name] is False` — not `0`; an unspecified attribute's value is `None` itself,
  so `result[name] is None` — not the string `"None"`, and not omitted;
- a `name=value` attribute's value is a `str`, never converted to any other type: `k=1`
  resolves to the string `"1"`, and `k=` to `""`;
- no other keys ever appear;
- each call returns a fresh dict; mutating a returned dict must not affect the compiled
  object or any later call.

## 4. Patterns — exact order

Given the pattern field:

1. If the pattern is empty, the line is invalid.
2. If the pattern ends with an unescaped `/`, the line is invalid. (There is no
   directory-only form; paths never end in `/`.)
3. If the pattern begins with `/`, it is **anchored**; remove ALL of its leading `/`
   characters. If the pattern becomes empty, the line is invalid.
4. Otherwise the pattern is anchored iff it contains an unescaped `/` anywhere; if it does
   not, it is **unanchored**.
5. Split the pattern into **segments** on its unescaped `/` characters. An unanchored
   pattern therefore always has exactly one segment.
6. An **anchored** pattern matches iff its segments match the path's full component list,
   in order, with every component consumed.
7. An **unanchored** pattern matches iff its single segment matches the path's LAST
   component (its basename), and nothing else. It never matches an interior component:
   the pattern `b` does NOT match the path `b/c`.

An **empty segment** (from `a//b`) matches no component, so a pattern containing one
matches nothing — but it is still not an error, and the rest of the pattern is still
checked for the errors in section 8.

## 5. Segments

A segment consisting of exactly `**` matches zero or more consecutive components. So the
anchored pattern `a/**` matches `a`, `a/b` and `a/b/c`; `**/x` matches `x`, `a/x` and
`a/b/x`; `a/**/b` matches `a/b`, `a/x/b` and `a/x/y/b`. This special meaning only applies
inside an anchored pattern; the unanchored pattern `**` is a single segment matched
against the basename, in which `**` behaves like the `*` described below, so it matches
every path.

Any other segment matches exactly one whole component. Inside such a segment:

- A backslash escapes the next character: the pair becomes one ordinary literal character
  that has lost all special meaning (`\*`, `\?`, `\[`, `\\`, `\ `, `\#`, `\/` …). A
  backslash as the last character of a segment is invalid. Note that an escaped `/` is an
  ordinary literal character, which no component can contain, so a segment containing one
  matches nothing — and, per step 4, an escaped `/` does not make a pattern anchored.
- `?` matches exactly one character (which is never `/`, as components hold no `/`).
- `*` matches any run of zero or more characters. It never crosses a component boundary,
  since a segment is matched against one component. A run of two or more `*` inside a
  segment that is not the whole segment (as in `a**b` or `**x`) behaves exactly like a
  single `*`; only a segment that is exactly `**` has the special meaning above.
- `[...]` matches exactly one character, per section 6.
- Every other character, including `]`, `!`, `^`, `-` and `#`, is an ordinary literal.

## 6. Bracket classes

A class starts at an unescaped `[`. If the next character is `!` or `^` the class is
**negated** (both spellings mean the same thing) and that character is consumed. The class
then holds one or more members, and ends at the first `]` that is not the very first
character position of the member list. Scanning members, in this order:

- A `]` in the very first member position is an ordinary member (`[]abc]`, `[!]abc]`).
- `[:name:]` is a POSIX class member, where `name` is looked up after finding the first
  following `:]`. The eight legal names, in ASCII terms, are: `alpha` (`A`-`Z`, `a`-`z`),
  `digit` (`0`-`9`), `alnum` (alpha or digit), `space` (space, `\t`, `\n`, `\v`, `\f`,
  `\r`), `upper` (`A`-`Z`), `lower` (`a`-`z`), `punct` (the ASCII printable characters
  that are neither alphanumeric nor space: code points 33-47, 58-64, 91-96, 123-126) and
  `xdigit` (`0`-`9`, `a`-`f`, `A`-`F`). Any other name is invalid, as is a `[:` inside a
  class with no following `:]`. A POSIX class member can never be an endpoint of a range.
- Otherwise take one member character, honouring a backslash escape (`[\]]` holds `]`,
  `[\-]` holds `-`). Then, if the very next character is an unescaped `-` AND the
  character after that is neither `]` nor the end of the segment, this is a **range**: the
  `-` is consumed and one more character (again honouring a backslash escape) is taken as
  the range's upper endpoint. Otherwise the member stands alone. A `-` that is not
  consumed as a range separator — at the start of the member list, immediately before the
  closing `]`, or directly after a POSIX class member — is an ordinary member character.
- A range matches any character whose code point lies between the two endpoints
  inclusive. A **reversed** range such as `[z-a]` matches nothing, while the class's other
  members still apply normally.

The class matches its character iff that character is one of the members (or in one of the
ranges); if the class is negated, it matches iff the character is NOT.

## 7. Macros

A macro definition line is `[attr]NAME` followed by attribute fields, e.g.
`[attr]binary -diff -text merge=binary`. `NAME` must be a valid name (section 2) and must
follow `[attr]` immediately, with no space; there must be at least one attribute field.
Defining the same macro name twice is invalid. Macro definitions are collected before any
resolution, so a macro may be used on lines above its definition, and a macro body may
reference a macro defined later.

When applying attribute fields to the result (section 3), each field is handled like this:

1. Store `name -> value` in the result, as usual. The macro's own name is recorded too,
   exactly like any other attribute.
2. Then, and only if `name` is a defined macro AND the value just stored is `True` (i.e.
   the field had the plain `name` form), immediately apply that macro's own attribute
   fields, left to right, by this same two-step procedure — so macro expansion is
   recursive to any depth. The forms `-name`, `!name` and `name=value` never expand,
   even for a macro name.

Because expansion happens at the point of the field that triggered it, anything applied
afterwards wins: a later field on the same line, or any later matching line, overrides
what an expansion stored. Conversely an expansion overrides values stored before it.

For cycle detection, a macro body is said to **reference** every macro name it mentions in
any of the four field forms. If any macro references itself directly or indirectly,
`compile_attrs` raises `AttrError`.

## 8. Invalid lines, their `.kind`, and the order errors are reported

`compile_attrs` raises `AttrError` for exactly these ten cases, and the raised exception's
`.kind` must be exactly the string given:

| # | case | `.kind` |
|---|------|---------|
| 1 | A rule line whose pattern is empty — including a line beginning with an unescaped space or tab, and a pattern that is nothing but `/` characters. | `empty_pattern` |
| 2 | A pattern ending with an unescaped `/`. | `trailing_slash` |
| 3 | A backslash as the last character of a segment, including the last character of the pattern and a backslash at the end of an unfinished bracket class. | `trailing_backslash` |
| 4 | An unterminated bracket class: a `[` whose class never ends, once the "first `]` is a literal member" rule of section 6 has been applied (so `[`, `[]`, `[!]`, `[a-` are all invalid). | `unterminated_class` |
| 5 | A `[:` inside a bracket class with no following `:]`, or a POSIX class name that is not one of the eight listed. | `bad_posix_class` |
| 6 | A rule line or macro definition line with zero attribute fields. | `no_attrs` |
| 7 | An attribute field that is not one of the four forms of section 2, or whose name is not a valid name (`-`, `!`, `=v`, `9x`, `a b`, `a/b` …), or that carries a value on the `-`/`!` form. | `bad_attr_name` |
| 8 | A macro definition line whose macro name is invalid or missing. | `bad_macro_name` |
| 9 | Two macro definition lines defining the same name. | `duplicate_macro` |
| 10 | A macro reference cycle. | `macro_cycle` |

Nothing else raises. In particular a pattern that can never match is fine, `name=` with an
empty value is fine, a name that is not a defined macro is an ordinary attribute and is
fine, a macro body mentioning the same macro twice (`[attr]m1 m2 -m2`) is fine, and a rule
line's pattern is still fully validated even when the pattern can never match.

A single line can be wrong in several ways at once, so the order in which these are
checked is fixed. Lines are processed strictly in file order and the FIRST line that is
invalid decides which `AttrError` is raised; a later line's problems are then never
reported. Within one line the checks run in exactly this order:

For a **macro definition** line: (a) macro name — `bad_macro_name`; (b) zero attribute
fields — `no_attrs`; (c) name already defined — `duplicate_macro`; (d) its attribute
fields, left to right — `bad_attr_name`.

For a **rule** line: (a) empty pattern — `empty_pattern`; (b) pattern ends with an
unescaped `/` — `trailing_slash`; (c) the pattern is then scanned from left to right and
the FIRST fault met wins, whether it is `trailing_backslash`, `unterminated_class` or
`bad_posix_class`; (d) zero attribute fields — `no_attrs`; (e) finally its attribute
fields, left to right — `bad_attr_name`.

Note that the whole pattern is validated before the line's attribute fields are even
looked at. So `[` is `unterminated_class` and so is `[ -x`; `a\` is `trailing_backslash`;
`x/ -` is `trailing_slash`; `[[:zz:] t` is `bad_posix_class` (met before the class turns
out to be unterminated); `*.c` is `no_attrs`; `* -` is `bad_attr_name`; and `[attr]9m -`
is `bad_macro_name`.

`macro_cycle` is special: cycles are looked for only after every line of the file has been
read and parsed without any other error, so a file that both contains a cycle and has a
malformed line reports that malformed line instead.

## Examples

```python
c = compile_attrs(["*.txt text", "/doc/*.txt -text diff=plain"])
check_attrs("a/b.txt", c)          == {"text": True}
check_attrs("doc/b.txt", c)        == {"text": False, "diff": "plain"}

c2 = compile_attrs(["[attr]bin -diff -text", "*.png bin", "*.png diff=hex"])
check_attrs("x.png", c2)           == {"bin": True, "diff": "hex", "text": False}

c3 = compile_attrs(["a/**/z !k", "**/z k=1"])
check_attrs("a/q/z", c3)           == {"k": "1"}

try:
    compile_attrs(["[ x"])
except AttrError as e:
    e.kind                         == "unterminated_class"
```

Write a few quick checks of your own and run them with `python`, then reply "done".
