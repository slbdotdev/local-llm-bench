"""Hidden grader for 48_editor: randomised differential test against an
inlined naive snapshot oracle, with partial credit."""
import sys, os, re, random, threading, inspect

TOTAL = 22
fails = []
done = 0
_lock = threading.Lock()


def check(name, fn):
    global done
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)
    with _lock:
        done += 1


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


def _watchdog():
    n = max(0, min(TOTAL, done - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    print("FAIL ['grader timed out (candidate too slow or hung)']")
    sys.stdout.flush()
    os._exit(1)


_t = threading.Timer(45.0, _watchdog)
_t.daemon = True
_t.start()


# ======================================================================
# Inlined oracle (names prefixed _orc / _Orc so they cannot collide).
# ======================================================================
_ORC_LIMIT = 12
_ORC_WORD = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")


class _OrcError(Exception):
    pass


class _OrcEditor(object):
    def __init__(self):
        self.text = ""
        self.cursor = 0
        self.anchor = 0
        self.clipboard = ""
        self.us = []        # undo stack of dicts
        self.rs = []        # redo stack
        self.open = None
        self.goal = None

    # queries
    def selection(self):
        return (min(self.anchor, self.cursor), max(self.anchor, self.cursor))

    def selected_text(self):
        lo, hi = self.selection()
        return self.text[lo:hi]

    def undo_depth(self):
        return len(self.us)

    def redo_depth(self):
        return len(self.rs)

    # helpers
    def _snap(self):
        return (self.text, self.cursor, self.anchor)

    def _push(self, kind, before, chars):
        g = {"kind": kind, "before": before, "after": self._snap(), "chars": chars}
        self.us.append(g)
        self.open = g if kind == "insert" else None
        self.rs = []

    def _motion(self, p, extend):
        old = (self.cursor, self.anchor)
        self.cursor = p
        if not extend:
            self.anchor = p
        if (self.cursor, self.anchor) != old:
            self.open = None

    def _dircheck(self, d):
        if d != -1 and d != 1:
            raise _OrcError("bad direction")

    # motion
    def move_char(self, d, extend=False):
        self._dircheck(d)
        self.goal = None
        lo, hi = self.selection()
        if not extend and lo != hi:
            p = lo if d == -1 else hi
        else:
            p = min(max(self.cursor + d, 0), len(self.text))
        self._motion(p, extend)

    def move_word(self, d, extend=False):
        self._dircheck(d)
        self.goal = None
        t, p, n = self.text, self.cursor, len(self.text)
        if d == 1:
            while p < n and t[p] not in _ORC_WORD:
                p += 1
            while p < n and t[p] in _ORC_WORD:
                p += 1
        else:
            while p > 0 and t[p - 1] not in _ORC_WORD:
                p -= 1
            while p > 0 and t[p - 1] in _ORC_WORD:
                p -= 1
        self._motion(p, extend)

    def move_line(self, d, extend=False):
        self._dircheck(d)
        lines = self.text.split("\n")
        starts = []
        acc = 0
        for L in lines:
            starts.append(acc)
            acc += len(L) + 1
        cur_line = self.text.count("\n", 0, self.cursor)
        if self.goal is None:
            self.goal = self.cursor - starts[cur_line]
        t = cur_line + d
        if t < 0:
            p = 0
        elif t >= len(lines):
            p = len(self.text)
        else:
            p = starts[t] + min(self.goal, len(lines[t]))
        self._motion(p, extend)

    def move_doc(self, d, extend=False):
        self._dircheck(d)
        self.goal = None
        self._motion(0 if d == -1 else len(self.text), extend)

    def set_selection(self, a, c):
        n = len(self.text)
        if a < 0 or a > n or c < 0 or c > n:
            raise _OrcError("out of range")
        self.goal = None
        old = (self.cursor, self.anchor)
        self.anchor, self.cursor = a, c
        if (self.cursor, self.anchor) != old:
            self.open = None

    # edits
    def insert(self, s):
        self.goal = None
        if s == "":
            return
        before = self._snap()
        lo, hi = self.selection()
        kind = "insert" if lo == hi else "replace"
        self.text = self.text[:lo] + s + self.text[hi:]
        self.cursor = self.anchor = lo + len(s)
        g = self.open
        if (kind == "insert" and g is not None and "\n" not in s
                and g["after"][1] == before[1]
                and g["chars"] + len(s) <= _ORC_LIMIT):
            g["after"] = self._snap()
            g["chars"] += len(s)
            self.rs = []
            return
        self._push(kind, before, len(s))
        if "\n" in s:
            self.open = None

    def _del(self, n, fwd):
        if n < 0:
            raise _OrcError("negative")
        self.goal = None
        lo, hi = self.selection()
        if lo != hi:
            before = self._snap()
            self.text = self.text[:lo] + self.text[hi:]
            self.cursor = self.anchor = lo
            self._push("delsel", before, hi - lo)
            return
        c = self.cursor
        k = min(n, len(self.text) - c) if fwd else min(n, c)
        if k == 0:
            return
        before = self._snap()
        if fwd:
            self.text = self.text[:c] + self.text[c + k:]
        else:
            self.text = self.text[:c - k] + self.text[c:]
            self.cursor = c - k
        self.anchor = self.cursor
        self._push("delfwd" if fwd else "delback", before, k)

    def delete_forward(self, n):
        self._del(n, True)

    def delete_back(self, n):
        self._del(n, False)

    def copy(self):
        self.goal = None
        lo, hi = self.selection()
        if lo != hi:
            self.clipboard = self.text[lo:hi]

    def cut(self):
        self.goal = None
        lo, hi = self.selection()
        if lo == hi:
            return
        self.clipboard = self.text[lo:hi]
        before = self._snap()
        self.text = self.text[:lo] + self.text[hi:]
        self.cursor = self.anchor = lo
        self._push("cut", before, hi - lo)

    def paste(self):
        self.goal = None
        s = self.clipboard
        if s == "":
            return
        before = self._snap()
        lo, hi = self.selection()
        self.text = self.text[:lo] + s + self.text[hi:]
        self.cursor = self.anchor = lo + len(s)
        self._push("paste", before, len(s))

    def undo(self):
        self.goal = None
        if not self.us:
            return False
        g = self.us.pop()
        self.text, self.cursor, self.anchor = g["before"]
        self.rs.append(g)
        self.open = None
        return True

    def redo(self):
        self.goal = None
        if not self.rs:
            return False
        g = self.rs.pop()
        self.text, self.cursor, self.anchor = g["after"]
        self.us.append(g)
        self.open = None
        return True


# ======================================================================
# Candidate import
# ======================================================================
_MOD = None
_ED = None
_ERR = None
try:
    import editor as _MOD
    _ED = _MOD.Editor
    _ERR = _MOD.EditorError
except Exception as _e:
    fails = ["import failed: %r" % (_e,)] + ["not run"] * (TOTAL - 1)
    report()


def _orc_run(obj, op):
    k = op[0]
    if k == "insert":
        return obj.insert(op[1])
    if k == "delfwd":
        return obj.delete_forward(op[1])
    if k == "delback":
        return obj.delete_back(op[1])
    if k == "mchar":
        return obj.move_char(op[1], op[2])
    if k == "mword":
        return obj.move_word(op[1], op[2])
    if k == "mline":
        return obj.move_line(op[1], op[2])
    if k == "mdoc":
        return obj.move_doc(op[1], op[2])
    if k == "sel":
        return obj.set_selection(op[1], op[2])
    if k == "copy":
        return obj.copy()
    if k == "cut":
        return obj.cut()
    if k == "paste":
        return obj.paste()
    if k == "undo":
        return obj.undo()
    if k == "redo":
        return obj.redo()
    if k == "drainu":
        n = 0
        while obj.undo() is True:
            n += 1
            if n > 500:
                break
        return n
    if k == "drainr":
        n = 0
        while obj.redo() is True:
            n += 1
            if n > 500:
                break
        return n
    raise AssertionError("bad op")


def _orc_view(obj):
    return (obj.text, obj.cursor, obj.anchor, obj.clipboard,
            tuple(obj.selection()), obj.selected_text(),
            obj.undo_depth(), obj.redo_depth())


_ORC_ALPHA = "ab c,de_f9"


def _orc_gen(rng, fam, m):
    """Generate one op for family fam given oracle state m."""
    n = len(m.text)
    big = n > 70

    def rand_text(maxlen, nl):
        out = []
        for _ in range(rng.randint(1, maxlen)):
            if nl and rng.random() < 0.22:
                out.append("\n")
            else:
                out.append(rng.choice(_ORC_ALPHA))
        return "".join(out)

    def ins_op(nl=False):
        r = rng.random()
        if r < 0.10:
            return ("insert", "")
        if r < 0.22:
            return ("insert", rand_text(16, nl))
        return ("insert", rand_text(5, nl))

    def del_op():
        n2 = rng.choice([0, 1, 1, 1, 2, 3, 7, 14, -1])
        return (rng.choice(["delfwd", "delback"]), n2)

    def mv(kind, pext=0.45):
        d = rng.choice([-1, 1, 1, -1, 0])
        return (kind, d, rng.random() < pext)

    def sel_op():
        if rng.random() < 0.12:
            return ("sel", rng.randint(-1, n + 1), rng.randint(-1, n + 1))
        if rng.random() < 0.15:
            return ("sel", m.anchor, m.cursor)
        a = rng.randint(0, n)
        b = rng.randint(0, n)
        return ("sel", a, b)

    r = rng.random()
    if fam == "A":
        # typing / coalescing: never creates a selection (no extend, no sel)
        if r < 0.48 and not big:
            return ins_op(rng.random() < 0.16)
        if r < 0.70:
            return del_op()
        if r < 0.86:
            return mv("mchar", 0.0)
        if r < 0.90:
            return mv("mdoc", 0.0)
        if r < 0.95:
            return ("undo",)
        return ("redo",)
    if fam == "B":
        # selection + horizontal motion: no undo/redo at all
        if r < 0.22:
            return sel_op()
        if r < 0.42:
            return mv("mchar")
        if r < 0.64:
            return mv("mword")
        if r < 0.72:
            return mv("mdoc")
        if r < 0.86 and not big:
            return ins_op()
        return del_op()
    if fam == "C":
        # vertical motion / goal column: no undo/redo, no set_selection
        if r < 0.44:
            return mv("mline")
        if r < 0.58:
            return mv("mchar")
        if r < 0.68:
            return mv("mword")
        if r < 0.82 and not big:
            return ins_op(True)
        if r < 0.94:
            return del_op()
        return mv("mdoc")
    if fam == "D":          # clipboard
        if r < 0.22:
            return sel_op()
        if r < 0.40:
            return ("copy",)
        if r < 0.54:
            return ("cut",)
        if r < 0.74:
            return ("paste",) if not big else del_op()
        if r < 0.84 and not big:
            return ins_op()
        if r < 0.92:
            return del_op()
        if r < 0.97:
            return mv("mchar")
        return ("undo",)
    if fam == "E":          # history churn
        if r < 0.24 and not big:
            return ins_op(rng.random() < 0.15)
        if r < 0.36:
            return del_op()
        if r < 0.46:
            return mv("mchar")
        if r < 0.54:
            return sel_op()
        if r < 0.72:
            return ("undo",)
        if r < 0.88:
            return ("redo",)
        if r < 0.94:
            return ("drainu",)
        return ("drainr",)
    # fam F: everything
    if r < 0.18 and not big:
        return ins_op(rng.random() < 0.25)
    if r < 0.30:
        return del_op()
    if r < 0.40:
        return sel_op()
    if r < 0.48:
        return mv("mchar")
    if r < 0.56:
        return mv("mword")
    if r < 0.64:
        return mv("mline")
    if r < 0.68:
        return mv("mdoc")
    if r < 0.74:
        return ("copy",)
    if r < 0.79:
        return ("cut",)
    if r < 0.86:
        return ("paste",) if not big else del_op()
    if r < 0.93:
        return ("undo",)
    if r < 0.98:
        return ("redo",)
    return ("drainu",)


def _orc_trial(seed, fam, steps):
    """Run one differential trial; return None if OK else a description."""
    rng = random.Random(seed)
    m = _OrcEditor()
    c = _ED()
    if fam == "C":
        seed_text = "alpha\nbb\n\nlong line here\nxy"
        m.insert(seed_text)
        c.insert(seed_text)
        m.move_doc(-1)
        c.move_doc(-1)
    for step in range(steps):
        op = _orc_gen(rng, fam, m)
        w_err = False
        want = None
        try:
            want = _orc_run(m, op)
        except _OrcError:
            w_err = True
        got = None
        g_err = None
        try:
            got = _orc_run(c, op)
        except Exception as e:
            g_err = e
        tag = "seed %d step %d op %r" % (seed, step, op)
        if w_err:
            if not isinstance(g_err, _ERR):
                return "%s: expected EditorError, got %r" % (tag, g_err)
        elif g_err is not None:
            return "%s: unexpected %r" % (tag, g_err)
        elif isinstance(want, bool):
            if got is not want:
                return "%s: return %r want %r" % (tag, got, want)
        elif isinstance(want, int):
            if got != want:
                return "%s: drain count %r want %r" % (tag, got, want)
        elif got is not None:
            return "%s: should return None, got %r" % (tag, got)
        gv = _orc_view(c)
        wv = _orc_view(m)
        if gv != wv:
            names = ("text", "cursor", "anchor", "clipboard", "selection",
                     "selected_text", "undo_depth", "redo_depth")
            diff = [names[i] for i in range(len(wv)) if gv[i] != wv[i]]
            return "%s: %s differ (got %r want %r)" % (tag, ",".join(diff), gv, wv)
    if fam in ("B", "C"):
        return None
    # drain both stacks at the end and compare
    for k in ("drainu", "drainr", "drainu"):
        if _orc_run(c, (k,)) != _orc_run(m, (k,)):
            return "seed %d: final %s count" % (seed, k)
        if _orc_view(c) != _orc_view(m):
            return "seed %d: state after final %s" % (seed, k)
    return None


def _orc_bucket(fam, base, trials, steps):
    def probe():
        for i in range(trials):
            bad = _orc_trial(base + i, fam, steps)
            if bad is not None:
                probe.why = bad
                return False
        return True
    return probe


# ======================================================================
# Checks
# ======================================================================
check("module exposes Editor and EditorError",
      lambda: isinstance(_ED, type) and isinstance(_ERR, type))


def _no_banned():
    src = inspect.getsource(_MOD)
    return re.search(r"^\s*(?:import|from)\s+(?:re|copy)\b", src, re.M) is None


check("editor.py imports neither re nor copy", _no_banned)


def _errors():
    if not issubclass(_ERR, ValueError):
        return False
    e = _ED()
    e.insert("abcdef")
    e.set_selection(2, 4)
    snap = _orc_view(e)
    bad = [(e.set_selection, (0, 7)), (e.set_selection, (-1, 2)),
           (e.delete_forward, (-1,)), (e.delete_back, (-3,)),
           (e.move_char, (0,)), (e.move_word, (2,)), (e.move_line, (0,)),
           (e.move_doc, (-2,))]
    for fn, args in bad:
        try:
            fn(*args)
        except _ERR:
            pass
        except Exception:
            return False
        else:
            return False
    return _orc_view(e) == snap


check("EditorError subclasses ValueError; bad arguments raise and change nothing",
      _errors)


def _prompt_examples():
    e = _ED()
    e.insert("hello")
    e.insert(" you")
    if e.undo_depth() != 1:
        return False
    e.set_selection(6, 9)
    e.insert("me")
    if (e.text, e.cursor, e.anchor) != ("hello me", 8, 8):
        return False
    if e.undo_depth() != 2:
        return False
    if e.undo() is not True or (e.text, e.cursor, e.anchor) != ("hello you", 9, 6):
        return False

    e = _ED()
    e.insert("one two three")
    e.move_doc(-1)
    e.move_word(+1)
    if e.cursor != 3:
        return False
    e.move_word(+1, extend=True)
    if e.selection() != (3, 7) or e.selected_text() != " two":
        return False
    e.cut()
    if (e.text, e.clipboard, e.cursor, e.anchor) != ("one three", " two", 3, 3):
        return False

    e = _ED()
    e.insert("abcdef")
    e.move_char(-1)
    e.delete_back(2)
    if (e.text, e.cursor) != ("abcf", 3):
        return False
    e.undo()
    if (e.text, e.cursor, e.anchor) != ("abcdef", 5, 5) or e.redo_depth() != 1:
        return False

    e = _ED()
    e.insert("ab")
    e.undo()
    e.insert("z")
    return e.redo_depth() == 0 and e.text == "z"


check("worked examples from the prompt", _prompt_examples)

_FAMS = [("A", "typing and coalescing", 4800),
         ("B", "selection and word motion", 5300),
         ("C", "vertical motion and goal column", 5900),
         ("D", "clipboard cut/copy/paste", 6400),
         ("E", "undo/redo churn", 7100),
         ("F", "everything mixed", 7700)]

for _fam, _desc, _base in _FAMS:
    for _b in range(3):
        _probe = _orc_bucket(_fam, _base + _b * 100, 32, 60)
        check("differential %s (%s) bucket %d" % (_fam, _desc, _b + 1), _probe)

_t.cancel()
report()
