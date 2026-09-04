"""Hidden grader for 56_tmpl: a small text template engine.

The oracle below (`_ora_*`) is an independent implementation that uses a different
strategy from the reference solution: it lexes to a FLAT item list, validates it with an
explicit block stack that records jump targets, and renders with a program counter and a
control stack (no AST tree-walk).
"""
import sys, os, random, threading, inspect

TOTAL = 29
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

try:
    import tmpl
except Exception as e:
    fails = ["import failed: %r" % (e,)] + ["not run"] * (TOTAL - 1)
    report()


class _MissingErr(Exception):
    pass


TE = getattr(tmpl, "TemplateError", None)
if not (isinstance(TE, type) and issubclass(TE, BaseException)):
    TE = _MissingErr


# =====================================================================
# oracle
# =====================================================================
_OWS = " \t\r\n\x0b\x0c"
_ODIG = "0123456789"
_OIDC = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789")
_OID0 = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
_OKW = ("true", "false", "none", "not", "and", "or", "in")
_OFIL = {"upper": 0, "lower": 0, "trim": 0, "length": 0, "first": 0, "safe": 0,
         "escape": 0, "default": 1, "join": 1, "replace": 2, "slice": 2}
_OENDS = ("elif", "else", "endif", "empty", "endfor")


class _OraErr(Exception):
    def __init__(self, kind, pos):
        Exception.__init__(self, "%s@%s" % (kind, pos))
        self.kind = kind
        self.pos = pos


class _OraUndef(object):
    __slots__ = ()


_OU = _OraUndef()


def _ora_type(v):
    if v is _OU:
        return None
    if v is None:
        return "none"
    if v is True or v is False:
        return "bool"
    if isinstance(v, int):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "list"
    return "map"


def _ora_truth(v):
    t = _ora_type(v)
    if t is None or t == "none":
        return False
    if t == "bool":
        return v is True
    if t == "number":
        return v != 0
    if t == "string":
        return v not in ("", "0", "false")
    return len(v) != 0


def _ora_text(v):
    t = _ora_type(v)
    if t is None or t == "none":
        return ""
    if t == "bool":
        return "true" if v else "false"
    if t == "number":
        return "%d" % v
    if t == "string":
        return v
    if t == "list":
        return "[" + ", ".join([_ora_text(x) for x in v]) + "]"
    return "{" + ", ".join([_ora_text(k) + ": " + _ora_text(v[k]) for k in v]) + "}"


def _ora_esc(s):
    r = []
    for c in s:
        if c == "&":
            r.append("&amp;")
        elif c == "<":
            r.append("&lt;")
        elif c == ">":
            r.append("&gt;")
        elif c == chr(34):
            r.append("&#34;")
        elif c == chr(39):
            r.append("&#39;")
        else:
            r.append(c)
    return "".join(r)


def _ora_eq(a, b):
    ta, tb = _ora_type(a), _ora_type(b)
    if ta != tb:
        return False
    if ta is None or ta == "none":
        return True
    if ta == "list":
        if len(a) != len(b):
            return False
        i = 0
        while i < len(a):
            if not _ora_eq(a[i], b[i]):
                return False
            i += 1
        return True
    if ta == "map":
        if len(a) != len(b):
            return False
        for k in a:
            if k not in b:
                return False
            if not _ora_eq(a[k], b[k]):
                return False
        return True
    return a == b


def _ora_lookup(base, key):
    tb = _ora_type(base)
    if tb is None or tb == "none":
        return _OU
    if tb == "map":
        try:
            if key in base:
                return base[key]
        except TypeError:
            pass
    elif tb in ("list", "string"):
        i = None
        if key is True or key is False:
            i = None
        elif isinstance(key, int):
            i = key
        elif isinstance(key, str) and len(key) > 0:
            ok = True
            for c in key:
                if c not in _ODIG:
                    ok = False
            if ok:
                i = int(key)
        if i is not None:
            if 0 <= i < len(base):
                return base[i]
            return _OU
    if key == "size":
        return len(base) if tb in ("list", "string", "map") else _OU
    if key == "keys":
        return [k for k in base] if tb == "map" else _OU
    if key == "type":
        return tb if tb is not None else _OU
    return _OU


# --- expression tokenizer / parser -----------------------------------
def _ora_rdstr(s, i, pos):
    q = s[i]
    j = i + 1
    out = []
    while True:
        if j >= len(s):
            raise _OraErr("syntax", pos)
        c = s[j]
        if c == "\\":
            if j + 1 >= len(s):
                raise _OraErr("syntax", pos)
            d = s[j + 1]
            out.append("\n" if d == "n" else ("\t" if d == "t" else d))
            j += 2
        elif c == q:
            return "".join(out), j + 1
        else:
            out.append(c)
            j += 1


def _ora_split_head(text, pos):
    """Return (head_text, index_after_first_toplevel_bar_or_None)."""
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == chr(34) or c == chr(39):
            _v, i = _ora_rdstr(text, i, pos)
            continue
        if c == "|":
            return text[:i], i + 1
        i += 1
    return text, None


def _ora_tokens(text, pos):
    toks = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in _OWS:
            i += 1
        elif c in _OID0:
            j = i
            while j < n and text[j] in _OIDC:
                j += 1
            toks.append(("name", text[i:j]))
            i = j
        elif c in _ODIG:
            j = i
            while j < n and text[j] in _ODIG:
                j += 1
            toks.append(("int", text[i:j]))
            i = j
        elif c == chr(34) or c == chr(39):
            v, j = _ora_rdstr(text, i, pos)
            toks.append(("str", v))
            i = j
        elif text[i:i + 2] in ("==", "!=", "<=", ">="):
            toks.append(("op", text[i:i + 2]))
            i += 2
        elif c in "<>.[],:":
            toks.append(("op", c))
            i += 1
        else:
            raise _OraErr("syntax", pos)
    toks.append(("eof", ""))
    return toks


_OCMP = ("==", "!=", "<", "<=", ">", ">=")


class _OraPz(object):
    def __init__(self, toks, pos):
        self.t = toks
        self.k = 0
        self.pos = pos

    def cur(self):
        return self.t[self.k]

    def bad(self):
        raise _OraErr("syntax", self.pos)

    def cmpop(self):
        k, v = self.t[self.k]
        if k == "op" and v in _OCMP:
            return v
        if k == "name" and v == "in":
            return "in"
        return None

    def disj(self):
        ps = [self.conj()]
        while self.cur() == ("name", "or"):
            self.k += 1
            ps.append(self.conj())
        return ps[0] if len(ps) == 1 else ("or", ps)

    def conj(self):
        ps = [self.neg()]
        while self.cur() == ("name", "and"):
            self.k += 1
            ps.append(self.neg())
        return ps[0] if len(ps) == 1 else ("and", ps)

    def neg(self):
        if self.cur() == ("name", "not"):
            self.k += 1
            return ("not", self.neg())
        a = self.prim()
        op = self.cmpop()
        if op is None:
            return a
        self.k += 1
        b = self.prim()
        if self.cmpop() is not None:
            self.bad()
        return ("cmp", op, a, b)

    def prim(self):
        k, v = self.cur()
        if k == "int":
            node = ("lit", int(v))
        elif k == "str":
            node = ("lit", v)
        elif k == "name":
            if v == "true":
                node = ("lit", True)
            elif v == "false":
                node = ("lit", False)
            elif v == "none":
                node = ("lit", None)
            elif v in _OKW:
                self.bad()
            else:
                node = ("var", v)
        else:
            self.bad()
        self.k += 1
        while True:
            k, v = self.cur()
            if k == "op" and v == ".":
                self.k += 1
                k2, v2 = self.cur()
                if k2 not in ("name", "int"):
                    self.bad()
                self.k += 1
                node = ("get", node, ("lit", v2))
            elif k == "op" and v == "[":
                self.k += 1
                sub = self.prim()
                if self.cur() != ("op", "]"):
                    self.bad()
                self.k += 1
                node = ("get", node, sub)
            else:
                return node


