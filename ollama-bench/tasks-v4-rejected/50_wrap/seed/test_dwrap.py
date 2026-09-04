"""Visible examples for dwrap.py.  Run with: python test_dwrap.py"""
import dwrap

assert dwrap.width("hi") == 2
assert dwrap.width("a" + chr(0x4E2D) + "b") == 4

assert dwrap.clusters("ab") == ["a", "b"]

assert dwrap.expand_tabs("ab\tc") == "ab      c"
assert dwrap.expand_tabs("a\tb", 4) == "a   b"

assert dwrap.wrap("the quick brown fox", 9) == ["the quick", "brown fox"]
assert dwrap.wrap("hello\n\nworld", 10) == ["hello", "", "world"]

assert dwrap.truncate("hello world", 8) == "hello w" + chr(0x2026)
assert dwrap.truncate("abc", 10) == "abc"

print("visible examples ok")
