from numlit import scan, format_number, NumError

def expect_err(fn, kind, pos):
    try:
        fn()
        raise AssertionError("expected NumError kind=%s" % kind)
    except NumError as e:
        assert e.kind == kind, (e.kind, kind)
        assert e.pos == pos, (e.pos, pos)

# separator checks
expect_err(lambda: scan(" 1"), "space", 0)
expect_err(lambda: scan("1 "), "space", 1)
expect_err(lambda: scan("1  2"), "space", 2)
expect_err(lambda: scan(" "), "space", 0)

# charset
expect_err(lambda: scan("1$2"), "char", 1)

# sign
expect_err(lambda: scan("+"), "sign", 0)
expect_err(lambda: scan("-"), "sign", 0)

# suffix empty after strip
expect_err(lambda: scan("u"), "suffix", 0)
expect_err(lambda: scan("+u"), "suffix", 1)

# prefix uppercase
expect_err(lambda: scan("0X1"), "prefix", 1)
expect_err(lambda: scan("0O1"), "prefix", 1)
expect_err(lambda: scan("0B1"), "prefix", 1)

# radix empty after prefix
expect_err(lambda: scan("0x"), "prefix", 2)
expect_err(lambda: scan("0o"), "prefix", 2)
expect_err(lambda: scan("0b"), "prefix", 2)

# radix bad digit
expect_err(lambda: scan("0xG"), "digit", 2)
expect_err(lambda: scan("0o8"), "digit", 2)
expect_err(lambda: scan("0b2"), "digit", 2)

# syntax
expect_err(lambda: scan("1+2"), "syntax", 1)
expect_err(lambda: scan("1u5"), "syntax", 1)  # step C removes nothing since last char is '5'
expect_err(lambda: scan("1.2.3"), "syntax", 3)

# underscore
expect_err(lambda: scan("_1"), "underscore", 0)
expect_err(lambda: scan("1_"), "underscore", 1)
expect_err(lambda: scan("1__2"), "underscore", 1)
expect_err(lambda: scan("0x_1"), "underscore", 2)
expect_err(lambda: scan("1_.5"), "underscore", 1)
expect_err(lambda: scan("1._5"), "underscore", 2)
expect_err(lambda: scan("1e_5"), "underscore", 2)
expect_err(lambda: scan("1e+_5"), "underscore", 3)
expect_err(lambda: scan("1_e5"), "underscore", 1)

# dangling dot
expect_err(lambda: scan("5."), "dangling_dot", 1)
expect_err(lambda: scan("5.e3"), "dangling_dot", 1)
expect_err(lambda: scan("."), "dangling_dot", 0)

# .5 valid
r = scan(".5")[0]
assert r["kind"] == "float" and r["value"] == 0.5 and r["text"] == "0.5"

# exponent
expect_err(lambda: scan("1e"), "exponent", 1)
expect_err(lambda: scan("1e+"), "exponent", 1)

# leading zero
expect_err(lambda: scan("007"), "leading_zero", 0)
expect_err(lambda: scan("00"), "leading_zero", 0)
expect_err(lambda: scan("01.5"), "leading_zero", 0)
expect_err(lambda: scan("0_1"), "leading_zero", 0)
# fraction/exp/radix leading zeros are fine
r = scan("1.00")[0]; assert r["value"] == 1.0
r = scan("1e007")[0]; assert r["text"] == "1.0e7"
r = scan("0x00Ff")[0]; assert r["text"] == "0xff" and r["value"]==255

# suffix on float/int
expect_err(lambda: scan("1.5u"), "suffix", 3)
expect_err(lambda: scan("1.5l"), "suffix", 3)
expect_err(lambda: scan("5s"), "suffix", 1)
r = scan("12u")[0]; assert r["suffix"] == "u" and r["kind"]=="int"
r = scan("12l")[0]; assert r["suffix"] == "l" and r["kind"]=="int"
r = scan("1.5s")[0]; assert r["suffix"] == "s" and r["kind"]=="float"

# int radix10 canonical text, negative zero collapses
r = scan("-0")[0]; assert r["value"] == 0 and r["text"] == "0" and type(r["value"]) is int

# float negative zero
r = scan("-0.0")[0]; assert r["text"] == "-0.0"
assert repr(r["value"]) == "-0.0"

# examples from spec
r = scan("1e5")[0]; assert r["text"] == "1.0e5"
r = scan("1_0.2_5E+0_07")[0]; assert r["text"] == "10.25e7"
r = scan("1e000")[0]; assert r["text"] == "1.0e0"
r = scan("1e-0_3")[0]; assert r["text"] == "1.0e-3"

recs = scan("42 -7 3.5")
assert recs == [
    {"kind": "int", "radix": 10, "value": 42, "text": "42", "suffix": "", "start": 0},
    {"kind": "int", "radix": 10, "value": -7, "text": "-7", "suffix": "", "start": 3},
    {"kind": "float", "radix": 10, "value": 3.5, "text": "3.5", "suffix": "", "start": 6},
]
assert list(recs[0].keys()) == ["kind", "radix", "value", "text", "suffix", "start"]

# format_number basics
assert format_number(1234.5678, ",.2") == "1,234.57"
assert format_number(-3.5, "8.1") == "    -3.5"
assert format_number(0, "") == "0"
assert format_number(-0, "+") == "+0"
assert format_number(-0.001, ".2") == "-0.00"
assert format_number(-0.0, ".2") == "-0.00"
assert format_number(-0.6, "d") == "-0"

# ties
assert format_number(0.5, ".0h") == "0"   # half-even: 0 is even
assert format_number(1.5, ".0h") == "2"
assert format_number(2.5, ".0h") == "2"
assert format_number(0.5, ".0u") == "1"
assert format_number(-0.5, ".0u") == "-1"
assert format_number(2.675, ".2h") != "2.68"  # not a tie in binary, exact float below .675

# fill/align
assert format_number(5, "*^5") == "**5**"
assert format_number(5, "*<5") == "5****"
assert format_number(5, "*>5") == "****5"

# grouping
assert format_number(1234567, ",") == "1,234,567"

# spec errors
def bad_spec(spec):
    expect_err(lambda: format_number(1, spec), "spec", -1)

bad_spec("05")     # leading zero width
bad_spec("0")       # bare zero width
bad_spec(".")        # dot no digits
bad_spec("z")        # unknown mode
bad_spec(".21")      # precision > 20
bad_spec("201")      # width > 200

# type errors
expect_err(lambda: format_number(True, ""), "type", -1)
expect_err(lambda: format_number("1", ""), "type", -1)
expect_err(lambda: format_number(1, 5), "type", -1)

# nonfinite
expect_err(lambda: format_number(float("nan"), ""), "nonfinite", -1)
expect_err(lambda: format_number(float("inf"), ""), "nonfinite", -1)

print("ALL OK")