def _ora_skip(s, i):
    while i < len(s) and s[i] in _OWS:
        i += 1
    return i


def _ora_argval(raw):
    if len(raw) > 0:
        alld = True
        for c in raw:
            if c not in _ODIG:
                alld = False
        if alld:
            return int(raw)
    if raw == "true":
        return True
    if raw == "false":
        return False
    if raw == "none":
        return None
    return raw


def _ora_filters(text, i, pos):
    """Parse the filter chain; `i` is the index just after the first '|'."""
    out = []
    while True:
        i = _ora_skip(text, i)
        j = i
        while j < len(text) and text[j] in _OIDC:
            j += 1
        name = text[i:j]
        if name == "" or name[0] in _ODIG:
            raise _OraErr("syntax", pos)
        if name not in _OFIL:
            raise _OraErr("unknown_filter", pos)
        i = _ora_skip(text, j)
        args = []
        if i < len(text) and text[i] == ":":
            i += 1
            while True:
                i = _ora_skip(text, i)
                if i < len(text) and (text[i] == chr(34) or text[i] == chr(39)):
                    v, j2 = _ora_rdstr(text, i, pos)
                    i = _ora_skip(text, j2)
                    if i < len(text) and text[i] not in ",|":
                        raise _OraErr("syntax", pos)
                    args.append(v)
                else:
                    j2 = i
                    while j2 < len(text) and text[j2] not in ",|":
                        j2 += 1
                    args.append(_ora_argval(text[i:j2].strip(_OWS)))
                    i = j2
                if i < len(text) and text[i] == ",":
                    i += 1
                    continue
                break
        if len(args) != _OFIL[name]:
            raise _OraErr("filter_args", pos)
        out.append((name, args))
        i = _ora_skip(text, i)
        if i >= len(text):
            return out
        if text[i] != "|":
            raise _OraErr("syntax", pos)
        i += 1


def _ora_expr(text, pos, allow_filters):
    head, after = _ora_split_head(text, pos)
    if after is not None and not allow_filters:
        raise _OraErr("syntax", pos)
    if head.strip(_OWS) == "":
        raise _OraErr("syntax", pos)
    pz = _OraPz(_ora_tokens(head, pos), pos)
    node = pz.disj()
    if pz.cur()[0] != "eof":
        pz.bad()
    fl = _ora_filters(text, after, pos) if after is not None else []
    return (node, fl)


# --- lexer -----------------------------------------------------------
def _ora_lex(src):
    spans = []
    i = 0
    n = len(src)
    while i < n:
        if src[i] == "{" and i + 1 < n and src[i + 1] in "{%#":
            o = src[i + 1]
            cl = "}}" if o == "{" else ("%}" if o == "%" else "#}")
            j = i + 2
            lm = False
            if j < n and src[j] == "-":
                lm = True
                j += 1
            e = src.find(cl, j)
            if e < 0:
                raise _OraErr("unclosed_tag", i)
            body = src[j:e]
            rm = False
            if body[-1:] == "-":
                rm = True
                body = body[:-1]
            spans.append((i, e + 2, o, body, lm, rm))
            i = e + 2
        else:
            i += 1
    items = []
    cursor = 0
    for k in range(len(spans)):
        st, en, o, body, lm, rm = spans[k]
        txt = src[cursor:st]
        if lm:
            txt = txt.rstrip(_OWS)
        if k > 0 and spans[k - 1][5]:
            txt = txt.lstrip(_OWS)
        if txt:
            items.append(("text", txt, 0))
        if o == "{":
            items.append(("out", body, st))
        elif o == "%":
            items.append(("blk", body, st))
        cursor = en
    tail = src[cursor:]
    if spans and spans[-1][5]:
        tail = tail.lstrip(_OWS)
    if tail:
        items.append(("text", tail, 0))
    return items


# --- validation (explicit stack -> jump tables) -----------------------
def _ora_ident(rest, pos):
    i = _ora_skip(rest, 0)
    j = i
    while j < len(rest) and rest[j] in _OIDC:
        j += 1
    nm = rest[i:j]
    if nm == "" or nm[0] in _ODIG or nm in _OKW:
        raise _OraErr("syntax", pos)
    return nm, j


def _ora_parse(items):
    """Return (prog, links).  prog[i] is an executable record."""
    prog = []
    for it in items:
        if it[0] == "text":
            prog.append(["text", it[1]])
        elif it[0] == "out":
            body = it[1].strip(_OWS)
            if body == "":
                raise _OraErr("syntax", it[2])
            prog.append(["out", _ora_expr(body, it[2], True), it[2]])
        else:
            body = it[1].strip(_OWS)
            pos = it[2]
            if body == "":
                raise _OraErr("unknown_tag", pos)
            sp = 0
            while sp < len(body) and body[sp] not in _OWS:
                sp += 1
            name = body[:sp]
            rest = body[sp:].strip(_OWS)
            if name in ("if", "elif"):
                prog.append([name, None, pos, rest])
            elif name in ("else", "endif", "empty", "endfor"):
                prog.append([name, None, pos, rest])
            elif name == "for":
                prog.append(["for", None, pos, rest])
            elif name == "set":
                prog.append(["set", None, pos, rest])
            else:
                raise _OraErr("unknown_tag", pos)
    # structural pass with an explicit stack
    stack = []
    alt = {}
    chain_end = {}
    forinfo = {}
    backfor = {}
    for k in range(len(prog)):
        r = prog[k]
        op = r[0]
        if op == "if":
            if r[3] == "":
                raise _OraErr("syntax", r[2])
            r[1] = _ora_expr(r[3], r[2], False)
            stack.append(["if", k, [k], r[2]])
        elif op == "elif":
            if not stack or stack[-1][0] != "if" or stack[-1][2][-1] == -1:
                raise _OraErr("unexpected_tag", r[2])
            if r[3] == "":
                raise _OraErr("syntax", r[2])
            r[1] = _ora_expr(r[3], r[2], False)
            alt[stack[-1][2][-1]] = k
            stack[-1][2].append(k)
        elif op == "else":
            if not stack or stack[-1][0] != "if" or stack[-1][2][-1] == -1:
                raise _OraErr("unexpected_tag", r[2])
            if r[3] != "":
                raise _OraErr("syntax", r[2])
            alt[stack[-1][2][-1]] = k
            stack[-1][2].append(k)
            stack[-1][2].append(-1)
        elif op == "endif":
            if not stack or stack[-1][0] != "if":
                raise _OraErr("unexpected_tag", r[2])
            if r[3] != "":
                raise _OraErr("syntax", r[2])
            fr = stack.pop()
            for idx in fr[2]:
                if idx != -1:
                    chain_end[idx] = k
            if fr[2][-1] == -1:
                fr[2].pop()
            if alt.get(fr[2][-1]) is None:
                alt[fr[2][-1]] = k
        elif op == "for":
            nm, i = _ora_ident(r[3], r[2])
            i = _ora_skip(r[3], i)
            if r[3][i:i + 2] != "in" or (i + 2 < len(r[3]) and r[3][i + 2] in _OIDC):
                raise _OraErr("syntax", r[2])
            tail = r[3][i + 2:].strip(_OWS)
            if tail == "":
                raise _OraErr("syntax", r[2])
            r[1] = (nm, _ora_expr(tail, r[2], True))
            stack.append(["for", k, None, r[2]])
        elif op == "empty":
            if not stack or stack[-1][0] != "for" or stack[-1][2] is not None:
                raise _OraErr("unexpected_tag", r[2])
            if r[3] != "":
                raise _OraErr("syntax", r[2])
            stack[-1][2] = k
        elif op == "endfor":
            if not stack or stack[-1][0] != "for":
                raise _OraErr("unexpected_tag", r[2])
            if r[3] != "":
                raise _OraErr("syntax", r[2])
            fr = stack.pop()
            forinfo[fr[1]] = (fr[2], k)
            backfor[k] = fr[1]
            if fr[2] is not None:
                backfor[fr[2]] = fr[1]
        elif op == "set":
            nm, i = _ora_ident(r[3], r[2])
            i = _ora_skip(r[3], i)
            if not (i < len(r[3]) and r[3][i] == "=" and r[3][i:i + 2] != "=="):
                raise _OraErr("syntax", r[2])
            tail = r[3][i + 1:].strip(_OWS)
            if tail == "":
                raise _OraErr("syntax", r[2])
            r[1] = (nm, _ora_expr(tail, r[2], True))
    if stack:
        raise _OraErr("unclosed_block", stack[-1][3])
    return prog, (alt, chain_end, forinfo, backfor)


