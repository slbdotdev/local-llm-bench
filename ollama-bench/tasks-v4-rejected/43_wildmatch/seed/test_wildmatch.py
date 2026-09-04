"""Visible examples for wildmatch.py -- run with: python test_wildmatch.py"""
from wildmatch import expand, match, filter

assert expand("a{b,c}d") == ["abd", "acd"]
assert expand("{x,y}{1,2}") == ["x1", "x2", "y1", "y2"]

assert match("a*c", "abbbc") is True
assert match("a?c", "ac") is False
assert match("[[:digit:]]x", "7x") is True
assert match("A*", "abc", casefold=True) is True

assert filter(["*.log", "a?"], ["x.log", "ab", "abc"]) == ["x.log", "ab"]

print("visible examples OK")
