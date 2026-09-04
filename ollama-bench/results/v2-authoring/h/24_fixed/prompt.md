Create `fixed.py` in the current directory implementing exact decimal fixed-point arithmetic on plain Python integers. Do NOT import or use the `decimal` or `fractions` modules in any way — the grader checks the source of `fixed.py` for such imports. Build everything from `int` arithmetic (`re` from the standard library is allowed).

A `Fixed` value represents the exact rational `units / 10**scale`, where `units` is a signed int and `scale` a non-negative int.

## The exception

Define `class MalformedNumber(ValueError)` in `fixed.py`. Every malformed input string must raise it.

## Construction and parsing

`Fixed(s)` takes exactly one argument, which must be a `str` (raise `TypeError` if it is not). The string must match exactly this grammar; anything else is malformed and raises `MalformedNumber` (leading/trailing whitespace is malformed):

```
^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$
```

i.e. optional sign, then either digits with an optional `.fraction`, or `.` followed by digits (so `5`, `5.`, `5.0`, `.5` are all valid), then an optional exponent `e`/`E`, optional sign, at least one digit. Malformed examples (all must raise `MalformedNumber`): `""`, `" "`, `"1.2.3"`, `".e3"`, `"1e"`, `"+"`, `"-"`, `"-.e2"`, `"1e+"`, `"e5"`, `"."`, `"1_0"`, `"0x10"`, `"nan"`, `"1.2e1.5"`.

Scale derivation from the literal: let `d` be the number of digits after the point in the mantissa (0 if there is no point or nothing after it) and `e` the exponent value (0 if absent). Let `coef` be the mantissa read as an integer (its digits with the point removed). If `e <= d`: `_scale = d - e` and `_units = coef`. If `e > d`: `_scale = 0` and `_units = coef * 10**(e - d)`. Apply the sign last; if the value is zero, `_units` is exactly `0` (never negative).

The representation is public: every instance stores the scaled integer in the attribute `_units` (int) and the scale in `_scale` (int >= 0); the grader inspects these. For example: `Fixed("1.5")._units == 15` and `_scale == 1`; `Fixed("1e2")._units == 100, _scale == 0`; `Fixed("1.23e-3")._units == 123, _scale == 5`; `Fixed("100e-2")._units == 100, _scale == 2`; `Fixed("-0.0")._units == 0, _scale == 1`; `Fixed("-.5")._units == -5, _scale == 1`; `Fixed("5.")._units == 5, _scale == 0`; `Fixed("0e-5")._units == 0, _scale == 5`.

## Rounding modes

`fixed.py` defines three module-level constants `ROUND_HALF_EVEN`, `ROUND_HALF_UP`, `ROUND_DOWN` (distinct values; their concrete values are up to you). All rounding operates on the magnitude; the sign is reapplied afterwards. When rounding to fewer digits:

- `ROUND_DOWN`: truncate toward zero (drop the extra digits).
- `ROUND_HALF_UP`: if the dropped part is more than half a unit of the last kept digit, round up (away from zero); if it is exactly half, also round up; if less, round down. Ties go away from zero.
- `ROUND_HALF_EVEN`: like HALF_UP except that an exact tie rounds to the even candidate (the last kept digit becomes even).

Examples (to scale 0 unless stated), as HALF_EVEN / HALF_UP / DOWN: `2.5` -> `2` / `3` / `2`; `3.5` -> `4` / `4` / `3`; `-2.5` -> `-2` / `-3` / `-2`; `0.125` to scale 2 -> `0.12` / `0.13` / `0.12`; `-0.125` to scale 2 -> `-0.12` / `-0.13` / `-0.12`. A zero result never carries a sign: rounding `-0.4` to scale 0 gives `"0"`.

## Arithmetic

Every binary operator requires a `Fixed` operand; given anything else it returns `NotImplemented` (so `Fixed("1") == 1` is `False`, `Fixed("1") != 1` is `True`, and `Fixed("1") < 1` raises `TypeError`).

