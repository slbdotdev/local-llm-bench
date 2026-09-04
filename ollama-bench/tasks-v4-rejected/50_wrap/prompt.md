Create `dwrap.py` in the current directory: unicode-aware display width, tab expansion,
line wrapping and truncation.

```python
def char_width(ch: str) -> int
def width(s: str) -> int
def clusters(s: str) -> list[str]
def expand_tabs(s: str, tabsize: int = 8) -> str
def wrap(text: str, budget: int, tabsize: int = 8) -> list[str]
def truncate(s: str, budget: int, ellipsis: str = "\N{HORIZONTAL ELLIPSIS}") -> str
```

You MAY import `unicodedata` (you will need it). You must NOT import `textwrap` or
`wcwidth`, and no third-party library at all.

Throughout, "ZW" means the four characters U+200B (ZERO WIDTH SPACE), U+200C (ZERO WIDTH
NON-JOINER), U+200D (ZERO WIDTH JOINER) and U+FEFF (ZERO WIDTH NO-BREAK SPACE).
"space" always means exactly U+0020, never any other whitespace character.
Inputs never contain control characters other than TAB (U+0009) and LF (U+000A).

## 1. `char_width(ch)` -- display columns of one character

Apply these rules in order, first match wins:
1. If `unicodedata.combining(ch) != 0` -> `0`.
2. Else if `ch` is one of the four ZW characters -> `0`.
3. Else if `unicodedata.east_asian_width(ch)` is `"W"` or `"F"` -> `2`.
4. Else -> `1`.

Note rule 4 covers `"A"` (ambiguous, e.g. U+2026 HORIZONTAL ELLIPSIS and U+00B1) and
`"H"` (halfwidth, e.g. U+FF76): those are **1** column wide. TAB counts as 1 by these
rules, but `wrap` expands tabs before measuring anything, so that never matters there.

`width(s)` is simply the sum of `char_width` over every character of `s`;
`width("") == 0`.

## 2. `clusters(s)` -- splitting into unbreakable units

Nothing may ever be cut in the middle of a cluster. `clusters(s)` returns the list of
clusters, in order, whose concatenation is exactly `s` (so `clusters("") == []`).
Compute it with exactly this scan:

```
i = 0
while i < len(s):
    j = i + 1
    while j < len(s):
        c = s[j]
        if unicodedata.combining(c) != 0 or c is one of the four ZW characters:
            j += 1
            if c is U+200D and j < len(s):
                j += 1              # ZWJ also glues the character after it
            continue
        break
    emit s[i:j]
    i = j
```

Consequences you must reproduce: a cluster's width is the sum of its characters' widths
(so a wide base plus a combining mark is 2, and `A U+200D B` where both A and B are wide
is 4). A leading combining mark, or a leading U+200D, becomes a cluster of its own.
A space followed by a combining mark forms a two-character cluster which is therefore
**not** a plain space cluster.

## 3. `expand_tabs(s, tabsize=8)`

Walk `s` left to right keeping a display column `col`, starting at 0.
* TAB emits `tabsize - (col % tabsize)` spaces (always at least 1, at most `tabsize`) and
  advances `col` by that many.
* LF is emitted unchanged and resets `col` to 0.
* Any other character is emitted unchanged and advances `col` by `char_width(ch)`
  (so a wide character advances the column by 2).

## 4. `wrap(text, budget, tabsize=8)` -> list of lines

Steps:
1. `text = expand_tabs(text, tabsize)`.
2. Split on LF into segments. Wrap each segment independently and concatenate the
   resulting lists in order. A segment that produces no lines at all (it was empty, or
   held only spaces) contributes exactly one line, the empty string `""`. So the result
   is never `[]`, and blank input lines survive as blank output lines.
3. To wrap one segment: take its clusters and group them into *pieces*.
   * A maximal run of one or more clusters that are each exactly the single character
     U+0020 is one **gap** piece.
   * Every other maximal run of clusters is a run of **word** pieces: scan it left to
     right accumulating clusters, and end the current word piece immediately after any
     cluster whose FIRST character is `-` (U+002D). Any leftover at the end of the run is
     a final word piece. So `"well-known"` gives `["well-", "known"]`, `"a--b"` gives
     `["a-", "-", "b"]`, and `"-x"` gives `["-", "x"]`. Word pieces are never empty.
4. Now fill lines greedily. Keep `cur` (the current line, initially `""`) and `held`
   (a pending gap, initially `""`). For each piece in order:
   * **gap**: if `cur` is `""` the gap is discarded (leading gaps never appear in output);
     otherwise append its text to `held`.
   * **word** with text `t`: if `cur` is not `""` and
     `width(cur) + width(held) + width(t) <= budget`, then set `cur = cur + held + t`,
     clear `held`, and continue. Otherwise, if `cur` is not `""`, emit `cur` as a
     finished line and reset both `cur` and `held` to `""` (a gap at the end of a line is
     dropped, never emitted and never counted). Then place `t` on the now-empty line:
     * if `width(t) <= budget`, set `cur = t`;
     * else break the long word: walk `t`'s clusters, accumulating a chunk; before adding
       a cluster of width `cw` to a non-empty chunk of width `chw`, if `chw + cw > budget`
       emit the chunk as a finished line and start a new empty chunk. A cluster is always
       added to an empty chunk even if it alone is wider than the budget (so with
       `budget == 1` a wide character is emitted alone on its line, overflowing it).
       After the walk the final chunk becomes `cur` -- it is NOT emitted yet, so a
       following word can still be appended to the tail of a broken long word.
   When the pieces run out, emit `cur` if it is not `""`; a trailing `held` is discarded.

The rules above are the whole story; note in particular that runs of spaces INSIDE a line
are **preserved verbatim** (never collapsed) and count their full width against the budget,
while gaps at the start or the end of a line are dropped.
`budget` must be an `int` (a `bool` is not acceptable) and `>= 1`; `tabsize` must be an
`int` and `>= 1`; otherwise raise `ValueError`. `expand_tabs` applies the same rule to
`tabsize`.

## 5. `truncate(s, budget, ellipsis=...)`

`budget` must be an `int` (not a `bool`) and `>= 0`, else `ValueError`. Then:
1. If `width(s) <= budget`, return `s` unchanged.
2. Else if `width(ellipsis) > budget`, return `""`.
3. Else let `room = budget - width(ellipsis)`. Take clusters of `s` from the left while
   the accumulated width stays `<= room`, stopping at the first cluster that would push it
   over. Then drop trailing clusters that are exactly the single character U+0020, one by
   one, from the kept prefix. Return that prefix concatenated with `ellipsis`.

`ellipsis` is an arbitrary string (it may be `"..."`, `""`, or contain wide characters);
its width is measured with the same `width` rules. Because clusters are never split, the
result can be narrower than `budget` (for example when the next cluster is 2 columns wide
but only 1 column is left).

## Examples

```python
width("hi") == 2
width("a" + chr(0x4E2D) + "b") == 4              # U+4E2D is East Asian Wide

clusters("ab") == ["a", "b"]

expand_tabs("ab\tc") == "ab      c"              # tabsize 8: pad to column 8
expand_tabs("a\tb", 4) == "a   b"

wrap("the quick brown fox", 9) == ["the quick", "brown fox"]
wrap("hello\n\nworld", 10) == ["hello", "", "world"]

truncate("hello world", 8) == "hello w" + chr(0x2026)
truncate("abc", 10) == "abc"
```

Write a few quick checks of your own and run them with `python`, then reply "done".
