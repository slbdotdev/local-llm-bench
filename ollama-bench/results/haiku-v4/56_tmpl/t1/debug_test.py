#!/usr/bin/env python3
from tmpl import render, TemplateError

# Test 4: For loop
template = "{% for c in cs %}{{ loop.index }}.{{ c }} {% empty %}none{% endfor %}"
context = {"cs": ["a", "b"]}
result = render(template, context)
print(f"Result: '{result}'")
print(f"Expected: '1.a 2.b '")

# Simpler test
result2 = render("{% for c in cs %}{{ c }}{% endfor %}", {"cs": ["a", "b"]})
print(f"\nSimple loop result: '{result2}'")

# Test accessing loop
result3 = render("{% for c in cs %}{{ loop.index }}{% endfor %}", {"cs": ["a", "b"]})
print(f"Loop.index result: '{result3}'")
