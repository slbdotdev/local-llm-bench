def diff(a, b):
    n, m = len(a), len(b)
    # L[i][j] = LCS length of a[i:], b[j:]
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            L[i][j] = L[i + 1][j + 1] + 1 if a[i] == b[j] else max(L[i + 1][j], L[i][j + 1])
    out = []; i = j = 0
    while i < n and j < m:
        if a[i] == b[j]:
            out.append(("=", a[i])); i += 1; j += 1
        elif L[i + 1][j] >= L[i][j + 1]:
            out.append(("-", a[i])); i += 1
        else:
            out.append(("+", b[j])); j += 1
    while i < n: out.append(("-", a[i])); i += 1
    while j < m: out.append(("+", b[j])); j += 1
    return out


def apply(a, script):
    i = 0; out = []
    for op, line in script:
        if op in ("=", "-"):
            if i >= len(a) or a[i] != line: raise ValueError("script does not match input")
            if op == "=": out.append(line)
            i += 1
        elif op == "+":
            out.append(line)
        else:
            raise ValueError("bad op")
    if i != len(a): raise ValueError("leftover lines")
    return out
