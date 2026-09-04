Create `shquote.py`: POSIX-sh-like word splitting with quote removal, plus the inverse
(minimal shell quoting). Do not import `shlex` (or `subprocess`); implement the scanner
yourself.

```python
class SplitError(ValueError): ...        # has an attribute .kind (a str)

def split(s: str) -> list[str]: ...      # split a command line into words
def quote(word: str) -> str: ...         # minimal quoting of one word
def join(words: list[str]) -> str: ...   # " ".join(quote(w) for w in words)
```

## `split(s)`

Scan `s` strictly left to right, one character at a time, building up the current word.
There is no expansion of any kind: no variables, no globbing, no history, no aliases, and
**no comments** -- `#` is an ordinary character, so `split("a #b")` is `["a", "#b"]`.

1. **Whitespace** is exactly these four characters: space, tab (`\t`), newline (`\n`) and
   carriage return (`\r`). A run of whitespace ends the current word (if any) and starts a
   new one. Leading, trailing and repeated whitespace never produce empty words, so
   `split("")` and `split("   ")` are both `[]`.
2. **Single quotes.** A `'` starts a single-quoted section that runs up to the next `'`.
   Every character in between -- including whitespace, `"` and backslash -- is literal;
   there are no escapes at all inside single quotes. The two quote characters themselves
   are removed.
3. **Double quotes.** A `"` starts a double-quoted section that runs up to the next
   *unescaped* `"`. Inside it, a backslash escapes **only** `"` and `\`: `\"` produces `"`
   and `\\` produces `\`. Before ANY other character the backslash has no special meaning
   and is kept, together with that character: inside double quotes `\n` produces the two
   characters `\` and `n`, and `\$` produces `\` and `$`. In particular a backslash before
   a real newline is NOT a line continuation: both characters are kept. All other
   characters (whitespace included) are literal. The delimiting quotes are removed.
4. **Backslash outside quotes.** A backslash makes the very next character literal,
   whatever it is -- including space, tab, `\r`, a real newline, `'`, `"` and `\`. The
   backslash itself is removed. There is no line continuation: `"a\<newline>b"` written
   unquoted as `a\` + newline + `b` yields the single word `"a\nb"` (a word containing a
   newline).
5. **Quotes are word-internal.** Quoting only affects how characters are read; it never
   starts or ends a word. A word ends only at unquoted, unescaped whitespace (or at the end
   of the string). So `a'b'c` -> `["abc"]`, `x""y` -> `["xy"]`, `"a"'b'c` -> `["abc"]`.
   A word that is written entirely as empty quotes still exists: `''` -> `[""]`,
   `""` -> `[""]`, `'' ""` -> `["", ""]`, and `a'' ''b` -> `["a", "b"]`.

## Errors

`split`, `quote` and `join` never raise anything but `SplitError`, whose `.kind` is one of:

* `"type"` -- `s` / `word` is not a `str`, or `words` is not a `list` or `tuple`.
  This is checked first, before any scanning.
* `"escape"` -- the string ends while a backslash is still waiting for the character it
  escapes. That is, the last character of the string is a backslash that is acting as an
  escape: either outside quotes or inside a double-quoted section. (A backslash inside a
  single-quoted section is an ordinary character and can never cause this.)
* `"quote"` -- the end of the string is reached with a single- or double-quoted section
  still open.

**Precedence:** `"escape"` beats `"quote"`. A string that ends with an escaping backslash
inside an unterminated double quote raises kind `"escape"`, not `"quote"`. But because a
backslash is not an escape inside single quotes, a string that ends with a backslash inside
an unterminated *single* quote raises kind `"quote"`.

## `quote(word)`

Return the shortest of these three forms that is correct, using exactly this rule:

1. If `word` is the empty string, return `"''"` (two apostrophes).
2. Otherwise, if every character of `word` is in the safe set
   `A-Z a-z 0-9 @ % + = : , . / _ -` (that is, `[A-Za-z0-9@%+=:,./_-]`), return `word`
   unchanged.
3. Otherwise wrap `word` in single quotes and replace every apostrophe inside it with the
   four-character sequence `'"'"'` (close-quote, double-quoted apostrophe, re-open-quote).
   So `quote("it's")` is `'it'"'"'s'` (11 characters).

This is exactly `shlex.quote` -- but you must implement it yourself.

`join(words)` is `" ".join(quote(w) for w in words)`.

Invariants that must hold for every `str` `w` and every list of `str` `ws`:
`split(quote(w)) == [w]` and `split(join(ws)) == ws`.

Worked examples:

```python
split("ls -l  /tmp/x")            == ["ls", "-l", "/tmp/x"]
split("echo 'hello   world'")     == ["echo", "hello   world"]
split('say "hi there" now')       == ["say", "hi there", "now"]
split("a\\ b c")                  == ["a b", "c"]      # source: a\ b c
split("grep -n a#b file")         == ["grep", "-n", "a#b", "file"]
join(["git", "commit", "-m", "a message"]) == "git commit -m 'a message'"
```

Write a few quick checks of your own and run them with `python`, then reply "done".
