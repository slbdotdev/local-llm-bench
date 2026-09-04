"""Hidden grader for 23_glob: gitignore-style path matcher."""
import sys, random, re

fails = []


def check(name, cond):
    if not cond:
        fails.append(name)


# ---------------- differential reference (structured rules, no text parsing) ----------
DSTAR = ("dstar",)


def tok_re(t):
    if t[0] == "lit":
        return re.escape(t[1])
    if t[0] in ("star", "dstar"):
        return ".*"
    if t[0] == "q":
        return "."
    inner = ""
    for m in t[2]:
        if isinstance(m, tuple):
            inner += re.escape(m[0]) + "-" + re.escape(m[1])
        else:
            inner += re.escape(m)
    return "[" + ("^" if t[1] else "") + inner + "]"


def compile_ref_rule(r):
    pats = []
    for seg in r["segs"]:
        if len(seg) == 1 and seg[0][0] == "dstar":
            pats.append(DSTAR)
        else:
            pats.append(re.compile("".join(tok_re(t) for t in seg)))
    return (r["neg"], r["dir_only"], r["anchored"], pats)


def segs_match(pats, comps):
    if not pats:
        return not comps
    if pats[0] == DSTAR:
        return any(segs_match(pats[1:], comps[i:]) for i in range(len(comps) + 1))
    if not comps:
        return False
    return pats[0].fullmatch(comps[0]) is not None and segs_match(pats[1:], comps[1:])


def rmatch(rule, comps, is_dir):
    neg, dir_only, anchored, pats = rule
    if dir_only and not is_dir:
        return False
    if anchored:
        return segs_match(pats, comps)
    p0 = pats[0]
    if p0 == DSTAR:
        return True
    return any(p0.fullmatch(c) is not None for c in comps)


def ref_ignored(comps, is_dir, rules):
    if len(comps) > 1 and ref_ignored(comps[:-1], True, rules):
        return True
    res = False
    for r in rules:
        if rmatch(r, comps, is_dir):
            res = not r[0]
    return res


# ---------------- random rule / path generation ----------------
def gen_token():
    r = random.random()
    if r < 0.30:
        return ("lit", random.choice("abfo.x-t_ #!*[]\\"))
    if r < 0.45:
        return ("star",)
    if r < 0.60:
        return ("q",)
    neg = random.random() < 0.3
    members = []
    for _ in range(random.randint(1, 3)):
        if random.random() < 0.25:
            lo, hi = sorted(random.sample("abcxyz0259", 2))
            members.append((lo, hi))
        else:
            members.append(random.choice("abx-]!\\^0"))
    return ("cls", neg, tuple(members))


def gen_seg():
    if random.random() < 0.12:
        return [("dstar",)]
    n = random.randint(1, 3)
    toks = [gen_token() for _ in range(n)]
    if n == 2 and toks[0] == ("star",) and toks[1] == ("star",):
        toks = [("q",)]
    return toks


def gen_rule():
    nseg = random.randint(1, 3)
    segs = [gen_seg() for _ in range(nseg)]
    return {
        "neg": random.random() < 0.25,
        "dir_only": random.random() < 0.3,
        "anchored": nseg > 1 or random.random() < 0.3,
        "segs": segs,
    }


def render_tok(t):
    if t[0] == "dstar":
        return "**"
    if t[0] == "star":
        return "*"
    if t[0] == "q":
        return "?"
    if t[0] == "lit":
        return "".join("\\" + ch if ch in '*?[]\\!# -' else ch for ch in t[1])
    s = "[" + ("!" if t[1] else "")
    for m in t[2]:
        if isinstance(m, tuple):
            s += m[0] + "-" + m[1]
        else:
            s += "\\" + m if m in "\\]-!^" else m
    return s + "]"


def render_rule(r):
    body = "/".join("".join(render_tok(t) for t in seg) for seg in r["segs"])
    if r["anchored"] and len(r["segs"]) == 1:
        body = "/" + body
    if r["dir_only"]:
        body += "/"
    return ("!" if r["neg"] else "") + body


NAMES = ["a", "b", "x.txt", "foo", "build", "keep.log", "c.o", "d e", "!w", "#h",
         ".hid", "[br]", "q?", "st*", "back\\slash", "z"]


def gen_path():
    comps = [random.choice(NAMES) for _ in range(random.randint(1, 4))]
    return comps, random.random() < 0.35


