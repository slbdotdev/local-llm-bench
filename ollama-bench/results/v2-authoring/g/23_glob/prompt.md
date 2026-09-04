Create `globmatch.py` in the current directory. It implements a gitignore-style path
matcher as pure string processing (no filesystem access, standard library only) and must
define exactly this API:

- `RuleError` — an exception class you define; raised for invalid patterns (only the two
  invalid cases listed below).
- `compile_rules(lines)` — `lines` is a list of strings (or any iterable of strings), each
  element being one pattern line, with no trailing newline. Returns the compiled rules in
  any form you like; that value is what gets passed back to `is_ignored`. Raises
  `RuleError` if any line is an invalid pattern.
- `is_ignored(path, rules)` — returns `True` iff the path is ignored under the compiled
  rules.

## Paths

A path is a non-empty string of non-empty components separated by `/`, with at most one
trailing `/`. A trailing `/` marks the path as a **directory**; without it the path is a
**file**. Paths never begin with `/` and matching is case-sensitive. Components are raw
text, never escaped; they may contain any character except `/` (so `"a b"`, `#x`, `x*`,
`a\b` are all valid components).

## Turning one line into a rule — exact order

1. Strip trailing spaces: repeatedly, while the line ends with a space character, remove
   that final space unless it is escaped. A character is escaped iff it is immediately
   preceded by an odd number of backslashes. Leading spaces are NOT stripped.
2. If the line is now empty, skip it entirely (it matches nothing).
3. If the line begins with `#` (unescaped), it is a comment: skip it entirely.
4. If the line begins with `!` (unescaped), the rule is a **negation**: remove the `!` and
   continue processing the rest as the pattern. A `!` anywhere else is an ordinary
   character.
5. If the pattern ends with `/`, the rule is **directory-only**: remove exactly that one
   trailing `/`.
6. If the pattern begins with `/`, it is anchored: remove ALL leading `/` characters.
7. The pattern is anchored if it (still) contains a `/` anywhere; otherwise it is
   unanchored.

Everywhere else, a backslash escapes the next character: the two-character pair becomes
one ordinary literal character (so `\!`, `\#`, `\ `, `\*`, `\?`, `\[`, `\]`, `\\`, `\/`
all produce literals, and the escaped character loses all special meaning). A backslash
as the final character of the line makes the pattern **invalid**.

Two consequences worth stating explicitly: an escaped `/` is an ordinary literal
character, which no component can contain, so such a pattern matches nothing (but it
still counts for anchoring in step 7); and a pattern that is empty after the steps above
(e.g. the line `!` or the line `/`) matches nothing.

## Matching one pattern

Split the pattern into segments on unescaped `/`. An **empty segment** (arising from
consecutive slashes) matches no component, so a pattern containing one matches nothing.

- **Anchored** pattern: its segments are matched against the full list of the path's
  components, in order, with all of them consumed.
- **Unanchored** pattern (it then always has exactly one segment): it matches if that one
  segment matches any ONE of the path's components, at any depth.

Within that framework:

- A segment consisting of exactly `**` matches zero or more consecutive components. So
  `a/**` matches `a` itself as well as `a/b` and `a/b/c`; `**/x` matches `x`, `a/x`,
  `a/b/x`.
- Any other segment matches exactly one component:
  - `*` matches any run of zero or more characters; `?` matches exactly one character.
    Neither treats leading dots specially (`*` matches `.hidden`).
  - `[...]` matches exactly one character: `[abc]` any listed character; `[a-z]` a range
    by code point; members and ranges may be mixed (`[a-cx0-9]`); `[!abc]` any character
    NOT in the set (negation is written with `!` only; `^` inside a class is an ordinary
    character).
  - Inside a class: a `]` immediately after `[` or `[!` is a literal member; a `-` at the
    start of the class or immediately before the closing `]` is a literal member; a
    backslash escapes the next character (`[\]]` contains `]`, `[\-z]` contains `-`); an
    unescaped `-` between two member characters (the character to its right not being
    `]` or end of line) forms a range; a reversed range such as `[z-a]` matches nothing
    (the other members of the class still apply).
- A **directory-only** rule can only match a path that itself is a directory (i.e. the
  path argument ends with `/`). It never matches a file path directly.

## Deciding `is_ignored(path, rules)`

1. If any proper ancestor directory of the path is ignored — apply this entire definition
   recursively to the ancestor's path with a `/` appended (for `a/b/c` that means
   checking `a/` and `a/b/`) — then the path is ignored. This is checked first and cannot
   be undone: no negation rule can re-include a path that lies inside an ignored
   directory.
2. Otherwise walk the rules in order. The decision starts as "not ignored"; every
   matching rule sets the decision to "ignored", or to "not ignored" if the rule is a
   negation. In other words the last matching rule wins, and if no rule matches, the path
   is not ignored.

Invalid patterns — `compile_rules` raises `RuleError` for exactly these two: an
unterminated character class (a `[` with no closing `]` anywhere later in the line; this
includes `[]` and `[!`), and a backslash as the final character of the line.

Examples:

- `is_ignored("build/x", compile_rules(["build/"]))` is `True` (ancestor rule), while
  `is_ignored("build", ...)` is `False` (that path is a file).
- `is_ignored("a/keep.log", compile_rules(["*.log", "!keep.log"]))` is `False`;
  `is_ignored("a/x.log", ...)` is `True`.
- `is_ignored("b", compile_rules(["/b"]))` is `True`; `is_ignored("a/b", ...)` is
  `False`.

Write a few quick checks of your own and run them with `python`, then reply "done".