# --- filter application ----------------------------------------------
def _ora_up(s):
    return "".join([chr(ord(c) - 32) if "a" <= c <= "z" else c for c in s])


def _ora_lo(s):
    return "".join([chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in s])


def _ora_int(v):
    if v is True or v is False:
        return None
    if isinstance(v, int):
        return v if v >= 0 else None
    if isinstance(v, str) and len(v) > 0:
        for c in v:
            if c not in _ODIG:
                return None
        return int(v)
    return None


def _ora_apply(name, args, v, safe):
    t = _ora_type(v)
    if name == "safe":
        return v, True
    if name == "escape":
        return _ora_esc(_ora_text(v)), True
    if name == "upper":
        return _ora_up(_ora_text(v)), safe
    if name == "lower":
        return _ora_lo(_ora_text(v)), safe
    if name == "trim":
        return _ora_text(v).strip(_OWS), safe
    if name == "length":
        if t is None or t == "none" or t == "bool":
            return 0, safe
        if t == "number":
            return len("%d" % v), safe
        return len(v), safe
    if name == "first":
        if t in ("string", "list"):
            return (v[0] if len(v) else _OU), safe
        if t == "map":
            for k in v:
                return k, safe
            return _OU, safe
        return _OU, safe
    if name == "default":
        if _ora_truth(v):
            return v, safe
        return args[0], False
    if name == "join":
        sep = _ora_text(args[0])
        if t is None or t == "none":
            return "", safe
        if t == "list":
            return sep.join([_ora_text(x) for x in v]), safe
        if t == "string":
            return sep.join(list(v)), safe
        if t == "map":
            return sep.join([_ora_text(k) for k in v]), safe
        return _ora_text(v), safe
    if name == "replace":
        a, b = _ora_text(args[0]), _ora_text(args[1])
        s = _ora_text(v)
        if a == "":
            return s, safe
        return s.replace(a, b), safe
    st, ln = _ora_int(args[0]), _ora_int(args[1])
    if st is None or ln is None:
        return v, safe
    if t in ("string", "list"):
        return v[st:st + ln], safe
    return _ora_text(v)[st:st + ln], safe


# --- evaluation ------------------------------------------------------
def _ora_isnum(v):
    return isinstance(v, int) and v is not True and v is not False


def _ora_find(scopes, nm):
    k = len(scopes) - 1
    while k >= 0:
        if nm in scopes[k]:
            return scopes[k][nm]
        k -= 1
    return (_OU, False)


def _ora_val(node, scopes, pos):
    op = node[0]
    if op == "lit":
        return node[1]
    if op == "var":
        return _ora_find(scopes, node[1])[0]
    if op == "get":
        return _ora_lookup(_ora_val(node[1], scopes, pos), _ora_val(node[2], scopes, pos))
    if op == "not":
        return not _ora_truth(_ora_val(node[1], scopes, pos))
    if op == "and":
        for p in node[1]:
            if not _ora_truth(_ora_val(p, scopes, pos)):
                return False
        return True
    if op == "or":
        for p in node[1]:
            if _ora_truth(_ora_val(p, scopes, pos)):
                return True
        return False
    o = node[1]
    a = _ora_val(node[2], scopes, pos)
    b = _ora_val(node[3], scopes, pos)
    if o == "==":
        return _ora_eq(a, b)
    if o == "!=":
        return not _ora_eq(a, b)
    if o == "in":
        tb = _ora_type(b)
        if tb == "string":
            return isinstance(a, str) and a in b
        if tb == "list":
            for x in b:
                if _ora_eq(a, x):
                    return True
            return False
        if tb == "map":
            return isinstance(a, str) and a in b
        return False
    if not ((_ora_isnum(a) and _ora_isnum(b))
            or (_ora_type(a) == "string" and _ora_type(b) == "string")):
        raise _OraErr("bad_operand", pos)
    if o == "<":
        return a < b
    if o == "<=":
        return a <= b
    if o == ">":
        return a > b
    return a >= b


def _ora_pipe(pipe, scopes, pos):
    node, fl = pipe
    if node[0] == "var":
        v, safe = _ora_find(scopes, node[1])
    else:
        v, safe = _ora_val(node, scopes, pos), False
    for name, args in fl:
        v, safe = _ora_apply(name, args, v, safe)
    return v, safe


def _ora_seq(v, pos):
    t = _ora_type(v)
    if t is None or t == "none":
        return []
    if t == "list":
        return list(v)
    if t == "string":
        return list(v)
    if t == "map":
        return [k for k in v]
    raise _OraErr("not_iterable", pos)


def _ora_run(prog, links, ctx):
    alt, chain_end, forinfo, backfor = links
    scopes = [dict([(k, (v, False)) for k, v in (ctx or {}).items()])]
    ctrl = []
    out = []
    pc = 0
    steps = 0
    while pc < len(prog):
        steps += 1
        if steps > 400000:
            raise _OraErr("__runaway__", -1)
        r = prog[pc]
        op = r[0]
        if op == "text":
            out.append(r[1])
            pc += 1
        elif op == "out":
            v, safe = _ora_pipe(r[1], scopes, r[2])
            s = _ora_text(v)
            out.append(s if safe else _ora_esc(s))
            pc += 1
        elif op == "set":
            nm, pipe = r[1]
            scopes[-1][nm] = _ora_pipe(pipe, scopes, r[2])
            pc += 1
        elif op == "if":
            taken = _ora_truth(_ora_pipe(r[1], scopes, r[2])[0])
            ctrl.append(["if", taken])
            pc = pc + 1 if taken else alt[pc]
        elif op == "elif":
            fr = ctrl[-1]
            if fr[1]:
                pc = chain_end[pc]
            else:
                taken = _ora_truth(_ora_pipe(r[1], scopes, r[2])[0])
                fr[1] = taken
                pc = pc + 1 if taken else alt[pc]
        elif op == "else":
            fr = ctrl[-1]
            if fr[1]:
                pc = chain_end[pc]
            else:
                fr[1] = True
                pc += 1
        elif op == "endif":
            ctrl.pop()
            pc += 1
        elif op == "for":
            nm, pipe = r[1]
            seq = _ora_seq(_ora_pipe(pipe, scopes, r[2])[0], r[2])
            emp, endk = forinfo[pc]
            scopes.append({})
            if seq:
                ctrl.append(["for", pc, seq, 0, nm, endk, True])
                _ora_bind(scopes, nm, seq, 0)
                pc += 1
            else:
                ctrl.append(["for", pc, seq, 0, nm, endk, False])
                pc = (emp + 1) if emp is not None else endk
        elif op == "empty" or op == "endfor":
            fr = ctrl[-1]
            if not fr[6]:
                ctrl.pop()
                scopes.pop()
                pc = fr[5] + 1
            else:
                fr[3] += 1
                if fr[3] < len(fr[2]):
                    _ora_bind(scopes, fr[4], fr[2], fr[3])
                    pc = fr[1] + 1
                else:
                    ctrl.pop()
                    scopes.pop()
                    pc = fr[5] + 1
        else:
            pc += 1
    return "".join(out)


