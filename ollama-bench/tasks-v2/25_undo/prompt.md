# 25_undo — text buffer with undo/redo and edit coalescing

Create `buffer.py` in the current directory containing a single class `Buffer`
(the grader will do `from buffer import Buffer`). Pure Python 3, standard
library only, no printing, no I/O.

## State

- `Buffer()` takes no arguments. Initial state: `text == ""`, `cursor == 0`.
- Readable properties `text` (a `str`) and `cursor` (an `int`). Invariant:
  always `0 <= cursor <= len(text)`.
- Internally the buffer keeps an **undo stack** and a **redo stack** of *undo
  groups*. The **undo depth** is the number of groups on the undo stack, the
  **redo depth** the number on the redo stack. Both are externally observable:
  from any state, `undo()` returns `True` exactly as many times as the undo
  depth (then `False` forever after), and `redo()` returns `True` exactly as
  many times as the redo depth.
- Each group records: its **kind** (`"insert"` or `"delete"` — a group never
  mixes kinds), the full state (text *and* cursor) **before** the group's
  first edit, the full state **after** the group's latest edit (its
  *post-cursor* is the cursor of that state), and `chars`: the accumulated
  number of characters the group accounts for.
- At any moment at most one group is **open**: the group a subsequent edit may
  coalesce into. Initially there is none. A **successful** `undo()` or `redo()`
  (one that returns `True`) and any cursor-changing `move()` **seal** the open group: it stays on the undo stack
  and remains one undoable/redoable unit, but nothing may coalesce into it
  again. Pushing a new group also seals the currently open group.

## Operations

### `insert(s)`

- If `s == ""`: a **complete no-op** — no group is created, extended or
  sealed, and the redo stack is untouched.
- Otherwise the string `s` is inserted at the cursor and the cursor advances
  by `len(s)`. This clears the whole redo stack.
- It coalesces into the open group **iff**: an open group exists, it is an
  insert group, the current cursor equals the group's post-cursor (i.e. the
  previous insertion in the group ended exactly where this one starts), and
  `group.chars + len(s) <= 10`. If it coalesces, the group's post-state and
  `chars` are updated. Otherwise a new insert group is pushed (recording the
  pre-edit state and the post-edit state) and becomes the open group.

### `delete(n)` — delete `n` characters forward from the cursor

- If `n < 0`: raise `BufferError` — the Python **built-in** exception; do not
  define your own class of that name. Nothing changes (validation happens first).
- Let `k = min(n, len(text) - cursor)` — deletions running past the end of
  the text are **clamped**. If `k == 0` (because `n == 0` or the deletion was
  clamped to nothing): a complete no-op, exactly like `insert("")`.
- Otherwise: remove `text[cursor:cursor+k]`; the cursor does **not** move.
  This clears the whole redo stack.
- Coalesces into the open group iff: an open group exists, it is a delete
  group, the current cursor equals the group's post-cursor, and
  `group.chars + k <= 10`; otherwise a new delete group is pushed (recording
  pre- and post-edit states) and becomes the open group.

### `backspace(n)` — delete `n` characters before the cursor

- If `n < 0`: raise `BufferError`. Nothing changes.
- Let `k = min(n, cursor)` — clamped at the start of the text. If `k == 0`:
  a complete no-op.
- Otherwise: remove `text[cursor-k:cursor]` and set the cursor to
  `cursor - k`. This clears the whole redo stack.
- Coalescing: the same rule as `delete`. The post-cursor of a backspace is
  `cursor - k` (the left end of the removed range); the post-cursor of a
  forward `delete` is the unchanged cursor. `delete` and `backspace` feed the
  same kind of group and may share one, so a run of deletion calls with no
  intervening cursor change coalesces into one group as long as the limit
  holds.

The character limit is exactly **10 per group** and the condition is
`group.chars + chars_of_this_edit <= 10`. A single edit larger than 10
characters is always allowed and simply forms its own group that no further
edit can ever join. An insertion never joins a delete group and vice versa:
an edit whose kind differs from the open group always pushes a new group
(thereby sealing the old one).

### `move(p)`

