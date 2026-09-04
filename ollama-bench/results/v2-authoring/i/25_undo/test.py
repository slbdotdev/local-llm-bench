"""Hidden grader for 25_undo (text buffer with undo/redo and coalescing)."""
import sys, random
fails = []
def check(name, cond):
    if not cond: fails.append(name)

def drain_undo(b):
    n = 0
    while b.undo() is True: n += 1
    return n

def drain_redo(b):
    n = 0
    while b.redo() is True: n += 1
    return n


class Model:
    """Reference model: stores full snapshots per undo group."""
    LIMIT = 10
    def __init__(self):
        self.text = ""
        self.cursor = 0
        self.undo_stack = []
        self.redo_stack = []
        self.open = None
    def _push(self, kind, before, after, chars):
        g = {"kind": kind, "before": before, "after": after, "chars": chars}
        self.undo_stack.append(g); self.open = g
    def insert(self, s):
        if s == "": return
        before = (self.text, self.cursor)
        self.text = self.text[:self.cursor] + s + self.text[self.cursor:]
        self.cursor += len(s)
        g = self.open
        if (g is not None and g["kind"] == "insert"
                and g["after"][1] == before[1]
                and g["chars"] + len(s) <= self.LIMIT):
            g["after"] = (self.text, self.cursor); g["chars"] += len(s)
        else:
            self._push("insert", before, (self.text, self.cursor), len(s))
        self.redo_stack = []
    def _remove(self, n, forward):
        if n < 0: raise BufferError("negative count")
        k = min(n, len(self.text) - self.cursor) if forward else min(n, self.cursor)
        if k == 0: return
        before = (self.text, self.cursor)
        if forward: start, end, post = self.cursor, self.cursor + k, self.cursor
        else: start, end, post = self.cursor - k, self.cursor, self.cursor - k
        self.text = self.text[:start] + self.text[end:]
        self.cursor = post
        g = self.open
        if (g is not None and g["kind"] == "delete"
                and g["after"][1] == before[1]
                and g["chars"] + k <= self.LIMIT):
            g["after"] = (self.text, post); g["chars"] += k
        else:
            self._push("delete", before, (self.text, post), k)
        self.redo_stack = []
    def delete(self, n): self._remove(n, True)
    def backspace(self, n): self._remove(n, False)
    def move(self, p):
        if p < 0 or p > len(self.text): raise BufferError("out of range")
        if p == self.cursor: return
        self.cursor = p; self.open = None
    def undo(self):
        if not self.undo_stack: return False
        g = self.undo_stack.pop()
        self.text, self.cursor = g["before"]
        self.redo_stack.append(g); self.open = None
        return True
    def redo(self):
        if not self.redo_stack: return False
        g = self.redo_stack.pop()
        self.text, self.cursor = g["after"]
        self.undo_stack.append(g); self.open = None
        return True


def run_op(obj, op):
    k = op[0]
    if k == "insert": return obj.insert(op[1])
    if k == "delete": return obj.delete(op[1])
    if k == "backspace": return obj.backspace(op[1])
    if k == "move": return obj.move(op[1])
    if k == "undo": return obj.undo()
    if k == "redo": return obj.redo()
    if k == "drain_undo":
        n = 0
        while obj.undo() is True: n += 1
        return n
    if k == "drain_redo":
        n = 0
        while obj.redo() is True: n += 1
        return n


