#!/usr/bin/env python3
"""Test specific requirements from the spec."""
from tmpl import render, TemplateError
import sys

def test(name, template, context, expected=None, error_kind=None):
    try:
        result = render(template, context)
        if error_kind:
            print(f"FAIL {name}: Expected {error_kind} but got: {result}")
            return False
        if expected is not None and result != expected:
            print(f"FAIL {name}: Expected '{expected}' but got '{result}'")
            return False
        print(f"OK {name}")
        return True
    except TemplateError as e:
        if error_kind and e.kind == error_kind:
            print(f"OK {name}")
            return True
        else:
            print(f"FAIL {name}: Got {e.kind} at {e.pos}, expected {error_kind}")
            return False

all_pass = True

# From spec examples
all_pass &= test("spec_ex1",
    "Hello {{ name | upper }}!", {"name": "ada"},
    "Hello ADA!")

all_pass &= test("spec_ex2",
    "{% for c in cs %}{{ loop.index }}.{{ c }} {% empty %}none{% endfor %}",
    {"cs": ["a", "b"]}, "1.a 2.b ")

all_pass &= test("spec_ex3",
    "{{ bio }}", {"bio": "<b>x</b>"},
    "&lt;b&gt;x&lt;/b&gt;")

all_pass &= test("spec_ex4",
    "A\n  {%- if ok %}yes{% endif %}", {"ok": True},
    "Ayes")

all_pass &= test("spec_ex5",
    "{{ miss | default:'n/a' }}", {},
    "n/a")

# Type names from spec
all_pass &= test("type_none",
    "{{ x.type }}", {"x": None}, "")  # x.type is undefined when x is None

all_pass &= test("type_bool",
    "{{ x.type }}", {"x": True}, "bool")

all_pass &= test("type_number",
    "{{ x.type }}", {"x": 42}, "number")

all_pass &= test("type_string",
    "{{ x.type }}", {"x": "hi"}, "string")

all_pass &= test("type_list",
    "{{ x.type }}", {"x": [1, 2]}, "list")

all_pass &= test("type_map",
    "{{ x.type }}", {"x": {"a": 1}}, "map")

# Falsy values from spec
all_pass &= test("falsy_undefined",
    "{% if x %}yes{% else %}no{% endif %}", {},
    "no")

all_pass &= test("falsy_none",
    "{% if x %}yes{% else %}no{% endif %}", {"x": None},
    "no")

all_pass &= test("falsy_false",
    "{% if x %}yes{% else %}no{% endif %}", {"x": False},
    "no")

all_pass &= test("falsy_zero",
    "{% if x %}yes{% else %}no{% endif %}", {"x": 0},
    "no")

all_pass &= test("falsy_empty_string",
    "{% if x %}yes{% else %}no{% endif %}", {"x": ""},
    "no")

all_pass &= test("falsy_zero_string",
    "{% if x %}yes{% else %}no{% endif %}", {"x": "0"},
    "no")

all_pass &= test("falsy_false_string",
    "{% if x %}yes{% else %}no{% endif %}", {"x": "false"},
    "no")

all_pass &= test("falsy_empty_list",
    "{% if x %}yes{% else %}no{% endif %}", {"x": []},
    "no")

all_pass &= test("falsy_empty_map",
    "{% if x %}yes{% else %}no{% endif %}", {"x": {}},
    "no")

# Truthy values
all_pass &= test("truthy_space",
    "{% if x %}yes{% else %}no{% endif %}", {"x": " "},
    "yes")

all_pass &= test("truthy_false_string",
    "{% if x %}yes{% else %}no{% endif %}", {"x": "False"},
    "yes")

all_pass &= test("truthy_zero_float",
    "{% if x %}yes{% else %}no{% endif %}", {"x": "0.0"},
    "yes")

all_pass &= test("truthy_negative",
    "{% if x %}yes{% else %}no{% endif %}", {"x": -1},
    "yes")

# List text representation
all_pass &= test("list_text",
    "{{ x }}", {"x": ["a", 2, True]},
    "[a, 2, true]")

# Map text representation (insertion order)
all_pass &= test("map_text",
    "{{ x }}", {"x": {"a": 1, "b": "x"}},
    "{a: 1, b: x}")

# Escape replacements in single pass (& not re-escaped)
all_pass &= test("escape_no_rescale",
    "{{ x }}",
    {"x": "&"},
    "&amp;")

# Safe values persist through filters
all_pass &= test("safe_sticky",
    "{{ x | escape | upper }}",
    {"x": "a&b"},
    "A&AMP;B")

# Default replaces with unsafe value
all_pass &= test("default_unsafe",
    "{{ x | escape | default:'<b>' }}",
    {"x": None},
    "&lt;b&gt;")

# Loop.first and loop.last are booleans (not integers)
all_pass &= test("loop_first_bool",
    "{% for i in x %}{{ loop.first }}{% endfor %}",
    {"x": [1, 2]},
    "truefalse")

# Empty for body with empty
all_pass &= test("for_empty_body",
    "{% for i in x %}{% empty %}empty{% endfor %}",
    {"x": []},
    "empty")

# Not operator precedence
all_pass &= test("not_precedence",
    "{{ not 5 == 5 }}",
    {},
    "false")  # not (5 == 5) = not true = false

# Non-associative comparison
all_pass &= test("non_assoc_cmp",
    "{{ 1 < 2 < 3 }}",
    {},
    error_kind="syntax")

# Whitespace insignificant in expressions
all_pass &= test("ws_insig",
    "{{   x   +   y   }}",
    {"x": 1},
    error_kind="syntax")  # + is not supported, but whitespace is fine

# String escape sequences
all_pass &= test("str_escape_n",
    "{{ x }}",
    {"x": "hello\nworld"},
    "hello\nworld")

all_pass &= test("str_escape_t",
    "{{ x }}",
    {"x": "hello\tworld"},
    "hello\tworld")

# Missing bracket
all_pass &= test("missing_bracket",
    "{{ x[0 }}",
    {},
    error_kind="syntax")

# Undefined comparison
all_pass &= test("cmp_undefined",
    "{{ x == y }}",
    {},
    "true")  # Two undefined values are equal

all_pass &= test("cmp_undefined_ne",
    "{{ x != y }}",
    {},
    "false")  # Two undefined values are equal

# Filter first on map
all_pass &= test("first_map",
    "{{ x | first }}",
    {"x": {"a": 1, "b": 2}},
    "a")

if all_pass:
    print("\n✓ All spec requirement tests passed!")
    sys.exit(0)
else:
    print("\n✗ Some spec tests failed")
    sys.exit(1)
