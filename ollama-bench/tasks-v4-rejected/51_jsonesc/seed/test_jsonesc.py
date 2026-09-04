"""Visible checks for jsonesc.py -- run with `python test_jsonesc.py`.

These cover only the basics from the task description; the grader checks a great
deal more.
"""
from jsonesc import dumps, loads, JsonError

assert dumps({"b": 1, "a": [1, 2]}) == '{"b": 1, "a": [1, 2]}'
assert dumps([1, {"x": None}], separators=(",", ":")) == '[1,{"x":null}]'
assert dumps({"a": [1]}, indent=2) == '{\n  "a": [\n    1\n  ]\n}'
assert dumps({"k": "héllo"}) == '{"k": "h\\u00e9llo"}'
assert loads('{"a": [1, 2.5, true, null], "b": {}}') == {
    "a": [1, 2.5, True, None], "b": {}}

try:
    loads("[1, 2")
except JsonError as e:
    assert (e.kind, e.pos, e.lineno, e.colno) == ("eof", 5, 1, 6), (
        e.kind, e.pos, e.lineno, e.colno)
    assert isinstance(e, ValueError)
else:
    raise AssertionError("expected JsonError")

print("visible checks passed")
