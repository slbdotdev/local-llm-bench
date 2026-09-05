# Numeric review: signed and zero contributions

The numeric review is intentionally about arithmetic, not validation. Deltas
are valid Python integers and may be negative, zero, or very large. Action
policy supplies the multiplier and the adapter performs ordinary integer
multiplication.

For an `add` of 8 the contribution is 8; for an `add` of -8 it is -8. For a
`remove` of 8 it is -8; for a `remove` of -8 it is +8. For an `adjust`, the
signed delta is unchanged. For a `hold`, any signed delta contributes zero.
Every accepted case increments occurrences exactly once, including cancellation
to zero and a zero multiplier. Rejected actions do none of these.

The review includes the sequence add 10, remove 10, adjust -4, hold 99, void
100 for one key. Its total is -4, its occurrences are 4, and its labels include
only labels from the first four changes in their canonical first-seen order.
The void label is absent. A model that counts nonzero totals or uses absolute
values can look reasonable on ordinary positive inputs but fails this sequence.
