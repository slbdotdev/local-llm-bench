import tmpl
from tmpl import render, TemplateError

def check(desc, cond):
    status = "OK" if cond else "FAIL"
    print(status, desc)
    if not cond:
        global failures
        failures += 1

failures = 0

check("ex1", render("Hello {{ name | upper }}!", {"name": "ada"}) == "Hello ADA!")
check("ex2", render("{% for c in cs %}{{ loop.index }}.{{ c }} {% empty %}none{% endfor %}", {"cs": ["a", "b"]}) == "1.a 2.b ")
check("ex3", render("{{ bio }}", {"bio": "<b>x</b>"}) == "&lt;b&gt;x&lt;/b&gt;")
check("ex4", render("A\n  {%- if ok %}yes{% endif %}", {"ok": True}) == "Ayes")
check("ex5", render("{{ miss | default:'n/a' }}", {}) == "n/a")

# basic literal text, no tags
check("literal", render("hello world", {}) == "hello world")

# unclosed tag
try:
    render("abc {{ x", {})
    check("unclosed_tag", False)
except TemplateError as e:
    check("unclosed_tag", e.kind == "unclosed_tag" and e.pos == 4)

# unknown tag name
try:
    render("{% frobnicate %}", {})
    check("unknown_tag_name", False)
except TemplateError as e:
    check("unknown_tag_name", e.kind == "unknown_tag" and e.pos == 0)

# empty block body
try:
    render("{%   %}", {})
    check("empty_block_body", False)
except TemplateError as e:
    check("empty_block_body", e.kind == "unknown_tag" and e.pos == 0)

# empty interpolation
try:
    render("{{ }}", {})
    check("empty_interp", False)
except TemplateError as e:
    check("empty_interp", e.kind == "syntax" and e.pos == 0)

# unexpected tag at top level
try:
    render("{% endif %}", {})
    check("unexpected_top", False)
except TemplateError as e:
    check("unexpected_top", e.kind == "unexpected_tag" and e.pos == 0)

# structural-first example
try:
    render("{% if 1 %}{% else x %}{% endif %}", {})
    check("else_x_syntax", False)
except TemplateError as e:
    check("else_x_syntax", e.kind == "syntax")

try:
    render("{% else x %}", {})
    check("else_x_top_unexpected", False)
except TemplateError as e:
    check("else_x_top_unexpected", e.kind == "unexpected_tag")

# unclosed block - innermost
try:
    render("{% if a %}{% for x in y %}body", {"a": True, "y": []})
    check("unclosed_block_innermost", False)
except TemplateError as e:
    check("unclosed_block_innermost", e.kind == "unclosed_block" and e.pos == 10)

# comments not nested
r = render("{# a {# b #} c #}", {})
check("comment_no_nest", r == " c #}")

# tag ends at first closer, quotes not special
try:
    render('{% if x == "%}" %}', {"x": "y"})
    check("quote_not_special", False)
except TemplateError as e:
    # body is 'if x == "' -> name if, rest = x == " -> string unterminated -> syntax
    check("quote_not_special", e.kind == "syntax")

# whitespace control unbounded, crosses newlines
r = render("A\n\n  {%- if True %}B{% endif %}", {"True": True})
check("ws_trim_cross_newline", r == "AB")

r = render("{% if ok %}A{% endif -%}\n\n   B", {"ok": True})
check("ws_trim_right_marker", r == "AB")

# trimming doesn't cross tags
r = render("{{ a }}{%- if ok %}X{% endif %}", {"a": "V", "ok": True})
check("marker_no_text_between", r == "VX")

# safe sticky
r = render("{{ x | escape | upper }}", {"x": "a&b"})
check("safe_sticky", r == "A&AMP;B")

# default unmarks when substituting; keeps when not
r = render("{{ x | safe | default:'z' }}", {"x": ""})
check("default_substitute_unsafe", r == "z")
r2 = render("{{ x | safe | default:'z' }}", {"x": "<a>"})
check("default_keep_safe", r2 == "<a>")

# set stores safety, bare read gets it back, lookup unmarks
r = render("{% set x = y | safe %}{{ x }}", {"y": "<a>"})
check("set_bare_safe", r == "<a>")

r3 = render('{% set lst = y %}{% set s = lst.0 %}{{ s }}', {"y": ["<a>"]})
check("lookup_unmarks", r3 == "&lt;a&gt;")

# truthiness rules
check("truthy_zero_str", render("{% if x %}T{% else %}F{% endif %}", {"x": "0"}) == "F")
check("truthy_false_str", render("{% if x %}T{% else %}F{% endif %}", {"x": "false"}) == "F")
check("truthy_space_str", render("{% if x %}T{% else %}F{% endif %}", {"x": " "}) == "T")
check("truthy_False_cap", render("{% if x %}T{% else %}F{% endif %}", {"x": "False"}) == "T")
check("truthy_neg1", render("{% if x %}T{% else %}F{% endif %}", {"x": -1}) == "T")

# loop.first / loop.last real booleans
r = render("{% for c in cs %}{% if loop.first == 1 %}Y{% else %}N{% endif %}{% endfor %}", {"cs": ["a"]})
check("loop_first_not_1", r == "N")

