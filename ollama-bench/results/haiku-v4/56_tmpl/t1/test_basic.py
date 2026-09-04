#!/usr/bin/env python3
from tmpl import render, TemplateError

# Test 1: Simple interpolation
result = render("Hello {{ name | upper }}!", {"name": "ada"})
print(f"Test 1: {result}")
assert result == "Hello ADA!", f"Expected 'Hello ADA!', got '{result}'"

# Test 2: Escaping
result = render("{{ bio }}", {"bio": "<b>x</b>"})
print(f"Test 2: {result}")
assert result == "&lt;b&gt;x&lt;/b&gt;", f"Expected escaped, got '{result}'"

# Test 3: Whitespace control
result = render("A\n  {%- if ok %}yes{% endif %}", {"ok": True})
print(f"Test 3: {result}")
assert result == "Ayes", f"Expected 'Ayes', got '{result}'"

# Test 4: For loop
result = render("{% for c in cs %}{{ loop.index }}.{{ c }} {% empty %}none{% endfor %}", {"cs": ["a", "b"]})
print(f"Test 4: {result}")
assert result == "1.a 2.b ", f"Expected '1.a 2.b ', got '{result}'"

# Test 5: Default filter
result = render("{{ miss | default:'n/a' }}", {})
print(f"Test 5: {result}")
assert result == "n/a", f"Expected 'n/a', got '{result}'"

print("All tests passed!")
