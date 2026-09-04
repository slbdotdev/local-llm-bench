"""Visible examples from the prompt.  Run with: python test_minilang.py"""
from minilang import run, MiniError

assert run("1 + 2 * 3") == 7
assert run("let x = 4 in x * x") == 16
assert run("letrec f = fun n -> if n == 0 then 1 else n * f (n - 1) in f 5") == 120
assert run('match {tag = "pt", x = 3} with | {tag = "pt", x = v} -> v + 1 | _ -> 0 end') == 4
assert run("let r = ref 2 in r := !r + 3") == 5

try:
    run("{a = 1}.b")
except MiniError as e:
    assert e.kind == "no_field"
else:
    raise AssertionError("expected a MiniError")

print("ok")
