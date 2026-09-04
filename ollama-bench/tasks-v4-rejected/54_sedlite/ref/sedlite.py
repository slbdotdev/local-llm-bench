"""sedlite -- a small sed-like line editing language."""
import re

DELIMS = "/,:#_@%!"
LETTERS = "sydpqai"


class ScriptError(ValueError):
    def __init__(self, kind):
        ValueError.__init__(self, kind)
        self.kind = kind


class _Cmd(object):
    __slots__ = ("a1", "a2", "neg", "letter", "arg", "active", "start")

    def __init__(self):
        self.a1 = None
        self.a2 = None
        self.neg = False
        self.letter = None
        self.arg = None
        self.active = False
        self.start = 0


# ---------------------------------------------------------------- parsing

class _P(object):
    def __init__(self, s):
        self.s = s
        self.i = 0
        self.n = len(s)

    def eof(self):
        return self.i >= self.n

    def cur(self):
        return self.s[self.i] if self.i < self.n else ""

    def ws(self):
        while self.i < self.n and self.s[self.i] in " \t":
            self.i += 1

    def digits(self):
        j = self.i
        while self.i < self.n and self.s[self.i].isdigit():
            self.i += 1
        if j == self.i:
            return None
        return int(self.s[j:self.i])


def _err(kind):
    raise ScriptError(kind)


def _read_delimited(p, d):
    """Read raw text up to the next unescaped delimiter d; consume the d."""
    out = []
    while True:
        if p.eof() or p.s[p.i] == "\n":
            _err("unterminated")
        c = p.s[p.i]
        if c == "\\":
            if p.i + 1 >= p.n or p.s[p.i + 1] == "\n":
                _err("unterminated")
            out.append(c)
            out.append(p.s[p.i + 1])
            p.i += 2
            continue
        if c == d:
            p.i += 1
            return "".join(out)
        out.append(c)
        p.i += 1


def _unesc_regex(raw, d):
    """Only \\<delim> collapses; everything else is handed to `re` verbatim."""
    out = []
    i = 0
    while i < len(raw):
        if raw[i] == "\\" and i + 1 < len(raw):
            if raw[i + 1] == d:
                out.append(d)
            else:
                out.append(raw[i])
                out.append(raw[i + 1])
            i += 2
        else:
            out.append(raw[i])
            i += 1
    return "".join(out)


def _unesc_plain(raw, d):
    out = []
    i = 0
    while i < len(raw):
        c = raw[i]
        if c == "\\" and i + 1 < len(raw):
            n = raw[i + 1]
            out.append("\n" if n == "n" else "\t" if n == "t" else n)
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _compile_re(raw, d, ic):
    pat = _unesc_regex(raw, d)
    if pat == "":
        _err("bad_regex")
    try:
        return re.compile(pat, re.IGNORECASE if ic else 0)
    except re.error:
        _err("bad_regex")


def _parse_repl(raw, d, ngroups):
    """-> list of ('l', text) / ('g', k)"""
    parts = []
    lit = []
    i = 0
    while i < len(raw):
        c = raw[i]
        if c == "&":
            if lit:
                parts.append(("l", "".join(lit)))
                lit = []
            parts.append(("g", 0))
            i += 1
        elif c == "\\":
            if i + 1 >= len(raw):
                _err("bad_regex")
            n = raw[i + 1]
            if n in "123456789":
                k = int(n)
                if k > ngroups:
                    _err("bad_backref")
                if lit:
                    parts.append(("l", "".join(lit)))
                    lit = []
                parts.append(("g", k))
            elif n == "n":
                lit.append("\n")
            elif n == "t":
                lit.append("\t")
            else:
                lit.append(n)
            i += 2
        else:
            lit.append(c)
            i += 1
    if lit:
        parts.append(("l", "".join(lit)))
    return parts


def _parse_addr(p, allow_step, allow_plus):
    c = p.cur()
    if allow_plus and c == "+":
        p.i += 1
        v = p.digits()
        if v is None:
            _err("bad_address")
        return ("plus", v)
    if c == "$":
        p.i += 1
        return ("last",)
    if c == "/":
        p.i += 1
        raw = _read_delimited(p, "/")
        return ("re", _compile_re(raw, "/", False))
    if c.isdigit():
        v = p.digits()
        if allow_step and p.cur() == "~":
            p.i += 1
            st = p.digits()
            if st is None:
                _err("bad_address")
            return ("step", v, st)
        if v == 0:
            _err("bad_address")
        return ("num", v)
    return None


def _end_of_cmd(p):
    p.ws()
    if p.eof():
        return
    if p.s[p.i] in ";\n":
        p.i += 1
        return
    _err("trailing_garbage")


def _rest_of_line(p):
    j = p.s.find("\n", p.i)
    if j < 0:
        j = p.n
    t = p.s[p.i:j]
    p.i = j
    return t


