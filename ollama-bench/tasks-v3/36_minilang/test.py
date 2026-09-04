import os
import subprocess
import sys

TOTAL = 39
fails = []

ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
CWD = os.getcwd()


def check(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok = False
        name = "%s raised %s" % (name, type(e).__name__)
    if not ok:
        fails.append(name)


def report():
    n = max(0, min(TOTAL, TOTAL - len(fails)))
    print("SCORE %d/%d" % (n, TOTAL))
    if fails:
        print("FAIL", fails[:10])
        sys.exit(1)
    print("PASS")
    sys.exit(0)


PRELUDE = r'''
import minilang as M

R = getattr(M, "run", None)
E = getattr(M, "evaluate", None)
LE = getattr(M, "LangError", None)
LexE = getattr(M, "LexError", None)
ParseE = getattr(M, "ParseError", None)
NameE = getattr(M, "UndefinedNameError", None)
TypeE = getattr(M, "TypeMismatchError", None)
ZeroE = getattr(M, "DivideByZeroError", None)

NL = chr(10)
TAB = chr(9)
Q = chr(34)
BS = chr(92)


def ierr(fn, src, cls, kind, line, detail=None):
    try:
        fn(src)
        return False
    except BaseException as exc:
        e = exc
    if not (isinstance(cls, type) and isinstance(e, cls)):
        return False
    if not (isinstance(LE, type) and isinstance(e, LE)):
        return False
    if getattr(e, "kind", None) != kind:
        return False
    if getattr(e, "line", None) != line:
        return False
    pre = "%s error at line %d: " % (kind, line)
    s = str(e)
    if not s.startswith(pre) or len(s) <= len(pre):
        return False
    if detail is not None and s != pre + detail:
        return False
    return True


def isint(x):
    return type(x) is int


def isflt(x):
    return type(x) is float


'''


def sub(body, timeout=20):
    code = PRELUDE + body + "\nprint('__OK__')\n"

    def probe():
        try:
            r = subprocess.run([sys.executable, "-c", code], cwd=CWD,
                               capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=timeout, env=ENV)
        except Exception:
            return False
        return r.returncode == 0 and r.stdout.strip().endswith("__OK__")

    return probe


# ---- module must at least import ---------------------------------------
def _importable():
    try:
        r = subprocess.run([sys.executable, "-c", "import minilang"], cwd=CWD,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30, env=ENV)
    except Exception as e:
        return "could not run python: %r" % (e,)
    if r.returncode != 0:
        msg = (r.stderr or r.stdout).strip().splitlines()
        return (msg[-1] if msg else "no output")[:160]
    return None


_bad = _importable()
if _bad is not None:
    fails = ["import minilang failed: %s" % _bad] + ["not run"] * (TOTAL - 1)
    report()


# ---- 1: exception hierarchy --------------------------------------------
check("exception classes", sub(r'''
assert isinstance(LE, type) and issubclass(LE, Exception)
subs = [LexE, ParseE, NameE, TypeE, ZeroE]
for c in subs:
    assert isinstance(c, type) and issubclass(c, LE) and c is not LE
assert len(set(subs)) == 5
'''))

# ---- 2-9: lexing --------------------------------------------------------
check("empty programs and empty blocks", sub(r'''
assert R("") == []
assert R("   " + NL + TAB + NL) == []
assert R("# just a comment") == []
assert R("{}") == []
assert R("{ }" + NL + "{ { } }") == []
'''))

check("number literals", sub(r'''
assert E("42") == 42 and isint(E("42"))
assert E("3.5") == 3.5 and isflt(E("3.5"))
assert E("0") == 0 and E("007") == 7
assert E("0.25") == 0.25
assert R("print 42;" + NL + "print 3.5;" + NL + "print 0.25;") == ["42", "3.5", "0.25"]
'''))

check("string literals and escapes", sub(r'''
assert E('""') == ""
assert E('"hello world"') == "hello world"
assert E(r'"a\nb"') == "a" + NL + "b"
assert E(r'"a\tb"') == "a" + TAB + "b"
assert E(r'"a\\b"') == "a" + BS + "b"
assert E(r'"he said \"hi\""') == "he said " + Q + "hi" + Q
'''))

check("comments", sub(r'''
assert R("print 1; # print 999;" + NL + "print 3;") == ["1", "3"]
assert R("print 1;#c") == ["1"]
assert R("#") == []
assert R('print "# not a comment";') == ["# not a comment"]
'''))

check("lex error: unexpected character", sub(r'''
assert ierr(R, "print 1;" + NL + "print @;", LexE, "lex", 2, "unexpected character '@'")
assert ierr(E, "1 & 2", LexE, "lex", 1, "unexpected character '&'")
assert ierr(E, ".5", LexE, "lex", 1, "unexpected character '.'")
'''))

check("lex error: malformed number", sub(r'''
assert ierr(E, "1.", LexE, "lex", 1, "malformed number '1.'")
assert ierr(E, "12abc", LexE, "lex", 1, "malformed number '12abc'")
assert ierr(E, "1e5", LexE, "lex", 1, "malformed number '1e5'")
assert ierr(R, "print 1;" + NL + "print 1.2.3;", LexE, "lex", 2, "malformed number '1.2.3'")
'''))

check("lex error: unterminated string", sub(r'''
assert ierr(R, 'print "abc;' + NL + 'print 1;', LexE, "lex", 1, "unterminated string")
assert ierr(E, '"abc', LexE, "lex", 1, "unterminated string")
assert ierr(R, "print 1;" + NL + 'print "x' + NL + "print 2;", LexE, "lex", 2, "unterminated string")
'''))

check("lex error: invalid escape", sub(r'''
assert ierr(E, r'"a\qb"', LexE, "lex", 1, r"invalid escape '\q'")
assert ierr(R, "print 1;" + NL + r'print "\0";', LexE, "lex", 2, r"invalid escape '\0'")
assert E(r'"a\\nb"') == "a" + BS + "nb"
'''))

# ---- 10-14: precedence and associativity --------------------------------
check("arithmetic precedence and left associativity", sub(r'''
assert E("1 + 2 * 3") == 7
assert E("2 * 3 + 4") == 10
assert E("10 - 2 - 3") == 5
assert E("100 / 10 / 2") == 5.0
assert E("2 + 10 % 3") == 3
assert E("(1 + 2) * 3") == 9
assert E("7 % 4 % 2") == 1
assert E("1 - 2 + 3") == 2
'''))

check("** is right associative", sub(r'''
assert E("2 ** 3 ** 2") == 512
assert E("2 ** 2 ** 3") == 256
assert E("(2 ** 3) ** 2") == 64
'''))

check("unary minus vs **", sub(r'''
assert E("-2 ** 2") == -4
assert E("(-2) ** 2") == 4
assert E("2 ** -1") == 0.5
assert E("-2 ** -2") == -0.25
assert E("- -3") == 3
assert E("+ -3") == -3
assert E("-2 ** 2 ** 1") == -4
assert E("-3 * -3") == 9
'''))

check("not precedence", sub(r'''
assert E("not 1 == 2") is True
assert E("not true or true") is True
assert E("not (true or true)") is False
assert E("not not 0") is False
assert E("not 0") is True
assert E('not ""') is True
assert E("not 1") is False
'''))

check("and/or precedence", sub(r'''
assert E("true or false and false") is True
assert E("false and false or true") is True
assert E("1 or 2 and 3") == 1
assert E("0 or 2 and 3") == 3
assert E("true and false or true") is True
'''))

# ---- 15-17: parse errors ------------------------------------------------
check("comparison is non-associative", sub(r'''
assert E("1 < 2") is True
assert E("2 <= 2") is True
assert E("3 != 4") is True
assert E("(1 < 2) == true") is True
assert ierr(E, "1 < 2 < 3", ParseE, "parse", 1)
assert ierr(E, "1 == 2 != 3", ParseE, "parse", 1)
assert ierr(R, "print 1;" + NL + "print 1 < 2 > 3;", ParseE, "parse", 2)
'''))

check("assorted parse errors", sub(r'''
bad = ["print 1", "print (1;", "let 1 = 2;", "let if = 1;", "x 1;", "print;",
       "{ print 1;", "print 1;;", "if (true)", "let x = ;", "while true {}",
       "let x = 1", "}", "1 + 1;"]
for s in bad:
    assert ierr(R, s, ParseE, "parse", 1), s
'''))

check("parse error line numbers", sub(r'''
assert ierr(R, "print 1;" + NL + "print 2" + NL + "print 3;", ParseE, "parse", 3)
assert ierr(R, "print 1;" + NL + ")", ParseE, "parse", 2)
assert ierr(R, "print 1;" + NL + "print (1 + 2;", ParseE, "parse", 2)
assert ierr(R, "print 1;" + NL + NL + "print", ParseE, "parse", 3)
'''))

# ---- 18-20: output rendering -------------------------------------------
check("int and float rendering", sub(r'''
assert R("print 4 / 2;") == ["2.0"]
assert R("print 1 / 3;") == ["0.3333333333333333"]
assert R("print 7;" + NL + "print -7;" + NL + "print 1000000;") == ["7", "-7", "1000000"]
assert R("print 2.0; print 0.5; print -0.25;") == ["2.0", "0.5", "-0.25"]
assert R("print 2 ** 100;") == [str(2 ** 100)]
'''))

check("bool rendering", sub(r'''
assert R("print true; print false; print not 0; print 1 == 1.0;") == ["true", "false", "true", "true"]
assert R("print 1 < 2; print 1 > 2;") == ["true", "false"]
'''))

check("string rendering and string operators", sub(r'''
assert R('print "hi"; print "";') == ["hi", ""]
assert R(r'print "a\tb";') == ["a" + TAB + "b"]
assert E('"a" + "b"') == "ab"
assert E('"abc" < "abd"') is True
assert E('"B" < "a"') is True
assert E('"a" <= "a"') is True
assert R('print "a" + "b" + "c";') == ["abc"]
'''))

# ---- 21-26: types ------------------------------------------------------
check("booleans are not numbers", sub(r'''
assert ierr(E, "true + 1", TypeE, "type", 1)
assert ierr(E, "true * true", TypeE, "type", 1)
assert ierr(E, "false - 1", TypeE, "type", 1)
assert ierr(E, "- true", TypeE, "type", 1)
assert ierr(E, "true < false", TypeE, "type", 1)
assert ierr(E, "true ** 2", TypeE, "type", 1)
assert E("true == true") is True
'''))

check("mixed-type operands are type errors", sub(r'''
assert ierr(E, '"x" + 1', TypeE, "type", 1)
assert ierr(E, '1 + "x"', TypeE, "type", 1)
assert ierr(E, '"a" < 1', TypeE, "type", 1)
assert ierr(E, '"a" * 2', TypeE, "type", 1)
assert ierr(E, '- "a"', TypeE, "type", 1)
assert ierr(E, '"a" >= true', TypeE, "type", 1)
assert ierr(R, "print 1;" + NL + 'print "a" - "b";', TypeE, "type", 2)
'''))

check("== and != accept any two values", sub(r'''
assert E('1 == "1"') is False
assert E("true == 1") is False
assert E("false == 0") is False
assert E("1 == 1.0") is True
assert E("1 != 1.0") is False
assert E('"a" != "b"') is True
assert E('"" == false') is False
assert E("true != 1") is True
assert E('"a" == "a"') is True
'''))

check("result types of * / %", sub(r'''
assert isint(E("2 * 3")) and E("2 * 3") == 6
assert isflt(E("2.0 * 3")) and E("2.0 * 3") == 6.0
assert isflt(E("7 / 2")) and E("7 / 2") == 3.5
assert isflt(E("4 / 2"))
assert isint(E("7 % 3")) and E("7 % 3") == 1
assert E("-7 % 3") == 2
assert E("7 % -3") == -2
assert isflt(E("7.0 % 3")) and E("7.0 % 3") == 1.0
'''))

check("result types of **", sub(r'''
assert isint(E("2 ** 3")) and E("2 ** 3") == 8
assert isint(E("2 ** 0")) and E("2 ** 0") == 1
assert isflt(E("2 ** -1")) and E("2 ** -1") == 0.5
assert isflt(E("2.0 ** 2")) and E("2.0 ** 2") == 4.0
assert isflt(E("9 ** 0.5")) and E("9 ** 0.5") == 3.0
assert isflt(E("2 ** -2")) and E("2 ** -2") == 0.25
'''))

check("division and modulo by zero", sub(r'''
assert ierr(E, "1 / 0", ZeroE, "zero", 1)
assert ierr(E, "1 / 0.0", ZeroE, "zero", 1)
assert ierr(E, "1 % 0", ZeroE, "zero", 1)
assert ierr(E, "0 ** -1", ZeroE, "zero", 1)
assert ierr(E, "0.0 ** -1", ZeroE, "zero", 1)
assert ierr(R, "print 1;" + NL + "print 5 / 0;", ZeroE, "zero", 2)
assert E("0 ** 0") == 1
'''))

# ---- 27-30: scoping ----------------------------------------------------
check("blocks shadow and let sees the outer value", sub(r'''
assert R("let x = 1;" + NL + "{ let x = x + 10; print x; }" + NL + "print x;") == ["11", "1"]
assert R("let x = 1; { let x = 2; { let x = 3; print x; } print x; } print x;") == ["3", "2", "1"]
assert R('let s = "a"; { let s = s + s; print s; } print s;') == ["aa", "a"]
'''))

check("assignment targets the nearest declaring scope", sub(r'''
assert R("let x = 1;" + NL + "{ x = 5; }" + NL + "print x;") == ["5"]
assert R("let x = 1; { { { x = 7; } } } print x;") == ["7"]
assert R("let x = 1; { let x = 2; x = 3; print x; } print x;") == ["3", "1"]
'''))

check("undefined variable errors", sub(r'''
assert ierr(R, "print zzz;", NameE, "name", 1, "undefined variable 'zzz'")
assert ierr(R, "zzz = 1;", NameE, "name", 1, "undefined variable 'zzz'")
assert ierr(R, "{ let q = 1; }" + NL + "print q;", NameE, "name", 2, "undefined variable 'q'")
assert ierr(R, "print 1;" + NL + "let y = 2;" + NL + "print y + w;", NameE, "name", 3, "undefined variable 'w'")
'''))

check("duplicate declaration errors", sub(r'''
assert ierr(R, "let x = 1;" + NL + "let x = 2;", NameE, "name", 2, "duplicate declaration 'x'")
assert R("let x = 1; { let x = 2; } print x;") == ["1"]
src = "let x = 1;" + NL + "{" + NL + "let x = 2;" + NL + "let x = 3;" + NL + "}"
assert ierr(R, src, NameE, "name", 4, "duplicate declaration 'x'")
'''))

# ---- 31-32: short circuiting -------------------------------------------
check("short-circuit skips errors in the dead operand", sub(r'''
assert E("false and zzz") is False
assert E("true or zzz") is True
assert E("true or (1 / 0)") is True
assert E("false and (1 / 0)") is False
assert E("0 and (true + 1)") == 0
assert E('"" or "b"') == "b"
assert E('"x" or zzz') == "x"
'''))

check("and/or return an operand", sub(r'''
assert E("1 and 2") == 2 and isint(E("1 and 2"))
assert E('0 or "z"') == "z"
assert E('"" or 0') == 0 and isint(E('"" or 0'))
assert E("2 and 0") == 0
assert E("false or false") is False
assert E("1.5 and 0.0") == 0.0
assert E("true and 3") == 3
assert E("0.0 or 5") == 5
'''))

# ---- 33-34: error precedence -------------------------------------------
check("lex errors beat parse errors", sub(r'''
assert ierr(R, "print ;" + NL + "print @;", LexE, "lex", 2, "unexpected character '@'")
assert ierr(R, "let = 1;" + NL + "#" + NL + "print 1.;", LexE, "lex", 3, "malformed number '1.'")
assert ierr(R, ")))" + NL + '"oops', LexE, "lex", 2, "unterminated string")
'''))

check("parse errors beat runtime errors", sub(r'''
assert ierr(R, "print zzz;" + NL + "print (;", ParseE, "parse", 2)
assert ierr(R, "print 1 / 0;" + NL + "print", ParseE, "parse", 2)
assert ierr(R, "print true + 1;" + NL + "1", ParseE, "parse", 2)
'''))

check("runtime errors happen left to right", sub(r'''
assert ierr(E, "zzz + (1 / 0)", NameE, "name", 1)
assert ierr(E, "(1 / 0) + zzz", ZeroE, "zero", 1)
assert ierr(E, '"a" + (1 / 0)', ZeroE, "zero", 1)
assert ierr(R, "print undefA;" + NL + "print 1 / 0;", NameE, "name", 1)
assert ierr(E, "(1 / 0) * (2 / 0)", ZeroE, "zero", 1)
'''))

# ---- 35-36: control flow -----------------------------------------------
check("if / else", sub(r'''
assert R("if (true) print 1; else print 2;") == ["1"]
assert R("if (false) print 1; else print 2;") == ["2"]
assert R("if (0) print 1; else print 2;") == ["2"]
assert R('if ("") print 1; else print 2;') == ["2"]
assert R('if ("x") print 1;') == ["1"]
assert R("if (true) if (false) print 1; else print 2;") == ["2"]
assert R("if (false) if (true) print 1; else print 2;") == []
assert R("if (false and (1 / 0)) print 1; else print 2;") == ["2"]
assert R("if (true) { let a = 5; print a; } print 9;") == ["5", "9"]
'''))

check("while loops", sub(r'''
src = 'let i = 0;' + NL + 'while (i < 3) { print i * 2; i = i + 1; }' + NL + 'print "done";'
assert R(src) == ["0", "2", "4", "done"]
assert R("let i = 0; while (false) { i = i + 1; } print i;") == ["0"]
src2 = "let i = 0; let s = 0; while (i < 5) { if (i % 2 == 0) { s = s + i; } i = i + 1; } print s;"
assert R(src2) == ["6"]
'''))

# ---- 37-38: performance ------------------------------------------------
check("performance: 40000 flat statements", sub(r'''
import time
parts = ["let a = 0;"]
for i in range(40000):
    parts.append("a = a + " + str(i % 7) + " * 2 - 1;")
parts.append("print a;")
src = NL.join(parts)
exp = 0
for i in range(40000):
    exp = exp + (i % 7) * 2 - 1
t = time.time()
out = R(src)
el = time.time() - t
assert out == [str(exp)], out[:3]
assert el < 6.0, el
''', timeout=40))

check("performance: 200000 loop iterations", sub(r'''
import time
src = ("let i = 0;" + NL + "let s = 0;" + NL
       + "while (i < 200000) { s = s + i % 7; i = i + 1; }" + NL + "print s;")
exp = 0
for i in range(200000):
    exp += i % 7
t = time.time()
out = R(src)
el = time.time() - t
assert out == [str(exp)], out
assert el < 6.0, el
''', timeout=40))

report()
