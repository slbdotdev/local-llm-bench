from tmpl import render, TemplateError


def ok(src, ctx, expected):
    got = render(src, ctx)
    assert got == expected, "src=%r ctx=%r got=%r expected=%r" % (src, ctx, got, expected)


def err(src, ctx, kind, pos):
    try:
        render(src, ctx)
    except TemplateError as e:
        assert e.kind == kind and e.pos == pos, "src=%r got kind=%r pos=%r expected kind=%r pos=%r" % (
            src, e.kind, e.pos, kind, pos)
    else:
        assert False, "src=%r expected error %r@%r but rendered fine" % (src, kind, pos)


# basic
ok("hello", {}, "hello")
ok("{{ 1 }}", {}, "1")
err("{{ 1 + 1 }}", {}, "syntax", 0)

# comments
ok("a{# comment #}b", {}, "ab")
ok("{# a {# b #} c #}", {}, " c #}")

# unclosed tag leftmost
err("{{ a {% b", {}, "unclosed_tag", 0)
err("ok {% if x %}", {}, "unclosed_block", 3)

# whitespace control
ok("A\n  {%- if true %}yes{% endif %}", {}, "Ayes")
ok("{% if true -%}\n  B{% endif %}", {}, "B")
ok("  {#- -#}  ", {}, "")
ok("x  {#- -#}  y", {}, "xy")
ok("a  {%- if true %}{% endif -%}  b", {}, "ab")

# escaping
ok("{{ v }}", {"v": "<a>&'\""}, "&lt;a&gt;&amp;&#39;&#34;")
ok("{{ v | safe }}", {"v": "<a>"}, "<a>")
ok("{{ v | escape | upper }}", {"v": "a&b"}, "A&AMP;B")

# set / scoping
ok("{% set x = 5 %}{{ x }}", {}, "5")
ok("{% if true %}{% set x = 1 %}{% endif %}{{ x }}", {}, "1")
ok("{% for i in cs %}{% endfor %}{{ x }}", {"cs": [1, 2]}, "")

# for / loop
ok("{% for c in cs %}{{ loop.index }}.{{ loop.index0 }}.{{ loop.first }}.{{ loop.last }}.{{ loop.length }} {% endfor %}",
   {"cs": ["a", "b"]}, "1.0.true.false.2 2.1.false.true.2 ")

ok("{% for c in cs %}x{% empty %}none{% endfor %}", {"cs": []}, "none")

# for over string/map
ok("{% for c in 'ab' %}{{ c }}{% endfor %}", {}, "ab")
ok("{% for k in m %}{{ k }} {% endfor %}", {"m": {"a": 1, "b": 2}}, "a b ")

# not iterable
err("{% for x in 5 %}{% endfor %}", {}, "not_iterable", 0)
err("{% for x in true %}{% endfor %}", {}, "not_iterable", 0)

# nested loop shadow
ok("{% for i in cs %}{% for j in ds %}{{ loop.index }}{% endfor %}{% endfor %}",
   {"cs": [1, 2], "ds": [3, 4]}, "12" * 2)

# loop.parent doesn't exist
ok("{% for i in cs %}{% for j in cs %}{{ loop.parent }}{% endfor %}{% endfor %}", {"cs": [1]}, "")

# filters
ok("{{ 'Hi' | upper }}", {}, "HI")
ok("{{ 'Hi' | lower }}", {}, "hi")
ok("{{ '  x  ' | trim }}", {}, "x")
ok("{{ v | length }}", {"v": [1, 2, 3]}, "3")
ok("{{ 123 | length }}", {}, "3")
err("{{ -12 | length }}", {}, "syntax", 0)  # unary minus not supported

ok("{{ v | first }}", {"v": [1, 2]}, "1")
ok("{{ v | first }}", {"v": []}, "")
ok("{{ '' | first }}", {}, "")

ok("{{ miss | default:'n/a' }}", {}, "n/a")
ok("{{ v | default:'n/a' }}", {"v": "x"}, "x")
ok("{{ v | default:'n/a' }}", {"v": 0}, "n/a")

ok("{{ v | join:', ' }}", {"v": [1, 2, 3]}, "1, 2, 3")
ok("{{ 'abc' | join:'-' }}", {}, "a-b-c")
ok("{{ m | join:',' }}", {"m": {"a": 1, "b": 2}}, "a,b")

ok("{{ 'hello' | replace:'l','L' }}", {}, "heLLo")
ok("{{ 'hello' | replace:'','x' }}", {}, "hello")

ok("{{ v | slice:1,2 }}", {"v": "hello"}, "el")
ok("{{ v | slice:1,100 }}", {"v": "hello"}, "ello")
ok("{{ v | slice:'x',2 }}", {"v": "hello"}, "hello")  # invalid start -> unchanged

# filter arg parsing: bare arg never a variable
ok("{{ 'x' | default:x }}", {"x": "y"}, "x")  # value 'x' is truthy so default not applied; result unescaped? 'x' safe? not safe -> just 'x'
ok("{{ v | default:x }}", {"v": 0, "x": "y"}, "x")  # bare arg "x" -> literal string "x", not lookup

# unknown filter / filter args
err("{{ v | nope }}", {"v": 1}, "unknown_filter", 0)
err("{{ v | upper: }}", {"v": 1}, "filter_args", 0)  # upper takes 0 args, got 1 (empty string arg)
err("{{ v | default }}", {"v": 1}, "filter_args", 0)  # default needs 1 arg, got 0
err("{{ v | | }}", {"v": 1}, "syntax", 0)

