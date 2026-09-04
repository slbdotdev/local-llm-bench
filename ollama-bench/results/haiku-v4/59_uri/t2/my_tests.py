"""Comprehensive tests for uriref.py"""
from uriref import parse, unparse, normalize, resolve, UriError

# Test basic parsing
print("Testing basic parsing...")
result = parse("http://a.com/x?y=1#z")
assert result["scheme"] == "http"
assert result["host"] == "a.com"
assert result["path"] == "/x"
assert result["query"] == "y=1"
assert result["fragment"] == "z"
assert result["userinfo"] is None
assert result["port"] is None

# Test empty query and fragment
result = parse("http://a.com/x")
assert result["query"] is None
assert result["fragment"] is None
assert result["path"] == "/x"

# Test userinfo and port
result = parse("http://user:pass@host:8080/path")
assert result["userinfo"] == "user:pass"
assert result["host"] == "host"
assert result["port"] == "8080"

# Test scheme-less URI
result = parse("//example.com/path")
assert result["scheme"] is None
assert result["host"] == "example.com"

# Test relative path
result = parse("../path")
assert result["scheme"] is None
assert result["host"] is None
assert result["path"] == "../path"

# Test empty authority
result = parse("//")
assert result["scheme"] is None
assert result["userinfo"] is None
assert result["host"] == ""
assert result["port"] is None
assert result["path"] == ""

# Test @ in authority
result = parse("//@host")
assert result["userinfo"] == ""
assert result["host"] == "host"

# Test : in port
result = parse("//:8080")
assert result["host"] == ""
assert result["port"] == "8080"

print("Basic parsing OK")

# Test error cases - type validation
print("Testing type errors...")
try:
    parse(123)
    assert False, "Should raise UriError for non-string"
except UriError as e:
    assert e.kind == "type"

try:
    unparse("not a dict")
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "type"

print("Type errors OK")

# Test error cases - scheme validation
print("Testing scheme errors...")
try:
    parse(":invalid")  # scheme starts with :
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "scheme"

try:
    parse("9invalid:path")  # scheme starts with digit
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "scheme"

try:
    parse("inval@id:path")  # invalid char in scheme
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "scheme"

print("Scheme errors OK")

# Test error cases - port validation
print("Testing port errors...")
try:
    parse("http://host:abc/")
    assert False, "Should raise UriError for non-digit port"
except UriError as e:
    assert e.kind == "port"

print("Port errors OK")

# Test error cases - host validation
print("Testing host errors...")
try:
    parse("http://host[bracket]/")
    assert False, "Should raise UriError for [ in host"
except UriError as e:
    assert e.kind == "host"

try:
    parse("http://host]bracket/")
    assert False, "Should raise UriError for ] in host"
except UriError as e:
    assert e.kind == "host"

print("Host errors OK")

# Test error cases - character validation
print("Testing character errors...")
try:
    parse("http://host/path with space")
    assert False, "Should raise UriError for space in path"
except UriError as e:
    assert e.kind == "char"

print("Character errors OK")

# Test error cases - escape validation
print("Testing escape errors...")
try:
    parse("http://host/%")
    assert False, "Should raise UriError for incomplete escape"
except UriError as e:
    assert e.kind == "escape"

try:
    parse("http://host/%A")
    assert False, "Should raise UriError for incomplete escape"
except UriError as e:
    assert e.kind == "escape"

try:
    parse("http://host/%GG")
    assert False, "Should raise UriError for invalid hex"
except UriError as e:
    assert e.kind == "escape"

print("Escape errors OK")

# Test unparse validation
print("Testing unparse validation...")
try:
    unparse({"scheme": None})  # missing keys
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "form"

try:
    d = {"scheme": None, "userinfo": None, "host": None, "port": None,
         "path": None, "query": None, "fragment": None}
    unparse(d)  # path is None
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "form"

