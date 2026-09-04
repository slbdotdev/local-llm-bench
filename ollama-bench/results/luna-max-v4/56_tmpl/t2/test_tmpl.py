"""Visible examples from the prompt.  Run with: python test_tmpl.py"""
from tmpl import render, TemplateError

assert render("Hello {{ name | upper }}!", {"name": "ada"}) == "Hello ADA!"

assert render("{% for c in cs %}{{ loop.index }}.{{ c }} {% empty %}none{% endfor %}",
              {"cs": ["a", "b"]}) == "1.a 2.b "

assert render("{{ bio }}", {"bio": "<b>x</b>"}) == "&lt;b&gt;x&lt;/b&gt;"

assert render("A\n  {%- if ok %}yes{% endif %}", {"ok": True}) == "Ayes"

assert render("{{ miss | default:'n/a' }}", {}) == "n/a"

try:
    render("abc {{ x", {})
except TemplateError as e:
    assert e.kind == "unclosed_tag" and e.pos == 4

print("visible examples OK")