def _ora_bind(scopes, nm, seq, i):
    n = len(seq)
    scopes[-1][nm] = (seq[i], False)
    scopes[-1]["loop"] = ({"index": i + 1, "index0": i, "first": i == 0,
                           "last": i == n - 1, "length": n}, False)


def _ora_render(src, ctx):
    prog, links = _ora_parse(_ora_lex(src))
    return _ora_run(prog, links, ctx)


# =====================================================================
# comparison helpers
# =====================================================================
def _cand(src, ctx):
    """Return ('ok', text) or ('err', kind, pos) or ('bad', reason)."""
    try:
        r = tmpl.render(src, ctx)
    except TE as e:
        k = getattr(e, "kind", None)
        p = getattr(e, "pos", None)
        if not isinstance(k, str) or not isinstance(p, int) or isinstance(p, bool):
            return ("bad", "missing kind/pos")
        return ("err", k, p)
    except Exception as e:
        return ("bad", type(e).__name__)
    if not isinstance(r, str):
        return ("bad", "not a str")
    return ("ok", r)


def _want(src, ctx):
    try:
        return ("ok", _ora_render(src, ctx))
    except _OraErr as e:
        return ("err", e.kind, e.pos)


def one(src, ctx=None):
    ctx = {} if ctx is None else ctx
    return _cand(src, ctx) == _want(src, ctx)


def _all(cases):
    def probe():
        for c in cases:
            if not one(c[0], c[1]):
                return False
        return True
    return probe


def out(src, ctx, expect):
    return _cand(src, ctx) == ("ok", expect)


def err(src, kind, pos, ctx=None):
    return _cand(src, {} if ctx is None else ctx) == ("err", kind, pos)


def group(fn, cases):
    def probe():
        for c in cases:
            if not fn(*c):
                return False
        return True
    return probe


# =====================================================================
# 1-2: API surface and forbidden imports
# =====================================================================
def api_probe():
    if not (isinstance(getattr(tmpl, "TemplateError", None), type)
            and issubclass(tmpl.TemplateError, BaseException)):
        return False
    if TE is _MissingErr:
        return False
    return (out("hi", {}, "hi") and out("", {}, "")
            and out("Hello {{ name | upper }}!", {"name": "ada"}, "Hello ADA!")
            and err("abc {{ x", "unclosed_tag", 4)
            and err("a{# c", "unclosed_tag", 1)
            and err("{% if x %}", "unclosed_block", 0))


check("render()/TemplateError API with .kind and .pos", api_probe)


def _calls(src, word):
    n = len(word)
    i = src.find(word + "(")
    while i >= 0:
        before = src[:i].rstrip(" \t")
        prev = src[i - 1] if i > 0 else " "
        if prev not in _OIDC and prev != "." and not before.endswith("def"):
            return True
        i = src.find(word + "(", i + n)
    return False


def ban_probe():
    src = inspect.getsource(tmpl)
    if "__import__" in src or "importlib" in src:
        return False
    if _calls(src, "eval") or _calls(src, "exec"):
        return False
    bad = ("re", "string", "html", "shlex", "jinja2", "jinja", "django", "mako",
           "chevron", "pystache", "mustache", "genshi")
    for line in src.split("\n"):
        s = line.split("#")[0].strip().replace(",", " ")
        p = s.split()
        if not p:
            continue
        if p[0] == "from" and len(p) > 1 and p[1].split(".")[0] in bad:
            return False
        if p[0] == "import":
            i = 1
            while i < len(p):
                if p[i] == "as":
                    i += 2
                    continue
                if p[i].split(".")[0] in bad:
                    return False
                i += 1
    return True


check("bans: no re/string/html/shlex/templating lib, no eval/exec", ban_probe)

# =====================================================================
# 3-5: whitespace control and comments
# =====================================================================
check("whitespace control: unbounded, crosses newlines, both sides", group(out, [
    ("a  \n\t {%- if 1 %}x{% endif %}", {}, "ax"),
    ("{% if 1 %}x{% endif %} \n\n  b", {}, "x \n\n  b"),
    ("{% if 1 -%} \n\n  b{% endif %}", {}, "b"),
    ("a \n {{- v -}} \n b", {"v": "V"}, "aVb"),
    ("   {{- v }}", {"v": "V"}, "V"),
    ("{{ v -}}   ", {"v": "V"}, "V"),
    ("a{{- v }}", {"v": "V"}, "aV"),
    ("{{ v }}b", {"v": "V"}, "Vb"),
    ("x  {%- if 0 %}q{% endif %}  y", {}, "x  y"),
    ("x  {% if 0 %}q{% endif %}  y", {}, "x    y"),
    ("a\n{%- if 1 -%}\n\nb\n{%- endif -%}\nc", {}, "abc"),
]))

check("whitespace control: markers do not reach past a tag", group(out, [
    ("a {{ v }}{{- w }} b", {"v": "1", "w": "2"}, "a 12 b"),
    ("a {{ v -}}{{ w }} b", {"v": "1", "w": "2"}, "a 12 b"),
    ("a {{ v -}} {{- w }} b", {"v": "1", "w": "2"}, "a 12 b"),
    ("  {%- if 1 %}{% endif -%}  ", {}, ""),
    ("{{- v -}}", {"v": " x "}, " x "),
    ("a \n {%- if 1 %} \n keep{% endif %}", {}, "a \n keep"),
]))

check("whitespace control: inside blocks, trimmed once at lex time", group(out, [
    ("{% for x in l %}\n  {{- x }}\n{% endfor %}", {"l": ["a", "b"]},
     "a\nb\n"),
    ("{% for x in l %}  {{- x -}}  {% endfor %}", {"l": ["a", "b"]}, "ab"),
    ("{%- for x in l -%}\n {{ x }}\n{%- endfor -%}", {"l": ["a"]}, "a"),
    ("A{% if 1 %}\n\t{%- endif %}B", {}, "AB"),
    ("A{% if 0 %}\n\t{%- endif %}B", {}, "AB"),
    ("{% for x in l %}{{ x }} {%- endfor %}!", {"l": ["a", "b"]}, "ab!"),
    ("{% if 1 %} a {% else %} b {% endif %}", {}, " a "),
    ("{%- if 1 -%} a {%- else -%} b {%- endif -%}", {}, "a"),
    ("\n\n{%- set v = 1 -%}\n\n{{ v }}", {}, "1"),
]))

