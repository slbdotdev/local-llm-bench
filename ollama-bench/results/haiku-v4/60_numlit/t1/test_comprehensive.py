"""Comprehensive tests for numlit.py"""
from numlit import scan, format_number, NumError

def test_error(text, kind, pos, description):
    try:
        scan(text)
        print(f"FAIL: {description} - expected error")
    except NumError as e:
        if e.kind == kind and e.pos == pos:
            print(f"OK: {description}")
        else:
            print(f"FAIL: {description} - got kind={e.kind}, pos={e.pos}, expected kind={kind}, pos={pos}")

# Separator errors
test_error(" 42", "space", 0, "leading space")
test_error("42 ", "space", 2, "trailing space")
test_error("42  43", "space", 3, "double space")

# Sign errors
test_error("+", "sign", 0, "sign only")
test_error("-", "sign", 0, "minus only")

# Suffix errors
test_error("1.5u", "suffix", 3, "u on float")
test_error("1.5l", "suffix", 3, "l on float")
test_error("123s", "suffix", 3, "s on int")

# Underscore errors
test_error("_1", "underscore", 0, "underscore at start of intpart")
test_error("1_", "underscore", 1, "underscore at end of intpart")
test_error("1__2", "underscore", 1, "double underscore")
test_error("1_.5", "underscore", 1, "underscore before dot")
test_error("1._5", "underscore", 2, "underscore at start of fracpart")
test_error("1.5_", "underscore", 3, "underscore at end of fracpart")
test_error("1e_5", "underscore", 2, "underscore at start of expdigits")
test_error("1e+_5", "underscore", 3, "underscore after exp sign")
test_error("1e5_", "underscore", 3, "underscore at end of expdigits")

# Dangling dot errors
test_error("5.", "dangling_dot", 1, "number with trailing dot")
test_error("5.e3", "dangling_dot", 1, "trailing dot before exponent")

# Exponent errors
test_error("1e", "exponent", 1, "e with no exponent digits")
test_error("1e+", "exponent", 1, "e+ with no exponent digits")
test_error("1E-", "exponent", 1, "E- with no exponent digits")

# Leading zero errors
test_error("007", "leading_zero", 0, "leading zeros 007")
test_error("00", "leading_zero", 0, "leading zeros 00")
test_error("01.5", "leading_zero", 0, "leading zero with fraction")
test_error("0_1", "leading_zero", 0, "0_ with underscore")

# Radix errors
test_error("0X1F", "prefix", 1, "uppercase X")
test_error("0O17", "prefix", 1, "uppercase O")
test_error("0B101", "prefix", 1, "uppercase B")
test_error("0x", "prefix", 2, "0x with no digits")
test_error("0o", "prefix", 2, "0o with no digits")
test_error("0b", "prefix", 2, "0b with no digits")
test_error("0x1g", "digit", 3, "invalid hex digit g")
test_error("0o8", "digit", 2, "invalid octal digit 8")
test_error("0b2", "digit", 2, "invalid binary digit 2")

# Charset errors
test_error("1@2", "char", 1, "invalid character @")

# Syntax errors
test_error("1+2", "syntax", 1, "plus in middle")
test_error("1.2.3", "syntax", 3, "double dot")
test_error("1a", "syntax", 1, "letter in decimal")

print("\n--- Testing format_number ---")

# Test basic formatting
result = format_number(42, "")
assert result == "42", f"Expected '42', got '{result}'"
print(f"OK: basic int format")

result = format_number(3.5, ".1")
assert result == "3.5", f"Expected '3.5', got '{result}'"
print(f"OK: basic float format")

# Test sign handling
result = format_number(-3.5, "-.1")
assert result == "-3.5", f"Expected '-3.5', got '{result}'"
print(f"OK: sign minus")

result = format_number(-3.5, "+.1")
assert result == "-3.5", f"Expected '-3.5', got '{result}'"
print(f"OK: sign plus with negative")

