import sys
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    from indent import tokenize as T
    L = lambda s: ("LINE", s); I = ("INDENT", ""); D = ("DEDENT", ""); E = ("EOF", "")
    check("example", T("a\n  b\n    c\n  d\ne\n") == [L("a"), I, L("b"), I, L("c"), D, L("d"), D, L("e"), E])
    check("empty", T("") == [E])
    check("only blank/comment", T("\n   \n# hi\n  # there\n") == [E])
    check("no trailing newline", T("a\n  b") == [L("a"), I, L("b"), D, E])
    check("double dedent at end", T("a\n b\n  c\n") == [L("a"), I, L("b"), I, L("c"), D, D, E])
    check("blank lines ignored", T("a\n\n  b\n\n\n  c\n") == [L("a"), I, L("b"), L("c"), D, E])
    check("comment line ignored mid-block", T("a\n  b\n# x\n  c\n") == [L("a"), I, L("b"), L("c"), D, E])
    check("inline comment stripped", T("x = 1  # set\n") == [L("x = 1"), E])
    check("hash in dquotes kept", T('s = "a#b"  # c\n') == [L('s = "a#b"'), E])
    check("hash in squotes kept", T("s = 'a#b' # c\n") == [L("s = 'a#b'"), E])
    check("trailing ws stripped", T("a   \n") == [L("a"), E])
    check("crlf", T("a\r\n  b\r\n") == [L("a"), I, L("b"), D, E])
    check("deep", T("a\n b\n  c\n   d\ne\n") == [L("a"), I, L("b"), I, L("c"), I, L("d"), D, D, D, L("e"), E])
    for bad in ["a\n    b\n  c\n", "a\n\tb\n", "  a\n b\n"]:
        try:
            T(bad); fails.append(f"no ValueError for {bad!r}")
        except ValueError:
            pass
    check("dedent to nonzero ok", T("a\n  b\n    c\n  d\n") == [L("a"), I, L("b"), I, L("c"), D, L("d"), D, E])
    check("first line indented", T("  a\n  b\nc\n") == [I, L("a"), L("b"), D, L("c"), E])
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