check("comments: no nesting, discarded, own whitespace control", group(out, [
    ("a{# c #}b", {}, "ab"),
    ("a {#- c -#} b", {}, "ab"),
    ("a{# {# b #} c #}", {}, "a c #}"),
    ("a{#{{ v }}#}b", {"v": "V"}, "ab"),
    ("{# only #}", {}, ""),
    ("x{##}y", {}, "xy"),
    ("x{#-#}y", {}, "xy"),
    ("a  {# c #}  b", {}, "a    b"),
    ("{% if 1 %}{# c #}z{% endif %}", {}, "z"),
]))

# =====================================================================
# 6-7: escaping and safety
# =====================================================================
_H = {"h": "<a href='x'>&", "n": 5, "L": ["<", "&"], "M": {"k": "<"}}

check("auto-escaping: exact character set, literals never escaped", group(out, [
    ("<b>{{ h }}</b>", _H, "<b>&lt;a href=&#39;x&#39;&gt;&amp;</b>"),
    ("{{ '<&>' }}", {}, "&lt;&amp;&gt;"),
    ("{{ n }}", _H, "5"),
    ("{{ L }}", _H, "[&lt;, &amp;]"),
    ("{{ M }}", _H, "{k: &lt;}"),
    ("{{ 'a\"b' }}", {}, "a&#34;b"),
    ("{{ h | length }}", _H, "13"),
    ("{% if h %}&{% endif %}", _H, "&"),
]))

check("safe/escape are sticky through later filters", group(out, [
    ("{{ h | safe }}", _H, "<a href='x'>&"),
    ("{{ h | safe | upper }}", _H, "<A HREF='X'>&"),
    ("{{ h | escape }}", _H, "&lt;a href=&#39;x&#39;&gt;&amp;"),
    ("{{ h | escape | upper }}", _H, "&LT;A HREF=&#39;X&#39;&GT;&AMP;"),
    ("{{ h | safe | escape }}", _H, "&lt;a href=&#39;x&#39;&gt;&amp;"),
    ("{{ h | safe | replace:a,& }}", _H, "<& href='x'>&"),
    ("{% set s = h | safe %}{{ s }}", _H, "<a href='x'>&"),
    ("{% set s = h | safe %}{{ s | lower }}{{ s.0 }}", _H, "<a href='x'>&&lt;"),
    ("{{ miss | safe | default:< }}", {}, "&lt;"),
    ("{{ h | safe | default:< }}", _H, "<a href='x'>&"),
]))

# =====================================================================
# 8-10: filters
# =====================================================================
_F = {"s": " Ab \n", "L": ["a", 2, True, None], "M": {"b": 1, "a": 2},
      "n": -12, "z": 0, "t": True, "e": "", "el": [], "em": {}}

check("filters on odd inputs: upper/lower/trim/length/first", group(out, [
    ("{{ s | trim }}", _F, "Ab"),
    ("{{ s | upper }}", _F, " AB \n"),
    ("{{ L | upper }}", _F, "[A, 2, TRUE, ]"),
    ("{{ t | upper }}", _F, "TRUE"),
    ("{{ miss | upper }}", _F, ""),
    ("{{ n | length }}{{ z | length }}{{ t | length }}", _F, "310"),
    ("{{ miss | length }}{{ e | length }}{{ M | length }}", _F, "002"),
    ("{{ L | first }}{{ M | first }}{{ el | first }}{{ e | first }}", _F, "ab"),
    ("{{ s | first }}", _F, " "),
    ("{{ n | first }}", _F, ""),
]))

check("filters on odd inputs: default/join/replace/slice", group(out, [
    ("{{ z | default:X }}{{ e | default:X }}{{ el | default:X }}", _F, "XXX"),
    ("{{ '0' | default:X }}{{ 'false' | default:X }}", {}, "XX"),
    ("{{ '0.0' | default:X }}{{ 'False' | default:X }}", {}, "0.0False"),
    ("{{ L | join:- }}", _F, "a-2-true-"),
    ("{{ M | join:',' }}", _F, "b,a"),
    ("{{ 'abc' | join:. }}", {}, "a.b.c"),
    ("{{ n | join:X }}{{ miss | join:X }}", _F, "-12"),
    ("{{ 'aaa' | replace:aa,b }}", {}, "ba"),
    ("{{ 'abc' | replace:'',X }}", {}, "abc"),
    ("{{ 'abc' | replace:b, }}", {}, "ac"),
    ("{{ L | slice:1,2 }}", _F, "[2, true]"),
    ("{{ 'abcdef' | slice:4,9 }}", {}, "ef"),
    ("{{ 'abc' | slice:9,1 }}", {}, ""),
    ("{{ 'abc' | slice:x,1 }}", {}, "abc"),
    ("{{ n | slice:0,2 }}", _F, "-1"),
]))

check("filter argument parsing: quotes, escapes, bare, commas", group(out, [
    ("{{ miss | default:'a,b' }}", {}, "a,b"),
    ("{{ miss | default:\"x|y\" }}", {}, "x|y"),
    ("{{ miss | default: a b  }}", {}, "a b"),
    ("{{ miss | default: }}", {}, ""),
    ("{{ miss | default:x }}", {"x": "V"}, "x"),
    ("{{ miss | default:0 }}", {}, "0"),
    ("{{ miss | default:'\\n' | length }}", {}, "1"),
    ("{{ miss | default:'a\\'b' }}", {}, "a&#39;b"),
    ("{{ 'abc' | replace: b , 'Q' }}", {}, "aQc"),
    ("{{ 'a\"b' | replace:\"\\\"\",Q }}", {}, "aQb"),
    ("{{ miss|default:true }}{{ miss|default:none }}{{ miss|default:false }}", {},
     "truefalse"),
    ("{{ 'ab' | slice:'1','1' }}", {}, "b"),
]))

# =====================================================================
# 11-12: lookups and truthiness
# =====================================================================
_LK = {"m": {"a": {"b": "deep"}, "0": "zero", "size": "S", "keys": "K"},
       "l": ["p", "q"], "s": "hey", "i": 1, "n": None, "bt": True}

check("lookup precedence, missing keys, pseudo-keys", group(out, [
    ("{{ m.a.b }}", _LK, "deep"),
    ("{{ m.0 }}", _LK, "zero"),
    ("{{ m[0] }}", _LK, ""),
    ("{{ m['0'] }}", _LK, "zero"),
    ("{{ m.size }}{{ m.keys }}", _LK, "SK"),
    ("{{ l.size }}{{ s.size }}", _LK, "23"),
    ("{{ l.keys }}{{ i.size }}{{ n.size }}", _LK, ""),
    ("{{ l.1 }}{{ l[1] }}{{ s.2 }}", _LK, "qqy"),
    ("{{ l.2 }}{{ l['x'] }}{{ s.9 }}", _LK, ""),
    ("{{ m.a.zzz.qqq }}", _LK, ""),
    ("{{ l.type }}{{ s.type }}{{ i.type }}{{ bt.type }}{{ n.type }}", _LK,
     "liststringnumberbool"),
    ("{{ miss.type }}", _LK, ""),
    ("{{ m[m.0] }}", {"m": {"0": "a", "a": "hit"}}, "hit"),
]))

check("truthiness differs from Python in stated places", group(out, [
    ("{% if '0' %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if 'false' %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if 'False' %}T{% else %}F{% endif %}", {}, "T"),
    ("{% if '0.0' %}T{% else %}F{% endif %}", {}, "T"),
    ("{% if ' ' %}T{% else %}F{% endif %}", {}, "T"),
    ("{% if 0 %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if none %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if miss %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if em %}T{% else %}F{% endif %}", {"em": {}}, "F"),
    ("{% if em %}T{% else %}F{% endif %}", {"em": {"a": 0}}, "T"),
    ("{{ '0' | default:D }}{{ '0.0' | default:D }}", {}, "D0.0"),
]))

