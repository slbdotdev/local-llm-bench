Create `reengine.py` in the current directory: a backtracking regular-expression engine written
from scratch.

**Bans (all enforced by reading your source):** do not import `re`, `regex`, `sre_compile`,
`sre_parse` or `_sre`; do not import `importlib` and do not call `__import__`; do not use the
`eval`, `exec` or `compile` builtins. Everything else in the standard library is fine, and no
third-party packages.

## 0. API

- `PatternError` — an exception class you define. It **must** subclass `ValueError`, and every
  instance you raise **must** have an attribute `kind` whose value is one of the exact lowercase
  strings listed in §7. The exception message is never checked; `kind` always is.
- `search(pattern, text)` — both arguments are `str`.
  - Returns `None` — the object `None` itself — if the pattern matches nowhere in `text`.
  - Otherwise returns a `tuple` of exactly three items, `(start, end, groups)`:
    - `start`, `end`: plain `int`s (not `bool`s), the half-open span of the overall match.
    - `groups`: a plain `list` with exactly one entry per **capturing** group, ordered by the
      position of the group's `(`, numbered from 1. The overall match is **not** included as an
      entry. Each entry is either `None` (that group did not participate in the final match) or a
      `tuple` `(gs, ge)` of two plain `int`s. A group that matched the empty string has
      `gs == ge` and is **not** `None`. A pattern with no capturing groups yields `[]`.
  - Raises `PatternError` if `pattern` is malformed (§7). This must happen for a malformed
    pattern whatever `text` is, including `""`.

The matching semantics below are exactly those of Python's `re` for this subset, but you must
implement them yourself.

## 1. Atoms

Reading a pattern left to right, an *atom* is one of:

1. `(` … `)` — a **capturing group**. `(?:` … `)` — a **non-capturing group**; it gets no number.
2. `[` … `]` — a character class (§3).
3. `.` — any single character **except** `\n`.
4. `^` — an *anchor*: matches only at position 0 of the text (there is no multi-line mode).
5. `$` — an *anchor*: matches at `len(text)`, and also at `len(text) - 1` when the text ends with
   `\n`. Nowhere else.
