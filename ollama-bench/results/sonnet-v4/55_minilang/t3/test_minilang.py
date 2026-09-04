from minilang import run, MiniError


def ok(src, expected):
    got = run(src)
    assert got == expected and type(got) == type(expected), \
        f"{src!r}: expected {expected!r} ({type(expected)}), got {got!r} ({type(got)})"


def err(src, kind):
    try:
        run(src)
    except MiniError as e:
        assert e.kind == kind, f"{src!r}: expected kind {kind}, got {e.kind}"
    else:
        raise AssertionError(f"{src!r}: expected MiniError kind {kind}, no error raised")


# examples from spec
ok("1 + 2 * 3", 7)
ok("let x = 4 in x * x", 16)
ok("letrec f = fun n -> if n == 0 then 1 else n * f (n - 1) in f 5", 120)
ok('match {tag = "pt", x = 3} with | {tag = "pt", x = v} -> v + 1 | _ -> 0 end', 4)
ok("let r = ref 2 in r := !r + 3", 5)
err("{a = 1}.b", "no_field")

# lexical
err("007", "parse")
err("01", "parse")
ok("0", 0)
ok("40", 40)
err('"unterminated', "parse")
ok('""', "")
err(";", "parse")
err("é", "parse")
err("", "parse")
err("   ", "parse")

# precedence
ok("let x = 3 in -x * 2", -6)
err("ref 1 + 2", "type")  # (ref 1) + 2 -> ref + int is a type error
ok("- - 1", 1)
err("let f = fun x -> x in f let x = 1 in x", "parse")
err("let f = fun x -> x in f if true then 1 else 2", "parse")
ok("let f = fun x -> x in f (let x = 1 in x)", 1)
ok("let f = fun a -> fun b -> a + b in f 1 2", 3)
ok('"a" ++ "b" ++ "c"', "abc")
ok("10 - 4 - 3", 3)
ok("2 * 3 % 4", 2)
err("let f = fun x -> x + 1 in f -1", "type")  # f -1 is f - 1 (subtraction): closure - int is type error

# division / modulo
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
err("true + (1 / 0)", "div_zero")
err('"x" / 0', "type")

# strings / concat / repeat
ok('"ab" * 3', "ababab")
ok('"ab" * 0', "")
err('3 * "ab"', "type")
err('"n=" ++ 1 ++ "!"', "type")
err('1 ++ "x"', "type")
ok('"x" ++ 1', "x1")
ok('"x" ++ -1', "x-1")
ok('"x" ++ true', "xtrue")
ok('"x" ++ false', "xfalse")
err('"x" ++ {}', "type")

# comparisons
ok("1 < 2", True)
err("1 < 2 < 3", "parse")
err("a == b == c", "parse")
err('1 == "1"', "type")
err("1 < true", "type")
ok("true == true", True)
ok("let a = ref 1 in let b = a in a == b", True)
ok("let a = ref 1 in let b = ref 1 in a == b", False)
err("{} == {}", "type")

# scope
err("let x = 1 in y", "unbound")
ok("letrec a = 1 and b = a in b", 1)
err("letrec a = b and b = 1 in a", "uninit")
err("letrec a = 1 and a = 2 in a", "dup_binding")
ok("let x = 1 in let f = fun y -> x + y in let x = 2 in f 3", 4)

# records / patterns
err("{a = 1, a = 2}", "dup_field")
err("match 1 with | {a = x, b = x} -> x | _ -> 0 end", "dup_binding")
ok('match 5 with | 1 -> "one" | 5 -> "five" | _ -> "other" end', "five")
ok("match {a = 1} with | {a = 1, b = 2} -> 1 | _ -> 0 end", 0)
err("match {a=1} with | {a=1,a=2} -> 1 end", "dup_field")
ok('let s = {x = 1, y = 2} in s.x + s.y', 3)

# reserved words
err("let end = 1 in end", "parse")
err("{end = 1}", "parse")
err("fun in -> 1", "parse")
err("let _ = 1 in 1", "parse")
err("_", "parse")
ok("match 1 with | _ -> 2 end", 2)

# result conversion types
r = run("{a = 1, b = true, c = ref 1}")
assert isinstance(r, dict) and r["a"] == 1 and r["b"] is True and r["c"] == "<ref>"
assert run("fun x -> x") == "<fn>"
assert run("true") is True
assert run("false") is False
assert isinstance(run("1"), int) and not isinstance(run("1"), bool)

print("ALL TESTS PASSED")
