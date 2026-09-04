"""Reference: backtracking regex via continuation-passing matcher."""


class _P:
    def __init__(self, s):
        self.s = s; self.i = 0

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else None

    def take(self):
        c = self.peek()
        if c is None: raise ValueError("unexpected end")
        self.i += 1; return c

    def alt(self):
        branches = [self.seq()]
        while self.peek() == "|":
            self.take(); branches.append(self.seq())
        return ("alt", branches)

    def seq(self):
        items = []
        while self.peek() not in (None, "|", ")"):
            items.append(self.quant())
        return ("seq", items)

    def quant(self):
        a = self.atom()
        while self.peek() in ("*", "+", "?"):
            a = (self.take(), a)
        return a

    def atom(self):
        c = self.take()
        if c in "*+?": raise ValueError("nothing to repeat")
        if c == "(":
            inner = self.alt()
            if self.peek() != ")": raise ValueError("missing )")
            self.take(); return inner
        if c == ")": raise ValueError("unbalanced )")
        if c == "\\":
            return ("lit", self.take())
        if c == "[":
            neg = self.peek() == "^"
            if neg: self.take()
            items = []; first = True
            while True:
                ch = self.peek()
                if ch is None: raise ValueError("unterminated class")
                if ch == "]" and not first: self.take(); break
                self.take(); first = False
                if self.peek() == "-" and self.i + 1 < len(self.s) and self.s[self.i + 1] != "]":
                    self.take(); hi = self.take(); items.append((ch, hi))
                else:
                    items.append((ch, ch))
            return ("cls", neg, items)
        if c == ".": return ("any",)
        return ("lit", c)


def _m(node, text, pos, k):
    t = node[0]
    if t == "lit":
        return pos < len(text) and text[pos] == node[1] and k(pos + 1)
    if t == "any":
        return pos < len(text) and k(pos + 1)
    if t == "cls":
        if pos >= len(text): return False
        c = text[pos]; hit = any(lo <= c <= hi for lo, hi in node[2])
        return (hit != node[1]) and k(pos + 1)
    if t == "seq":
        def run(i, p):
            if i == len(node[1]): return k(p)
            return _m(node[1][i], text, p, lambda np: run(i + 1, np))
        return run(0, pos)
    if t == "alt":
        return any(_m(b, text, pos, k) for b in node[1])
    if t == "?":
        return _m(node[1], text, pos, k) or k(pos)
    if t == "*":
        def star(p):
            return _m(node[1], text, p, lambda np: np != p and star(np)) or k(p)
        return star(pos)
    if t == "+":
        def plus(p):
            return _m(node[1], text, p, lambda np: (np != p and plus(np)) or k(np))
        return plus(pos)
    raise ValueError(t)


def fullmatch(pattern, text):
    p = _P(pattern); tree = p.alt()
    if p.i != len(pattern): raise ValueError("unbalanced )")
    import sys
    sys.setrecursionlimit(max(10000, sys.getrecursionlimit()))
    return bool(_m(tree, text, 0, lambda e: e == len(text)))
