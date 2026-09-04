#!/usr/bin/env python3
"""Final integration test."""
from tmpl import render, TemplateError

# Complex template
template = """
{# Header comment #}
<h1>{{ title | upper }}</h1>

<div class="items">
  {% for item in items %}
    {% if item.active %}
      <div class="active">
        Item {{ loop.index }}: {{ item.name | escape }}
        {% if item.count %}
          Count: {{ item.count }}
        {% else %}
          No count available
        {% endif %}
      </div>
    {% endif %}
  {% empty %}
    <p>No items found</p>
  {% endfor %}
</div>

{% set summary = "Total items: " | escape %}
{{ summary }}{{ items.size }}
"""

context = {
    "title": "Product List",
    "items": [
        {"name": "Widget A", "active": True, "count": 5},
        {"name": "Widget <B>", "active": True, "count": None},
        {"name": "Widget C", "active": True, "count": 0},
    ]
}

result = render(template, context)
print("Result:")
print(result)
print("\n✓ Complex template rendered successfully!")

# Verify key parts of output
assert "<h1>PRODUCT LIST</h1>" in result
assert "Item 1: Widget A" in result
assert "Count: 5" in result
assert "Item 2: Widget &lt;B&gt;" in result  # Escaped HTML tag
assert "Item 3: Widget C" in result
assert "No count available" in result
assert "Total items:" in result
assert "3" in result  # Size of items list

print("✓ All assertions passed!")
