import tmpl
from tmpl import render, TemplateError

def eq(a, b, label=""):
    if a != b:
        print("FAIL", label, repr(a), "!=", repr(b))
    else:
        print("ok", label)

def err(src, ctx, kind, pos, label=""):
    try:
        r = render(src, ctx)
        print("FAIL (no error)", label, repr(r))
    except TemplateError as e:
        if e.kind != kind or e.pos != pos:
            print("FAIL", label, "got", e.kind, e.pos, "want", kind, pos)
        else:
            print("ok", label)

# examples from spec
eq(render("Hello {{ name | upper }}!", {"name": "ada"}), "Hello ADA!", "ex1")
eq(render("{% for c in cs %}{{ loop.index }}.{{ c }} {% empty %}none{% endfor %}", {"cs": ["a", "b"]}), "1.a 2.b ", "ex2")
eq(render("{{ bio }}", {"bio": "<b>x</b>"}), "&lt;b&gt;x&lt;/b&gt;", "ex3")
eq(render("A\n  {%- if ok %}yes{% endif %}", {"ok": True}), "Ayes", "ex4")
eq(render("{{ miss | default:'n/a' }}", {}), "n/a", "ex5")

# basic literal
eq(render("hello", {}), "hello", "literal")

# comment
eq(render("a{# comment #}b", {}), "ab", "comment")
eq(render("{# a {# b #} c #}", {}), " c #}", "comment nesting example")

# unclosed tag
err("{{ x", {}, "unclosed_tag", 0, "unclosed interp")
err("abc{% if x", {}, "unclosed_tag", 3, "unclosed block")

# whitespace control unbounded
eq(render("a   \n\n{%- if true %}X{% endif %}", {}), "aX", "trim left unbounded")
eq(render("{% if true -%}   \n\nb{% endif %}", {}), "b", "trim right unbounded")

# safe stickiness example
eq(render("{{ x | escape | upper }}", {"x": "a&b"}), "A&AMP;B", "sticky safe")

# set + bare name safety
eq(render("{% set y = x | safe %}{{ y }}", {"x": "<a>"}), "<a>", "set safe sticky")
eq(render("{% set y = x | safe %}{{ y.type }}", {"x": "<a>"}), "string", "dot unmarks")
eq(render("{% set y = x | safe %}{{ (y == x) }}", {"x": "<a>"}), "", "dummy") if False else None

# truthiness
eq(render("{% if '0' %}T{% else %}F{% endif %}", {}), "F", "truthy str 0")
eq(render("{% if '0.0' %}T{% else %}F{% endif %}", {}), "T", "truthy str 0.0")
eq(render("{% if ' ' %}T{% else %}F{% endif %}", {}), "T", "truthy space")
eq(render("{% if x %}T{% else %}F{% endif %}", {"x": -1}), "T", "truthy -1")

# loop.first/last booleans
eq(render("{% for c in cs %}{% if loop.first == 1 %}Y{% else %}N{% endif %}{% endfor %}", {"cs":["a"]}), "N", "loop.first is real bool")

# filters
eq(render("{{ ' hi ' | trim }}", {}), "hi", "trim filter")
eq(render("{{ x | length }}", {"x": [1,2,3]}), "3", "length list")
eq(render("{{ x | length }}", {"x": -12}), "2", "length number")
eq(render("{{ x | first }}", {"x": []}), "", "first empty list undefined")
eq(render("{{ x | join:', ' }}", {"x": ["a","b"]}), "a, b", "join list")
eq(render("{{ x | replace:'a','b' }}", {"x": "banana"}), "bbnbnb", "replace")
eq(render("{{ x | replace:'','b' }}", {"x": "abc"}), "abc", "replace empty A")
eq(render("{{ x | slice:1,2 }}", {"x": "abcdef"}), "bc", "slice str")
eq(render("{{ x | slice:1,2 }}", {"x": [1,2,3,4]}), "[2, 3]", "slice list")
eq(render("{{ x | slice:'a',2 }}", {"x": "abcdef"}), "abcdef", "slice invalid start unchanged")

# unknown filter / arity
err("{{ x | nope }}", {}, "unknown_filter", 0, "unknown filter")
err("{{ x | default }}", {}, "filter_args", 0, "default arity")
err("{{ x | default:1,2 }}", {}, "filter_args", 0, "default arity 2")

# syntax errors
err("{{ }}", {}, "syntax", 0, "empty interp")
err("{% if %}{% endif %}", {}, "syntax", 0, "empty if cond")
err("{% foo %}", {}, "unknown_tag", 0, "unknown tag")
err("{%  %}", {}, "unknown_tag", 0, "empty block body")
err("{% else %}", {}, "unexpected_tag", 0, "else top level")
err("{% if 1 %}{% else x %}{% endif %}", {}, "syntax", 10, "else nonempty rest -> syntax not unexpected")
err("{% if 1 %}{% endfor %}", {}, "unexpected_tag", 10, "endfor closes if")
err("{% if a < b < c %}{% endif %}", {"a":1,"b":2,"c":3}, "syntax", 0, "chained comparison")
err("{% if a | upper %}{% endif %}", {"a":"x"}, "syntax", 0, "pipe in if condition")

# bad_operand
err("{% if a < b %}{% endif %}", {"a": True, "b": 1}, "bad_operand", 0, "bad operand bool")
err("{% if a < b %}{% endif %}", {"a": "x", "b": 1}, "bad_operand", 0, "bad operand str/num")

# not_iterable
err("{% for x in y %}{% endfor %}", {"y": 5}, "not_iterable", 0, "not iterable number")
err("{% for x in y %}{% endfor %}", {"y": True}, "not_iterable", 0, "not iterable bool")

# unclosed block innermost
err("{% if a %}{% for x in y %}", {"a":True,"y":[]}, "unclosed_block", 10, "unclosed innermost for")

# and/or short circuit (no error raised on unevaluated side)
eq(render("{% if false and (1 < 'a') %}T{% else %}F{% endif %}", {}), "F", "and shortcircuit") if False else None
eq(render("{% if a and b %}T{% else %}F{% endif %}", {"a": False}), "F", "and shortcircuit no b needed")

print("done")
