Create `wildmatch.py` in the current directory: a brace-expanding wildcard matcher over
FLAT strings. It is pure string processing (no filesystem access) and must define exactly
this API:

```python
class PatternError(ValueError): ...        # has an attribute .kind (a str)

def expand(pattern: str) -> list[str]      # brace expansion only
def match(pattern: str, text: str, casefold: bool = False) -> bool
def filter(patterns, texts, casefold: bool = False) -> list[str]
```

Do not import `fnmatch`, `re`, `glob` or `pathlib`; write the matcher yourself.

A text is an arbitrary string. There are NO path components: `/` is an ordinary character
with no special meaning, nothing is "anchored", and a leading `.` in the text is ordinary
too. A pattern matches only if it matches the WHOLE text.

Throughout, a character of the pattern is **escaped** iff it is immediately preceded by a
backslash that is itself not escaped (i.e. by an odd run of backslashes). "Unescaped `X`"
below always means that.

## 1. `expand(pattern)` -- brace expansion

`expand` only deals with braces. It never looks at `*`, `?` or `[...]`, never validates
anything, and never removes backslashes: the strings it returns still contain every
backslash of the input, for the matcher to interpret later.

Scan the pattern from left to right with a resume position, initially 0, and find the
first **expandable group**:

1. Find the next unescaped `{` at or after the resume position. If there is none, there is
   no expandable group.
2. Find its matching `}`: walk forward counting unescaped `{` (+1) and unescaped `}` (-1);
   the matching `}` is the one that brings the count back to 0. If the count never returns
   to 0 the `{` is unmatched: it is an ordinary literal character; set the resume position
   to just after that `{` and go back to step 1.
3. Split the body (the text strictly between the two braces) on its unescaped commas that
   are at depth 0 of the body (commas inside nested unescaped `{...}` do not count). If
   there is no such comma, the group is NOT expandable: the whole group, INCLUDING any
   nested braces inside it, is literal text and is never expanded; set the resume position
   to just after its matching `}` and go back to step 1.
4. Otherwise this is the expandable group, splitting into the parts found (in order).

If there is no expandable group, `expand(pattern)` returns `[pattern]` (a one-element
list). Otherwise, with `prefix` the text before the `{`, `suffix` the text after the `}`,
and `parts` the alternatives in order, the result is the concatenation, in order, of
`expand(prefix + part + suffix)` for each `part`. So the leftmost group varies SLOWEST:
`expand("{a,b}{c,d}") == ["ac", "ad", "bc", "bd"]`.

Consequences, all of which you must reproduce:

- An unmatched `}` is an ordinary literal character, as is an unmatched `{`.
- `{}`, `{a}` and `{1..3}` have no depth-0 comma, so they stay literal exactly as written;
  there are no numeric ranges -- `{1..3}` is NOT expanded to `1`, `2`, `3`.
- `{a{b,c}}` has no depth-0 comma in its body (the comma is nested), so the whole thing is
  literal: `expand("{a{b,c}}") == ["{a{b,c}}"]`. But `{x{a,b},c}` does have one, giving
  `["xa", "xb", "c"]`.
- Empty alternatives are allowed and produce empty strings: `expand("a{,b}") ==
  ["a", "ab"]`, `expand("{,}") == ["", ""]`. Duplicates are kept, never de-duplicated,
  and the order above is never changed or sorted.
- `\{`, `\}` and `\,` are escaped, so they neither open, close nor split a group; the
  backslashes stay in the output: `expand("{a\\,b,c}") == ["a\\,b", "c"]` (written with
  Python escaping; the pattern is `{a\,b,c}` and the first alternative is `a\,b`).

## 2. `match(pattern, text, casefold=False)`

`match` first calls `expand(pattern)`, then PARSES every alternative, in order, before
matching anything: if any alternative is malformed, `match` raises `PatternError` (see
section 6) even when an earlier alternative would have matched. If all alternatives parse,
`match` returns `True` iff at least one of them matches the whole text.

A parsed alternative is a sequence of items, each of which is one of:

- `*` -- matches zero or more characters, ANY characters, including `/`, `.` and spaces.
- `?` -- matches exactly one character, any character.
- `[...]` -- a bracket expression, matching exactly one character (section 3).
- `\c` -- for any character `c`: one literal `c`, stripped of all special meaning.
- any other character -- itself, literally (this includes `{`, `}`, `,`, `]`, `!`, `^`,
  `-` and `/` when they are left over outside a group or class).

The empty pattern matches only the empty text. Patterns may contain several `*`; your
matcher must not take exponential time on them.

## 3. Bracket expressions `[...]`

A bracket expression starts at an unescaped `[` and matches exactly one character. Reading
its contents, in this order:

1. If the first character after `[` is `!` or `^`, the expression is NEGATED and that
   character is consumed. BOTH spellings are accepted and mean the same thing.
2. A `]` in the very first content position (i.e. immediately after `[`, `[!` or `[^`) is
   an ordinary member, not the terminator. So `[]]` is the class containing `]`, and `[]`
   and `[!]` are unterminated.
3. Otherwise the first unescaped `]` ends the expression.

Members inside, left to right:

- `\c` -- a literal `c` member (`[\]]` is the class containing `]`, `[\-z]` is the class
  containing `-` and `z`).