# comparisons
ok("{{ 1 < 2 }}", {}, "true")
ok("{{ 'a' < 'b' }}", {}, "true")
err("{{ 1 < 'a' }}", {}, "bad_operand", 0)
err("{{ true < 1 }}", {}, "bad_operand", 0)
err("{{ 1 < 2 < 3 }}", {}, "syntax", 0)
ok("{{ 1 == true }}", {}, "false")
ok("{{ '1' == 1 }}", {}, "false")
ok("{{ none == miss }}", {}, "false")  # none vs undefined: different types
ok("{{ miss == miss2 }}", {}, "true")  # both undefined
ok("{{ none == none }}", {}, "true")

# in
ok("{{ '' in 'ab' }}", {}, "true")
ok("{{ 'x' in v }}", {"v": ["x", "y"]}, "true")
ok("{{ 'x' in v }}", {"v": {"x": 1}}, "true")
ok("{{ 'x' in 5 }}", {}, "false")

# and/or/not short circuit
ok("{{ true or 1 < 'a' }}", {}, "true")  # or short-circuits, never evaluates the bad comparison
ok("{{ false and 1 < 'a' }}", {}, "false")  # and short-circuits too
err("{{ false or 1 < 'a' }}", {}, "bad_operand", 0)  # or must evaluate rhs -> error
err("{{ true and 1 < 'a' }}", {}, "bad_operand", 0)
ok("{{ not false }}", {}, "true")
ok("{{ not 0 }}", {}, "true")
ok("{{ not true == false }}", {}, "true")  # not binds looser: not (true==false) = not false = true


# lookup
ok("{{ a.b }}", {"a": {"b": 5}}, "5")
ok("{{ a.0 }}", {"a": ["x", "y"]}, "x")
ok("{{ a[0] }}", {"a": ["x", "y"]}, "x")
ok("{{ a['0'] }}", {"a": {"0": "z"}}, "z")
ok("{{ a[0] }}", {"a": {"0": "z"}}, "")  # int 0 doesn't match string key "0"
ok("{{ a.size }}", {"a": [1, 2, 3]}, "3")
ok("{{ a.size }}", {"a": {"size": 99}}, "99")  # shadowed
ok("{{ a.type }}", {"a": [1]}, "list")
ok("{{ a.type }}", {"a": None}, "")  # none.type -> undefined via rule1
ok("{{ a.keys | join:',' }}", {"a": {"x": 1, "y": 2}}, "x,y")
ok("{{ miss.x }}", {}, "")
ok("{{ a[i] }}", {"a": [1, 2], "i": -1}, "")  # negative index from context var never valid

# truthiness
ok("{{ '0' }}", {}, "0")
ok("{% if v %}T{% else %}F{% endif %}", {"v": "0"}, "F")
ok("{% if v %}T{% else %}F{% endif %}", {"v": "false"}, "F")
ok("{% if v %}T{% else %}F{% endif %}", {"v": " "}, "T")
ok("{% if v %}T{% else %}F{% endif %}", {"v": "False"}, "T")
ok("{% if v %}T{% else %}F{% endif %}", {"v": -1}, "T")
ok("{% if v %}T{% else %}F{% endif %}", {"v": 0}, "F")
ok("{% if v %}T{% else %}F{% endif %}", {"v": []}, "F")
ok("{% if v %}T{% else %}F{% endif %}", {"v": {}}, "F")

# safe stickiness with set
ok("{% set x = v | safe %}{{ x }}", {"v": "<b>"}, "<b>")
ok("{% set x = v | safe %}{{ x.y }}", {"v": "<b>"}, "")  # lookup on it unmarks (also lookup fails anyway - string has no .y)
ok("{% set x = v | safe %}{{ x | upper }}", {"v": "<b>"}, "<B>")  # sticky through upper

# default never safe when substituted
ok("{{ miss | default:x }}", {"x": "<b>"}, "x")  # bare arg is literal string "x", not a lookup
ok("{% set s = v | safe %}{{ miss | default:s }}", {"v": "ok"}, "s")  # bare arg never variable -> literal "s"

# structural errors
err("{% else %}", {}, "unexpected_tag", 0)
err("{% endif %}", {}, "unexpected_tag", 0)
err("{% endfor %}", {}, "unexpected_tag", 0)
err("{% empty %}", {}, "unexpected_tag", 0)
err("{% if 1 %}{% else x %}{% endif %}", {}, "syntax", 10)
err("{% if 1 %}{% else %}{% else %}{% endif %}", {}, "unexpected_tag", 20)
err("{% if 1 %}{% elif 2 %}{% else %}{% elif 3 %}{% endif %}", {}, "unexpected_tag", 32)
err("{% for i in v %}{% else %}{% endfor %}", {"v": [1]}, "unexpected_tag", 16)
err("{% for i in v %}{% empty %}{% empty %}{% endfor %}", {"v": []}, "unexpected_tag", 27)
err("{% for i in v %}{% if 1 %}{% endfor %}", {"v": [1]}, "unexpected_tag", 26)

# unknown / empty tags
err("{% %}", {}, "unknown_tag", 0)
err("{% bogus %}", {}, "unknown_tag", 0)
err("{{ }}", {}, "syntax", 0)

# leftmost-first rule: first error in source wins
err("{{ }}{% bogus %}", {}, "syntax", 0)
err("{% bogus %}{{ }}", {}, "unknown_tag", 0)

print("all extra tests passed")
