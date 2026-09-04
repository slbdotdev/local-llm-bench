# 48_editor — editor buffer with selection, clipboard and undo/redo

Create `editor.py` in the current directory. Pure Python 3, standard library
only, no printing, no I/O. **Do not import `re` and do not import `copy`** (no
third-party modules either). The grader does
`from editor import Editor, EditorError`.

`EditorError` must be a class you define that is a subclass of `ValueError`.

## State

`Editor()` takes no arguments. It exposes four readable attributes:

- `text` — a `str`, initially `""`.
- `cursor` — an `int` in `[0, len(text)]`, initially `0`.
- `anchor` — an `int` in `[0, len(text)]`, initially `0`.
- `clipboard` — a `str`, initially `""`.

The **selection** is the character range `[lo, hi)` where
`lo = min(anchor, cursor)` and `hi = max(anchor, cursor)`. It is **empty** iff
`anchor == cursor`. Two query methods must exist:

- `selection()` → the tuple `(lo, hi)`.
- `selected_text()` → `text[lo:hi]`.

Two more query methods report the undo machinery:

- `undo_depth()` → the number of groups on the undo stack.
- `redo_depth()` → the number of groups on the redo stack.

Query methods (`selection`, `selected_text`, `undo_depth`, `redo_depth`) and
attribute reads never change anything.

### Undo groups

Undo history is a stack of **groups**. Each group stores its **kind**, the full
state `(text, cursor, anchor)` **before** its first edit, the full state
**after** its latest edit, and `chars`, the number of characters the group has
accounted for so far. The clipboard is **not** part of a group's state: undo and
redo never change `clipboard`.

At most one group is **open** at a time — the group a later edit may coalesce
into. Initially there is none. To **seal** means: set the open group to "none";
the group stays on the undo stack as one undoable unit but nothing can join it
any more. Pushing a new group seals whatever was open before.

### Goal column

The editor keeps a **goal column**, initially "none". **Every** call to an
*operation* method other than `move_line` sets the goal column back to "none",
even when that call turns out to be a complete no-op. The operation methods are
`insert`, `delete_forward`, `delete_back`, `move_char`, `move_word`,
`move_line`, `move_doc`, `set_selection`, `copy`, `cut`, `paste`, `undo`,
`redo`. (Query methods do not touch it.)

If an operation raises `EditorError`, **nothing at all changes** — not the text,
cursor, anchor, clipboard, stacks, open group, or goal column.

A **complete no-op** means: no group is created, extended or sealed, the redo
stack is untouched, and no attribute changes. (The goal column is still reset,
per the rule above, unless the call was `move_line`.)

## Lines, words, characters

- Lines are separated by `"\n"`. For a position `p`:
  `line_start(p) = text.rfind("\n", 0, p) + 1`, the **column** of `p` is
  `p - line_start(p)`, and the **line index** of `p` is `text.count("\n", 0, p)`.
  The buffer always has `text.count("\n") + 1` lines (so `""` has one line).
- A **word character** is one of `a-z`, `A-Z`, `0-9`, `_`. Everything else
  (including `"\n"`) is a separator.

## Motion

All four motion methods take `(d, extend=False)` where `d` must be `-1` or `+1`;
any other value of `d` raises `EditorError`. They return `None`.

Each motion computes a new cursor position `p` as described below, then:

- if `extend` is true: `cursor = p`, `anchor` unchanged;
- if `extend` is false: `cursor = anchor = p`.

If the resulting `(cursor, anchor)` pair equals the one before the call, the
motion is a complete no-op; otherwise it **seals** the open group. Motions never
touch the undo or redo stacks.

- **`move_char(d, extend=False)`** — if `extend` is false **and** the selection
  is non-empty, the motion only *collapses* the selection: `p = lo` when
  `d == -1`, `p = hi` when `d == +1` (the cursor does **not** move an extra
  character). Otherwise `p = cursor + d`, clamped into `[0, len(text)]`.
- **`move_word(d, extend=False)`** — always measured from the current `cursor`
  (there is no collapse rule here). Starting from `p = cursor`:
  for `d == +1`, first `while p < len(text) and text[p]` is **not** a word
  character: `p += 1`; then `while p < len(text) and text[p]` **is** a word
  character: `p += 1`.
  For `d == -1`, first `while p > 0 and text[p-1]` is **not** a word character:
  `p -= 1`; then `while p > 0 and text[p-1]` **is** a word character: `p -= 1`.
- **`move_line(d, extend=False)`** — vertical motion. If the goal column is
  "none", set it to the current column of `cursor`. Let `t` be the line index of
  `cursor` plus `d`. If `t < 0` then `p = 0`; if `t` is past the last line then
  `p = len(text)`; otherwise `p = s + min(goal, e - s)` where `s` is the start
  of line `t` and `e` is its end (the index of that line's `"\n"`, or
  `len(text)` for the last line). The goal column keeps its value in all three
  cases.
- **`move_doc(d, extend=False)`** — `p = 0` for `d == -1`, `p = len(text)` for
  `d == +1`.

**`set_selection(a, c)`** — if `a` or `c` is outside `[0, len(text)]`, raise
`EditorError`. Otherwise set `anchor = a`, `cursor = c`; if that leaves
`(cursor, anchor)` unchanged it is a complete no-op, else it seals the open
group. Returns `None`.

