"""The rate table and the money arithmetic.

Rates are in integer cents per unit-thousand, so a rate of 37 means 3.7 cents per unit.
"""

RATES = {
    "transit": 37,
    "storage": 4,
    "lookup": 190,
    "egress": 21,
}


def round_half_up(value):
    """Round a non-negative fractional cent amount to the nearest whole cent, half away from zero.

    See docs/rounding.md, which is authoritative. Python's built-in round() is half-to-even and
    is not what this project wants.
    """
    return int(value + 0.5)


def line_total(kind, units):
    """The billable amount in whole cents for ``units`` of ``kind``."""
    if kind not in RATES:
        raise KeyError(kind)
    return round_half_up(RATES[kind] * units / 1000.0)


def invoice_total(lines):
    """Sum a sequence of (kind, units) pairs, rounding each line before summing."""
    return sum(line_total(kind, units) for kind, units in lines)
