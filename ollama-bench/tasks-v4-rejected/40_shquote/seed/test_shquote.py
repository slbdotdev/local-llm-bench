"""Visible checks for shquote.py -- run with: python test_shquote.py"""
from shquote import split, quote, join

assert split("ls -l  /tmp/x") == ["ls", "-l", "/tmp/x"]
assert split("echo 'hello   world'") == ["echo", "hello   world"]
assert split('say "hi there" now') == ["say", "hi there", "now"]
assert split("a\\ b c") == ["a b", "c"]
assert split("grep -n a#b file") == ["grep", "-n", "a#b", "file"]
assert join(["git", "commit", "-m", "a message"]) == "git commit -m 'a message'"
assert quote("plain") == "plain"

print("visible OK")
