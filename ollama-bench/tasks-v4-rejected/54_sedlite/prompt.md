Create `sedlite.py` in the current directory. It implements a small `sed`-like line-editing
language as pure string processing (no filesystem access, standard library only) and must
define exactly this API:

- `ScriptError` — an exception class you define. It **must subclass `ValueError`**, and every
  instance **must carry a `.kind` attribute** whose value is one of the twelve exact lowercase
  strings listed in "Syntax errors" below. It is raised by `run` for invalid scripts (only the
  cases listed there), before any input line is processed.
- `run(script, text, quiet=False)` — returns the output as a single `str`.

Library use: you MAY use `re` for compiling and *matching* only (`re.compile`, `.search`,
`.match`, `.finditer`, `.groups` and friends) — the regex syntax below is defined to be exactly
Python's. You must NOT use `re.sub`, `re.subn`, any `Pattern.sub`/`Pattern.subn`, or
`Match.expand`: build the `s///` replacement text yourself. You must NOT use `str.translate`
or `str.maketrans`: build the `y///` result yourself. Nothing else is banned.

## Input and output

1. `text` is split on `"\n"`. If the resulting list's LAST element is the empty string, that
   one element is removed. So `""` is zero lines, `"a\n"` is one line `a`, `"a"` is one line
   `a`, `"a\n\n"` is two lines `a` and `""`, and `"\n"` is one empty line.
2. Execution emits a sequence of *chunks* (strings). The return value is exactly the
   concatenation of every emitted chunk with `"\n"` appended to each one — a `str`, never a
   list, with no separator inserted between chunks and nothing added at the end. Output
   therefore always ends with a newline unless it is empty, and when nothing is emitted at all
   (no input lines, or `quiet` with no `p`, or every line deleted) the result is exactly `""`.
3. Lines are numbered from 1. `$` means the last line of the input.

## Script syntax

The script is scanned left to right. Repeat until the script is exhausted:

4. Skip any run of spaces, tabs, newlines and `;` characters. (Empty commands are allowed:
   `;;` and blank lines are fine.) If the script is exhausted, stop.
5. If the next character is `#`, everything up to the next newline (or the end of the script)
   is a comment and is discarded; go back to step 4. `#` is only a comment here, at a position
   where a command may start; anywhere else it is an ordinary character.
6. Parse an optional first address (§ Addresses). If one was parsed, skip spaces/tabs; if the
   next character is `,`, consume it, skip spaces/tabs and parse a second address, which must
   be present.
7. Skip spaces/tabs. Consume any run of `!` characters (skipping spaces/tabs after each). Two
   or more `!` is an error. One `!` negates the address match (§ Address matching); a `!` with
   no address at all is an error.
8. The next character must be a command letter, one of `s y d p q a i`; anything else
   (including the end of the script) is an error.
9. `d`, `p`, `q`, `s` and `y` are terminated by `;`, a newline, or the end of the script; after
   the command's own argument, spaces and tabs are skipped and then one of those three must
   follow (the `;` or newline is consumed). Any other character there is an error. `a` and `i`
   instead consume the whole rest of the LINE as their text: `;` and `#` inside that text are
   ordinary characters.

## Addresses

An address is one of these forms (`N`, `first`, `step` are runs of decimal digits):

10. `N` — matches line number `N`. `N` must be at least 1; `0` alone is an error.
11. `$` — matches the last line.
12. `/re/` — matches if the regex `re` is found anywhere in the pattern space (see § Regexes).
13. `first~step` — allowed only as a FIRST address. If `step` is 0 it matches only line
    `first`; otherwise it matches every line `L` with `L >= first` and `(L - first) % step == 0`.
    Here `first` may be 0, so `0~3` matches lines 3, 6, 9, ... and `2~0` matches only line 2.
    There may be no spaces around `~`.
14. `+N` — allowed only as a SECOND address (§ Ranges). `N` may be 0.

`first~step` may not be used as a second address; `+N` may not be used as a first address; in
either wrong position the parse of that address fails, which is an error.

## Address matching

