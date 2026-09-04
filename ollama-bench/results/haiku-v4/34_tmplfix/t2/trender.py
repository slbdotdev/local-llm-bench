"""Parser + renderer for the tiny template language."""

import tlex
from tlex import TemplateError

DIGITS = set("0123456789")
LETTERS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
WORD = LETTERS | DIGITS
KEYWORDS = ("if", "elif", "else", "endif", "for", "empty", "endfor")


def _is_ident(s):
    return bool(s) and s[0] in LETTERS and all(c in WORD for c in s)


def _all_digits(s):
    return bool(s) and all(c in DIGITS for c in s)


# --------------------------------------------------------------- expressions

def _split_pipes(src):
    parts = []
    cur = []
    i = 0
    while i < len(src):
        c = src[i]
        if c == "'":
            q = src.find("'", i + 1)
            if q < 0:
                raise TemplateError("syntax", "unterminated string literal")
            cur.append(src[i:q + 1])
            i = q + 1
            continue
        if c == "|":
            parts.append("".join(cur))
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    parts.append("".join(cur))
    return parts


def _parse_primary(s):
    if _all_digits(s):
        return ("int", int(s))
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'" and "'" not in s[1:-1]:
        return ("str", s[1:-1])
    segs = s.split(".")
    if not _is_ident(segs[0]):
        raise TemplateError("syntax", "bad expression %r" % (s,))
    for seg in segs[1:]:
        if not seg or not all(c in WORD for c in seg):
            raise TemplateError("syntax", "bad expression %r" % (s,))
    return ("path", segs)


def parse_expr(src):
    parts = _split_pipes(src)
    prim = parts[0].strip()
    if not prim:
        raise TemplateError("syntax", "empty expression")
    node = _parse_primary(prim)
    filters = []
    for f in parts[1:]:
        f = f.strip()
        if not _is_ident(f):
            raise TemplateError("syntax", "bad filter %r" % (f,))
        filters.append(f)
    return (node, filters)


# -------------------------------------------------------------------- parser

class _Parser(object):
    def __init__(self, toks):
        self.toks = toks
        self.pos = 0

    def parse(self):
        nodes, kw, _rest = self.block(())
        assert kw is None
        return nodes

    def block(self, stop):
        nodes = []
        while self.pos < len(self.toks):
            kind, src = self.toks[self.pos]
            if kind == "text":
                nodes.append(("text", src))
                self.pos += 1
                continue
            if kind == "var":
                self.pos += 1
                node, filters = parse_expr(src)
                nodes.append(("var", node, filters))
                continue
            parts = src.strip().split(None, 1)
            kw = parts[0] if parts else ""
            rest = parts[1].strip() if len(parts) > 1 else ""
            if kw == "if":
                self.pos += 1
                nodes.append(self.parse_if(rest))
                continue
            if kw == "for":
                self.pos += 1
                nodes.append(self.parse_for(rest))
                continue
            if kw in stop:
                self.pos += 1
                return nodes, kw, rest
            if kw in KEYWORDS:
                raise TemplateError("mismatch", "unexpected {%% %s %%}" % kw)
            raise TemplateError("syntax", "unknown tag %r" % kw)
        if stop:
            raise TemplateError("unclosed", "block not closed")
        return nodes, None, None

    def parse_if(self, rest):
        branches = []
        cond = parse_expr(rest)
        while True:
            body, kw, rest = self.block(("elif", "else", "endif"))
            branches.append((cond, body))
            if kw == "elif":
                cond = parse_expr(rest)
                continue
            if kw == "else":
                if rest:
                    raise TemplateError("syntax", "{% else %} takes no argument")
                cond = None
                continue
            if rest:
                raise TemplateError("syntax", "{% endif %} takes no argument")
            break
        return ("if", branches)

    def parse_for(self, rest):
        bits = rest.split(None, 2)
        if len(bits) != 3 or bits[1] != "in" or not _is_ident(bits[0]):
            raise TemplateError("syntax", "bad for header %r" % (rest,))
        name = bits[0]
        expr = parse_expr(bits[2])
        body, kw, tail = self.block(("empty", "endfor"))
        empty = None
        if kw == "empty":
            if tail:
                raise TemplateError("syntax", "{% empty %} takes no argument")
            empty, kw2, tail2 = self.block(("endfor",))
            if tail2:
                raise TemplateError("syntax", "{% endfor %} takes no argument")
        elif tail:
            raise TemplateError("syntax", "{% endfor %} takes no argument")
        return ("for", name, expr, body, empty)


