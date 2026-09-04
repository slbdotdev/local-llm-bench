#!/usr/bin/env python3
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

# Multiple nested levels
all_pass &= test("nested_if_for",
    "{% for i in items %}{% if i %}{{ i }}{% endif %}{% endfor %}",
    {"items": [1, None, 3]},
    "13")

# Set in conditional
all_pass &= test("set_in_if",
    "{% if true %}{% set x = 5 %}{{ x }}{% endif %}{{ x }}",
    {}, "55")

# Set persists in loop
all_pass &= test("set_in_for",
    "{% for i in items %}{% set sum = 10 %}{{ sum }}{% endfor %}",
    {"items": [1, 2]}, "1010")

# Filter chain
all_pass &= test("filter_chain_many",
    "{{ x | lower | upper | lower }}",
    {"x": "HeLLo"}, "hello")

# Safe mark preserves through operations
all_pass &= test("safe_through_filter",
    "{{ x | safe | upper }}",
    {"x": "<b>&</b>"}, "<B>&</B>")

# Escape then safe (default replaces)
all_pass &= test("default_loses_safe",
    "{{ miss | default:'<b>' }}",
    {}, "&lt;b&gt;")

# Slice filter
all_pass &= test("slice_string",
    "{{ x | slice:1,2 }}",
    {"x": "abcde"}, "bc")

all_pass &= test("slice_list",
    "{{ x | slice:1,2 }}",
    {"x": [1, 2, 3, 4, 5]}, "[2, 3]")

# First on empty
all_pass &= test("first_empty",
    "{{ x | first }}",
    {"x": ""}, "")

# Join on non-list
all_pass &= test("join_string",
    "{{ x | join:'-' }}",
    {"x": "abc"}, "a-b-c")

# Complex expression in for
all_pass &= test("for_expr",
    "{% for i in x | slice:1,2 %}{{ i }}{% endfor %}",
    {"x": [1, 2, 3, 4]}, "23")

# Nested loops with inner variable
all_pass &= test("nested_loops",
    "{% for i in x %}{% for j in i %}{{ j }}{% endfor %}-{% endfor %}",
    {"x": [[1, 2], [3, 4]]}, "12-34-")

# Scope shadowing in nested for
all_pass &= test("scope_shadow",
    "{% for x in outer %}{{ x }}{% for x in inner %}{{ x }}{% endfor %}{% endfor %}",
    {"outer": ["a", "b"], "inner": [1, 2]}, "a12b12")

# Empty for with empty body
all_pass &= test("for_empty_no_body",
    "{% for i in x %}{% endfor %}",
    {"x": []}, "")

# Non-iterable error
all_pass &= test("for_non_iterable_error",
    "{% for i in x %}{{ i }}{% endfor %}",
    {"x": 42}, error_kind="not_iterable")

# Escaped HTML tags in text
all_pass &= test("escape_in_text",
    "<b>{{ x }}</b>", {"x": "<i>"}, "<b>&lt;i&gt;</b>")

# Literal text not escaped
all_pass &= test("literal_text",
    "{{ x }} <b>text</b>", {"x": "<script>"}, "&lt;script&gt; <b>text</b>")

# Empty interpolation
all_pass &= test("empty_interp", "{{ }}", {}, error_kind="syntax")

# Unclosed tag
all_pass &= test("unclosed_interp", "{{ x", {}, error_kind="unclosed_tag")

# Missing closing brace
all_pass &= test("missing_brace", "{{ x }", {}, error_kind="unclosed_tag")

# Unknown tag
all_pass &= test("unknown_tag", "{% badtag %}body{% endbadtag %}", {}, error_kind="unknown_tag")

# Syntax in condition
all_pass &= test("bad_cond_syntax", "{% if a < b < c %}yes{% endif %}", {}, error_kind="syntax")

# Lookup chain
all_pass &= test("lookup_chain",
    "{{ x.y.z }}",
    {"x": {"y": {"z": "found"}}}, "found")

# Lookup with missing intermediate
all_pass &= test("lookup_missing_chain",
    "{{ x.y.z }}",
    {"x": {}}, "")

# Subscript with variable
all_pass &= test("subscript_var",
    "{{ x[idx] }}",
    {"x": ["a", "b"], "idx": 1}, "b")

# Comparison with different types
all_pass &= test("cmp_different_types",
    "{{ 1 == '1' }}", {}, "false")

# In operator with string
all_pass &= test("in_substring",
    "{{ 'ell' in 'hello' }}", {}, "true")

# In operator with missing item
all_pass &= test("in_not_found",
    "{{ 'x' in x }}", {"x": [1, 2, 3]}, "false")

# Truthiness of various values
all_pass &= test("truthy_nonzero_float",
    "{% if x %}yes{% endif %}", {"x": 0.5}, "yes")

# False value string
all_pass &= test("falsy_string",
    "{% if 'false' %}yes{% endif %}", {}, "")

# None value
all_pass &= test("truthy_none",
    "{% if x %}yes{% endif %}", {"x": None}, "")

# Loop with variable shadowing outer
all_pass &= test("loop_shadow_outer",
    "{{ c }}{% for c in items %}{{ c }}{% endfor %}{{ c }}",
    {"c": "outer", "items": ["a", "b"]}, "outerabouter")

# Empty string context value
all_pass &= test("empty_string",
    "{% if x %}yes{% else %}no{% endif %}",
    {"x": ""}, "no")

# Whitespace with multiple tags
all_pass &= test("ws_multiple",
    "a {%- if true -%} {%- if true -%}b{% endif %} {%- endif -%} c",
    {}, "abc")

# Comment with nested braces (not actual nesting per spec)
all_pass &= test("comment_braces",
    "a {# {# inner #} #} b", {}, "a  #} b")

if all_pass:
    print("\n✓ All edge case tests passed!")
    sys.exit(0)
else:
    print("\n✗ Some edge case tests failed")
    sys.exit(1)
