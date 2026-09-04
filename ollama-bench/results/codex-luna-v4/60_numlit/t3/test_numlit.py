"""Visible checks for numlit.py -- run with: python test_numlit.py"""
from numlit import scan, format_number, NumError

assert scan("42 -7 3.5") == [
    {"kind": "int", "radix": 10, "value": 42, "text": "42", "suffix": "", "start": 0},
    {"kind": "int", "radix": 10, "value": -7, "text": "-7", "suffix": "", "start": 3},
    {"kind": "float", "radix": 10, "value": 3.5, "text": "3.5", "suffix": "", "start": 6},
]
assert scan("0x1F")[0]["value"] == 31
assert scan("0x1F")[0]["text"] == "0x1f"
assert scan("12u")[0]["suffix"] == "u"

try:
    scan("1+2")
    raise AssertionError("expected NumError")
except NumError as e:
    assert e.kind == "syntax" and e.pos == 1

assert format_number(1234.5678, ",.2") == "1,234.57"
assert format_number(-3.5, "8.1") == "    -3.5"

print("visible OK")