# ------------------------------------------------------------------ renderer

def _lookup(segs, ctx):
    cur = ctx
    for seg in segs:
        if isinstance(cur, dict):
            if seg in cur:
                cur = cur[seg]
                continue
            return ""
        if isinstance(cur, (list, tuple)) and _all_digits(seg):
            idx = int(seg)
            if 0 <= idx < len(cur):
                cur = cur[idx]
                continue
            return ""
        return ""
    return cur


def _apply(expr, ctx):
    (kind, val), filters = expr
    if kind == "path":
        v = _lookup(val, ctx)
    else:
        v = val
    # Determine escaping mode: the last raw/esc filter in the pipeline decides
    mode = "esc"  # Default to escaping ON
    for f in filters:
        if f == "raw":
            mode = "raw"
        elif f == "esc":
            mode = "esc"
    # Now apply all filters
    for f in filters:
        if f == "raw" or f == "esc":
            pass
        elif f == "upper":
            if not isinstance(v, str):
                raise TemplateError("type", "upper needs a string")
            v = v.upper()
        elif f == "lower":
            if not isinstance(v, str):
                raise TemplateError("type", "lower needs a string")
            v = v.lower()
        elif f == "len":
            if not isinstance(v, (str, list, tuple, dict)):
                raise TemplateError("type", "len needs a sized value")
            v = len(v)
        else:
            raise TemplateError("filter", "unknown filter %r" % (f,))
    return v, mode


def _escape(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    return s


def _tostr(v):
    if isinstance(v, str):
        return v
    if isinstance(v, int):
        return str(v)
    raise TemplateError("type", "cannot render %s" % type(v).__name__)


def _run(nodes, ctx, out):
    for nd in nodes:
        t = nd[0]
        if t == "text":
            out.append(nd[1])
        elif t == "var":
            v, mode = _apply((nd[1], nd[2]), ctx)
            s = _tostr(v)
            out.append(_escape(s) if mode == "esc" else s)
        elif t == "if":
            for cond, body in nd[1]:
                if cond is None:
                    _run(body, ctx, out)
                    break
                v, _m = _apply(cond, ctx)
                if v:
                    _run(body, ctx, out)
                    break
        else:
            _run_for(nd, ctx, out)


def _run_for(nd, ctx, out):
    _t, name, expr, body, empty = nd
    it, _m = _apply(expr, ctx)
    if isinstance(it, str) and not it:
        it = []
    if not isinstance(it, (list, tuple)):
        raise TemplateError("type", "cannot iterate %s" % type(it).__name__)
    # Save old values to restore after loop
    _MISSING = object()
    old_name_val = ctx.get(name, _MISSING)
    old_loop_val = ctx.get("loop", _MISSING)
    try:
        if len(it) == 0:
            if empty is not None:
                _run(empty, ctx, out)
        else:
            total = len(it)
            for i, item in enumerate(it):
                ctx[name] = item
                ctx["loop"] = {"index": i + 1, "index0": i,
                               "first": i == 0, "last": i == total - 1}
                _run(body, ctx, out)
    finally:
        # Restore old values
        if old_name_val is _MISSING:
            ctx.pop(name, None)
        else:
            ctx[name] = old_name_val
        if old_loop_val is _MISSING:
            ctx.pop("loop", None)
        else:
            ctx["loop"] = old_loop_val


def render(text, ctx=None):
    if ctx is None:
        ctx = {}
    nodes = _Parser(tlex.tokenize(text)).parse()
    out = []
    _run(nodes, ctx, out)
    return "".join(out)