try:
    d = {"scheme": None, "userinfo": None, "host": None, "port": None,
         "path": "/path", "query": None, "fragment": None}
    d["scheme"] = 123  # invalid value type
    unparse(d)
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "type"

print("Unparse validation OK")

# Test unparse structural errors
print("Testing unparse structural errors...")

# host is None but userinfo is not None
try:
    d = {"scheme": None, "userinfo": "user", "host": None, "port": None,
         "path": "/path", "query": None, "fragment": None}
    unparse(d)
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "form"

# host is not None but path doesn't start with /
try:
    d = {"scheme": None, "userinfo": None, "host": "example.com", "port": None,
         "path": "path", "query": None, "fragment": None}
    unparse(d)
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "form"

# host is None but path starts with //
try:
    d = {"scheme": None, "userinfo": None, "host": None, "port": None,
         "path": "//path", "query": None, "fragment": None}
    unparse(d)
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "form"

# scheme and host are None, first segment contains :
try:
    d = {"scheme": None, "userinfo": None, "host": None, "port": None,
         "path": "a:b/c", "query": None, "fragment": None}
    unparse(d)
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "form"

print("Unparse structural errors OK")

# Test round-trip
print("Testing round-trip...")
tests = [
    "http://example.com/path",
    "//example.com:8080/path",
    "http://user@host/path",
    "http://host/path?query=value",
    "http://host/path#fragment",
    "/path/to/resource",
    "path/to/resource",
    "//",
    "//@",
    "//:8080",
]
for uri in tests:
    parsed = parse(uri)
    unparsed = unparse(parsed)
    assert unparsed == uri, f"Round-trip failed for {uri}: got {unparsed}"

print("Round-trip OK")

# Test normalization
print("Testing normalization...")

# Scheme lowercasing
result = normalize("HTTP://example.com")
assert result == "http://example.com"

# Host lowercasing
result = normalize("http://EXAMPLE.COM")
assert result == "http://example.com"

# Port normalization
result = normalize("http://example.com:80")
assert result == "http://example.com"

result = normalize("https://example.com:443")
assert result == "https://example.com"

result = normalize("http://example.com:8080")
assert result == "http://example.com:8080"

# Dot segment removal
result = normalize("http://example.com/a/b/../c")
assert result == "http://example.com/a/c"

result = normalize("http://example.com/a/./b")
assert result == "http://example.com/a/b"

result = normalize("http://example.com/a/../../b")
assert result == "http://example.com/b"

# Percent-escape canonicalization
result = normalize("http://example.com/%2f")
assert result == "http://example.com/%2F"

result = normalize("http://example.com/%7e")
assert result == "http://example.com/~"

print("Normalization OK")

# Test resolution
print("Testing resolution...")

# Relative path - verify path merging and dot segment removal
result = resolve("http://a/b/c/d", "../g")
assert result == "http://a/b/g", f"Expected http://a/b/g, got {result}"

# Absolute path
result = resolve("http://a/b/c", "/d")
assert result == "http://a/d"

# Query-only reference
result = resolve("http://a/b/c?old", "?new")
assert result == "http://a/b/c?new"

# Fragment-only reference
result = resolve("http://a/b/c", "#new")
assert result == "http://a/b/c#new"

# With authority
result = resolve("http://a/b/c", "//b/d")
assert result == "http://b/d"

# With scheme
result = resolve("http://a/b/c", "https://b/d")
assert result == "https://b/d"

print("Resolution OK")

# Test base without scheme error
print("Testing base validation...")
try:
    resolve("//example.com/path", "../ref")
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "base"

print("Base validation OK")

# Test resolve type checking
print("Testing resolve type checking...")
try:
    resolve(123, "ref")
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "type"

try:
    resolve("http://example.com", 123)
    assert False, "Should raise UriError"
except UriError as e:
    assert e.kind == "type"

print("Resolve type checking OK")

print("\nAll tests passed!")
