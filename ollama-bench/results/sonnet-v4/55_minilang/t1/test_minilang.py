import sys
from minilang import run, MiniError


def ok(src, expected):
    got = run(src)
    assert got == expected and type(got) == type(expected), \
        "FAIL %r -> %r (expected %r, type %s vs %s)" % (src, got, expected, type(got), type(expected))
    print("OK", src, "->", got)


def err(src, kind):
    try:
        run(src)
    except MiniError as e:
        assert e.kind == kind, "FAIL %r -> kind %r (expected %r)" % (src, e.kind, kind)
        print("OK(err)", src, "->", e.kind)
        return
    raise AssertionError("FAIL %r did not raise (expected kind %r)" % (src, kind))


# Examples from spec
ok("1 + 2 * 3", 7)
ok("let x = 4 in x * x", 16)
ok("letrec f = fun n -> if n == 0 then 1 else n * f (n - 1) in f 5", 120)
ok('match {tag = "pt", x = 3} with | {tag = "pt", x = v} -> v + 1 | _ -> 0 end', 4)
ok("let r = ref 2 in r := !r + 3", 5)
err("{a = 1}.b", "no_field")

# Lexical
err("007", "parse")
err("01", "parse")
ok("0", 0)
ok("40", 40)
err("é", "parse")
err("", "parse")
err("   ", "parse")
err("1 ;", "parse")

# Strings
ok('""', "")
ok('"hello"', "hello")

# Reserved words
err("let end = 1 in end", "parse")
err("fun in -> 1", "parse")
err("{end = 1}", "parse")
err("_", "parse")
err("let _ = 1 in _", "parse")

# Precedence
ok("-1 * 2", -2)
ok("10 - 4 - 3", 3)
ok("2 * 3 % 4", 2)
ok('"a" ++ "b" ++ "c"', "abc")
err("1 < 2 < 3", "parse")
err("a == b == c", "parse")

# application precedence
ok("let f = fun x -> x + 1 in f 5", 6)
ok("let f = fun x -> fun y -> x + y in (f 1) 2", 3)
err("let f = fun x -> x in f let x = 1 in x", "parse")
err("let f = fun x -> x in f if true then 1 else 2", "parse")
ok("let f = fun x -> x + 1 in f -1", None) if False else None

def test_f_minus():
    try:
        v = run("let f = fun x -> x - 1 in f -1")
        print("f -1 gave", v)
    except MiniError as e:
        print("f -1 raised", e.kind)

test_f_minus()

# f -1 should be f - 1 (subtraction): f is not int, so type error
err("let f = fun x -> x in f -1", "type")

ok("let f = fun x -> fun y -> x + y in f 1 2", 3)

# division/modulo
ok("7 / 2", 3)
ok("-7 / 2", -3)
ok("7 / -2", -3)
ok("-7 / -2", 3)
ok("7 % 2", 1)
ok("-7 % 2", 1)
ok("7 % -2", -1)
ok("-7 % -2", -1)
err("1 / 0", "div_zero")
err("1 % 0", "div_zero")
err('"x" / 0', "type")
err("true + (1 / 0)", "div_zero")

# string repetition
ok('"ab" * 3', "ababab")
ok('"ab" * 0', "")
ok('"ab" * -2', "")
err('2 * "ab"', "type")

# concat
err('"n=" ++ 1 ++ "!"', "type")
ok('"n=" ++ (1 ++ "!")', None) if False else None
err('"n=" ++ (1 ++ "!")', "type")
ok('"x" ++ 1', "x1")
ok('"x" ++ -5', "x-5")
ok('"x" ++ true', "xtrue")
ok('"x" ++ false', "xfalse")
err('"x" ++ {}', "type")

# comparisons
ok("1 < 2", True)
ok('"a" < "b"', True)
err("1 < true", "type")
err('1 < "a"', "type")
ok("1 == 1", True)
ok("true == true", True)
err("1 == true", "type")
err('1 == "1"', "type")
ok("let r = ref 1 in r == r", True)
ok("let r = ref 1 in let s = ref 1 in r == s", False)
err("{} == {}", "type")

# refs
ok("let r = ref 5 in !r", 5)
ok("let r = ref 5 in (r := 10)", 10)
ok("let r = ref 5 in let _x = (r := 10) in !r", 10)
err("!5", "type")
err("5 := 6", "type")

# and/or short circuit
ok("false && (1/0 == 0)", False)
ok("true || (1/0 == 0)", True)
err("1 && true", "type")
err("true && 1", "type")
err("1 || true", "type")
ok("true || 1", True)

# if
ok("if true then 1 else (1/0)", 1)
ok("if false then (1/0) else 2", 2)
err("if 1 then 1 else 2", "type")

# let scoping
err("let x = x in x", "unbound")
ok("let x = 1 in let x = x + 1 in x", 2)

# letrec
ok("letrec a = 1 and b = a in b", 1)
err("letrec a = b and b = 1 in a", "uninit")
err("letrec a = 1 and a = 2 in a", "dup_binding")

# records
ok("{}.a", None) if False else None
err("{}.a", "no_field")
err("{a = 1, a = 2}", "dup_field")
ok('{a = 1, b = 2}', {"a": 1, "b": 2})
ok("let r = {a = 1} in r.a", 1)

# match
err('match 1 with | 2 -> 1 end', "no_match")
ok('match 1 with | 1 -> "a" | _ -> "b" end', "a")
err('match {a=1,b=2} with | {a=x,b=x} -> x end', "dup_binding")
ok('match {a=1} with | {a=x} -> x | _ -> 0 end', 1)
ok('match 5 with | x -> x end', 5)

# closures / result conversion
ok("fun x -> x", "<fn>")
ok("ref 1", "<ref>")

# nested record conversion
ok('{a = {b = 1}, c = true}', {"a": {"b": 1}, "c": True})

# whitespace-only / general
err("let x = 1", "parse")
err("let x = 1 in", "parse")
err("(1", "parse")
err("1)", "parse")

# unary chain
ok("- - 1", 1)
ok("! ! ref ref 3", None) if False else None

# field access tightest
ok("let f = fun x -> x in let a = {b = 5} in f a.b", 5)

print("ALL TESTS PASSED")