# not_iterable
try:
    render("{% for x in n %}{{x}}{% endfor %}", {"n": 5})
    check("not_iterable", False)
except TemplateError as e:
    check("not_iterable", e.kind == "not_iterable")

try:
    render("{% for x in n %}{{x}}{% endfor %}", {"n": True})
    check("not_iterable_bool", False)
except TemplateError as e:
    check("not_iterable_bool", e.kind == "not_iterable")

# bad_operand
try:
    render("{% if a < b %}Y{% endif %}", {"a": 1, "b": "x"})
    check("bad_operand", False)
except TemplateError as e:
    check("bad_operand", e.kind == "bad_operand")

try:
    render("{% if a < b %}Y{% endif %}", {"a": True, "b": 1})
    check("bad_operand_bool", False)
except TemplateError as e:
    check("bad_operand_bool", e.kind == "bad_operand")

# short circuit avoids error
r = render("{% if a and b < c %}Y{% else %}N{% endif %}", {"a": False, "b": "x", "c": 1})
check("short_circuit_and", r == "N")

r = render("{% if a or b < c %}Y{% else %}N{% endif %}", {"a": True, "b": "x", "c": 1})
check("short_circuit_or", r == "Y")

# comparison non-associative
try:
    render("{{ 1 < 2 < 3 }}", {})
    check("non_assoc_cmp", False)
except TemplateError as e:
    check("non_assoc_cmp", e.kind == "syntax")

# not binds looser
r = render("{% if not a == b %}Y{% else %}N{% endif %}", {"a": 1, "b": 1})
check("not_looser", r == "N")

# pipe in if is syntax
try:
    render("{% if a | upper %}Y{% endif %}", {"a": "x"})
    check("pipe_in_if_syntax", False)
except TemplateError as e:
    check("pipe_in_if_syntax", e.kind == "syntax")

# unknown filter
try:
    render("{{ a | bogus }}", {"a": "x"})
    check("unknown_filter", False)
except TemplateError as e:
    check("unknown_filter", e.kind == "unknown_filter")

# filter args arity
try:
    render("{{ a | default }}", {"a": ""})
    check("filter_args_arity", False)
except TemplateError as e:
    check("filter_args_arity", e.kind == "filter_args")

try:
    render("{{ a | replace:'x' }}", {"a": "x"})
    check("filter_args_arity2", False)
except TemplateError as e:
    check("filter_args_arity2", e.kind == "filter_args")

# slice
r = render("{{ s | slice:1,2 }}", {"s": "abcdef"})
check("slice_basic", r == "bc")

r = render("{{ s | slice:1,100 }}", {"s": "abcdef"})
check("slice_clamp", r == "bcdef")

r = render("{{ s | slice:'x',2 }}", {"s": "abcdef"})
check("slice_invalid", r == "abcdef")

r = render("{{ lst | slice:1,2 | join:',' }}", {"lst": [1,2,3,4]})
check("slice_list", r == "2,3")

# lookup rules
r = render("{{ m.0 }}", {"m": {"0": "zero", "size": "shadow"}})
check("map_str_key_zero", r == "zero")

r = render("{{ lst.0 }}", {"lst": ["a", "b"]})
check("list_dot_index", r == "a")

r = render("{{ m.size }}", {"m": {"size": "shadow"}})
check("shadow_size", r == "shadow")

r = render("{{ m.size }}", {"m": {"a": 1, "b": 2}})
check("real_size", r == "2")

r = render("{{ m.type }}", {"m": {"a": 1}})
check("type_map", r == "map")

r = render("{{ x.type }}", {"x": None})
check("type_none_undefined", r == "")

# for over map yields keys
r = render("{% for k in m %}{{k}} {% endfor %}", {"m": {"a":1,"b":2}})
check("for_map_keys", r == "a b ")

# filter escape on non-string
r = render("{{ n | escape }}", {"n": 5})
check("escape_number", r == "5")

# join variations
r = render("{{ m | join:',' }}", {"m": {"a":1,"b":2}})
check("join_map", r == "a,b")

r = render("{{ s | join:'-' }}", {"s": "abc"})
check("join_string", r == "a-b-c")

r = render("{{ n | join:',' }}", {"n": 5})
check("join_number", r == "5")

# escaping single pass (no re-escape of produced &)
r = render("{{ x }}", {"x": "<"})
check("escape_lt", r == "&lt;")

# text of list/map
r = render("{{ lst }}", {"lst": [1, "a", True]})
check("text_list", r == "[1, a, true]")

r = render("{{ m }}", {"m": {"a": 1, "b": "x"}})
check("text_map", r == "{a: 1, b: x}")

# render always str
r = render("", {})
check("empty_source", r == "")

# scoping - set inside if leaks
r = render("{% if True %}{% set z = 5 %}{% endif %}{{ z }}", {"True": True})
check("set_leaks_from_if", r == "5")

# set inside for scope, gone after
r = render("{% for i in xs %}{% set z = i %}{% endfor %}{{ z }}", {"xs":[1,2,3]})
check("set_scoped_to_for", r == "")

r = render("{% for i in xs %}{{ z|default:'-' }}{% set z = i %}{% endfor %}", {"xs":[1,2,3]})
check("set_persists_across_iters", r == "-12")

print()
print("Failures:", failures)