# ---------------- main ----------------
def main():
    import globmatch

    C = globmatch.compile_rules
    I = globmatch.is_ignored
    check("RuleError defined", hasattr(globmatch, "RuleError")
          and issubclass(globmatch.RuleError, Exception))
    RuleError = globmatch.RuleError

    CASES = [
        # plain literals, unanchored matches any component at any depth
        (["foo"], "foo", True), (["foo"], "a/foo", True), (["foo"], "a/b/foo", True),
        (["foo"], "a/foo/b", True), (["foo"], "foobar", False),
        (["foo"], "a/foobar", False), (["foo"], "fo", False),
        # star / qmark
        (["*.txt"], "a.txt", True), (["*.txt"], "x/y.txt", True),
        (["*.txt"], "x.txt.bak", False), (["*.txt"], ".txt", True),
        (["*"], "anything", True), (["*"], "a/b", True),
        (["a*c"], "ac", True), (["a*c"], "abbbc", True), (["a*c"], "ab", False),
        (["f?o"], "foo", True), (["f?o"], "fxo", True), (["f?o"], "fo", False),
        (["?"], "a", True), (["?"], "ab", False),
        (["a?c"], "abc", True), (["a?c"], "ac", False),
        # ** segments
        (["**/x"], "x", True), (["**/x"], "a/x", True), (["**/x"], "a/b/x", True),
        (["**/x"], "a/x/b", True),  # dir a/x is matched, so everything under it too
        (["**/x"], "a/xy", False),
        (["a/**/b"], "a/b", True), (["a/**/b"], "a/x/b", True),
        (["a/**/b"], "a/x/y/b", True), (["a/**/b"], "a/xb", False),
        (["a/**/b"], "x/a/b", False),
        (["a/**"], "a", True), (["a/**"], "a/b/c", True), (["a/**"], "ab", False),
        (["**"], "a/b/c", True),
        (["**/a/**"], "a", True), (["**/a/**"], "x/a/y/z", True),
        (["**/a/**"], "b", False),
        # anchoring
        (["/foo"], "foo", True), (["/foo"], "a/foo", False),
        (["//foo"], "foo", True), (["//foo"], "a/foo", False),
        (["foo/bar"], "foo/bar", True), (["foo/bar"], "x/foo/bar", False),
        (["foo/bar"], "foo/bar/baz", True),  # dir foo/bar matched -> contents ignored
        (["/a/b"], "a/b", True), (["/a/b"], "b", False),
        # directory-only rules
        (["build/"], "build", False), (["build/"], "build/", True),
        (["build/"], "build/x", True), (["build/"], "build/x/y", True),
        (["build/"], "x/build", False), (["build/"], "x/build/y", True),
        (["build/"], "building", False),
        (["a/b/"], "a/b", False), (["a/b/"], "a/b/", True), (["a/b/"], "a/b/c", True),
        (["/build/"], "build/", True), (["/build/"], "x/build/", False),
        (["*/"], "a/b/", True), (["*/"], "a/b", True), (["*/"], "a", False),
        (["*/"], "a/b/c", True),
        (["b/"], "a/b/c/d", True), (["a/b/"], "a/b/c/d", True),
        # negation and ordering (last matching rule wins)
        (["*.log", "!keep.log"], "keep.log", False),
        (["*.log", "!keep.log"], "other.log", True),
        (["!keep.log", "*.log"], "keep.log", True),
        (["*.log", "!keep*"], "keep.log", False),
        (["*.o", "!main.o"], "src/main.o", False),
        (["*.o", "!main.o"], "src/other.o", True),
        (["build/*.tmp", "!build/x.tmp"], "build/x.tmp", False),
        (["build/*.tmp", "!build/x.tmp"], "build/y.tmp", True),
        (["build/", "!build/keep.txt"], "build/keep.txt", True),
        (["build/", "!build"], "build/x", False),
        (["!x", "x"], "x", True), (["x", "!x"], "x", False),
        # comments and blank lines
        ([""], "foo", False), (["   "], "foo", False),
        (["#doc"], "#doc", False), (["\\#doc"], "#doc", True),
        (["\\#doc"], "doc", False),
        ([" #x"], " #x", True), ([" #x"], "#x", False),
        (["  ", "#c", "", "foo"], "foo", True),
        (["!"], "x", False), (["/"], "x", False), (["/"], "x/", False),
        # trailing spaces and escapes
        (["foo   "], "foo", True),
        (["foo\\ "], "foo ", True), (["foo\\ "], "foo", False),
        (["foo \\ "], "foo  ", True), (["foo \\ "], "foo ", False),
        (["\\*.c"], "*.c", True), (["\\*.c"], "x.c", False),
        (["\\?x"], "?x", True), (["\\?x"], "ax", False),
        (["a\\\\b"], "a\\b", True), (["a\\\\b"], "ab", False),
        (["\\[a]"], "[a]", True), (["\\[a]"], "a", False),
        (["\\!x"], "!x", True), (["\\!x"], "x", False),
        (["a\\/b"], "a/b", False),
        # character classes
        (["[abc]"], "b", True), (["[abc]"], "d", False), (["[abc]"], "ab", False),
        (["[a-z]"], "q", True), (["[a-z]"], "Q", False),
        (["[a-cx]"], "x", True), (["[a-cx]"], "d", False), (["[a-cx]"], "b", True),
        (["[a-cx0-9]"], "7", True), (["[a-cx0-9]"], "d", False),
        (["[0-9]"], "5", True),
        (["[!abc]"], "d", True), (["[!abc]"], "a", False), (["[!abc]"], "ab", False),
        (["[!a-z]"], "Q", True),
        (["[]x]"], "]", True), (["[]x]"], "x", True), (["[]x]"], "a", False),
        (["[-a]"], "-", True), (["[-a]"], "a", True), (["[-a]"], "b", False),
        (["[a-]"], "-", True), (["[a-]"], "a", True),
        (["[\\]]"], "]", True), (["[\\]]"], "[", False),
        (["[z-a]"], "y", False), (["[z-a]"], "z", False), (["[z-ab]"], "b", True),
        (["[!]]"], "a", True), (["[!]]"], "]", False),
        (["[a!b]"], "!", True), (["[a!b]"], "a", True), (["[a!b]"], "c", False),
        (["[^a]"], "^", True), (["[^a]"], "b", False),
        (["[a\\-z]"], "-", True), (["[a\\-z]"], "b", False),
        (["x[0-9]y"], "x7y", True), (["x[0-9]y"], "x7y", True),
        (["[a-z]*[0-9]"], "abc-x9", True),
    ]
    for lines, path, want in CASES:
        try:
            rules = C(lines)
            got = I(path, rules)
            check(f"cases {lines} vs {path!r} -> {got}", got == want)
        except Exception as e:
            fails.append(f"cases {lines} vs {path!r} raised {e!r}")

    # compile_rules must accept any iterable
    try:
        check("iterable input", I("foo", C(iter(["#c", "foo"]))) == True)
        check("empty rules", I("a/b", C([])) == False)
        check("comment-only rules", I("a/b", C(iter(["#x", "  "]))) == False)
    except Exception as e:
        fails.append(f"iterable input raised {e!r}")

    # valid but tricky patterns must not raise
    try:
        C(["\\[", "[\\]]", "[]x]", "[!]]", "[a-]", "[-a]", "[a\\-z]", "[^a]",
           "\\!x", "\\#x", "foo\\ ", "a\\\\b", "!a/b/", "**/x", "a/**"])
    except Exception as e:
        fails.append(f"valid patterns raised {e!r}: {e}")

    # invalid patterns raise RuleError at compile time
    for bad in ["[", "[abc", "[]", "[!", "[!]", "a\\", "foo\\", "a[0-9\\", "[a-",
                "[!a", "x[y", "[a-", "  [abc  "]:
        try:
            C([bad])
            fails.append(f"no RuleError for {bad!r}")
        except RuleError:
            pass
        except Exception as e:
            fails.append(f"{bad!r} raised {type(e).__name__}, not RuleError")
    try:
        C(["ok", "[abc"])
        fails.append("no RuleError for bad line among good ones")
    except RuleError:
        pass
    except Exception as e:
        fails.append(f"bad line raised {type(e).__name__}, not RuleError")

    # seeded randomised differential test against the structured reference
    random.seed(23)
    nm = 0
    for _ in range(400):
        rules_struct = [gen_rule() for _ in range(random.randint(1, 4))]
        lines = [render_rule(r) for r in rules_struct]
        try:
            rules_agent = C(lines)
        except Exception as e:
            fails.append(f"rand compile {lines!r} raised {e!r}")
            continue
        rules_ref = [compile_ref_rule(r) for r in rules_struct]
        for _ in range(25):
            comps, is_dir = gen_path()
            path = "/".join(comps) + ("/" if is_dir else "")
            want = ref_ignored(comps, is_dir, rules_ref)
            try:
                got = I(path, rules_agent)
            except Exception as e:
                fails.append(f"rand {lines!r} path {path!r} raised {e!r}")
                break
            nm += 1
            if got != want:
                fails.append(f"rand rules={lines!r} path={path!r}: got {got} want {want}")
    check("enough random cases", nm > 8000)


try:
    main()
except Exception as e:
    import traceback
    fails.append("exception: " + traceback.format_exc(limit=3))

if fails:
    print("FAIL")
    for f in fails[:12]:
        print(" -", f)
    sys.exit(1)
print("PASS")
sys.exit(0)
