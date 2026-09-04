def _strip_comment(s):
    q = None
    for i, c in enumerate(s):
        if q:
            if c == q: q = None
        elif c in "\"'": q = c
        elif c == "#": return s[:i]
    return s


def tokenize(src):
    out = []; stack = [0]
    for raw in src.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        lead = line[: len(line) - len(line.lstrip())]
        if "\t" in lead: raise ValueError("tab in indentation")
        n = len(lead)
        if n > stack[-1]:
            stack.append(n); out.append(("INDENT", ""))
        else:
            while n < stack[-1]:
                stack.pop(); out.append(("DEDENT", ""))
            if n != stack[-1]: raise ValueError("inconsistent dedent")
        out.append(("LINE", _strip_comment(line.lstrip()).rstrip()))
    while len(stack) > 1:
        stack.pop(); out.append(("DEDENT", ""))
    out.append(("EOF", ""))
    return out
