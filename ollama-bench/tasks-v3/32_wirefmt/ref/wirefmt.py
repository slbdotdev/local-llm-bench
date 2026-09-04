"""A small nested-string wire format: encode / decode / canon."""
import re

MAX_DEPTH = 200
_HEX = "0123456789abcdefABCDEF"


class WireError(ValueError):
    def __init__(self, kind, pos):
        ValueError.__init__(self, "%s at %d" % (kind, pos))
        self.kind = kind
        self.pos = pos


# ---------------------------------------------------------------- encode
_TT = {ord("\\"): "\\\\"}
for _c in "(),~":
    _TT[ord(_c)] = "\\" + _c
for _n in list(range(0x20)) + [0x7F]:
    _TT[_n] = "\\x%02x" % _n


def encode(value, _depth=0):
    if isinstance(value, str):
        return value.translate(_TT) or "~"
    if isinstance(value, list):
        if _depth >= MAX_DEPTH:
            raise WireError("depth", 0)
        d = _depth + 1
        return "(" + ",".join(encode(v, d) for v in value) + ")"
    raise WireError("type", 0)


# ---------------------------------------------------------------- decode
_ORD = re.compile(r"[^\\,)~]*")


def _atom(text, i):
    n = len(text)
    start = i
    out = []
    while i < n:
        m = _ORD.match(text, i)
        if m.end() > i:
            out.append(text[i:m.end()])
            i = m.end()
            if i >= n:
                break
        c = text[i]
        if c == "," or c == ")":
            break
        if c == "\\":
            j = i + 1
            if j < n and text[j] == "x":
                h = text[j + 1:j + 3]
                if len(h) == 2 and h[0] in _HEX and h[1] in _HEX:
                    out.append(chr(int(h, 16)))
                    i = j + 3
                    continue
                raise WireError("escape", i)
            if j < n and " " <= text[j] <= "~":
                out.append(text[j])
                i = j + 1
                continue
            raise WireError("escape", i)
        # c == '~'
        if i == start and (i + 1 >= n or text[i + 1] in ",)"):
            return "", i + 1
        raise WireError("tilde", i)
    return "".join(out), i


def decode(text):
    n = len(text)
    i = 0
    stack = []
    value = None
    want_value = True
    while True:
        if want_value:
            if i >= n:
                raise WireError("empty", i)
            c = text[i]
            if c == "(":
                if len(stack) >= MAX_DEPTH:
                    raise WireError("depth", i)
                if i + 1 < n and text[i + 1] == ")":
                    value = []
                    i += 2
                    want_value = False
                    continue
                stack.append([])
                i += 1
                continue
            if c == "," or c == ")":
                raise WireError("empty", i)
            value, i = _atom(text, i)
            want_value = False
            continue
        if stack:
            if i >= n:
                raise WireError("unterminated", n)
            c = text[i]
            if c == ",":
                stack[-1].append(value)
                i += 1
                want_value = True
            elif c == ")":
                stack[-1].append(value)
                value = stack.pop()
                i += 1
            else:
                raise WireError("trailing", i)
            continue
        if i >= n:
            return value
        if text[i] == "," or text[i] == ")":
            raise WireError("delim", i)
        raise WireError("trailing", i)


def canon(text):
    return encode(decode(text))
