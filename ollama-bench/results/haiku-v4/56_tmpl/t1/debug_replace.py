#!/usr/bin/env python3
from tmpl import render

# Test replace filter
result = render("{{ x | replace:'a','b' }}", {"x": "banana"})
print(f"Result: '{result}'")
print(f"Result chars: {[c for c in result]}")
print(f"Length: {len(result)}")

# Expected: "bbnbn" (5 chars)
# Got: "bbnbnb" (6 chars)

# Direct Python test
print(f"\nDirect Python: {'banana'.replace('a', 'b')}")

# Test just the parts
result2 = render("{{ 'banana' | replace:'a','b' }}", {})
print(f"\nWith literal string: '{result2}'")