try:
    from buffer import Buffer

    # --- basics ---
    b = Buffer()
    check("initial text", b.text == "")
    check("initial cursor", b.cursor == 0)
    b = Buffer(); b.insert("hello")
    check("insert basic", (b.text, b.cursor) == ("hello", 5))
    b.move(2); b.insert("XY")
    check("insert middle", (b.text, b.cursor) == ("heXYllo", 4))

    # --- insert coalescing ---
    b = Buffer(); b.insert("ab"); b.insert("cd")
    check("contig coalesce count", drain_undo(b) == 1)
    check("contig coalesce empty", (b.text, b.cursor) == ("", 0))

    b = Buffer(); b.insert("ab"); b.move(0); b.insert("cd")
    check("move seals depth", drain_undo(b) == 2)
    b = Buffer(); b.insert("ab"); b.move(0); b.insert("cd")
    b.undo(); check("move seals state1", (b.text, b.cursor) == ("ab", 0))
    b.undo(); check("move seals state2", (b.text, b.cursor) == ("", 0))
    check("move seals exhausted", b.undo() is False)

    b = Buffer(); b.insert("ab"); b.move(2); b.insert("cd")
    check("move same pos no seal", drain_undo(b) == 1)

    # --- insert character limit (10) ---
    b = Buffer(); b.insert("aaaaaa"); b.insert("bbbb")
    check("limit exactly 10 coalesces", drain_undo(b) == 1)
    b = Buffer(); b.insert("aaaaaa"); b.insert("bbbbb")
    check("limit 11 splits", drain_undo(b) == 2)
    b = Buffer(); b.insert("aaaaaa"); b.insert("bbbbb"); b.insert("ccccc")
    check("new group becomes open", drain_undo(b) == 2)
    b = Buffer(); b.insert("aaaaaa"); b.insert("bbbbb"); b.insert("ccccc")
    b.undo(); check("limit undo1", (b.text, b.cursor) == ("aaaaaa", 6))
    b.undo(); check("limit undo2", (b.text, b.cursor) == ("", 0))

    # --- kind never mixes ---
    b = Buffer(); b.insert("ab"); b.backspace(1); b.insert("x")
    check("kind mix depth", drain_undo(b) == 3)
    b = Buffer(); b.insert("ab"); b.backspace(1); b.insert("x")
    b.undo(); check("kind mix s1", (b.text, b.cursor) == ("a", 1))
    b.undo(); check("kind mix s2", (b.text, b.cursor) == ("ab", 2))
    b.undo(); check("kind mix s3", (b.text, b.cursor) == ("", 0))

    # --- delete/backspace coalesce together ---
    b = Buffer(); b.insert("hello"); b.move(2); b.delete(2); b.backspace(2)
    check("del mix text", (b.text, b.cursor) == ("o", 0))
    check("del mix depth", drain_undo(b) == 2)
    b = Buffer(); b.insert("hello"); b.move(2); b.delete(2); b.backspace(2)
    b.undo(); check("del mix undo", (b.text, b.cursor) == ("hello", 2))

    # --- delete limit boundary ---
    b = Buffer(); b.insert("abcdefghij"); b.move(4); b.backspace(4); b.delete(4); b.delete(4)
    check("del limit text", (b.text, b.cursor) == ("", 0))
    check("del limit depth", drain_undo(b) == 2)
    b = Buffer(); b.insert("abcdefghij"); b.move(4); b.backspace(4); b.delete(4); b.delete(4)
    b.undo(); check("del limit undo", (b.text, b.cursor) == ("abcdefghij", 4))

    # --- delete limit exceeded ---
    b = Buffer(); b.insert("0123456789abc"); b.move(0); b.delete(6); b.delete(6)
    check("del exceeded text", (b.text, b.cursor) == ("c", 0))
    check("del exceeded depth", drain_undo(b) == 3)
    b = Buffer(); b.insert("0123456789abc"); b.move(0); b.delete(6); b.delete(6)
    b.undo(); check("del exceeded u1", (b.text, b.cursor) == ("6789abc", 0))
    b.undo(); check("del exceeded u2", (b.text, b.cursor) == ("0123456789abc", 0))

    # --- no-ops: nothing recorded, nothing sealed, redo intact ---
    b = Buffer(); b.insert("ab"); b.insert(""); b.insert("cd")
    check("insert empty no seal", drain_undo(b) == 1)
    b = Buffer(); b.insert("abc"); b.undo(); b.insert("")
    check("insert empty keeps redo", b.redo() is True and b.text == "abc")
    b = Buffer(); b.insert("abc"); b.undo(); b.delete(0)
    check("delete0 keeps redo", b.redo() is True and b.text == "abc")
    b = Buffer(); b.insert("abc"); b.undo(); b.backspace(5)
    check("clamped backspace keeps redo", b.redo() is True and (b.text, b.cursor) == ("abc", 3))
    b = Buffer(); b.insert("abc"); b.undo(); b.delete(10)
    check("clamped delete keeps redo", b.redo() is True and b.text == "abc")
    b = Buffer(); b.delete(0); b.backspace(3)
    check("no-ops on empty buffer", (b.text, b.cursor) == ("", 0))
    b = Buffer(); b.insert("abcd"); b.move(1); b.delete(1); b.delete(0); b.delete(1)
    check("delete0 no seal depth", drain_undo(b) == 2)
    b = Buffer(); b.insert("abcd"); b.move(1); b.delete(1); b.delete(0); b.delete(1)
    b.undo(); check("delete0 no seal state", (b.text, b.cursor) == ("abcd", 1))

    # --- move never clears redo ---
    b = Buffer(); b.insert("abc"); b.backspace(1); b.undo()
    check("pre move-undo state", (b.text, b.cursor) == ("abc", 3))
    b.move(1)
    check("move keeps redo", b.redo() is True and (b.text, b.cursor) == ("ab", 2))

    # --- redo does not reopen the group ---
    b = Buffer(); b.insert("ab"); b.undo(); b.redo(); b.insert("cd")
    check("redo no reopen depth", drain_undo(b) == 2)

    # --- exact cursor restore, return values, exhaustion ---
    b = Buffer(); b.insert("hello"); b.move(2); b.backspace(1)
    check("cursor restore text", (b.text, b.cursor) == ("hllo", 1))
    check("undo ret1", b.undo() is True and (b.text, b.cursor) == ("hello", 2))
    check("undo ret2", b.undo() is True and (b.text, b.cursor) == ("", 0))
    check("undo exhausted", b.undo() is False)
    check("redo ret1", b.redo() is True and (b.text, b.cursor) == ("hello", 5))
    check("redo ret2", b.redo() is True and (b.text, b.cursor) == ("hllo", 1))
    check("redo exhausted", b.redo() is False)

    # --- new edit clears redo ---
    b = Buffer(); b.insert("ab"); b.undo(); b.insert("x")
    check("edit clears redo", b.redo() is False and (b.text, b.cursor) == ("x", 1))

    # --- LIFO ordering with exact cursors ---
    b = Buffer(); b.insert("a"); b.move(0); b.insert("b")
    check("lifo text", (b.text, b.cursor) == ("ba", 1))
    b.undo(); check("lifo u1", (b.text, b.cursor) == ("a", 0))
    b.undo(); check("lifo u2", (b.text, b.cursor) == ("", 0))
    b.redo(); check("lifo r1", (b.text, b.cursor) == ("a", 1))
    b.redo(); check("lifo r2", (b.text, b.cursor) == ("ba", 1))

    # --- errors ---
    b = Buffer()
    for nm, fn, args in [("move -1", b.move, (-1,)), ("move beyond empty", b.move, (1,)),
                         ("delete neg", b.delete, (-1,)), ("backspace neg", b.backspace, (-1,))]:
        try:
            fn(*args); check(f"error {nm}", False)
        except BufferError:
            pass
        except Exception:
            check(f"error {nm} wrong type", False)
    b = Buffer(); b.insert("ab")
    try: b.move(3); check("move len+1 raises", False)
    except BufferError: pass
    check("move to len ok", b.move(2) is None and b.cursor == 2)
    b2 = Buffer(); b2.insert("ab")
    try: b2.move(99)
    except BufferError: pass
    b2.insert("cd")
    check("error keeps open group", drain_undo(b2) == 1)
    b3 = Buffer(); b3.insert("ab"); b3.undo()
    try: b3.move(1)
    except BufferError: pass
    check("error keeps redo", b3.redo() is True and b3.text == "ab")
    b4 = Buffer()
    try: b4.backspace(-2); check("neg on empty raises", False)
    except BufferError: pass

    # --- full worked transcript from prompt.md, every prefix ---
    steps = [
        ("insert", "hello", "hello", 5, 1, 0, None),
        ("insert", " w", "hello w", 7, 1, 0, None),
        ("insert", "orld", "hello world", 11, 2, 0, None),
        ("move", 5, "hello world", 5, 2, 0, None),
        ("insert", ",", "hello, world", 6, 3, 0, None),
        ("backspace", 1, "hello world", 5, 4, 0, None),
        ("undo", None, "hello, world", 6, 3, 1, True),
        ("redo", None, "hello world", 5, 4, 0, True),
        ("backspace", 5, " world", 0, 5, 0, None),
        ("delete", 3, "rld", 0, 5, 0, None),
        ("backspace", 2, "rld", 0, 5, 0, None),
        ("delete", 10, "", 0, 6, 0, None),
        ("undo", None, "rld", 0, 5, 1, True),
        ("undo", None, "hello world", 5, 4, 2, True),
        ("undo", None, "hello, world", 6, 3, 3, True),
        ("undo", None, "hello world", 5, 2, 4, True),
        ("undo", None, "hello w", 7, 1, 5, True),
        ("undo", None, "", 0, 0, 6, True),
        ("undo", None, "", 0, 0, 6, False),
        ("redo", None, "hello w", 7, 1, 5, True),
        ("insert", "!", "hello w!", 8, 2, 0, None),
        ("undo", None, "hello w", 7, 1, 1, True),
    ]
    for i in range(1, len(steps) + 1):
        b = Buffer(); ok = True
        for (meth, arg, etext, ecur, eu, er, eret) in steps[:i]:
            if meth in ("undo", "redo"):
                if getattr(b, meth)() is not eret: ok = False
            else:
                getattr(b, meth)(arg)
        check(f"transcript returns prefix {i}", ok)
        check(f"transcript state prefix {i}", (b.text, b.cursor) == (etext, ecur))
        c1 = drain_undo(b); c2 = drain_redo(b)
        check(f"transcript depth prefix {i}", c1 == eu and c2 == eu + er)

    # --- seeded randomised differential test against the snapshot model ---
    def gen_op(m):
        r = random.random()
        if r < 0.28:
            s = "".join(random.choice("ab c") for _ in range(random.randint(0, 4)))
            return ("insert", s)
        if r < 0.40:
            return ("delete", random.choice([0, 1, 1, 2, 3, 5, 12, -1]))
        if r < 0.52:
            return ("backspace", random.choice([0, 1, 1, 2, 3, 5, 12, -1]))
        if r < 0.64:
            if random.random() < 0.2:
                return ("move", m.cursor)
            return ("move", random.randint(-1, len(m.text) + 1))
        if r < 0.76: return ("undo",)
        if r < 0.86: return ("redo",)
        if r < 0.93: return ("drain_undo",)
        return ("drain_redo",)

    random.seed(2525)
    for trial in range(150):
        m = Model(); b = Buffer()
        for step in range(45):
            op = gen_op(m)
            want_err = False
            try:
                want = run_op(m, op)
            except BufferError:
                want_err = True; want = None
            got_err = None; got = None
            try:
                got = run_op(b, op)
            except BufferError:
                got_err = "BufferError"
            except Exception:
                got_err = "other"
            tag = f"rand t{trial} s{step} {op}"
            if want_err:
                check(f"{tag} expected BufferError", got_err == "BufferError")
            elif got_err is not None:
                check(f"{tag} unexpected raise ({got_err})", False)
            else:
                if op[0].startswith("drain"):
                    check(f"{tag} drain count", got == want)
                elif isinstance(want, bool):
                    check(f"{tag} return", got is want)
            check(f"{tag} text", b.text == m.text)
            check(f"{tag} cursor", b.cursor == m.cursor)
            check(f"{tag} invariant", 0 <= b.cursor <= len(b.text))
        ub = drain_undo(b); um = drain_undo(m)
        check(f"rand t{trial} final undo depth", ub == um)
        rb = drain_redo(b); rm = drain_redo(m)
        check(f"rand t{trial} final redo depth", rb == rm)
        check(f"rand t{trial} drained state", (b.text, b.cursor) == (m.text, m.cursor))

except Exception as e:
    fails.append(f"exception: {e!r}")

if fails:
    print("FAIL", fails[:12]); sys.exit(1)
print("PASS")