15. A command with no address applies to every line.
16. A command with one address applies to a line iff that address matches it.
17. A command with two addresses (`addr1,addr2`) is a **range**. Each command in the script
    keeps its own range state — inactive or active-with-a-remembered start line — which
    persists from cycle to cycle. On each line `L`, with pattern space `PS` as it is at the
    moment this command is reached:
    - If the range is INACTIVE: test `addr1` against `L`/`PS`. If it does not match, the
      command does not apply and the state stays inactive. If it matches, the command applies,
      the start line is remembered as `L`, and the range becomes ACTIVE — *except* that it
      stays INACTIVE (a one-line range) if `addr2` is a plain number `<= L`, or is `+0`.
    - If the range is ACTIVE (it was started on an EARLIER line): the command applies, and then
      `addr2` is tested against this line: a number `M` closes the range if `L >= M`; `$`
      closes it if `L` is the last line; `/re/` closes it if the regex is found in `PS`; `+N`
      closes it if `L >= start + N`. If it closes, the state returns to inactive.
    So `addr2` is NEVER tested on the start line, a range that never closes runs to the end of
    the input, and once a range has closed `addr1` may start it again on a later line.
18. `!` inverts the final "applies / does not apply" decision. It does NOT change range
    bookkeeping: a range with `!` still activates and closes exactly as in rule 17.

## Regexes

19. A regex is written `/re/` in an address, or between the delimiters of `s`. Inside it, a
    backslash followed by the delimiter character produces that character; every other
    character, and every other backslash pair, is passed through UNCHANGED to Python's `re`.
    The result must be a valid Python regular expression, and it must not be empty (`//` and
    `s///` are errors).
20. So `.` `*` `+` `?` `[...]` (with ranges and `^` negation) `^` `$` `(...)` groups `|`
    alternation and the escapes `\.` `\*` `\[` `\\` `\n` `\t` `\(` `\)` `\|` `\+` `\?` `\$`
    `\^` all mean what they mean in Python. Matching is case-sensitive unless the `s` command
    has the `i` flag (then the whole regex is case-insensitive); address regexes are always
    case-sensitive.
21. The sequence of matches of a regex in a string is exactly the sequence Python's
    `re.finditer` produces for it.

## Delimiters

22. For `s` and `y`, the delimiter is the single character immediately following the command
    letter and must be one of ``/ , : # _ @ % !`` — any other character (or the end of the
    script/line) is an error. Each of the command's sections then runs up to the next
    delimiter that is not preceded by a backslash. A backslash always consumes the following
    character while scanning. A section may not contain a newline and the script may not end
    inside one (either is an error). Address regexes always use `/`.

## Commands

23. `s<d>re<d>repl<d>flags` — substitute. Flags are the run of alphanumeric characters after
    the closing delimiter, and may contain, in any order:
    - `g` — replace all matches instead of one;
    - `i` — case-insensitive regex;
    - `p` — print the pattern space immediately if a replacement was made;
    - one decimal number `N >= 1` — start at the `N`th match instead of the first.
    A flag letter given twice, a second number, the number `0`, and any other character are
    errors. With neither `g` nor a number, match 1 is replaced. With `N` and no `g`, ONLY match
    `N` is replaced (and nothing happens if there are fewer than `N` matches). With `g` and
    `N`, matches `N`, `N+1`, ... are ALL replaced (with `N` defaulting to 1). Replacing nothing
    counts as "no replacement made" for the `p` flag.
