"""Visible examples for gitattr.py -- run with: python test_gitattr.py"""
from gitattr import AttrError, compile_attrs, check_attrs

c = compile_attrs(["*.txt text", "/doc/*.txt -text diff=plain"])
assert check_attrs("a/b.txt", c) == {"text": True}
assert check_attrs("doc/b.txt", c) == {"text": False, "diff": "plain"}

c2 = compile_attrs(["[attr]bin -diff -text", "*.png bin", "*.png diff=hex"])
assert check_attrs("x.png", c2) == {"bin": True, "diff": "hex", "text": False}

c3 = compile_attrs(["a/**/z !k", "**/z k=1"])
assert check_attrs("a/q/z", c3) == {"k": "1"}

try:
    compile_attrs(["[ x"])
    raise SystemExit("expected AttrError")
except AttrError as e:
    assert e.kind == "unterminated_class"

print("visible examples OK")
