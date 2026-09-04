from numlit import scan, format_number, NumError

# Check the examples from the task
print("Testing examples from TASK.md:")

# Example 1
result = scan("42 -7 3.5")
expected = [
    {"kind": "int", "radix": 10, "value": 42, "text": "42", "suffix": "", "start": 0},
    {"kind": "int", "radix": 10, "value": -7, "text": "-7", "suffix": "", "start": 3},
    {"kind": "float", "radix": 10, "value": 3.5, "text": "3.5", "suffix": "", "start": 6},
]
assert result == expected, f"Example 1 failed"
print("✓ Example 1: scan('42 -7 3.5')")

# Example 2
assert scan("0x1F")[0]["value"] == 31, "Example 2a failed"
print("✓ Example 2a: scan('0x1F')[0]['value'] == 31")

assert scan("0x1F")[0]["text"] == "0x1f", "Example 2b failed"
print("✓ Example 2b: scan('0x1F')[0]['text'] == '0x1f'")

# Example 3
assert scan("12u")[0]["suffix"] == "u", "Example 3 failed"
print("✓ Example 3: scan('12u')[0]['suffix'] == 'u'")

# Example 4
try:
    scan("1+2")
    print("✗ Example 4 failed: should raise NumError")
except NumError as e:
    assert e.kind == "syntax" and e.pos == 1, f"Example 4 failed: got kind={e.kind}, pos={e.pos}"
    print("✓ Example 4: scan('1+2') raises NumError('syntax', 1)")

# Example 5
result = format_number(1234.5678, ",.2")
assert result == "1,234.57", f"Example 5 failed: got {result}"
print("✓ Example 5: format_number(1234.5678, ',.2') == '1,234.57'")

# Example 6
result = format_number(-3.5, "8.1")
assert result == "    -3.5", f"Example 6 failed: got '{result}'"
print("✓ Example 6: format_number(-3.5, '8.1') == '    -3.5'")

print("\nAll examples from TASK.md pass!")
