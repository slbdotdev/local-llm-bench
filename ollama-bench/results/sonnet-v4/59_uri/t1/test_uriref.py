"""Visible checks for uriref.py -- run with: python test_uriref.py"""
from uriref import parse, unparse, normalize, resolve

assert parse("http://a.com/x?y=1#z") == {
    "scheme": "http", "userinfo": None, "host": "a.com", "port": None,
    "path": "/x", "query": "y=1", "fragment": "z"}
assert parse("mailto:x@y") == {
    "scheme": "mailto", "userinfo": None, "host": None, "port": None,
    "path": "x@y", "query": None, "fragment": None}
assert unparse(parse("//u@h:8080/p")) == "//u@h:8080/p"
assert normalize("HTTP://Example.COM:80/a/./b/../c") == "http://example.com/a/c"
assert resolve("http://a/b/c/d;p?q", "../g") == "http://a/b/g"
assert resolve("http://a/b/c/d;p?q", "?y") == "http://a/b/c/d;p?y"

print("visible OK")