def _parse(script):
    p = _P(script)
    cmds = []
    while True:
        while not p.eof() and p.s[p.i] in " \t\n;":
            p.i += 1
        if p.eof():
            break
        if p.s[p.i] == "#":
            _rest_of_line(p)
            continue
        c = _Cmd()
        c.a1 = _parse_addr(p, True, False)
        if c.a1 is not None:
            p.ws()
            if p.cur() == ",":
                p.i += 1
                p.ws()
                c.a2 = _parse_addr(p, False, True)
                if c.a2 is None:
                    _err("bad_address")
        p.ws()
        nbang = 0
        while p.cur() == "!":
            nbang += 1
            p.i += 1
            p.ws()
        if nbang > 1:
            _err("bad_bang")
        if nbang == 1:
            if c.a1 is None:
                _err("bad_bang")
            c.neg = True
        letter = p.cur()
        if letter == "" or letter not in LETTERS:
            _err("unknown_command")
        p.i += 1
        c.letter = letter
        if letter == "q" and c.a2 is not None:
            _err("extra_address")
        if letter in "dpq":
            _end_of_cmd(p)
        elif letter in "ai":
            t = _rest_of_line(p)
            t = t.lstrip(" \t")
            if t == "":
                _err("empty_text")
            c.arg = _unesc_plain(t, None)
        elif letter == "y":
            d = p.cur()
            if d == "" or d not in DELIMS:
                _err("bad_delimiter")
            p.i += 1
            src = _unesc_plain(_read_delimited(p, d), d)
            dst = _unesc_plain(_read_delimited(p, d), d)
            if len(src) != len(dst):
                _err("bad_y")
            m = {}
            for a, b in zip(src, dst):
                m[a] = b
            c.arg = m
            _end_of_cmd(p)
        else:  # s
            d = p.cur()
            if d == "" or d not in DELIMS:
                _err("bad_delimiter")
            p.i += 1
            praw = _read_delimited(p, d)
            rraw = _read_delimited(p, d)
            j = p.i
            while j < p.n and p.s[j].isalnum():
                j += 1
            fl = p.s[p.i:j]
            p.i = j
            g = ic = pr = False
            num = None
            k = 0
            while k < len(fl):
                ch = fl[k]
                if ch.isdigit():
                    if num is not None:
                        _err("bad_flag")
                    v = 0
                    while k < len(fl) and fl[k].isdigit():
                        v = v * 10 + int(fl[k])
                        k += 1
                    if v == 0:
                        _err("bad_flag")
                    num = v
                    continue
                if ch == "g":
                    if g:
                        _err("bad_flag")
                    g = True
                elif ch == "i":
                    if ic:
                        _err("bad_flag")
                    ic = True
                elif ch == "p":
                    if pr:
                        _err("bad_flag")
                    pr = True
                else:
                    _err("bad_flag")
                k += 1
            rx = _compile_re(praw, d, ic)
            c.arg = (rx, _parse_repl(rraw, d, rx.groups), g, pr, 1 if num is None else num)
            _end_of_cmd(p)
        cmds.append(c)
    return cmds


# -------------------------------------------------------------- execution

def _m1(a, L, ps, last):
    t = a[0]
    if t == "num":
        return L == a[1]
    if t == "last":
        return last
    if t == "re":
        return a[1].search(ps) is not None
    if t == "step":
        if a[2] == 0:
            return L == a[1]
        return L >= a[1] and (L - a[1]) % a[2] == 0
    return False


def _closes(a, L, ps, last, start):
    t = a[0]
    if t == "num":
        return L >= a[1]
    if t == "last":
        return last
    if t == "re":
        return a[1].search(ps) is not None
    if t == "plus":
        return L >= start + a[1]
    return True


def _applies(c, L, ps, last):
    if c.a1 is None:
        m = True
    elif c.a2 is None:
        m = _m1(c.a1, L, ps, last)
    else:
        if c.active:
            m = True
            if _closes(c.a2, L, ps, last, c.start):
                c.active = False
        elif _m1(c.a1, L, ps, last):
            m = True
            c.start = L
            a2 = c.a2
            one = (a2[0] == "num" and a2[1] <= L) or (a2[0] == "plus" and a2[1] == 0)
            c.active = not one
        else:
            m = False
    return (not m) if c.neg else m


def _expand(parts, m):
    out = []
    for k, v in parts:
        if k == "l":
            out.append(v)
        else:
            g = m.group(v)
            out.append(g if g is not None else "")
    return "".join(out)


def _subst(arg, ps):
    rx, parts, g, pr, num = arg
    ms = list(rx.finditer(ps))
    if g:
        sel = ms[num - 1:]
    else:
        sel = [ms[num - 1]] if len(ms) >= num else []
    if not sel:
        return ps, False
    out = []
    last = 0
    for m in sel:
        out.append(ps[last:m.start()])
        out.append(_expand(parts, m))
        last = m.end()
    out.append(ps[last:])
    return "".join(out), True


def run(script, text, quiet=False):
    cmds = _parse(script)
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    out = []
    n = len(lines)
    for idx in range(1, n + 1):
        ps = lines[idx - 1]
        app = []
        deleted = False
        quitting = False
        for c in cmds:
            if not _applies(c, idx, ps, idx == n):
                continue
            L = c.letter
            if L == "p":
                out.append(ps)
            elif L == "d":
                deleted = True
                break
            elif L == "s":
                ps, ch = _subst(c.arg, ps)
                if ch and c.arg[3]:
                    out.append(ps)
            elif L == "y":
                ps = "".join(c.arg.get(ch, ch) for ch in ps)
            elif L == "a":
                app.append(c.arg)
            elif L == "i":
                out.append(c.arg)
            else:  # q
                quitting = True
                break
        if not deleted and not quiet:
            out.append(ps)
        out.extend(app)
        if quitting:
            break
    return "".join(x + "\n" for x in out)
