"""Reference: gitignore-style path matcher (pure string semantics)."""


class RuleError(Exception):
    pass


def _rstrip(line):
    while line.endswith(" "):
        i = len(line) - 2
        n = 0
        while i >= 0 and line[i] == "\\":
            n += 1
            i -= 1
        if n % 2:
            break
        line = line[:-1]
    return line


def _parse_class(line, i, toks):
    j = i + 1
    neg = j < len(line) and line[j] == "!"
    if neg:
        j += 1
    members = []
    first = True
    closed = False
    while j < len(line):
        if line[j] == "]" and not first:
            j += 1
            closed = True
            break
        if line[j] == "\\":
            if j + 1 >= len(line):
                raise RuleError("trailing backslash")
            ch = line[j + 1]
            j += 2
            esc = True
        else:
            ch = line[j]
            j += 1
            esc = False
        if not esc and j < len(line) and line[j] == "-" and line[j + 1 : j + 2] not in ("", "]"):
            j += 1
            if line[j] == "\\":
                if j + 1 >= len(line):
                    raise RuleError("trailing backslash")
                hi = line[j + 1]
                j += 2
            else:
                hi = line[j]
                j += 1
            members.append((ch, hi))
        else:
            members.append(ch)
        first = False
    if not closed:
        raise RuleError("unterminated character class")
    toks.append(("cls", neg, tuple(members)))
    return j


def _parse(line):
    segs = [[]]
    i = 0
    while i < len(line):
        c = line[i]
        if c == "\\":
            if i + 1 >= len(line):
                raise RuleError("trailing backslash")
            segs[-1].append(("lit", line[i + 1]))
            i += 2
        elif c == "/":
            segs.append([])
            i += 1
        elif c == "[":
            i = _parse_class(line, i, segs[-1])
        elif c == "*":
            segs[-1].append(("star",))
            i += 1
        elif c == "?":
            segs[-1].append(("q",))
            i += 1
        else:
            segs[-1].append(("lit", c))
            i += 1
    return segs


class _Rule:
    __slots__ = ("neg", "dir_only", "anchored", "segs")

    def __init__(self, neg, dir_only, anchored, segs):
        self.neg = neg
        self.dir_only = dir_only
        self.anchored = anchored
        self.segs = segs


def _compile(line):
    line = _rstrip(line)
    if not line or line.startswith("#"):
        return None
    neg = line.startswith("!")
    if neg:
        line = line[1:]
    dir_only = line.endswith("/")
    if dir_only:
        line = line[:-1]
    anchored = line.startswith("/")
    if anchored:
        line = line.lstrip("/")
    anchored = anchored or "/" in line
    return _Rule(neg, dir_only, anchored, _parse(line))


def compile_rules(lines):
    rules = []
    for line in lines:
        r = _compile(line)
        if r is not None:
            rules.append(r)
    return rules


def _cls_match(neg, members, c):
    for m in members:
        if isinstance(m, tuple):
            if m[0] <= c <= m[1]:
                return not neg
        elif m == c:
            return not neg
    return neg


def _seg_match(toks, s, i=0, k=0):
    while True:
        if i == len(toks):
            return k == len(s)
        t = toks[i]
        if t[0] == "star":
            return any(_seg_match(toks, s, i + 1, nk) for nk in range(k, len(s) + 1))
        if k >= len(s):
            return False
        if t[0] == "lit":
            if s[k] != t[1]:
                return False
        elif t[0] == "q":
            pass
        else:
            if not _cls_match(t[1], t[2], s[k]):
                return False
        k += 1
        i += 1


def _is_dstar(toks):
    return len(toks) == 2 and toks[0] == ("star",) and toks[1] == ("star",)


def _segs_match(segs, comps):
    if not segs:
        return not comps
    if _is_dstar(segs[0]):
        return any(_segs_match(segs[1:], comps[i:]) for i in range(len(comps) + 1))
    if not comps:
        return False
    return _seg_match(segs[0], comps[0]) and _segs_match(segs[1:], comps[1:])


def _rule_match(rule, comps, is_dir):
    if rule.dir_only and not is_dir:
        return False
    if rule.anchored:
        return _segs_match(rule.segs, comps)
    return any(_seg_match(rule.segs[0], c) for c in comps)


def is_ignored(path, rules):
    is_dir = path.endswith("/")
    comps = (path[:-1] if is_dir else path).split("/")
    return _ignored(comps, is_dir, rules)


def _ignored(comps, is_dir, rules):
    if len(comps) > 1 and _ignored(comps[:-1], True, rules):
        return True
    result = False
    for r in rules:
        if _rule_match(r, comps, is_dir):
            result = not r.neg
    return result