- `__add__` / `__sub__`: the result scale is the maximum of the two operand scales; each operand's units are first multiplied by `10**(result_scale - operand_scale)`, then added or subtracted. Exact, no rounding. E.g. `Fixed("1.5") + Fixed("2.25")` prints `"3.75"`; `Fixed("1.5") - Fixed("1.50")` prints `"0.00"`; `Fixed("0.1") + Fixed("0.2")` prints `"0.3"`.
- `__mul__`: result units are the product of the units, result scale is the sum of the scales. Exact. E.g. `Fixed("1.5") * Fixed("0.2")` prints `"0.30"`; `Fixed("-2.0") * Fixed("3")` prints `"-6.0"`.
- `__truediv__`: the result scale is exactly 12. Let `k = 12 - scale_a + scale_b`. With `a = |units_a|`, `b = |units_b|`: if `k >= 0` use numerator `a * 10**k` and denominator `b`; if `k < 0` use numerator `a` and denominator `b * 10**(-k)`. Then `q, r = divmod(numerator, denominator)`; if `2*r > denominator`, or `2*r == denominator` and `q` is odd, increment `q` (ROUND_HALF_EVEN on the magnitude); apply the sign (negative iff the operand signs differ). If `units_b` is 0, raise `ZeroDivisionError`. E.g. `Fixed("1")/Fixed("3")` prints `"0.333333333333"`; `Fixed("2")/Fixed("2")` prints `"1.000000000000"`; `Fixed("1")/Fixed("8192")` prints `"0.000122070312"` (exact tie at scale 12, rounds to even); `Fixed("-1")/Fixed("8192")` prints `"-0.000122070312"`.
- `__neg__`: negates the units; zero stays zero (there is no negative zero anywhere: `str(-Fixed("-0.0"))` is `"0.0"`).

Arithmetic results are not additionally normalised: `Fixed("1.5") * Fixed("0.2")` has `_units == 30`, `_scale == 2`.

## quantize

`f.quantize(scale, rounding=ROUND_HALF_EVEN)` returns a new `Fixed` with exactly `scale` digits after the point. `scale` must be a non-negative `int` and `rounding` one of the three constants; anything else raises `ValueError`. If `scale >= f._scale` the result is exact (zeros appended). Otherwise round per the mode. E.g. `Fixed("1.5").quantize(4)` prints `"1.5000"`; `Fixed("9.999").quantize(2)` prints `"10.00"`; `Fixed("9.999").quantize(2, ROUND_DOWN)` prints `"9.99"`; `Fixed("-9.999").quantize(2)` prints `"-10.00"`.

## Comparison, equality, hashing

Equality and ordering compare numeric values across different scales: `Fixed("1.50") == Fixed("1.5")` is `True`, and `Fixed("-1.5") < Fixed("-1.45")` is `True`. `__hash__` must be consistent with `__eq__` (values that are equal but differently scaled must have equal hashes), so `Fixed` values work in sets and as dict keys: `len({Fixed("1.5"), Fixed("1.50")}) == 1` and `d = {Fixed("1.5"): "x"}; d[Fixed("1.50")] == "x"`.

## String form

`__str__` renders the value's own scale: a `-` prefix iff `_units < 0`, then the digits of `|_units|` with the point inserted so exactly `_scale` digits follow it (zero-padded on the right); when `_scale == 0` there is no point at all. Zero never prints with a sign but keeps its scale: `str(Fixed("-0")) == "0"`, `str(Fixed("0.000")) == "0.000"`, `str(Fixed("-0.0")) == "0.0"`. Also: `str(Fixed("1.5")) == "1.5"`, `str(Fixed("1e2")) == "100"`, `str(Fixed("100e-2")) == "1.00"`, `str(Fixed("1.23e-3")) == "0.00123"`, `str(Fixed("-.5")) == "-0.5"`, `str(Fixed("5.")) == "5"`, `str(Fixed("-12e3")) == "-12000"`.

Write a few quick checks of your own and run them with `python`, then reply "done".