# =====================================================================
# 13-15: conditions
# =====================================================================
check("equality compares types first; ordering demands matching types", group(out, [
    ("{% if 1 == true %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if '1' == 1 %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if miss == none %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if miss == other %}T{% else %}F{% endif %}", {}, "T"),
    ("{% if l == r %}T{% else %}F{% endif %}", {"l": [1, 2], "r": [1, 2]}, "T"),
    ("{% if l == r %}T{% else %}F{% endif %}", {"l": {"a": 1, "b": 2},
                                                "r": {"b": 2, "a": 1}}, "T"),
    ("{% if l != r %}T{% else %}F{% endif %}", {"l": [1], "r": [True]}, "T"),
    ("{% if 'a' < 'b' %}T{% endif %}{% if 2 <= 2 %}T{% endif %}", {}, "TT"),
]))

check("bad_operand and not_iterable are render errors at the tag offset", group(err, [
    ("xx{% if true < 2 %}q{% endif %}", "bad_operand", 2),
    ("{% if 'a' < 1 %}q{% endif %}", "bad_operand", 0),
    ("{% if miss > 1 %}q{% endif %}", "bad_operand", 0),
    ("{{ 1 > none }}", "bad_operand", 0),
    ("ab{% for x in 3 %}q{% endfor %}", "not_iterable", 2),
    ("{% for x in true %}q{% endfor %}", "not_iterable", 0),
]))

check("in, not/and/or precedence, short-circuit skips errors", group(out, [
    ("{% if 'b' in 'abc' %}T{% endif %}{% if '' in 'a' %}T{% endif %}", {}, "TT"),
    ("{% if 1 in 'abc' %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if 'a' in l %}T{% else %}F{% endif %}", {"l": ["a"]}, "T"),
    ("{% if 1 in l %}T{% else %}F{% endif %}", {"l": [True]}, "F"),
    ("{% if 'k' in m %}T{% endif %}{% if 'z' in m %}T{% endif %}", {"m": {"k": 1}}, "T"),
    ("{% if 'a' in 5 %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if not 1 == 2 %}T{% else %}F{% endif %}", {}, "T"),
    ("{% if not '0' %}T{% else %}F{% endif %}", {}, "T"),
    ("{% if false and true < 2 %}T{% else %}F{% endif %}", {}, "F"),
    ("{% if true or true < 2 %}T{% else %}F{% endif %}", {}, "T"),
    ("{% if 1 or 0 and 0 %}T{% else %}F{% endif %}", {}, "T"),
    ("{{ 0 or 'x' }}", {}, "true"),
    ("{{ miss or miss }}", {}, "false"),
    ("{{ 'a' or 'b' | upper }}", {}, "TRUE"),
]))

# =====================================================================
# 16-17: loops
# =====================================================================
check("loop variables, nesting, shadowing and restoration", group(out, [
    ("{% for x in l %}{{ loop.index }}{{ loop.index0 }}{{ loop.first }}"
     "{{ loop.last }}{{ loop.length }};{% endfor %}", {"l": ["a", "b"]},
     "10truefalse2;21falsetrue2;"),
    ("{{ x }}{% for x in l %}{{ x }}{% endfor %}{{ x }}", {"x": "O", "l": ["a"]}, "OaO"),
    ("{% for x in l %}{% for y in l %}{{ loop.index }}{{ x }}{{ y }}{% endfor %}"
     "{{ loop.index }}{% endfor %}", {"l": ["a", "b"]},
     "1aa2ab11ba2bb2"),
    ("{% for x in l %}{{ loop.parent }}{{ loop.parent.index }}{% endfor %}",
     {"l": [1]}, ""),
    ("{% for x in s %}[{{ x }}]{% endfor %}", {"s": "ab"}, "[a][b]"),
    ("{% for k in m %}{{ k }}={{ m[k] }};{% endfor %}", {"m": {"b": 1, "a": 2}},
     "b=1;a=2;"),
    ("{% for x in miss %}q{% empty %}E{% endfor %}", {}, "E"),
    ("{% for x in none %}q{% empty %}E{% endfor %}", {}, "E"),
    ("{% for x in el %}q{% endfor %}!", {"el": []}, "!"),
    ("{% for x in l %}{{ loop.keys | join:'-' }}{% endfor %}", {"l": [1]},
     "index-index0-first-last-length"),
    ("{% for x in l %}{{ loop }}{% endfor %}", {"l": ["a"]},
     "{index: 1, index0: 0, first: true, last: true, length: 1}"),
]))

check("set scoping: leaks out of if, not out of for", group(out, [
    ("{% if 1 %}{% set a = 'X' %}{% endif %}{{ a }}", {}, "X"),
    ("{% if 0 %}{% set a = 'X' %}{% else %}{% set a = 'Y' %}{% endif %}{{ a }}", {}, "Y"),
    ("{% for x in l %}{% set a = 'X' %}{% endfor %}[{{ a }}]", {"l": [1]}, "[]"),
    ("{% set a = 'O' %}{% for x in l %}{% set a = 'X' %}{% endfor %}{{ a }}",
     {"l": [1]}, "O"),
    ("{% for x in l %}{{ a }}{% set a = 'X' %}{% endfor %}", {"l": [1, 2, 3]}, "XX"),
    ("{% for x in l %}{% if loop.first %}{% set a = 'F' %}{% endif %}{{ a }}{% endfor %}",
     {"l": [1, 2]}, "FF"),
    ("{% for x in l %}{% set x = 'S' %}{{ x }}{% endfor %}", {"l": [1, 2]}, "SS"),
    ("{% for x in el %}{% set a = 'X' %}{% empty %}{% set b = 'Y' %}{% endfor %}"
     "[{{ a }}{{ b }}]", {"el": []}, "[]"),
    ("{% if 0 %}{% set a = 'X' %}{% endif %}[{{ a }}]", {}, "[]"),
    ("{% set a = miss | default:D %}{{ a }}", {}, "D"),
]))



# =====================================================================
# 17-25: strictness -- error taxonomy, positions and ordering
# =====================================================================
check("strict: unknown_tag / unexpected_tag with exact positions", group(err, [
    ("{% bogus %}", "unknown_tag", 0),
    ("ab{%  %}", "unknown_tag", 2),
    ("{% IF 1 %}{% endif %}", "unknown_tag", 0),
    ("{% endiff %}", "unknown_tag", 0),
    ("x{% endif %}", "unexpected_tag", 1),
    ("{% else %}", "unexpected_tag", 0),
    ("{% empty %}", "unexpected_tag", 0),
    ("{% if 1 %}{% endfor %}{% endif %}", "unexpected_tag", 10),
    ("{% if 1 %}{% else %}{% elif 2 %}{% endif %}", "unexpected_tag", 20),
    ("{% if 1 %}{% else %}{% else %}{% endif %}", "unexpected_tag", 20),
    ("{% for x in l %}{% else %}{% endfor %}", "unexpected_tag", 16),
    ("{% for x in l %}{% empty %}{% empty %}{% endfor %}", "unexpected_tag", 27),
    ("{% for x in l %}{% endif %}{% endfor %}", "unexpected_tag", 16),
]))

