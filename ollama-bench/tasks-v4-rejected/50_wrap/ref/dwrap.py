"""Unicode-aware display width, tab expansion, wrapping and truncation."""
import unicodedata

ZERO_WIDTH = frozenset(chr(0x200B) + chr(0x200C) + chr(0x200D) + chr(0xFEFF))


def char_width(ch):
    if unicodedata.combining(ch) != 0:
        return 0
    if ch in ZERO_WIDTH:
        return 0
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    return 1


def width(s):
    total = 0
    for ch in s:
        total += char_width(ch)
    return total


def clusters(s):
    out = []
    n = len(s)
    i = 0
    while i < n:
        j = i + 1
        while j < n:
            c = s[j]
            if unicodedata.combining(c) != 0 or c in ZERO_WIDTH:
                j += 1
                if c == chr(0x200D) and j < n:
                    j += 1
                continue
            break
        out.append(s[i:j])
        i = j
    return out


def _check_int(v, lo, what):
    if isinstance(v, bool) or not isinstance(v, int) or v < lo:
        raise ValueError("%s must be an int >= %d" % (what, lo))


def expand_tabs(s, tabsize=8):
    _check_int(tabsize, 1, "tabsize")
    out = []
    col = 0
    for ch in s:
        if ch == "\t":
            n = tabsize - (col % tabsize)
            out.append(" " * n)
            col += n
        elif ch == "\n":
            out.append(ch)
            col = 0
        else:
            out.append(ch)
            col += char_width(ch)
    return "".join(out)


def _pieces(seg):
    """Split one newline-free segment into (is_gap, list_of_clusters) pieces."""
    cl = clusters(seg)
    n = len(cl)
    pieces = []
    i = 0
    while i < n:
        if cl[i] == " ":
            j = i
            while j < n and cl[j] == " ":
                j += 1
            pieces.append((True, cl[i:j]))
            i = j
        else:
            cur = []
            while i < n and cl[i] != " ":
                cur.append(cl[i])
                if cl[i][0] == "-":
                    pieces.append((False, cur))
                    cur = []
                i += 1
            if cur:
                pieces.append((False, cur))
    return pieces


def _wrap_segment(seg, budget):
    lines = []
    cur = ""
    curw = 0
    held = ""
    for is_gap, cls in _pieces(seg):
        text = "".join(cls)
        if is_gap:
            if cur:
                held += text
            continue
        w = width(text)
        hw = width(held)
        if cur and curw + hw + w <= budget:
            cur += held + text
            curw += hw + w
            held = ""
            continue
        if cur:
            lines.append(cur)
            cur = ""
            curw = 0
            held = ""
        if w <= budget:
            cur = text
            curw = w
        else:
            chunk = ""
            chw = 0
            for c in cls:
                cw = width(c)
                if chunk and chw + cw > budget:
                    lines.append(chunk)
                    chunk = ""
                    chw = 0
                chunk += c
                chw += cw
            cur = chunk
            curw = chw
    if cur:
        lines.append(cur)
    if not lines:
        lines.append("")
    return lines


def wrap(text, budget, tabsize=8):
    _check_int(budget, 1, "budget")
    _check_int(tabsize, 1, "tabsize")
    expanded = expand_tabs(text, tabsize)
    out = []
    for seg in expanded.split("\n"):
        out.extend(_wrap_segment(seg, budget))
    return out


def truncate(s, budget, ellipsis=chr(0x2026)):
    _check_int(budget, 0, "budget")
    if width(s) <= budget:
        return s
    ew = width(ellipsis)
    if ew > budget:
        return ""
    room = budget - ew
    keep = []
    w = 0
    for c in clusters(s):
        cw = width(c)
        if w + cw > room:
            break
        keep.append(c)
        w += cw
    while keep and keep[-1] == " ":
        keep.pop()
    return "".join(keep) + ellipsis
