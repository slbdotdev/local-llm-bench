"""Editor buffer with selection, clipboard, and undo/redo with coalescing."""

LIMIT = 12

_WORD = set("abcdefghijklmnopqrstuvwxyz"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "0123456789_")


class EditorError(ValueError):
    """Raised for invalid arguments; the editor is left untouched."""


class _Group(object):
    __slots__ = ("kind", "before", "after", "chars")

    def __init__(self, kind, before, after, chars):
        self.kind = kind
        self.before = before
        self.after = after
        self.chars = chars


class Editor(object):
    def __init__(self):
        self.text = ""
        self.cursor = 0
        self.anchor = 0
        self.clipboard = ""
        self._undo = []
        self._redo = []
        self._open = None
        self._goal = None

    # ---- queries -------------------------------------------------------
    def selection(self):
        return (min(self.anchor, self.cursor), max(self.anchor, self.cursor))

    def selected_text(self):
        lo, hi = self.selection()
        return self.text[lo:hi]

    def undo_depth(self):
        return len(self._undo)

    def redo_depth(self):
        return len(self._redo)

    # ---- internals -----------------------------------------------------
    def _state(self):
        return (self.text, self.cursor, self.anchor)

    def _line_start(self, p):
        return self.text.rfind("\n", 0, p) + 1

    def _line_index(self, p):
        return self.text.count("\n", 0, p)

    def _line_bounds(self, t):
        """Return (start, end) of line index t (t assumed in range)."""
        s = 0
        for _ in range(t):
            s = self.text.index("\n", s) + 1
        e = self.text.find("\n", s)
        if e < 0:
            e = len(self.text)
        return s, e

    def _apply_motion(self, p, extend):
        before = (self.cursor, self.anchor)
        if extend:
            self.cursor = p
        else:
            self.cursor = p
            self.anchor = p
        if (self.cursor, self.anchor) != before:
            self._open = None

    def _push(self, kind, before, chars):
        g = _Group(kind, before, self._state(), chars)
        self._undo.append(g)
        self._open = g if kind == "insert" else None
        self._redo = []

    # ---- motion --------------------------------------------------------
    def move_char(self, d, extend=False):
        if d != -1 and d != 1:
            raise EditorError("direction must be -1 or +1")
        self._goal = None
        lo, hi = self.selection()
        if not extend and lo != hi:
            p = lo if d == -1 else hi
        else:
            p = self.cursor + d
            if p < 0:
                p = 0
            elif p > len(self.text):
                p = len(self.text)
        self._apply_motion(p, extend)

    def move_word(self, d, extend=False):
        if d != -1 and d != 1:
            raise EditorError("direction must be -1 or +1")
        self._goal = None
        t = self.text
        p = self.cursor
        if d == 1:
            n = len(t)
            while p < n and t[p] not in _WORD:
                p += 1
            while p < n and t[p] in _WORD:
                p += 1
        else:
            while p > 0 and t[p - 1] not in _WORD:
                p -= 1
            while p > 0 and t[p - 1] in _WORD:
                p -= 1
        self._apply_motion(p, extend)

    def move_line(self, d, extend=False):
        if d != -1 and d != 1:
            raise EditorError("direction must be -1 or +1")
        if self._goal is None:
            self._goal = self.cursor - self._line_start(self.cursor)
        t = self._line_index(self.cursor) + d
        last = self.text.count("\n")
        if t < 0:
            p = 0
        elif t > last:
            p = len(self.text)
        else:
            s, e = self._line_bounds(t)
            p = s + min(self._goal, e - s)
        self._apply_motion(p, extend)

    def move_doc(self, d, extend=False):
        if d != -1 and d != 1:
            raise EditorError("direction must be -1 or +1")
        self._goal = None
        p = 0 if d == -1 else len(self.text)
        self._apply_motion(p, extend)

    def set_selection(self, a, c):
        n = len(self.text)
        if a < 0 or a > n or c < 0 or c > n:
            raise EditorError("position out of range")
        self._goal = None
        before = (self.cursor, self.anchor)
        self.anchor = a
        self.cursor = c
        if (self.cursor, self.anchor) != before:
            self._open = None

    # ---- edits ---------------------------------------------------------
    def insert(self, s):
        self._goal = None
        if s == "":
            return
        before = self._state()
        lo, hi = self.selection()
        kind = "insert" if lo == hi else "replace"
        self.text = self.text[:lo] + s + self.text[hi:]
        self.cursor = self.anchor = lo + len(s)
        g = self._open
        if (kind == "insert" and g is not None and "\n" not in s
                and g.after[1] == before[1] and g.chars + len(s) <= LIMIT):
            g.after = self._state()
            g.chars += len(s)
            self._redo = []
            return
        self._push(kind, before, len(s))
        if "\n" in s:
            self._open = None

    def _delete(self, n, forward):
        if n < 0:
            raise EditorError("count must be non-negative")
        self._goal = None
        lo, hi = self.selection()
        if lo != hi:
            before = self._state()
            self.text = self.text[:lo] + self.text[hi:]
            self.cursor = self.anchor = lo
            self._push("delsel", before, hi - lo)
            return
        c = self.cursor
        k = min(n, len(self.text) - c) if forward else min(n, c)
        if k == 0:
            return
        before = self._state()
        if forward:
            self.text = self.text[:c] + self.text[c + k:]
        else:
            self.text = self.text[:c - k] + self.text[c:]
            self.cursor = c - k
        self.anchor = self.cursor
        self._push("delfwd" if forward else "delback", before, k)

    def delete_forward(self, n):
        self._delete(n, True)

    def delete_back(self, n):
        self._delete(n, False)

    # ---- clipboard -----------------------------------------------------
    def copy(self):
        self._goal = None
        lo, hi = self.selection()
        if lo == hi:
            return
        self.clipboard = self.text[lo:hi]

    def cut(self):
        self._goal = None
        lo, hi = self.selection()
        if lo == hi:
            return
        self.clipboard = self.text[lo:hi]
        before = self._state()
        self.text = self.text[:lo] + self.text[hi:]
        self.cursor = self.anchor = lo
        self._push("cut", before, hi - lo)

    def paste(self):
        self._goal = None
        s = self.clipboard
        if s == "":
            return
        before = self._state()
        lo, hi = self.selection()
        self.text = self.text[:lo] + s + self.text[hi:]
        self.cursor = self.anchor = lo + len(s)
        self._push("paste", before, len(s))

    # ---- history -------------------------------------------------------
    def undo(self):
        self._goal = None
        if not self._undo:
            return False
        g = self._undo.pop()
        self.text, self.cursor, self.anchor = g.before
        self._redo.append(g)
        self._open = None
        return True

    def redo(self):
        self._goal = None
        if not self._redo:
            return False
        g = self._redo.pop()
        self.text, self.cursor, self.anchor = g.after
        self._undo.append(g)
        self._open = None
        return True