## Edits

Every edit that actually changes the text clears the **whole** redo stack.
No-ops and motions never clear it. All edit methods return `None`.

- **`insert(s)`** — if `s == ""` this is a complete no-op (in particular the
  selection is **not** deleted). Otherwise, with `(lo, hi)` the selection, the
  new text is `text[:lo] + s + text[hi:]` and `cursor = anchor = lo + len(s)`.
  The group kind is `"insert"` if the selection was empty, else `"replace"`.
- **`delete_forward(n)` / `delete_back(n)`** — if `n < 0`, raise `EditorError`.
  If the selection is **non-empty**, the selection is deleted and `n` is
  **ignored entirely** (even `n == 0` deletes the selection): the new text is
  `text[:lo] + text[hi:]`, `cursor = anchor = lo`, kind `"delsel"`.
  Otherwise let `k = min(n, len(text) - cursor)` for `delete_forward` and
  `k = min(n, cursor)` for `delete_back`. If `k == 0` this is a complete no-op.
  `delete_forward` removes `text[cursor:cursor+k]` and leaves the cursor where
  it is; `delete_back` removes `text[cursor-k:cursor]` and sets
  `cursor = cursor - k`. In both cases `anchor = cursor` afterwards. The kinds
  are `"delfwd"` and `"delback"` respectively.
- **`copy()`** — if the selection is empty, a complete no-op. Otherwise set
  `clipboard` to the selected text. Nothing else happens: the text, cursor and
  anchor are unchanged, no group is created, the redo stack is untouched, and
  the open group is **not** sealed.
- **`cut()`** — if the selection is empty, a complete no-op (the clipboard is
  left alone). Otherwise set `clipboard` to the selected text and delete the
  selection exactly as `"delsel"` does, but with kind `"cut"`.
- **`paste()`** — if `clipboard == ""` this is a complete no-op, **even when
  the selection is non-empty**. Otherwise it replaces the selection with the
  clipboard exactly as `insert(clipboard)` would change text/cursor/anchor, but
  the group kind is `"paste"`.

### Coalescing

After an edit, the newly created group becomes the open group **only** if its
kind is `"insert"` **and** the inserted string contains no `"\n"`. Groups of
kind `"replace"`, `"delsel"`, `"cut"`, `"paste"`, `"delfwd"`, `"delback"`, and
`"insert"` groups whose text contained a newline, are sealed the moment they are
created, so nothing can ever coalesce into them. *(Consequently two consecutive
`delete_forward` calls never merge into one group either.)*

An `insert(s)` coalesces into the open group instead of pushing a new one iff
**all** of these hold:

1. there is an open group (its kind is therefore `"insert"`);
2. the selection is empty (so this edit's kind is `"insert"`);
3. `"\n" not in s`;
4. `cursor` (before the edit) equals the cursor stored in the open group's
   *after* state;
5. `group.chars + len(s) <= 12`.

When it coalesces, the group's *after* state and `chars` are updated; otherwise
a new group is pushed. A single insert longer than 12 characters is fine — it
just forms its own group (which is still "open" by the rule above, but rule 5
will then reject every later insert, so nothing can ever join it).

## Undo / redo

- **`undo()`** — if the undo stack is empty, return `False` (a complete no-op).
  Otherwise pop the top group, restore its *before* `(text, cursor, anchor)`
  exactly, push it onto the redo stack, seal, and return `True`.
- **`redo()`** — if the redo stack is empty, return `False` (a complete no-op).
  Otherwise pop the top group of the redo stack, restore its *after*
  `(text, cursor, anchor)` exactly, push it back onto the undo stack, seal, and
  return `True`. A successful `redo()` does **not** re-open the group.

## Examples

```python
e = Editor()
e.insert("hello")            # text "hello", cursor 5, anchor 5
e.insert(" you")             # coalesces: 5 + 4 <= 12  -> undo_depth() == 1
e.set_selection(6, 9)        # selects "you"
e.insert("me")               # kind "replace": text "hello me", cursor 8
assert (e.text, e.cursor, e.anchor) == ("hello me", 8, 8)
assert e.undo_depth() == 2
e.undo()                     # back to "hello you", with cursor 9 and anchor 6
assert (e.text, e.cursor, e.anchor) == ("hello you", 9, 6)

e = Editor()
e.insert("one two three")
e.move_doc(-1)               # cursor 0
e.move_word(+1)              # cursor 3 (end of "one")
e.move_word(+1, extend=True) # cursor 7, anchor 3 -> selection (3, 7)
assert e.selected_text() == " two"
e.cut()                      # text "one three", clipboard " two", cursor 3
assert (e.text, e.clipboard, e.cursor, e.anchor) == ("one three", " two", 3, 3)

e = Editor()
e.insert("abcdef")
e.move_char(-1)              # cursor 5
e.delete_back(2)             # text "abcf", cursor 3
e.undo()
assert (e.text, e.cursor, e.anchor) == ("abcdef", 5, 5)
assert e.redo_depth() == 1

e = Editor()
e.insert("ab")
e.undo()
e.insert("z")                # a new edit after an undo clears the redo stack
assert e.redo_depth() == 0 and e.text == "z"
```

Write a few quick checks of your own and run them with `python`, then reply "done".