24. In the replacement text: `&` is the whole match; `\1`..`\9` are capture groups (a group
    that did not participate contributes the empty string; a number greater than the regex's
    group count is an error); `\n` is a newline; `\t` is a tab; `\` followed by ANY other
    character (including `\`, `&`, the delimiter, and a digit `0`) is that character literally.
    Every other character stands for itself. The replacement may be empty.
25. `y<d>src<d>dst<d>` — transliterate. In `src` and `dst`, `\n` is a newline, `\t` is a tab,
    and `\` followed by any other character is that character literally; a trailing `\` is a
    literal backslash. After that unescaping the two must have the same length (else an error);
    both being empty is allowed. Every character of the pattern space that appears in `src` is
    replaced by the character at the same index in `dst`; if a character occurs more than once
    in `src`, the LAST occurrence wins. Characters not in `src` are untouched.
26. `d` — delete: end this cycle immediately. No auto-print happens and no later command in the
    script runs on this line. Queued `a` text IS still emitted (rule 30).
27. `p` — emit the pattern space as a chunk immediately, even when `quiet` is true.
28. `a text` — queue `text` to be emitted at the end of the cycle (rule 30). `i text` — emit
    `text` as a chunk immediately, at the moment the command runs. In both, the text is the
    rest of the line with leading spaces and tabs removed, and it must not be empty (an error).
    `\n`, `\t` and `\`+any-other-character are unescaped exactly as in rule 25; an embedded
    newline therefore makes the chunk span several output lines.
29. `q` — quit: if `quiet` is false emit the pattern space, then emit the queued `a` text, then
    stop the whole run (no later command on this line, no later lines). `q` accepts at most ONE
    address; two addresses is an error.

## The cycle

30. For each input line in order: the pattern space is set to that line and the `a` queue is
    emptied; every command is considered in script order (rules 15-18 decide whether it
    applies) and executed if it applies. When the command list is exhausted, or a `d` or `q`
    ended it early: if the cycle was NOT ended by `d` and `quiet` is false, emit the pattern
    space; then emit every queued `a` text in the order it was queued; then, if the cycle was
    ended by `q`, stop. (For `q` the emission order is exactly: pattern space if not quiet,
    then the queue — which is what rule 29 says.)
31. `s` and `y` change the pattern space, so an address regex on a LATER command in the same
    cycle sees the changed text, as does a later `p`, `q` or auto-print.

## Syntax errors

32. `run` raises `ScriptError` for exactly the cases below and nothing else, with `.kind` set to
    exactly the listed string. An empty script (or one holding only blanks, `;` and comments)
    is legal and simply auto-prints every line.

    - `"bad_address"` — a `,` not followed by a parsable second address; `first~step` with
      nothing after `~`; `+` with nothing after it; the line number `0` used as a plain address
      (in either position).
    - `"unterminated"` — a `/re/`, or an `s`/`y` section, that runs into a newline or the end of
      the script (including a backslash immediately before that newline or end).
    - `"bad_regex"` — a regex that is empty, or that Python's `re` rejects.
    - `"bad_backref"` — a `\1`..`\9` in an `s` replacement greater than the pattern's group
      count (so `s/(a)(b)/\5/` is an error, never a silent empty string).
    - `"bad_delimiter"` — the character after `s` or `y` is not one of the eight allowed
      delimiters, or the script/line ends there.
    - `"bad_flag"` — an unknown `s` flag character, a flag letter repeated, a second numeric
      flag, or the numeric flag `0`.
    - `"bad_bang"` — a `!` with no address, or two or more `!`.
    - `"unknown_command"` — the character where a command letter is required is not one of
      `s y d p q a i`, or the script ends there. (A `+N` in first position and a `first~step` in
      second position both fail this way: the address parse simply does not consume them.)
    - `"extra_address"` — two addresses on `q`.
    - `"bad_y"` — `src` and `dst` of different lengths in `y`, after unescaping.
    - `"empty_text"` — empty `a`/`i` text.
    - `"trailing_garbage"` — characters other than spaces/tabs before the `;`, newline or end of
      script that must terminate a `d`, `p`, `q`, `s` or `y`.

33. **Error precedence.** Commands are parsed strictly left to right and the FIRST error
    encountered is the one reported, so an earlier bad command hides a later one. Within one
    command the checks happen in exactly this order:
    1. the first address, then (if a `,` follows) the second address — and within an address,
       the `/.../` is scanned to its closing delimiter (`unterminated`) before its contents are
       given to `re` (`bad_regex`);
    2. the `!` handling (`bad_bang`);
    3. the command letter (`unknown_command`);
    4. the address-count check for `q` (`extra_address`);
    5. the command's argument — for `s` and `y`: the delimiter (`bad_delimiter`), then each
       section scanned left to right (`unterminated`), then for `s` the FLAGS (`bad_flag`), then
       the regex (`bad_regex`), then the replacement's backreferences (`bad_backref`); for `y`
       the equal-length check (`bad_y`); for `a`/`i` the emptiness check (`empty_text`);
    6. the terminator check (`trailing_garbage`).

    So `1,2!!q` is `bad_bang` (not `extra_address`), `1,2q x` is `extra_address` (not
    `trailing_garbage`), `s/(/x/z/` is `bad_flag` (not `bad_regex`), `s/(/\1/` is `bad_regex`
    (not `bad_backref`), `s/(a)/\3/ x` is `bad_backref` (not `trailing_garbage`), `y/ab/c/ x` is
    `bad_y` (not `trailing_garbage`), and `1,x` is `bad_address` (not `unknown_command`).

Examples:

- `run("s/a/X/", "abca\nxyz\n")` is `"Xbca\nxyz\n"`
- `run("2d", "one\ntwo\nthree\n")` is `"one\nthree\n"`
- `run("/b/p", "a\nb\n", quiet=True)` is `"b\n"`
- `run("1a hello", "x\ny\n")` is `"x\nhello\ny\n"`
- `run("s,o,0,g", "foo boo\n")` is `"f00 b00\n"`

Write a few quick checks of your own and run them with `python`, then reply "done".
