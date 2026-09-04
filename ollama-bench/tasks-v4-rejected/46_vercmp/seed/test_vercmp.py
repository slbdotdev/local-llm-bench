"""Visible examples for vercmp.py.  Run with: python test_vercmp.py"""
from vercmp import parse, compare, satisfies, best_match, sort_versions

assert parse("2:1.02.3-beta.4+build.1") == {
    "epoch": 2, "release": [1, 2, 3], "pre": ["beta", 4], "build": "build.1"}

assert compare("1.2.3", "1.10.0") == -1
assert compare("1.0.0-alpha", "1.0.0") == -1

assert satisfies("1.4.2", "^1.2.3") is True
assert satisfies("2.0.0", "^1.2.3") is False
assert satisfies("1.2.9", ">=1.0.0,<1.2.0 || ~1.2.5") is True

assert best_match(["1.0.0", "1.4.0", "2.1.0"], "1.*") == "1.4.0"
assert sort_versions(["1.10", "1.2", "1.2.0-rc"]) == ["1.2.0-rc", "1.2", "1.10"]

print("ALL OK")
