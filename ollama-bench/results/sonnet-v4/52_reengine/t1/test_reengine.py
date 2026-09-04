"""Visible examples from the task description.  Run with: python test_reengine.py"""
from reengine import search

assert search("a+b", "xaaab") == (1, 5, [])
assert search(r"(\d+)-(\d+)", "sum 12-345!") == (4, 10, [(4, 6), (7, 10)])
assert search("colou?r", "color") == (0, 5, [])
assert search("^b", "ab") is None
assert search("(x)|(y)", "wy") == (1, 2, [None, (1, 2)])

print("visible examples ok")