- If `p < 0` or `p > len(text)`: raise `BufferError`. Nothing changes
  (validation happens first).
- If `p == cursor`: a complete no-op (does **not** seal the open group).
- Otherwise: set the cursor to `p` and seal the open group. `move` **never**
  clears the redo stack, whether or not it actually moves.

### `undo()`

- If the undo stack is empty: return `False`; nothing changes.
- Otherwise: return `True`; pop the top group, restore its **before** state
  (both text and cursor exactly), and push the group onto the redo stack.
  Seals the open group. The rest of the redo stack is untouched.

### `redo()`

- If the redo stack is empty: return `False`; nothing changes.
- Otherwise: return `True`; pop the top group (the most recently undone one),
  restore its **after** state (both text and cursor exactly), and push it back
  onto the undo stack. Seals the open group. Note: `redo()` does **not**
  re-open the restored group — a following edit always starts a new group.

`insert`, `delete`, `backspace` and `move` return `None`. `undo`/`redo` return
`True`/`False`. Any edit that actually removes or inserts at least one
character clears the entire redo stack; `move`, `undo` and no-op edits never
do. `undo` grows the redo stack; `redo` grows the undo stack.

## Worked transcript

Starting from `b = Buffer()` (text `""`, cursor 0, undo depth 0, redo depth 0),
apply each call to the same buffer:

| step | call | text after | cursor | undo depth | redo depth | note |
|-----:|---------------------|-----------------|-------:|-----------:|-----------:|------|
| 1 | `insert("hello")` | `hello` | 5 | 1 | 0 | new insert group |
| 2 | `insert(" w")` | `hello w` | 7 | 1 | 0 | 5+2 <= 10, contiguous → coalesces |
| 3 | `insert("orld")` | `hello world` | 11 | 2 | 0 | 7+4 > 10 → new group |
| 4 | `move(5)` | `hello world` | 5 | 2 | 0 | seals the open group |
| 5 | `insert(",")` | `hello, world` | 6 | 3 | 0 | new group |
| 6 | `backspace(1)` | `hello world` | 5 | 4 | 0 | deletion can't join an insert group |
| 7 | `undo()` → `True` | `hello, world` | 6 | 3 | 1 | |
| 8 | `redo()` → `True` | `hello world` | 5 | 4 | 0 | |
| 9 | `backspace(5)` | ` world` | 0 | 5 | 0 | no open group after redo → new group |
| 10 | `delete(3)` | `rld` | 0 | 5 | 0 | cursor 0 == group post-cursor, 5+3 <= 10 → coalesces with the backspaces |
| 11 | `backspace(2)` | `rld` | 0 | 5 | 0 | clamped to 0 chars → complete no-op |
| 12 | `delete(10)` | (empty) | 0 | 6 | 0 | removes 3 (clamped); 8+3 > 10 → new group |
| 13 | `undo()` → `True` | `rld` | 0 | 5 | 1 | |
| 14 | `undo()` → `True` | `hello world` | 5 | 4 | 2 | |
| 15 | `undo()` → `True` | `hello, world` | 6 | 3 | 3 | |
| 16 | `undo()` → `True` | `hello world` | 5 | 2 | 4 | before-cursor of the insert-`,` group is 5 (where the group's first edit happened) |
| 17 | `undo()` → `True` | `hello w` | 7 | 1 | 5 | |
| 18 | `undo()` → `True` | (empty) | 0 | 0 | 6 | |
| 19 | `undo()` → `False` | (empty) | 0 | 0 | 6 | no-op |
| 20 | `redo()` → `True` | `hello w` | 7 | 1 | 5 | |
| 21 | `insert("!")` | `hello w!` | 8 | 2 | 0 | redo() left no open group → new group; redo stack cleared |
| 22 | `undo()` → `True` | `hello w` | 7 | 1 | 1 | |

After step 22, `move(99)` raises `BufferError` and changes nothing (not even
the open group or redo stack), and `backspace(-1)` likewise raises
`BufferError` and changes nothing. Also note `move(7)` would be valid there
(the cursor may equal `len(text)`) but is a complete no-op since the cursor is
already 7.

Write a few quick checks of your own and run them with `python`, then reply "done".
