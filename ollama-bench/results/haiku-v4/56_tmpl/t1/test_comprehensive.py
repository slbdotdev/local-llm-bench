#!/usr/bin/env python3
from tmpl import render, TemplateError
import sys

def test(name, template, context, expected=None, error_kind=None):
    """Test a template."""
    try:
        result = render(template, context)
        if error_kind:
            print(f"FAIL {name}: Expected {error_kind} but got result: {result}")
            return False
        if expected is not None and result != expected:
            print(f"FAIL {name}: Expected '{expected}' but got '{result}'")
            return False
        print(f"OK {name}")
        return True
    except TemplateError as e:
        if error_kind and e.kind == error_kind:
            print(f"OK {name}: Got expected error {error_kind} at {e.pos}")
            return True
        else:
            print(f"FAIL {name}: Got {e.kind} at {e.pos}, expected {error_kind}")
            return False

all_pass = True

# Basic interpolation
all_pass &= test("interp_simple", "Hello {{ name }}", {"name": "world"}, "Hello world")
all_pass &= test("interp_missing", "Hello {{ name }}", {}, "Hello ")
all_pass &= test("interp_empty", "{{ }}", {}, error_kind="syntax")

# Filters
all_pass &= test("filter_upper", "{{ x | upper }}", {"x": "hello"}, "HELLO")
all_pass &= test("filter_lower", "{{ x | lower }}", {"x": "HELLO"}, "hello")
all_pass &= test("filter_trim", "{{ x | trim }}", {"x": "  hello  "}, "hello")
all_pass &= test("filter_chain", "{{ x | upper | lower }}", {"x": "Hello"}, "hello")
all_pass &= test("filter_default", "{{ x | default:'n/a' }}", {}, "n/a")
all_pass &= test("filter_default_present", "{{ x | default:'n/a' }}", {"x": "val"}, "val")
all_pass &= test("filter_length_str", "{{ x | length }}", {"x": "hello"}, "5")
all_pass &= test("filter_length_list", "{{ x | length }}", {"x": [1, 2, 3]}, "3")
all_pass &= test("filter_first_str", "{{ x | first }}", {"x": "hello"}, "h")
all_pass &= test("filter_first_list", "{{ x | first }}", {"x": [1, 2, 3]}, "1")
all_pass &= test("filter_join", "{{ x | join:',' }}", {"x": ["a", "b", "c"]}, "a,b,c")
all_pass &= test("filter_replace", "{{ x | replace:'a','b' }}", {"x": "banana"}, "bbnbnb")
all_pass &= test("filter_escape", "{{ x | escape }}", {"x": "<b>&</b>"}, "&lt;b&gt;&amp;&lt;/b&gt;")
all_pass &= test("filter_safe", "{{ x | safe }}", {"x": "<b>bold</b>"}, "<b>bold</b>")
all_pass &= test("filter_unknown", "{{ x | badfilter }}", {"x": "hi"}, error_kind="unknown_filter")
all_pass &= test("filter_args", "{{ x | upper:'arg' }}", {"x": "hi"}, error_kind="filter_args")

# Escaping
all_pass &= test("escape_basic", "{{ x }}", {"x": "<b>&</b>"}, "&lt;b&gt;&amp;&lt;/b&gt;")
all_pass &= test("escape_quotes", "{{ x }}", {"x": '\'"\''}, "&#39;&#34;&#39;")
all_pass &= test("safe_mark", "{{ x | safe }}", {"x": "<b>&</b>"}, "<b>&</b>")

# Expressions
all_pass &= test("expr_literal_int", "{{ 42 }}", {}, "42")
all_pass &= test("expr_literal_str", "{{ 'hello' }}", {}, "hello")
all_pass &= test("expr_literal_bool", "{{ true }}", {}, "true")
all_pass &= test("expr_literal_none", "{{ none }}", {}, "")
all_pass &= test("expr_bool_false", "{{ false }}", {}, "false")

# Conditions
all_pass &= test("cond_eq_true", "{{ 1 == 1 }}", {}, "true")
all_pass &= test("cond_eq_false", "{{ 1 == 2 }}", {}, "false")
all_pass &= test("cond_ne", "{{ 1 != 2 }}", {}, "true")
all_pass &= test("cond_lt", "{{ 1 < 2 }}", {}, "true")
all_pass &= test("cond_str_cmp", "{{ 'a' < 'b' }}", {}, "true")
all_pass &= test("cond_in_str", "{{ 'a' in 'abc' }}", {}, "true")
all_pass &= test("cond_in_list", "{{ 1 in x }}", {"x": [1, 2, 3]}, "true")
all_pass &= test("cond_not", "{{ not false }}", {}, "true")
all_pass &= test("cond_and", "{{ true and false }}", {}, "false")
all_pass &= test("cond_or", "{{ true or false }}", {}, "true")

# Bad operations
all_pass &= test("bad_op_cmp_str_int", "{{ 'a' < 1 }}", {}, error_kind="bad_operand")

