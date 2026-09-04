import sys, inspect
fails = []
def check(name, cond):
    if not cond: fails.append(name)
try:
    import csvlite
    src = inspect.getsource(csvlite)
    check("no csv module", "import csv\n" not in src and "from csv " not in src and "import csv " not in src)
    P = csvlite.parse
    check("simple", P("a,b,c\n1,2,3\n") == [["a", "b", "c"], ["1", "2", "3"]])
    check("no trailing nl", P("a,b\nc,d") == [["a", "b"], ["c", "d"]])
    check("crlf", P("a,b\r\nc,d\r\n") == [["a", "b"], ["c", "d"]])
    check("empty", P("") == [])
    check("empty fields", P("a,,b\n") == [["a", "", "b"]])
    check("only comma", P(",\n") == [["", ""]])
    check("quoted comma", P('"x,y",z\n') == [["x,y", "z"]])
    check("escaped quote", P('"say ""hi""",2\n') == [['say "hi"', "2"]])
    check("newline in quotes", P('"line1\nline2",b\nc,d\n') == [["line1\nline2", "b"], ["c", "d"]])
    check("spaces kept", P(" a , b \n") == [[" a ", " b "]])
    check("quoted empty", P('"",""\n') == [["", ""]])
    check("single field rows", P("a\nb\nc\n") == [["a"], ["b"], ["c"]])
    check("quoted crlf inside", P('"a\r\nb",c\r\n') == [["a\r\nb", "c"]])
    check("trailing comma", P("a,b,\n") == [["a", "b", ""]])
except Exception as e:
    fails.append(f"exception: {e!r}")
if fails:
    print("FAIL", fails[:10]); sys.exit(1)
print("PASS")
