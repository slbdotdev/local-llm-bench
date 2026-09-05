# Rounding

Every billable amount is computed in **integer cents** and rounded exactly once, at the point
where a fractional cent first appears.

## The rule

`round_half_up(value)` rounds a non-negative fractional cent amount to the nearest whole cent,
and a value exactly halfway between two cents rounds **up**, away from zero.

    0.4  -> 0
    0.5  -> 1
    1.5  -> 2
    2.5  -> 3

This is deliberately **not** Python's built-in `round`, which rounds half to even and would send
`0.5` to `0` and `2.5` to `2`. Bankers' rounding is correct for many purposes and is wrong for
this one: the meter's readings are already truncated in the customer's favour upstream, and
rounding half to even at this point compounds that in the same direction. A quarter's worth of
half-cents came to a four-figure discrepancy the last time this was got wrong.

## Where it applies

Anywhere a rate multiplied by a quantity produces a fractional cent. In practice that is
`line_total` in the rate module and nothing else today.