result = format_number(3.5, "+.1")
assert result == "+3.5", f"Expected '+3.5', got '{result}'"
print(f"OK: sign plus with positive")

result = format_number(3.5, " .1")
assert result == " 3.5", f"Expected ' 3.5', got '{result}'"
print(f"OK: sign space with positive")

result = format_number(-3.5, " .1")
assert result == "-3.5", f"Expected '-3.5', got '{result}'"
print(f"OK: sign space with negative")

# Test alignment and padding
result = format_number(3.5, "8.1")
assert result == "     3.5", f"Expected '     3.5', got '{result}'"
print(f"OK: right align padding")

result = format_number(3.5, "<8.1")
assert result == "3.5     ", f"Expected '3.5     ', got '{result}'"
print(f"OK: left align padding")

result = format_number(3.5, "^9.1")
expected = "   3.5   "
assert result == expected, f"Expected '{expected}', got '{result}'"
print(f"OK: center align padding")

# Test fill character
result = format_number(3.5, "*>8.1")
assert result == "*****3.5", f"Expected '*****3.5', got '{result}'"
print(f"OK: custom fill character")

# Test comma grouping
result = format_number(1234.5678, ",.2")
assert result == "1,234.57", f"Expected '1,234.57', got '{result}'"
print(f"OK: comma grouping")

# Test rounding modes
result = format_number(0.5, ".0")  # half-even, should round to 0
assert result == "0", f"Expected '0', got '{result}'"
print(f"OK: half-even rounding")

result = format_number(1.5, ".0h")  # half-even, should round to 2
assert result == "2", f"Expected '2', got '{result}'"
print(f"OK: half-even rounding to even")

result = format_number(0.5, ".0u")  # half-up, should round to 1
assert result == "1", f"Expected '1', got '{result}'"
print(f"OK: half-up rounding")

result = format_number(3.7, ".0d")  # truncate
assert result == "3", f"Expected '3', got '{result}'"
print(f"OK: truncate toward zero")

result = format_number(-3.7, ".0d")  # truncate
assert result == "-3", f"Expected '-3', got '{result}'"
print(f"OK: truncate toward zero (negative)")

result = format_number(-3.2, ".0f")  # floor
assert result == "-4", f"Expected '-4', got '{result}'"
print(f"OK: floor rounding")

# Test negative zero
result = format_number(-0.0, ".2")
assert result == "-0.00", f"Expected '-0.00', got '{result}'"
print(f"OK: negative zero format")

# Test precision
result = format_number(1.23456, ".3")
assert result == "1.235", f"Expected '1.235', got '{result}'"
print(f"OK: precision rounding")

print("\n--- Testing scan edge cases ---")

# Test .5 (valid)
result = scan(".5")
assert result[0]["value"] == 0.5, f"Expected 0.5, got {result[0]['value']}"
print(f"OK: .5 is valid")

# Test leading zeros in fraction (valid)
result = scan("1.00")
assert result[0]["value"] == 1.0, f"Expected 1.0, got {result[0]['value']}"
print(f"OK: leading zeros in fraction")

# Test leading zeros in exponent (valid)
result = scan("1e007")
assert result[0]["value"] == 1e7, f"Expected 1e7, got {result[0]['value']}"
print(f"OK: leading zeros in exponent")

# Test radix with underscores
result = scan("0x1_F")
assert result[0]["value"] == 31, f"Expected 31, got {result[0]['value']}"
print(f"OK: radix with underscores")

# Test canonical forms
result = scan("0x00FF")
assert result[0]["text"] == "0xff", f"Expected '0xff', got '{result[0]['text']}'"
print(f"OK: canonical radix lowercase")

result = scan("-0x000")
assert result[0]["text"] == "0x0", f"Expected '0x0', got '{result[0]['text']}'"
print(f"OK: canonical negative zero in radix")

print("\nAll tests passed!")
