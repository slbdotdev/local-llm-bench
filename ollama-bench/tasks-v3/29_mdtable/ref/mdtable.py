"""Reference: pipe-table parser and canonical formatter."""

import re

_ALIGN = re.compile(r":?-+:?")


def _split_line(line):
    seg = line[1:-1]
    cells, cur, i = [], [], 0
    while i < len(seg):
        c = seg[i]
        if c == "\\" and i + 1 < len(seg):
            cur.append(c)
            cur.append(seg[i + 1])
            i += 2
        elif c == "|":
            cells.append("".join(cur))
            cur = []
            i += 1
        else:
            cur.append(c)
            i += 1
    cells.append("".join(cur))
    return cells


def _unescape(s):
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] in "|\\":
            out.append(s[i + 1])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def parse_table(text):
    lines = [ln for ln in text.split("\n") if ln.strip()]
    if not lines:
        return [], None
    parsed = []
    for ln in lines:
        ln = ln.strip()
        if not (ln.startswith("|") and ln.endswith("|")):
            raise ValueError("each line must start and end with |")
        parsed.append([_unescape(c.strip()) for c in _split_line(ln)])
    aligns = None
    rows = parsed
    if len(parsed) >= 2 and all(_ALIGN.fullmatch(c) for c in parsed[1]):
        aligns = []
        for c in parsed[1]:
            if c.startswith(":") and c.endswith(":"):
                aligns.append("center")
            elif c.endswith(":"):
                aligns.append("right")
            else:
                aligns.append("left")
        if len(aligns) != len(parsed[0]):
            raise ValueError("alignment row column count mismatch")
        rows = parsed[:1] + parsed[2:]
    ncols = len(parsed[0])
    if any(len(r) != ncols for r in rows):
        raise ValueError("ragged rows")
    return rows, aligns


def _escape(s):
    return s.replace("\\", "\\\\").replace("|", "\\|")


def format_table(rows, aligns=None):
    if not rows:
        return ""
    ncols = len(rows[0])
    if ncols < 1 or any(len(r) != ncols for r in rows):
        raise ValueError("ragged rows")
    if aligns is None:
        aligns = ["left"] * ncols
    if len(aligns) != ncols or any(a not in ("left", "right", "center") for a in aligns):
        raise ValueError("bad aligns")
    esc = [[_escape(c) for c in r] for r in rows]
    widths = [max(3, max(len(r[j]) for r in esc)) for j in range(ncols)]

    def pad(text, w, a):
        pad = w - len(text)
        if a == "left":
            return text + " " * pad
        if a == "right":
            return " " * pad + text
        left = pad // 2
        return " " * left + text + " " * (pad - left)

    out = []
    for r in esc:
        out.append("| " + " | ".join(pad(r[j], widths[j], aligns[j]) for j in range(ncols)) + " |")
    sep = []
    for j in range(ncols):
        w = widths[j]
        a = aligns[j]
        if a == "left":
            sep.append(":" + "-" * (w - 1))
        elif a == "right":
            sep.append("-" * (w - 1) + ":")
        else:
            sep.append(":" + "-" * (w - 2) + ":")
    out.insert(1, "| " + " | ".join(sep) + " |")
    return "\n".join(out)


def normalize(text):
    rows, aligns = parse_table(text)
    return format_table(rows, aligns)
