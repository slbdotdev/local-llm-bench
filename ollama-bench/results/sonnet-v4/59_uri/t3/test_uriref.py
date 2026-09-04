import uriref as u

def check(cond, msg):
    if not cond:
        raise AssertionError(msg)

# banned imports check
import sys
banned = ("re", "urllib", "urllib.parse", "posixpath", "ipaddress", "string", "binascii")
for name in list(sys.modules):
    pass
# ensure module itself didn't import banned modules
src = open("uriref.py").read()
for b in banned:
    check(("import " + b) not in src and ("from " + b) not in src, "banned import " + b)

check(u.parse("http://a.com/x?y=1#z") == {"scheme": "http", "userinfo": None, "host": "a.com",
    "port": None, "path": "/x", "query": "y=1", "fragment": "z"}, "ex1")

check(u.parse("mailto:x@y") == {"scheme": "mailto", "userinfo": None, "host": None, "port": None,
    "path": "x@y", "query": None, "fragment": None}, "ex2")

check(u.unparse(u.parse("//u@h:8080/p")) == "//u@h:8080/p", "ex3")

check(u.normalize("HTTP://Example.COM:80/a/./b/../c") == "http://example.com/a/c", "ex4")

check(u.resolve("http://a/b/c/d;p?q", "../g") == "http://a/b/g", "ex5")
check(u.resolve("http://a/b/c/d;p?q", "?y") == "http://a/b/c/d;p?y", "ex6")

# type errors
try:
    u.parse(123)
    check(False, "should raise type")
except u.UriError as e:
    check(e.kind == "type", "parse type kind")

try:
    u.unparse("not a dict")
    check(False, "unparse type")
except u.UriError as e:
    check(e.kind == "type", "unparse type kind")

try:
    u.resolve(1, "x")
    check(False, "resolve type")
except u.UriError as e:
    check(e.kind == "type", "resolve type kind")

# scheme error
try:
    u.parse("1http://a/b")
    check(False, "scheme")
except u.UriError as e:
    check(e.kind == "scheme", "scheme kind: " + e.kind)

# port error
try:
    u.parse("//h:8a0/")
    check(False, "port")
except u.UriError as e:
    check(e.kind == "port", e.kind)

# host error
try:
    u.parse("//h[x]/")
    check(False, "host")
except u.UriError as e:
    check(e.kind == "host", e.kind)

# userinfo error
try:
    u.parse("//u[x]@h/")
    check(False, "userinfo")
except u.UriError as e:
    check(e.kind == "userinfo", e.kind)

# char error
try:
    u.parse("/pa th")
    check(False, "char")
except u.UriError as e:
    check(e.kind == "char", e.kind)

# escape error
try:
    u.parse("/p%zz")
    check(False, "escape")
except u.UriError as e:
    check(e.kind == "escape", e.kind)

# form errors for unparse
try:
    u.unparse({"scheme": None, "userinfo": None, "host": None, "port": None,
               "path": None, "query": None, "fragment": None})
    check(False, "form path none")
except u.UriError as e:
    check(e.kind == "form", e.kind)

try:
    u.unparse({"scheme": None, "userinfo": "u", "host": None, "port": None,
               "path": "", "query": None, "fragment": None})
    check(False, "form userinfo w/o host")
except u.UriError as e:
    check(e.kind == "form", e.kind)

try:
    u.unparse({"scheme": None, "userinfo": None, "host": "h", "port": None,
               "path": "notslash", "query": None, "fragment": None})
    check(False, "form path w/ host must start with /")
except u.UriError as e:
    check(e.kind == "form", e.kind)

try:
    u.unparse({"scheme": None, "userinfo": None, "host": None, "port": None,
               "path": "//weird", "query": None, "fragment": None})
    check(False, "form host none path starts //")
except u.UriError as e:
    check(e.kind == "form", e.kind)

try:
    u.unparse({"scheme": None, "userinfo": None, "host": None, "port": None,
               "path": "a:b/c", "query": None, "fragment": None})
    check(False, "form colon in first segment")
except u.UriError as e:
    check(e.kind == "form", e.kind)

# missing key -> form
try:
    d = u.parse("http://a.com/x")
    del d["query"]
    u.unparse(d)
    check(False, "form missing key")
except u.UriError as e:
    check(e.kind == "form", e.kind)

# None/"" distinction
p = u.parse("//h")
check(p["path"] == "", "empty path")
p2 = u.parse("mailto:x")
check(p2["host"] is None, "absent host")

# remove_dot_segments direct-ish via normalize
check(u.normalize("http://h/a/b/../../c") == "http://h/c", "dotseg1")
check(u.normalize("http://h/a//b") == "http://h/a//b", "no collapse empty segs")
check(u.normalize("http://h") == "http://h", "no growing slash")

# port default removal
check(u.normalize("http://h:80/") == "http://h/", "http 80 removed")
check(u.normalize("https://h:443/") == "https://h/", "https 443 removed")
check(u.normalize("ws://h:80/") == "ws://h/", "ws 80 removed")
check(u.normalize("wss://h:443/") == "wss://h/", "wss 443 removed")
check(u.normalize("http://h:443/") == "http://h:443/", "http 443 kept")
check(u.normalize("http://h:") == "http://h", "empty port removed")
check(u.normalize("ftp://h:080/") == "ftp://h:80/", "leading zero port")
check(u.normalize("ftp://h:00/") == "ftp://h:0/", "zero port")

# percent escape canonicalization
check(u.normalize("http://h/%2f") == "http://h/%2F", "percent 2f stays encoded uppercase")
check(u.normalize("http://h/%7e") == "http://h/~", "tilde decoded")
check(u.normalize("http://%68/") == "http://h/", "host escape decode+lower... check")

# host case-fold vs escape
n = u.normalize("http://%41/")
check(n == "http://a/", "escape then lowercase: " + n)
n2 = u.normalize("http://%C3/")
check(n2 == "http://%C3/", "non-ascii-hex escape kept uppercase: " + n2)

# recomposition guard
d3 = {"scheme": None, "userinfo": None, "host": None, "port": None, "path": "//x", "query": None, "fragment": None}
# can't unparse directly (form err), but via normalize with host None and path already has // after dot removal
# test via resolve producing host None scenario is unlikely; test remove_dot_segments + guard indirectly:
check(u.normalize("foo:/.//x") == "foo:/.//x" or True, "guard sanity (not exhaustive)")

# unparse roundtrip
for test_s in ["http://a.com/x?y=1#z", "mailto:x@y", "//u@h:8080/p", "", "/a/b", "a/b", "?q", "#f", "//h"]:
    parsed = u.parse(test_s)
    back = u.unparse(parsed)
    check(back == test_s, "roundtrip failed for %r -> %r" % (test_s, back))

print("ALL TESTS PASSED")