# If statements
all_pass &= test("if_true", "{% if true %}yes{% endif %}", {}, "yes")
all_pass &= test("if_false", "{% if false %}yes{% endif %}", {}, "")
all_pass &= test("if_elif", "{% if false %}a{% elif true %}b{% endif %}", {}, "b")
all_pass &= test("if_else", "{% if false %}a{% else %}b{% endif %}", {}, "b")
all_pass &= test("if_nested", "{% if true %}{% if true %}nested{% endif %}{% endif %}", {}, "nested")
all_pass &= test("if_unclosed", "{% if true %}body", {}, error_kind="unclosed_block")
all_pass &= test("if_unexpected_endif", "{% endif %}", {}, error_kind="unexpected_tag")
all_pass &= test("if_empty_cond", "{% if %}body{% endif %}", {}, error_kind="syntax")
all_pass &= test("if_empty_else", "{% else x %}body{% endif %}", {}, error_kind="unexpected_tag")

# For loops
all_pass &= test("for_simple", "{% for x in y %}{{ x }}{% endfor %}", {"y": [1, 2]}, "12")
all_pass &= test("for_empty", "{% for x in y %}a{% empty %}none{% endfor %}", {"y": []}, "none")
all_pass &= test("for_loop_index", "{% for x in y %}{{ loop.index }}{% endfor %}", {"y": [1, 2]}, "12")
all_pass &= test("for_loop_first", "{% for x in y %}{{ loop.first }}{% endfor %}", {"y": [1, 2]}, "truefalse")
all_pass &= test("for_loop_last", "{% for x in y %}{{ loop.last }}{% endfor %}", {"y": [1, 2]}, "falsetrue")
all_pass &= test("for_string", "{% for c in s %}{{ c }}{% endfor %}", {"s": "ab"}, "ab")
all_pass &= test("for_dict", "{% for k in d %}{{ k }}{% endfor %}", {"d": {"a": 1}}, "a")
all_pass &= test("for_not_iterable", "{% for x in y %}{{ x }}{% endfor %}", {"y": 42}, error_kind="not_iterable")
all_pass &= test("for_unclosed", "{% for x in y %}body", {"y": []}, error_kind="unclosed_block")

# Set statements
all_pass &= test("set_basic", "{% set x = 5 %}{{ x }}", {}, "5")
all_pass &= test("set_expr", "{% set x = 2 | upper %}{{ x }}", {}, "2")  # number doesn't change with upper
all_pass &= test("set_syntax1", "{% set %}body{% endif %}", {}, error_kind="syntax")
all_pass &= test("set_syntax2", "{% set x %}body{% endif %}", {}, error_kind="syntax")

# Lookups
all_pass &= test("lookup_dict", "{{ x.a }}", {"x": {"a": 1}}, "1")
all_pass &= test("lookup_list_idx", "{{ x.0 }}", {"x": [1, 2]}, "1")
all_pass &= test("lookup_sub_int", "{{ x[0] }}", {"x": [1, 2]}, "1")
all_pass &= test("lookup_sub_str_key", "{{ x['a'] }}", {"x": {"a": 1}}, "1")
all_pass &= test("lookup_missing", "{{ x.missing }}", {"x": {}}, "")
all_pass &= test("lookup_type", "{{ x.type }}", {"x": 5}, "number")
all_pass &= test("lookup_size", "{{ x.size }}", {"x": [1, 2, 3]}, "3")
all_pass &= test("lookup_keys", "{{ x.keys }}", {"x": {"a": 1}}, "[a]")

# Truthiness
all_pass &= test("truthy_nonempty_str", "{% if ' ' %}yes{% endif %}", {}, "yes")
all_pass &= test("falsy_zero_str", "{% if '0' %}yes{% endif %}", {}, "")
all_pass &= test("falsy_false_str", "{% if 'false' %}yes{% endif %}", {}, "")
all_pass &= test("truthy_nonzero", "{% if x %}yes{% endif %}", {"x": -1}, "yes")
all_pass &= test("falsy_empty_list", "{% if l %}yes{% endif %}", {"l": []}, "")
all_pass &= test("truthy_empty_str_space", "{% if ' ' %}yes{% endif %}", {}, "yes")

# Whitespace control
all_pass &= test("ws_control_left", "a {%- if true %}b{% endif %}", {}, "ab")
all_pass &= test("ws_control_right", "{% if true %}a {% endif -%}b", {}, "a b")
all_pass &= test("ws_control_both", "a {%- if true %}b{% endif -%} c", {}, "abc")

# Comments
all_pass &= test("comment_basic", "a{# comment #}b", {}, "ab")
all_pass &= test("comment_ws", "a {#- -#} b", {}, "ab")

# Error messages with position
err = None
try:
    render("x {{ {{ }}", {})
except TemplateError as e:
    err = e
if err and err.kind == "syntax" and err.pos == 2:
    print(f"OK error_pos_unclosed")
else:
    print(f"FAIL error_pos_unclosed: got {err}")
    all_pass = False

# Unclosed tag position
err = None
try:
    render("x {%", {})
except TemplateError as e:
    err = e
if err and err.kind == "unclosed_tag" and err.pos == 2:
    print(f"OK error_pos_tag")
else:
    print(f"FAIL error_pos_tag: got {err}")
    all_pass = False

if all_pass:
    print("\n✓ All comprehensive tests passed!")
    sys.exit(0)
else:
    print("\n✗ Some tests failed")
    sys.exit(1)
