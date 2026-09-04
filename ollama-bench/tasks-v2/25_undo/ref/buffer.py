"""Text buffer with undo/redo and edit coalescing."""

GROUP_CHAR_LIMIT = 10


class Buffer:
    def __init__(self):
        self._text = ""
        self._cursor = 0
        self._undo_stack = []   # list of group dicts, oldest first
        self._redo_stack = []
        self._open = None       # group the next edit may coalesce into

    @property
    def text(self):
        return self._text

    @property
    def cursor(self):
        return self._cursor

    def _push(self, kind, before, after, chars):
        group = {"kind": kind, "before": before, "after": after, "chars": chars}
        self._undo_stack.append(group)
        self._open = group

    def insert(self, s):
        if s == "":
            return
        before = (self._text, self._cursor)
        self._text = self._text[:self._cursor] + s + self._text[self._cursor:]
        self._cursor += len(s)
        after = (self._text, self._cursor)
        g = self._open
        if (g is not None and g["kind"] == "insert"
                and g["after"][1] == before[1]
                and g["chars"] + len(s) <= GROUP_CHAR_LIMIT):
            g["after"] = after
            g["chars"] += len(s)
        else:
            self._push("insert", before, after, len(s))
        self._redo_stack.clear()

    def delete(self, n):
        self._remove(n, True)

    def backspace(self, n):
        self._remove(n, False)

    def _remove(self, n, forward):
        if n < 0:
            raise BufferError("negative count")
        if forward:
            k = min(n, len(self._text) - self._cursor)
        else:
            k = min(n, self._cursor)
        if k == 0:
            return
        before = (self._text, self._cursor)
        if forward:
            start, end, post = self._cursor, self._cursor + k, self._cursor
        else:
            start, end, post = self._cursor - k, self._cursor, self._cursor - k
        self._text = self._text[:start] + self._text[end:]
        self._cursor = post
        after = (self._text, post)
        g = self._open
        if (g is not None and g["kind"] == "delete"
                and g["after"][1] == before[1]
                and g["chars"] + k <= GROUP_CHAR_LIMIT):
            g["after"] = after
            g["chars"] += k
        else:
            self._push("delete", before, after, k)
        self._redo_stack.clear()

    def move(self, p):
        if p < 0 or p > len(self._text):
            raise BufferError("cursor position out of range")
        if p == self._cursor:
            return
        self._cursor = p
        self._open = None

    def undo(self):
        if not self._undo_stack:
            return False
        g = self._undo_stack.pop()
        self._text, self._cursor = g["before"]
        self._redo_stack.append(g)
        self._open = None
        return True

    def redo(self):
        if not self._redo_stack:
            return False
        g = self._redo_stack.pop()
        self._text, self._cursor = g["after"]
        self._undo_stack.append(g)
        self._open = None
        return True