6. `\` followed by one character — an escape (§2).
7. Any other character — itself, literally. In particular `]` and `}` outside a class, and a `{`
   that does not start a well-formed quantifier (§4 rule 2), are ordinary literal characters: the
   pattern `{` matches the text `{`, and `a{x}` matches the text `a{x}`.

## 2. Escapes (outside a character class)

Applied in this order; `X` is the character after the backslash.

1. If there is no character after the backslash → error `trailing_backslash`.
2. `\d` = `[0-9]`; `\w` = `[A-Za-z0-9_]`; `\s` = one of space, `\t`, `\n`, `\r`, `\f`, `\v`.
   `\D`, `\W`, `\S` match exactly one character that is **not** in the corresponding set.
   These are ASCII-only; no Unicode categories.
3. `\n` `\t` `\r` `\f` `\v` are the single characters LF (0x0A), TAB (0x09), CR (0x0D),
   FF (0x0C), VT (0x0B).
4. `\b` is a zero-width *anchor*: it matches at a position where exactly one of the two adjacent
   characters is a **word character** (`[A-Za-z0-9_]`). Positions before index 0 and at index
   `len(text)` count as non-word. `\B` is the zero-width anchor matching exactly where `\b` does
   not.
5. Otherwise, if `X` is an ASCII letter or an ASCII digit (`A-Z`, `a-z`, `0-9`) → error
   `bad_escape`. This covers `\1`, `\q`, `\A`, `\Z`, `\x`; there are no back-references.
6. Otherwise the escape is the literal character `X` (so `\.`, `\\`, `\*`, `\[`, `\{`, `\-`,
   `\ `, `\|` are all ordinary literals).

## 3. Character classes

Parse a class in exactly this order, starting after the opening `[`:

1. If the next character is `^`, consume it: the class is **negated**.
2. If the next character (after a possible `^`) is `]`, that `]` is an ordinary **member**, not
   the terminator. So `[]]`, `[^]]` and `[]a]` are valid classes, while `[]` and `[^]` are not.
3. Then read members until an unescaped `]` is reached, which closes the class. Reaching the end
   of the pattern first → error `unterminated_class`.
4. A **member** is either an escape as in §2 rules 1-3, or a single ordinary character. Inside a
   class the only special characters are `\`, `]` and `-`; everything else (`[`, `^` other than
   the leading one, `.`, `*`, `(`, `|`, `$`, `{`, …) is a plain literal. Two escapes differ
   inside a class: `\b` is the backspace character U+0008 (it is **not** an anchor here), and
   `\B` is error `bad_escape`.
5. After reading a member `M`, look at the next character. It forms a **range** `M`-`N` iff it is
   `-` **and** there is a character after that `-` **and** that character is not `]`. In that case
   consume the `-`, read the next member `N`, and:
   - if `M` or `N` is one of `\d \w \s \D \W \S` → error `bad_range`;
   - if `ord(M) > ord(N)` → error `bad_range` (a reversed range is *not* an empty range);
   - otherwise the range matches every character `c` with `M <= c <= N` by code point.
   Otherwise `M` stands alone and parsing continues at the next character. Consequently a `-`
   that is the first member, or that sits immediately before the closing `]`, is an ordinary
   literal `-` member (`[-a]`, `[a-]`, `[a\-z]` all contain a literal `-`).
6. The class matches exactly one character: one that is a member, or — if the class is negated —
   one that is not a member. A class never matches at the end of the text. Negation does not
   exempt `\n`: `[^a]` matches a newline.

## 4. Quantifiers

After an atom has been parsed, a quantifier may follow. Apply these rules in order:

1. `*` means bounds 0..∞, `+` means 1..∞, `?` means 0..1.
2. `{` may start a bounded quantifier: read the run of ASCII digits after it as `LO`, then
   - if the next character is `}` **and** `LO` had at least one digit → bounds `LO`..`LO`;
   - else if the next character is `,`: read the following run of digits as `HI`, and if the
     character after that is `}` → bounds `LO` (0 when `LO` was empty) .. `HI` (unbounded when
     `HI` was empty). So `{2,}` is 2..∞ and `{,3}` is 0..3, a real quantifier, not a literal.
   - otherwise this `{` is **not** a quantifier: it is a literal `{` atom (§1 rule 7) and parsing
     resumes at the character right after it. `a{`, `a{2`, `a{x}`, `a{}`, `a{,}`, `a{2,x}` all
     contain a literal `{`.
3. If a quantifier was recognised and the very next character is `?`, consume it: the quantifier
   is **non-greedy**. Otherwise it is **greedy**.
4. If the recognised bounded quantifier has `LO > HI` → error `bad_repeat`.
5. If the quantifier was applied to an anchor (`^`, `$`, `\b`, `\B`) → error `anchor_repeat`.
6. If the character following the recognised quantifier (after its optional `?`) would itself
   start a quantifier by rules 1-2 → error `multiple_repeat`. `a**`, `a*?*`, `a?{2}`, `a{1,2}+`
   are all errors; `a*{` is not, because that `{` is not a quantifier.
7. A quantifier with no preceding atom in the current branch — at the start of the pattern, or
   right after `(`, `(?:` or `|` — is error `nothing_to_repeat`. This includes a brace quantifier
   that is well-formed by rule 2, so `{2}` and `{2,1}` on their own are both `nothing_to_repeat`.
   A `{` that is not well-formed by rule 2 is, as always, a literal.

## 5. Concatenation and alternation

A branch is a (possibly empty) concatenation of quantified atoms; a pattern (and each group body)
is one or more branches separated by `|`. `|` has the lowest precedence. Empty branches are legal
and match the empty string: `(a|)`, `(|a)`, `a||b`, `()` and the empty pattern are all valid.

## 6. Matching semantics — leftmost, then first found by backtracking

`search` tries start positions `0, 1, 2, …, len(text)` in that order and returns the **first**
position at which a match is found. Within one start position the engine performs an ordered
depth-first search and returns the **first** complete match it finds — which is not necessarily
the longest one. The order is:

1. Alternation tries its branches left to right.
2. Concatenation matches its first item, and for each way that item can match (in that item's own
   order) attempts the remainder; on failure it asks the item for its next way.
3. **Repetition** of a body `B` with bounds `m..n` at position `p`:
   - Iterations 1..`m` are mandatory: each one must match `B`. A mandatory iteration is allowed
     to consume no characters.
   - A further, optional iteration is attempted **only if** the number of iterations so far is
     below `n` **and** the previous iteration consumed at least one character (i.e. the current
     position differs from the position at which the previous iteration began). If the previous
     iteration consumed nothing, no further iteration is attempted — this is what stops `(a*)*`
     from looping forever. There is no previous iteration for the very first optional one, so the
     guard does not apply to it.
   - **Greedy**: try the optional iteration first; only if the whole remainder of the match fails
     from there, continue with what follows the repetition.
   - **Non-greedy**: try what follows the repetition first; only if that fails, try the optional
     iteration.
4. **Group capture.** When a group's body matches, that group's span becomes (position where this
   attempt of the body started, position where it ended). When the engine backtracks past a
   decision, every group span is restored to the value it had before that decision. The reported
   `groups` are the spans in effect at the instant the overall match succeeds. Two consequences
   you must reproduce: a group inside a repetition reports the span of the **last iteration in
   which it actually matched** — even when later iterations took a branch that did not contain it
   — and a group is `None` only if it never successfully matched along the surviving path.
5. Empty overall matches are legal and are returned like any other, as `(start, start, groups)`.
   A pattern that can match empty therefore always matches, at the leftmost position where it
   can.

## 7. Malformed patterns: the `kind` values, and the order they are decided in

The complete set of `kind` strings, with the complete set of causes:

| `kind` | raised for |
| --- | --- |
| `unbalanced_paren` | a `(` with no matching `)`, or a `)` with no matching `(` |
| `bad_group` | `(?` not followed by `:` (so `(?P<x>a)`, `(?=a)`, `(?` are all this) |
| `unterminated_class` | a class never closed, including `[`, `[]`, `[^]`, `[a-`, `[abc*` |
| `bad_range` | a range with reversed endpoints (`[z-a]`), or with a class escape as an endpoint (`[\d-z]`, `[a-\w]`) |
| `trailing_backslash` | a `\` as the last character of the pattern, inside or outside a class |
| `bad_escape` | §2 rule 5, and `\B` inside a class |
| `nothing_to_repeat` | §4 rule 7 |
| `anchor_repeat` | §4 rule 5 |
| `multiple_repeat` | §4 rule 6 |
| `bad_repeat` | §4 rule 4 |

Nothing else is an error; in particular every construct explicitly called "literal" above is
legal, and so are `[]]`, `[^]]`, `[a-]`, `[-a]`, `a{,3}`, `a*{`, `()`, `(|a)` and `]` on its own.

When a pattern is malformed in more than one way, exactly one `kind` must be reported, decided by
this rule: **the pattern is validated during a single left-to-right parse, and the first error
that parse runs into is the one raised.** A construct is checked at the moment the parse has
finished reading it, and the checks of §4 are applied to a quantifier in the order they are
numbered there (4.4 `bad_repeat`, then 4.5 `anchor_repeat`, then 4.6 `multiple_repeat`), while
§4 rule 7's `nothing_to_repeat` is decided before any of them because it is decided as soon as
the quantifier is recognised. An unterminated class, a trailing backslash and an unclosed `(` are
each only detected when the parse reaches the end of the pattern, so any error inside them is
found first. Worked consequences: `"(a{3,1}"` → `bad_repeat`; `"*[abc"` → `nothing_to_repeat`;
`"[abc*"` → `unterminated_class`; `"(\q"` → `bad_escape`; `"[z-a"` → `bad_range`; `"^{2,1}"` →
`bad_repeat`; `"^*+"` → `anchor_repeat`; `"{2,1}"` → `nothing_to_repeat`.

## Examples

```python
search("a+b", "xaaab")                 == (1, 5, [])
search(r"(\d+)-(\d+)", "sum 12-345!")  == (4, 10, [(4, 6), (7, 10)])
search("colou?r", "color")             == (0, 5, [])
search("^b", "ab")                     is None
search("(x)|(y)", "wy")                == (1, 2, [None, (1, 2)])
```

Write a few quick checks of your own and run them with `python`, then reply "done".