check("strict: unclosed_tag / unclosed_block point at the right opener", group(err, [
    ("abc {{ x", "unclosed_tag", 4),
    ("a{# c", "unclosed_tag", 1),
    ("a{% if 1 %}b{% x", "unclosed_tag", 12),
    ("{{ a }}{{", "unclosed_tag", 7),
    ("{{-", "unclosed_tag", 0),
    ("{% if 1 %}", "unclosed_block", 0),
    ("a{% for x in l %}{% if 1 %}{% endif %}", "unclosed_block", 1),
    ("{% if 1 %}{% for x in l %}", "unclosed_block", 10),
    ("{% if 1 %}{% for x in l %}{% endfor %}", "unclosed_block", 0),
    ("{% if 1 %}{% elif 2 %}", "unclosed_block", 0),
    ("{% for x in l %}{% empty %}", "unclosed_block", 0),
]))

check("strict: statement-level syntax errors", group(err, [
    ("{{  }}", "syntax", 0),
    ("{{}}", "syntax", 0),
    ("{% if %}{% endif %}", "syntax", 0),
    ("{% if 1 %}{% elif %}{% endif %}", "syntax", 10),
    ("{% if 1 %}{% else x %}{% endif %}", "syntax", 10),
    ("{% for x in l %}{% endfor x %}", "syntax", 16),
    ("{% if 1 %}{% endif x %}", "syntax", 10),
    ("{% for x in l %}{% empty y %}{% endfor %}", "syntax", 16),
    ("{% set 1x = 2 %}", "syntax", 0),
    ("{% set a == 2 %}", "syntax", 0),
    ("{% set a = %}", "syntax", 0),
    ("{% set in = 2 %}", "syntax", 0),
    ("{% for x of l %}{% endfor %}", "syntax", 0),
    ("{% for in in l %}{% endfor %}", "syntax", 0),
    ("{% for xs l %}{% endfor %}", "syntax", 0),
    ("{% for x in %}{% endfor %}", "syntax", 0),
]))

check("strict: expression-level syntax errors", group(err, [
    ("{{ a b }}", "syntax", 0),
    ("{{ 1 < 2 < 3 }}", "syntax", 0),
    ("{{ a[1 }}", "syntax", 0),
    ("{{ 'ab }}", "syntax", 0),
    ("{{ a. }}", "syntax", 0),
    ("{{ a.'b' }}", "syntax", 0),
    ("{{ and }}", "syntax", 0),
    ("{{ a and }}", "syntax", 0),
    ("{{ not }}", "syntax", 0),
    ("{{ a == }}", "syntax", 0),
    ("{{ a ! b }}", "syntax", 0),
    ("{{ a) }}", "syntax", 0),
    ("{% if a | upper %}{% endif %}", "syntax", 0),
    ("{% if a %}{% elif b|upper %}{% endif %}", "syntax", 10),
]))

check("strict: filter errors and their order inside one tag", group(err, [
    ("{{ x | nope }}", "unknown_filter", 0),
    ("{{ x | upper | nope }}", "unknown_filter", 0),
    ("{{ x | UPPER }}", "unknown_filter", 0),
    ("{{ x | nope:'a }}", "unknown_filter", 0),
    ("{{ x | nope:1,2,3 }}", "unknown_filter", 0),
    ("{{ x | upper:1 }}", "filter_args", 0),
    ("{{ x | safe: }}", "filter_args", 0),
    ("{{ x | replace:1 }}", "filter_args", 0),
    ("{{ x | default:1,2 }}", "filter_args", 0),
    ("{{ x | slice:1 }}", "filter_args", 0),
    ("{{ x | default:'a'b }}", "syntax", 0),
    ("{{ x | default:'a }}", "syntax", 0),
    ("{{ x | 2up }}", "syntax", 0),
    ("{{ x | }}", "syntax", 0),
    ("{{ x | upper | }}", "syntax", 0),
]))

check("strict: bad_operand / not_iterable are render errors at the tag offset",
      group(err, [
          ("xx{% if true < 2 %}q{% endif %}", "bad_operand", 2),
          ("{% if 'a' < 1 %}q{% endif %}", "bad_operand", 0),
          ("{% if miss > 1 %}q{% endif %}", "bad_operand", 0),
          ("{% if none <= none %}q{% endif %}", "bad_operand", 0),
          ("{{ 1 > none }}", "bad_operand", 0),
          ("{{ 'a' | length }}{{ 1 >= false }}", "bad_operand", 18),
          ("ab{% for x in 3 %}q{% endfor %}", "not_iterable", 2),
          ("{% for x in true %}q{% endfor %}", "not_iterable", 0),
          ("{% for x in l %}{% for y in 0 %}{% endfor %}{% endfor %}",
           "not_iterable", 16, {"l": [1]}),
          ("{% for x in n|length %}{% endfor %}", "not_iterable", 0, {"n": "ab"}),
      ]))

check("strict: lexing beats parsing beats rendering", group(err, [
    ("{% bogus %}{{ x", "unclosed_tag", 11),
    ("{% if 1 < true %}q{% endif %}{{ y", "unclosed_tag", 29),
    ("{% for x in 3 %}{% endfor %}{% zz", "unclosed_tag", 28),
    ("{% if 1 < true %}{% bogus %}{% endif %}", "unknown_tag", 17),
    ("{% if 1 < true %}{% endif %}{% endfor %}", "unexpected_tag", 28),
    ("{% for x in 3 %}{% endfor %}{% if 1 %}", "unclosed_block", 28),
    ("{{ 1 < true }}{{ x | nope }}", "unknown_filter", 14),
    ("{{ 1 < true }}{{ a b }}", "syntax", 14),
    ("{% for x in 3 %}{% endfor %}{{ z | upper:1 }}", "filter_args", 28),
]))

check("strict: leftmost-first, innermost unclosed block", group(err, [
    ("{% if 1 < true %}a{% endif %}{% for y in 2 %}{% endfor %}", "bad_operand", 0),
    ("{% if 0 %}{% bogus %}{% endif %}", "unknown_tag", 10),
    ("{% if 0 %}{{ 1 < true }}{% endif %}{{ 2 < false }}", "bad_operand", 35),
    ("{% bogus %}{% alsobogus %}", "unknown_tag", 0),
    ("{{ a b }}{{ c | nope }}", "syntax", 0),
    ("{% if 1 %}{% for x in l %}{% if 2 %}", "unclosed_block", 26),
    ("{% for a in l %}{% for b in l %}{% endfor %}", "unclosed_block", 0),
    ('{% if x == "%}" %}{% endif %}', "syntax", 0),
    ("{# {% bogus %} #}{% alsobogus %}", "unknown_tag", 17),
]))


def canon_probe():
    if not isinstance(_cand("{{ v }}", {"v": 1})[1], str):
        return False
    cases = [
        ("{{ '<&>' }}", {}, "&lt;&amp;&gt;"),
        ("{{ v }}", {"v": "&lt;"}, "&amp;lt;"),
        ("{{ v }}", {"v": "&amp;"}, "&amp;amp;"),
        ("{{ v }}", {"v": "a\\b`~!@#$%^*()_+=[]{}|;:,./?"},
         "a\\b`~!@#$%^*()_+=[]{}|;:,./?"),
        ("{% for x in l %}{{ loop.first == true }}{{ loop.first == 1 }}{% endfor %}",
         {"l": [1]}, "truefalse"),
        ("{% for x in l %}{{ loop.last }}{% endfor %}", {"l": [1, 2]}, "falsetrue"),
        ("{{ v }}", {"v": [True, 1, None]}, "[true, 1, ]"),
        ("{{ v }}", {"v": {"a": [1], "b": {"c": 2}}}, "{a: [1], b: {c: 2}}"),
        ("  a  ", {}, "  a  "),
        ("{{ v }}{{ w }}", {"v": "", "w": ""}, ""),
    ]
    for s, c, e in cases:
        if not out(s, c, e):
            return False
    for s in ("{{ miss.a.b }}", "{% for x in miss %}{% endfor %}", "{{ 'x' }}"):
        if _cand(s, {})[0] != "ok":
            return False
    for s in ("{{ 1 < 'a' }}", "{% bogus %}", "{{ x |", "{{ a[ }}", "{% endif %}"):
        r = _cand(s, {})
        if r[0] != "err" or r[1] not in ("unclosed_tag", "unknown_tag",
                                         "unexpected_tag", "unclosed_block", "syntax",
                                         "unknown_filter", "filter_args",
                                         "bad_operand", "not_iterable"):
            return False
    return True