- `[[:name:]]` -- a POSIX class element (section 4).
- `a-b` -- a range: an unescaped `-` forms a range when it is preceded by an ordinary
  member character (a plain one or an escaped one -- NOT a POSIX class element and not the
  start of the contents) and followed by a character that is neither the closing `]` nor
  the end of the pattern. The range covers every character `c` with
  `ord(a) <= ord(c) <= ord(b)`, comparing code points. A REVERSED range such as `[z-a]`
  is not an error: it simply contains no character, while the other members of the class
  still apply, so `[z-a5]` matches only `5`.
- any other character -- itself, a literal member. In particular a `-` that is the first
  content character, or that comes immediately before the closing `]`, or that follows a
  POSIX class element, is a literal `-` member.

A character matches the expression iff it is a member of at least one item (with
`casefold` applied as in section 5); if the expression is negated, the result is inverted
AFTER that test. A negated expression matches any single character that is not a member.

## 4. POSIX class elements

Inside a bracket expression, a `[` immediately followed by `:` starts a POSIX class
element, which ends at the next `:]`. (A `[` inside a bracket expression that is not
followed by `:` is just a literal `[` member.) POSIX class elements may be mixed freely
with other members (`[[:digit:]x-z]`) and may appear in a negated expression
(`[![:space:]]`). The member sets are defined over ASCII ONLY -- no character with a code
point above 127 is ever a member of any of them:

- `[:digit:]` -- `0123456789`
- `[:upper:]` -- `A`-`Z`
- `[:lower:]` -- `a`-`z`
- `[:alpha:]` -- `A`-`Z` and `a`-`z`
- `[:alnum:]` -- `A`-`Z`, `a`-`z` and `0`-`9`
- `[:xdigit:]` -- `0`-`9`, `A`-`F` and `a`-`f`
- `[:space:]` -- space, `\t`, `\n`, `\v`, `\f`, `\r`
- `[:punct:]` -- the 32 ASCII punctuation characters
  `` !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ ``

Any other name is an error. Nothing is special inside a POSIX class element: the name runs
to the next `:]` exactly as written.

## 5. `casefold`

With `casefold=True`, define `swap(c)` as: an ASCII letter `A`-`Z` becomes its lowercase
counterpart, an ASCII letter `a`-`z` becomes its uppercase counterpart, and every other
character (including every non-ASCII one) stays as it is. Then a text character `c`
matches a literal, a bracket member, a range or a POSIX class element iff `c` matches it
OR `swap(c)` matches it. Nothing else changes:

- it applies to literals as well as to everything inside brackets, so `match("A", "a",
  casefold=True)` and `match("[A]", "a", casefold=True)` are both `True`;
- it applies to ranges by code point, so `[a-c]` also matches `A`, `B`, `C`, and `[X-Z]`
  also matches `x`, `y`, `z`, while `[0-9]` is unaffected;
- `[:upper:]` and `[:lower:]` then both match letters of either case, and so does
  `[:xdigit:]` for `A`-`F`/`a`-`f`; `[:digit:]`, `[:space:]` and `[:punct:]` are
  unaffected;
- negation is applied AFTER the case-swapped test, so `match("[!a]", "A", casefold=True)`
  is `False`;
- with `casefold=False` nothing above happens at all.

## 6. Errors

Every malformed alternative raises `PatternError` with `.kind` set to one of these strings:

- `"trailing_backslash"` -- a backslash is the last character of the alternative (whether
  it is inside a bracket expression or not).
- `"unterminated_class"` -- a bracket expression that reaches the end of the alternative
  without its closing `]`.
- `"unterminated_posix"` -- a POSIX class element `[:` that reaches the end of the
  alternative without its closing `:]`.
- `"unknown_class"` -- a POSIX class element whose name is not one of the eight above.

Which one is raised is decided by scanning the alternative left to right and reporting the
FIRST position at which the scan fails. So (patterns written as Python literals):

- `"a\\"` (the pattern `a\`) -> `trailing_backslash`; `"[a\\"` (the pattern `[a\`) ->
  `trailing_backslash`, because the scan reaches the backslash before it runs off the end.
- `"[abc"` -> `unterminated_class`; `"[]"` and `"[!]"` -> `unterminated_class`.
- `"[[:dig"` -> `unterminated_posix`; `"[[:alpha:]"` -> `unterminated_class` (the POSIX
  element is fine, the bracket expression is not).
- `"[[:foo:]]"` -> `unknown_class`, and so does `"[[:foo:]"`, because the unknown name is
  found before the class turns out to be unterminated.

`expand` itself never raises: `expand("[a")` is `["[a"]`.

## 7. `filter(patterns, texts, casefold=False)`

`patterns` and `texts` are iterables of strings. Returns a list of those `texts` that
match at least one of the `patterns`, keeping the original order of `texts` and keeping
duplicates. An empty `patterns` gives `[]`. A `PatternError` from any pattern propagates.

## Examples

```python
expand("a{b,c}d") == ["abd", "acd"]
expand("{x,y}{1,2}") == ["x1", "x2", "y1", "y2"]

match("a*c", "abbbc") is True
match("a?c", "ac") is False
match("[[:digit:]]x", "7x") is True
match("A*", "abc", casefold=True) is True
filter(["*.log", "a?"], ["x.log", "ab", "abc"]) == ["x.log", "ab"]
```

Write a few quick checks of your own and run them with `python`, then reply "done".
