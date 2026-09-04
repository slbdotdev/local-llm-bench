Create `money.py` in the current directory: exact money arithmetic on decimal STRINGS.

Do NOT import or use the `decimal` or `fractions` modules in any way — the grader inspects
the source of `money.py` and fails you if it finds them. Do everything with plain `int`
arithmetic (`re` and other stdlib modules are fine). There must be no floats anywhere: every
result must be exact.

```python
class MoneyError(ValueError): ...

ROUND_HALF_EVEN = "half_even"
ROUND_HALF_UP   = "half_up"
ROUND_HALF_DOWN = "half_down"
ROUND_CEILING   = "ceiling"
ROUND_FLOOR     = "floor"
ROUND_DOWN      = "down"        # toward zero (truncate)
ROUND_UP        = "up"          # away from zero

def quantize(amount: str, places: int, mode: str) -> str
def allocate(total: str, weights: list[str], places: int) -> list[str]
def add_tax(net: str, rate: str, places: int, mode: str) -> tuple[str, str, str]
def extract_tax(gross: str, rate: str, places: int, mode: str) -> tuple[str, str, str]
```

The seven module-level constants must exist and must be exactly the strings shown; the
`mode` argument is one of those strings.

## Number strings

An **amount string** matches exactly `^[+-]?[0-9]+(\.[0-9]+)?$`: an optional sign, at least
one digit, and optionally a `.` followed by at least one digit. Leading zeros are allowed
(`"007.50"` is 7.5). Everything else is malformed and must raise `MoneyError`: `""`, `" 1"`,
`"1 "`, `"1."`, `".5"`, `"1.2.3"`, `"1e3"`, `"1_0"`, `"--1"`, `"+-1"`, `"abc"`, `"nan"`,
`"1,000.00"`, and any argument that is not a `str`.

A string denotes the exact rational `digits-with-the-point-removed / 10**(number of decimals)`;
`"-0.00"` denotes exactly 0.

**Output format.** Every amount returned by these functions is canonical: an optional `-`,
then the integer part with no leading zeros (just `"0"` if it is zero), then — only when
`places > 0` — a `.` and exactly `places` digits. A value of zero is NEVER signed: the output
`"-0"`, `"-0.00"`, … must never occur; zero prints as `"0"`, `"0.00"`, …

`places` must be an `int` with `places >= 0` (a `bool` counts as an `int` here — do not worry
about it); otherwise raise `MoneyError`. A `mode` that is not one of the seven strings raises
`MoneyError`. Validate arguments before doing any work.

## Rounding

Every rounding in this task takes an EXACT rational value `v` (never a float) and picks the
integer `u` such that the answer is `u / 10**places`. `v` always lies between two consecutive
candidates `lo/10**places <= v <= hi/10**places` with `hi = lo + 1`. If `v` is exactly
representable (`v == lo/10**places`) the answer is `lo` and the mode is irrelevant. Otherwise
the mode decides, and it decides on the SIGNED value `v`, not on its magnitude:

- `floor`   — pick `lo` (toward -infinity).
- `ceiling` — pick `hi` (toward +infinity).
- `down`    — pick whichever of `lo`/`hi` is closer to zero (truncate).
- `up`      — pick whichever of `lo`/`hi` is further from zero.
- `half_even`, `half_up`, `half_down` — pick the nearer candidate; if `v` is exactly halfway
  between them, then `half_even` picks the candidate whose `u` is even, `half_up` picks the
  candidate further from zero, and `half_down` picks the candidate closer to zero.

So, at `places = 0`: `2.5` gives `2 / 3 / 2` and `-2.5` gives `-2 / -3 / -2` for
`half_even / half_up / half_down`; `-0.4` gives `-1` with `floor`, `0` with `ceiling` and with
`down` — and it prints as `"0"`, never `"-0"`. `-1.2` gives `-2` with `up`.

## `quantize(amount, places, mode)`

Round the amount to `places` decimals with `mode` and return it in the canonical output
format. If the amount already has `places` decimals or fewer, the value is unchanged (it is
just re-formatted, padding with zeros on the right).

## `allocate(total, weights, places)`

Split `total` into `len(weights)` shares that add up to `total` EXACTLY.

`total` must be exactly representable at `places` (i.e. it must not have more than `places`
decimals) or `MoneyError` is raised; `total` may be negative or zero. Let `T` be its value in
units of `10**-places` (an int). Each weight is an amount string and must not be negative, or
`MoneyError` is raised.

1. If `weights` is empty: return `[]` when `T == 0`, otherwise raise `MoneyError`.
2. Turn the weights into non-negative integers `w[0..n-1]` by scaling them all by the same
   power of ten (multiply each by `10**k`, where `k` is the largest number of decimals of any
   weight), so their ratios are preserved exactly. Let `S = sum(w)`.
3. If `S == 0` (every weight is zero), replace every `w[i]` by `1` and `S` by `n`: an all-zero
   weight vector splits the total as evenly as possible.
4. For each `i`, let `q[i]` and `r[i]` be the FLOOR quotient and remainder of `T * w[i]`
   divided by `S`, i.e. `q[i] = floor(T*w[i]/S)` and `r[i] = T*w[i] - S*q[i]`, so `r[i]` is
   always in `0 <= r[i] < S` even when `T` is negative.
5. `L = T - sum(q)` is an integer with `0 <= L < n`. Add exactly `+1` unit to the `L` shares
   with the LARGEST `r[i]`; ties among equal `r[i]` are broken by the SMALLER index first.
6. Return the shares in the original order of `weights`, each formatted with `places`
   decimals.

A zero-weight share therefore always gets exactly `0` (`r[i] == 0` is the smallest possible
remainder — but if several shares tie at `r[i] == 0` and units are still left over, the
lowest indices among them do get a unit, exactly as rule 5 says).

## `add_tax(net, rate, places, mode)` and `extract_tax(gross, rate, places, mode)`

`rate` is a PERCENTAGE amount string (`"19"` means 19%, `"8.875"` means 8.875%) and must not
be negative or `MoneyError` is raised. `net` / `gross` must be exactly representable at
`places` (else `MoneyError`); they may be negative or zero. Both functions return the triple
`(net, tax, gross)`, each formatted with `places` decimals.

- `add_tax` (tax-exclusive): `tax` is the exact rational `net * rate / 100` rounded to
  `places` with `mode`; then `gross = net + tax` exactly (no further rounding).
- `extract_tax` (tax-inclusive): `tax` is the exact rational `gross * rate / (100 + rate)`
  rounded to `places` with `mode`; then `net = gross - tax` exactly (no further rounding).

In both cases the returned `net + tax == gross` holds exactly, digit for digit.

## Examples

```python
quantize("2.345", 2, ROUND_HALF_EVEN) == "2.34"
quantize("2.345", 2, ROUND_HALF_UP)   == "2.35"
quantize("5", 3, ROUND_FLOOR)         == "5.000"
quantize("007.50", 1, ROUND_DOWN)     == "7.5"

allocate("100.00", ["1", "1", "1"], 2) == ["33.34", "33.33", "33.33"]
allocate("0.05", ["3", "1"], 2)        == ["0.04", "0.01"]

add_tax("100.00", "19", 2, ROUND_HALF_EVEN)     == ("100.00", "19.00", "119.00")
extract_tax("119.00", "19", 2, ROUND_HALF_EVEN) == ("100.00", "19.00", "119.00")
```

Write a few quick checks of your own and run them with `python`, then reply "done".