check("strict: canonical output, real booleans, only TemplateError escapes", canon_probe)

# =====================================================================
# 26-29: randomised differential
# =====================================================================
_CTXS = [
    {"a": "A&b", "b": "<i>", "s": " hi \n", "n": 3, "z": 0, "l": ["p", "q", "r"],
     "m": {"a": 1, "b": {"c": "deep"}, "size": "S"}, "t": True, "f": False, "u": None},
    {"a": "", "b": "0", "s": "false", "n": -2, "z": 7, "l": [], "m": {},
     "t": False, "f": True, "u": None, "x": ["<", "&", "'"]},
    {"a": "zz", "b": [1, 2], "s": {"k": "v"}, "n": 0, "z": "0", "l": ["x"],
     "m": {"0": "zero", "keys": "K"}, "t": None, "f": 1, "u": "u"},
    {"a": 12, "b": True, "s": "abc", "n": 1, "z": [[1], [2]], "l": "str",
     "m": {"a": ["x", "y"]}, "t": "t", "f": "", "u": []},
]
_PATHS = ["a", "b", "s", "n", "z", "l", "m", "t", "f", "u", "miss", "l.0", "l.1",
          "m.a", "m.b", "m.0", "m.size", "m.keys", "m.type", "l.size", "s.0",
          "m['a']", "m[0]", "l[1]", "m.b.c", "a.type", "miss.x", "loop.index",
          "loop.index0", "loop.first", "loop.last", "loop.length", "loop.parent"]
_LITS = ["'x'", "0", "1", "'0'", "'false'", "true", "false", "none", "''", "'<&>'",
         "2", "'abc'", '"a\'b"']
_FILTS = ["upper", "lower", "trim", "length", "first", "safe", "escape",
          "default:D", "default:'a,b'", "default:0", "default:", "join:-",
          "join:', '", "replace:a,B", "replace:'',X", "slice:0,2", "slice:1,9",
          "slice:x,1"]
_TXT = ["", " ", "\n", "  \n ", "ab", "<&>", "x", " y ", "\t", "a\nb", "'q'"]


def _rmark(rng):
    return ("-" if rng.random() < 0.4 else "", "-" if rng.random() < 0.4 else "")


def _rexpr(rng, depth):
    r = rng.random()
    if r < 0.45:
        return rng.choice(_PATHS)
    if r < 0.6:
        return rng.choice(_LITS)
    if r < 0.72 and depth > 0:
        return "not " + _rexpr(rng, depth - 1)
    if r < 0.86:
        op = rng.choice(["==", "!=", "<", "<=", ">", ">=", "in"])
        a = rng.choice(_PATHS + _LITS)
        b = rng.choice(_PATHS + _LITS)
        return "%s %s %s" % (a, op, b)
    if depth <= 0:
        return rng.choice(_PATHS)
    op = rng.choice([" and ", " or "])
    return _rexpr(rng, depth - 1) + op + _rexpr(rng, depth - 1)


def _rpipe(rng, depth):
    e = _rexpr(rng, depth)
    for _ in range(rng.randint(0, 3)):
        if rng.random() < 0.55:
            e = e + " | " + rng.choice(_FILTS)
        else:
            e = e + "|" + rng.choice(_FILTS)
    return e


def _rbody(rng, depth, budget):
    acc = []
    for _ in range(rng.randint(1, 4)):
        if budget[0] <= 0:
            break
        budget[0] -= 1
        r = rng.random()
        if r < 0.24:
            acc.append(rng.choice(_TXT))
        elif r < 0.5:
            lm, rm = _rmark(rng)
            acc.append("{{%s %s %s}}" % (lm, _rpipe(rng, 1), rm))
        elif r < 0.6:
            lm, rm = _rmark(rng)
            acc.append("{#%s c %s#}" % (lm, rm))
        elif r < 0.68:
            lm, rm = _rmark(rng)
            acc.append("{%%%s set %s = %s %s%%}"
                       % (lm, rng.choice(["v", "a", "w"]), _rpipe(rng, 0), rm))
        elif r < 0.84 and depth > 0:
            lm, rm = _rmark(rng)
            parts = ["{%%%s if %s %s%%}" % (lm, _rexpr(rng, 1), rm)]
            parts.append(_rbody(rng, depth - 1, budget))
            for _k in range(rng.randint(0, 2)):
                lm, rm = _rmark(rng)
                parts.append("{%%%s elif %s %s%%}" % (lm, _rexpr(rng, 1), rm))
                parts.append(_rbody(rng, depth - 1, budget))
            if rng.random() < 0.5:
                lm, rm = _rmark(rng)
                parts.append("{%%%s else %s%%}" % (lm, rm))
                parts.append(_rbody(rng, depth - 1, budget))
            lm, rm = _rmark(rng)
            parts.append("{%%%s endif %s%%}" % (lm, rm))
            acc.append("".join(parts))
        elif depth > 0:
            lm, rm = _rmark(rng)
            var = rng.choice(["i", "x", "a", "l"])
            parts = ["{%%%s for %s in %s %s%%}" % (lm, var, _rpipe(rng, 0), rm)]
            parts.append(_rbody(rng, depth - 1, budget))
            if rng.random() < 0.45:
                lm, rm = _rmark(rng)
                parts.append("{%%%s empty %s%%}" % (lm, rm))
                parts.append(_rbody(rng, depth - 1, budget))
            lm, rm = _rmark(rng)
            parts.append("{%%%s endfor %s%%}" % (lm, rm))
            acc.append("".join(parts))
        else:
            acc.append(rng.choice(_TXT))
    return "".join(acc)


def gen(seed, n, mutate=0.0):
    rng = random.Random(seed)
    cases = []
    while len(cases) < n:
        src = _rbody(rng, 3, [14])
        if len(src) > 900:
            continue
        if mutate and rng.random() < mutate:
            k = rng.randint(0, max(0, len(src) - 1))
            r = rng.random()
            if r < 0.4 and len(src) > 2:
                src = src[:rng.randint(1, len(src))]
            elif r < 0.7:
                src = (src[:k] + rng.choice(["{%", "{{", "}}", "%}", "|", "'", "-"])
                       + src[k:])
            else:
                src = src[:k] + src[k + 1:]
        cases.append((src, _CTXS[len(cases) % len(_CTXS)]))
    return cases


def _slice(cases, k, i):
    return [c for j, c in enumerate(cases) if j % k == i]


_G = gen(5601, 600)
for _i in range(2):
    check("randomised differential, well-formed templates (bucket %d)" % (_i + 1),
          _all(_slice(_G, 2, _i)))

_M = gen(5677, 400, mutate=1.0)
for _i in range(2):
    check("randomised differential, mutated/malformed templates (bucket %d)" % (_i + 1),
          _all(_slice(_M, 2, _i)))

_t.cancel()
report()
